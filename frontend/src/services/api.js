// src/services/api.js (Fixed endpoints)
const BASE_URL = 'http://localhost:8000';

// Helper function to get CSRF token for Django
function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  return cookieValue || '';
}

// Generic fetch function with error handling
async function apiFetch(endpoint, options = {}) {
  try {
    const url = `${BASE_URL}${endpoint}`;
    console.log('API Request:', url, options); // Debug log

    const config = {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'include', // Important for cookies/sessions
      ...options,
    };

    const response = await fetch(url, config);
    console.log('API Response:', response.status); // Debug log

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Auth-related API calls - FIXED ENDPOINTS
export const authAPI = {
  login: (credentials) => {
    return apiFetch('/api/login/', { // Added /api/ prefix
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  register: (userData) => {
    return apiFetch('/api/register/', { // Added /api/ prefix
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  logout: () => {
    return apiFetch('/api/logout/', { // Added /api/ prefix
      method: 'POST',
    });
  },

  checkAuth: () => {
    return apiFetch('/api/check-auth/'); // Added /api/ prefix
  },
};

// Movie-related API calls
export const movieAPI = {
  search: (query) => {
    return apiFetch(`/api/movies/search/?q=${encodeURIComponent(query)}`);
  },

  getMovie: (id) => {
    return apiFetch(`/api/movies/${id}/`);
  },

  getSimilarMovies: (id) => {
    return apiFetch(`/api/movies/${id}/similar/`);
  },
};