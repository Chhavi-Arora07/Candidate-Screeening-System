from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.rag import ingest_text, ROLE_DOCS, KNOWLEDGE_DIR

router = APIRouter()


@router.post("/upload")
async def upload_knowledge(role: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    if file.filename.endswith(".pdf"):
        try:
            import pypdf, io
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise HTTPException(400, f"PDF parsing failed: {e}")
    else:
        text = content.decode("utf-8", errors="ignore")

    ingest_text(role, text, file.filename)
    return {"status": "ingested", "role": role, "filename": file.filename, "chars": len(text)}


@router.get("/status")
def knowledge_status():
    status = {}
    for role, docs in ROLE_DOCS.items():
        status[role] = []
        for doc in docs:
            path = KNOWLEDGE_DIR / doc
            status[role].append({
                "file": doc,
                "exists": path.exists(),
                "size_kb": round(path.stat().st_size / 1024, 1) if path.exists() else 0
            })
    return status
