from dataclasses import dataclass
from typing import Any
import os

@dataclass
class AIResult:
    enabled: bool
    provider: str
    model: str | None
    review: dict[str, Any] | None
    error: str | None = None


def analyze_resume_ai(resume_text: str, job_description: str, heuristics: dict) -> AIResult:
    """Single boundary for model calls.

    This is intentionally isolated so prompt/versioning, guardrails, Langfuse tracing,
    Azure OpenAI, or model routing can be added without touching API/business logic.
    """
    if not os.getenv("GEMINI_API_KEY"):
        return AIResult(False, "none", None, None)

    if len(resume_text) > 20000 or len(job_description) > 14000:
        return AIResult(False, "gemini", None, None, "AI review limits are 20,000 resume characters and 14,000 JD characters. Shorten the input; local checks still cover the complete text.")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    try:
        from src.gemini_analyzer import analyze_with_gemini
        review = analyze_with_gemini(resume_text, job_description, heuristics)
        return AIResult(True, "gemini", model, review.model_dump())
    except Exception as exc:  # app should still return deterministic analysis
        return AIResult(True, "gemini", model, None, str(exc))
