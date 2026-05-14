from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import create_session, get_session, get_session_qa, complete_session
from services.ai import parse_resume, generate_summary

router = APIRouter()

ROLES = ["AI/ML Engineer", "Backend Engineer", "Data Scientist", "Full Stack Engineer"]


@router.get("/roles")
def list_roles():
    return {"roles": ROLES}


@router.post("/start")
async def start_session(
    candidate_name: str = Form(...),
    role: str = Form(...),
    resume: UploadFile = File(...)
):
    if role not in ROLES:
        raise HTTPException(400, f"Invalid role. Choose from: {ROLES}")
    content = await resume.read()
    # Handle PDF or plain text
    if resume.filename.endswith(".pdf"):
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(content))
            resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            resume_text = content.decode("utf-8", errors="ignore")
    else:
        resume_text = content.decode("utf-8", errors="ignore")

    resume_info = parse_resume(resume_text)
    import json
    session = create_session(candidate_name, role, json.dumps({
        "raw": resume_text[:5000],
        "parsed": resume_info
    }))
    return {"session_id": session["id"], "resume_info": resume_info, "role": role}


@router.get("/{session_id}")
def get_session_detail(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session


@router.post("/{session_id}/complete")
def finish_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    import json
    resume_data = json.loads(session["resume_text"])
    qa_records = get_session_qa(session_id)
    summary = generate_summary(session["role"], resume_data.get("parsed", {}), qa_records)
    complete_session(session_id)
    return {"summary": summary, "qa_records": qa_records}
