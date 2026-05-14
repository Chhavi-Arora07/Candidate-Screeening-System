# AI Candidate Screening System

An AI-powered technical interview platform using RAG (Retrieval-Augmented Generation) to generate personalized questions based on the candidate's resume and selected role.

## Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────────────────────┐
│   React Frontend│ ────────────► │   FastAPI Backend                │
│   (port 3000)   │              │   ├── /api/sessions  (lifecycle) │
└─────────────────┘              │   ├── /api/interview (Q&A flow)  │
                                 │   └── /api/knowledge (RAG ingest) │
                                 │                                    │
                                 │   Services:                        │
                                 │   ├── rag.py   (chunk+retrieve)   │
                                 │   └── ai.py    (Claude API calls) │
                                 │                                    │
                                 │   Storage:                         │
                                 │   ├── SQLite   (sessions, Q&A)    │
                                 │   └── .txt files (knowledge base) │
                                 └──────────────────────────────────┘
```

## Key Design Decisions

- **RAG**: Text chunks (400 words, 80 overlap) with keyword scoring (or sentence-transformers if installed). Knowledge base is role-specific `.txt` files.
- **Question generation**: Claude generates contextually grounded, difficulty-ramped questions using resume info + retrieved context.
- **Storage**: SQLite for simplicity; sessions and Q&A are persisted with full traceability.
- **5 questions per interview**: Difficulty escalates from foundational → intermediate → advanced.

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key

### Backend

```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000

## Knowledge Base

Role-specific knowledge is in `backend/knowledge_base/`. Seed files are included for all 4 roles. To add books from the assignment:

1. Go to `/api/knowledge/upload` (or add a UI upload)
2. POST with `role` and `file` (PDF or TXT)

To enable semantic embeddings (better retrieval), install:
```bash
pip install sentence-transformers numpy
```
The system auto-detects and uses them if available.

## Flow

1. Candidate uploads resume (PDF or TXT) + selects role
2. Backend parses resume via Claude → extracts skills, tech, domains
3. For each question: RAG retrieves relevant context → Claude generates tailored question
4. After 5 questions: Claude generates structured evaluation report
5. Results page shows score, recommendation, strengths, and full transcript

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/sessions/roles | List available roles |
| POST | /api/sessions/start | Start session (multipart: name, role, resume) |
| GET | /api/interview/{id}/question | Get next question |
| POST | /api/interview/{id}/answer | Submit answer |
| POST | /api/sessions/{id}/complete | Generate evaluation |
| POST | /api/knowledge/upload | Upload knowledge doc |
| GET | /api/knowledge/status | Check knowledge base |
