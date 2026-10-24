const API_BASE = 'http://localhost:8000';

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = 'Request failed';
    try {
      const err = await res.json();
      errorDetail = err.detail || JSON.stringify(err);
    } catch {
      errorDetail = await res.text();
    }
    throw new Error(errorDetail || `HTTP error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Question Bank
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

  async getQuestionBank({ status = 'unique', search = '', paper = '', topic = '', skip = 0, limit = 100 } = {}) {
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

  // Resources
  async listResources() {
    const res = await fetch(`${API_BASE}/resources`);
    return handleResponse(res);
  },

  async uploadResources(files) {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
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
      body: JSON.stringify({ url }),
    });
    return handleResponse(res);
  },

  async addWeb(url) {
    const res = await fetch(`${API_BASE}/resources/web`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    return handleResponse(res);
  },

  // Chat
  async createConversation(userId = 'student_user', title = 'Study Session') {
    const res = await fetch(`${API_BASE}/chat/conversation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, title }),
    });
    return handleResponse(res);
  },

  async listConversations(userId = 'student_user') {
    const res = await fetch(`${API_BASE}/chat/conversations?user_id=${userId}`);
    return handleResponse(res);
  },

  async getConversation(id) {
    const res = await fetch(`${API_BASE}/chat/conversation/${id}`);
    return handleResponse(res);
  },

  async sendMessage(conversationId, question, topK = 5) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: conversationId,
        question,
        top_k: topK,
      }),
    });
    return handleResponse(res);
  },

  // Learning features
  async summarize(query) {
    const res = await fetch(`${API_BASE}/ai/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    return handleResponse(res);
  },

  async explain(topic) {
    const res = await fetch(`${API_BASE}/ai/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    });
    return handleResponse(res);
  },

  async generateQuiz(topic, numberOfQuestions = 3, difficulty = 'medium') {
    const res = await fetch(`${API_BASE}/quiz/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, number_of_questions: numberOfQuestions, difficulty }),
    });
    return handleResponse(res);
  },

  async generateMCQ(topic, numberOfQuestions = 3, difficulty = 'medium') {
    const res = await fetch(`${API_BASE}/quiz/mcq`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, number_of_questions: numberOfQuestions, difficulty }),
    });
    return handleResponse(res);
  },

  async evaluateQuiz(questions, userAnswers) {
    const res = await fetch(`${API_BASE}/quiz/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ questions, user_answers: userAnswers }),
    });
    return handleResponse(res);
  },
};
