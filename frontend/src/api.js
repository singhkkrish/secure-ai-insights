import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // AI calls can take a while
});

// Request logging
api.interceptors.request.use((config) => {
  console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || 'Request failed';
    console.error(`[API Error] ${msg}`);
    return Promise.reject(new Error(msg));
  }
);

export const chatApi = {
  sendMessage: (message, conversationHistory = []) =>
    api.post('/chat/', { message, conversation_history: conversationHistory }),
  getSuggestedQuestions: () => api.get('/chat/suggested-questions'),
};

export const analyticsApi = {
  getOverviewStats: () => api.get('/analytics/overview-stats'),
  getTopTitles: (params = {}) => api.get('/analytics/top-titles', { params }),
  getGenreTrends: () => api.get('/analytics/genre-trends'),
  getRegionalHeatmap: (month) => api.get('/analytics/regional-heatmap', { params: month ? { month } : {} }),
  getMarketingEfficiency: () => api.get('/analytics/marketing-efficiency'),
  getAudienceSegments: () => api.get('/analytics/audience-segments'),
};

export const documentsApi = {
  listDocuments: () => api.get('/documents/'),
  searchDocuments: (q, top_k = 5) => api.get('/documents/search', { params: { q, top_k } }),
};

export default api;
