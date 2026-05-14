import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "screening.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            candidate_name TEXT,
            role TEXT,
            resume_text TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS qa_records (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            question TEXT,
            answer TEXT,
            context_used TEXT,
            question_index INTEGER,
            created_at TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    """)
    conn.commit()
    conn.close()

def create_session(candidate_name: str, role: str, resume_text: str) -> dict:
    conn = get_db()
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, candidate_name, role, resume_text, "active", now)
    )
    conn.commit()
    conn.close()
    return {"id": session_id, "candidate_name": candidate_name, "role": role, "status": "active", "created_at": now}

def save_qa(session_id: str, question: str, answer: str, context: str, index: int):
    conn = get_db()
    conn.execute(
        "INSERT INTO qa_records VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), session_id, question, answer, context, index, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_session(session_id: str) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_session_qa(session_id: str) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM qa_records WHERE session_id = ? ORDER BY question_index",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def complete_session(session_id: str):
    conn = get_db()
    conn.execute("UPDATE sessions SET status = 'completed' WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

init_db()
