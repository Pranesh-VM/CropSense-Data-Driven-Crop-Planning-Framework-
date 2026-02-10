// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
export const API_TIMEOUT = 10000; // 10 seconds

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    SIGNUP: `${API_BASE_URL}/api/auth/signup`,
    LOGIN: `${API_BASE_URL}/api/auth/login`,
  },
  RINDM: {
    GET_RECOMMENDATIONS: `${API_BASE_URL}/api/rindm/get-recommendations`,
    START_CYCLE: `${API_BASE_URL}/api/rindm/start-cycle`,
    ACTIVE_CYCLE: `${API_BASE_URL}/api/rindm/active-cycle`,
    CYCLE_STATUS: `${API_BASE_URL}/api/rindm/cycle-status`,
    COMPLETE_CYCLE: `${API_BASE_URL}/api/rindm/complete-cycle`,
    CYCLE_HISTORY: `${API_BASE_URL}/api/rindm/history`,
    CHECK_WEATHER: `${API_BASE_URL}/api/rindm/check-weather`,
  },
};

// Nutrient Thresholds (kg/ha)
export const NUTRIENT_THRESHOLDS = {
  nitrogen: { min: 40, optimal: 80, max: 150 },
  phosphorus: { min: 15, optimal: 40, max: 80 },
  potassium: { min: 40, optimal: 100, max: 200 },
};

// Nutrient Status Colors
export const NUTRIENT_STATUS_COLORS = {
  critical: '#DC2626', // Dark red
  below: '#EF4444',    // Red
  optimal: '#22C55E',  // Green
  above: '#EAB308',    // Yellow
};

// Application Colors
export const COLORS = {
  primary: '#10B981',      // Emerald
  secondary: '#3B82F6',    // Blue
  success: '#22C55E',      // Green
  warning: '#EAB308',      // Yellow
  error: '#EF4444',        // Red
  critical: '#DC2626',     // Dark red
  background: '#F9FAFB',   // Light gray
  surface: '#FFFFFF',      // White
  text: {
    primary: '#1F2937',    // Dark gray
    secondary: '#6B7280',  // Medium gray
    light: '#9CA3AF',      // Light gray
  },
};

// Crop List
export const CROPS = [
  'rice',
  'wheat',
  'maize',
  'soybean',
  'cotton',
  'sugarcane',
  'groundnut',
  'sunflower',
  'chickpea',
  'pigeonpea',
  'lentil',
  'mustard',
  'sorghum',
  'bajra',
  'barley',
  'tomato',
  'potato',
  'onion',
  'garlic',
  'cabbage',
  'carrot',
  'muskmelon',
];

// Soil Types
export const SOIL_TYPES = [
  'clay',
  'sandy',
  'loamy',
  'silt',
  'peaty',
  'chalky',
];

// Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'cropsense_auth_token',
  USER_DATA: 'cropsense_user_data',
  REFRESH_TOKEN: 'cropsense_refresh_token',
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  SERVER_ERROR: 500,
};

// Messages
export const MESSAGES = {
  LOADING: 'Loading...',
  ERROR: 'An error occurred. Please try again.',
  SUCCESS: 'Operation successful!',
  NO_DATA: 'No data available',
  UNAUTHORIZED: 'Please login to continue',
  SESSION_EXPIRED: 'Session expired. Please login again.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
};
