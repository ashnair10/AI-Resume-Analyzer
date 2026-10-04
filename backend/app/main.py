from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from core.ai_gateway import analyze_resume_ai
from core.guardrails import inspect_input
from core.logging import configure_logging, get_logger
from core.telemetry import configure_telemetry
from src.extractor import extract_resume
from src.heuristics import analyze_heuristics
from app.builder_routes import router as builder_router

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
configure_logging()
logger = get_logger()

app = FastAPI(
    title="TechCV API",
    version="0.3.0",
    description="Evidence-first resume analysis API for developers and tech professionals.",
)

app.include_router(builder_router)

origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
configure_telemetry(app)


class Health(BaseModel):
    status: str
    service: str
    version: str


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", service="techcv-api", version="0.3.0")


@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    use_ai: bool = Form(True),
    x_trace_id: str | None = Header(default=None),
):
    started = time.perf_counter()
    trace_id = x_trace_id or uuid.uuid4().hex
    log = logger.bind(trace_id=trace_id, filename=resume.filename)

    if not resume.filename or not resume.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Upload a PDF or DOCX resume.")
    if len(job_description.strip()) < 80:
        raise HTTPException(400, "Paste a meaningful job description (at least 80 characters).")

    file_bytes = await resume.read(8 * 1024 * 1024 + 1)
    if len(file_bytes) > 8 * 1024 * 1024:
        raise HTTPException(413, "Resume exceeds the 8 MB local-demo limit.")

    try:
        doc = await run_in_threadpool(extract_resume, file_bytes, resume.filename)
    except Exception as exc:
        log.exception("resume_parse_failed")
        raise HTTPException(422, f"Could not parse resume: {exc}") from exc
    if not doc.text.strip():
        raise HTTPException(
            422,
            "No extractable text found. Scanned resumes need OCR before they can be analyzed.",
        )

    guardrail = inspect_input(job_description)
    result = analyze_heuristics(doc.text, job_description, doc.page_count, doc.fonts, doc.font_sizes)

    ai_payload = None
    ai_meta = {"enabled": False, "provider": "none", "model": None, "error": None}
    if use_ai:
        ai = await run_in_threadpool(analyze_resume_ai, doc.text, job_description, result)
        ai_payload = ai.review
        ai_meta = {"enabled": ai.enabled, "provider": ai.provider, "model": ai.model, "error": ai.error}

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    log.info(
        "resume_analysis_completed",
        duration_ms=duration_ms,
        role_evidence_score=result["role_evidence_score"],
        readiness=result["readiness"],
        pii_detected=guardrail.pii_detected,
        prompt_injection_signals=len(guardrail.prompt_injection_signals),
        ai_enabled=ai_meta["enabled"],
    )

    return {
        "trace_id": trace_id,
        "duration_ms": duration_ms,
        "document": {
            "filename": resume.filename,
            "file_type": doc.file_type,
            "page_count": doc.page_count,
        },
        "guardrails": {
            "pii_detected": guardrail.pii_detected,
            "pii_types": guardrail.pii_types,
            "prompt_injection_signals": guardrail.prompt_injection_signals,
        },
        "analysis": result,
        "ai": ai_meta,
        "ai_review": ai_payload,
    }
