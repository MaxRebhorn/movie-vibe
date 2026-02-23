// Lade API-Version aus Umgebungsvariable oder use v1 als Default
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';
export const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Dynamischer API-Base-Path mit Version
const API_BASE_PATH = `/api/${API_VERSION}`;

// Helper function to get CSRF token from browser cookies
function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue || '';
}

// Ensure CSRF cookie exists in the browser
async function ensureCSRF() {
  if (!getCSRFToken()) {
    await fetch(`${BASE_URL}/api/get-csrf/`, {
      credentials: 'include',
    });
  }
}

// Generic fetch function with automatic CSRF handling
async function apiFetch(endpoint, options = {}) {
  await ensureCSRF();

  // Entferne mögliches doppeltes /api/ im endpoint
  const cleanEndpoint = endpoint.replace(/^\/?api\//, '');
  const url = `${BASE_URL}${API_BASE_PATH}/${cleanEndpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    credentials: 'include', // include cookies for session
    ...options,
  };

  console.log(`🌐 API Request: ${url}`); // Debug-Log

  const response = await fetch(url, config);

  if (!response.ok) {
    // Try to parse JSON error response
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth-related API calls
export const authAPI = {
  login: (credentials) =>
    apiFetch('users/login/', { method: 'POST', body: JSON.stringify(credentials) }),

  register: (userData) =>
    apiFetch('users/register/', { method: 'POST', body: JSON.stringify(userData) }),

  // JWT Token endpoints
  getToken: (credentials) =>
    apiFetch('auth/token/', { method: 'POST', body: JSON.stringify(credentials) }),

  refreshToken: (refreshToken) =>
    apiFetch('auth/token/refresh/', { 
      method: 'POST', 
      body: JSON.stringify({ refresh: refreshToken }) 
    }),

  logout: () =>
    apiFetch('users/logout/', { method: 'POST' }),

  checkAuth: () =>
    apiFetch('users/check-auth/'),
};

// Movie-related API calls
export const movieAPI = {
  getAll: () =>
    apiFetch('movies/'),

  search: (query) =>
    apiFetch(`movies/search/?q=${encodeURIComponent(query)}`),

  getMovie: (id) =>
    apiFetch(`movies/${id}/`),

  getSimilarMovies: (id) =>
    apiFetch(`movies/${id}/similar/`),

  create: (movieData) =>
    apiFetch('movies/', { 
      method: 'POST', 
      body: JSON.stringify(movieData) 
    }),
};

export const recommendationAPI = {
    getRecommendations: () => apiFetch('users/recommendations/')
};

// Favorite movies API calls
export const favoriteAPI = {
    getFavorites: () => apiFetch('users/favorites/'),
    toggleFavorite: (movieId) => apiFetch('users/favorites/', {
        method: 'POST',
        body: JSON.stringify({ movie_id: movieId }),
    }),
    checkFavorite: (movieId) => apiFetch(`users/favorites/check/${movieId}/`)
};

// Questionnaire-related API calls
export const questionnaireAPI = {
  submitQuestionnaire: (movieId, payload) =>
    apiFetch(`movies/${movieId}/review`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  getQuestionnaire: (movieId) =>
    apiFetch(`movies/${movieId}/review`),
};

// Version info (optional)
export const getApiVersion = () => {
  return {
    version: API_VERSION,
    basePath: API_BASE_PATH,
    fullBaseUrl: `${BASE_URL}${API_BASE_PATH}`
  };
};