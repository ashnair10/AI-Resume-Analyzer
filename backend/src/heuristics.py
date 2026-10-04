import re
from collections import Counter

STOPWORDS = {
    "and", "the", "with", "for", "from", "that", "this", "you", "your", "our", "are", "will", "into",
    "using", "use", "used", "have", "has", "who", "but", "not", "all", "job", "role", "work", "team",
    "experience", "years", "skills", "strong", "ability", "knowledge", "preferred", "required", "requirements",
    "candidate", "responsibilities", "responsibility", "including", "across", "within", "about", "their",
    "position", "positions", "working", "works", "worked", "qualification", "qualifications", "description",
    "descriptions", "build", "building", "built", "develop", "developing", "seeking", "looking", "ideal",
    "successful", "success", "must", "would", "could", "should", "able", "also", "well", "such", "etc",
    "example", "examples", "e.g", "eg", "most", "many", "more", "less", "least", "make", "making",
    "provide", "providing", "support", "supporting", "include", "including", "ensure", "ensuring",
    "across", "various", "multiple", "business", "company", "organization", "organizations", "team",
    "teams", "india", "hyderabad", "bengaluru", "bangalore", "pune", "gurgaon", "remote",
    "technical", "professional", "professionals", "responsible", "responsibilities", "including",
    "environment", "environments", "solutions", "solution", "role", "position", "description",
}

SECTIONS = {
    "summary": ["summary", "professional summary", "profile", "objective"],
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

WEAK_OPENINGS = (
    "responsible for",
    "worked on",
    "helped with",
    "involved in",
    "duties included",
    "tasked with",
)

COMMON_MISSPELLINGS = {
    "experiance": "experience",
    "recieve": "receive",
    "recieved": "received",
    "managment": "management",
    "developement": "development",
    "enviroment": "environment",
    "seperated": "separated",
    "occured": "occurred",
    "succesful": "successful",
}

SUBJECTIVE_CLAIMS = {
    "expert", "highly skilled", "exceptional", "world-class", "best-in-class", "highly scalable", "cutting-edge",
    "proven expert", "deep expertise", "extensive expertise", "outstanding",
}


def _tokens(text: str) -> list[str]:
    return [token.rstrip(".,/") for token in re.findall(r"[A-Za-z][A-Za-z0-9+.#/-]{1,}", text.lower())]


def top_job_keywords(jd: str, limit: int = 40) -> list[str]:
    words = [w for w in _tokens(jd) if w not in STOPWORDS and len(w) > 2]
    return [w for w, _ in Counter(words).most_common(limit)]


def _lines(text: str) -> list[str]:
    return [re.sub(r"^[•\-–*]\s*", "", line.strip()) for line in text.splitlines() if line.strip()]


def _mentions(keyword: str, line: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", line, re.I))


def _has_action(line: str) -> bool:
    return any(_mentions(word, line) for word in ACTION_WORDS)


def _has_metric(line: str) -> bool:
    # Dates, years of experience, and numbered headings alone are not impact.
    return bool(re.search(r"\d+(?:\.\d+)?\s*%|[₹$]\s*\d|\d[\d,]*(?:\s*[-–]\s*\d[\d,]*)?\s*(?:documents?|requests?|users?|hours?|minutes?|seconds?|ms|days?|files?|pages?)\b", line, re.I))


def _context_lines(text: str) -> list[tuple[str, str]]:
    aliases = {alias: section for section, names in SECTIONS.items() for alias in names}
    aliases.update({"personal projects": "projects"})
    current = "other"
    result = []
    for raw in text.splitlines():
        line = re.sub(r"^[•\-–*]\s*", "", raw.strip())
        if not line:
            continue
        heading = line.lstrip("# ").rstrip(":").lower()
        if heading in aliases:
            current = aliases[heading]
        elif raw.strip().startswith("## "):
            current = "other"
        else:
            result.append((line, current))
    return result


def _best_evidence_for_keyword(keyword: str, resume_lines: list[str], limit: int = 3) -> list[str]:
    matches = [line for line in resume_lines if _mentions(keyword, line)]
    matches.sort(key=lambda line: (
        _has_action(line) and _has_metric(line),
        _has_action(line),
        len(line),
    ), reverse=True)
    return matches[:limit]


def _quality_feedback(
    resume: str,
    section_hits: dict[str, bool],
    bullet_lines: list[str],
    quantified_lines: list[str],
    page_count: int,
    word_count: int,
) -> list[dict[str, str]]:
    feedback: list[dict[str, str]] = []

    def add(priority: str, category: str, title: str, detail: str) -> None:
        feedback.append({
            "priority": priority,
            "category": category,
            "title": title,
            "detail": detail,
        })

    missing_sections = [name.title() for name, present in section_hits.items() if not present]
    if missing_sections:
        add(
            "suggestion",
            "Structure",
            "Check your resume sections",
            f"These common sections were not detected: {', '.join(missing_sections)}. Add only sections that fit your experience; section detection is based on heading text.",
        )

    weak_bullets = [
        line for line in bullet_lines
        if line.lstrip("•-*– ").lower().startswith(WEAK_OPENINGS)
    ]
    for line in weak_bullets[:3]:
        add(
            "priority",
            "Bullet clarity",
            "Replace a passive bullet opening",
            f"'{line[:180]}' starts with a vague phrase. Start with your specific action and state the outcome you can verify.",
        )
    if len(weak_bullets) > 3:
        add(
            "suggestion",
            "Bullet clarity",
            "Review other passive bullet openings",
            f"{len(weak_bullets) - 3} more bullets use openings such as 'worked on' or 'responsible for'.",
        )

    long_bullets = [
        (line, len(_tokens(line)))
        for line in bullet_lines
        if len(_tokens(line)) > 32
    ]
    for line, count in long_bullets[:3]:
        add(
            "suggestion",
            "Conciseness",
            f"Consider shortening this {count}-word bullet",
            f"'{line[:180]}' is long for a quick scan. Keep the problem, your action, and the most useful result; this is a readability hint, not a strict limit.",
        )
    if not bullet_lines:
        add(
            "priority",
            "Experience",
            "Use concise achievement bullets",
            "No bullet-style lines were detected. Use short bullets for work and project outcomes so readers can scan your contribution.",
        )
    elif not quantified_lines:
        add(
            "suggestion",
            "Impact",
            "Make outcomes clearer where possible",
            "No action-led work or project bullet with a detected metric was found. Add a truthful scale, time, quality, or outcome measure where one is available; do not invent numbers.",
        )

    lowered_resume = resume.lower()
    for misspelling, correction in COMMON_MISSPELLINGS.items():
        needle = misspelling.strip()
        if re.search(rf"\b{re.escape(needle)}\b", lowered_resume):
            add(
                "priority",
                "Spelling",
                f"Check spelling: “{needle}”",
                f"Possible correction: “{correction.strip()}”. This is a limited automated spelling check; review the source wording.",
            )

    for line in bullet_lines:
        text = line.lstrip("•-*– ").strip()
        if text and text[0].islower() and len(text) > 1 and text[1].isalpha():
            add(
                "suggestion",
                "Grammar",
                "Check sentence capitalization",
                f"'{line[:180]}' begins with a lowercase letter. Capitalize it if it is a complete bullet sentence.",
            )
            break

    word_count_message = (
        f"The extracted resume contains about {word_count} words. "
        "As a rough editing guide, many early-career resumes fit one page and experienced candidates often use one to two pages. "
        "Keep relevant evidence and readable type; do not remove useful content just to hit a number."
    )
    if page_count > 2:
        add(
            "suggestion",
            "Length",
            f"Review the {page_count}-page layout",
            word_count_message,
        )
    elif word_count > 1100:
        add(
            "suggestion",
            "Length",
            f"Review the {word_count}-word content for focus",
            word_count_message,
        )
    elif page_count == 0:
        add(
            "info",
            "Length",
            "Confirm page count in the exported PDF",
            "DOCX pagination depends on the renderer and cannot be read reliably here. Use the builder's PDF preview/export to confirm the final page count and avoid shrinking text below a comfortable reading size.",
        )

    add(
        "info",
        "Layout",
        "Prefer a clear single-column layout for ATS parsing",
        "This text analysis cannot reliably detect columns, tables, icons, or reading order. A simple single-column template is the safer default; inspect the exported PDF and imported text if you use a multi-column design.",
    )

    if len(feedback) == 1 and feedback[0]["category"] == "Layout":
        add(
            "info",
            "Review",
            "No obvious high-priority writing issue detected",
            "This is a limited automated check, not a complete grammar proofread. Review the resume manually and use optional AI review for broader language feedback.",
        )
    return feedback


def analyze_heuristics(resume: str, jd: str, page_count: int, fonts: list[tuple[str, int]], font_sizes: list[tuple[float, int]]) -> dict:
    tokens = set(_tokens(resume))
    jd_keywords = top_job_keywords(jd)
    matched = [k for k in jd_keywords if k in tokens]
    missing = [k for k in jd_keywords if k not in tokens]

    headings = {
        line.strip().lstrip("# ").rstrip(":").strip().lower()
        for line in resume.splitlines()
        if line.strip()
    }
    section_hits = {
        name: any(alias in headings for alias in aliases)
        for name, aliases in SECTIONS.items()
    }
    section_score = round(100 * sum(section_hits.values()) / len(section_hits))
    coverage_score = round(100 * len(matched) / max(1, len(jd_keywords)))

    lines = _lines(resume)
    raw_lines = [line.strip() for line in resume.splitlines() if line.strip()]
    bulletish = [line for line in raw_lines if re.match(r"^[•\-–*]", line)]
    contexts = _context_lines(resume)
    quantified = [line for line, section in contexts if section in {"experience", "projects"} and _has_action(line) and _has_metric(line)]
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
        work_evidence = [line for line, section in contexts
                         if section in {"experience", "projects"} and _mentions(keyword, line) and _has_action(line)]
        if any(_has_metric(line) for line in work_evidence):
            strength = "strong"
        elif work_evidence:
            strength = "moderate"
        elif evidence:
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

    word_count = len(_tokens(resume))
    quality_feedback = _quality_feedback(
        resume,
        section_hits,
        bulletish,
        quantified,
        page_count,
        word_count,
    )

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
        "quality_feedback": quality_feedback,
        "page_count": page_count,
        "fonts": fonts,
        "font_sizes": font_sizes,
        "stats": {
            "lines": len(lines),
            "bullet_lines": len(bulletish),
            "quantified_lines": len(quantified),
            "action_lines": len(action_lines),
            "word_count": word_count,
        },
    }
