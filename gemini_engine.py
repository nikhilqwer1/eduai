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
# PYDANTIC STRUCTURED SCHEMAS
# ============================================================

class Scene(BaseModel):
    scene_id: int
    title: str = Field(description="Subtopic heading with logical flow")
    avatar_speech: str = Field(description="Exhaustive explanation with analogies and intuition")
    visual_type: Literal["bullet_points", "code", "formula", "diagram_description"]
    visual_content: str = Field(description="Working code, formula or markdown notes")

class Checkpoint(BaseModel):
    checkpoint_id: int
    trigger_after_scene_id: int
    question: str = Field(description="Deep conceptual question")
    options: List[str]
    correct_answer: str
    explanation_on_fail: str = Field(description="Why the mistake happened")

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
# CLIENT INITIALIZATION (STREAMLIT SECRETS + FALLBACK)
# ============================================================

def get_gemini_client():
    api_key = None
    
    # Check Streamlit Cloud Secrets
    try:
        if hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets:
                api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
            elif "GOOGLE_API_KEY" in st.secrets:
                api_key = str(st.secrets["GOOGLE_API_KEY"]).strip().strip('"').strip("'")
    except Exception:
        pass

    # Check environment variable
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "AQ.Ab8RN6J3EHrvghxmztAwO0XDTf2vaMrHczxOQB2ZcS5vZ1Xb4Q"

    return genai.Client(api_key=api_key)

# ============================================================
# LESSON GENERATION
# ============================================================

def generate_structured_lesson(topic: str, context: str, level: str, time_mins: int, language: str) -> LessonPlan:
    client = get_gemini_client()

    prompt = f"""You are an elite professor and expert instructor.
Deliver an in-depth masterclass on: "{topic}".

REQUIREMENTS:
1. Explain from first principles with clarity and deep mechanics.
2. Provide 3 to 5 clear sequential scenes.
3. For code: Write valid code in visual_content.
4. Language: Teach in {language}.
   - If Hinglish: Hindi sentence structure with English technical keywords.
   - If Hindi: Clear educational Hindi.
   - If English: Clear academic English.

Level: {level}
Duration: {time_mins} mins
Context: {context if context else 'Authoritative technical foundations.'}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LessonPlan,
            temperature=0.2,
        ),
    )
    return LessonPlan(**json.loads(response.text))

# ============================================================
# DIAGNOSTIC REPORT
# ============================================================

def generate_diagnostic_report(topic: str, answers_summary: str) -> DiagnosticReport:
    client = get_gemini_client()
    prompt = f"""Conduct a diagnostic performance evaluation:
Topic: {topic}
Performance Data:
{answers_summary}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DiagnosticReport,
            temperature=0.1,
        ),
    )
    return DiagnosticReport(**json.loads(response.text))
