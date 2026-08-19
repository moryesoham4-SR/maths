"""
MathMate — Interactive Mathematics Lab
Streamlit app covering: Euclidean Algorithm & GCD, Complex Numbers & Polar Form,
De Moivre's Theorem, Permutations & Combinations, Injective/Surjective/Bijective
Functions, and Limits & Continuity.
"""

import io
import re
import math
import random
from datetime import datetime

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import symbols, sympify, limit, oo, latex, I, re as s_re, im as s_im, Rational
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
)


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
# PAGE CONFIG & THEME
# ============================================================
st.set_page_config(page_title="MathMate — Interactive Mathematics Lab",
                    page_icon="🧮", layout="wide")

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

.hero-title {{
    background: linear-gradient(135deg, #FFFFFF 0%, {TEAL} 50%, {AMBER} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
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
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
}}

.glass-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(46, 196, 182, 0.4);
    box-shadow: 0 12px 35px 0 rgba(46, 196, 182, 0.15);
}}

.step-box {{
    background: rgba(247, 245, 239, 0.03);
    border: 1px solid rgba(247, 245, 239, 0.1);
    border-left: 4px solid {TEAL};
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}

.step-title {{
    color: {TEAL};
    font-weight: 700;
    font-size: 0.88rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 6px;
}}

.result-box {{
    background: linear-gradient(135deg, rgba(46, 196, 182, 0.18) 0%, rgba(255, 182, 39, 0.12) 100%);
    border: 1px solid {TEAL};
    border-radius: 14px;
    padding: 20px 24px;
    font-size: 1.25rem;
    font-weight: 700;
    color: {TEAL};
    box-shadow: 0 8px 30px rgba(46, 196, 182, 0.2);
    margin: 16px 0;
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

[data-testid="stSidebar"] {{
    background-color: #091224;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}}
</style>
""", unsafe_allow_html=True)


# ============================================================
# TOPIC DEFINITIONS + DETECTION
# ============================================================
TOPICS = {
    "gcd": "🧮 Euclidean Algorithm & GCD",
    "complex": "📍 Complex Numbers & Polar Form",
    "demoivre": "🔄 De Moivre's Theorem",
    "permcomb": "🔢 Permutations & Combinations",
    "functions": "🔗 Injective, Surjective & Bijective Functions",
    "limits": "📈 Limits & Continuity",
}

TOPIC_KEYWORDS = {
    "gcd": ["gcd", "hcf", "euclidean", "greatest common divisor", "highest common factor"],
    "complex": ["polar form", "modulus", "argument", "rectangular form", "complex number", "argand"],
    "demoivre": ["de moivre", "demoivre", "nth root", "z^n", "power of complex", "roots of unity"],
    "permcomb": ["permutation", "combination", "arrange", "select", "ncr", "npr", "how many ways"],
    "functions": ["injective", "surjective", "bijective", "one-one", "onto", "into", "mapping"],
    "limits": ["limit", "lim ", "continuity", "continuous", "discontinuous", "x->", "x→"],
}


def detect_topic(text: str) -> str:
    """Very lightweight keyword-based topic classifier with a scoring fallback."""
    t = text.lower()
    scores = {k: 0 for k in TOPICS}
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[topic] += 1
    # heuristics for symbol-only inputs
    if re.search(r"\bi\b|√-?1|imaginary", t):
        scores["complex"] += 1
    if re.search(r"\(.*\)\^\d|\^n\b", t):
        scores["demoivre"] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def extract_complex_parts(text: str):
    """Extracts (a, b) floats for complex number a + bi from text."""
    t = text.strip()
    try:
        clean = re.sub(r'\b[zZ]\s*=\s*', '', t)
        m_sub = re.search(r'([+-]?\s*\d*\.?\d*\s*[\+\-]?\s*\d*\.?\d*\s*\*?\s*i|\d*\.?\d*\s*\*?\s*i)', clean, re.IGNORECASE)
        if m_sub:
            sub = m_sub.group(0).replace(" ", "").replace("j", "i")
            sub_sp = re.sub(r'(\d+|\b)i\b', r'\1*I', sub, flags=re.IGNORECASE)
            expr = sympify(sub_sp)
            if expr.has(I) or expr.is_number:
                re_val = float(sp.re(expr).evalf())
                im_val = float(sp.im(expr).evalf())
                return re_val, im_val
    except Exception:
        pass

    m = re.search(r'([+-]?\s*\d*\.?\d+)?\s*([+-])?\s*(\d*\.?\d*)i', text, re.IGNORECASE)
    if m:
        r_str, sign, im_str = m.group(1), m.group(2), m.group(3)
        a = float(r_str.replace(" ", "")) if r_str and r_str.strip() not in ("+", "-") else (
            -1.0 if r_str and "-" in r_str else 0.0)
        b_val = float(im_str.replace(" ", "")) if im_str and im_str.strip() else 1.0
        if sign == "-":
            b_val = -b_val
        return a, b_val

    return None, None


def extract_gcd_params(text: str):
    nums = [int(n) for n in re.findall(r'\b\d+\b', text)]
    if len(nums) >= 2:
        return {"a": nums[0], "b": nums[1]}
    return {}


def extract_permcomb_params(text: str):
    p_match = re.search(r'(\d+)\s*[pP]\s*(\d+)|P\(\s*(\d+)\s*,\s*(\d+)\s*\)', text)
    if p_match:
        g = [x for x in p_match.groups() if x is not None]
        return {"kind": "Permutation (nPr)", "n": int(g[0]), "r": int(g[1])}

    c_match = re.search(r'(\d+)\s*[cC]\s*(\d+)|C\(\s*(\d+)\s*,\s*(\d+)\s*\)|(\d+)\s*choose\s*(\d+)', text, re.IGNORECASE)
    if c_match:
        g = [x for x in c_match.groups() if x is not None]
        return {"kind": "Combination (nCr)", "n": int(g[0]), "r": int(g[1])}

    return {}


def extract_demoivre_params(text: str):
    pow_match = re.search(r'\^(\d+)|\bpower\s*(\d+)|\bto the (\d+)', text, re.IGNORECASE)
    n = 4
    if pow_match:
        g = [x for x in pow_match.groups() if x is not None]
        n = int(g[0])

    a, b = extract_complex_parts(text)
    if a is not None and b is not None:
        return {"a": a, "b": b, "n": n}
    return {}


def extract_limit_params(text: str):
    m1 = re.search(r'(?:lim|limit)\s*(?:of)?\s*(?:_\{|\()?\s*([a-zA-Z])\s*(?:->|→|=)\s*([^\s\):\}]+)(?:\}|\))?\s*(.+)', text, re.IGNORECASE)
    if m1:
        var_str = m1.group(1).strip()
        point_str = m1.group(2).strip()
        expr_str = m1.group(3).strip().lstrip("=").strip()
        return {"expr_str": expr_str, "var_str": var_str, "point_str": point_str}

    m2 = re.search(r'(?:lim|limit)\s*(?:of)?\s*(.+?)\s+(?:as|when|for)\s+([a-zA-Z])\s*(?:->|→|=)\s*([^\s,]+)', text, re.IGNORECASE)
    if m2:
        expr_str = m2.group(1).strip().lstrip("=").strip()
        var_str = m2.group(2).strip()
        point_str = m2.group(3).strip()
        return {"expr_str": expr_str, "var_str": var_str, "point_str": point_str}

    return {}


def parse_question(text: str):
    """
    Parses pasted question text, returns (topic_key, extracted_params_dict).
    """
    if not text or not text.strip():
        return None, {}

    t = text.strip()

    if "lim" in t.lower() or "limit" in t.lower():
        params = extract_limit_params(t)
        if params:
            return "limits", params

    if re.search(r'\b\d+\s*[pPcC]\s*\d+\b|\b[pPcC]\(\s*\d+|\bchoose\b', t, re.IGNORECASE):
        params = extract_permcomb_params(t)
        if params:
            return "permcomb", params

    if ("de moivre" in t.lower() or "demoivre" in t.lower() or "^" in t) and re.search(r'i\b', t, re.IGNORECASE):
        params = extract_demoivre_params(t)
        if params:
            return "demoivre", params

    if "polar" in t.lower() or "modulus" in t.lower() or "argument" in t.lower() or re.search(r'i\b', t, re.IGNORECASE):
        a, b = extract_complex_parts(t)
        if a is not None and b is not None:
            return "complex", {"a": a, "b": b}

    if any(kw in t.lower() for kw in ["gcd", "hcf", "euclidean", "greatest common"]):
        params = extract_gcd_params(t)
        if params:
            return "gcd", params

    detected = detect_topic(t)
    if detected == "gcd":
        params = extract_gcd_params(t)
        return "gcd", params
    elif detected == "complex":
        a, b = extract_complex_parts(t)
        if a is not None and b is not None:
            return "complex", {"a": a, "b": b}
    elif detected == "demoivre":
        params = extract_demoivre_params(t)
        if params:
            return "demoivre", params
    elif detected == "permcomb":
        params = extract_permcomb_params(t)
        if params:
            return "permcomb", params
    elif detected == "limits":
        params = extract_limit_params(t)
        if params:
            return "limits", params

    return detected, {}



# ============================================================
# SOLVERS — each returns (steps: list[(title, body)], final_answer: str, extra: dict)
# ============================================================

def solve_gcd(a: int, b: int):
    steps = []
    a, b = abs(int(a)), abs(int(b))
    x, y = a, b
    if y == 0:
        return [("Edge case", f"gcd({x}, 0) = {x}")], str(x), {}
    steps.append(("Set up", f"Apply the Euclidean Algorithm to gcd({x}, {y})."))
    while y != 0:
        q = x // y
        r = x % y
        steps.append((f"Divide", f"{x} = {q} × {y} + {r}"))
        x, y = y, r
    steps.append(("Remainder is 0", f"Stop — the last non-zero remainder is the GCD."))
    return steps, str(x), {"pairs": (a, b)}


def solve_complex_to_polar(a: float, b: float):
    steps = []
    steps.append(("Identify the form", f"z = {a} + {b}i is in rectangular (x + yi) form."))
    r = math.sqrt(a**2 + b**2)
    steps.append(("Find the modulus", f"r = √(x² + y²) = √({a}² + {b}²) = √{a**2 + b**2:g} = {r:.4f}"))
    theta = math.atan2(b, a)
    theta_deg = math.degrees(theta)
    quadrant = "1st" if a > 0 and b >= 0 else "2nd" if a < 0 and b >= 0 else "3rd" if a < 0 and b < 0 else "4th"
    steps.append(("Find the argument", f"θ = atan2(y, x) = {theta:.4f} rad ≈ {theta_deg:.2f}°  ({quadrant} quadrant)"))
    steps.append(("Write in polar form", f"z = r(cosθ + i sinθ) = {r:.4f}(cos({theta_deg:.2f}°) + i·sin({theta_deg:.2f}°))"))
    answer = f"z = {r:.4f} · (cos {theta_deg:.2f}° + i sin {theta_deg:.2f}°)"
    return steps, answer, {"r": r, "theta": theta, "a": a, "b": b}


def solve_demoivre(a: float, b: float, n: int):
    steps = []
    steps.append(("Convert to polar", f"Start from z = {a} + {b}i and convert to polar form first."))
    r = math.sqrt(a**2 + b**2)
    theta = math.atan2(b, a)
    steps.append(("Modulus & argument", f"r = {r:.4f},  θ = {math.degrees(theta):.2f}°"))
    steps.append(("Apply De Moivre's theorem", f"zⁿ = rⁿ(cos(nθ) + i sin(nθ)),  n = {n}"))
    r_n = r ** n
    theta_n = theta * n
    theta_n_deg = math.degrees(theta_n) % 360
    steps.append(("Compute rⁿ and nθ", f"rⁿ = {r:.4f}^{n} = {r_n:.4f}\nnθ = {n} × {math.degrees(theta):.2f}° = {theta_n_deg:.2f}° (mod 360°)"))
    real_part = r_n * math.cos(theta_n)
    imag_part = r_n * math.sin(theta_n)
    steps.append(("Convert back to rectangular", f"zⁿ = {r_n:.4f}(cos {theta_n_deg:.2f}° + i sin {theta_n_deg:.2f}°) = {real_part:.4f} + {imag_part:.4f}i"))
    answer = f"z^{n} ≈ {real_part:.4f} + {imag_part:.4f}i"
    return steps, answer, {"r_n": r_n, "theta_n": theta_n, "real": real_part, "imag": imag_part}


def demoivre_roots(a: float, b: float, n: int):
    """All n-th roots of z = a+bi."""
    r = math.sqrt(a**2 + b**2)
    theta = math.atan2(b, a)
    r_root = r ** (1 / n)
    roots = []
    for k in range(n):
        angle = (theta + 2 * math.pi * k) / n
        roots.append((r_root * math.cos(angle), r_root * math.sin(angle), math.degrees(angle)))
    return roots, r_root


def solve_permcomb(kind: str, n: int, r: int):
    steps = []
    n, r = int(n), int(r)
    if r > n:
        return [("Invalid input", "r cannot be greater than n.")], "Undefined", {}
    if kind == "Permutation (nPr)":
        steps.append(("Formula", "nPr = n! / (n − r)!"))
        steps.append(("Substitute", f"{n}P{r} = {n}! / ({n} − {r})! = {n}! / {n-r}!"))
        val = math.perm(n, r)
        steps.append(("Simplify", f"= {' × '.join(str(i) for i in range(n, n-r, -1))} = {val}"))
        answer = str(val)
    else:
        steps.append(("Formula", "nCr = n! / (r! (n − r)!)"))
        steps.append(("Substitute", f"{n}C{r} = {n}! / ({r}! × {n-r}!)"))
        val = math.comb(n, r)
        steps.append(("Simplify", f"= {val}"))
        answer = str(val)
    return steps, answer, {}


def solve_functions(domain: list, codomain: list, mapping: dict):
    """mapping: dict domain_element -> codomain_element"""
    steps = []
    steps.append(("Set up", f"Domain = {domain}, Codomain = {codomain}, mapping f = {mapping}"))
    images = list(mapping.values())
    is_injective = len(images) == len(set(images))
    steps.append(("Check injectivity (one-one)",
                  "No two distinct domain elements share an image." if is_injective
                  else "Two or more domain elements map to the same image → not injective."))
    is_surjective = set(codomain) == set(images)
    unmapped = set(codomain) - set(images)
    steps.append(("Check surjectivity (onto)",
                  "Every element of the codomain is hit by some domain element." if is_surjective
                  else f"Codomain element(s) {sorted(unmapped)} have no pre-image → not surjective."))
    is_bijective = is_injective and is_surjective
    steps.append(("Conclusion", "Bijective (both injective and surjective)." if is_bijective
                  else "Not bijective."))
    classification = []
    if is_injective: classification.append("Injective")
    if is_surjective: classification.append("Surjective")
    if is_bijective: classification.append("Bijective")
    answer = ", ".join(classification) if classification else "Neither injective nor surjective"
    return steps, answer, {"injective": is_injective, "surjective": is_surjective, "bijective": is_bijective}


def solve_limit(expr_str: str, var_str: str, point_str: str):
    steps = []
    x = symbols(var_str)
    transformations = standard_transformations + (implicit_multiplication_application,)
    expr = parse_expr(expr_str.replace("^", "**"), transformations=transformations)
    point = oo if point_str.strip() in ("inf", "infinity", "oo") else \
            -oo if point_str.strip() in ("-inf", "-infinity", "-oo") else sympify(point_str)

    steps.append(("Original expression", f"lim_{{{var_str}→{point_str}}} {expr}"))

    # try direct substitution first
    try:
        direct = expr.subs(x, point)
        if direct.is_finite and not direct.has(sp.zoo, sp.nan):
            steps.append(("Direct substitution", f"Substitute {var_str} = {point_str}: result is finite → {direct}"))
            result = direct
        else:
            raise ValueError("indeterminate")
    except Exception:
        steps.append(("Direct substitution", f"Substituting {var_str} = {point_str} gives an indeterminate form (0/0 or ∞/∞) — simplify or apply L'Hôpital's rule."))
        result = limit(expr, x, point)
        simplified = sp.simplify(expr)
        if simplified != expr:
            steps.append(("Simplify", f"Simplify the expression: {simplified}"))
        steps.append(("Evaluate the limit", f"L = {result}"))

    # continuity check at the point (only for finite points)
    continuity_note = None
    if point not in (oo, -oo):
        try:
            f_val = expr.subs(x, point)
            if sp.simplify(f_val - result) == 0 and f_val.is_finite:
                continuity_note = f"f({var_str}) is continuous at {var_str} = {point_str} since lim = f({point_str}) = {result}."
            else:
                continuity_note = f"f({var_str}) is NOT continuous at {var_str} = {point_str} (limit ≠ function value, or function undefined there)."
        except Exception:
            continuity_note = None
    steps.append(("Final result", f"lim_{{{var_str}→{point_str}}} {expr} = {result}"))
    answer = str(result)
    return steps, answer, {"continuity_note": continuity_note, "expr": expr, "var": x, "point": point}


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_complex_plane(points: list, labels: list, colors: list = None, draw_polygon: bool = False):
    fig, ax = plt.subplots(figsize=(4.8, 4.8), dpi=180)
    fig.patch.set_facecolor("#0b132b")
    ax.set_facecolor("#0b132b")
    colors = colors or [TEAL, AMBER, CORAL, "#9B5DE5", "#00B4D8", "#F72585"]
    max_r = max([abs(complex(*p)) for p in points] + [1]) * 1.35
    
    ax.axhline(0, color="rgba(247,245,239,0.25)", alpha=0.3, linewidth=1)
    ax.axvline(0, color="rgba(247,245,239,0.25)", alpha=0.3, linewidth=1)
    ax.grid(True, color="#1c2d42", linestyle=":", linewidth=0.8, alpha=0.6)

    r_val = abs(complex(*points[0]))
    if r_val > 0:
        circle = plt.Circle((0, 0), r_val, color=TEAL, fill=False, linestyle="--", alpha=0.35, linewidth=1.2)
        ax.add_patch(circle)

    if draw_polygon and len(points) > 2:
        poly_pts = points + [points[0]]
        px, py = zip(*poly_pts)
        ax.plot(px, py, color=AMBER, linestyle="--", linewidth=1.2, alpha=0.65, label="Roots Polygon")

    for i, (p, lab) in enumerate(zip(points, labels)):
        c = colors[i % len(colors)]
        ax.annotate("", xy=(p[0], p[1]), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=c, lw=1.8, alpha=0.85))
        ax.scatter([p[0]], [p[1]], color=c, s=55, zorder=5, edgecolors="#ffffff", linewidths=0.8)
        ax.annotate(f" {lab}\n ({p[0]:.2f}, {p[1]:.2f}i)", (p[0], p[1]), textcoords="offset points", xytext=(8, 6),
                    color=c, fontsize=9, fontweight="bold")

    ax.set_xlim(-max_r, max_r)
    ax.set_ylim(-max_r, max_r)
    ax.set_xlabel("Real Axis (Re)", color=PAPER, fontsize=9, fontweight="bold")
    ax.set_ylabel("Imaginary Axis (Im)", color=PAPER, fontsize=9, fontweight="bold")
    ax.tick_params(colors=PAPER, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#1c2d42")
    ax.set_aspect("equal")
    return fig


def plot_function_diagram(domain, codomain, mapping):
    fig, ax = plt.subplots(figsize=(5.5, 3.5), dpi=180)
    fig.patch.set_facecolor("#0b132b")
    ax.set_facecolor("#0b132b")
    ax.axis("off")
    y_dom = np.linspace(0.85, 0.15, len(domain)) if len(domain) > 1 else [0.5]
    y_cod = np.linspace(0.85, 0.15, len(codomain)) if len(codomain) > 1 else [0.5]
    dom_pos = {d: (0.15, y) for d, y in zip(domain, y_dom)}
    cod_pos = {c: (0.75, y) for c, y in zip(codomain, y_cod)}
    
    ax.add_patch(plt.Circle((0.15, 0.5), 0.42, color="rgba(46,196,182,0.08)", fill=True, ec=TEAL, ls="--", lw=1.2))
    ax.add_patch(plt.Circle((0.75, 0.5), 0.42, color="rgba(255,182,39,0.08)", fill=True, ec=AMBER, ls="--", lw=1.2))

    for d, (x, y) in dom_pos.items():
        ax.scatter([x], [y], color=TEAL, s=280, zorder=5, edgecolors="#ffffff", lw=1)
        ax.annotate(str(d), (x, y), color="#080e1e", ha="center", va="center", fontweight="bold", fontsize=10)
    for c, (x, y) in cod_pos.items():
        ax.scatter([x], [y], color=AMBER, s=280, zorder=5, edgecolors="#ffffff", lw=1)
        ax.annotate(str(c), (x, y), color="#080e1e", ha="center", va="center", fontweight="bold", fontsize=10)
    for d, c in mapping.items():
        x1, y1 = dom_pos[d]
        x2, y2 = cod_pos[c]
        ax.annotate("", xy=(x2 - 0.05, y2), xytext=(x1 + 0.05, y1),
                    arrowprops=dict(arrowstyle="->", color=PAPER, alpha=0.75, lw=1.6, connectionstyle="arc3,rad=0.08"))
    ax.text(0.15, 0.98, "Domain", color=TEAL, ha="center", fontsize=11, fontweight="bold")
    ax.text(0.75, 0.98, "Codomain", color=AMBER, ha="center", fontsize=11, fontweight="bold")
    return fig


def plot_limit_function(expr, var, point):
    fig, ax = plt.subplots(figsize=(5.5, 3.5), dpi=180)
    fig.patch.set_facecolor("#0b132b")
    ax.set_facecolor("#0b132b")
    ax.grid(True, color="#1c2d42", linestyle=":", linewidth=0.8, alpha=0.6)
    try:
        pt = float(point) if point not in (oo, -oo) else 0
        xs = np.linspace(pt - 5, pt + 5, 500)
        f = sp.lambdify(var, expr, "numpy")
        with np.errstate(all="ignore"):
            ys = f(xs)
        ax.plot(xs, ys, color=TEAL, linewidth=3, alpha=0.3)
        ax.plot(xs, ys, color=TEAL, linewidth=1.8, label=f"f({var}) = {expr}")
        ax.axvline(pt, color=AMBER, linestyle="--", alpha=0.85, linewidth=1.4, label=f"Approach: {var} → {point}")
        
        try:
            lim_val = float(sp.limit(expr, var, point))
            ax.scatter([pt], [lim_val], color=CORAL, s=60, zorder=6, edgecolors="#ffffff", lw=1.2, label=f"L = {lim_val:.4f}")
        except Exception:
            pass

        ax.legend(facecolor="#091224", labelcolor=PAPER, edgecolor="#1c2d42", fontsize=8)
    except Exception:
        ax.text(0.5, 0.5, "Graph unavailable for this expression", color=PAPER, ha="center", va="center")
    ax.tick_params(colors=PAPER, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#1c2d42")
    return fig


# ============================================================
# EXPORT HELPERS
# ============================================================

def build_docx(question, topic, steps, answer):
    doc = Document()
    doc.add_heading("MathMate — Solution", level=1)
    doc.add_paragraph(f"Topic: {topic}")
    doc.add_paragraph(f"Question: {question}")
    doc.add_heading("Step-by-step solution", level=2)
    for title, body in steps:
        doc.add_paragraph(title, style="Heading 3")
        doc.add_paragraph(body)
    doc.add_heading("Final Answer", level=2)
    doc.add_paragraph(answer)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def build_pdf(question, topic, steps, answer):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("MathMate — Solution", styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph(f"<b>Topic:</b> {topic}", styles["Normal"]))
    story.append(Paragraph(f"<b>Question:</b> {question}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Step-by-step solution", styles["Heading2"]))
    for title, body in steps:
        story.append(Paragraph(f"<b>{title}</b>", styles["Normal"]))
        story.append(Paragraph(body.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 6))
    story.append(Paragraph("Final Answer", styles["Heading2"]))
    story.append(Paragraph(str(answer), styles["Normal"]))
    doc.build(story)
    buf.seek(0)
    return buf


def render_steps(steps):
    for title, body in steps:
        st.markdown(f"""
        <div class="step-box">
            <div class="step-title">{title}</div>
            <div style="white-space:pre-line;">{body}</div>
        </div>
        """, unsafe_allow_html=True)


def push_history(question, topic, answer):
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {
        "question": question, "topic": topic, "answer": answer,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })


# ============================================================
# SIDEBAR NAV
# ============================================================
st.sidebar.markdown("## 🧮 MathMate")
st.sidebar.caption("Interactive Mathematics Lab")
page = st.sidebar.radio("Navigate", ["🏠 Home", "✨ Solve", "📐 Formula Reference", "🎯 Practice & Quiz", "🕘 History"], label_visibility="collapsed")

if "streak" not in st.session_state:
    st.session_state.streak = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = {"correct": 0, "total": 0}

st.sidebar.markdown("---")
streak = st.session_state.streak
tier_badge = "🌱 Novice" if streak < 2 else "🥉 Apprentice" if streak < 5 else "🥈 Scholar" if streak < 10 else "👑 Math Wizard"
st.sidebar.metric("🔥 Streak & Rank", f"{streak} · {tier_badge}")

if st.session_state.quiz_score["total"] > 0:
    pct = round(100 * st.session_state.quiz_score["correct"] / st.session_state.quiz_score["total"])
    st.sidebar.metric("🎯 Quiz accuracy", f"{pct}%")


# ============================================================
# PAGE: HOME
# ============================================================
if page == "🏠 Home":
    st.markdown('<div class="hero-title">🧮 MathMate Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Interactive Mathematics Solver · Instant Topic Parser · High-DPI Visualizations · Step-by-Step Proofs</div>', unsafe_allow_html=True)
    st.write("Pick a syllabus topic below to open the interactive solver:")
    
    topic_descriptions = {
        "gcd": ("🧮 Euclidean Algorithm & GCD", "Step-by-step Euclidean division, quotient-remainder breakdowns, and last non-zero remainder."),
        "complex": ("📍 Complex Numbers & Polar Form", "Rectangular to polar conversion, modulus r, argument θ in radians/degrees, and Argand plane."),
        "demoivre": ("🔄 De Moivre's Theorem", "Compute zⁿ and all n-th roots of complex numbers with geometric roots polygon."),
        "permcomb": ("🔢 Permutations & Combinations", "Factorial formulas for nPr and nCr with step-by-step simplification."),
        "functions": ("🔗 Injective, Surjective & Bijective", "Classify domain-to-codomain mappings with interactive arrow diagrams."),
        "limits": ("📈 Limits & Continuity", "Symbolic limit computation via SymPy, direct substitution, and continuity diagnostics."),
    }
    
    cols = st.columns(3)
    for i, (key, (title, desc)) in enumerate(topic_descriptions.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="min-height: 140px;">
                <div style="font-weight:700; font-size:1.1rem; color:#2EC4B6; margin-bottom:8px;">{title}</div>
                <div style="font-size:0.88rem; color:rgba(247,245,239,0.8); line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Solve {title.split()[0]} →", key=f"btn_home_{key}"):
                sample_qs = {
                    "gcd": "Find GCD of 1071 and 462",
                    "complex": "Convert z = 1 + 1.73205i to polar form",
                    "demoivre": "Find (1 + i)^4 using De Moivre's theorem",
                    "permcomb": "Find 5C2",
                    "functions": "Domain: 1, 2, 3. Codomain: a, b, c",
                    "limits": "lim x->0 sin(3*x)/x"
                }
                st.session_state.preset_question = sample_qs[key]
                st.session_state.nav_page = "✨ Solve"
                st.rerun()


# ============================================================
# PAGE: SOLVE
# ============================================================
elif page == "✨ Solve":
    st.markdown('<div class="hero-title">✨ Interactive Solver</div>', unsafe_allow_html=True)
    st.caption("Paste any question or click a quick sample chip below:")

    chip_c1, chip_c2, chip_c3, chip_c4, chip_c5 = st.columns(5)
    if chip_c1.button("💡 GCD: 1071 & 462"):
        st.session_state.preset_question = "Find GCD of 1071 and 462"
    if chip_c2.button("💡 Polar: 1 + 1.732i"):
        st.session_state.preset_question = "Convert z = 1 + 1.73205i to polar form"
    if chip_c3.button("💡 De Moivre: (1+i)⁴"):
        st.session_state.preset_question = "Find (1 + i)^4 using De Moivre"
    if chip_c4.button("💡 5C2"):
        st.session_state.preset_question = "Find 5C2"
    if chip_c5.button("💡 Limit: sin(3x)/x"):
        st.session_state.preset_question = "lim x->0 sin(3*x)/x"

    initial_q = st.session_state.pop("preset_question", "")
    question_text = st.text_area("Enter your question", value=initial_q,
                                  placeholder="e.g. Find z⁴ if z = 1 + i√3, expressing the answer in rectangular form.",
                                  height=90)

    detected, parsed_params = parse_question(question_text) if question_text else (None, {})
    topic_options = list(TOPICS.keys())
    default_idx = topic_options.index(detected) if (detected and detected in topic_options) else 0
    if detected:
        st.markdown(f'<span class="topic-badge">✨ AUTO-PARSED: {TOPICS[detected]}</span>', unsafe_allow_html=True)
    chosen = st.selectbox("Topic (auto-detected — override if needed)",
                           topic_options, index=default_idx, format_func=lambda k: TOPICS[k])
    st.markdown("---")

    steps, answer, extra = None, None, {}
    auto_trigger = bool(question_text and parsed_params and detected == chosen)

    if chosen == "gcd":
        c1, c2 = st.columns(2)
        default_a = parsed_params.get("a", 1071) if chosen == detected else 1071
        default_b = parsed_params.get("b", 462) if chosen == detected else 462
        a = c1.number_input("a", value=int(default_a), step=1)
        b = c2.number_input("b", value=int(default_b), step=1)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_gcd(a, b)

    elif chosen == "complex":
        c1, c2 = st.columns(2)
        default_a = parsed_params.get("a", 1.0) if chosen == detected else 1.0
        default_b = parsed_params.get("b", 1.7320508) if chosen == detected else 1.7320508
        a = c1.number_input("Real part (a)", value=float(default_a))
        b = c2.number_input("Imaginary part (b)", value=float(default_b))
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_complex_to_polar(a, b)

    elif chosen == "demoivre":
        c1, c2, c3 = st.columns(3)
        default_a = parsed_params.get("a", 1.0) if chosen == detected else 1.0
        default_b = parsed_params.get("b", 1.7320508) if chosen == detected else 1.7320508
        default_n = parsed_params.get("n", 4) if chosen == detected else 4
        a = c1.number_input("Real part (a)", value=float(default_a))
        b = c2.number_input("Imaginary part (b)", value=float(default_b))
        n = c3.number_input("Power n", value=int(default_n), step=1)
        show_roots = st.checkbox("Also show all n-th roots of z (instead of zⁿ)")
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

    elif chosen == "permcomb":
        c1, c2, c3 = st.columns(3)
        default_kind = parsed_params.get("kind", "Permutation (nPr)") if chosen == detected else "Permutation (nPr)"
        kind_opts = ["Permutation (nPr)", "Combination (nCr)"]
        kind_idx = kind_opts.index(default_kind) if default_kind in kind_opts else 0
        kind = c1.selectbox("Type", kind_opts, index=kind_idx)
        default_n = parsed_params.get("n", 5) if chosen == detected else 5
        default_r = parsed_params.get("r", 2) if chosen == detected else 2
        n = c2.number_input("n", value=int(default_n), step=1, min_value=0)
        r = c3.number_input("r", value=int(default_r), step=1, min_value=0)
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            steps, answer, extra = solve_permcomb(kind, n, r)

    elif chosen == "functions":
        st.caption("Define a finite function by its mapping to classify it.")
        c1, c2 = st.columns(2)
        domain_str = c1.text_input("Domain elements (comma-separated)", "1,2,3")
        codomain_str = c2.text_input("Codomain elements (comma-separated)", "a,b,c,d")
        domain = [x.strip() for x in domain_str.split(",") if x.strip()]
        codomain = [x.strip() for x in codomain_str.split(",") if x.strip()]
        st.write("Map each domain element to a codomain element:")
        mapping = {}
        mcols = st.columns(min(len(domain), 4) or 1)
        for i, d in enumerate(domain):
            with mcols[i % len(mcols)]:
                mapping[d] = st.selectbox(f"f({d}) =", codomain, key=f"map_{d}")
        if st.button("Classify function", type="primary") or (auto_trigger and len(domain) > 0):
            steps, answer, extra = solve_functions(domain, codomain, mapping)

    elif chosen == "limits":
        c1, c2, c3 = st.columns(3)
        default_expr = parsed_params.get("expr_str", "sin(3*x)/x") if chosen == detected else "sin(3*x)/x"
        default_var = parsed_params.get("var_str", "x") if chosen == detected else "x"
        default_point = parsed_params.get("point_str", "0") if chosen == detected else "0"
        expr_str = c1.text_input("f(x) =", str(default_expr))
        var_str = c2.text_input("Variable", str(default_var))
        point_str = c3.text_input("x →", str(default_point))
        if st.button("Solve step-by-step", type="primary") or auto_trigger:
            try:
                steps, answer, extra = solve_limit(expr_str, var_str, point_str)
            except Exception as e:
                st.error(f"Couldn't parse that expression: {e}")

    # ---- render result ----
    if steps:
        st.markdown("### Step-by-step solution")
        render_steps(steps)
        st.markdown(f'<div class="result-box">✅ Final answer: {answer}</div>', unsafe_allow_html=True)
        
        last_solved_key = f"{question_text}_{chosen}_{answer}"
        if st.session_state.get("last_solved_key") != last_solved_key:
            st.session_state.last_solved_key = last_solved_key
            st.session_state.streak += 1
            push_history(question_text or f"{TOPICS[chosen]} problem", TOPICS[chosen], answer)

        # visualization
        st.markdown("### Interactive Visualization")
        if chosen == "complex":
            fig = plot_complex_plane([(extra["a"], extra["b"])], ["z"])
            st.pyplot(fig)
        elif chosen == "demoivre":
            if "roots" in extra:
                pts = [(re_, im_) for re_, im_, _ in extra["roots"]]
                labs = [f"w{k}" for k in range(len(pts))]
                st.pyplot(plot_complex_plane(pts, labs, draw_polygon=True))
            else:
                st.pyplot(plot_complex_plane([(extra["real"], extra["imag"])], ["zⁿ"], colors=[AMBER]))
        elif chosen == "functions":
            st.pyplot(plot_function_diagram(
                [x.strip() for x in domain_str.split(",") if x.strip()],
                [x.strip() for x in codomain_str.split(",") if x.strip()],
                mapping))
        elif chosen == "limits":
            st.pyplot(plot_limit_function(extra["expr"], extra["var"], extra["point"]))
            if extra.get("continuity_note"):
                st.info(extra["continuity_note"])

        # ---- export / actions ----
        st.markdown("### Save / Export")
        e1, e2, e3, e4 = st.columns(4)
        with e1:
            st.button("📋 Copy answer", on_click=lambda: None, help="Answer shown above — select & copy.")
        with e2:
            if DOCX_AVAILABLE:
                buf = build_docx(question_text or TOPICS[chosen], TOPICS[chosen], steps, answer)
                st.download_button("⬇️ DOCX", buf, file_name="mathmate_solution.docx")
            else:
                st.caption("Add `python-docx` to enable DOCX export.")
        with e3:
            if REPORTLAB_AVAILABLE:
                buf = build_pdf(question_text or TOPICS[chosen], TOPICS[chosen], steps, answer)
                st.download_button("⬇️ PDF", buf, file_name="mathmate_solution.pdf")
            else:
                st.caption("Add `reportlab` to enable PDF export.")
        with e4:
            st.button("🔗 Share link", help="Wire this up to your own link-sharing/backend.")


# ============================================================
# PAGE: FORMULA REFERENCE
# ============================================================
elif page == "📐 Formula Reference":
    st.markdown('<div class="hero-title">📐 Formula Reference</div>', unsafe_allow_html=True)
    st.caption("Essential mathematical formulas, definitions, and identities for all 6 syllabus topics.")
    
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "🧮 GCD", "📍 Complex", "🔄 De Moivre", "🔢 Perm & Comb", "🔗 Functions", "📈 Limits"
    ])
    
    with t1:
        st.markdown("### Euclidean Algorithm & GCD")
        st.latex(r"a = q \cdot b + r \quad (0 \le r < b)")
        st.latex(r"\gcd(a, b) = \gcd(b, r)")
        st.markdown("""
        - **Bézout's Identity**: For any non-zero integers $a$ and $b$, there exist integers $x$ and $y$ such that $a x + b y = \gcd(a, b)$.
        - **Properties**: $\gcd(a, 0) = |a|$, $\gcd(a, b) = \gcd(|a|, |b|)$.
        """)
        
    with t2:
        st.markdown("### Complex Numbers & Polar Form")
        st.latex(r"z = x + i y = r(\cos\theta + i\sin\theta) = r e^{i\theta}")
        st.latex(r"r = |z| = \sqrt{x^2 + y^2}, \quad \theta = \operatorname{atan2}(y, x)")
        st.markdown("""
        - **Euler's Formula**: $e^{i\theta} = \cos\theta + i\sin\theta$.
        - **Conjugate**: $\bar{z} = x - iy$, with $z \bar{z} = |z|^2$.
        """)

    with t3:
        st.markdown("### De Moivre's Theorem & n-th Roots")
        st.latex(r"[r(\cos\theta + i\sin\theta)]^n = r^n (\cos(n\theta) + i\sin(n\theta))")
        st.latex(r"w_k = r^{1/n} \left(\cos\frac{\theta + 2\pi k}{n} + i\sin\frac{\theta + 2\pi k}{n}\right), \quad k = 0, 1, \dots, n-1")
        st.markdown("""
        - **Roots of Unity**: The $n$-th roots of $1$ form a regular $n$-sided polygon centered at the origin on the complex Argand plane.
        """)

    with t4:
        st.markdown("### Permutations & Combinations")
        st.latex(r"nPr = \frac{n!}{(n-r)!}, \quad nCr = \binom{n}{r} = \frac{n!}{r!(n-r)!}")
        st.markdown("""
        - **Pascal's Identity**: $\binom{n}{r} = \binom{n-1}{r-1} + \binom{n-1}{r}$.
        - **Symmetry**: $\binom{n}{r} = \binom{n}{n-r}$.
        """)

    with t5:
        st.markdown("### Functions (Injective, Surjective & Bijective)")
        st.markdown("""
        - **Injective (One-to-One)**: $f(a) = f(b) \implies a = b$. No two distinct domain elements map to the same image.
        - **Surjective (Onto)**: Every element in the codomain has at least one pre-image in the domain ($\operatorname{range}(f) = \text{codomain}$).
        - **Bijective**: Both injective and surjective (invertible function).
        """)

    with t6:
        st.markdown("### Limits & Continuity")
        st.latex(r"\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)} \quad \text{(L'Hôpital's Rule for } \frac{0}{0}, \frac{\infty}{\infty} \text{)}")
        st.latex(r"\lim_{x \to 0} \frac{\sin x}{x} = 1, \quad \lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e")
        st.markdown("""
        - **Continuity Condition**: $f(x)$ is continuous at $x = a$ if $\lim_{x \to a} f(x) = f(a)$.
        """)


# ============================================================
# PAGE: PRACTICE & QUIZ
# ============================================================
elif page == "🎯 Practice & Quiz":
    st.markdown('<div class="hero-title">🎯 Practice & Quiz Lab</div>', unsafe_allow_html=True)
    st.caption("Test your problem-solving skills across syllabus topics.")

    QUESTION_BANK = [
        {"q": "Find gcd(48, 18) using the Euclidean algorithm.", "topic": "gcd",
         "options": ["6", "8", "12", "3"], "answer": "6",
         "exp": "48 = 2×18 + 12\n18 = 1×12 + 6\n12 = 2×6 + 0. Last non-zero remainder is 6."},
        {"q": "Convert z = √3 + i to polar form. What is the argument θ?", "topic": "complex",
         "options": ["30°", "45°", "60°", "90°"], "answer": "30°",
         "exp": "tan(θ) = 1/√3 → θ = 30° (or π/6 radians)."},
        {"q": "If z = 2(cos30° + i sin30°), what is |z³|?", "topic": "demoivre",
         "options": ["6", "8", "4", "2"], "answer": "8",
         "exp": "|z³| = |z|³ = 2³ = 8."},
        {"q": "How many ways can 4 distinct books be arranged on a shelf?", "topic": "permcomb",
         "options": ["24", "12", "16", "10"], "answer": "24",
         "exp": "Arranging 4 items = 4! = 4 × 3 × 2 × 1 = 24."},
        {"q": "A function f: {1,2,3} → {a,b} where f(1)=a, f(2)=a, f(3)=b — is it injective?", "topic": "functions",
         "options": ["No", "Yes"], "answer": "No",
         "exp": "f(1) = f(2) = a. Two distinct inputs map to the same output, so it is NOT injective."},
        {"q": "lim(x→0) sin(x)/x = ?", "topic": "limits",
         "options": ["1", "0", "∞", "undefined"], "answer": "1",
         "exp": "Standard limit: lim_(x→0) sin(x)/x = 1 (by L'Hôpital's Rule: cos(0)/1 = 1)."},
    ]

    if "quiz_q" not in st.session_state:
        st.session_state.quiz_q = random.choice(QUESTION_BANK)

    q = st.session_state.quiz_q
    st.markdown(f'<span class="topic-badge">{TOPICS[q["topic"]]}</span>', unsafe_allow_html=True)
    st.markdown(f"#### {q['q']}")
    choice = st.radio("Choose an answer", q["options"], key="quiz_choice")

    c1, c2 = st.columns(2)
    if c1.button("Submit answer"):
        st.session_state.quiz_score["total"] += 1
        if choice == q["answer"]:
            st.session_state.quiz_score["correct"] += 1
            st.success("Correct! 🎉")
        else:
            st.error(f"Not quite — the correct answer is {q['answer']}.")
        with st.expander("💡 View step-by-step solution breakdown", expanded=True):
            st.write(q["exp"])

    if c2.button("Next question"):
        st.session_state.quiz_q = random.choice(QUESTION_BANK)
        st.rerun()

    st.markdown("---")
    total = st.session_state.quiz_score["total"]
    correct = st.session_state.quiz_score["correct"]
    st.metric("Score", f"{correct} / {total}" if total else "0 / 0")


# ============================================================
# PAGE: HISTORY
# ============================================================
elif page == "🕘 History":
    st.markdown('<div class="hero-title">🕘 Solution History</div>', unsafe_allow_html=True)
    history = st.session_state.get("history", [])
    if not history:
        st.info("No solved questions yet — head to **Solve** to get started.")
    else:
        for item in history:
            with st.expander(f"{item['topic']} · {item['time']}"):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['answer']}")
