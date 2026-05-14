"""
AI service: resume parsing and question generation using Claude (Anthropic API).
"""

import os
import re
import anthropic

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-20250514"


def parse_resume(resume_text: str) -> dict:
    """Extract structured info from raw resume text."""
    msg = _client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""Extract structured information from this resume. 
Return ONLY valid JSON with keys: skills (list), technologies (list), experience_years (int or null), domains (list), education (string).

Resume:
{resume_text[:3000]}"""
        }]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        import json
        return json.loads(raw)
    except Exception:
        return {"skills": [], "technologies": [], "experience_years": None, "domains": [], "education": ""}


def generate_question(
    role: str,
    resume_info: dict,
    context_chunks: list[str],
    previous_qa: list[dict],
    question_index: int,
) -> str:
    """Generate the next interview question."""
    context_str = "\n---\n".join(context_chunks) if context_chunks else "No specific context retrieved."
    history_str = ""
    for qa in previous_qa[-3:]:
        history_str += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"

    difficulty = "foundational" if question_index < 2 else ("intermediate" if question_index < 4 else "advanced")

    prompt = f"""You are conducting a technical interview for a {role} position.

Candidate background:
- Skills: {', '.join(resume_info.get('skills', [])[:8])}
- Technologies: {', '.join(resume_info.get('technologies', [])[:8])}
- Domains: {', '.join(resume_info.get('domains', [])[:5])}
- Experience: {resume_info.get('experience_years', 'unknown')} years

Knowledge base context to draw from:
{context_str[:1500]}

Previous interview exchange:
{history_str if history_str else "This is the first question."}

Generate ONE {difficulty} interview question (question #{question_index + 1}).
- It must be grounded in the context above
- Tailor it to the candidate's background
- Be specific, not generic
- Do NOT number it or add any prefix — just the question text."""

    msg = _client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def generate_summary(role: str, resume_info: dict, qa_records: list[dict]) -> dict:
    """Generate a structured evaluation summary."""
    qa_text = ""
    for i, qa in enumerate(qa_records, 1):
        qa_text += f"Q{i}: {qa['question']}\nA: {qa['answer']}\n\n"

    prompt = f"""You evaluated a candidate for a {role} role.

Candidate skills: {', '.join(resume_info.get('skills', []))}

Interview transcript:
{qa_text}

Return ONLY valid JSON with these keys:
- overall_rating: integer 1-10
- strengths: list of 2-3 strings
- areas_for_improvement: list of 2-3 strings  
- recommendation: one of "Strong Hire", "Hire", "Maybe", "No Hire"
- summary: 2-3 sentence paragraph"""

    msg = _client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        import json
        return json.loads(raw)
    except Exception:
        return {
            "overall_rating": 5,
            "strengths": ["Participated in interview"],
            "areas_for_improvement": ["More detail needed"],
            "recommendation": "Maybe",
            "summary": "Evaluation could not be fully parsed."
        }


def build_rag_query(role: str, resume_info: dict, question_index: int) -> str:
    """Build a targeted query for RAG retrieval based on role + resume."""
    skills = resume_info.get("skills", [])[:4]
    domains = resume_info.get("domains", [])[:3]
    topics = {
        0: "fundamentals core concepts",
        1: "algorithms data structures",
        2: "system design architecture",
        3: "advanced optimization",
        4: "best practices trade-offs",
    }
    topic = topics.get(question_index, "advanced concepts")
    return f"{role} {topic} {' '.join(skills)} {' '.join(domains)}"
