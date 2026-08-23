"""
API Client module for MathMate.
Safely retrieves API keys from Streamlit secrets or environment variables.
Provides AI solver fallback and AI Math Tutor interaction for the 6 syllabus topics.
"""

import os
import json
import streamlit as st

def get_api_key():
    """Safely fetch NVIDIA_API_KEY or OPENAI_API_KEY from st.secrets or os.environ."""
    try:
        if hasattr(st, "secrets"):
            if "NVIDIA_API_KEY" in st.secrets:
                return st.secrets["NVIDIA_API_KEY"], "https://integrate.api.nvidia.com/v1", "meta/llama-3.1-70b-instruct"
            if "OPENAI_API_KEY" in st.secrets:
                return st.secrets["OPENAI_API_KEY"], "https://api.openai.com/v1", "gpt-4o-mini"
    except Exception:
        pass

    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    if nvidia_key:
        return nvidia_key, "https://integrate.api.nvidia.com/v1", "meta/llama-3.1-70b-instruct"

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        return openai_key, "https://api.openai.com/v1", "gpt-4o-mini"

    return None, None, None


def setup_client():
    """Sets up API client safely, returning (client, model_name) or (None, None) if key is missing."""
    api_key, base_url, model_name = get_api_key()
    if not api_key:
        return None, None
    
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        return client, model_name
    except Exception:
        return None, None


def solve_with_ai(question: str) -> dict:
    """
    Solves a math question using LLM fallback when standard parser/solver needs assistance.
    Returns dict with keys: 'topic', 'steps', 'answer'.
    """
    client, model = setup_client()
    if not client:
        return None

    system_prompt = (
        "You are MathMate AI, an expert mathematics solver specializing in 6 syllabus topics:\n"
        "1. Euclidean Algorithm & GCD\n"
        "2. Complex Numbers & Polar Form\n"
        "3. De Moivre's Theorem (powers and n-th roots)\n"
        "4. Permutations & Combinations\n"
        "5. Injective, Surjective & Bijective Functions\n"
        "6. Limits & Continuity\n\n"
        "Given a question, respond STRICTLY in JSON format with keys:\n"
        "{\n"
        "  \"topic\": \"one of the 6 topics\",\n"
        "  \"steps\": [ [\"Step 1 Title\", \"Description\"], [\"Step 2 Title\", \"Description\"], ... ],\n"
        "  \"answer\": \"Final concise numerical/symbolic answer\"\n"
        "}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Solve this math problem step-by-step: {question}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"AI solve error: {e}")
        return None


def ask_ai_tutor(user_question: str, topic_context: str = "") -> str:
    """
    Answers a student's conceptual question as an AI Math Tutor.
    """
    client, model = setup_client()
    if not client:
        return (
            "⚠️ **AI Tutor API Key Missing**\n\n"
            "To activate the AI Math Tutor, set `NVIDIA_API_KEY` or `OPENAI_API_KEY` in your `.streamlit/secrets.toml` file or environment variables."
        )

    system_prompt = (
        "You are MathMate AI Tutor — an encouraging, clear, and concise mathematics tutor. "
        "You help university and high-school students master 6 core topics:\n"
        "- Euclidean Algorithm & GCD\n"
        "- Complex Numbers & Polar Form\n"
        "- De Moivre's Theorem\n"
        "- Permutations & Combinations\n"
        "- Injective, Surjective & Bijective Functions\n"
        "- Limits & Continuity\n\n"
        "Explain concepts intuitively using clear markdown formatting and LaTeX notation ($...$ or $$...$$) where appropriate."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if topic_context:
        messages.append({"role": "system", "content": f"Current Topic Context: {topic_context}"})
    messages.append({"role": "user", "content": user_question})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Could not generate response from AI Tutor: {e}"
