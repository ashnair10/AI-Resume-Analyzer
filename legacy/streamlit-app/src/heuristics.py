import re
from collections import Counter

STOPWORDS = {
    "and", "the", "with", "for", "from", "that", "this", "you", "your", "our", "are", "will", "into",
    "using", "use", "used", "have", "has", "who", "but", "not", "all", "job", "role", "work", "team",
    "experience", "years", "skills", "strong", "ability", "knowledge", "preferred", "required", "requirements",
    "candidate", "responsibilities", "responsibility", "including", "across", "within", "about", "their",
}

SECTIONS = {
    "summary": ["summary", "profile", "objective"],
    "experience": ["experience", "employment", "work history", "professional experience"],
    "skills": ["skills", "technical skills", "technologies", "core competencies"],
    "education": ["education", "academic"],
    "projects": ["projects", "project experience", "selected projects"],
}

ACTION_WORDS = {
    "built", "developed", "designed", "implemented", "deployed", "led", "created", "optimized", "automated",
    "reduced", "improved", "delivered", "integrated", "engineered", "architected", "scaled", "migrated",
    "owned", "launched", "orchestrated", "streamlined", "increased", "decreased", "managed", "drove",
}

SUBJECTIVE_CLAIMS = {
    "expert", "highly skilled", "exceptional", "world-class", "best-in-class", "highly scalable", "cutting-edge",
    "proven expert", "deep expertise", "extensive expertise", "outstanding",
}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9+.#/-]{1,}", text.lower())


def top_job_keywords(jd: str, limit: int = 40) -> list[str]:
    words = [w for w in _tokens(jd) if w not in STOPWORDS and len(w) > 2]
    return [w for w, _ in Counter(words).most_common(limit)]


def _lines(text: str) -> list[str]:
    return [re.sub(r"^[•\-–*]\s*", "", line.strip()) for line in text.splitlines() if line.strip()]


def _best_evidence_for_keyword(keyword: str, resume_lines: list[str], limit: int = 3) -> list[str]:
    key = keyword.lower()
    matches = [line for line in resume_lines if re.search(rf"\b{re.escape(key)}\b", line.lower())]
    matches.sort(key=lambda line: (bool(re.search(r"\d", line)), len(line)), reverse=True)
    return matches[:limit]


def analyze_heuristics(resume: str, jd: str, page_count: int, fonts: list[tuple[str, int]], font_sizes: list[tuple[float, int]]) -> dict:
    lower = resume.lower()
    tokens = set(_tokens(resume))
    jd_keywords = top_job_keywords(jd)
    matched = [k for k in jd_keywords if k in tokens]
    missing = [k for k in jd_keywords if k not in tokens]

    section_hits = {
        name: any(re.search(rf"\b{re.escape(alias)}\b", lower) for alias in aliases)
        for name, aliases in SECTIONS.items()
    }
    section_score = round(100 * sum(section_hits.values()) / len(section_hits))
    coverage_score = round(100 * len(matched) / max(1, len(jd_keywords)))

    lines = _lines(resume)
    raw_lines = [line.strip() for line in resume.splitlines() if line.strip()]
    bulletish = [line for line in raw_lines if re.match(r"^[•\-–*]", line)]
    quantified = [line for line in lines if re.search(r"\b\d+(?:\.\d+)?%|\b\d+[+,]?\b|₹|\$", line)]
    action_lines = [line for line in lines if any(re.search(rf"\b{w}\b", line.lower()) for w in ACTION_WORDS)]

    impact_score = min(
        100,
        round(
            45 * min(len(quantified), 6) / 6
            + 35 * min(len(action_lines), 8) / 8
            + 20 * min(len(bulletish), 10) / 10
        ),
    )

    evidence_map = []
    for keyword in jd_keywords[:20]:
        evidence = _best_evidence_for_keyword(keyword, lines)
        if evidence:
            if any(re.search(r"\d", e) for e in evidence) and any(
                any(re.search(rf"\b{w}\b", e.lower()) for w in ACTION_WORDS) for e in evidence
            ):
                strength = "strong"
            elif len(evidence) >= 2:
                strength = "moderate"
            else:
                strength = "weak"
        else:
            strength = "missing"
        evidence_map.append({"requirement": keyword, "status": strength, "evidence": evidence})

    evidence_weights = {"strong": 1.0, "moderate": 0.7, "weak": 0.35, "missing": 0.0}
    evidence_strength_score = round(
        100 * sum(evidence_weights[item["status"]] for item in evidence_map) / max(1, len(evidence_map))
    )

    formatting_flags = []
    if page_count > 2:
        formatting_flags.append("Resume is longer than 2 pages; confirm the extra length adds role-relevant evidence.")
    if len(fonts) > 5:
        formatting_flags.append("Many font families detected; simplify typography for consistency and ATS-safe rendering.")
    common_sizes = [size for size, _ in font_sizes[:5]]
    if common_sizes and min(common_sizes) < 9:
        formatting_flags.append("Very small text detected; keep body text readable, typically around 10–12 pt.")
    formatting_score = max(55, 100 - 12 * len(formatting_flags))

    subjective_claims = [line for line in lines if any(term in line.lower() for term in SUBJECTIVE_CLAIMS)]
    unsupported_skill_mentions = [
        item["requirement"] for item in evidence_map if item["status"] == "weak" and item["requirement"] in tokens
    ]

    # CVAlchemy score: role evidence is deliberately weighted above raw keyword frequency.
    role_evidence_score = round(
        0.35 * coverage_score
        + 0.30 * evidence_strength_score
        + 0.15 * impact_score
        + 0.10 * section_score
        + 0.10 * formatting_score
    )

    if role_evidence_score >= 78 and evidence_strength_score >= 65:
        readiness = "ready_to_apply"
    elif role_evidence_score >= 55:
        readiness = "improve_before_applying"
    else:
        readiness = "weak_fit"

    return {
        "role_evidence_score": role_evidence_score,
        "requirement_coverage_score": coverage_score,
        "evidence_strength_score": evidence_strength_score,
        "section_score": section_score,
        "impact_score": impact_score,
        "formatting_score": formatting_score,
        "readiness": readiness,
        "sections": section_hits,
        "matched_keywords": matched[:25],
        "missing_keywords": missing[:25],
        "evidence_map": evidence_map,
        "subjective_claims": subjective_claims[:12],
        "weakly_supported_mentions": unsupported_skill_mentions[:12],
        "formatting_flags": formatting_flags,
        "page_count": page_count,
        "fonts": fonts,
        "font_sizes": font_sizes,
        "stats": {
            "lines": len(lines),
            "bullet_lines": len(bulletish),
            "quantified_lines": len(quantified),
            "action_lines": len(action_lines),
        },
    }
