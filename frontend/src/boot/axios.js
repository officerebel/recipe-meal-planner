import { boot } from 'quasar/wrappers'
import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production'
    ? '/api'
    : 'http://localhost:8000/api',
  timeout: 30000, // Increased to 30 seconds for Railway
  headers: {
    'Content-Type': 'application/json',
  }
})

// Auto demo login for local development
if (process.env.NODE_ENV === 'development') {
  // Check if we have a token, if not try to get one for demo user
  const token = localStorage.getItem('auth_token')
  if (!token) {
    console.log('No auth token found, attempting demo login...')
    // Try to login with demo user
    axios.post('http://localhost:8000/api/auth/login/', {
      email: 'demo@example.com',
      password: 'demo123'
    }).then(response => {
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token)
        console.log('✅ Auto-logged in as demo user for development')
        // Reload the page to apply the token
        window.location.reload()
      }
    }).catch(err => {
      console.log('❌ Demo login failed:', err.response?.data?.message || err.message)
      console.log('Please login manually at /login')
    })
  } else {
    console.log('✅ Auth token found, user is logged in')
  }
}

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
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
