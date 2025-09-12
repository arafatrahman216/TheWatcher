// Central place for API config and authentication functions

require('dotenv').config();

export const API_BASE_URL =  "" + process.env.server_api

export const authAPI = {
  // User signup
  async signup(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      return data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  // User login
  async login(credentials) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store user data in localStorage
      if (data.success && data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('isAuthenticated', 'true');
      }

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Email verification
  async verifyEmail(verificationData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(verificationData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Email verification failed');
      }

      return data;
    } catch (error) {
      console.error('Email verification error:', error);
      throw error;
    }
  },

  // Logout
  logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
  },

  // Get current user
  getCurrentUser() {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated() {
    return localStorage.getItem('isAuthenticated') === 'true';
  },

  // Check authentication health
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/health`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Auth health check error:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }
};

// ==========================================
// Helper Functions
// ==========================================

export const monitorAPI = {
  // Create a new monitor
  async createMonitor(monitorData) {
    try {
      const response = await fetch(`${API_BASE_URL}/monitors/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(monitorData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create monitor');
      }

      return data;
    } catch (error) {
      console.error('Create monitor error:', error);
      throw error;
    }
  },

  // Get user monitors
  async getUserMonitors(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/monitors/user/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch monitors');
      }

      return data;
    } catch (error) {
      console.error('Fetch monitors error:', error);
      throw error;
    }
  },

  // Delete a monitor
  async deleteMonitor(userId, monitorId) {
    try {
      const response = await fetch(`${API_BASE_URL}/monitors/delete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          monitor_id: monitorId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to delete monitor');
      }

      return data;
    } catch (error) {
      console.error('Delete monitor error:', error);
      throw error;
    }
  },
};

export const apiHelpers = {
  // Generic API request with error handling
  async makeRequest(url, options = {}) {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Request failed');
      }

      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  },

  // Format validation errors consistently
  formatError(error) {
    if (typeof error === 'string') {
      return error;
    }
    
    if (Array.isArray(error)) {
      return error.map(err => {
        if (typeof err === 'string') return err;
        if (err.msg) return err.msg;
        if (err.message) return err.message;
        return JSON.stringify(err);
      }).join('; ');
    }
    
    if (typeof error === 'object' && error !== null) {
      if (error.msg) return error.msg;
      if (error.message) return error.message;
      if (error.detail) {
        return this.formatError(error.detail);
      }
      return JSON.stringify(error);
    }
    
    return 'Unknown error occurred';
  },

  // Format validation errors (legacy - for backward compatibility)
  formatErrors(errors) {
    return this.formatError(errors);
  }
};
