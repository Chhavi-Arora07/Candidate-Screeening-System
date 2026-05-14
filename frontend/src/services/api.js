const BASE = '';

export const api = {
  async getRoles() {
    const r = await fetch(`${BASE}/api/sessions/roles`);
    return r.json();
  },

  async startSession(formData) {
    const r = await fetch(`${BASE}/api/sessions/start`, { method: 'POST', body: formData });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },

  async getQuestion(sessionId) {
    const r = await fetch(`${BASE}/api/interview/${sessionId}/question`);
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },

  async submitAnswer(sessionId, answer) {
    const r = await fetch(`${BASE}/api/interview/${sessionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer }),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },

  async completeSession(sessionId) {
    const r = await fetch(`${BASE}/api/sessions/${sessionId}/complete`, { method: 'POST' });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },

  async uploadKnowledge(role, file) {
    const fd = new FormData();
    fd.append('role', role);
    fd.append('file', file);
    const r = await fetch(`${BASE}/api/knowledge/upload`, { method: 'POST', body: fd });
    return r.json();
  },

  async knowledgeStatus() {
    const r = await fetch(`${BASE}/api/knowledge/status`);
    return r.json();
  }
};
