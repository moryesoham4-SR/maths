"""
MathMate — Interactive Mathematics Lab
Streamlit app covering 6 core syllabus topics:
1. Euclidean Algorithm & GCD
2. Complex Numbers & Polar Form
3. De Moivre's Theorem (powers and n-th roots)
4. Permutations & Combinations
5. Injective, Surjective & Bijective Functions
6. Limits & Continuity

Features:
- Step-by-step problem solvers
- Supabase cloud storage integration with automatic SQLite local fallback
- Interactive Plotly visualizations (Argand plane, roots polygon, function mappings, limit curves)
- Infinite procedural practice quiz engine
- Formula & Concept Cheat Sheet reference page
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
from sympy import symbols, sympify, limit, oo, latex, I, re as s_re, im as s_im, Rational
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
# TOPIC DEFINITIONS & METADATA
# ============================================================
TOPICS = {
    "gcd": "🧮 Euclidean Algorithm & GCD",
    "complex": "📍 Complex Numbers & Polar Form",
    "demoivre": "🔄 De Moivre's Theorem",
    "permcomb": "🔢 Permutations & Combinations",
    "functions": "🔗 Functions & Mappings",
    "limits": "📈 Limits & Continuity",
}

TOPIC_NAV_MAP = {
    "gcd": "🧮 Euclidean Algorithm & GCD",
    "complex": "📍 Complex Numbers & Polar Form",
    "demoivre": "🔄 De Moivre's Theorem",
    "permcomb": "🔢 Permutations & Combinations",
    "functions": "🔗 Functions & Mappings",
    "limits": "📈 Limits & Continuity"
}

TOPIC_KEYWORDS = {
    "gcd": ["gcd", "hcf", "euclidean", "greatest common divisor", "highest common factor", "divide", "divisible", "remainder", "coprime"],
    "complex": ["polar form", "modulus", "argument", "rectangular form", "complex number", "argand", "imaginary", "real part"],
    "demoivre": ["de moivre", "demoivre", "nth root", "z^n", "power of complex", "roots of unity", "roots of"],
    "permcomb": ["permutation", "permutations", "combination", "combinations", "arrange", "arrangement", "select", "selection", "choose", "chosen", "committee", "committees", "group", "groups", "members", "member", "team", "pool", "volunteers", "people", "ncr", "npr", "how many", "ways", "formed", "possibilities", "possible"],
    "functions": ["injective", "surjective", "bijective", "one-one", "onto", "into", "mapping", "domain", "codomain"],
    "limits": ["limit", "lim ", "continuity", "continuous", "discontinuous", "x->", "x→", "approaches"],
}

TOPIC_CONCEPTS = {
    "gcd": {
        "title": "Euclidean Algorithm & GCD",
        "desc": "The Greatest Common Divisor (GCD) is the largest positive integer that divides both numbers without a remainder.",
        "formula": r"a = q \cdot b + r \quad (0 \le r < b)",
        "identity": r"\gcd(a, b) = \gcd(b, r)",
        "key_points": [
            "Repeatedly replace (a, b) with (b, a mod b).",
            "When remainder becomes 0, the last non-zero remainder is the GCD.",
            "Bézout's identity: integers x, y exist such that ax + by = gcd(a,b)."
        ]
    },
    "complex": {
        "title": "Complex Numbers & Polar Form",
        "desc": "Complex numbers z = x + yi can be represented in polar coordinates (r, θ) on the Argand plane.",
        "formula": r"z = r(\cos\theta + i\sin\theta) = r e^{i\theta}",
        "identity": r"r = \sqrt{x^2 + y^2}, \quad \theta = \operatorname{atan2}(y, x)",
        "key_points": [
            "Modulus r is distance from origin on the Argand plane.",
            "Argument θ is angle with positive real axis.",
            "Euler's formula: e^{iθ} = cos θ + i sin θ."
        ]
    },
    "demoivre": {
        "title": "De Moivre's Theorem & Roots",
        "desc": "De Moivre's Theorem simplifies powers and roots of complex numbers in polar form.",
        "formula": r"[r(\cos\theta + i\sin\theta)]^n = r^n (\cos(n\theta) + i\sin(n\theta))",
        "identity": r"w_k = r^{1/n} \left(\cos\frac{\theta + 2\pi k}{n} + i\sin\frac{\theta + 2\pi k}{n}\right)",
        "key_points": [
            "To compute zⁿ: raise modulus to n (rⁿ) and multiply angle by n (nθ).",
            "The n-th roots of z form a regular n-sided polygon centered at origin.",
            "Sum of all n-th roots of unity equals 0."
        ]
    },
    "permcomb": {
        "title": "Permutations & Combinations",
        "desc": "Permutations count ordered arrangements; Combinations count unordered selections.",
        "formula": r"nPr = \frac{n!}{(n-r)!}, \quad nCr = \binom{n}{r} = \frac{n!}{r!(n-r)!}",
        "identity": r"\binom{n}{r} = \binom{n}{n-r}",
        "key_points": [
            "Order matters for Permutations (nPr).",
            "Order does NOT matter for Combinations (nCr).",
            "Pascal's Identity: nCr = (n-1)C(r-1) + (n-1)Cr."
        ]
    },
    "functions": {
        "title": "Injective, Surjective & Bijective",
        "desc": "Function classifications based on how elements in the Domain map to elements in the Codomain.",
        "formula": r"f: A \to B",
        "identity": r"\text{Injective: } f(a)=f(b) \implies a=b, \quad \text{Surjective: } \operatorname{range}(f) = B",
        "key_points": [
            "Injective (One-to-One): No two domain elements share an image.",
            "Surjective (Onto): Every codomain element has a pre-image.",
            "Bijective: Both Injective and Surjective (invertible function)."
        ]
    },
    "limits": {
        "title": "Limits & Continuity",
        "desc": "Limits describe function behavior near a target point. Continuous functions equal their limit at that point.",
        "formula": r"\lim_{x \to a} f(x) = L",
        "identity": r"\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)} \quad (\text{L'Hôpital's Rule})",
        "key_points": [
            "Direct substitution works for continuous functions.",
            "Indeterminate forms (0/0, ∞/∞) require simplification or L'Hôpital's Rule.",
            "f(x) is continuous at x=a if lim(x→a) f(x) = f(a)."
        ]
    }
}


# ============================================================
# NATURAL LANGUAGE PARSING
# ============================================================
def detect_topic(text: str) -> str:
    """Keyword-based topic classifier with a scoring fallback."""
    t = text.lower()
    scores = {k: 0 for k in TOPICS}
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[topic] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "permcomb" if any(w in t for w in ["choose", "select", "committee", "pool", "volunteers", "people", "how many", "group"]) else "gcd"


def extract_complex_parts(text: str):
    t = text.replace(" ", "")
    m = re.search(r"z?\=?([+-]?\d+\.?\d*)\s*([+-]\s*\d*\.?\d*)[ij]", t, re.IGNORECASE)
    if m:
        a = float(m.group(1))
        b_str = m.group(2).replace(" ", "")
        if b_str in ["+", ""]:
            b = 1.0
        elif b_str == "-":
            b = -1.0
        else:
            b = float(b_str)
        return a, b
    
    m_pure_im = re.search(r"([+-]?\d*\.?\d*)[ij]", t, re.IGNORECASE)
    if m_pure_im and not re.search(r"[+-]\d", t):
        val = m_pure_im.group(1)
        if val in ["", "+"]:
            b = 1.0
        elif val == "-":
            b = -1.0
        else:
            b = float(val)
        return 0.0, b
    
    m_real = re.search(r"([+-]?\d+\.?\d*)", t)
    if m_real:
        return float(m_real.group(1)), 0.0
    return 1.0, 1.7320508


def extract_gcd_params(text: str):
    nums = [int(x) for x in re.findall(r"\b\d+\b", text)]
    if len(nums) >= 2:
        return nums[0], nums[1]
    return 1071, 462


def extract_permcomb_params(text: str):
    t_low = text.lower()
    if any(w in t_low for w in ["permutation", "permutations", "arrange", "order", "sequence", "line", "row", "npr", "arrangement"]):
        kind = "Permutation (nPr)"
    elif any(w in t_low for w in ["combination", "combinations", "choose", "chosen", "select", "committee", "group", "team", "pool", "volunteers", "people", "ncr", "member", "subset", "formed"]):
        kind = "Combination (nCr)"
    else:
        kind = "Combination (nCr)" if "c" in t_low else "Permutation (nPr)"

    nums = [int(x) for x in re.findall(r"\b\d+\b", text)]
    if len(nums) >= 2:
        n_val = max(nums[0], nums[1])
        r_val = min(nums[0], nums[1])
        return kind, n_val, r_val
    elif len(nums) == 1:
        return kind, max(5, nums[0]), min(2, nums[0])
    return kind, 5, 2


def extract_demoivre_params(text: str):
    a, b = extract_complex_parts(text)
    m_pow = re.search(r"[\^]\s*(\d+)", text)
    n = int(m_pow.group(1)) if m_pow else 4
    return a, b, n


def extract_limit_params(text: str):
    m_pt = re.search(r"(?:->|to|→)\s*([+-]?\w+)", text, re.IGNORECASE)
    point_str = m_pt.group(1) if m_pt else "0"
    m_expr = re.search(r"lim(?:its)?\s*(?:[a-zA-Z]\s*(?:->|to|→)\s*[+-]?\w+)?\s+(.+)", text, re.IGNORECASE)
    expr_str = m_expr.group(1).strip() if m_expr else "sin(3*x)/x"
    m_var = re.search(r"([a-zA-Z])\s*(?:->|to|→)", text)
    var_str = m_var.group(1) if m_var else "x"
    return expr_str, var_str, point_str


def parse_question(text: str):
    topic = detect_topic(text)
    if topic == "gcd":
        a, b = extract_gcd_params(text)
        return topic, {"a": a, "b": b}
    elif topic == "complex":
        a, b = extract_complex_parts(text)
        return topic, {"a": a, "b": b}
    elif topic == "demoivre":
        a, b, n = extract_demoivre_params(text)
        return topic, {"a": a, "b": b, "n": n}
    elif topic == "permcomb":
        kind, n, r = extract_permcomb_params(text)
        return topic, {"kind": kind, "n": n, "r": r}
    elif topic == "limits":
        expr_str, var_str, point_str = extract_limit_params(text)
        return topic, {"expr_str": expr_str, "var_str": var_str, "point_str": point_str}
    else:
        return topic, {}


# ============================================================
# SOLVER ALGORITHMS
# ============================================================
def solve_gcd(a: int, b: int):
    steps = []
    orig_a, orig_b = a, b
    a, b = abs(a), abs(b)
    if a < b:
        steps.append(("Ordering Check", f"Swap inputs so larger integer is first: a = {b}, b = {a}"))
        a, b = b, a

    step_idx = 1
    while b != 0:
        q = a // b
        r = a % b
        steps.append((f"Euclidean Step {step_idx}", f"{a} = {q} × {b} + {r}  (Quotient: {q}, Remainder: {r})"))
        a, b = b, r
        step_idx += 1

    gcd_val = a
    steps.append(("Final Result", f"The last non-zero remainder is {gcd_val}. Therefore, gcd({orig_a}, {orig_b}) = {gcd_val}."))
    return steps, str(gcd_val), {"gcd": gcd_val, "a": orig_a, "b": orig_b}


def solve_complex_to_polar(a: float, b: float):
    steps = []
    steps.append(("Identify Parts", f"Rectangular form z = a + bi with Real part a = {a}, Imaginary part b = {b}"))
    r = math.hypot(a, b)
    steps.append(("Compute Modulus (r)", f"r = √(a² + b²) = √(({a})² + ({b})²) = √({a**2 + b**2:.4f}) = {r:.4f}"))
    theta_rad = math.atan2(b, a)
    theta_deg = math.degrees(theta_rad)
    quadrant = "Quadrant I" if a >= 0 and b >= 0 else "Quadrant II" if a < 0 and b >= 0 else "Quadrant III" if a < 0 and b < 0 else "Quadrant IV"
    steps.append(("Compute Argument (θ)", f"θ = atan2(b, a) = atan2({b}, {a}) = {theta_rad:.4f} rad ({theta_deg:.2f}°)\nLocated in {quadrant}"))
    polar_str = f"{r:.4f} (cos({theta_deg:.2f}°) + i sin({theta_deg:.2f}°))"
    euler_str = f"{r:.4f} e^({theta_rad:.4f}i)"
    steps.append(("Formulate Polar & Exponential", f"Polar Form: z = {polar_str}\nExponential Form: z = {euler_str}"))
    return steps, polar_str, {"r": r, "theta_rad": theta_rad, "theta_deg": theta_deg, "a": a, "b": b}


def solve_demoivre(a: float, b: float, n: int):
    steps = []
    r = math.hypot(a, b)
    theta = math.atan2(b, a)
    theta_deg = math.degrees(theta)
    steps.append(("Convert to Polar", f"z = {a} + {b}i  →  r = {r:.4f}, θ = {theta_deg:.2f}°"))

    r_n = r ** n
    n_theta = n * theta
    n_theta_deg = math.degrees(n_theta)
    steps.append(("Apply De Moivre's Theorem", f"z^{n} = [r (cos θ + i sin θ)]^{n} = r^{n} [cos({n}θ) + i sin({n}θ)]"))
    steps.append(("Calculate Powered Values", f"Modulus r^{n} = {r:.4f}^{n} = {r_n:.4f}\nArgument {n}θ = {n} × {theta_deg:.2f}° = {n_theta_deg:.2f}°"))

    final_real = r_n * math.cos(n_theta)
    final_imag = r_n * math.sin(n_theta)
    sign = "+" if final_imag >= 0 else "-"
    ans_str = f"{final_real:.4f} {sign} {abs(final_imag):.4f}i"
    steps.append(("Convert back to Rectangular", f"z^{n} = {r_n:.4f}(cos({n_theta_deg:.2f}°) + i sin({n_theta_deg:.2f}°)) = {ans_str}"))
    return steps, ans_str, {"r_n": r_n, "n_theta": n_theta, "real": final_real, "imag": final_imag, "a": a, "b": b, "n": n}


def demoivre_roots(a: float, b: float, n: int):
    r = math.hypot(a, b)
    theta = math.atan2(b, a)
    r_root = r ** (1.0 / n)
    roots = []
    for k in range(n):
        angle = (theta + 2 * math.pi * k) / n
        re_ = r_root * math.cos(angle)
        im_ = r_root * math.sin(angle)
        roots.append((re_, im_, math.degrees(angle)))
    return roots, r_root


def solve_permcomb(kind: str, n: int, r: int):
    steps = []
    if r > n or n < 0 or r < 0:
        return [("Validation Error", "n must be ≥ r and both must be non-negative.")], "Invalid input", {}

    if "Permutation" in kind or "nPr" in kind:
        steps.append(("Formula Selection", f"Permutation formula: nPr = n! / (n - r)!"))
        val = math.perm(n, r)
        steps.append(("Substitute Values", f"{n}P{r} = {n}! / ({n} - {r})! = {n}! / {n - r}!"))
        terms = " × ".join(str(i) for i in range(n, n - r, -1)) if r > 0 else "1"
        steps.append(("Expanded Product", f"{n}P{r} = {terms} = {val}"))
        return steps, str(val), {"val": val, "type": "nPr"}
    else:
        steps.append(("Formula Selection", f"Combination formula: nCr = n! / (r! (n - r)!)"))
        val = math.comb(n, r)
        steps.append(("Substitute Values", f"{n}C{r} = {n}! / ({r}! × ({n} - {r})!)"))
        num_terms = " × ".join(str(i) for i in range(n, n - r, -1)) if r > 0 else "1"
        den_terms = " × ".join(str(i) for i in range(1, r + 1)) if r > 0 else "1"
        steps.append(("Simplified Factorials", f"{n}C{r} = ({num_terms}) / ({den_terms}) = {val}"))
        return steps, str(val), {"val": val, "type": "nCr"}


def solve_functions(domain: list, codomain: list, mapping: dict):
    steps = []
    steps.append(("Domain & Codomain Setup", f"Domain A = {{{', '.join(map(str, domain))}}}\nCodomain B = {{{', '.join(map(str, codomain))}}}"))
    map_str = ", ".join(f"f({k})={v}" for k, v in mapping.items())
    steps.append(("Mapping Definition", f"Mappings: {map_str}"))

    mapped_values = list(mapping.values())
    is_injective = len(mapped_values) == len(set(mapped_values))
    if is_injective:
        steps.append(("Injectivity Test (One-to-One)", "PASSED: All outputs are distinct. No two domain elements map to the same codomain element. Function is INJECTIVE."))
    else:
        duplicates = [x for x in set(mapped_values) if mapped_values.count(x) > 1]
        steps.append(("Injectivity Test (One-to-One)", f"FAILED: Multiple inputs map to the same codomain element(s): {duplicates}. Function is NOT Injective."))

    range_set = set(mapped_values)
    codomain_set = set(codomain)
    is_surjective = range_set == codomain_set
    if is_surjective:
        steps.append(("Surjectivity Test (Onto)", "PASSED: Range equals Codomain. Every element in Codomain B has at least one pre-image in Domain A. Function is SURJECTIVE."))
    else:
        uncovered = list(codomain_set - range_set)
        steps.append(("Surjectivity Test (Onto)", f"FAILED: Uncovered codomain elements with no pre-image: {uncovered}. Function is NOT Surjective."))

    is_bijective = is_injective and is_surjective
    classification = "BIJECTIVE (Bijective / One-to-One Correspondence)" if is_bijective else \
                     "INJECTIVE ONLY (One-to-One but not Onto)" if is_injective else \
                     "SURJECTIVE ONLY (Onto but not One-to-One)" if is_surjective else \
                     "NEITHER (Neither Injective nor Surjective)"

    steps.append(("Final Classification", f"Classification: {classification}"))
    return steps, classification, {"injective": is_injective, "surjective": is_surjective, "bijective": is_bijective}


def solve_limit(expr_str: str, var_str: str, point_str: str):
    steps = []
    x = symbols(var_str)
    transformations = standard_transformations + (implicit_multiplication_application,)
    
    try:
        expr = parse_expr(expr_str, transformations=transformations)
    except Exception as e:
        return [("Parsing Error", f"Could not parse expression: {e}")], "Error", {}

    if point_str.lower() in ["oo", "inf", "infinity"]:
        target_point = oo
        target_disp = "∞"
    elif point_str.lower() in ["-oo", "-inf", "-infinity"]:
        target_point = -oo
        target_disp = "-∞"
    else:
        try:
            target_point = parse_expr(point_str, transformations=transformations)
            target_disp = str(target_point)
        except Exception:
            target_point = 0
            target_disp = "0"

    steps.append(("Expression Parsing", f"Target Limit: lim ({var_str} → {target_disp})  [ {expr_str} ]"))
    
    try:
        direct_sub = expr.subs(x, target_point)
        steps.append(("Direct Substitution Check", f"Evaluating f({target_disp}): {direct_sub}"))
    except Exception:
        direct_sub = None
        steps.append(("Direct Substitution Check", "Direct substitution resulted in an undefined or indeterminate form."))

    try:
        lim_val = limit(expr, x, target_point)
        steps.append(("Symbolic Computation (SymPy)", f"lim ({var_str} → {target_disp}) = {lim_val}"))
    except Exception as e:
        return [("Computation Error", f"Failed to compute limit: {e}")], "Error", {}

    continuity_note = ""
    if direct_sub is not None and direct_sub == lim_val:
        continuity_note = f"Since lim ({var_str} → {target_disp}) f({var_str}) = f({target_disp}) = {lim_val}, the function is CONTINUOUS at {var_str} = {target_disp}."
    else:
        continuity_note = f"The limit is {lim_val}, but direct substitution gives {direct_sub}. The function has a removable or step discontinuity at {var_str} = {target_disp}."

    steps.append(("Continuity Diagnostic", continuity_note))
    return steps, str(lim_val), {"expr": expr, "var": x, "point": target_point, "lim_val": lim_val, "continuity_note": continuity_note}


# ============================================================
# INTERACTIVE PLOTLY VISUALIZATIONS
# ============================================================
def plot_complex_plane_plotly(points: list, labels: list, colors: list = None, draw_polygon: bool = False):
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

    if draw_polygon and len(points) > 1:
        px_coords = [p[0] for p in points] + [points[0][0]]
        py_coords = [p[1] for p in points] + [points[0][1]]
        fig.add_trace(go.Scatter(
            x=px_coords, y=py_coords,
            mode='lines', line=dict(color=TEAL, width=2),
            fill='toself', fillcolor='rgba(46, 196, 182, 0.12)',
            name='Roots Polygon'
        ))

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


def plot_function_diagram_plotly(domain: list, codomain: list, mapping: dict):
    fig = go.Figure()

    d_len = len(domain)
    c_len = len(codomain)

    d_y = np.linspace(1, 0, d_len) if d_len > 1 else [0.5]
    c_y = np.linspace(1, 0, c_len) if c_len > 1 else [0.5]

    d_pos = {elem: (0, d_y[i]) for i, elem in enumerate(domain)}
    c_pos = {elem: (1, c_y[i]) for i, elem in enumerate(codomain)}

    for dom_elem, codom_elem in mapping.items():
        if dom_elem in d_pos and codom_elem in c_pos:
            x0, y0 = d_pos[dom_elem]
            x1, y1 = c_pos[codom_elem]
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines', line=dict(color=TEAL, width=2.5),
                hoverinfo='skip', showlegend=False
            ))

    dx = [pos[0] for pos in d_pos.values()]
    dy = [pos[1] for pos in d_pos.values()]
    dtxt = [str(k) for k in d_pos.keys()]
    fig.add_trace(go.Scatter(
        x=dx, y=dy, mode='markers+text',
        marker=dict(size=28, color=AMBER, line=dict(width=2, color='#FFFFFF')),
        text=dtxt, textposition="middle center",
        textfont=dict(color="#000000", weight="bold"),
        hoverinfo='text', hovertext=[f"Domain element: {t}" for t in dtxt],
        name="Domain A"
    ))

    cx = [pos[0] for pos in c_pos.values()]
    cy = [pos[1] for pos in c_pos.values()]
    ctxt = [str(k) for k in c_pos.keys()]
    fig.add_trace(go.Scatter(
        x=cx, y=cy, mode='markers+text',
        marker=dict(size=28, color=CORAL, line=dict(width=2, color='#FFFFFF')),
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
            dict(x=0, y=1.1, text="<b>Domain A</b>", showarrow=False, font=dict(size=14, color=AMBER)),
            dict(x=1, y=1.1, text="<b>Codomain B</b>", showarrow=False, font=dict(size=14, color=CORAL)),
        ],
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        height=380
    )
    return fig


def plot_limit_function_plotly(expr, var, point):
    fig = go.Figure()
    
    try:
        if point == oo or point == -oo:
            p_val = 5.0
        else:
            p_val = float(point)
    except Exception:
        p_val = 0.0

    x_vals = np.linspace(p_val - 4, p_val + 4, 300)
    f_lambdified = sp.lambdify(var, expr, modules=["numpy", "math"])
    
    y_vals = []
    for xv in x_vals:
        try:
            yv = float(f_lambdified(xv))
            y_vals.append(yv if not (math.isnan(yv) or math.isinf(yv)) else np.nan)
        except Exception:
            y_vals.append(np.nan)

    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='lines', line=dict(color=TEAL, width=3),
        name=f"f({var}) = {expr}"
    ))

    try:
        target_y = float(limit(expr, var, point))
        fig.add_trace(go.Scatter(
            x=[p_val], y=[target_y],
            mode='markers',
            marker=dict(size=14, color=CORAL, line=dict(width=3, color='#FFFFFF')),
            hovertemplate=f"Limit Point<br>x = {p_val}<br>y = {target_y:.4f}<extra></extra>",
            name="Limit Point"
        ))
    except Exception:
        pass

    fig.update_layout(
        xaxis=dict(title=str(var), gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title=f"f({var})", gridcolor="rgba(255,255,255,0.05)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,18,38,0.6)",
        font=dict(color="#FFFFFF", family="Outfit"),
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        height=380
    )
    return fig


# ============================================================
# PROCEDURAL QUIZ GENERATOR
# ============================================================
def generate_procedural_question(topic_key: str = None):
    if not topic_key:
        topic_key = random.choice(list(TOPICS.keys()))

    if topic_key == "gcd":
        a = random.randint(100, 1500)
        b = random.randint(24, 450)
        steps, ans, extra = solve_gcd(a, b)
        correct = str(ans)
        opts = {correct, str(int(correct) + 2), str(max(1, int(correct) - 2)), str(int(correct) * 2)}
        while len(opts) < 4:
            opts.add(str(random.randint(1, 20)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"Find gcd({a}, {b}) using the Euclidean algorithm.",
            "topic": "gcd",
            "options": opts,
            "answer": correct,
            "exp": f"Applying Euclidean division steps:\n" + "\n".join([f"• {s[1]}" for s in steps])
        }

    elif topic_key == "complex":
        a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        b = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        r = math.hypot(a, b)
        deg = math.degrees(math.atan2(b, a))
        correct = f"{deg:.1f}°"
        opts = [f"{deg:.1f}°", f"{(deg + 45) % 360:.1f}°", f"{(deg + 90) % 360:.1f}°", f"{(deg - 30) % 360:.1f}°"]
        random.shuffle(opts)
        return {
            "q": f"Find the principal argument θ (in degrees) for z = {a} + {b}i.",
            "topic": "complex",
            "options": opts,
            "answer": correct,
            "exp": f"θ = atan2({b}, {a}) = {deg:.2f}°. Modulus r = √({a}² + {b}²) = {r:.3f}."
        }

    elif topic_key == "demoivre":
        n = random.randint(3, 6)
        mod_z = random.randint(2, 4)
        ans_mod = mod_z ** n
        correct = str(ans_mod)
        opts = [str(ans_mod), str(mod_z * n), str(ans_mod + n), str(max(1, ans_mod - 4))]
        random.shuffle(opts)
        return {
            "q": f"If a complex number has modulus |z| = {mod_z}, what is the modulus |z^{n}| by De Moivre's Theorem?",
            "topic": "demoivre",
            "options": opts,
            "answer": correct,
            "exp": f"By De Moivre's theorem, |zⁿ| = |z|ⁿ = {mod_z}^{n} = {ans_mod}."
        }

    elif topic_key == "permcomb":
        kind = random.choice(["nPr", "nCr"])
        n = random.randint(5, 9)
        r = random.randint(2, 4)
        steps, ans, _ = solve_permcomb(kind, n, r)
        correct = str(ans)
        opts = {correct, str(int(correct) + 5), str(max(1, int(correct) - 3)), str(int(correct) * 2)}
        while len(opts) < 4:
            opts.add(str(random.randint(5, 100)))
        opts = list(opts)
        random.shuffle(opts)
        return {
            "q": f"Evaluate {n}{kind[:1]}{r} ({'Permutations' if 'P' in kind else 'Combinations'}).",
            "topic": "permcomb",
            "options": opts,
            "answer": correct,
            "exp": f"Formula calculation:\n" + "\n".join([f"• {s[1]}" for s in steps])
        }

    elif topic_key == "functions":
        d = ["1", "2", "3"]
        c = ["a", "b", "c"] if random.random() > 0.5 else ["a", "b"]
        mapping = {"1": "a", "2": "b", "3": "c" if len(c) == 3 else "a"}
        steps, ans, extra = solve_functions(d, c, mapping)
        correct = "Yes" if extra["injective"] else "No"
        return {
            "q": f"Function f: {{{','.join(d)}}} → {{{','.join(c)}}} with mapping f(1)={mapping['1']}, f(2)={mapping['2']}, f(3)={mapping['3']}. Is f Injective?",
            "topic": "functions",
            "options": ["Yes", "No"],
            "answer": correct,
            "exp": f"Injectivity check: {steps[2][1]}"
        }

    else:  # limits
        k = random.randint(2, 6)
        correct = str(k)
        opts = [str(k), "0", "1", "∞"]
        random.shuffle(opts)
        return {
            "q": f"Evaluate lim (x → 0) sin({k}*x) / x.",
            "topic": "limits",
            "options": opts,
            "answer": correct,
            "exp": f"Standard trigonometric limit: lim(x→0) sin(kx)/x = k. Here k = {k}."
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
        if i < len(steps):
            st.markdown('<div class="timeline-connector">↓</div>', unsafe_allow_html=True)


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
# SIDEBAR NAVIGATION & PERSISTENCE METRICS
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
    "🧮 Euclidean Algorithm & GCD",
    "📍 Complex Numbers & Polar Form",
    "🔄 De Moivre's Theorem",
    "🔢 Permutations & Combinations",
    "🔗 Functions & Mappings",
    "📈 Limits & Continuity",
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
    st.markdown('<div class="hero-symbol-banner">∫   Σ   √   π   ∞</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">MATHMATE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Interactive Mathematics Lab · 6 Core Syllabus Topics • AI Assisted • Persistent History</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card" style="padding: 26px; border: 1px solid rgba(46, 196, 182, 0.35);">
        <div style="font-weight:800; font-size:1.35rem; color:#FFFFFF; margin-bottom:4px;">✨ What would you like to solve?</div>
        <div style="font-size:0.88rem; color:rgba(247,245,239,0.7); margin-bottom:16px;">Type or paste any syllabus problem below:</div>
    """, unsafe_allow_html=True)

    home_q_input = st.text_area("Question Input", key="home_question_input",
                                placeholder="e.g. Find GCD of 1071 and 462  OR  Choose 4 members from 9 available employees",
                                height=85, label_visibility="collapsed")
    
    st.caption("Quick sample questions:")
    sample_qs = {
        "gcd": "Find GCD of 1071 and 462",
        "complex": "Convert z = 1 + 1.73205i to polar form",
        "demoivre": "Find (1 + i)^4 using De Moivre's theorem",
        "permcomb": "Choose 4 members from a group of 9 available employees",
        "functions": "Domain: 1, 2, 3. Codomain: a, b, c",
        "limits": "lim x->0 sin(3*x)/x"
    }

    c1, c2, c3, c4 = st.columns(4)
    c1.button("💡 GCD: 1071 & 462", on_click=set_nav_page, args=("🧮 Euclidean Algorithm & GCD", sample_qs["gcd"]))
    c2.button("💡 Polar: 1 + 1.732i", on_click=set_nav_page, args=("📍 Complex Numbers & Polar Form", sample_qs["complex"]))
    c3.button("💡 Choose 4 from 9", on_click=set_nav_page, args=("🔢 Permutations & Combinations", sample_qs["permcomb"]))
    c4.button("💡 Limit: sin(3x)/x", on_click=set_nav_page, args=("📈 Limits & Continuity", sample_qs["limits"]))

    def handle_home_solve():
        q = st.session_state.get("home_question_input", "").strip()
        if q:
            detected, _ = parse_question(q)
            target = TOPIC_NAV_MAP.get(detected, "🧮 Euclidean Algorithm & GCD")
            st.session_state.preset_question = q
            st.session_state.nav_page = target

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("🧮 Solve Problem Step-by-Step", type="primary", use_container_width=True, on_click=handle_home_solve)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 Explore Syllabus Topics")
    
    topic_descriptions = {
        "gcd": ("🧮 Euclidean Algorithm & GCD", "Step-by-step Euclidean division, quotient-remainder breakdowns, and last non-zero remainder."),
        "complex": ("📍 Complex Numbers & Polar Form", "Rectangular to polar conversion, modulus r, argument θ, and interactive Argand plane."),
        "demoivre": ("🔄 De Moivre's Theorem", "Compute zⁿ and all n-th roots of complex numbers with interactive root polygon."),
        "permcomb": ("🔢 Permutations & Combinations", "Factorial formulas for nPr and nCr with step-by-step word problem solver."),
        "functions": ("🔗 Functions & Mappings", "Classify domain-to-codomain mappings with interactive bipartite graph diagrams."),
        "limits": ("📈 Limits & Continuity", "Symbolic limit computation via SymPy, direct substitution, and interactive limit curves."),
    }

    t_cols = st.columns(3)
    for i, (key, (title, desc)) in enumerate(topic_descriptions.items()):
        with t_cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="min-height: 150px;">
                <div style="font-weight:800; font-size:1.1rem; color:#2EC4B6; margin-bottom:8px;">{title}</div>
                <div style="font-size:0.88rem; color:rgba(247,245,239,0.8); line-height:1.4; margin-bottom:12px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"Learn & Solve →", key=f"card_btn_{key}",
                      on_click=set_nav_page, args=(TOPIC_NAV_MAP[key], sample_qs[key]))


# ============================================================
# SOLVER DISPATCHER (FOR ALL 6 TOPIC PAGES)
# ============================================================
elif page in TOPIC_NAV_MAP.values():
    current_topic_key = [k for k, v in TOPIC_NAV_MAP.items() if v == page][0]
    
    initial_q = st.session_state.pop("preset_question", "")
    question_text = st.text_area("Enter or edit your question", value=initial_q,
                                  placeholder=f"Type your problem for {TOPICS[current_topic_key]}...",
                                  height=80)

    # Dynamic Topic Detection & Auto-Redirection
    if question_text:
        detected_topic, parsed_params = parse_question(question_text)
    else:
        detected_topic, parsed_params = current_topic_key, {}

    # If the user typed a question that belongs to a DIFFERENT topic, offer 1-click switch & auto-route
    topic_key = current_topic_key
    if question_text and detected_topic != current_topic_key:
        detected_title = TOPICS.get(detected_topic, detected_topic)
        st.warning(f"🔍 Question detected for **{detected_title}**! (You are currently on the {TOPICS[current_topic_key]} page)")
        if st.button(f"🚀 Switch to {detected_title} & Solve Now", type="primary", use_container_width=True):
            st.session_state.preset_question = question_text
            st.session_state.nav_page = TOPIC_NAV_MAP[detected_topic]
            st.rerun()
        # Use detected topic parameters if the user proceeds
        topic_key = detected_topic

    st.markdown(f'<span class="topic-badge">{TOPICS[topic_key]}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title">{TOPICS[topic_key]}</div>', unsafe_allow_html=True)

    steps, answer, extra = None, None, {}
    auto_trigger = bool(question_text)
    domain_str, codomain_str, mapping = "1,2,3", "a,b,c,d", {}

    if topic_key == "gcd":
        c1, c2 = st.columns(2)
        default_a = parsed_params.get("a", 1071) if topic_key == detected_topic else 1071
        default_b = parsed_params.get("b", 462) if topic_key == detected_topic else 462
        a = c1.number_input("Integer a", value=int(default_a), step=1)
        b = c2.number_input("Integer b", value=int(default_b), step=1)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_gcd(a, b)

    elif topic_key == "complex":
        c1, c2 = st.columns(2)
        default_a = parsed_params.get("a", 1.0) if topic_key == detected_topic else 1.0
        default_b = parsed_params.get("b", 1.7320508) if topic_key == detected_topic else 1.7320508
        a = c1.number_input("Real part (a)", value=float(default_a))
        b = c2.number_input("Imaginary part (b)", value=float(default_b))
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_complex_to_polar(a, b)

    elif topic_key == "demoivre":
        c1, c2, c3 = st.columns(3)
        default_a = parsed_params.get("a", 1.0) if topic_key == detected_topic else 1.0
        default_b = parsed_params.get("b", 1.0) if topic_key == detected_topic else 1.0
        default_n = parsed_params.get("n", 4) if topic_key == detected_topic else 4
        a = c1.number_input("Real part (a)", value=float(default_a))
        b = c2.number_input("Imaginary part (b)", value=float(default_b))
        n = c3.number_input("Power n", value=int(default_n), step=1)
        show_roots = st.checkbox("Also show all n-th roots of z")
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            if show_roots:
                roots, r_root = demoivre_roots(a, b, int(n))
                steps = [("Convert to polar", f"z = {a} + {b}i → r = {math.hypot(a,b):.4f}, θ = {math.degrees(math.atan2(b,a)):.2f}°")]
                steps.append(("Root formula", f"wₖ = r^(1/n) [cos((θ+2πk)/n) + i sin((θ+2πk)/n)],  k = 0,…,{int(n)-1}"))
                for k, (re_, im_, ang) in enumerate(roots):
                    steps.append((f"Root k={k}", f"w{k} = {re_:.4f} + {im_:.4f}i  (angle {ang:.2f}°)"))
                answer = ", ".join(f"{re_:.3f}+{im_:.3f}i" for re_, im_, _ in roots)
                extra = {"roots": roots}
            else:
                steps, answer, extra = solve_demoivre(a, b, int(n))

    elif topic_key == "permcomb":
        c1, c2, c3 = st.columns(3)
        default_kind = parsed_params.get("kind", "Combination (nCr)") if topic_key == detected_topic else "Combination (nCr)"
        kind_opts = ["Permutation (nPr)", "Combination (nCr)"]
        kind_idx = kind_opts.index(default_kind) if default_kind in kind_opts else 1
        kind = c1.selectbox("Type", kind_opts, index=kind_idx)
        default_n = parsed_params.get("n", 10) if topic_key == detected_topic else 10
        default_r = parsed_params.get("r", 4) if topic_key == detected_topic else 4
        n = c2.number_input("n (total items)", value=int(default_n), step=1, min_value=0)
        r = c3.number_input("r (chosen items)", value=int(default_r), step=1, min_value=0)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_permcomb(kind, n, r)

    elif topic_key == "functions":
        c1, c2 = st.columns(2)
        domain_str = c1.text_input("Domain elements (comma-separated)", "1,2,3")
        codomain_str = c2.text_input("Codomain elements (comma-separated)", "a,b,c,d")
        domain = [x.strip() for x in domain_str.split(",") if x.strip()]
        codomain = [x.strip() for x in codomain_str.split(",") if x.strip()]
        mapping = {}
        mcols = st.columns(min(len(domain), 4) or 1)
        for i, d in enumerate(domain):
            with mcols[i % len(mcols)]:
                mapping[d] = st.selectbox(f"f({d}) =", codomain, key=f"map_{d}")
        if st.button("Classify function", type="primary") or (auto_trigger and len(domain) > 0):
            steps, answer, extra = solve_functions(domain, codomain, mapping)

    elif topic_key == "limits":
        c1, c2, c3 = st.columns(3)
        default_expr = parsed_params.get("expr_str", "sin(3*x)/x") if topic_key == detected_topic else "sin(3*x)/x"
        default_var = parsed_params.get("var_str", "x") if topic_key == detected_topic else "x"
        default_point = parsed_params.get("point_str", "0") if topic_key == detected_topic else "0"
        expr_str = c1.text_input("f(x) =", str(default_expr))
        var_str = c2.text_input("Variable", str(default_var))
        point_str = c3.text_input("x →", str(default_point))
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            try:
                steps, answer, extra = solve_limit(expr_str, var_str, point_str)
            except Exception as e:
                st.error(f"Couldn't parse that expression: {e}")

    # Optional AI Solver Fallback button
    if question_text and st.button("🤖 Ask AI Solver (LLM Fallback)", use_container_width=False):
        with st.spinner("AI Solver analyzing problem..."):
            ai_res = api_client.solve_with_ai(question_text)
            if ai_res:
                steps = ai_res.get("steps", [])
                answer = ai_res.get("answer", "")
                st.success("Solved via AI Math Engine!")

    # Save solution state
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

    # Render solution & Plotly charts
    if steps:
        st.markdown("---")
        sol_col, info_col = st.columns([7, 5])
        
        with sol_col:
            st.markdown("### 📚 STEP-BY-STEP REASONING")
            render_step_timeline(steps)
            
            st.markdown("### 📐 Interactive Mathematics Visualization")
            if topic_key == "complex":
                fig = plot_complex_plane_plotly([(extra["a"], extra["b"])], ["z"])
                st.plotly_chart(fig, use_container_width=True)
            elif topic_key == "demoivre":
                if "roots" in extra:
                    pts = [(re_, im_) for re_, im_, _ in extra["roots"]]
                    labs = [f"w{k}" for k in range(len(pts))]
                    fig = plot_complex_plane_plotly(pts, labs, draw_polygon=True)
                else:
                    fig = plot_complex_plane_plotly([(extra["real"], extra["imag"])], ["zⁿ"], colors=[AMBER])
                st.plotly_chart(fig, use_container_width=True)
            elif topic_key == "functions":
                fig = plot_function_diagram_plotly(
                    [x.strip() for x in domain_str.split(",") if x.strip()],
                    [x.strip() for x in codomain_str.split(",") if x.strip()],
                    mapping
                )
                st.plotly_chart(fig, use_container_width=True)
            elif topic_key == "limits":
                fig = plot_limit_function_plotly(extra["expr"], extra["var"], extra["point"])
                st.plotly_chart(fig, use_container_width=True)
                if extra.get("continuity_note"):
                    st.info(extra["continuity_note"])
            else:
                st.info("💡 Calculation breakdown completed.")

            # Save / Export Actions
            st.markdown("### 💾 Save & Export Solution")
            e1, e2, e3 = st.columns(3)
            with e1:
                if st.button("📋 Copy Answer", key="btn_copy_ans_act"):
                    st.session_state.show_copy_box = True
                    st.toast(f"📋 Answer '{answer}' ready to copy!")
            with e2:
                if DOCX_AVAILABLE:
                    buf = build_docx(question_text or TOPICS[topic_key], TOPICS[topic_key], steps, answer) if 'build_docx' in globals() else None
                    if buf:
                        st.download_button("📄 DOCX Export", buf, file_name="mathmate_solution.docx", key="dl_docx_btn")
                else:
                    st.caption("Install `python-docx` for DOCX.")
            with e3:
                if REPORTLAB_AVAILABLE:
                    buf = build_pdf(question_text or TOPICS[topic_key], TOPICS[topic_key], steps, answer) if 'build_pdf' in globals() else None
                    if buf:
                        st.download_button("📥 PDF Export", buf, file_name="mathmate_solution.pdf", key="dl_pdf_btn")
                else:
                    st.caption("Install `reportlab` for PDF.")

            if st.session_state.get("show_copy_box"):
                st.code(answer, language=None)

        with info_col:
            render_answer_card(answer)
            render_understand_panel(topic_key)

            # Persist to database (Supabase / SQLite)
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
    st.caption("Infinite procedurally-generated math problems across the 6 syllabus topics. Earn XP and level up!")

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
        
        # Save updated stats to DB
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
    st.caption("Key formulas, identities, and theorems for all 6 syllabus topics.")

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
