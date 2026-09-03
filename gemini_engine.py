import os
import json
from typing import List, Literal
from pydantic import BaseModel, Field
import google.generativeai as genai
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
# API KEY RESOLUTION & CONFIGURATION
# ============================================================

def setup_gemini():
    api_key = None
    try:
        if hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets:
                api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
            elif "GOOGLE_API_KEY" in st.secrets:
                api_key = str(st.secrets["GOOGLE_API_KEY"]).strip().strip('"').strip("'")
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("API Key missing! Please set GEMINI_API_KEY in Streamlit Secrets.")

    genai.configure(api_key=api_key)

# ============================================================
# LESSON GENERATION
# ============================================================

def generate_structured_lesson(topic: str, context: str, level: str, time_mins: int, language: str) -> LessonPlan:
    setup_gemini()
    model = genai.GenerativeModel("gemini-1.5-flash")

    schema_instruction = """
    Return ONLY a valid JSON object matching this exact structure:
    {
        "lesson_title": "string",
        "target_level": "string",
        "language": "string",
        "scenes": [
            {
                "scene_id": 1,
                "title": "string",
                "avatar_speech": "string",
                "visual_type": "code",
                "visual_content": "string"
            }
        ],
        "checkpoints": [
            {
                "checkpoint_id": 1,
                "trigger_after_scene_id": 1,
                "question": "string",
                "options": ["opt1", "opt2", "opt3"],
                "correct_answer": "opt1",
                "explanation_on_fail": "string"
            }
        ]
    }
    """

    prompt = f"""You are an elite master teacher.
Create a comprehensive masterclass for topic: "{topic}".

Level: {level}
Duration: {time_mins} minutes
Target Language: {language}
Reference Context: {context if context else 'Core technical foundations.'}

Provide 3 to 5 scenes with practical code or formulas.
{schema_instruction}
"""

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    data = json.loads(response.text)
    return LessonPlan(**data)

# ============================================================
# DIAGNOSTIC REPORT GENERATION
# ============================================================

def generate_diagnostic_report(topic: str, answers_summary: str) -> DiagnosticReport:
    setup_gemini()
    model = genai.GenerativeModel("gemini-1.5-flash")

    schema_instruction = """
    Return ONLY a valid JSON object matching this structure:
    {
        "score_percentage": 85.0,
        "mastered_concepts": ["concept 1", "concept 2"],
        "weak_concepts": ["weak area 1"],
        "recommended_revision_plan": "string",
        "suggested_next_topic": "string"
    }
    """

    prompt = f"""Generate a diagnostic performance evaluation for topic: {topic}.
Data: {answers_summary}
{schema_instruction}
"""

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    data = json.loads(response.text)
    return DiagnosticReport(**data)
