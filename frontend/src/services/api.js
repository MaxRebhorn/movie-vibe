
export const BASE_URL = process.env.REACT_APP_API_BASE_URL;

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
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'include', // Important for cookies/sessions
      ...options,
    };

    const response = await fetch(url, config);

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

// Auth-related API calls
export const authAPI = {
  login: (credentials) => {
    return apiFetch('/api/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  register: (userData) => {
    return apiFetch('/api/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  logout: () => {
    return apiFetch('/api/logout/', {
      method: 'POST',
    });
  },

  checkAuth: () => {
    return apiFetch('/api/check-auth/');
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