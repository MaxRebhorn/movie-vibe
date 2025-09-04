export const BASE_URL = process.env.REACT_APP_API_BASE_URL;

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

  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    credentials: 'include', // include cookies for session
    ...options,
  };

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
    apiFetch('/api/login/', { method: 'POST', body: JSON.stringify(credentials) }),

  register: (userData) =>
    apiFetch('/api/register/', { method: 'POST', body: JSON.stringify(userData) }),

  logout: () =>
    apiFetch('/api/logout/', { method: 'POST' }),

  checkAuth: () =>
    apiFetch('/api/check-auth/'),
};

// Movie-related API calls
export const movieAPI = {
  search: (query) =>
    apiFetch(`/api/movies/search/?q=${encodeURIComponent(query)}`),

  getMovie: (id) =>
    apiFetch(`/api/movies/${id}/`),

  getSimilarMovies: (id) =>
    apiFetch(`/api/movies/${id}/similar/`),
};

// Favorite movies API calls
export const favoriteAPI = {
    getFavorites: () => apiFetch('/api/favorites/'),
    toggleFavorite: (movieId) => apiFetch('/api/favorites/', {
        method: 'POST',
        body: JSON.stringify({ movie_id: movieId }),
    }),
    checkFavorite: (movieId) => apiFetch(`/api/favorites/check/${movieId}/`)
};

// Questionnaire-related API calls
export const questionnaireAPI = {
  submitQuestionnaire: (movieId, payload) =>
    apiFetch(`/api/movies/${movieId}/review/`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  getQuestionnaire: (movieId) =>
    apiFetch(`/api/movies/${movieId}/review/`),
};
