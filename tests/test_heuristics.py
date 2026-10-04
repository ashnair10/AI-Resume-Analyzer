from src.heuristics import analyze_heuristics


def test_resume_with_matching_skills_scores_keywords():
    resume = """Summary\nAI Engineer\nSkills\nPython Gemini Streamlit Docker\nExperience\n- Built AI automation and reduced manual effort by 80%\nEducation\nB.Tech\nProjects\nRAG assistant"""
    jd = "We need an AI Engineer with Python, Gemini, Streamlit, Docker and RAG experience."
    result = analyze_heuristics(resume, jd, 1, [("Arial", 100)], [(11.0, 100)])
    assert result["keyword_score"] > 0
    assert result["ats_score"] > 0
    assert "python" in result["matched_keywords"]
