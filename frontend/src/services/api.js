import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT, STORAGE_KEYS } from '../utils/constants';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data on unauthorized
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============= AUTH ENDPOINTS =============

export const authService = {
  signup: async (username, email, password, phone) => {
    const response = await api.post('/api/auth/signup', {
      username,
      email,
      password,
      phone,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/api/auth/profile');
    return response.data;
  },
};

// ============= RINDM ENDPOINTS =============

export const rindmService = {
  getRecommendations: async (n, p, k, ph, latitude, longitude) => {
    const response = await api.post('/api/rindm/get-recommendations', {
      N: n,
      P: p,
      K: k,
      ph,
      latitude,
      longitude,
    });
    return response.data;
  },

  startCycle: async (recommendationId, selectedCrop, soilType) => {
    const response = await api.post('/api/rindm/start-cycle', {
      recommendation_id: recommendationId,
      selected_crop: selectedCrop,
      soil_type: soilType,
    });
    return response.data;
  },

  getActiveCycle: async () => {
    const response = await api.get('/api/rindm/active-cycle');
    return response.data;
  },

  getCycleStatus: async (cycleId) => {
    const response = await api.get(`/api/rindm/cycle-status/${cycleId}`);
    return response.data;
  },

  completeCycle: async (cycleId) => {
    const response = await api.post(`/api/rindm/complete-cycle/${cycleId}`, {});
    return response.data;
  },

  getCycleHistory: async () => {
    const response = await api.get('/api/rindm/history');
    return response.data;
  },

  checkWeather: async (cycleId) => {
    const response = await api.post(`/api/rindm/check-weather/${cycleId}`, {});
    return response.data;
  },
};

// ============= QUICK RECOMMENDATION (NO AUTH) =============

export const recommendationService = {
  getQuickRecommendation: async (n, p, k, ph, latitude, longitude) => {
    const response = await api.post('/api/predict', {
      N: n,
      P: p,
      K: k,
      ph,
      latitude,
      longitude,
    });
    return response.data;
  },
};

// ============= PLANNING ENDPOINTS (Phase 3) =============

export const planningService = {
  // Compare crops using hybrid LSTM + Formula prediction
  compareCrops: async (N, P, K, soilType, seasonIndex = 0, expectedRainfallMm = 600, candidateCrops = ['rice', 'wheat', 'maize']) => {
    const response = await api.post('/api/planning/compare-crops', {
      N,
      P,
      K,
      soil_type: soilType,
      season_index: seasonIndex,
      expected_rainfall_mm: expectedRainfallMm,
      candidate_crops: candidateCrops,
    });
    return response.data;
  },

  // Monte Carlo profit risk analysis
  profitRiskReport: async (N, P, K, soilType, expectedRainfallMm = 600, candidateCrops = ['rice', 'wheat', 'maize'], rainfallUncertainty = 0.20, priceUncertainty = 0.15) => {
    const response = await api.post('/api/planning/profit-risk-report', {
      N,
      P,
      K,
      soil_type: soilType,
      expected_rainfall_mm: expectedRainfallMm,
      candidate_crops: candidateCrops,
      rainfall_uncertainty_pct: rainfallUncertainty,
      price_uncertainty_pct: priceUncertainty,
    });
    return response.data;
  },

  // Q-Learning seasonal rotation plan
  seasonalRotationPlan: async (N, P, K, soilType, expectedRainfallMm = 600, seasonIndex = 0, numSeasons = 5) => {
    const response = await api.post('/api/planning/seasonal-rotation-plan', {
      N,
      P,
      K,
      soil_type: soilType,
      expected_rainfall_mm: expectedRainfallMm,
      season_index: seasonIndex,
      num_seasons: numSeasons,
    });
    return response.data;
  },

  // Get farmer's financial history
  getFinancialHistory: async () => {
    const response = await api.get('/api/planning/financial-history');
    return response.data;
  },
};

// ============= ERROR HANDLING UTILITY =============

export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const data = error.response.data;

    if (status === 400) {
      return data.message || 'Invalid request. Please check your input.';
    } else if (status === 401) {
      return 'Unauthorized. Please login again.';
    } else if (status === 403) {
      return 'Forbidden. You do not have permission to access this resource.';
    } else if (status === 404) {
      return 'Resource not found.';
    } else if (status === 409) {
      return data.message || 'This resource already exists.';
    } else if (status >= 500) {
      return 'Server error. Please try again later.';
    }
    return data.message || 'An error occurred. Please try again.';
  } else if (error.request) {
    // Request made but no response received
    return 'No response from server. Please check your connection.';
  } else {
    // Error in request setup
    return error.message || 'An error occurred.';
  }
};

export default api;
