import React, { createContext, useState, useCallback, useEffect } from 'react';
import { STORAGE_KEYS } from '../utils/constants';
import { authService, handleApiError } from '../services/api';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load user data on mount
  useEffect(() => {
    const savedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      }
    }
  }, [token]);

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
    error,
    signup,
    login,
    logout,
    isAuthenticated,
    setError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
