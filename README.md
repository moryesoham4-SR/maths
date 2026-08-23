# MathMate — Interactive Mathematics Lab 🧮

Streamlit application covering **6 core syllabus topics** with step-by-step reasoning, interactive Plotly visualizations, AI math tutoring, persistent database history, and procedural practice quizzes:

1. 🧮 **Euclidean Algorithm & GCD**
2. 📍 **Complex Numbers & Polar Form**
3. 🔄 **De Moivre's Theorem (powers & n-th roots)**
4. 🔢 **Permutations & Combinations**
5. 🔗 **Injective, Surjective & Bijective Functions**
6. 📈 **Limits & Continuity (symbolic via SymPy)**

---

## Features

- **Step-by-Step Solvers**: Detailed quotient-remainder breakdowns, Argand conversions, permutation factorials, function mappings, and symbolic limits.
- **Interactive Visualizations**: Dynamic Plotly Argand planes, roots polygons, bipartite mapping diagrams, and limit curves.
- **Supabase Persistence**: Cloud storage for solution history, streak tracking, XP points, and quiz metrics (with local SQLite fallback).
- **AI Solver & Tutor**: LLM fallback for natural language problems and an interactive AI Math Tutor chat.
- **Procedural Quiz Engine**: Infinite variable-randomized practice problems.
- **Formula Cheat Sheet**: Comprehensive reference cards with LaTeX expressions.

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Push code to your GitHub repository.
2. In **Streamlit Cloud Settings** $\to$ **Secrets**, paste your credentials:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-key"
NVIDIA_API_KEY = "your-nvidia-key" # Optional for AI Tutor
```

3. Set `app.py` as the main file path.
