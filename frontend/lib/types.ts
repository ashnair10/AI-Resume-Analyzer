export type EvidenceStatus = "strong" | "moderate" | "weak" | "missing";

export type EvidenceItem = {
  requirement: string;
  status: EvidenceStatus;
  evidence: string[];
};

export type Analysis = {
  role_evidence_score: number;
  requirement_coverage_score: number;
  evidence_strength_score: number;
  section_score: number;
  impact_score: number;
  formatting_score: number;
  readiness: "ready_to_apply" | "improve_before_applying" | "weak_fit";
  matched_keywords: string[];
  missing_keywords: string[];
  evidence_map: EvidenceItem[];
  subjective_claims: string[];
  weakly_supported_mentions: string[];
  formatting_flags: string[];
  stats: {
    lines: number;
    bullet_lines: number;
    quantified_lines: number;
    action_lines: number;
  };
};

export type AIReview = {
  role_summary: string;
  requirements: Array<{
    requirement: string;
    category: "technical" | "domain" | "responsibility" | "seniority" | "education" | "other";
    priority: "must_have" | "important" | "nice_to_have";
    keywords: string[];
  }>;
  evidence_map: Array<{
    requirement: string;
    status: EvidenceStatus;
    evidence: string[];
    explanation: string;
    recommendation: string;
  }>;
  strengths: string[];
  material_gaps: string[];
  recruiter_10_second_scan: string[];
  interview_focus: string[];
  readiness: "ready_to_apply" | "improve_before_applying" | "weak_fit";
  final_recommendation: string;
  rewrite_suggestions: Array<{
    original: string;
    suggested: string;
    reason: string;
    requires_confirmation: boolean;
  }>;
  claim_checks: Array<{
    claim: string;
    status: "supported" | "needs_confirmation" | "unsupported" | "subjective";
    evidence: string[];
    safer_rewrite: string;
    explanation: string;
  }>;
};

export type AnalyzeResponse = {
  trace_id: string;
  duration_ms: number;
  document: { filename: string; file_type: string; page_count: number };
  guardrails: {
    pii_detected: boolean;
    pii_types: string[];
    prompt_injection_signals: string[];
  };
  analysis: Analysis;
  ai: { enabled: boolean; provider: string; model: string | null; error: string | null };
  ai_review: AIReview | null;
};
