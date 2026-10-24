/**
 * Source2Study - Centralized API Service Layer
 * Fully connected with FastAPI backend routes.
 */

// Use relative URL by default so it works seamlessly in development (via Vite proxy)
// and production (served by FastAPI at /app), or honor VITE_API_BASE if specified.
const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      errorDetail = err.detail || err.message || JSON.stringify(err);
    } catch {
      try {
        const text = await res.text();
        if (text) errorDetail = text;
      } catch {
        // use default HTTP error
      }
    }
    throw new Error(errorDetail);
  }
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return res.json();
  }
  return res.text();
}

export const api = {
  // ----------------------------------------------------
  // Health & Overview
  // ----------------------------------------------------
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  async getDashboardOverview() {
    const res = await fetch(`${API_BASE}/dashboard/overview`);
    return handleResponse(res);
  },

  // ----------------------------------------------------
  // Resources Management
  // ----------------------------------------------------
  async listResources() {
    const res = await fetch(`${API_BASE}/resources`);
    return handleResponse(res);
  },

  async getResource(resourceId) {
    const res = await fetch(`${API_BASE}/resources/${encodeURIComponent(resourceId)}`);
    return handleResponse(res);
  },

  async uploadResources(files) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const res = await fetch(`${API_BASE}/resources/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async addYoutube(url) {
    const res = await fetch(`${API_BASE}/resources/youtube`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.trim() }),
    });
    return handleResponse(res);
  },

  async addWeb(url) {
    const res = await fetch(`${API_BASE}/resources/web`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.trim() }),
    });
    return handleResponse(res);
  },

  async deleteResource(resourceId) {
    const res = await fetch(`${API_BASE}/resources/${encodeURIComponent(resourceId)}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // ----------------------------------------------------
  // AI Chat & Conversations
  // ----------------------------------------------------
  async listConversations(userId = 'student_user') {
    const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    const res = await fetch(`${API_BASE}/chat/conversations${query}`);
    return handleResponse(res);
  },

  async getConversation(conversationId) {
    const res = await fetch(`${API_BASE}/chat/conversation/${encodeURIComponent(conversationId)}`);
    return handleResponse(res);
  },

  async createConversation(userId = 'student_user', title = 'New Study Session', resourceId = null) {
    const res = await fetch(`${API_BASE}/chat/conversation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        title: title.trim(),
        resource_id: resourceId,
      }),
    });
    return handleResponse(res);
  },

  async renameConversation(conversationId, title) {
    const res = await fetch(`${API_BASE}/chat/conversation/${encodeURIComponent(conversationId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title.trim() }),
    });
    return handleResponse(res);
  },

  async deleteConversation(conversationId) {
    const res = await fetch(`${API_BASE}/chat/conversation/${encodeURIComponent(conversationId)}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  async sendMessage(conversationId, question, topK = 5) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: conversationId,
        question: question.trim(),
        top_k: Number(topK),
      }),
    });
    return handleResponse(res);
  },

  // ----------------------------------------------------
  // AI Learning Features (Summary, Explanations, Quizzes, Answer Evaluation)
  // ----------------------------------------------------
  async summarize(query = 'Summarize key concepts', topK = 5, resourceId = null) {
    const res = await fetch(`${API_BASE}/ai/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query.trim(),
        top_k: Number(topK),
        resource_id: resourceId,
      }),
    });
    return handleResponse(res);
  },

  async explain(topic, style = 'standard', topK = 5, resourceId = null) {
    const res = await fetch(`${API_BASE}/ai/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic.trim(),
        style,
        top_k: Number(topK),
        resource_id: resourceId,
      }),
    });
    return handleResponse(res);
  },

  async generateQuiz(topic = null, numberOfQuestions = 5, difficulty = 'medium', topK = 5, resourceId = null) {
    const res = await fetch(`${API_BASE}/quiz/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic ? topic.trim() : null,
        number_of_questions: Number(numberOfQuestions),
        difficulty,
        top_k: Number(topK),
        resource_id: resourceId,
      }),
    });
    return handleResponse(res);
  },

  async generateMCQ(topic = null, numberOfQuestions = 5, difficulty = 'medium', topK = 5, resourceId = null) {
    const res = await fetch(`${API_BASE}/quiz/mcq`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic ? topic.trim() : null,
        number_of_questions: Number(numberOfQuestions),
        difficulty,
        top_k: Number(topK),
        resource_id: resourceId,
      }),
    });
    return handleResponse(res);
  },

  async evaluateQuiz(questions, userAnswers) {
    const res = await fetch(`${API_BASE}/quiz/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        questions,
        user_answers: userAnswers,
      }),
    });
    return handleResponse(res);
  },

  async evaluateAnswer(question, studentAnswer, resourceId = null, referenceAnswer = null) {
    const res = await fetch(`${API_BASE}/ai/evaluate-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question.trim(),
        student_answer: studentAnswer.trim(),
        resource_id: resourceId,
        reference_answer: referenceAnswer,
      }),
    });
    return handleResponse(res);
  },

  // ----------------------------------------------------
  // Question Bank & Deduplication
  // ----------------------------------------------------
  async getStats() {
    const res = await fetch(`${API_BASE}/question-bank/stats`);
    return handleResponse(res);
  },

  async getPapers() {
    const res = await fetch(`${API_BASE}/question-bank/papers`);
    return handleResponse(res);
  },

  async uploadPapers(files) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const res = await fetch(`${API_BASE}/question-bank/upload-and-extract`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async getQuestionBank({
    status = 'unique',
    search = '',
    paper = '',
    topic = '',
    skip = 0,
    limit = 100,
  } = {}) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    if (paper) params.append('paper_name', paper);
    if (topic) params.append('topic', topic);
    params.append('skip', skip);
    params.append('limit', limit);

    const res = await fetch(`${API_BASE}/question-bank?${params.toString()}`);
    return handleResponse(res);
  },

  async getDuplicateCandidates() {
    const res = await fetch(`${API_BASE}/question-bank/duplicates`);
    return handleResponse(res);
  },

  async mergeQuestions({ canonicalId, duplicateIds, chosenText }) {
    const res = await fetch(`${API_BASE}/question-bank/duplicates/merge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        canonical_id: canonicalId,
        duplicate_ids: duplicateIds,
        chosen_canonical_text: chosenText,
      }),
    });
    return handleResponse(res);
  },

  async separateQuestion(questionId) {
    const res = await fetch(`${API_BASE}/question-bank/duplicates/separate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: questionId }),
    });
    return handleResponse(res);
  },

  getExportUrl(format = 'csv') {
    return `${API_BASE}/question-bank/export?format=${format}`;
  },
};
