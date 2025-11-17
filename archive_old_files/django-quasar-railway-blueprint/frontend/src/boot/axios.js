import { boot } from 'quasar/wrappers'
import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      // Redirect to login if needed
    }

    return Promise.reject(error)
  }
)

export default boot(({ app }) => {
  // Make axios available globally
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }