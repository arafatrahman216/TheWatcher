// Central place for API config
export const API_BASE_URL =
  (import.meta?.env && import.meta.env.VITE_API_BASE_URL) ||
  'http://localhost:8000/api/v1';
