from pydantic import BaseModel, Field


class ResumeAIReview(BaseModel):
    fit_summary: str = Field(description="Concise recruiter-style fit summary")
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    rewrite_suggestions: list[str] = Field(default_factory=list)
    interview_focus: list[str] = Field(default_factory=list)
    final_recommendation: str
