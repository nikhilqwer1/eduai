import os
import json
from typing import List, Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
import streamlit as st

load_dotenv(override=True)

# ============================================================
# PYDANTIC STRUCTURED SCHEMAS FOR STRUCTURED CURRICULUM
# ============================================================

class Scene(BaseModel):
    scene_id: int
    title: str = Field(description="Subtopic heading with logical flow")
    avatar_speech: str = Field(description="Exhaustive, rigorous, engaging explanation with analogies and intuition")
    visual_type: Literal["bullet_points", "code", "formula", "diagram_description"]
    visual_content: str = Field(description="Complete working code, mathematical derivation, or deep architecture notes")

class Checkpoint(BaseModel):
    checkpoint_id: int
    trigger_after_scene_id: int
    question: str = Field(description="Deep conceptual question testing reasoning, not memory")
    options: List[str]
    correct_answer: str
    explanation_on_fail: str = Field(description="Intuitive real-life mental model explaining why the mistake happened")

class LessonPlan(BaseModel):
    lesson_title: str
    target_level: str
    language: str
    scenes: List[Scene]
    checkpoints: List[Checkpoint]

class DiagnosticReport(BaseModel):
    score_percentage: float
    mastered_concepts: List[str]
    weak_concepts: List[str]
    recommended_revision_plan: str
    suggested_next_topic: str

# ============================================================
# CLIENT INITIALIZATION (STREAMLIT SECRETS + ENV FALLBACK)
# ============================================================

def get_gemini_client():
    api_key = None
    
    # 1. Streamlit Cloud Secrets check
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        elif hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass

    # 2. Local .env or OS Environment fallback
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "AQ.Ab8RN6J3EHrvghxmztAwO0XDTf2vaMrHczxOQB2ZcS5vZ1Xb4Q"

    return genai.Client(api_key=api_key)

# ============================================================
# DEEP PEDAGOGICAL LESSON GENERATION
# ============================================================

def generate_structured_lesson(topic: str, context: str, level: str, time_mins: int, language: str) -> LessonPlan:
    client = get_gemini_client()

    prompt = f"""You are an elite professor and expert instructor.
Deliver an IN-DEPTH, RIGOROUS, AND CRYSTAL-CLEAR masterclass on the topic: "{topic}".

PEDAGOGICAL INSTRUCTIONS:
1. Deep Technical Rigor:
   - Do NOT give generic or shallow summaries. Explain the underlying "WHY" from first principles.
   - For algorithmic/CS topics: Show full code logic, step-by-step memory mutations, pointers, time/space complexity analysis.
   - For mathematical topics: Show formal formula derivations step-by-step using clean LaTeX notation.
   
2. Structured Scenes Breakdown:
   - Scene 1: First Principles Motivation & Intuitive Metaphor (Why does this exist? What problem does it solve?).
   - Scene 2: Core Architecture & Mathematical Foundations (Underlying equations or mechanical invariants).
   - Scene 3: Practical Implementation (Fully working code snippet or rigorous mathematical proof).
   - Scene 4: Edge Cases, Invariant Failures & Optimization Trade-offs.
   - Scene 5: Real-World Industry Application & Best Practices.

3. Blackboard Content Formatting:
   - If visual_type is 'code': Provide clean, syntactically correct Python code with explanatory comments.
   - If visual_type is 'formula': Output valid LaTeX mathematical expressions.
   - If visual_type is 'bullet_points': Output concise, high-contrast engineering notes.

4. Language Delivery:
   - Target Language: {language}.
   - If Hinglish: Natural conversational Hindi grammar mixed with standard English tech terms (e.g. array, memory, pointer, buffer, condition).
   - If Hindi: Formal, high-clarity educational Hindi.
   - If English: Authoritative pedagogical English.
   - If Regional (Bengali, Tamil, Telugu, Marathi, etc.): Explain strictly and naturally in that language.

Student Proficiency Level: {level}
Target Session Duration: {time_mins} minutes

Reference Material (RAG Context):
{context if context else 'Rely on authoritative foundational domain knowledge.'}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LessonPlan,
            temperature=0.2,
        ),
    )
    return LessonPlan(**json.loads(response.text))

# ============================================================
# DIAGNOSTIC PERFORMANCE REPORT
# ============================================================

def generate_diagnostic_report(topic: str, answers_summary: str) -> DiagnosticReport:
    client = get_gemini_client()
    prompt = f"""You are conducting a pedagogical diagnostic evaluation on a student.
Topic Evaluated: {topic}
Checkpoint Performance Data:
{answers_summary}

Analyze the exact root-cause misconceptions, list mastered competencies vs weak areas, and generate an actionable revision roadmap."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DiagnosticReport,
            temperature=0.1,
        ),
    )
    return DiagnosticReport(**json.loads(response.text))
