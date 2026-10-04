from typing import Literal
from pydantic import BaseModel, Field


class JDRequirement(BaseModel):
    requirement: str
    category: Literal["technical", "domain", "responsibility", "seniority", "education", "other"] = "other"
    priority: Literal["must_have", "important", "nice_to_have"] = "important"
    keywords: list[str] = Field(default_factory=list)


class EvidenceMatch(BaseModel):
    requirement: str
    status: Literal["strong", "moderate", "weak", "missing"]
    evidence: list[str] = Field(default_factory=list, description="Exact or tightly paraphrased evidence found in the resume")
    explanation: str
    recommendation: str


class ClaimCheck(BaseModel):
    claim: str
    status: Literal["supported", "needs_confirmation", "unsupported", "subjective"]
    evidence: list[str] = Field(default_factory=list)
    safer_rewrite: str = ""
    explanation: str = ""


class RewriteSuggestion(BaseModel):
    original: str
    suggested: str
    reason: str
    requires_confirmation: bool = False


class ResumeAIReview(BaseModel):
    role_summary: str = Field(description="Concise summary of what the role is really asking for")
    requirements: list[JDRequirement] = Field(default_factory=list)
    evidence_map: list[EvidenceMatch] = Field(default_factory=list)
    claim_checks: list[ClaimCheck] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    material_gaps: list[str] = Field(default_factory=list)
    rewrite_suggestions: list[RewriteSuggestion] = Field(default_factory=list)
    recruiter_10_second_scan: list[str] = Field(default_factory=list)
    interview_focus: list[str] = Field(default_factory=list)
    readiness: Literal["ready_to_apply", "improve_before_applying", "weak_fit"]
    final_recommendation: str
