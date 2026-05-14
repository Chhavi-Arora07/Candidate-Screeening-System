"""
RAG service: chunks documents, embeds them, and retrieves relevant context.
Uses sentence-transformers for embeddings and FAISS for vector search.
Falls back to keyword matching if FAISS/transformers are not installed.
"""

import os
import re
import json
import math
from pathlib import Path
from typing import List, Tuple

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge_base"
KNOWLEDGE_DIR.mkdir(exist_ok=True)

# Try to import heavy ML deps; fall back to BM25-style retrieval
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    _USE_EMBEDDINGS = True
except Exception:
    _EMBED_MODEL = None
    _USE_EMBEDDINGS = False

_CHUNK_STORE: dict[str, list] = {}  # role -> list of {"text": ..., "embedding": ...}

ROLE_DOCS = {
    "AI/ML Engineer": ["ml_knowledge.txt"],
    "Backend Engineer": ["backend_knowledge.txt"],
    "Data Scientist": ["data_science_knowledge.txt"],
    "Full Stack Engineer": ["fullstack_knowledge.txt"],
}


def _chunk_text(text: str, size: int = 400, overlap: int = 80) -> List[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i: i + size])
        if chunk:
            chunks.append(chunk)
        i += size - overlap
    return chunks


def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-9)


def _keyword_score(query: str, chunk: str) -> float:
    q_words = set(re.findall(r"\w+", query.lower()))
    c_words = set(re.findall(r"\w+", chunk.lower()))
    if not q_words:
        return 0.0
    return len(q_words & c_words) / len(q_words)


def load_role_knowledge(role: str):
    """Load and chunk documents for a role into the in-memory store."""
    if role in _CHUNK_STORE:
        return
    docs = ROLE_DOCS.get(role, [])
    chunks = []
    for doc in docs:
        path = KNOWLEDGE_DIR / doc
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for chunk in _chunk_text(text):
                entry = {"text": chunk}
                if _USE_EMBEDDINGS:
                    entry["embedding"] = _EMBED_MODEL.encode(chunk).tolist()
                chunks.append(entry)
    _CHUNK_STORE[role] = chunks


def retrieve(role: str, query: str, top_k: int = 4) -> List[str]:
    """Return top_k relevant chunks for the given query."""
    load_role_knowledge(role)
    chunks = _CHUNK_STORE.get(role, [])
    if not chunks:
        return []

    if _USE_EMBEDDINGS and chunks[0].get("embedding"):
        import numpy as np
        q_emb = _EMBED_MODEL.encode(query).tolist()
        scored = [(c["text"], _cosine(q_emb, c["embedding"])) for c in chunks]
    else:
        scored = [(c["text"], _keyword_score(query, c["text"])) for c in chunks]

    scored.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in scored[:top_k] if _ > 0]


def ingest_text(role: str, text: str, filename: str = "custom"):
    """Ingest arbitrary text into the knowledge base for a role."""
    path = KNOWLEDGE_DIR / ROLE_DOCS.get(role, [f"{role.lower().replace(' ', '_')}_knowledge.txt"])[0]
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n" + text)
    # Invalidate cache
    _CHUNK_STORE.pop(role, None)
