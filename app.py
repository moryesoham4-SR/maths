"""
MathMate — Interactive Mathematics Lab
Structured according to Syllabus Requirements:

UNIT I: Practical based on basics of integers, real numbers and complex numbers
  1. Integers and Divisibility (Prime Factorization, Divisors, Primality)
  2. Computation of GCD using Euclid’s Algorithm & GCD in Factorization Form
  3. Solutions of Linear Congruences (ax ≡ b mod m)
  4. Complex Numbers & Polar Form

UNIT II: Practical based on Introduction to basic counting and basics of functions
  5. Permutations of Distinct Objects (n!, P(n,r), Circular)
  6. Combinations of Distinct Objects (C(n,r), Binomial)
  7. Injective, Bijective, Surjective Functions
  8. Inverse Images of Sets under Functions (f⁻¹(S))
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
import matplotlib.pyplot as plt
import sympy as sp
from sympy import (
    symbols, sympify, limit, oo, latex, I, re as s_re, im as s_im, Rational,
    factorint, gcd as sp_gcd, lcm as sp_lcm, gcdex, mod_inverse, solve as sp_solve
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
)

import plotly.graph_objects as go
import plotly.express as px

# Safe Local Database Import with Fallback
try:
    import db
except Exception:
    class DummyDB:
        @staticmethod
        def is_supabase_connected(): return False
        @staticmethod
        def save_solution(*args, **kwargs): pass
        @staticmethod
        def fetch_history(*args, **kwargs): return []
        @staticmethod
        def load_user_stats(): return {"streak": 0, "xp": 0, "quiz_correct": 0, "quiz_total": 0}
        @staticmethod
        def save_user_stats(*args, **kwargs): pass
    db = DummyDB

# Safe API Client Import with Fallback
try:
    import api_client
except Exception:
    class DummyAPIClient:
        @staticmethod
        def solve_with_ai(*args, **kwargs): return None
        @staticmethod
        def ask_ai_tutor(*args, **kwargs): return "AI Tutor module unavailable. Ensure `api_client.py` is uploaded."
    api_client = DummyAPIClient

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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at 15% 15%, #182848 0%, #0b132b 60%, #060b18 100%);
}}

h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{
    color: {PAPER};
}}

.hero-symbol-banner {{
    font-size: 1.3rem;
    letter-spacing: 0.35em;
    color: rgba(46, 196, 182, 0.65);
    font-weight: 700;
    margin-bottom: 2px;
    text-shadow: 0 0 12px rgba(46, 196, 182, 0.3);
}}

.hero-title {{
    background: linear-gradient(135deg, #FFFFFF 0%, {TEAL} 50%, {AMBER} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}}

.hero-subtitle {{
    color: rgba(247, 245, 239, 0.75);
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
}}

.glass-card {{
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
    padding: 22px;
    margin: 12px 0;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
}}

.glass-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(46, 196, 182, 0.45);
    box-shadow: 0 12px 35px 0 rgba(46, 196, 182, 0.18);
}}

.timeline-step {{
    display: flex;
    align-items: flex-start;
    background: rgba(247, 245, 239, 0.03);
    border: 1px solid rgba(247, 245, 239, 0.1);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 6px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}

.timeline-num {{
    background: linear-gradient(135deg, {TEAL} 0%, #1c988b 100%);
    color: #080e1e;
    font-weight: 800;
    font-size: 1.05rem;
    min-width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    box-shadow: 0 0 12px rgba(46, 196, 182, 0.4);
    flex-shrink: 0;
}}

.timeline-content {{
    flex-grow: 1;
}}

.timeline-title {{
    color: {TEAL};
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

.timeline-body {{
    color: rgba(247, 245, 239, 0.9);
    font-size: 0.95rem;
    line-height: 1.45;
    white-space: pre-line;
}}

.answer-card {{
    background: linear-gradient(135deg, rgba(46, 196, 182, 0.15) 0%, rgba(255, 182, 39, 0.1) 100%);
    border: 2px solid {TEAL};
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(46, 196, 182, 0.25);
    margin-bottom: 20px;
}}

.answer-badge {{
    font-size: 0.82rem;
    font-weight: 800;
    color: {AMBER};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
}}

.answer-value {{
    font-size: 1.5rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 8px;
    word-break: break-word;
}}

.understand-card {{
    background: rgba(11, 19, 43, 0.75);
    border: 1px solid rgba(255, 182, 39, 0.35);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.25);
}}

.understand-title {{
    color: {AMBER};
    font-weight: 800;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
}}

.topic-badge {{
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, rgba(255, 182, 39, 0.2) 0%, rgba(230, 57, 70, 0.15) 100%);
    color: {AMBER};
    border: 1px solid rgba(255, 182, 39, 0.5);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    box-shadow: 0 4px 15px rgba(255, 182, 39, 0.15);
    margin-bottom: 12px;
}}

.db-status-badge {{
    font-size: 0.75rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 12px;
    display: inline-block;
    margin-bottom: 12px;
}}

[data-testid="stSidebar"] {{
    background-color: #07111F;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}}
</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALIZE PERSISTENT USER STATS FROM DATABASE
# ============================================================
if "stats_loaded" not in st.session_state:
    db_stats = db.load_user_stats()
    st.session_state.streak = db_stats.get("streak", 0)
    st.session_state.xp = db_stats.get("xp", 0)
    st.session_state.quiz_score = {
        "correct": db_stats.get("quiz_correct", 0),
        "total": db_stats.get("quiz_total", 0)
    }
    st.session_state.stats_loaded = True


# ============================================================
# TOPIC DEFINITIONS & SYLLABUS METADATA (UNIT I & UNIT II)
# ============================================================
TOPICS = {
    # UNIT I
    "divisibility": "🔢 Integers & Divisibility",
    "gcd": "🧮 Euclidean Algorithm & GCD (Factorization Form)",
    "congruence": "⚖️ Solutions of Linear Congruences",
    "complex": "📍 Complex Numbers & Polar Form",
    # UNIT II
    "perm": "🔀 Permutations of Distinct Objects",
    "comb": "🎲 Combinations of Distinct Objects",
    "functions": "🔗 Injective, Surjective & Bijective Functions",
    "inverse_image": "🔄 Inverse Images of Sets under Functions",
}

TOPIC_NAV_MAP = {
    "divisibility": "🔢 Integers & Divisibility",
    "gcd": "🧮 Euclidean Algorithm & GCD (Factorization Form)",
    "congruence": "⚖️ Solutions of Linear Congruences",
    "complex": "📍 Complex Numbers & Polar Form",
    "perm": "🔀 Permutations of Distinct Objects",
    "comb": "🎲 Combinations of Distinct Objects",
    "functions": "🔗 Injective, Surjective & Bijective Functions",
    "inverse_image": "🔄 Inverse Images of Sets under Functions",
}

TOPIC_KEYWORDS = {
    "divisibility": ["divisibility", "prime factor", "factorization", "divisors", "prime test", "is prime", "factors of"],
    "gcd": ["gcd", "hcf", "euclidean", "greatest common divisor", "factorization form", "factor form", "highest common factor", "bezout"],
    "congruence": ["congruence", "congruences", "mod", "modulo", "ax = b mod", "linear congruence", "ax ≡ b"],
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
        "title": "Euclidean Algorithm & GCD (Factorization Form)",
        "desc": "The Greatest Common Divisor (GCD) can be computed via repeated Euclidean division or prime factor exponent comparison.",
        "formula": r"\gcd(a, b) = \prod p_i^{\min(e_i, g_i)}, \quad \operatorname{lcm}(a, b) = \prod p_i^{\max(e_i, g_i)}",
        "identity": r"a \cdot b = \gcd(a, b) \cdot \operatorname{lcm}(a, b) \quad \text{and} \quad a x + b y = \gcd(a, b)",
        "key_points": [
            "Euclidean Algorithm: repeated replacement a = q·b + r until r = 0.",
            "Prime Factorization Form: take minimum exponent of each prime factor.",
            "Bézout's Identity: integers x,y exist satisfying ax + by = gcd(a,b)."
        ]
    },
    "congruence": {
        "title": "Linear Congruences",
        "desc": "A linear congruence ax ≡ b (mod m) asks for integer x such that m divides (ax - b).",
        "formula": r"a x \equiv b \pmod m",
        "identity": r"d = \gcd(a, m) \mid b \iff \text{Solvable with } d \text{ solutions modulo } m",
        "key_points": [
            "Solvability Condition: d = gcd(a, m) must divide b.",
            "If d | b, reduce to (a/d)x ≡ (b/d) mod (m/d).",
            "Solutions mod m: x_k = (x_0 + k · (m/d)) mod m for k = 0, 1, ..., d-1."
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
def format_prime_factorization(factor_dict: dict) -> str:
    """Format prime factorization dictionary {p: e} into LaTeX string like 2^3 × 3^2 × 5^1."""
    if not factor_dict:
        return "1"
    parts = []
    for p in sorted(factor_dict.keys()):
        e = factor_dict[p]
        parts.append(f"{p}^{{{e}}}")
    return r" \times ".join(parts)


def detect_topic(text: str) -> str:
    """Keyword-based topic classifier with a scoring fallback."""
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
    elif topic == "congruence":
        a = nums[0] if len(nums) >= 1 else 14
        b = nums[1] if len(nums) >= 2 else 12
        m = nums[2] if len(nums) >= 3 else 18
        return topic, {"a": a, "b": b, "m": m}
    elif topic == "complex":
        a, b = extract_complex_parts(text)
        return topic, {"a": a, "b": b}
    elif topic in ["perm", "comb"]:
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

    # Prime Test
    is_prime = sp.isprime(n)
    steps.append(("Primality Test", f"Is {n} prime? {'YES (Prime)' if is_prime else 'NO (Composite)'}"))

    # Prime Factorization
    factors = factorint(n)
    fact_str = format_prime_factorization(factors)
    steps.append(("Prime Factorization", f"{n} = {fact_str}"))

    # List of Divisors
    divisors = sorted(sp.divisors(n))
    tau = len(divisors)
    sigma = sum(divisors)

    steps.append(("Divisor Enumeration", f"Divisors of {n}: {divisors}\n"
                                         f"Total Number of Divisors τ({n}) = {tau}\n"
                                         f"Sum of Divisors σ({n}) = {sigma}"))

    ans_summary = f"{n} = {fact_str} | Divisors: {tau} | Prime: {is_prime}"
    return steps, ans_summary, {
        "n": n, "is_prime": is_prime, "factors": factors,
        "divisors": divisors, "tau": tau, "sigma": sigma
    }


def solve_gcd_factorization(a: int, b: int):
    """UNIT I: Computation of GCD using Euclid's Algorithm & Factorization Form."""
    orig_a, orig_b = a, b
    a_abs, b_abs = abs(a), abs(b)
    if a_abs == 0 or b_abs == 0:
        return [("Validation Error", "Both integers must be non-zero.")], "Invalid input", {}

    steps = []
    steps.append(("Input Integers", f"Compute gcd({orig_a}, {orig_b})"))

    # 1. Euclidean Algorithm Breakdown
    u, v = a_abs, b_abs
    if u < v:
        steps.append(("Ordering Adjustment", f"Swap inputs so larger integer is first: a = {v}, b = {u}"))
        u, v = v, u

    euclid_steps = []
    step_idx = 1
    curr_a, curr_b = u, v
    while curr_b != 0:
        q = curr_a // curr_b
        r = curr_a % curr_b
        euclid_steps.append(f"Step {step_idx}: {curr_a} = {q} × {curr_b} + {r}  (q={q}, r={r})")
        curr_a, curr_b = curr_b, r
        step_idx += 1

    gcd_val = curr_a
    steps.append(("Euclidean Algorithm Division Steps", "\n".join(euclid_steps)))
    steps.append(("Euclidean GCD Result", f"The last non-zero remainder is {gcd_val}. Thus, gcd({orig_a}, {orig_b}) = {gcd_val}."))

    # 2. Bézout's Identity via Extended Euclidean Algorithm
    g, x_bez, y_bez = gcdex(a_abs, b_abs)
    steps.append(("Bézout's Identity (Extended Euclidean)", f"Linear combination: ({x_bez}) × {a_abs} + ({y_bez}) × {b_abs} = {gcd_val}"))

    # 3. Prime Factorization Form
    fact_a = factorint(a_abs)
    fact_b = factorint(b_abs)

    all_primes = sorted(set(fact_a.keys()) | set(fact_b.keys()))
    fact_gcd = {}
    fact_lcm = {}
    comp_lines = []

    for p in all_primes:
        e_a = fact_a.get(p, 0)
        e_b = fact_b.get(p, 0)
        min_e = min(e_a, e_b)
        max_e = max(e_a, e_b)
        if min_e > 0:
            fact_gcd[p] = min_e
        fact_lcm[p] = max_e
        comp_lines.append(f"• Prime {p}: e_a={e_a}, e_b={e_b} → min(e_a, e_b) = {min_e}, max(e_a, e_b) = {max_e}")

    str_fact_a = format_prime_factorization(fact_a)
    str_fact_b = format_prime_factorization(fact_b)
    str_fact_gcd = format_prime_factorization(fact_gcd)
    str_fact_lcm = format_prime_factorization(fact_lcm)
    lcm_val = math.lcm(a_abs, b_abs)

    fact_block = (
        f"Prime Factorization of a = {a_abs}:  {a_abs} = {str_fact_a}\n"
        f"Prime Factorization of b = {b_abs}:  {b_abs} = {str_fact_b}\n\n"
        f"Exponent Comparison across Primes:\n" + "\n".join(comp_lines) + "\n\n"
        f"GCD in Factorization Form:\n"
        f"gcd({a_abs}, {b_abs}) = {str_fact_gcd} = {gcd_val}\n\n"
        f"LCM in Factorization Form:\n"
        f"lcm({a_abs}, {b_abs}) = {str_fact_lcm} = {lcm_val}"
    )

    steps.append(("GCD & LCM in Prime Factorization Form", fact_block))

    ans_str = f"gcd({orig_a}, {orig_b}) = {str_fact_gcd} = {gcd_val}"
    return steps, ans_str, {
        "gcd": gcd_val, "lcm": lcm_val, "a": a_abs, "b": b_abs,
        "fact_a": fact_a, "fact_b": fact_b, "fact_gcd": fact_gcd, "fact_lcm": fact_lcm,
        "x_bez": x_bez, "y_bez": y_bez, "all_primes": all_primes
    }


def solve_linear_congruence(a: int, b: int, m: int):
    """UNIT I: Solutions of linear congruences ax ≡ b (mod m)."""
    if m <= 0:
        return [("Validation Error", "Modulus m must be a positive integer.")], "Invalid m", {}

    steps = []
    a_mod = a % m
    b_mod = b % m
    steps.append(("Linear Congruence Formulation", f"Solve: {a}x ≡ {b} (mod {m})  →  Simplified: {a_mod}x ≡ {b_mod} (mod {m})"))

    # Step 1: Compute d = gcd(a, m)
    d = math.gcd(a_mod, m)
    steps.append(("GCD Check d = gcd(a, m)", f"d = gcd({a_mod}, {m}) = {d}"))

    # Step 2: Solvability Condition Check
    if b_mod % d != 0:
        fail_msg = (f"Solvability Condition FAILED!\n"
                    f"d = {d} does NOT divide b = {b_mod} (remainder {b_mod % d}).\n"
                    f"Conclusion: NO SOLUTION exists for {a}x ≡ {b} (mod {m}).")
        steps.append(("Solvability Analysis", fail_msg))
        return steps, "No Solution", {"solvable": False, "d": d, "solutions": []}

    steps.append(("Solvability Analysis", f"PASSED! d = {d} divides b = {b_mod} ({b_mod} / {d} = {b_mod // d}).\n"
                                         f"Conclusion: Exactly {d} incongruent solution(s) exist modulo {m}."))

    # Step 3: Reduce equation by dividing through by d
    a_prime = a_mod // d
    b_prime = b_mod // d
    m_prime = m // d

    steps.append(("Equation Reduction by d", f"Dividing by d = {d}:\n"
                                            f"({a_mod}/{d})x ≡ ({b_mod}/{d}) (mod {m}/{d})  →  {a_prime}x ≡ {b_prime} (mod {m_prime})"))

    # Step 4: Find Modular Inverse of a' mod m'
    inv_a = mod_inverse(a_prime, m_prime)
    x0 = (inv_a * b_prime) % m_prime

    steps.append(("Modular Inverse & Base Solution", f"Modular Inverse: ({a_prime})⁻¹ ≡ {inv_a} (mod {m_prime})\n"
                                                     f"Particular Base Solution: x₀ ≡ ({inv_a} × {b_prime}) mod {m_prime} = {x0}"))

    # Step 5: Generate all d incongruent solutions modulo m
    solutions = [(x0 + k * m_prime) % m for k in range(d)]
    sol_str = ", ".join(str(s) for s in solutions)
    sol_latex = r", \quad ".join(f"x \equiv {s} \pmod{{{m}}}" for s in solutions)

    steps.append(("All Incongruent Solutions Modulo m", f"Formula: xₖ = x₀ + k · (m/d)  for k = 0, 1, ..., {d-1}\n"
                                                       f"Generated Solutions mod {m}:\n"
                                                       f"{sol_latex}"))

    ans_summary = f"x ≡ {sol_str} (mod {m})"
    return steps, ans_summary, {
        "solvable": True, "d": d, "a": a, "b": b, "m": m,
        "a_prime": a_prime, "b_prime": b_prime, "m_prime": m_prime,
        "x0": x0, "solutions": solutions
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
    polar_str = f"{r:.4f} (cos({theta_deg:.2f}°) + i sin({theta_deg:.2f}°))"
    euler_str = f"{r:.4f} e^({theta_rad:.4f}i)"
    steps.append(("Polar & Exponential Forms", f"Polar Form: z = {polar_str}\nExponential Form: z = {euler_str}"))
    return steps, polar_str, {"r": r, "theta_rad": theta_rad, "theta_deg": theta_deg, "a": a, "b": b}


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

    return steps, str(val_npr), {"val": val_npr, "n": n, "r": r, "n_fact": val_fact, "circular": val_circ}


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

    return steps, str(val_ncr), {"val": val_ncr, "n": n, "r": r}


def solve_functions(domain: list, codomain: list, mapping: dict):
    """UNIT II: Injective, Bijective, Surjective functions."""
    steps = []
    steps.append(("Domain & Codomain Setup", f"Domain A = {{{', '.join(map(str, domain))}}}\nCodomain B = {{{', '.join(map(str, codomain))}}}"))
    map_str = ", ".join(f"f({k})={v}" for k, v in mapping.items())
    steps.append(("Mapping Definition", f"Mappings: {map_str}"))

    mapped_values = list(mapping.values())
    is_injective = len(mapped_values) == len(set(mapped_values))
    if is_injective:
        steps.append(("Injectivity Test (One-to-One)", "PASSED: All outputs are distinct. No two domain elements share an image. Function is INJECTIVE."))
    else:
        duplicates = [x for x in set(mapped_values) if mapped_values.count(x) > 1]
        steps.append(("Injectivity Test (One-to-One)", f"FAILED: Multiple domain inputs map to the same codomain element(s): {duplicates}. Function is NOT Injective."))

    range_set = set(mapped_values)
    codomain_set = set(codomain)
    is_surjective = range_set == codomain_set
    if is_surjective:
        steps.append(("Surjectivity Test (Onto)", "PASSED: Range equals Codomain. Every element in Codomain B has a pre-image in Domain A. Function is SURJECTIVE."))
    else:
        uncovered = list(codomain_set - range_set)
        steps.append(("Surjectivity Test (Onto)", f"FAILED: Uncovered codomain element(s) with no pre-image: {uncovered}. Function is NOT Surjective."))

    is_bijective = is_injective and is_surjective
    classification = "BIJECTIVE (Injective & Surjective)" if is_bijective else \
                     "INJECTIVE ONLY (One-to-One, not Onto)" if is_injective else \
                     "SURJECTIVE ONLY (Onto, not One-to-One)" if is_surjective else \
                     "NEITHER (Neither Injective nor Surjective)"

    steps.append(("Final Classification", f"Classification: {classification}"))
    return steps, classification, {"injective": is_injective, "surjective": is_surjective, "bijective": is_bijective}


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

    ans_str = f"f⁻¹({{{', '.join(target_set_clean)}}}) = {{{', '.join(unique_preimages) if unique_preimages else 'Ø'}}}"
    steps.append(("Inverse Image Set Result", f"f⁻¹(S) = {{ x ∈ A | f(x) ∈ S }} = {ans_str}"))

    return steps, ans_str, {"preimages": unique_preimages, "target_set": target_set_clean}


# ============================================================
# INTERACTIVE PLOTLY VISUALIZATIONS
# ============================================================

def plot_factor_breakdown_plotly(fact_a: dict, fact_b: dict, fact_gcd: dict, a_val: int, b_val: int):
    """Grouped bar chart comparing prime factor exponents for GCD factorization form."""
    all_primes = sorted(list(set(fact_a.keys()) | set(fact_b.keys())))
    if not all_primes:
        all_primes = [2, 3]

    x_labels = [f"Prime {p}" for p in all_primes]
    e_a = [fact_a.get(p, 0) for p in all_primes]
    e_b = [fact_b.get(p, 0) for p in all_primes]
    e_gcd = [fact_gcd.get(p, 0) for p in all_primes]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_labels, y=e_a, name=f"a = {a_val}", marker_color=AMBER))
    fig.add_trace(go.Bar(x=x_labels, y=e_b, name=f"b = {b_val}", marker_color=CORAL))
    fig.add_trace(go.Bar(x=x_labels, y=e_gcd, name=f"gcd({a_val},{b_val}) [min exponent]", marker_color=TEAL))

    fig.update_layout(
        title="<b>Prime Factor Exponent Comparison</b>",
        barmode='group',
        xaxis=dict(title="Prime Factors (p)", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="Exponent (e)", dtick=1, gridcolor="rgba(255,255,255,0.05)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,18,38,0.6)",
        font=dict(color="#FFFFFF", family="Outfit"),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380
    )
    return fig


def plot_congruence_clock_plotly(m: int, solutions: list):
    """Modular clock / circle visualization for linear congruences ax ≡ b (mod m)."""
    fig = go.Figure()

    # Draw modular circle
    angles = np.linspace(0, 2*np.pi, m, endpoint=False)
    angles = (np.pi/2 - angles) % (2*np.pi)
    r = 1.0

    x_nodes = r * np.cos(angles)
    y_nodes = r * np.sin(angles)

    sol_set = set(solutions)

    t_smooth = np.linspace(0, 2*np.pi, 200)
    fig.add_trace(go.Scatter(
        x=r*np.cos(t_smooth), y=r*np.sin(t_smooth),
        mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', dash='dash'),
        hoverinfo='skip', showlegend=False
    ))

    non_sol_idx = [i for i in range(m) if i not in sol_set]
    if non_sol_idx:
        fig.add_trace(go.Scatter(
            x=[x_nodes[i] for i in non_sol_idx],
            y=[y_nodes[i] for i in non_sol_idx],
            mode='markers+text',
            marker=dict(size=22, color='rgba(74, 78, 105, 0.6)', line=dict(width=1, color='#FFFFFF')),
            text=[str(i) for i in non_sol_idx],
            textposition="middle center",
            textfont=dict(color="#FFFFFF", size=10),
            name="Non-solution mod m"
        ))

    sol_idx = [i for i in range(m) if i in sol_set]
    if sol_idx:
        fig.add_trace(go.Scatter(
            x=[x_nodes[i] for i in sol_idx],
            y=[y_nodes[i] for i in sol_idx],
            mode='markers+text',
            marker=dict(size=30, color=TEAL, line=dict(width=3, color=AMBER)),
            text=[str(i) for i in sol_idx],
            textposition="middle center",
            textfont=dict(color="#000000", size=12, weight="bold"),
            name="Solution mod m"
        ))

    fig.update_layout(
        title=f"<b>Modular Clock Solution Graph (mod {m})</b>",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4], scaleanchor="x", scaleratio=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,18,38,0.6)",
        font=dict(color="#FFFFFF", family="Outfit"),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380
    )
    return fig


def plot_complex_plane_plotly(points: list, labels: list, colors: list = None):
    fig = go.Figure()
    max_r = max([math.hypot(x, y) for x, y in points] + [2.0]) * 1.25

    t_vals = np.linspace(0, 2*np.pi, 200)
    fig.add_trace(go.Scatter(
        x=max_r * 0.8 * np.cos(t_vals), y=max_r * 0.8 * np.sin(t_vals),
        mode='lines', line=dict(color='rgba(255, 255, 255, 0.15)', dash='dash'),
        hoverinfo='skip', showlegend=False
    ))

    fig.add_shape(type="line", x0=-max_r, y0=0, x1=max_r, y1=0, line=dict(color="rgba(255,255,255,0.3)", width=1.5))
    fig.add_shape(type="line", x0=0, y0=-max_r, x1=0, y1=max_r, line=dict(color="rgba(255,255,255,0.3)", width=1.5))

    for i, (re_, im_) in enumerate(points):
        lbl = labels[i] if i < len(labels) else f"z{i}"
        col = colors[i] if colors and i < len(colors) else AMBER
        r_val = math.hypot(re_, im_)
        ang_deg = math.degrees(math.atan2(im_, re_))

        fig.add_trace(go.Scatter(
            x=[0, re_], y=[0, im_],
            mode='lines', line=dict(color=col, width=2.5),
            hoverinfo='skip', showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=[re_], y=[im_],
            mode='markers+text',
            marker=dict(size=12, color=col, line=dict(width=2, color='#FFFFFF')),
            text=[f"  {lbl}"], textposition="top right",
            hovertemplate=f"<b>{lbl}</b><br>Real: {re_:.4f}<br>Imag: {im_:.4f}i<br>Modulus r: {r_val:.4f}<br>Angle θ: {ang_deg:.2f}°<extra></extra>",
            name=lbl
        ))

    fig.update_layout(
        xaxis=dict(title="Real Axis (Re)", range=[-max_r, max_r], zeroline=False, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="Imaginary Axis (Im)", range=[-max_r, max_r], zeroline=False, scaleanchor="x", scaleratio=1, gridcolor="rgba(255,255,255,0.05)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,18,38,0.6)",
        font=dict(color="#FFFFFF", family="Outfit"),
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        height=420
    )
    return fig


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
            "exp": f"Prime factorization of {n}: {format_prime_factorization(extra['factors'])}\nτ({n}) = {extra['tau']}."
        }

    elif topic_key == "gcd":
        a = random.randint(100, 1500)
        b = random.randint(24, 450)
        steps, ans, extra = solve_gcd_factorization(a, b)
        correct = str(extra["gcd"])
        opts = {correct, str(int(correct) + 2), str(max(1, int(correct) - 2)), str(int(correct) * 2)}
        while len(opts) < 4:
            opts.add(str(random.randint(1, 20)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"Find gcd({a}, {b}) using the Euclidean algorithm & prime factor comparison.",
            "topic": "gcd",
            "options": opts,
            "answer": correct,
            "exp": f"Euclidean breakdown and prime factor exponent comparison yields gcd({a}, {b}) = {correct}."
        }

    elif topic_key == "congruence":
        m = random.choice([7, 9, 11, 13])
        a = random.randint(2, m-1)
        x_true = random.randint(1, m-1)
        b = (a * x_true) % m
        steps, ans, extra = solve_linear_congruence(a, b, m)
        correct = str(x_true)
        opts = {correct, str((x_true + 2) % m), str((x_true + 4) % m), str((x_true + 5) % m)}
        while len(opts) < 4:
            opts.add(str(random.randint(0, m-1)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"Solve the linear congruence: {a}x ≡ {b} (mod {m}). Find x (mod {m}).",
            "topic": "congruence",
            "options": opts,
            "answer": correct,
            "exp": f"Since gcd({a}, {m}) = 1, x ≡ ({a}⁻¹ × {b}) mod {m} = {x_true}."
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


def render_answer_card(answer):
    st.markdown(f"""
    <div class="answer-card">
        <div class="answer-badge">FINAL ANSWER</div>
        <div class="answer-value">{answer}</div>
        <div class="answer-status">✓ Computed & Verified</div>
    </div>
    """, unsafe_allow_html=True)


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
    "🧮 Euclidean Algorithm & GCD (Factorization Form)",
    "⚖️ Solutions of Linear Congruences",
    "📍 Complex Numbers & Polar Form",
    "🔀 Permutations of Distinct Objects",
    "🎲 Combinations of Distinct Objects",
    "🔗 Injective, Surjective & Bijective Functions",
    "🔄 Inverse Images of Sets under Functions",
    "🤖 AI Math Tutor",
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
    st.markdown('<div class="hero-subtitle">Interactive Mathematics Lab · UNIT I & UNIT II Syllabus Modules • AI Assisted</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="padding: 26px; border: 1px solid rgba(46, 196, 182, 0.35);">
        <div style="font-weight:800; font-size:1.35rem; color:#FFFFFF; margin-bottom:4px;">✨ What would you like to solve?</div>
        <div style="font-size:0.88rem; color:rgba(247,245,239,0.7); margin-bottom:16px;">Type or paste any syllabus problem below:</div>
    """, unsafe_allow_html=True)

    home_q_input = st.text_area("Question Input", key="home_question_input",
                                placeholder="e.g. Find GCD of 1071 and 462 in factorization form  OR  Solve 14x = 12 mod 18",
                                height=85, label_visibility="collapsed")

    st.caption("Quick sample questions:")
    sample_qs = {
        "divisibility": "Prime factorization and divisors of 360",
        "gcd": "Find GCD of 1071 and 462 in factorization form",
        "congruence": "Solve linear congruence 14x ≡ 12 (mod 18)",
        "complex": "Convert z = 1 + 1.73205i to polar form",
        "perm": "Permutations P(7, 3) of 7 distinct objects",
        "comb": "Choose 4 members from a group of 9 available employees",
        "functions": "Domain: 1, 2, 3. Codomain: a, b, c. Mapping: f(1)=a, f(2)=b, f(3)=a",
        "inverse_image": "Find inverse image f⁻¹({a, c}) for f: {1,2,3,4} -> {a,b,c}"
    }

    c1, c2, c3, c4 = st.columns(4)
    c1.button("💡 GCD: 1071 & 462", on_click=set_nav_page, args=("🧮 Euclidean Algorithm & GCD (Factorization Form)", sample_qs["gcd"]))
    c2.button("💡 Congruence: 14x ≡ 12 (mod 18)", on_click=set_nav_page, args=("⚖️ Solutions of Linear Congruences", sample_qs["congruence"]))
    c3.button("💡 Choose 4 from 9", on_click=set_nav_page, args=("🎲 Combinations of Distinct Objects", sample_qs["comb"]))
    c4.button("💡 Divisors of 360", on_click=set_nav_page, args=("🔢 Integers & Divisibility", sample_qs["divisibility"]))

    def handle_home_solve():
        q = st.session_state.get("home_question_input", "").strip()
        if q:
            detected, _ = parse_question(q)
            target = TOPIC_NAV_MAP.get(detected, "🧮 Euclidean Algorithm & GCD (Factorization Form)")
            st.session_state.preset_question = q
            st.session_state.nav_page = target

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("🧮 Solve Problem Step-by-Step", type="primary", use_container_width=True, on_click=handle_home_solve)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 UNIT I: Integers, Real Numbers & Complex Numbers")
    u1_cols = st.columns(4)

    unit1_topics = [
        ("divisibility", "🔢 Integers & Divisibility", "Prime factorization, primality testing, complete divisor lists, τ(n) & σ(n)."),
        ("gcd", "🧮 Euclidean Algorithm & GCD", "Euclidean division, Bézout identity, and GCD & LCM in Prime Factorization Form."),
        ("congruence", "⚖️ Linear Congruences", "Solutions to ax ≡ b (mod m), solvability check gcd(a,m)|b, and incongruent roots."),
        ("complex", "📍 Complex Numbers & Polar Form", "Rectangular to polar conversion, modulus r, argument θ, and Argand plane.")
    ]

    for i, (key, title, desc) in enumerate(unit1_topics):
        with u1_cols[i % 4]:
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
            steps, answer, extra = solve_gcd_factorization(a_val, b_val)

    elif topic_key == "congruence":
        c1, c2, c3 = st.columns(3)
        default_a = parsed_params.get("a", 14) if topic_key == detected_topic else 14
        default_b = parsed_params.get("b", 12) if topic_key == detected_topic else 12
        default_m = parsed_params.get("m", 18) if topic_key == detected_topic else 18
        a_val = c1.number_input("a (coefficient)", value=int(default_a), step=1)
        b_val = c2.number_input("b (target remainder)", value=int(default_b), step=1)
        m_val = c3.number_input("m (modulus)", value=int(default_m), step=1, min_value=1)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_linear_congruence(a_val, b_val, m_val)

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
        if st.button("Find Inverse Image f⁻¹(S)", type="primary") or (auto_trigger and len(domain) > 0):
            steps, answer, extra = solve_inverse_image(domain, codomain, mapping, target_set)

    # Optional AI Solver Fallback button
    if question_text and st.button("🤖 Ask AI Solver (LLM Fallback)"):
        with st.spinner("AI Solver analyzing problem..."):
            ai_res = api_client.solve_with_ai(question_text)
            if ai_res:
                steps = ai_res.get("steps", [])
                answer = ai_res.get("answer", "")
                st.success("Solved via AI Math Engine!")

    # Render solution & Plotly charts
    if steps:
        st.markdown("---")
        sol_col, info_col = st.columns([7, 5])

        with sol_col:
            st.markdown("### 📚 STEP-BY-STEP REASONING")
            render_step_timeline(steps)

            st.markdown("### 📐 Interactive Mathematics Visualization")
            if topic_key == "gcd":
                fig = plot_factor_breakdown_plotly(extra["fact_a"], extra["fact_b"], extra["fact_gcd"], extra["a"], extra["b"])
                st.plotly_chart(fig, use_container_width=True)
            elif topic_key == "congruence" and extra.get("solvable"):
                fig = plot_congruence_clock_plotly(extra["m"], extra["solutions"])
                st.plotly_chart(fig, use_container_width=True)
            elif topic_key == "complex":
                fig = plot_complex_plane_plotly([(extra["a"], extra["b"])], ["z"])
                st.plotly_chart(fig, use_container_width=True)
            elif topic_key in ["functions", "inverse_image"]:
                fig = plot_function_diagram_plotly(
                    [x.strip() for x in domain_str.split(",") if x.strip()],
                    [x.strip() for x in codomain_str.split(",") if x.strip()],
                    mapping,
                    highlight_target_set=extra.get("target_set", [])
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 Computation breakdown completed.")

        with info_col:
            render_answer_card(answer)
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
# PAGE: AI MATH TUTOR
# ============================================================
elif page == "🤖 AI Math Tutor":
    st.markdown('<div class="hero-title">🤖 AI MATH TUTOR</div>', unsafe_allow_html=True)
    st.caption("Ask questions, seek clarifications, or explore theorems across Unit I and Unit II syllabus topics.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am your MathMate AI Tutor. Ask me any question about Integers & Divisibility, Euclidean Algorithm & GCD, Linear Congruences, Complex Numbers, Permutations, Combinations, Functions, or Inverse Images!"}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask any conceptual question or ask for help on a problem...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("AI Tutor thinking..."):
                tutor_reply = api_client.ask_ai_tutor(user_input)
                st.write(tutor_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": tutor_reply})


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
