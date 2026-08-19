# MathMate — Interactive Mathematics Lab

Streamlit app covering six syllabus topics with step-by-step solutions:

- 🧮 Euclidean Algorithm & GCD
- 📍 Complex Numbers & Polar Form
- 🔄 De Moivre's Theorem (powers + n-th roots)
- 🔢 Permutations & Combinations
- 🔗 Injective, Surjective & Bijective Functions
- 📈 Limits & Continuity (symbolic, via SymPy)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push `app.py` and `requirements.txt` to your GitHub repo (e.g. `mathmate-ai`).
2. On Streamlit Cloud, point the app at `app.py`.

## Notes on the current build

- **Topic detection** is keyword-based (see `TOPIC_KEYWORDS` in `app.py`).
  It's intentionally simple/fast — swap in an LLM call there later if you
  want smarter detection on messier inputs.
- **Exports**: DOCX via `python-docx`, PDF via `reportlab`. Both are optional
  imports — if either package is missing, that download button is hidden
  with a note instead of breaking the app.
- **Share link** and **Copy** buttons are UI stubs — wire them to your own
  backend / clipboard JS component when ready.
- **Quiz** question bank is a small static list in `app.py` (`QUESTION_BANK`)
  — easy to expand or move to a JSON/DB file later.
- **History** and **streak** are stored in `st.session_state`, so they reset
  per session. Hook up Supabase (like your other projects) if you want
  persistent history across logins.
