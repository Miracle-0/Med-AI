import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const textbookAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/textbooks/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 600000, // 10 minutes for large files
    });
  },
  parse: (id) => api.post(`/textbooks/${id}/parse`, null, { timeout: 300000 }),
  list: () => api.get('/textbooks/'),
  get: (id) => api.get(`/textbooks/${id}`),
  delete: (id) => api.delete(`/textbooks/${id}`),
  getChapters: (id) => api.get(`/textbooks/${id}/chapters`),
};

export const graphAPI = {
  extract: (textbookId) => api.post(`/graph/extract/${textbookId}`),
  getNodes: (textbookId) => api.get('/graph/nodes', { params: { textbook_id: textbookId } }),
  getEdges: (textbookId) => api.get('/graph/edges', { params: { textbook_id: textbookId } }),
  merge: () => api.post('/graph/merge'),
  getDecisions: () => api.get('/graph/decisions'),
};

export const ragAPI = {
  buildIndex: (textbookId) => api.post('/rag/index', null, { params: { textbook_id: textbookId } }),
  query: (query) => api.post('/rag/query', { query }),
  getStatus: () => api.get('/rag/status'),
};

export const chatAPI = {
  sendMessage: (message, sessionId = 'default') =>
    api.post('/chat/message', { message, session_id: sessionId }),
  getHistory: (sessionId = 'default') =>
    api.get('/chat/history', { params: { session_id: sessionId } }),
};

export const pipelineAPI = {
  run: (paths) => api.post('/pipeline/run', paths),
};

export default api;
