import os
from google import genai
from google.genai import types
from .schemas import ResumeAIReview


def analyze_with_gemini(resume_text: str, job_description: str, heuristic_result: dict) -> ResumeAIReview:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert technical recruiter and resume coach. Evaluate the resume strictly against the supplied job description.
Do not invent experience, skills, employers, metrics, or credentials. Missing keywords are suggestions only when they are genuinely supported by the candidate's background.
Treat the heuristic ATS score as a transparent project heuristic, NOT a commercial ATS score.

HEURISTIC ANALYSIS:
{heuristic_result}

JOB DESCRIPTION:
{job_description[:12000]}

RESUME:
{resume_text[:18000]}

Return:
- concise fit summary
- evidence-based strengths
- material gaps
- missing or under-emphasized JD keywords
- specific rewrite suggestions that preserve truthfulness
- interview focus areas
- final recommendation
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=ResumeAIReview,
        ),
    )

    if response.parsed:
        return response.parsed
    return ResumeAIReview.model_validate_json(response.text)
