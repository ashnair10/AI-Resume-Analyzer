import os
from google import genai
from google.genai import types
from .schemas import ResumeAIReview


def analyze_with_gemini(resume_text: str, job_description: str, heuristic_result: dict) -> ResumeAIReview:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are the reasoning engine for CVAlchemy, an evidence-first resume optimization copilot.
Your task is NOT to maximize keyword count. Your task is to determine what the target job requires, what the candidate can truthfully support, and how to present that evidence clearly.

NON-NEGOTIABLE RULES
1. Never invent experience, ownership, employers, certifications, metrics, seniority, technologies, or outcomes.
2. A skill appearing only in a Skills section is weak evidence unless experience/project evidence also supports it.
3. Distinguish exact evidence from inference. If a suggested rewrite adds scope, ownership, metric, or technology not explicitly supported, set requires_confirmation=true.
4. For claim_checks, mark subjective or inflated language separately. Prefer measurable wording over adjectives.
5. Do not call the project score an ATS score. It is a CVAlchemy Role Evidence Score.
6. Treat missing keywords as genuine gaps unless there is semantically equivalent evidence elsewhere in the resume.
7. Evidence strings must be copied exactly or very tightly paraphrased from the supplied resume; never fabricate evidence.
8. Prioritize MUST-HAVE job requirements over nice-to-have ones.

CVAlchemy DETERMINISTIC ANALYSIS:
{heuristic_result}

TARGET JOB DESCRIPTION:
{job_description[:14000]}

CANDIDATE RESUME:
{resume_text[:20000]}

Produce structured output containing:
- a concise role_summary describing what matters most in this JD
- 8-15 decomposed requirements with category and must_have/important/nice_to_have priority
- an evidence_map for important requirements, each marked strong/moderate/weak/missing
- claim_checks for important resume claims that are subjective, insufficiently evidenced, need confirmation, or are clearly supported
- strengths and material gaps
- 3-8 rewrite suggestions in Original -> Suggested -> Reason format; never fabricate facts
- recruiter_10_second_scan: what a recruiter is likely to notice immediately
- interview_focus: claims/skills the candidate should be prepared to defend
- readiness: ready_to_apply, improve_before_applying, or weak_fit
- final recommendation
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.15,
            response_mime_type="application/json",
            response_schema=ResumeAIReview,
        ),
    )

    if response.parsed:
        return response.parsed
    return ResumeAIReview.model_validate_json(response.text)
