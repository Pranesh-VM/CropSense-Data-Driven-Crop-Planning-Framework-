import React, { createContext, useState, useCallback, useEffect } from 'react';
import { STORAGE_KEYS } from '../utils/constants';
import { authService, handleApiError } from '../services/api';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN));
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true); // Session validation loading state
  const [error, setError] = useState(null);

  // Validate session on mount - automatically restore previous login
  useEffect(() => {
    const validateSession = async () => {
      const savedToken = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      const savedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      
      if (!savedToken) {
        setIsInitializing(false);
        return;
      }

      // First, set the saved user data for immediate display
      if (savedUser) {
        try {
          setUser(JSON.parse(savedUser));
          setToken(savedToken);
        } catch (e) {
          // Invalid saved data
        }
      }

      // Validate token with backend
      try {
        const response = await authService.getProfile();
        if (response.success && response.profile) {
          // Update user data with fresh data from server
          const userData = {
            farmer_id: response.profile.farmer_id,
            username: response.profile.username,
            email: response.profile.email,
            phone: response.profile.phone,
          };
          localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
          setUser(userData);
          setToken(savedToken);
        }
      } catch (err) {
        // Token is invalid or expired - clear session
        console.log('Session validation failed, clearing stored session');
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
        setToken(null);
        setUser(null);
      } finally {
        setIsInitializing(false);
      }
    };

    validateSession();
  }, []);

  const signup = useCallback(async (username, email, password, phone) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.signup(username, email, password, phone);
      
      if (response.token) {
        // Use user from response or create from input data
        const userData = response.user || { username, email, farmer_id: response.farmer_id };
        
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.token);
        localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
        
        setToken(response.token);
        setUser(userData);
        
        return { success: true, message: 'Signup successful!' };
      }
      return { success: false, message: 'Signup failed - no token received' };
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.login(email, password);
      
      if (response.token) {
        // Use farmer data from response (contains username from signup)
        const userData = response.farmer || { email, farmer_id: response.farmer_id };
        
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.token);
        localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
        
        setToken(response.token);
        setUser(userData);
        
        return { success: true, message: 'Login successful!' };
      }
      return { success: false, message: 'Login failed - no token received' };
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    setToken(null);
    setUser(null);
    setError(null);
  }, []);

  const isAuthenticated = !!token && !!user;

  const value = {
    user,
    token,
    isLoading,
    isInitializing,
    error,
    signup,
    login,
    logout,
    isAuthenticated,
    setError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
