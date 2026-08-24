"""
Database module for MathMate.
Connects to Supabase if SUPABASE_URL & SUPABASE_KEY are configured in st.secrets or os.environ.
Falls back seamlessly to local SQLite (mathmate.db) when credentials are missing.
"""

import os
import json
import sqlite3
from datetime import datetime
import streamlit as st

DB_FILE = os.path.join(os.path.dirname(__file__), "mathmate.db")


def get_supabase_client():
    """Retrieve Supabase client if secrets or environment variables exist."""
    url = None
    key = None
    
    try:
        if hasattr(st, "secrets"):
            if "SUPABASE_URL" in st.secrets:
                url = st.secrets["SUPABASE_URL"]
            elif "supabase" in st.secrets and "url" in st.secrets["supabase"]:
                url = st.secrets["supabase"]["url"]

            if "SUPABASE_KEY" in st.secrets:
                key = st.secrets["SUPABASE_KEY"]
            elif "supabase" in st.secrets and "key" in st.secrets["supabase"]:
                key = st.secrets["supabase"]["key"]
    except Exception:
        pass

    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

    if url and key:
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception as e:
            st.warning(f"Supabase connection warning: {e}. Falling back to SQLite.")
            return None
    return None


def init_db():
    """Ensure SQLite fallback tables exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            topic TEXT,
            answer TEXT,
            steps_json TEXT,
            created_at TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY DEFAULT 1,
            streak INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            quiz_correct INTEGER DEFAULT 0,
            quiz_total INTEGER DEFAULT 0,
            updated_at TEXT
        )
        """)
        # Ensure default stats row exists
        cursor.execute("SELECT COUNT(*) FROM user_stats WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO user_stats (id, streak, xp, quiz_correct, quiz_total, updated_at)
            VALUES (1, 0, 0, 0, 0, ?)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing SQLite DB: {e}")


# Initialize SQLite on load
init_db()


def is_supabase_connected() -> bool:
    """Check if Supabase is actively connected."""
    return get_supabase_client() is not None


def save_solution(question: str, topic: str, answer: str, steps: list = None):
    """Save a solved problem into Supabase or SQLite fallback."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    steps_str = json.dumps(steps or [])

    sp = get_supabase_client()
    if sp:
        try:
            sp.table("solutions").insert({
                "question": question,
                "topic": topic,
                "answer": answer,
                "steps_json": steps_str,
                "created_at": now
            }).execute()
            return
        except Exception as e:
            print(f"Supabase insert failed ({e}), saving to SQLite fallback.")

    # SQLite fallback
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO solutions (question, topic, answer, steps_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (question, topic, answer, steps_str, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"SQLite save_solution error: {e}")


def fetch_history(limit: int = 50) -> list:
    """Fetch recent solution history from Supabase or SQLite fallback."""
    sp = get_supabase_client()
    if sp:
        try:
            res = sp.table("solutions").select("*").order("created_at", desc=True).limit(limit).execute()
            if res.data:
                history = []
                for row in res.data:
                    history.append({
                        "question": row.get("question", ""),
                        "topic": row.get("topic", ""),
                        "answer": row.get("answer", ""),
                        "time": row.get("created_at", ""),
                        "steps": json.loads(row.get("steps_json", "[]")) if row.get("steps_json") else []
                    })
                return history
        except Exception as e:
            print(f"Supabase fetch history error ({e}), reading from SQLite.")

    # SQLite fallback
    history = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT question, topic, answer, steps_json, created_at
        FROM solutions
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        for q, t, a, s, created in rows:
            history.append({
                "question": q,
                "topic": t,
                "answer": a,
                "time": created,
                "steps": json.loads(s) if s else []
            })
    except Exception as e:
        print(f"SQLite fetch_history error: {e}")

    return history


def load_user_stats() -> dict:
    """Load persistent user stats (streak, xp, quiz accuracy)."""
    sp = get_supabase_client()
    if sp:
        try:
            res = sp.table("user_stats").select("*").eq("id", 1).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return {
                    "streak": row.get("streak", 0),
                    "xp": row.get("xp", 0),
                    "quiz_correct": row.get("quiz_correct", 0),
                    "quiz_total": row.get("quiz_total", 0)
                }
        except Exception as e:
            print(f"Supabase load_user_stats error ({e}), reading SQLite.")

    # SQLite fallback
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT streak, xp, quiz_correct, quiz_total FROM user_stats WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "streak": row[0],
                "xp": row[1],
                "quiz_correct": row[2],
                "quiz_total": row[3]
            }
    except Exception as e:
        print(f"SQLite load_user_stats error: {e}")

    return {"streak": 0, "xp": 0, "quiz_correct": 0, "quiz_total": 0}


def save_user_stats(streak: int, xp: int, quiz_correct: int, quiz_total: int):
    """Update user stats in Supabase or SQLite fallback."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sp = get_supabase_client()
    if sp:
        try:
            sp.table("user_stats").upsert({
                "id": 1,
                "streak": streak,
                "xp": xp,
                "quiz_correct": quiz_correct,
                "quiz_total": quiz_total,
                "updated_at": now
            }).execute()
            return
        except Exception as e:
            print(f"Supabase save_user_stats error ({e}), saving to SQLite.")

    # SQLite fallback
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE user_stats
        SET streak = ?, xp = ?, quiz_correct = ?, quiz_total = ?, updated_at = ?
        WHERE id = 1
        """, (streak, xp, quiz_correct, quiz_total, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"SQLite save_user_stats error: {e}")


def fetch_user_stats():
    """Wrapper returning tuple (streak, xp, quiz_correct, quiz_total)."""
    s = load_user_stats()
    return s.get("streak", 0), s.get("xp", 0), s.get("quiz_correct", 0), s.get("quiz_total", 0)

