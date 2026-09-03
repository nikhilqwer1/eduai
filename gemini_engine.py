import os
import json
from typing import List, Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

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

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "AQ.Ab8RN6J3EHrvghxmztAwO0XDTf2vaMrHczxOQB2ZcS5vZ1Xb4Q"
    return genai.Client(api_key=api_key)

def generate_structured_lesson(topic: str, context: str, level: str, time_mins: int, language: str) -> LessonPlan:
    client = get_gemini_client()

    prompt = f"""You are a world-class university professor and technical expert.
Your mission is to deliver an IN-DEPTH, RIGOROUS, AND CRYSTAL-CLEAR masterclass on: "{topic}".

PEDAGOGICAL REQUIREMENTS:
1. Deep Fundamentals: Do not give shallow summaries. Explain the "WHY" behind every mechanism from first principles.
2. Step-by-Step Flow: Divide the masterclass into 4 to 6 sequential scenes:
   - Scene 1: Intuition, Motivation & Real-world Analogy (Why does this exist?).
   - Scene 2: Architectural/Mathematical Foundations (Underlying equations or logic).
   - Scene 3: Practical Mechanics & Implementation (Step-by-step trace or production code).
   - Scene 4: Edge Cases, Time/Space Complexity & Optimization Trade-offs.
   - Scene 5: Common Pitfalls & Real-world Industry Applications.
3. Chalkboard Visuals:
   - Use clean LaTeX for mathematical equations.
   - Write complete, syntactically valid code blocks for programming topics.
   - Use structured bullet points for system flows.
4. Language Requirement:
   - Target Language: {language}.
   - If Hindi: Pure, formal yet simple educational Hindi.
   - If Hinglish: Natural conversational tech dialect (Hindi grammar structure using standard technical terms like 'function', 'memory', 'pointer', 'complexity').
   - If English: Clean, authoritative pedagogical English.
   - If any regional language (Bengali, Tamil, etc.): Strictly teach in that regional dialect.

Learner Level: {level}
Target Duration: {time_mins} minutes

Reference Material (RAG Context):
{context if context else 'Rely on comprehensive domain authority.'}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LessonPlan,
            temperature=0.2,
        ),
    )
    return LessonPlan(**json.loads(response.text))

def generate_diagnostic_report(topic: str, answers_summary: str) -> DiagnosticReport:
    client = get_gemini_client()
    prompt = f"""Conduct a diagnostic post-mortem on the student's answers:
Topic: {topic}
Performance Data:
{answers_summary}

Highlight exact root-cause misconceptions and provide a targeted remedial plan."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DiagnosticReport,
            temperature=0.1,
        ),
    )
    return DiagnosticReport(**json.loads(response.text))