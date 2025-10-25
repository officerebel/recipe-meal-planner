import { defineStore } from 'pinia'
import { api } from 'boot/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('auth_token'),
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isLoading: (state) => state.loading,
  },

  actions: {
    /**
     * Login with email and password
     */
    async login(email, password) {
      this.loading = true
      this.error = null

      try {
        const response = await api.post('auth/login/', {
          email,
          password,
        })

        const { token, user } = response.data

        this.token = token
        this.user = user

        // Store token in localStorage
        localStorage.setItem('auth_token', token)

        return { success: true, user }
      } catch (error) {
        this.error = error.response?.data?.message || 'Login failed'
        console.error('Login error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Register new user
     */
    async register(userData) {
      this.loading = true
      this.error = null

      try {
        const response = await api.post('auth/register/', userData)

        const { token, user } = response.data

        this.token = token
        this.user = user

        // Store token in localStorage
        localStorage.setItem('auth_token', token)

        return { success: true, user }
      } catch (error) {
        this.error = error.response?.data?.message || 'Registration failed'
        console.error('Registration error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Logout user
     */
    async logout() {
      try {
        // Call logout endpoint if available
        if (this.token) {
          await api.post('auth/logout/')
        }
      } catch (error) {
        console.error('Logout error:', error)
        // Continue with local logout even if API call fails
      } finally {
        // Clear local state regardless of API call result
        this.token = null
        this.user = null
        localStorage.removeItem('auth_token')
      }
    },

    /**
     * Get current user profile
     */
    async fetchUser() {
      if (!this.token) return null

      this.loading = true

      try {
        const response = await api.get('auth/user/')
        this.user = response.data
        return response.data
      } catch (error) {
        console.error('Fetch user error:', error)
        // If token is invalid, logout
        if (error.response?.status === 401) {
          await this.logout()
        }
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Initialize auth state from localStorage
     */
    async initializeAuth() {
      const token = localStorage.getItem('auth_token')
      if (token) {
        this.token = token
        try {
          await this.fetchUser()
        } catch {
          // Token is invalid, clear it
          await this.logout()
        }
      }
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null
    },
  },
})
