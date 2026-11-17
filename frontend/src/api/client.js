import axios from 'axios';

// Get local date as YYYY-MM-DD
export const getLocalDateString = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach user's local date for proper timezone streak calculation
api.interceptors.request.use(
  (config) => {
    config.headers['X-Client-Date'] = getLocalDateString();
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
