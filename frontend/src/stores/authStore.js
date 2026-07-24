/**
 * Auth store — Zustand for authentication state.
 * Persists tokens in localStorage for session continuity.
 * login() performs the actual API call to POST /api/auth/login/.
 */
import { create } from 'zustand';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const useAuthStore = create((set, get) => ({
  // State
  user: JSON.parse(localStorage.getItem('eshop_user') || 'null'),
  accessToken: localStorage.getItem('eshop_access_token') || null,
  refreshToken: localStorage.getItem('eshop_refresh_token') || null,
  isAuthenticated: !!localStorage.getItem('eshop_access_token'),
  error: null,

  // Actions
  setTokens: (access, refresh) => {
    localStorage.setItem('eshop_access_token', access);
    if (refresh) localStorage.setItem('eshop_refresh_token', refresh);
    set({
      accessToken: access,
      refreshToken: refresh || get().refreshToken,
      isAuthenticated: true,
    });
  },

  setUser: (user) => {
    localStorage.setItem('eshop_user', JSON.stringify(user));
    set({ user });
  },

  /**
   * Perform login API call.
   * @param {string} username - Username or email
   * @param {string} password - User password
   * @returns {Promise<boolean>} true on success, false on failure
   */
  login: async (username, password) => {
    set({ error: null });
    try {
      const { data } = await axios.post(`${API_BASE_URL}/auth/login/`, {
        username,
        password,
      });

      const user = {
        id: data.user_id,
        email: data.email,
        role: data.role,
        username: username,
      };

      localStorage.setItem('eshop_access_token', data.access);
      localStorage.setItem('eshop_refresh_token', data.refresh);
      localStorage.setItem('eshop_user', JSON.stringify(user));

      set({
        user,
        accessToken: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
        error: null,
      });

      return true;
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Login failed. Please check your credentials.';
      set({ error: message });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('eshop_access_token');
    localStorage.removeItem('eshop_refresh_token');
    localStorage.removeItem('eshop_user');
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
    });
  },
}));
