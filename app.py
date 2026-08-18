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

# Optional OCR — degrade gracefully if not installed / no tesseract binary on host
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

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
.stApp {{ background-color: {INK}; }}
h1, h2, h3, h4, p, span, label, .stMarkdown {{ color: {PAPER}; }}
.step-box {{
    background: rgba(247,245,239,0.06); border: 1px solid rgba(247,245,239,0.15);
    border-left: 4px solid {TEAL}; border-radius: 8px; padding: 14px 18px; margin: 10px 0;
}}
.step-title {{ color: {TEAL}; font-weight: 700; font-size: 0.85rem; letter-spacing: .03em;
    text-transform: uppercase; margin-bottom: 4px; }}
.result-box {{
    background: rgba(46,196,182,0.12); border: 1px solid {TEAL}; border-radius: 10px;
    padding: 16px 20px; font-size: 1.15rem; font-weight: 600; color: {TEAL};
}}
.topic-badge {{
    display: inline-block; background: rgba(255,182,39,0.15); color: {AMBER};
    border: 1px solid rgba(255,182,39,0.4); border-radius: 999px; padding: 4px 14px;
    font-size: 0.8rem; font-weight: 700; letter-spacing: .04em;
}}
[data-testid="stSidebar"] {{ background-color: #0D1730; }}

/* ---- Home page topic cards ---- */
[data-testid="stVerticalBlockBorderWrapper"]:has(.card-marker) {{
    border-radius: 16px !important;
    border: 1px solid rgba(247,245,239,0.14) !important;
    background: linear-gradient(180deg, rgba(247,245,239,0.05), rgba(247,245,239,0.02));
    padding: 6px 4px 2px 4px;
    transition: border-color .15s ease, transform .15s ease, background .15s ease;
}}
[data-testid="stVerticalBlockBorderWrapper"]:has(.card-marker):hover {{
    border-color: rgba(46,196,182,0.55) !important;
    background: linear-gradient(180deg, rgba(46,196,182,0.08), rgba(247,245,239,0.02));
    transform: translateY(-2px);
}}
.card-icon {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 42px; height: 42px; border-radius: 10px;
    background: rgba(46,196,182,0.15); font-size: 22px; margin-bottom: 10px;
}}
.card-title {{
    font-weight: 700; font-size: 1.02rem; color: {PAPER}; margin: 4px 0 6px 0;
    line-height: 1.3;
}}
.card-blurb {{
    color: rgba(247,245,239,0.65); font-size: 0.85rem; line-height: 1.4;
    min-height: 40px; margin-bottom: 12px;
}}
div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button {{
    border-radius: 8px; font-weight: 600; font-size: 0.85rem;
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

# icon / title / blurb split out for the Home page card grid
TOPIC_META = {
    "gcd":       {"icon": "🧮", "title": "Euclidean Algorithm & GCD",
                  "blurb": "Find the HCF of two numbers via repeated division."},
    "complex":   {"icon": "📍", "title": "Complex Numbers & Polar Form",
                  "blurb": "Convert between rectangular and polar form."},
    "demoivre":  {"icon": "🔄", "title": "De Moivre's Theorem",
                  "blurb": "Powers and n-th roots of complex numbers."},
    "permcomb":  {"icon": "🔢", "title": "Permutations & Combinations",
                  "blurb": "Count arrangements and selections."},
    "functions": {"icon": "🔗", "title": "Injective, Surjective & Bijective",
                  "blurb": "Classify a mapping between finite sets."},
    "limits":    {"icon": "📈", "title": "Limits & Continuity",
                  "blurb": "Evaluate limits and test continuity at a point."},
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


# ============================================================
# SOLVERS — each returns (steps: list[(title, body)], final_answer: str, extra: dict)
# ============================================================

def solve_gcd(a: int, b: int):
    steps = []
    a, b = abs(int(a)), abs(int(b))
    x, y = a, b
    if y == 0:
        return [("Edge case", f"gcd({x}, 0) = {x} — by definition, gcd(n, 0) = n.")], str(x), {}

    steps.append(("The principle", "The Euclidean Algorithm relies on the fact that "
                  "gcd(x, y) = gcd(y, x mod y). We repeatedly replace the larger number "
                  "with the remainder of dividing it by the smaller number, until the "
                  "remainder becomes 0."))
    steps.append(("Set up", f"We need gcd({x}, {y}). Since {x} > {y}, divide {x} by {y}."))

    divisions = []
    round_no = 1
    while y != 0:
        q = x // y
        r = x % y
        steps.append((f"Step {round_no}: Divide",
                      f"{x} ÷ {y} = {q} remainder {r}\n"
                      f"→ {x} = {q} × {y} + {r}"))
        divisions.append((x, y, q, r))
        if r == 0:
            steps.append((f"Step {round_no}: Remainder check",
                          f"Remainder is {r} — we stop here. The divisor at this step, {y}, "
                          f"is the GCD."))
        else:
            steps.append((f"Step {round_no}: Continue",
                          f"Remainder {r} ≠ 0, so repeat the process with gcd({y}, {r})."))
        x, y = y, r
        round_no += 1

    gcd_val = x
    steps.append(("Verify", f"Check: {a} ÷ {gcd_val} = {a // gcd_val} (no remainder), "
                  f"{b} ÷ {gcd_val} = {b // gcd_val} (no remainder) — confirms {gcd_val} "
                  f"divides both numbers exactly."))
    return steps, str(gcd_val), {"pairs": (a, b), "divisions": divisions}


def solve_complex_to_polar(a: float, b: float):
    steps = []
    steps.append(("Identify the form", f"z = {a} + {b}i is in rectangular (x + yi) form, "
                  f"where x = {a} (real part) and y = {b} (imaginary part)."))

    steps.append(("Modulus formula", "The modulus (distance from origin) is given by "
                  "r = √(x² + y²) — this comes directly from the Pythagorean theorem, "
                  "treating (x, y) as a point in the Argand plane."))
    x_sq, y_sq = a**2, b**2
    steps.append(("Square each part", f"x² = ({a})² = {x_sq:g}\ny² = ({b})² = {y_sq:g}"))
    sum_sq = x_sq + y_sq
    steps.append(("Sum the squares", f"x² + y² = {x_sq:g} + {y_sq:g} = {sum_sq:g}"))
    r = math.sqrt(sum_sq)
    steps.append(("Take the square root", f"r = √{sum_sq:g} = {r:.4f}"))

    quadrant = "1st (x>0, y>0)" if a > 0 and b >= 0 else \
               "2nd (x<0, y>0)" if a < 0 and b >= 0 else \
               "3rd (x<0, y<0)" if a < 0 and b < 0 else "4th (x>0, y<0)"
    steps.append(("Locate the quadrant", f"With x = {a} and y = {b}, the point lies in the "
                  f"{quadrant} quadrant — this tells us which range θ should fall in before "
                  f"we trust the calculator's inverse-tan output."))

    ref_angle = math.degrees(math.atan2(abs(b), abs(a))) if a != 0 else 90.0
    steps.append(("Argument formula", "The argument (angle from positive real axis) is "
                  "θ = tan⁻¹(y/x), adjusted for the correct quadrant."))
    theta = math.atan2(b, a)
    theta_deg = math.degrees(theta)
    steps.append(("Compute the reference angle", f"Reference angle = tan⁻¹(|y|/|x|) = "
                  f"tan⁻¹({abs(b):.4f}/{abs(a):.4f}) ≈ {ref_angle:.2f}°"))
    steps.append(("Adjust for quadrant", f"Adjusting the reference angle for the "
                  f"{quadrant.split(' ')[0]} quadrant gives θ ≈ {theta_deg:.2f}° "
                  f"({theta:.4f} radians)."))

    steps.append(("Write in polar form", f"z = r(cosθ + i sinθ) = "
                  f"{r:.4f}(cos {theta_deg:.2f}° + i·sin {theta_deg:.2f}°)"))

    check_a = r * math.cos(theta)
    check_b = r * math.sin(theta)
    steps.append(("Verify", f"Convert back: r·cosθ = {r:.4f}×cos({theta_deg:.2f}°) ≈ {check_a:.4f} ✓ "
                  f"(matches x = {a})\nr·sinθ = {r:.4f}×sin({theta_deg:.2f}°) ≈ {check_b:.4f} ✓ "
                  f"(matches y = {b})"))

    answer = f"z = {r:.4f} · (cos {theta_deg:.2f}° + i sin {theta_deg:.2f}°)"
    return steps, answer, {"r": r, "theta": theta, "a": a, "b": b}


def solve_demoivre(a: float, b: float, n: int):
    steps = []
    steps.append(("Goal", f"Compute z^{n} where z = {a} + {b}i. Raising a complex number to "
                  "a power directly in rectangular form means expanding a binomial many times — "
                  "converting to polar form first makes this far simpler."))

    # --- polar conversion sub-steps ---
    r = math.sqrt(a**2 + b**2)
    steps.append(("Find the modulus", f"r = √(x² + y²) = √({a}² + {b}²) = √{a**2+b**2:g} = {r:.4f}"))
    theta = math.atan2(b, a)
    theta_deg = math.degrees(theta)
    quadrant = "1st" if a > 0 and b >= 0 else "2nd" if a < 0 and b >= 0 else "3rd" if a < 0 and b < 0 else "4th"
    steps.append(("Find the argument", f"θ = tan⁻¹(y/x), adjusted for the {quadrant} quadrant "
                  f"→ θ ≈ {theta_deg:.2f}° ({theta:.4f} rad)"))
    steps.append(("Polar form", f"z = {r:.4f}(cos {theta_deg:.2f}° + i sin {theta_deg:.2f}°)"))

    steps.append(("State De Moivre's theorem", "For any integer n: "
                  "[r(cosθ + i sinθ)]ⁿ = rⁿ(cos(nθ) + i sin(nθ)). "
                  "The modulus gets raised to the power n, and the argument gets multiplied by n."))

    r_n = r ** n
    steps.append(("Raise the modulus", f"rⁿ = ({r:.4f})^{n} = {r_n:.4f}"))

    theta_n_raw = theta_deg * n
    theta_n = theta * n
    theta_n_deg = theta_n_raw % 360
    if theta_n_raw != theta_n_deg:
        steps.append(("Multiply the argument", f"nθ = {n} × {theta_deg:.2f}° = {theta_n_raw:.2f}°"))
        steps.append(("Reduce to [0°, 360°)", f"{theta_n_raw:.2f}° mod 360° = {theta_n_deg:.2f}° "
                      "— angles are periodic, so this is equivalent."))
    else:
        steps.append(("Multiply the argument", f"nθ = {n} × {theta_deg:.2f}° = {theta_n_deg:.2f}°"))

    steps.append(("Result in polar form", f"z^{n} = {r_n:.4f}(cos {theta_n_deg:.2f}° + i sin {theta_n_deg:.2f}°)"))

    cos_val = math.cos(theta_n)
    sin_val = math.sin(theta_n)
    steps.append(("Evaluate cos and sin", f"cos({theta_n_deg:.2f}°) ≈ {cos_val:.4f}\n"
                  f"sin({theta_n_deg:.2f}°) ≈ {sin_val:.4f}"))

    real_part = r_n * cos_val
    imag_part = r_n * sin_val
    steps.append(("Multiply through by rⁿ", f"Real part = {r_n:.4f} × {cos_val:.4f} = {real_part:.4f}\n"
                  f"Imaginary part = {r_n:.4f} × {sin_val:.4f} = {imag_part:.4f}"))

    steps.append(("Convert back to rectangular", f"z^{n} = {real_part:.4f} + {imag_part:.4f}i"))
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
        return [("Invalid input", "r cannot be greater than n — you can't choose or arrange "
                 "more items than are available.")], "Undefined", {}

    if kind == "Permutation (nPr)":
        steps.append(("What this counts", f"nPr counts the number of ways to arrange {r} items "
                      f"out of {n} distinct items, where ORDER MATTERS."))
        steps.append(("Formula", "nPr = n! / (n − r)!"))
        steps.append(("Substitute values", f"{n}P{r} = {n}! / ({n} − {r})! = {n}! / {n-r}!"))
        steps.append(("Expand n!", f"{n}! = " + " × ".join(str(i) for i in range(n, 0, -1))))
        steps.append(("Expand (n−r)!", f"{n-r}! = " + (" × ".join(str(i) for i in range(n-r, 0, -1)) if n-r > 0 else "1  (0! = 1 by definition)")))
        steps.append(("Cancel the common factorial tail",
                      f"{n}! / {n-r}! leaves only the top {r} descending terms, since everything "
                      f"from {n-r}! downward cancels:\n"
                      f"{n}P{r} = {' × '.join(str(i) for i in range(n, n-r, -1)) if r > 0 else '1'}"))
        val = math.perm(n, r)
        steps.append(("Multiply out", f"{' × '.join(str(i) for i in range(n, n-r, -1)) if r > 0 else '1'} = {val}"))
        answer = str(val)
    else:
        steps.append(("What this counts", f"nCr counts the number of ways to choose {r} items "
                      f"out of {n} distinct items, where ORDER DOES NOT MATTER."))
        steps.append(("Formula", "nCr = n! / (r! × (n − r)!)"))
        steps.append(("Substitute values", f"{n}C{r} = {n}! / ({r}! × ({n}−{r})!) = {n}! / ({r}! × {n-r}!)"))
        steps.append(("Expand n!", f"{n}! = " + " × ".join(str(i) for i in range(n, 0, -1))))
        steps.append(("Cancel with (n−r)!", f"Dividing {n}! by {n-r}! leaves the top {r} terms: "
                      f"{' × '.join(str(i) for i in range(n, n-r, -1)) if r > 0 else '1'}"))
        steps.append(("Expand r!", f"{r}! = " + (" × ".join(str(i) for i in range(r, 0, -1)) if r > 0 else "1  (0! = 1 by definition)")))
        numerator = math.perm(n, r)
        denom = math.factorial(r)
        steps.append(("Divide by r! to remove ordering",
                      f"Since nPr counts ordered arrangements and each group of {r} items can be "
                      f"ordered in {r}! ways, divide by {r}! to get unordered selections:\n"
                      f"{n}C{r} = {numerator} / {denom}"))
        val = math.comb(n, r)
        steps.append(("Simplify", f"{numerator} / {denom} = {val}"))
        answer = str(val)
    return steps, answer, {}


def solve_functions(domain: list, codomain: list, mapping: dict):
    """mapping: dict domain_element -> codomain_element"""
    steps = []
    steps.append(("Set up", f"Domain A = {domain}\nCodomain B = {codomain}\n"
                  f"Mapping f: A → B is given by f = {mapping}"))
    steps.append(("List the images explicitly",
                  "\n".join(f"f({d}) = {c}" for d, c in mapping.items())))

    # --- injectivity, pair by pair ---
    steps.append(("Injectivity definition", "f is injective (one-one) if f(x₁) = f(x₂) "
                  "implies x₁ = x₂ — i.e. distinct inputs always give distinct outputs. "
                  "We check this by comparing every pair of domain elements."))
    images = list(mapping.items())
    collisions = []
    checked_pairs = 0
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            d1, c1 = images[i]
            d2, c2 = images[j]
            checked_pairs += 1
            if c1 == c2:
                collisions.append((d1, d2, c1))
                steps.append((f"Compare f({d1}) and f({d2})",
                              f"f({d1}) = {c1}, f({d2}) = {c2} → EQUAL, but {d1} ≠ {d2} "
                              "→ this breaks injectivity."))
    is_injective = len(collisions) == 0
    if is_injective:
        steps.append(("Injectivity result", f"Checked all {checked_pairs} pair(s) of domain "
                      "elements — no two share an image. f is INJECTIVE."))
    else:
        steps.append(("Injectivity result", f"Found {len(collisions)} colliding pair(s) — "
                      "f is NOT injective."))

    # --- surjectivity, element by element ---
    steps.append(("Surjectivity definition", "f is surjective (onto) if every element of the "
                  "codomain has at least one pre-image in the domain — i.e. the range equals "
                  "the whole codomain B."))
    image_set = set(mapping.values())
    for c in codomain:
        preimages = [d for d, v in mapping.items() if v == c]
        if preimages:
            steps.append((f"Check codomain element {c}",
                          f"Pre-image(s): {preimages} → covered ✓"))
        else:
            steps.append((f"Check codomain element {c}",
                          f"No domain element maps to {c} → NOT covered ✗"))
    is_surjective = set(codomain) == image_set
    unmapped = set(codomain) - image_set
    if is_surjective:
        steps.append(("Surjectivity result", "Every codomain element has a pre-image. "
                      "f is SURJECTIVE."))
    else:
        steps.append(("Surjectivity result", f"Codomain element(s) {sorted(unmapped)} have no "
                      "pre-image — f is NOT surjective."))

    is_bijective = is_injective and is_surjective
    steps.append(("Bijectivity definition", "f is bijective if and only if it is BOTH "
                  "injective AND surjective."))
    steps.append(("Conclusion", f"Injective: {'Yes' if is_injective else 'No'}. "
                  f"Surjective: {'Yes' if is_surjective else 'No'}. "
                  f"→ {'Bijective' if is_bijective else 'Not bijective'}."))

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

    steps.append(("Original expression", f"Evaluate lim_{{{var_str}→{point_str}}} {expr}"))
    steps.append(("Strategy", "Always try direct substitution first. If it gives a finite, "
                  "well-defined value, that's the limit. If it produces an indeterminate form "
                  "like 0/0 or ∞/∞, we need to simplify algebraically (factor/cancel, "
                  "rationalize, or use a known standard limit) before substituting again."))

    # try direct substitution first
    is_indeterminate = False
    try:
        direct = expr.subs(x, point)
        direct_simplified = sp.simplify(direct)
        if direct_simplified.is_finite and not direct_simplified.has(sp.zoo, sp.nan):
            steps.append(("Try direct substitution",
                          f"Substitute {var_str} = {point_str} directly:\n"
                          f"f({point_str}) = {direct} = {direct_simplified}"))
            steps.append(("Check the result", f"This is a finite, defined number → "
                          "no further work needed."))
            result = direct_simplified
        else:
            raise ValueError("indeterminate")
    except Exception:
        is_indeterminate = True
        try:
            direct_form = expr.subs(x, point)
        except Exception:
            direct_form = "undefined"
        steps.append(("Try direct substitution",
                      f"Substitute {var_str} = {point_str}: f({point_str}) → {direct_form} "
                      "(an indeterminate or undefined form)."))
        steps.append(("Identify the indeterminate form",
                      "This is a classic 0/0 (or ∞/∞) indeterminate form — direct substitution "
                      "doesn't work here, so we simplify the expression algebraically first."))

        simplified = sp.simplify(expr)
        factored = sp.factor(expr) if expr.is_rational_function() else None
        if simplified != expr:
            steps.append(("Simplify algebraically",
                          f"Simplify the expression:\n{expr}  →  {simplified}\n"
                          "(common factors between numerator and denominator cancel, or a "
                          "known identity applies)."))
        elif factored is not None and factored != expr:
            steps.append(("Factor the expression", f"{expr}  →  {factored}"))
            simplified = factored

        steps.append(("Re-substitute after simplifying",
                      f"Now substitute {var_str} = {point_str} into the simplified form."))

        result = limit(expr, x, point)
        steps.append(("Evaluate", f"lim_{{{var_str}→{point_str}}} {expr} = {result}"))

    # continuity check at the point (only for finite points) — full 3-part definition
    continuity_note = None
    if point not in (oo, -oo):
        steps.append(("Continuity check — 3-part definition",
                      "f is continuous at a point c if: (1) f(c) is defined, "
                      "(2) lim_{x→c} f(x) exists, and (3) lim_{x→c} f(x) = f(c). "
                      "All three must hold."))
        try:
            f_val = expr.subs(x, point)
            f_defined = f_val.is_finite and not f_val.has(sp.zoo, sp.nan)
            steps.append((f"(1) Is f({point_str}) defined?",
                          f"f({point_str}) = {f_val}" + (" — defined ✓" if f_defined else " — undefined ✗")))
            limit_exists = result.is_finite if hasattr(result, "is_finite") else True
            steps.append((f"(2) Does the limit exist?",
                          f"lim = {result}" + (" — exists ✓" if limit_exists else " — does not exist ✗")))
            values_match = f_defined and sp.simplify(f_val - result) == 0
            steps.append((f"(3) Does lim = f({point_str})?",
                          (f"{result} = {f_val} ✓" if values_match else f"{result} ≠ {f_val} (or f undefined) ✗")))
            if f_defined and limit_exists and values_match:
                continuity_note = f"f({var_str}) is continuous at {var_str} = {point_str}: all three conditions hold."
            else:
                continuity_note = f"f({var_str}) is NOT continuous at {var_str} = {point_str}: at least one condition fails (this may be a removable discontinuity)."
        except Exception:
            continuity_note = None

    steps.append(("Final result", f"lim_{{{var_str}→{point_str}}} {expr} = {result}"))
    answer = str(result)
    return steps, answer, {"continuity_note": continuity_note, "expr": expr, "var": x, "point": point}


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_complex_plane(points: list, labels: list, colors: list = None):
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor(INK)
    ax.set_facecolor(INK)
    colors = colors or [TEAL, AMBER, CORAL, "#9B5DE5"]
    max_r = max([abs(complex(*p)) for p in points] + [1]) * 1.3
    ax.axhline(0, color=PAPER, alpha=0.3, linewidth=1)
    ax.axvline(0, color=PAPER, alpha=0.3, linewidth=1)
    for i, (p, lab) in enumerate(zip(points, labels)):
        c = colors[i % len(colors)]
        ax.plot([0, p[0]], [0, p[1]], color=c, linewidth=1.5)
        ax.scatter([p[0]], [p[1]], color=c, s=40, zorder=5)
        ax.annotate(lab, (p[0], p[1]), textcoords="offset points", xytext=(6, 6), color=c, fontsize=10)
    ax.set_xlim(-max_r, max_r)
    ax.set_ylim(-max_r, max_r)
    ax.set_xlabel("Re", color=PAPER)
    ax.set_ylabel("Im", color=PAPER)
    ax.tick_params(colors=PAPER)
    for spine in ax.spines.values():
        spine.set_color(GRAPHITE)
    ax.set_aspect("equal")
    return fig


def plot_function_diagram(domain, codomain, mapping):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    fig.patch.set_facecolor(INK)
    ax.set_facecolor(INK)
    ax.axis("off")
    y_dom = np.linspace(0.85, 0.15, len(domain)) if len(domain) > 1 else [0.5]
    y_cod = np.linspace(0.85, 0.15, len(codomain)) if len(codomain) > 1 else [0.5]
    dom_pos = {d: (0.15, y) for d, y in zip(domain, y_dom)}
    cod_pos = {c: (0.75, y) for c, y in zip(codomain, y_cod)}
    for d, (x, y) in dom_pos.items():
        ax.scatter([x], [y], color=TEAL, s=200, zorder=5)
        ax.annotate(str(d), (x, y), color=INK, ha="center", va="center", fontweight="bold", fontsize=9)
    for c, (x, y) in cod_pos.items():
        ax.scatter([x], [y], color=AMBER, s=200, zorder=5)
        ax.annotate(str(c), (x, y), color=INK, ha="center", va="center", fontweight="bold", fontsize=9)
    for d, c in mapping.items():
        x1, y1 = dom_pos[d]
        x2, y2 = cod_pos[c]
        ax.annotate("", xy=(x2 - 0.04, y2), xytext=(x1 + 0.04, y1),
                    arrowprops=dict(arrowstyle="->", color=PAPER, alpha=0.6))
    ax.text(0.15, 0.98, "Domain", color=PAPER, ha="center", fontsize=10)
    ax.text(0.75, 0.98, "Codomain", color=PAPER, ha="center", fontsize=10)
    return fig


def plot_limit_function(expr, var, point):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    fig.patch.set_facecolor(INK)
    ax.set_facecolor(INK)
    try:
        pt = float(point) if point not in (oo, -oo) else 0
        xs = np.linspace(pt - 5, pt + 5, 400)
        f = sp.lambdify(var, expr, "numpy")
        with np.errstate(all="ignore"):
            ys = f(xs)
        ax.plot(xs, ys, color=TEAL, linewidth=2)
        ax.axvline(pt, color=AMBER, linestyle="--", alpha=0.7, label=f"{var} = {point}")
        ax.legend(facecolor=INK, labelcolor=PAPER, edgecolor=GRAPHITE)
    except Exception:
        ax.text(0.5, 0.5, "Graph unavailable for this expression", color=PAPER, ha="center", va="center")
    ax.set_facecolor(INK)
    ax.tick_params(colors=PAPER)
    for spine in ax.spines.values():
        spine.set_color(GRAPHITE)
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
# SHARED RESULT RENDERER (steps, viz, export) — used by every topic page
# ============================================================
def render_result(chosen_key, topic_label, question_text, steps, answer, extra,
                   viz_fig=None, continuity_note=None):
    if not steps:
        return
    st.markdown("### Step-by-step solution")
    render_steps(steps)
    st.markdown(f'<div class="result-box">✅ Final answer: {answer}</div>', unsafe_allow_html=True)
    st.session_state.streak += 1
    push_history(question_text or f"{topic_label} problem", topic_label, answer)

    if viz_fig is not None:
        st.markdown("### Visualization")
        st.pyplot(viz_fig)
    if continuity_note:
        st.info(continuity_note)

    st.markdown("### Save / Export")
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.button("📋 Copy answer", key=f"copy_{chosen_key}", help="Answer shown above — select & copy.")
    with e2:
        if DOCX_AVAILABLE:
            buf = build_docx(question_text or topic_label, topic_label, steps, answer)
            st.download_button("⬇️ DOCX", buf, file_name="mathmate_solution.docx", key=f"docx_{chosen_key}")
        else:
            st.caption("Add `python-docx` to enable DOCX export.")
    with e3:
        if REPORTLAB_AVAILABLE:
            buf = build_pdf(question_text or topic_label, topic_label, steps, answer)
            st.download_button("⬇️ PDF", buf, file_name="mathmate_solution.pdf", key=f"pdf_{chosen_key}")
        else:
            st.caption("Add `reportlab` to enable PDF export.")
    with e4:
        st.button("🔗 Share link", key=f"share_{chosen_key}", help="Wire this up to your own link-sharing/backend.")


def scan_input_block(key_prefix):
    """Reusable Type / Paste / Scan block that returns whatever text the user entered.
    Each topic page still uses its own structured number/text inputs to actually solve —
    this is only for capturing the original question wording (for history/export)."""
    mode = st.radio("Input method", ["Type", "Paste", "Scan (image upload)"],
                     horizontal=True, key=f"{key_prefix}_mode")
    text = ""
    if mode == "Scan (image upload)":
        img_file = st.file_uploader("Upload a photo of your question", type=["png", "jpg", "jpeg"], key=f"{key_prefix}_upl")
        cam_file = st.camera_input("...or capture with your camera", key=f"{key_prefix}_cam")
        source = img_file or cam_file
        if source:
            if OCR_AVAILABLE:
                image = Image.open(source)
                st.image(image, caption="Uploaded question", width=300)
                ocr_text = pytesseract.image_to_string(image)
                text = st.text_area("OCR result (edit if needed)", value=ocr_text, key=f"{key_prefix}_ocr")
            else:
                st.warning("OCR isn't available on this deployment (pytesseract/tesseract not installed). "
                           "Add `pytesseract` to requirements.txt and `tesseract-ocr` to packages.txt, "
                           "or type/paste the question below instead.")
                text = st.text_area("Type the question from your image", "", key=f"{key_prefix}_fallback")
    else:
        text = st.text_area("Question (optional — for your records/history)",
                             placeholder="Paste or type the original question here…",
                             height=80, key=f"{key_prefix}_text")
    return text


def back_to_home():
    if st.button("← All topics", key=f"back_{st.session_state.page}"):
        st.session_state.page = "home"
        st.rerun()


# ============================================================
# PER-TOPIC PAGES — each is its own dedicated landing, not a shared form
# ============================================================
def page_gcd():
    back_to_home()
    st.markdown('<span class="topic-badge">🧮 EUCLIDEAN ALGORITHM & GCD</span>', unsafe_allow_html=True)
    st.title(TOPICS["gcd"])
    st.write("Find the greatest common divisor of two integers using repeated division.")
    q_text = scan_input_block("gcd")
    st.markdown("---")
    c1, c2 = st.columns(2)
    a = c1.number_input("a", value=1071, step=1, key="gcd_a")
    b = c2.number_input("b", value=462, step=1, key="gcd_b")
    if st.button("Solve step-by-step", type="primary", key="gcd_solve"):
        steps, answer, extra = solve_gcd(a, b)
        render_result("gcd", TOPICS["gcd"], q_text or f"gcd({a}, {b})", steps, answer, extra)


def page_complex():
    back_to_home()
    st.markdown('<span class="topic-badge">📍 COMPLEX NUMBERS & POLAR FORM</span>', unsafe_allow_html=True)
    st.title(TOPICS["complex"])
    st.write("Convert a complex number from rectangular (a + bi) form to polar form.")
    q_text = scan_input_block("complex")
    st.markdown("---")
    c1, c2 = st.columns(2)
    a = c1.number_input("Real part (a)", value=1.0, key="cx_a")
    b = c2.number_input("Imaginary part (b)", value=1.7320508, key="cx_b")
    if st.button("Solve step-by-step", type="primary", key="cx_solve"):
        steps, answer, extra = solve_complex_to_polar(a, b)
        fig = plot_complex_plane([(extra["a"], extra["b"])], ["z"])
        render_result("complex", TOPICS["complex"], q_text or f"Convert {a}+{b}i to polar form",
                       steps, answer, extra, viz_fig=fig)


def page_demoivre():
    back_to_home()
    st.markdown('<span class="topic-badge">🔄 DE MOIVRE\'S THEOREM</span>', unsafe_allow_html=True)
    st.title(TOPICS["demoivre"])
    st.write("Raise a complex number to a power, or find all its n-th roots, using De Moivre's theorem.")
    q_text = scan_input_block("demoivre")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("Real part (a)", value=1.0, key="dm_a")
    b = c2.number_input("Imaginary part (b)", value=1.7320508, key="dm_b")
    n = c3.number_input("Power n", value=4, step=1, key="dm_n")
    show_roots = st.checkbox("Also show all n-th roots of z (instead of zⁿ)", key="dm_roots")
    if st.button("Solve step-by-step", type="primary", key="dm_solve"):
        if show_roots:
            roots, r_root = demoivre_roots(a, b, int(n))
            steps = [("Convert to polar", f"z = {a} + {b}i → r = {math.hypot(a,b):.4f}, θ = {math.degrees(math.atan2(b,a)):.2f}°")]
            steps.append(("Root formula", f"wₖ = r^(1/n) [cos((θ+2πk)/n) + i sin((θ+2πk)/n)],  k = 0,…,{int(n)-1}"))
            for k, (re_, im_, ang) in enumerate(roots):
                steps.append((f"Root k={k}", f"w{k} = {re_:.4f} + {im_:.4f}i  (angle {ang:.2f}°)"))
            answer = ", ".join(f"{re_:.3f}+{im_:.3f}i" for re_, im_, _ in roots)
            extra = {"roots": roots}
            pts = [(re_, im_) for re_, im_, _ in roots]
            labs = [f"w{k}" for k in range(len(pts))]
            fig = plot_complex_plane(pts, labs)
        else:
            steps, answer, extra = solve_demoivre(a, b, int(n))
            fig = plot_complex_plane([(extra["real"], extra["imag"])], ["zⁿ"], colors=[AMBER])
        render_result("demoivre", TOPICS["demoivre"], q_text or f"z={a}+{b}i, n={int(n)}",
                       steps, answer, extra, viz_fig=fig)


def page_permcomb():
    back_to_home()
    st.markdown('<span class="topic-badge">🔢 PERMUTATIONS & COMBINATIONS</span>', unsafe_allow_html=True)
    st.title(TOPICS["permcomb"])
    st.write("Count arrangements (order matters) or selections (order doesn't matter) from n items.")
    q_text = scan_input_block("pc")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    kind = c1.selectbox("Type", ["Permutation (nPr)", "Combination (nCr)"], key="pc_kind")
    n = c2.number_input("n", value=5, step=1, min_value=0, key="pc_n")
    r = c3.number_input("r", value=2, step=1, min_value=0, key="pc_r")
    if st.button("Solve step-by-step", type="primary", key="pc_solve"):
        steps, answer, extra = solve_permcomb(kind, n, r)
        render_result("permcomb", TOPICS["permcomb"], q_text or f"{kind}: n={n}, r={r}", steps, answer, extra)


def page_functions():
    back_to_home()
    st.markdown('<span class="topic-badge">🔗 INJECTIVE, SURJECTIVE & BIJECTIVE FUNCTIONS</span>', unsafe_allow_html=True)
    st.title(TOPICS["functions"])
    st.write("Define a finite function by its mapping and classify it.")
    q_text = scan_input_block("fn")
    st.markdown("---")
    c1, c2 = st.columns(2)
    domain_str = c1.text_input("Domain elements (comma-separated)", "1,2,3", key="fn_dom")
    codomain_str = c2.text_input("Codomain elements (comma-separated)", "a,b,c,d", key="fn_cod")
    domain = [x.strip() for x in domain_str.split(",") if x.strip()]
    codomain = [x.strip() for x in codomain_str.split(",") if x.strip()]
    st.write("Map each domain element to a codomain element:")
    mapping = {}
    mcols = st.columns(min(len(domain), 4) or 1)
    for i, d in enumerate(domain):
        with mcols[i % len(mcols)]:
            mapping[d] = st.selectbox(f"f({d}) =", codomain, key=f"fn_map_{d}")
    if st.button("Classify function", type="primary", key="fn_solve"):
        steps, answer, extra = solve_functions(domain, codomain, mapping)
        fig = plot_function_diagram(domain, codomain, mapping)
        render_result("functions", TOPICS["functions"], q_text or f"f: {domain} → {codomain}",
                       steps, answer, extra, viz_fig=fig)


def page_limits():
    back_to_home()
    st.markdown('<span class="topic-badge">📈 LIMITS & CONTINUITY</span>', unsafe_allow_html=True)
    st.title(TOPICS["limits"])
    st.write("Evaluate a limit symbolically and check continuity at the target point.")
    q_text = scan_input_block("lim")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    expr_str = c1.text_input("f(x) =", "sin(3*x)/x", key="lim_expr")
    var_str = c2.text_input("Variable", "x", key="lim_var")
    point_str = c3.text_input("x →", "0", key="lim_point")
    if st.button("Solve step-by-step", type="primary", key="lim_solve"):
        try:
            steps, answer, extra = solve_limit(expr_str, var_str, point_str)
            fig = plot_limit_function(extra["expr"], extra["var"], extra["point"])
            render_result("limits", TOPICS["limits"], q_text or f"lim({var_str}→{point_str}) {expr_str}",
                           steps, answer, extra, viz_fig=fig, continuity_note=extra.get("continuity_note"))
        except Exception as e:
            st.error(f"Couldn't parse that expression: {e}")


TOPIC_PAGES = {
    "gcd": page_gcd,
    "complex": page_complex,
    "demoivre": page_demoivre,
    "permcomb": page_permcomb,
    "functions": page_functions,
    "limits": page_limits,
}


# ============================================================
# SIDEBAR NAV — all navigation goes through st.session_state.page
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = {"correct": 0, "total": 0}

st.sidebar.markdown("## 🧮 MathMate")
st.sidebar.caption("Interactive Mathematics Lab")

if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()
if st.sidebar.button("🎯 Practice & Quiz", use_container_width=True):
    st.session_state.page = "practice"
    st.rerun()
if st.sidebar.button("🕘 History", use_container_width=True):
    st.session_state.page = "history"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.metric("🔥 Streak", st.session_state.streak)
if st.session_state.quiz_score["total"] > 0:
    pct = round(100 * st.session_state.quiz_score["correct"] / st.session_state.quiz_score["total"])
    st.sidebar.metric("🎯 Quiz accuracy", f"{pct}%")


# ============================================================
# PAGE: HOME — each topic is a real card with icon/blurb, routing to its own page
# ============================================================
if st.session_state.page == "home":
    st.title("🧮 MathMate")
    st.subheader("Scan → Detect Topic → Solve Step-by-Step → Understand → Save")
    st.write("Six syllabus topics, one lab. Pick a topic below — each opens its own dedicated page.")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, key in enumerate(TOPIC_META):
        meta = TOPIC_META[key]
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="card-icon">{meta['icon']}</div>
                    <div class="card-title">{meta['title']}</div>
                    <div class="card-blurb">{meta['blurb']}</div>
                """, unsafe_allow_html=True)
                if st.button("Open →", key=f"card_{key}", use_container_width=True, type="primary"):
                    st.session_state.page = key
                    st.rerun()


# ============================================================
# PAGE: individual topic pages
# ============================================================
elif st.session_state.page in TOPIC_PAGES:
    TOPIC_PAGES[st.session_state.page]()


# ============================================================
# PAGE: PRACTICE & QUIZ
# ============================================================
elif st.session_state.page == "practice":
    st.title("Practice & Quiz")
    QUESTION_BANK = [
        {"q": "Find gcd(48, 18) using the Euclidean algorithm.", "topic": "gcd",
         "options": ["6", "8", "12", "3"], "answer": "6"},
        {"q": "Convert z = √3 + i to polar form. What is the argument θ?", "topic": "complex",
         "options": ["30°", "45°", "60°", "90°"], "answer": "30°"},
        {"q": "If z = 2(cos30° + i sin30°), what is |z³|?", "topic": "demoivre",
         "options": ["6", "8", "4", "2"], "answer": "8"},
        {"q": "How many ways can 4 distinct books be arranged on a shelf?", "topic": "permcomb",
         "options": ["24", "12", "16", "10"], "answer": "24"},
        {"q": "A function f: {1,2,3} → {a,b} where f(1)=a, f(2)=a, f(3)=b — is it injective?", "topic": "functions",
         "options": ["No", "Yes"], "answer": "No"},
        {"q": "lim(x→0) sin(x)/x = ?", "topic": "limits",
         "options": ["1", "0", "∞", "undefined"], "answer": "1"},
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
elif st.session_state.page == "history":
    st.title("Solution history")
    history = st.session_state.get("history", [])
    if not history:
        st.info("No solved questions yet — pick a topic on **Home** to get started.")
    else:
        for item in history:
            with st.expander(f"{item['topic']} · {item['time']}"):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['answer']}")
