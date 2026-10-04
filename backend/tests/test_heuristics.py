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
