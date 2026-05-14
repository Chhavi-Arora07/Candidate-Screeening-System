from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import get_session, get_session_qa, save_qa, get_db
from services.ai import generate_question, build_rag_query
from services.rag import retrieve

router = APIRouter()
TOTAL_QUESTIONS = 5

class AnswerPayload(BaseModel):
    answer: str

def _ensure_pending_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_questions (
            session_id TEXT PRIMARY KEY,
            question TEXT,
            context TEXT,
            question_index INTEGER
        )
    """)
    conn.commit()
    conn.close()

_ensure_pending_table()

def _get_pending(session_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM pending_questions WHERE session_id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def _set_pending(session_id, question, context, index):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO pending_questions VALUES (?, ?, ?, ?)",
                 (session_id, question, context, index))
    conn.commit()
    conn.close()

def _clear_pending(session_id):
    conn = get_db()
    conn.execute("DELETE FROM pending_questions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

@router.get("/{session_id}/question")
def get_next_question(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session["status"] == "completed":
        raise HTTPException(400, "Session already completed")

    qa_records = get_session_qa(session_id)
    question_index = len(qa_records)

    if question_index >= TOTAL_QUESTIONS:
        return {"done": True, "question": None, "question_index": question_index}

    pending = _get_pending(session_id)
    if pending and pending["question_index"] == question_index:
        return {"done": False, "question": pending["question"],
                "question_index": question_index, "total": TOTAL_QUESTIONS,
                "context_retrieved": bool(pending["context"])}

    resume_data = json.loads(session["resume_text"])
    resume_info = resume_data.get("parsed", {})
    role = session["role"]

    query = build_rag_query(role, resume_info, question_index)
    context_chunks = retrieve(role, query, top_k=4)
    context_str = " | ".join(context_chunks[:2])

    question = generate_question(role, resume_info, context_chunks, qa_records, question_index)
    _set_pending(session_id, question, context_str, question_index)

    return {"done": False, "question": question, "question_index": question_index,
            "total": TOTAL_QUESTIONS, "context_retrieved": len(context_chunks) > 0}

@router.post("/{session_id}/answer")
def submit_answer(session_id: str, payload: AnswerPayload):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    pending = _get_pending(session_id)
    if not pending:
        raise HTTPException(400, "No active question. Call GET /question first.")

    save_qa(session_id, pending["question"], payload.answer, pending["context"], pending["question_index"])
    _clear_pending(session_id)

    next_index = pending["question_index"] + 1
    return {"saved": True, "question_index": pending["question_index"], "done": next_index >= TOTAL_QUESTIONS}
