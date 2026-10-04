from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "techcv-api"


def test_cors_allows_localhost_and_loopback_frontend():
    response = TestClient(app).options(
        "/api/analyze",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-trace-id",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def make_resume(content: str) -> bytes:
    document = Document()
    for line in content.splitlines():
        document.add_paragraph(line)
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def test_analyze_upload_runs_resume_analysis_end_to_end():
    resume = make_resume(
        "Summary\nAI Engineer\nSkills\nPython Kubernetes\nExperience\n"
        "- Built Python APIs and reduced processing time by 30%\n"
        "Education\nB.Tech\nProjects\n- Developed a Kubernetes deployment"
    )
    response = TestClient(app).post(
        "/api/analyze",
        headers={"x-trace-id": "local-integration-test"},
        files={
            "resume": (
                "resume.docx",
                resume,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        data={
            "job_description": (
                "Seeking an AI Engineer with Python and Kubernetes experience to build "
                "production APIs, improve deployment reliability, and collaborate across teams."
            ),
            "use_ai": "false",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trace_id"] == "local-integration-test"
    assert body["document"]["file_type"] == "docx"
    assert body["analysis"]["role_evidence_score"] > 0
    assert "python" in body["analysis"]["matched_keywords"]
    assert any(item["requirement"] == "kubernetes" for item in body["analysis"]["evidence_map"])
    assert body["ai_review"] is None


def test_analyze_rejects_resume_without_extractable_text():
    response = TestClient(app).post(
        "/api/analyze",
        files={"resume": ("empty.docx", make_resume(""), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={
            "job_description": (
                "Seeking an AI Engineer with Python and Kubernetes experience to build "
                "production APIs, improve deployment reliability, and collaborate across teams."
            ),
            "use_ai": "false",
        },
    )

    assert response.status_code == 422
    assert "No extractable text" in response.json()["detail"]
