"""
MathMate — Interactive Mathematics Lab
Structured according to Syllabus Requirements:

UNIT I: Practical based on basics of integers, real numbers and complex numbers
  1. Integers and Divisibility (Prime Factorization, Divisors, Primality)
  2. Computation of greatest common divisor using Euclid’s algorithm
  3. Complex Numbers & Polar Form

UNIT II: Practical based on Introduction to basic counting and basics of functions
  4. Permutations of Distinct Objects (n!, P(n,r), Circular)
  5. Combinations of Distinct Objects (C(n,r), Binomial)
  6. Injective, Bijective, Surjective Functions
  7. Inverse Images of Sets under Functions (f⁻¹(S))
"""

import sys
import os
from pathlib import Path

# Ensure current working directory & file parent are on sys.path for Streamlit Cloud
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import io
import re
import math
import random
import json
from datetime import datetime

import streamlit as st

# ============================================================
# PAGE CONFIG (MUST BE THE FIRST STREAMLIT COMMAND EXECUTED)
# ============================================================
st.set_page_config(
    page_title="MathMate — Interactive Mathematics Lab",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

import numpy as np
import plotly.graph_objects as go
import sympy as sp
from sympy import factorint, gcdex, mod_inverse

import database as db
if not hasattr(db, "init_db"):
    class DummyDB:
        @staticmethod
        def init_db(): pass
        @staticmethod
        def is_supabase_connected(): return False
        @staticmethod
        def save_solution(*args, **kwargs): pass
        @staticmethod
        def fetch_history(*args, **kwargs): return []
        @staticmethod
        def save_user_stats(*args, **kwargs): pass
        @staticmethod
        def fetch_user_stats(): return 0, 0, 0, 0
    db = DummyDB

# Pure Mathematical Solver Engine (No AI/LLM Dependencies)

# Optional export libs — degrade gracefully
try:
    from docx import Document
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# ============================================================
# STYLES & COLOR PALETTE
# ============================================================
INK = "#14213D"
PAPER = "#F7F5EF"
TEAL = "#2EC4B6"
AMBER = "#FFB627"
CORAL = "#E63946"
GRAPHITE = "#4A4E69"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
        background-color: #0A1226;
        color: #F7F5EF;
    }}
    
    .main .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }}
    
    .stApp {{
        background: radial-gradient(circle at 10% 20%, rgba(20, 33, 61, 0.95) 0%, rgba(10, 18, 38, 1) 90%);
    }}
    
    [data-testid="stSidebar"] {{
        background: #0D1B2A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }}
    
    .hero-title {{
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #2EC4B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }}
    
    .hero-subtitle {{
        font-size: 1.05rem;
        color: rgba(247, 245, 239, 0.75);
        font-weight: 400;
        margin-bottom: 1.5rem;
    }}
    
    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    
    .glass-card:hover {{
        border-color: rgba(46, 196, 182, 0.35);
    }}
    
    .topic-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        background: rgba(46, 196, 182, 0.15);
        color: #2EC4B6;
        border: 1px solid rgba(46, 196, 182, 0.3);
        margin-bottom: 8px;
    }}
    
    .timeline-step {{
        display: flex;
        align-items: flex-start;
        margin-bottom: 14px;
        position: relative;
    }}
    
    .timeline-num {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #2EC4B6;
        color: #0A1226;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
        margin-right: 14px;
        box-shadow: 0 0 12px rgba(46, 196, 182, 0.4);
    }}
    
    .timeline-content {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
        width: 100%;
    }}
    
    .timeline-title {{
        font-weight: 700;
        color: #FFFFFF;
        font-size: 1.05rem;
        margin-bottom: 4px;
    }}
    
    .timeline-body {{
        font-size: 0.92rem;
        color: rgba(247, 245, 239, 0.85);
        line-height: 1.5;
        white-space: pre-wrap;
    }}
    
    .answer-card {{
        background: linear-gradient(135deg, rgba(46, 196, 182, 0.2) 0%, rgba(20, 33, 61, 0.4) 100%);
        border: 2px solid #2EC4B6;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 10px 30px rgba(46, 196, 182, 0.2);
    }}
    
    .answer-badge {{
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        color: #2EC4B6;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    
    .answer-value {{
        font-size: 1.9rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
    }}
    
    .understand-card {{
        background: rgba(255, 182, 39, 0.06);
        border: 1px solid rgba(255, 182, 39, 0.25);
        border-radius: 14px;
        padding: 18px;
        margin-top: 20px;
    }}
    
    .understand-title {{
        color: #FFB627;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    div[data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }}
    
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #2EC4B6 0%, #1B9AAA 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(46, 196, 182, 0.3);
    }}
    
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 196, 182, 0.45);
    }}
    
    .hero-symbol-banner {{
        font-size: 2.2rem;
        opacity: 0.15;
        letter-spacing: 0.8rem;
        user-select: none;
        margin-bottom: -10px;
    }}

    .db-status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# STATE INITIALIZATION
# ============================================================
db.init_db()

if "streak" not in st.session_state or "xp" not in st.session_state:
    st_streak, st_xp, st_quiz_corr, st_quiz_tot = db.fetch_user_stats()
    st.session_state.streak = max(st_streak, 1)
    st.session_state.xp = st_xp
    st.session_state.quiz_score = {"correct": st_quiz_corr, "total": st_quiz_tot}
    st.session_state.stats_loaded = True


# ============================================================
# TOPIC DEFINITIONS & SYLLABUS METADATA (UNIT I & UNIT II)
# ============================================================
TOPICS = {
    # UNIT I
    "divisibility": "🔢 Integers & Divisibility",
    "gcd": "🧮 Computation of GCD using Euclid’s Algorithm",
    "complex": "📍 Complex Numbers & Polar Form",
    # UNIT II
    "perm": "🔀 Permutations of Distinct Objects",
    "comb": "🎲 Combinations of Distinct Objects",
    "functions": "🔗 Injective, Surjective & Bijective Functions",
    "inverse_image": "🔄 Inverse Images of Sets under Functions",
}

TOPIC_NAV_MAP = {
    "divisibility": "🔢 Integers & Divisibility",
    "gcd": "🧮 Computation of GCD using Euclid’s Algorithm",
    "complex": "📍 Complex Numbers & Polar Form",
    "perm": "🔀 Permutations of Distinct Objects",
    "comb": "🎲 Combinations of Distinct Objects",
    "functions": "🔗 Injective, Surjective & Bijective Functions",
    "inverse_image": "🔄 Inverse Images of Sets under Functions",
}

TOPIC_KEYWORDS = {
    "divisibility": ["divisibility", "prime factor", "factorization", "divisors", "prime test", "is prime", "factors of"],
    "gcd": ["gcd", "hcf", "euclidean", "euclid", "greatest common divisor", "euclid's algorithm", "highest common factor", "bezout"],
    "complex": ["polar form", "modulus", "argument", "rectangular form", "complex number", "argand", "imaginary", "real part"],
    "perm": ["permutation", "permutations", "arrange", "arrangement", "order", "sequence", "line", "row", "npr", "circular permutation"],
    "comb": ["combination", "combinations", "choose", "chosen", "select", "selection", "committee", "team", "pool", "ncr", "ways to choose"],
    "functions": ["injective", "surjective", "bijective", "one-one", "onto", "mapping", "domain", "codomain", "classification"],
    "inverse_image": ["inverse image", "pre-image", "preimage", "f^-1", "f inverse", "inverse of set", "pullback"],
}

TOPIC_CONCEPTS = {
    "divisibility": {
        "title": "Integers & Divisibility",
        "desc": "An integer a divides b (a | b) if b = a·c for some integer c. Every positive integer n > 1 can be uniquely factored into primes.",
        "formula": r"n = p_1^{e_1} \cdot p_2^{e_2} \cdots p_k^{e_k}",
        "identity": r"\tau(n) = \prod (e_i + 1), \quad \sigma(n) = \prod \frac{p_i^{e_i + 1} - 1}{p_i - 1}",
        "key_points": [
            "Fundamental Theorem of Arithmetic guarantees unique prime factorization.",
            "τ(n) gives the total number of positive divisors.",
            "σ(n) gives the sum of all positive divisors."
        ]
    },
    "gcd": {
        "title": "Computation of Greatest Common Divisor using Euclid’s Algorithm",
        "desc": "The Greatest Common Divisor (GCD) of two integers a and b is computed via repeated Euclidean division without prime factorization.",
        "formula": r"a = q \cdot b + r, \quad 0 \le r < b \implies \gcd(a, b) = \gcd(b, r)",
        "identity": r"a \cdot b = \gcd(a, b) \cdot \operatorname{lcm}(a, b) \quad \text{and} \quad a x + b y = \gcd(a, b)",
        "key_points": [
            "Euclidean Algorithm: repeated replacement a = q·b + r until remainder r = 0.",
            "The last non-zero remainder in the division chain is the exact GCD.",
            "Bézout's Identity: Extended Euclidean algorithm finds integers x, y satisfying ax + by = gcd(a,b)."
        ]
    },
    "complex": {
        "title": "Complex Numbers & Polar Form",
        "desc": "Complex numbers z = a + bi can be represented in polar coordinates (r, θ) on the Argand plane.",
        "formula": r"z = r(\cos\theta + i\sin\theta) = r e^{i\theta}",
        "identity": r"r = \sqrt{a^2 + b^2}, \quad \theta = \operatorname{atan2}(b, a)",
        "key_points": [
            "Modulus r is distance from origin on the Argand plane.",
            "Argument θ is angle with positive real axis.",
            "Euler's formula: e^{iθ} = cos θ + i sin θ."
        ]
    },
    "perm": {
        "title": "Permutations of Distinct Objects",
        "desc": "Permutations count ordered arrangements of n distinct objects taken r at a time.",
        "formula": r"P(n, r) = nPr = \frac{n!}{(n-r)!}",
        "identity": r"\text{Full Arrangement: } n!, \quad \text{Circular Permutations: } (n-1)!",
        "key_points": [
            "Order matters for Permutations.",
            "n! counts arrangements of all n distinct items in a row.",
            "Circular arrangements fix 1 position: (n-1)! ways."
        ]
    },
    "comb": {
        "title": "Combinations of Distinct Objects",
        "desc": "Combinations count unordered selections of r distinct objects from n.",
        "formula": r"C(n, r) = nCr = \binom{n}{r} = \frac{n!}{r!(n-r)!}",
        "identity": r"\binom{n}{r} = \binom{n}{n-r}, \quad \sum_{r=0}^n \binom{n}{r} = 2^n",
        "key_points": [
            "Order does NOT matter for Combinations.",
            "Symmetry: C(n, r) = C(n, n-r).",
            "Pascal's Identity: C(n, r) = C(n-1, r-1) + C(n-1, r)."
        ]
    },
    "functions": {
        "title": "Injective, Surjective & Bijective Functions",
        "desc": "Classification of functions based on mapping properties between Domain A and Codomain B.",
        "formula": r"f: A \to B",
        "identity": r"\text{Injective: } f(x_1)=f(x_2) \implies x_1=x_2, \quad \text{Surjective: } \operatorname{range}(f) = B",
        "key_points": [
            "Injective (One-to-One): No two domain elements map to same output.",
            "Surjective (Onto): Every element in codomain has at least one pre-image.",
            "Bijective: Both Injective and Surjective (Invertible)."
        ]
    },
    "inverse_image": {
        "title": "Inverse Images of Sets under Functions",
        "desc": "The inverse image (pre-image) f⁻¹(S) of a subset S ⊆ B is the set of all elements in domain A mapping into S.",
        "formula": r"f^{-1}(S) = \{ x \in A \mid f(x) \in S \}",
        "identity": r"f^{-1}(S_1 \cup S_2) = f^{-1}(S_1) \cup f^{-1}(S_2)",
        "key_points": [
            "f⁻¹(S) lives inside Domain A.",
            "Defined for ANY function, even if non-bijective / non-invertible.",
            "f⁻¹(Ø) = Ø and f⁻¹(Codomain B) = Domain A."
        ]
    }
}


# ============================================================
# HELPER PARSERS & STRING FORMATTERS
# ============================================================
def format_prime_factorization_latex(factor_dict: dict) -> str:
    """Format prime factorization dictionary {p: e} into LaTeX string like 2^{3} \\times 3^{2}."""
    if not factor_dict:
        return "1"
    parts = []
    for p in sorted(factor_dict.keys()):
        e = factor_dict[p]
        parts.append(f"{p}^{{{e}}}")
    return r" \times ".join(parts)


def format_prime_factorization_plain(factor_dict: dict) -> str:
    """Format prime factorization dictionary {p: e} into plain readable text like 2³ × 3²."""
    if not factor_dict:
        return "1"
    superscripts = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    parts = []
    for p in sorted(factor_dict.keys()):
        e = factor_dict[p]
        e_str = "".join(superscripts.get(ch, ch) for ch in str(e))
        parts.append(f"{p}{e_str}")
    return " × ".join(parts)


def clean_math_string(text: str) -> str:
    """Converts raw LaTeX string into clean readable text for HTML cards."""
    superscripts = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    t = text.replace(r"\gcd", "gcd").replace(r"\times", "×").replace(r"\cdot", "·").replace(r"\operatorname{lcm}", "lcm").replace(r"\text", "")
    t = re.sub(r"\^\{(\d+)\}", lambda m: "".join(superscripts.get(c, c) for c in m.group(1)), t)
    t = re.sub(r"\^(\d)", lambda m: superscripts.get(m.group(1), m.group(1)), t)
    t = t.replace("{", "").replace("}", "").replace("\\", "").strip()
    return t


def detect_topic(text: str) -> str:
    t = text.lower()
    scores = {k: 0 for k in TOPICS}
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[topic] += 1
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    if any(w in t for w in ["mod", "modulo", "congruence", "≡"]):
        return "congruence"
    elif any(w in t for w in ["factor", "divisible", "prime"]):
        return "divisibility"
    elif any(w in t for w in ["pre-image", "inverse image", "f^-1"]):
        return "inverse_image"
    elif any(w in t for w in ["choose", "select", "committee", "group"]):
        return "comb"
    return "gcd"


def extract_integers(text: str):
    return [int(x) for x in re.findall(r"-?\b\d+\b", text)]


def extract_complex_parts(text: str):
    t = text.replace(" ", "")
    m = re.search(r"z?\=?([+-]?\d+\.?\d*)\s*([+-]\s*\d*\.?\d*)[ij]", t, re.IGNORECASE)
    if m:
        a = float(m.group(1))
        b_str = m.group(2).replace(" ", "")
        b = 1.0 if b_str in ["+", ""] else -1.0 if b_str == "-" else float(b_str)
        return a, b

    m_pure_im = re.search(r"([+-]?\d*\.?\d*)[ij]", t, re.IGNORECASE)
    if m_pure_im and not re.search(r"[+-]\d", t):
        val = m_pure_im.group(1)
        b = 1.0 if val in ["", "+"] else -1.0 if val == "-" else float(val)
        return 0.0, b

    m_real = re.search(r"([+-]?\d+\.?\d*)", t)
    if m_real:
        return float(m_real.group(1)), 0.0
    return 1.0, 1.7320508


def parse_question(text: str):
    topic = detect_topic(text)
    nums = extract_integers(text)

    if topic == "gcd":
        a = nums[0] if len(nums) >= 1 else 1071
        b = nums[1] if len(nums) >= 2 else 462
        return topic, {"a": a, "b": b}
    elif topic == "divisibility":
        n = nums[0] if len(nums) >= 1 else 360
        return topic, {"n": abs(n)}
    elif topic == "complex":
        a, b = extract_complex_parts(text)
        return topic, {"a": a, "b": b}
    elif topic in ["perm", "comb"]:
        n = max(nums[0], nums[1]) if len(nums) >= 2 else nums[0] if len(nums) == 1 else 7
        r = min(nums[0], nums[1]) if len(nums) >= 2 else 3
        return topic, {"n": abs(n), "r": abs(r)}
    return topic, {}

        n = max(nums[0], nums[1]) if len(nums) >= 2 else nums[0] if len(nums) == 1 else 7
        r = min(nums[0], nums[1]) if len(nums) >= 2 else 3
        return topic, {"n": abs(n), "r": abs(r)}
    return topic, {}


# ============================================================
# CORE MATHEMATICAL SOLVER ALGORITHMS
# ============================================================

def solve_divisibility(n: int):
    """UNIT I: Integers and divisibility solver."""
    n = abs(n)
    if n <= 1:
        return [("Input Validation", f"Integer n = {n} must be greater than 1 for prime factorization analysis.")], "n > 1 required", {}

    steps = []
    steps.append(("Input Specification", f"Analyze integer n = {n}"))

    is_prime = sp.isprime(n)
    steps.append(("Primality Test", f"Is {n} prime? {'YES (Prime)' if is_prime else 'NO (Composite)'}"))

    factors = factorint(n)
    fact_plain = format_prime_factorization_plain(factors)
    fact_latex = format_prime_factorization_latex(factors)
    steps.append(("Prime Factorization", f"Factorization: {n} = {fact_plain}"))

    divisors = sorted(sp.divisors(n))
    tau = len(divisors)
    sigma = sum(divisors)

    steps.append(("Divisor Enumeration & Counting Functions",
                  f"Divisors of {n}: {divisors}\n"
                  f"Total Number of Divisors τ({n}) = {tau}\n"
                  f"Sum of Divisors σ({n}) = {sigma}"))

    ans_str = f"{n} = {fact_plain} | τ({n}) = {tau} | σ({n}) = {sigma}"
    ans_latex = fr"{n} = {fact_latex} \implies \tau({n}) = {tau}, \ \sigma({n}) = {sigma}"
    return steps, ans_str, {
        "n": n, "is_prime": is_prime, "factors": factors,
        "divisors": divisors, "tau": tau, "sigma": sigma,
        "fact_plain": fact_plain, "fact_latex": fact_latex,
        "latex_ans": ans_latex
    }


def compute_extended_euclidean_table(a: int, b: int):
    """
    Computes rows for the Extended Euclidean Algorithm Table:
    Columns: Step (i), Dividend, Divisor, Quotient (q), Remainder (r), x, y
    satisfying a*x + b*y = r at each row.
    """
    a_orig, b_orig = a, b
    rows = []

    r0, r1 = a, b
    x0, x1 = 1, 0
    y0, y1 = 0, 1

    rows.append({
        "Step (i)": 0,
        "Dividend": a_orig,
        "Divisor": b_orig,
        "Quotient (q)": "—",
        "Remainder (r)": r0,
        "x": x0,
        "y": y0,
        "is_gcd": False
    })

    rows.append({
        "Step (i)": 1,
        "Dividend": a_orig,
        "Divisor": b_orig,
        "Quotient (q)": "—",
        "Remainder (r)": r1,
        "x": x1,
        "y": y1,
        "is_gcd": False
    })

    step_i = 2
    last_gcd_idx = -1
    while r1 != 0:
        q = r0 // r1
        r2 = r0 % r1
        x2 = x0 - q * x1
        y2 = y0 - q * y1

        rows.append({
            "Step (i)": step_i,
            "Dividend": r0,
            "Divisor": r1,
            "Quotient (q)": q,
            "Remainder (r)": r2,
            "x": x2,
            "y": y2,
            "is_gcd": False
        })

        if r2 != 0:
            last_gcd_idx = len(rows) - 1

        r0, r1 = r1, r2
        x0, x1 = x1, x2
        y0, y1 = y1, y2
        step_i += 1

    if last_gcd_idx != -1:
        rows[last_gcd_idx]["is_gcd"] = True

    return rows


def solve_gcd_euclidean(a: int, b: int):
    """UNIT I: Computation of greatest common divisor using Euclid's algorithm."""
    orig_a, orig_b = a, b
    a_abs, b_abs = abs(a), abs(b)
    if a_abs == 0 or b_abs == 0:
        return [("Validation Error", "Both integers must be non-zero.")], "Invalid input", {}

    steps = []
    steps.append(("Input Specification", f"Compute gcd({orig_a}, {orig_b}) strictly using Euclid's Algorithm."))

    u, v = a_abs, b_abs
    if u < v:
        steps.append(("Ordering Adjustment", f"Swap inputs so larger integer is dividend: a = {v}, b = {u}"))
        u, v = v, u

    euclid_steps = []
    step_idx = 1
    curr_a, curr_b = u, v

    while curr_b != 0:
        q = curr_a // curr_b
        r = curr_a % curr_b
        euclid_steps.append(f"Step {step_idx}: {curr_a} = {q} × {curr_b} + {r}  (q = {q}, r = {r})")
        curr_a, curr_b = curr_b, r
        step_idx += 1

    gcd_val = curr_a
    steps.append(("Euclidean Algorithm Division Steps", "\n".join(euclid_steps)))
    steps.append(("Euclidean GCD Result", f"The last non-zero remainder in the division chain is {gcd_val}.\nThus, gcd({orig_a}, {orig_b}) = {gcd_val}."))

    table_rows = compute_extended_euclidean_table(u, v)
    g, x_bez, y_bez = gcdex(a_abs, b_abs)
    bezout_str = f"({x_bez}) × ({a_abs}) + ({y_bez}) × ({b_abs}) = {gcd_val}"
    steps.append(("Bézout's Identity (Extended Euclidean Algorithm)",
                  f"Extended Euclidean Algorithm expresses GCD as a linear combination:\n"
                  f"gcd({a_abs}, {b_abs}) = ({x_bez}) × {a_abs} + ({y_bez}) × {b_abs} = {gcd_val}"))

    lcm_val = math.lcm(a_abs, b_abs)
    steps.append(("Fundamental Theorem Connection (GCD & LCM)",
                  f"Product relation verification: a × b = gcd(a,b) × lcm(a,b)\n"
                  f"{a_abs} × {b_abs} = {a_abs * b_abs}\n"
                  f"gcd({a_abs}, {b_abs}) × lcm({a_abs}, {b_abs}) = {gcd_val} × {lcm_val} = {gcd_val * lcm_val}\n"
                  f"lcm({orig_a}, {orig_b}) = {lcm_val}"))

    ans_str = f"gcd({orig_a}, {orig_b}) = {gcd_val}"
    ans_latex = fr"\gcd({orig_a}, {orig_b}) = {gcd_val}"

    return steps, ans_str, {
        "gcd": gcd_val, "lcm": lcm_val, "a": a_abs, "b": b_abs,
        "x_bez": x_bez, "y_bez": y_bez, "table_rows": table_rows,
        "bezout_str": bezout_str, "latex_ans": ans_latex
    }





def solve_complex_to_polar(a: float, b: float):
    """UNIT I: Complex Numbers & Polar Form."""
    steps = []
    steps.append(("Identify Rectangular Parts", f"z = a + bi with Real part a = {a}, Imaginary part b = {b}"))
    r = math.hypot(a, b)
    steps.append(("Compute Modulus (r)", f"r = √(a² + b²) = √(({a})² + ({b})²) = √({a**2 + b**2:.4f}) = {r:.4f}"))
    theta_rad = math.atan2(b, a)
    theta_deg = math.degrees(theta_rad)
    quadrant = "Quadrant I" if a >= 0 and b >= 0 else "Quadrant II" if a < 0 and b >= 0 else "Quadrant III" if a < 0 and b < 0 else "Quadrant IV"
    steps.append(("Compute Argument (θ)", f"θ = atan2(b, a) = atan2({b}, {a}) = {theta_rad:.4f} rad ({theta_deg:.2f}°)\nLocated in {quadrant}"))

    polar_str = f"z = {r:.4f} (cos({theta_deg:.2f}°) + i sin({theta_deg:.2f}°))"
    polar_latex = fr"z = {r:.4f} \left(\cos({theta_deg:.2f}^\circ) + i \sin({theta_deg:.2f}^\circ)\right)"

    steps.append(("Polar & Exponential Forms", f"Polar Form: {polar_str}\nExponential Form: z = {r:.4f} e^({theta_rad:.4f}i)"))
    return steps, polar_str, {"r": r, "theta_rad": theta_rad, "theta_deg": theta_deg, "a": a, "b": b, "latex_ans": polar_latex}


def solve_perm(n: int, r: int):
    """UNIT II: Permutations of distinct objects."""
    steps = []
    if r > n or n < 0 or r < 0:
        return [("Validation Error", "Requirements: n ≥ r ≥ 0.")], "Invalid input", {}

    val_npr = math.perm(n, r)
    val_fact = math.factorial(n)
    val_circ = math.factorial(n - 1) if n >= 1 else 0

    steps.append(("Formula Selection", f"Permutations P(n, r) = n! / (n - r)!"))
    steps.append(("Value Substitution", f"P({n}, {r}) = {n}! / ({n} - {r})! = {n}! / {n-r}!"))

    terms = " × ".join(str(i) for i in range(n, n - r, -1)) if r > 0 else "1"
    steps.append(("Expanded Product", f"P({n}, {r}) = {terms} = {val_npr}"))

    extra_info = (f"Related Permutation Types:\n"
                  f"• Full Arrangement of all {n} objects in a row: {n}! = {val_fact}\n"
                  f"• Circular Permutations of {n} objects around a table: ({n}-1)! = {val_circ}")
    steps.append(("Special Permutation Scenarios", extra_info))

    ans_str = f"P({n}, {r}) = {val_npr}"
    ans_latex = fr"P({n}, {r}) = {val_npr}"
    return steps, ans_str, {"val": val_npr, "n": n, "r": r, "n_fact": val_fact, "circular": val_circ, "latex_ans": ans_latex}


def solve_comb(n: int, r: int):
    """UNIT II: Combinations of distinct objects."""
    steps = []
    if r > n or n < 0 or r < 0:
        return [("Validation Error", "Requirements: n ≥ r ≥ 0.")], "Invalid input", {}

    val_ncr = math.comb(n, r)
    steps.append(("Formula Selection", f"Combinations C(n, r) = n! / (r! × (n - r)!)"))
    steps.append(("Value Substitution", f"C({n}, {r}) = {n}! / ({r}! × ({n} - {r})!)"))

    num_terms = " × ".join(str(i) for i in range(n, n - r, -1)) if r > 0 else "1"
    den_terms = " × ".join(str(i) for i in range(1, r + 1)) if r > 0 else "1"
    steps.append(("Simplified Product Ratio", f"C({n}, {r}) = ({num_terms}) / ({den_terms}) = {val_ncr}"))

    comp_r = n - r
    steps.append(("Symmetry Property", f"C({n}, {r}) = C({n}, {comp_r}) = {val_ncr}"))

    ans_str = f"C({n}, {r}) = {val_ncr}"
    ans_latex = fr"\binom{{{n}}}{{{r}}} = C({n}, {r}) = {val_ncr}"
    return steps, ans_str, {"val": val_ncr, "n": n, "r": r, "latex_ans": ans_latex}


def solve_functions(domain: list, codomain: list, mapping: dict):
    """UNIT II: Injective, Bijective, Surjective functions."""
    steps = []
    steps.append(("Domain & Codomain Setup", f"Domain A = {{{', '.join(map(str, domain))}}}\nCodomain B = {{{', '.join(map(str, codomain))}}}"))
    map_str = ", ".join(f"f({k})={v}" for k, v in mapping.items())
    steps.append(("Mapping Definition", f"Mappings: {map_str}"))

    mapped_values = list(mapping.values())
    is_injective = len(mapped_values) == len(set(mapped_values))
    if is_injective:
        steps.append(("Injectivity Test (One-to-One)", "PASSED: All outputs are distinct. Function is INJECTIVE."))
    else:
        duplicates = [x for x in set(mapped_values) if mapped_values.count(x) > 1]
        steps.append(("Injectivity Test (One-to-One)", f"FAILED: Multiple domain inputs map to same codomain element(s): {duplicates}. NOT Injective."))

    range_set = set(mapped_values)
    codomain_set = set(codomain)
    is_surjective = range_set == codomain_set
    if is_surjective:
        steps.append(("Surjectivity Test (Onto)", "PASSED: Range equals Codomain. Function is SURJECTIVE."))
    else:
        uncovered = list(codomain_set - range_set)
        steps.append(("Surjectivity Test (Onto)", f"FAILED: Uncovered element(s): {uncovered}. NOT Surjective."))

    is_bijective = is_injective and is_surjective
    classification = "BIJECTIVE (Injective & Surjective)" if is_bijective else \
                     "INJECTIVE ONLY (One-to-One, not Onto)" if is_injective else \
                     "SURJECTIVE ONLY (Onto, not One-to-One)" if is_surjective else \
                     "NEITHER (Neither Injective nor Surjective)"

    steps.append(("Final Classification", f"Classification: {classification}"))
    return steps, classification, {"injective": is_injective, "surjective": is_surjective, "bijective": is_bijective, "classification": classification}


def solve_inverse_image(domain: list, codomain: list, mapping: dict, target_set: list):
    """UNIT II: Inverse images of sets under functions f⁻¹(S)."""
    steps = []
    steps.append(("Function Specification", f"f: Domain A {{{', '.join(map(str, domain))}}} → Codomain B {{{', '.join(map(str, codomain))}}}"))
    target_set_clean = [str(y).strip() for y in target_set if str(y).strip()]
    steps.append(("Target Subset S ⊆ B", f"Target Subset S = {{{', '.join(target_set_clean)}}}"))

    pre_images = []
    element_breakdown = []
    for y in target_set_clean:
        pre_y = [x for x, val in mapping.items() if str(val).strip() == y]
        pre_images.extend(pre_y)
        element_breakdown.append(f"• Element '{y}': pre-images = {{{', '.join(pre_y) if pre_y else 'Ø'}}}")

    unique_preimages = sorted(list(set(pre_images)))
    steps.append(("Element-by-Element Pre-image Lookup", "\n".join(element_breakdown)))

    pre_str = ', '.join(unique_preimages) if unique_preimages else 'Ø'
    ans_str = f"f⁻¹({{{', '.join(target_set_clean)}}}) = {{{pre_str}}}"

    latex_pre_str = ', '.join(unique_preimages) if unique_preimages else r'\emptyset'
    latex_target_str = ', '.join(target_set_clean)
    ans_latex = fr"f^{{-1}}\left(\{{{latex_target_str}\}}\right) = \{{{latex_pre_str}\}}"

    steps.append(("Inverse Image Set Result", f"f⁻¹(S) = {{ x ∈ A | f(x) ∈ S }} = {{{pre_str}}}"))
    return steps, ans_str, {"preimages": unique_preimages, "target_set": target_set_clean, "latex_ans": ans_latex}


# ============================================================
# RICH MATHEMATICAL VISUALIZATIONS (PLOTLY & HTML ENGINES)
# ============================================================

def render_euclidean_html_table(rows: list):
    """Textbook Extended Euclidean Table UI Renderer."""
    html_lines = [
        '<div style="overflow-x:auto; margin-top:10px;">',
        '<table style="width:100%; border-collapse:collapse; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.12); border-radius:12px; font-size:0.92rem; text-align:center;">',
        '<thead>',
        '<tr style="background:rgba(46, 196, 182, 0.2); color:#2EC4B6; border-bottom:1px solid rgba(46,196,182,0.3); font-weight:700;">',
        '<th style="padding:10px;">Step (i)</th>',
        '<th style="padding:10px;">Dividend (a)</th>',
        '<th style="padding:10px;">Divisor (b)</th>',
        '<th style="padding:10px;">Quotient (q)</th>',
        '<th style="padding:10px;">Remainder (r)</th>',
        '<th style="padding:10px;">x</th>',
        '<th style="padding:10px;">y</th>',
        '</tr>',
        '</thead>',
        '<tbody>'
    ]
    for r in rows:
        is_gcd = r.get("is_gcd", False)
        bg = "background:rgba(46,196,182,0.3); color:#FFFFFF; font-weight:800;" if is_gcd else ""
        gcd_mark = " ⭐ (GCD)" if is_gcd else ""
        html_lines.append(
            f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05); {bg}">'
            f'<td style="padding:8px;">{r["Step (i)"]}</td>'
            f'<td style="padding:8px;">{r["Dividend"]}</td>'
            f'<td style="padding:8px;">{r["Divisor"]}</td>'
            f'<td style="padding:8px;">{r["Quotient (q)"]}</td>'
            f'<td style="padding:8px; color:{TEAL if is_gcd else "#FFFFFF"};">{r["Remainder (r)"]}{gcd_mark}</td>'
            f'<td style="padding:8px;">{r["x"]}</td>'
            f'<td style="padding:8px;">{r["y"]}</td>'
            f'</tr>'
        )
    html_lines.append('</tbody></table></div>')
    table_html = "".join(html_lines)
    st.markdown(table_html, unsafe_allow_html=True)






def plot_function_diagram_plotly(domain: list, codomain: list, mapping: dict, highlight_target_set: list = None):
    fig = go.Figure()
    d_len = len(domain)
    c_len = len(codomain)

    d_y = np.linspace(1, 0, d_len) if d_len > 1 else [0.5]
    c_y = np.linspace(1, 0, c_len) if c_len > 1 else [0.5]

    d_pos = {elem: (0, d_y[i]) for i, elem in enumerate(domain)}
    c_pos = {elem: (1, c_y[i]) for i, elem in enumerate(codomain)}

    hl_set = set(highlight_target_set or [])

    for dom_elem, codom_elem in mapping.items():
        if dom_elem in d_pos and codom_elem in c_pos:
            x0, y0 = d_pos[dom_elem]
            x1, y1 = c_pos[codom_elem]
            is_hl = codom_elem in hl_set
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines', line=dict(color=AMBER if is_hl else TEAL, width=3.5 if is_hl else 2.0),
                hoverinfo='skip', showlegend=False
            ))

    dx = [pos[0] for pos in d_pos.values()]
    dy = [pos[1] for pos in d_pos.values()]
    dtxt = [str(k) for k in d_pos.keys()]

    d_colors = []
    for k in d_pos.keys():
        if mapping.get(k) in hl_set:
            d_colors.append(AMBER)
        else:
            d_colors.append(TEAL)

    fig.add_trace(go.Scatter(
        x=dx, y=dy, mode='markers+text',
        marker=dict(size=28, color=d_colors, line=dict(width=2, color='#FFFFFF')),
        text=dtxt, textposition="middle center",
        textfont=dict(color="#000000", weight="bold"),
        hoverinfo='text', hovertext=[f"Domain element: {t}" for t in dtxt],
        name="Domain A"
    ))

    cx = [pos[0] for pos in c_pos.values()]
    cy = [pos[1] for pos in c_pos.values()]
    ctxt = [str(k) for k in c_pos.keys()]
    c_colors = [CORAL if k in hl_set else GRAPHITE for k in c_pos.keys()]

    fig.add_trace(go.Scatter(
        x=cx, y=cy, mode='markers+text',
        marker=dict(size=28, color=c_colors, line=dict(width=2, color='#FFFFFF')),
        text=ctxt, textposition="middle center",
        textfont=dict(color="#FFFFFF", weight="bold"),
        hoverinfo='text', hovertext=[f"Codomain element: {t}" for t in ctxt],
        name="Codomain B"
    ))

    fig.update_layout(
        xaxis=dict(range=[-0.3, 1.3], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-0.15, 1.15], showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,18,38,0.6)",
        font=dict(color="#FFFFFF", family="Outfit"),
        annotations=[
            dict(x=0, y=1.1, text="<b>Domain A</b>", showarrow=False, font=dict(size=14, color=TEAL)),
            dict(x=1, y=1.1, text="<b>Codomain B</b>", showarrow=False, font=dict(size=14, color=CORAL)),
        ],
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        height=380
    )
    return fig


# ============================================================
# PROCEDURAL QUIZ GENERATOR
# ============================================================
def generate_procedural_question(topic_key: str = None):
    if not topic_key or topic_key not in TOPICS:
        topic_key = random.choice(list(TOPICS.keys()))

    if topic_key == "divisibility":
        n = random.randint(30, 200)
        steps, ans, extra = solve_divisibility(n)
        correct = str(extra["tau"])
        opts = {correct, str(extra["tau"] + 2), str(max(1, extra["tau"] - 2)), str(extra["tau"] + 4)}
        while len(opts) < 4:
            opts.add(str(random.randint(2, 20)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"How many total positive divisors τ({n}) does the integer {n} have?",
            "topic": "divisibility",
            "options": opts,
            "answer": correct,
            "exp": f"Prime factorization of {n}: {extra['fact_plain']}\nτ({n}) = {extra['tau']}."
        }

    elif topic_key == "gcd":
        a = random.randint(100, 1500)
        b = random.randint(24, 450)
        steps, ans, extra = solve_gcd_euclidean(a, b)
        correct = str(extra["gcd"])
        opts = {correct, str(int(correct) + 2), str(max(1, int(correct) - 2)), str(int(correct) * 2)}
        while len(opts) < 4:
            opts.add(str(random.randint(1, 20)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"Find gcd({a}, {b}) strictly using Euclid's division algorithm.",
            "topic": "gcd",
            "options": opts,
            "answer": correct,
            "exp": f"Euclidean division breakdown yields last non-zero remainder gcd({a}, {b}) = {correct}."
        }



    elif topic_key == "complex":
        a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        b = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        deg = math.degrees(math.atan2(b, a))
        correct = f"{deg:.1f}°"
        opts = [f"{deg:.1f}°", f"{(deg + 45) % 360:.1f}°", f"{(deg + 90) % 360:.1f}°", f"{(deg - 30) % 360:.1f}°"]
        random.shuffle(opts)
        return {
            "q": f"Find the principal argument θ (in degrees) for z = {a} + {b}i.",
            "topic": "complex",
            "options": opts,
            "answer": correct,
            "exp": f"θ = atan2({b}, {a}) = {deg:.2f}°."
        }

    elif topic_key in ["perm", "comb"]:
        kind = "P" if topic_key == "perm" else "C"
        n = random.randint(5, 9)
        r = random.randint(2, 4)
        ans = math.perm(n, r) if kind == "P" else math.comb(n, r)
        correct = str(ans)
        opts = {correct, str(ans + 5), str(max(1, ans - 3)), str(ans * 2)}
        while len(opts) < 4:
            opts.add(str(random.randint(5, 100)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"Evaluate {n}{kind}{r} ({'Permutations' if kind=='P' else 'Combinations'}).",
            "topic": topic_key,
            "options": opts,
            "answer": correct,
            "exp": f"{n}{kind}{r} = {ans}."
        }

    elif topic_key == "functions":
        d = ["1", "2", "3"]
        c = ["a", "b", "c"] if random.random() > 0.5 else ["a", "b"]
        mapping = {"1": "a", "2": "b", "3": "c" if len(c) == 3 else "a"}
        steps, ans, extra = solve_functions(d, c, mapping)
        correct = "Yes" if extra["injective"] else "No"
        return {
            "q": f"Function f: {{{','.join(d)}}} → {{{','.join(c)}}} with f(1)={mapping['1']}, f(2)={mapping['2']}, f(3)={mapping['3']}. Is f Injective?",
            "topic": "functions",
            "options": ["Yes", "No"],
            "answer": correct,
            "exp": f"Injectivity check: {steps[2][1]}"
        }

    else:  # inverse_image
        d = ["1", "2", "3", "4"]
        c = ["a", "b", "c"]
        mapping = {"1": "a", "2": "b", "3": "a", "4": "c"}
        target = ["a"]
        steps, ans, extra = solve_inverse_image(d, c, mapping, target)
        correct = f"{{{', '.join(extra['preimages'])}}}"
        opts = [correct, "{1}", "{3}", "{1, 2, 3}"]
        random.shuffle(opts)
        return {
            "q": f"Given f(1)=a, f(2)=b, f(3)=a, f(4)=c. Find the inverse image f⁻¹({{a}}).",
            "topic": "inverse_image",
            "options": opts,
            "answer": correct,
            "exp": f"Elements mapping to 'a' are 1 and 3. So f⁻¹({{a}}) = {{1, 3}}."
        }


# ============================================================
# UI RENDER HELPERS
# ============================================================
def render_step_timeline(steps):
    for i, (title, body) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="timeline-step">
            <div class="timeline-num">{i}</div>
            <div class="timeline-content">
                <div class="timeline-title">{title}</div>
                <div class="timeline-body">{body}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_understand_panel(topic_key):
    c = TOPIC_CONCEPTS.get(topic_key, {})
    if not c:
        return

    st.markdown(f"""
    <div class="understand-card">
        <div class="understand-title">💡 KEY THEOREM & FORMULA</div>
        <div style="font-weight:700; font-size:1.1rem; color:#FFFFFF; margin-bottom:8px;">{c['title']}</div>
        <div style="font-size:0.9rem; color:rgba(247,245,239,0.8); line-height:1.45; margin-bottom:12px;">{c['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
    st.latex(c['formula'])
    st.latex(c['identity'])
    for pt in c['key_points']:
        st.markdown(f"• {pt}")


def format_full_solution_text(question_text: str, topic_name: str, steps: list, answer: str) -> str:
    lines = []
    lines.append(f"📌 TOPIC: {topic_name}")
    if question_text:
        lines.append(f"❓ QUESTION: {question_text}")
    lines.append("\n📚 STEP-BY-STEP SOLUTION:")
    if steps:
        for i, step in enumerate(steps, 1):
            if isinstance(step, (tuple, list)) and len(step) >= 2:
                title, body = step[0], step[1]
            else:
                title, body = f"Step {i}", str(step)
            clean_title = re.sub(r'<[^>]+>', '', str(title))
            clean_body = re.sub(r'<[^>]+>', '', str(body))
            lines.append(f"\n  Step {i}: {clean_title}")
            lines.append(f"    {clean_body.strip()}")
    
    clean_ans = re.sub(r'<[^>]+>', '', str(answer))
    lines.append(f"\n✅ FINAL ANSWER: {clean_ans.strip()}")
    return "\n".join(lines)


def build_docx(question_text: str, topic_name: str, steps: list, answer: str) -> io.BytesIO:
    if not DOCX_AVAILABLE:
        return None
    doc = Document()
    doc.add_heading('MathMate — Interactive Mathematics Lab', level=0)
    doc.add_heading(f'Topic: {topic_name}', level=2)
    if question_text:
        doc.add_paragraph(f'Question: {question_text}')
    
    doc.add_heading('Step-by-Step Reasoning:', level=2)
    if steps:
        for i, step in enumerate(steps, 1):
            if isinstance(step, (tuple, list)) and len(step) >= 2:
                title, body = step[0], step[1]
            else:
                title, body = f'Step {i}', str(step)
            clean_title = re.sub(r'<[^>]+>', '', str(title))
            clean_body = re.sub(r'<[^>]+>', '', str(body))
            p = doc.add_paragraph()
            p.add_run(f'Step {i}: {clean_title}\n').bold = True
            p.add_run(f'{clean_body.strip()}\n')
            
    doc.add_heading('Final Answer:', level=2)
    clean_ans = re.sub(r'<[^>]+>', '', str(answer))
    p_ans = doc.add_paragraph()
    p_ans.add_run(f'{clean_ans.strip()}').bold = True
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def build_pdf(question_text: str, topic_name: str, steps: list, answer: str) -> io.BytesIO:
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    body_style = styles['Normal']
    
    story.append(Paragraph("<b>MathMate — Interactive Mathematics Lab</b>", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Topic:</b> {topic_name}", subtitle_style))
    story.append(Spacer(1, 10))
    
    if question_text:
        clean_q = re.sub(r'<[^>]+>', '', str(question_text))
        story.append(Paragraph(f"<b>Question:</b> {clean_q}", body_style))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("<b>Step-by-Step Reasoning:</b>", subtitle_style))
    story.append(Spacer(1, 8))
    
    if steps:
        for i, step in enumerate(steps, 1):
            if isinstance(step, (tuple, list)) and len(step) >= 2:
                title, body = step[0], step[1]
            else:
                title, body = f'Step {i}', str(step)
            clean_title = re.sub(r'<[^>]+>', '', str(title))
            clean_body = re.sub(r'<[^>]+>', '', str(body)).replace('\n', '<br/>')
            story.append(Paragraph(f"<b>Step {i}: {clean_title}</b>", body_style))
            story.append(Paragraph(f"{clean_body}", body_style))
            story.append(Spacer(1, 6))
            
    clean_ans = re.sub(r'<[^>]+>', '', str(answer))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Final Answer: {clean_ans}</b>", subtitle_style))
    
    doc.build(story)
    buf.seek(0)
    return buf


def render_answer_card(answer: str, latex_ans: str = None, question_text: str = "", topic_name: str = "", steps: list = None):
    display_ans = clean_math_string(answer)
    st.markdown(f"""
    <div class="answer-card">
        <div class="answer-badge">FINAL ANSWER</div>
        <div class="answer-value">{display_ans}</div>
        <div style="font-size:0.82rem; color:#2EC4B6; font-weight:700; margin-top:6px;">✓ Computed & Verified</div>
    </div>
    """, unsafe_allow_html=True)
    if latex_ans:
        st.latex(latex_ans)
    if steps:
        full_text = format_full_solution_text(question_text, topic_name, steps, answer)
        with st.expander("📋 Copy Full Step-by-Step Solution", expanded=True):
            st.code(full_text, language=None)

        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        st.markdown("**💾 Export & Download Solution**")
        c_doc, c_pdf = st.columns(2)
        with c_doc:
            if DOCX_AVAILABLE:
                docx_buf = build_docx(question_text, topic_name, steps, answer)
                if docx_buf:
                    st.download_button(
                        label="📄 Word (.docx)",
                        data=docx_buf,
                        file_name="MathMate_solution.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            else:
                st.caption("Install python-docx for Word exports")

        with c_pdf:
            if REPORTLAB_AVAILABLE:
                pdf_buf = build_pdf(question_text, topic_name, steps, answer)
                if pdf_buf:
                    st.download_button(
                        label="📥 PDF (.pdf)",
                        data=pdf_buf,
                        file_name="MathMate_solution.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.caption("Install reportlab for PDF exports")





def set_nav_page(target_page, preset_q=None):
    st.session_state.nav_page = target_page
    if preset_q:
        st.session_state.preset_question = preset_q


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown("""
<div style="text-align: left; padding: 4px 0 12px 0;">
    <div style="font-size: 1.6rem; font-weight: 800; color: #2EC4B6; letter-spacing: -0.02em;">🧮 MATHMATE</div>
    <div style="font-size: 0.78rem; color: rgba(247,245,239,0.65);">Interactive Mathematics Lab</div>
</div>
""", unsafe_allow_html=True)

if db.is_supabase_connected():
    st.sidebar.markdown('<div class="db-status-badge" style="background:rgba(46,196,182,0.2); color:#2EC4B6; border:1px solid #2EC4B6;">🟢 Supabase Cloud Active</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="db-status-badge" style="background:rgba(255,182,39,0.2); color:#FFB627; border:1px solid #FFB627;">🟡 SQLite Local Fallback</div>', unsafe_allow_html=True)

NAV_PAGES = [
    "🏠 Home",
    "🔢 Integers & Divisibility",
    "🧮 Computation of GCD using Euclid’s Algorithm",
    "📍 Complex Numbers & Polar Form",
    "🔀 Permutations of Distinct Objects",
    "🎲 Combinations of Distinct Objects",
    "🔗 Injective, Surjective & Bijective Functions",
    "🔄 Inverse Images of Sets under Functions",
    "🧠 Quiz & Practice",
    "📐 Formula Cheat Sheet",
    "📜 Solution History"
]

if "redirect_page" in st.session_state:
    st.session_state.nav_page = st.session_state.pop("redirect_page")
elif "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Home"

page = st.sidebar.radio("Navigate", NAV_PAGES, key="nav_page", label_visibility="collapsed")

st.sidebar.markdown("---")
streak = st.session_state.streak
xp = st.session_state.xp
tier_badge = "🌱 Novice" if xp < 50 else "🥉 Apprentice" if xp < 150 else "🥈 Scholar" if xp < 300 else "👑 Math Wizard"
st.sidebar.metric("🔥 Streak & XP", f"{streak} Days · {xp} XP")
st.sidebar.caption(f"Rank Tier: {tier_badge}")

if st.session_state.quiz_score["total"] > 0:
    pct = round(100 * st.session_state.quiz_score["correct"] / st.session_state.quiz_score["total"])
    st.sidebar.metric("🎯 Quiz Accuracy", f"{pct}%")


# ============================================================
# PAGE: HOME
# ============================================================
if page == "🏠 Home":
    st.markdown('<div class="hero-symbol-banner">∫   Σ   ≡   √   π   ∞</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">MATHMATE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Interactive Mathematics Lab · UNIT I & UNIT II Syllabus Modules</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="padding: 26px; border: 1px solid rgba(46, 196, 182, 0.35);">
        <div style="font-weight:800; font-size:1.35rem; color:#FFFFFF; margin-bottom:4px;">✨ What would you like to solve?</div>
        <div style="font-size:0.88rem; color:rgba(247,245,239,0.7); margin-bottom:16px;">Type or paste any syllabus problem below:</div>
    """, unsafe_allow_html=True)

    home_q_input = st.text_area("Question Input", key="home_question_input",
                                placeholder="e.g. Find GCD of 1071 and 462 using Euclid's algorithm  OR  Convert z = 1 + 1.732i to polar form",
                                height=85, label_visibility="collapsed")

    st.caption("Quick sample questions:")
    sample_qs = {
        "divisibility": "Prime factorization and divisors of 360",
        "gcd": "Find GCD of 1071 and 462 using Euclid's algorithm",
        "complex": "Convert z = 1 + 1.73205i to polar form",
        "perm": "Permutations P(7, 3) of 7 distinct objects",
        "comb": "Choose 4 members from a group of 9 available employees",
        "functions": "Domain: 1, 2, 3. Codomain: a, b, c. Mapping: f(1)=a, f(2)=b, f(3)=a",
        "inverse_image": "Find inverse image f⁻¹({a, c}) for f: {1,2,3,4} -> {a,b,c}"
    }

    c1, c2, c3 = st.columns(3)
    c1.button("💡 GCD: 1071 & 462", on_click=set_nav_page, args=("🧮 Computation of GCD using Euclid’s Algorithm", sample_qs["gcd"]))
    c2.button("💡 Choose 4 from 9", on_click=set_nav_page, args=("🎲 Combinations of Distinct Objects", sample_qs["comb"]))
    c3.button("💡 Divisors of 360", on_click=set_nav_page, args=("🔢 Integers & Divisibility", sample_qs["divisibility"]))

    def handle_home_solve():
        q = st.session_state.get("home_question_input", "").strip()
        if q:
            detected, _ = parse_question(q)
            target = TOPIC_NAV_MAP.get(detected, "🧮 Computation of GCD using Euclid’s Algorithm")
            st.session_state.preset_question = q
            st.session_state.nav_page = target

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("🧮 Solve Problem Step-by-Step", type="primary", use_container_width=True, on_click=handle_home_solve)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 UNIT I: Integers, Real Numbers & Complex Numbers")
    u1_cols = st.columns(3)

    unit1_topics = [
        ("divisibility", "🔢 Integers & Divisibility", "Prime factorization, primality testing, complete divisor lists, τ(n) & σ(n)."),
        ("gcd", "🧮 Computation of GCD (Euclid)", "Computation of GCD using Euclidean division and Extended Euclidean Bézout identity."),
        ("complex", "📍 Complex Numbers & Polar Form", "Rectangular to polar conversion, modulus r, argument θ, and Argand plane.")
    ]

    for i, (key, title, desc) in enumerate(unit1_topics):
        with u1_cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="min-height: 150px;">
                <div style="font-weight:800; font-size:1.05rem; color:#2EC4B6; margin-bottom:8px;">{title}</div>
                <div style="font-size:0.88rem; color:rgba(247,245,239,0.8); line-height:1.4; margin-bottom:12px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"Explore →", key=f"btn_u1_{key}", on_click=set_nav_page, args=(TOPIC_NAV_MAP[key], sample_qs[key]))

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📚 UNIT II: Basic Counting & Basics of Functions")
    u2_cols = st.columns(4)

    unit2_topics = [
        ("perm", "🔀 Permutations of Distinct Objects", "Ordered arrangements nPr, factorial products n!, and circular table arrangements."),
        ("comb", "🎲 Combinations of Distinct Objects", "Unordered selections nCr, binomial coefficient properties, and group selections."),
        ("functions", "🔗 Injective, Surjective & Bijective", "Classify domain-to-codomain mappings with bipartite graph diagrams."),
        ("inverse_image", "🔄 Inverse Images of Sets", "Pre-image computation f⁻¹(S) = { x ∈ A | f(x) ∈ S } for subsets S ⊆ B.")
    ]

    for i, (key, title, desc) in enumerate(unit2_topics):
        with u2_cols[i % 4]:
            st.markdown(f"""
            <div class="glass-card" style="min-height: 150px;">
                <div style="font-weight:800; font-size:1.05rem; color:#FFB627; margin-bottom:8px;">{title}</div>
                <div style="font-size:0.88rem; color:rgba(247,245,239,0.8); line-height:1.4; margin-bottom:12px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"Explore →", key=f"btn_u2_{key}", on_click=set_nav_page, args=(TOPIC_NAV_MAP[key], sample_qs[key]))


# ============================================================
# SOLVER DISPATCHER FOR ALL SYLLABUS TOPICS
# ============================================================
elif page in TOPIC_NAV_MAP.values():
    current_topic_key = [k for k, v in TOPIC_NAV_MAP.items() if v == page][0]

    initial_q = st.session_state.pop("preset_question", "")
    question_text = st.text_area("Enter or edit your problem statement", value=initial_q,
                                  placeholder=f"Type your question for {TOPICS[current_topic_key]}...",
                                  height=80)

    # Topic auto-detection
    if question_text:
        detected_topic, parsed_params = parse_question(question_text)
    else:
        detected_topic, parsed_params = current_topic_key, {}

    topic_key = current_topic_key
    if question_text and detected_topic != current_topic_key:
        detected_title = TOPICS.get(detected_topic, detected_topic)
        st.warning(f"🔍 Question detected for **{detected_title}**!")
        if st.button(f"🚀 Switch to {detected_title} & Solve Now", type="primary"):
            st.session_state.preset_question = question_text
            st.session_state.nav_page = TOPIC_NAV_MAP[detected_topic]
            st.rerun()
        topic_key = detected_topic

    st.markdown(f'<span class="topic-badge">{TOPICS[topic_key]}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title">{TOPICS[topic_key]}</div>', unsafe_allow_html=True)

    steps, answer, extra = None, None, {}
    auto_trigger = bool(question_text)
    domain_str, codomain_str, mapping = "1,2,3,4", "a,b,c", {}
    target_set_str = "a,c"

    if topic_key == "divisibility":
        default_n = parsed_params.get("n", 360) if topic_key == detected_topic else 360
        n_val = st.number_input("Integer n", value=int(default_n), step=1, min_value=2)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_divisibility(n_val)

    elif topic_key == "gcd":
        c1, c2 = st.columns(2)
        default_a = parsed_params.get("a", 1071) if topic_key == detected_topic else 1071
        default_b = parsed_params.get("b", 462) if topic_key == detected_topic else 462
        a_val = c1.number_input("Integer a", value=int(default_a), step=1)
        b_val = c2.number_input("Integer b", value=int(default_b), step=1)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_gcd_euclidean(a_val, b_val)


    elif topic_key == "complex":
        c1, c2 = st.columns(2)
        default_a = parsed_params.get("a", 1.0) if topic_key == detected_topic else 1.0
        default_b = parsed_params.get("b", 1.7320508) if topic_key == detected_topic else 1.7320508
        a_val = c1.number_input("Real part (a)", value=float(default_a))
        b_val = c2.number_input("Imaginary part (b)", value=float(default_b))
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_complex_to_polar(a_val, b_val)

    elif topic_key == "perm":
        c1, c2 = st.columns(2)
        default_n = parsed_params.get("n", 7) if topic_key == detected_topic else 7
        default_r = parsed_params.get("r", 3) if topic_key == detected_topic else 3
        n_val = c1.number_input("n (total distinct objects)", value=int(default_n), step=1, min_value=0)
        r_val = c2.number_input("r (arranged objects)", value=int(default_r), step=1, min_value=0)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_perm(int(n_val), int(r_val))

    elif topic_key == "comb":
        c1, c2 = st.columns(2)
        default_n = parsed_params.get("n", 9) if topic_key == detected_topic else 9
        default_r = parsed_params.get("r", 4) if topic_key == detected_topic else 4
        n_val = c1.number_input("n (total items)", value=int(default_n), step=1, min_value=0)
        r_val = c2.number_input("r (chosen items)", value=int(default_r), step=1, min_value=0)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_comb(int(n_val), int(r_val))

    elif topic_key == "functions":
        c1, c2 = st.columns(2)
        domain_str = c1.text_input("Domain A elements (comma-separated)", "1,2,3,4")
        codomain_str = c2.text_input("Codomain B elements (comma-separated)", "a,b,c")
        domain = [x.strip() for x in domain_str.split(",") if x.strip()]
        codomain = [x.strip() for x in codomain_str.split(",") if x.strip()]
        mapping = {}
        mcols = st.columns(min(len(domain), 4) or 1)
        for i, d in enumerate(domain):
            with mcols[i % len(mcols)]:
                mapping[d] = st.selectbox(f"f({d}) =", codomain, key=f"fn_map_{d}")
        if st.button("Classify Function", type="primary") or (auto_trigger and len(domain) > 0):
            steps, answer, extra = solve_functions(domain, codomain, mapping)

    elif topic_key == "inverse_image":
        c1, c2, c3 = st.columns(3)
        domain_str = c1.text_input("Domain A elements", "1,2,3,4")
        codomain_str = c2.text_input("Codomain B elements", "a,b,c")
        target_set_str = c3.text_input("Target Subset S ⊆ B", "a,c")
        domain = [x.strip() for x in domain_str.split(",") if x.strip()]
        codomain = [x.strip() for x in codomain_str.split(",") if x.strip()]
        target_set = [x.strip() for x in target_set_str.split(",") if x.strip()]
        mapping = {}
        mcols = st.columns(min(len(domain), 4) or 1)
        for i, d in enumerate(domain):
            with mcols[i % len(mcols)]:
                mapping[d] = st.selectbox(f"f({d}) =", codomain, key=f"inv_map_{d}")
        if st.button("Find Inverse Image f⁻¹(S)", type="primary") or (auto_trigger and len(domain) > 4):
            steps, answer, extra = solve_inverse_image(domain, codomain, mapping, target_set)



    # Save solution state if new steps were calculated
    if steps:
        st.session_state.active_solution = {
            "topic_key": topic_key,
            "question_text": question_text,
            "steps": steps,
            "answer": answer,
            "extra": extra,
            "domain_str": domain_str,
            "codomain_str": codomain_str,
            "mapping": mapping,
        }
    elif "active_solution" in st.session_state:
        act = st.session_state.active_solution
        if act.get("topic_key") == topic_key:
            steps = act.get("steps")
            answer = act.get("answer")
            extra = act.get("extra", {})
            domain_str = act.get("domain_str", domain_str)
            codomain_str = act.get("codomain_str", codomain_str)
            mapping = act.get("mapping", mapping)

    # Render solution & Visualizations / Tables
    if steps:

        st.markdown("---")
        sol_col, info_col = st.columns([7, 5])

        with sol_col:
            st.markdown("### 📚 STEP-BY-STEP REASONING")
            render_step_timeline(steps)

            if topic_key == "gcd":
                st.markdown("### 📊 Extended Euclidean Table (Textbook Method)")
                render_euclidean_html_table(extra["table_rows"])
            elif topic_key in ["functions", "inverse_image"]:
                st.markdown("### 📐 Function Mapping Diagram")
                fig = plot_function_diagram_plotly(
                    [x.strip() for x in domain_str.split(",") if x.strip()],
                    [x.strip() for x in codomain_str.split(",") if x.strip()],
                    mapping,
                    highlight_target_set=extra.get("target_set", [])
                )
                st.plotly_chart(fig, use_container_width=True)


        with info_col:
            render_answer_card(answer, latex_ans=extra.get("latex_ans"), question_text=question_text, topic_name=TOPICS.get(topic_key, topic_key), steps=steps)
            render_understand_panel(topic_key)


            # Persist to database
            last_solved_key = f"{question_text}_{topic_key}_{answer}"
            if st.session_state.get("last_solved_key") != last_solved_key:
                st.session_state.last_solved_key = last_solved_key
                st.session_state.streak += 1
                st.session_state.xp += 15
                db.save_solution(question_text or f"{TOPICS[topic_key]} problem", TOPICS[topic_key], answer, steps)
                db.save_user_stats(st.session_state.streak, st.session_state.xp, st.session_state.quiz_score["correct"], st.session_state.quiz_score["total"])





# ============================================================
# PAGE: PRACTICE & QUIZ
# ============================================================
elif page == "🧠 Quiz & Practice":
    st.markdown('<div class="hero-title">🧠 MATHMATE PRACTICE QUIZ</div>', unsafe_allow_html=True)
    st.caption("Infinite procedurally-generated math problems across Unit I & Unit II syllabus topics. Earn XP and level up!")

    if "quiz_q" not in st.session_state:
        st.session_state.quiz_q = generate_procedural_question()

    q = st.session_state.quiz_q
    st.markdown(f'<span class="topic-badge">{TOPICS[q["topic"]]}</span>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card">
        <div style="font-weight:700; font-size:1.2rem; color:#FFFFFF; margin-bottom:12px;">{q['q']}</div>
    </div>
    """, unsafe_allow_html=True)

    choice = st.radio("Choose an answer", q["options"], key="quiz_choice", label_visibility="collapsed")

    c1, c2 = st.columns(2)
    if c1.button("Submit Answer", type="primary", use_container_width=True):
        st.session_state.quiz_score["total"] += 1
        if choice == q["answer"]:
            st.session_state.quiz_score["correct"] += 1
            st.session_state.streak += 1
            st.session_state.xp += 20
            st.success("Correct! 🎉 (+20 XP)")
        else:
            st.error(f"Not quite — the correct answer is {q['answer']}.")

        db.save_user_stats(st.session_state.streak, st.session_state.xp, st.session_state.quiz_score["correct"], st.session_state.quiz_score["total"])

        with st.expander("💡 View step-by-step solution breakdown", expanded=True):
            st.write(q["exp"])

    if c2.button("Next Question →", use_container_width=True):
        st.session_state.quiz_q = generate_procedural_question()
        st.rerun()

    st.markdown("---")
    total = st.session_state.quiz_score["total"]
    correct = st.session_state.quiz_score["correct"]
    st.metric("Total Quiz Accuracy", f"{correct} / {total}" if total else "0 / 0")


# ============================================================
# PAGE: FORMULA CHEAT SHEET
# ============================================================
elif page == "📐 Formula Cheat Sheet":
    st.markdown('<div class="hero-title">📐 FORMULA CHEAT SHEET</div>', unsafe_allow_html=True)
    st.caption("Key formulas, identities, and theorems for all Unit I and Unit II syllabus topics.")

    for topic_key, c in TOPIC_CONCEPTS.items():
        with st.expander(f"📌 {c['title']}", expanded=True):
            st.markdown(f"**Description**: {c['desc']}")
            st.markdown("**Main Formula:**")
            st.latex(c['formula'])
            st.markdown("**Key Identity / Relationship:**")
            st.latex(c['identity'])
            st.markdown("**Key Properties:**")
            for pt in c['key_points']:
                st.markdown(f"- {pt}")


# ============================================================
# PAGE: HISTORY & PROGRESS
# ============================================================
elif page == "📜 Solution History":
    st.markdown('<div class="hero-title">📜 SOLUTION HISTORY</div>', unsafe_allow_html=True)
    st.caption("Review your solved problems and tracking metrics (Persisted in Database).")

    m1, m2, m3 = st.columns(3)
    history = db.fetch_history(limit=50)
    m1.metric("Total Problems Solved", len(history))
    m2.metric("Current Streak", f"{st.session_state.streak} Days 🔥")
    m3.metric("Total XP", f"{st.session_state.xp} XP")

    st.markdown("---")
    if not history:
        st.info("No solved questions in database yet — head to **Home** or pick a topic to get started.")
    else:
        for item in history:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-weight:700; color:#2EC4B6; font-size:0.95rem;">{item.get('topic','')}</span>
                    <span style="font-size:0.88rem; color:rgba(247,245,239,0.5);">{item.get('time','')}</span>
                </div>
                <div style="font-size:1.05rem; font-weight:600; color:#FFFFFF; margin-bottom:6px;">{item.get('question','')}</div>
                <div style="font-size:0.9rem; color:#FFB627; font-weight:700;">Answer: {item.get('answer','')}</div>
            </div>
            """, unsafe_allow_html=True)
