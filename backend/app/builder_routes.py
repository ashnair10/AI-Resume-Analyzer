from functools import partial
import subprocess

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from core.ai_gateway import analyze_resume_ai
from src.extractor import extract_resume
from src.heuristics import analyze_heuristics
from src.resume_builder import ResumeExport, build_bundle, build_docx, filename_stem

router = APIRouter(prefix="/api/resume", tags=["Resume builder"])


@router.post("/import")
async def import_resume(resume: UploadFile = File(...)):
    if not resume.filename or not resume.filename.lower().endswith((".docx", ".pdf")):
        raise HTTPException(400, "Upload a PDF or DOCX resume.")
    data = await resume.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(413, "Resume exceeds the 8 MB limit.")
    try:
        document = await run_in_threadpool(extract_resume, data, resume.filename)
    except Exception:
        raise HTTPException(422, "Could not read this file. Upload a valid PDF or DOCX.")
    if not document.text.strip():
        raise HTTPException(422, "No extractable text. Scanned PDFs need OCR first.")
    return {"content": document.text, "note": "Text imported. Original layout is not preserved; check headings and reading order."}


class ReviewRequest(BaseModel):
    content: str = Field(min_length=40, max_length=40000)
    job_description: str = Field(min_length=80, max_length=20000)
    use_ai: bool = False


@router.post("/review")
async def review_resume(request: ReviewRequest):
    result = analyze_heuristics(request.content, request.job_description, 0, [], [])
    ai = None
    if request.use_ai:
        ai = await run_in_threadpool(analyze_resume_ai, request.content, request.job_description, result)
    return {"analysis": result, "ai_review": ai.review if ai else None,
            "ai_error": ai.error if ai else None,
            "ai_enabled": ai.enabled if ai else False}


@router.post("/export")
async def export_resume(request: ResumeExport, format: str = "bundle"):
    if format not in {"bundle", "docx"}:
        raise HTTPException(400, "Choose bundle or docx.")
    if not request.reviewed:
        raise HTTPException(400, "Review the resume and confirm its facts before exporting.")
    try:
        content = await run_in_threadpool(partial(build_bundle if format == "bundle" else build_docx, request))
    except (RuntimeError, subprocess.SubprocessError, OSError):
        raise HTTPException(503, "PDF conversion unavailable. Install LibreOffice or use Docker Compose. You can still download DOCX.")
    extension = "zip" if format == "bundle" else "docx"
    media = "application/zip" if format == "bundle" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return Response(content, media_type=media, headers={
        "Content-Disposition": f'attachment; filename="{filename_stem(request.company, request.role)}.{extension}"',
        "Cache-Control": "no-store",
    })
