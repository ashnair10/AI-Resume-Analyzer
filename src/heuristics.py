import re
from collections import Counter

STOPWORDS = {
    "and", "the", "with", "for", "from", "that", "this", "you", "your", "our", "are", "will", "into",
    "using", "use", "used", "have", "has", "who", "but", "not", "all", "job", "role", "work", "team",
    "experience", "years", "skills", "strong", "ability", "knowledge", "preferred", "required", "requirements",
}

SECTIONS = {
    "summary": ["summary", "profile", "objective"],
    "experience": ["experience", "employment", "work history"],
    "skills": ["skills", "technical skills", "technologies"],
    "education": ["education", "academic"],
    "projects": ["projects", "project experience"],
}

ACTION_WORDS = {
    "built", "developed", "designed", "implemented", "deployed", "led", "created", "optimized", "automated",
    "reduced", "improved", "delivered", "integrated", "engineered", "architected", "scaled", "migrated",
}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9+.#/-]{1,}", text.lower())


def top_job_keywords(jd: str, limit: int = 35) -> list[str]:
    words = [w for w in _tokens(jd) if w not in STOPWORDS and len(w) > 2]
    return [w for w, _ in Counter(words).most_common(limit)]


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
    keyword_score = round(100 * len(matched) / max(1, len(jd_keywords)))

    lines = [line.strip() for line in resume.splitlines() if line.strip()]
    bulletish = [line for line in lines if re.match(r"^[•\-–*]", line)]
    quantified = [line for line in lines if re.search(r"\b\d+(?:\.\d+)?%|\b\d+[+,]?\b|₹|\$", line)]
    action_lines = [line for line in lines if any(re.search(rf"\b{w}\b", line.lower()) for w in ACTION_WORDS)]

    impact_score = min(100, round(35 * min(len(quantified), 6) / 6 + 35 * min(len(action_lines), 8) / 8 + 30 * min(len(bulletish), 10) / 10))

    formatting_flags = []
    if page_count > 2:
        formatting_flags.append("Resume is longer than 2 pages; validate whether the target seniority justifies the length.")
    if len(fonts) > 5:
        formatting_flags.append("Many font families detected; simplify typography for consistency and ATS-safe rendering.")
    common_sizes = [size for size, _ in font_sizes[:5]]
    if common_sizes and min(common_sizes) < 9:
        formatting_flags.append("Very small text detected; keep body text readable (commonly ~10–12 pt).")

    formatting_score = max(55, 100 - 12 * len(formatting_flags))
    ats_score = round(0.45 * keyword_score + 0.25 * section_score + 0.20 * impact_score + 0.10 * formatting_score)

    return {
        "ats_score": ats_score,
        "keyword_score": keyword_score,
        "section_score": section_score,
        "impact_score": impact_score,
        "formatting_score": formatting_score,
        "sections": section_hits,
        "matched_keywords": matched[:20],
        "missing_keywords": missing[:20],
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
