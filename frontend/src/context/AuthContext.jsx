import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_BASE_URL = 'http://localhost:8000/api/v1';

const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    delete axios.defaults.headers.common['Authorization'];
    setToken(null);
    setCurrentUser(null);
  };

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (
          error.response?.status === 401 &&
          !originalRequest._retry &&
          originalRequest.url &&
          !originalRequest.url.includes('/auth/refresh') &&
          !originalRequest.url.includes('/auth/login')
        ) {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            originalRequest._retry = true;
            try {
              const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const { access_token, refresh_token: newRefreshToken } = res.data;
              
              localStorage.setItem('token', access_token);
              if (newRefreshToken) {
                localStorage.setItem('refresh_token', newRefreshToken);
              }
              
              axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
              originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
              
              setToken(access_token);
              
              return axios(originalRequest);
            } catch (err) {
              logout();
              return Promise.reject(err);
            }
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const decoded = decodeToken(token);
      if (decoded && decoded.exp * 1000 > Date.now()) {
        setCurrentUser({
          id: decoded.sub,
          email: decoded.email,
        });
        
        axios.get(`${API_BASE_URL}/auth/me`)
          .then(res => {
            setCurrentUser(res.data);
          })
          .catch(() => {
            // Interceptor handles retry/logout
          })
          .finally(() => {
            setLoading(false);
          });
      } else {
        // Access token is expired on load, attempt immediate refresh
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
            .then(res => {
              const { access_token, refresh_token: newRefreshToken } = res.data;
              localStorage.setItem('token', access_token);
              if (newRefreshToken) {
                localStorage.setItem('refresh_token', newRefreshToken);
              }
              setToken(access_token);
            })
            .catch(() => {
              logout();
              setLoading(false);
            });
        } else {
          logout();
          setLoading(false);
        }
      }
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setCurrentUser(null);
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password,
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setToken(access_token);
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      return { success: false, error: message };
    }
  };

  const register = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email,
        password,
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setToken(access_token);
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      return { success: false, error: message };
    }
  };

  const isAuthenticated = !!token && !!currentUser;

  const value = {
    token,
    currentUser,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
