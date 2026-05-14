from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sessions, interview, knowledge

app = FastAPI(title="AI Screening System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])

@app.get("/health")
def health():
    return {"status": "ok"}
