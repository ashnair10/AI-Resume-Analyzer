from src.heuristics import analyze_heuristics


def test_role_evidence_analysis_finds_supported_skills():
    resume = """Summary
AI Engineer
Skills
Python Gemini Streamlit Docker
Experience
- Built AI automation using Python and Docker and reduced manual effort by 80%
Education
B.Tech
Projects
- Built a RAG assistant using Gemini and Streamlit"""
    jd = "We need an AI Engineer with Python, Gemini, Streamlit, Docker and RAG experience."
    result = analyze_heuristics(resume, jd, 1, [("Arial", 100)], [(11.0, 100)])

    assert result["requirement_coverage_score"] > 0
    assert result["role_evidence_score"] > 0
    assert result["evidence_strength_score"] > 0
    assert "python" in result["matched_keywords"]
    assert any(item["requirement"] == "python" and item["evidence"] for item in result["evidence_map"])


def test_missing_requirement_is_marked_missing():
    resume = """Summary
AI Engineer
Skills
Python
Experience
- Built Python APIs and improved processing time by 30%
Education
B.Tech
Projects
Automation platform"""
    jd = "Must have Python and Kubernetes experience."
    result = analyze_heuristics(resume, jd, 1, [("Arial", 100)], [(11.0, 100)])

    kubernetes = next(item for item in result["evidence_map"] if item["requirement"] == "kubernetes")
    assert kubernetes["status"] == "missing"
    assert not kubernetes["evidence"]


def test_skill_lists_and_dates_are_not_strong_evidence():
    resume = "Summary\nPython specialist since 2022\nSkills\nPython\nExperience\nEngineer | 2022 - 2026\n- Built APIs with FastAPI\n- Reduced document processing time by 30%\nEducation\nB.Tech 2022"
    result = analyze_heuristics(resume, "Python FastAPI", 0, [], [])
    evidence = {item["requirement"]: item for item in result["evidence_map"]}
    assert evidence["python"]["status"] == "weak"
    assert evidence["fastapi"]["status"] == "moderate"
    assert result["stats"]["quantified_lines"] == 1


def test_punctuation_skills_and_terminal_periods_match():
    result = analyze_heuristics("Skills\nC++\nExperience\n- Built services using C++ and Python.", "Need C++ and Python.", 0, [], [])
    evidence = {item["requirement"]: item for item in result["evidence_map"]}
    assert evidence["c++"]["status"] == "moderate"
    assert "python" in result["matched_keywords"]


def test_job_keywords_skip_generic_location_and_resume_prompt_words():
    from src.heuristics import top_job_keywords

    keywords = top_job_keywords(
        "Position in India: qualifications include working, building, and technical solutions. "
        "Need Python, cloud security, Kubernetes, and generative AI agents."
    )

    assert {"position", "india", "qualifications", "working", "building", "technical"}.isdisjoint(keywords)
    assert {"python", "cloud", "security", "kubernetes", "generative", "agents"} <= set(keywords)


def test_actionable_feedback_includes_wording_length_and_layout_guidance():
    resume = """Jordan Example
Skills
Python FastAPI
Experience
- Responsible for building internal tools
- built a service that supports document extraction, workflow review, and reliable processing for multiple internal teams across several business functions, including audit records, manager approval workflows, structured data validation, retry handling, and clear status notifications
"""
    result = analyze_heuristics(
        resume,
        "Seeking Python and FastAPI experience to build reliable document tools for a technical team.",
        0,
        [],
        [],
    )

    feedback = result["quality_feedback"]
    titles = {item["title"] for item in feedback}
    assert any(item["category"] == "Bullet clarity" for item in feedback)
    assert any(item["category"] == "Conciseness" for item in feedback)
    assert any(item["category"] == "Layout" for item in feedback)
    assert any(item["category"] == "Length" for item in feedback)
    assert result["stats"]["word_count"] > 0
    assert titles
