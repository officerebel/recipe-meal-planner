// Production configuration
export const config = {
  // Disable demo mode in production
  enableDemoMode: process.env.NODE_ENV !== 'production',

  // API configuration
  apiBaseUrl: process.env.NODE_ENV === 'production'
    ? 'https://proud-mercy-production.up.railway.app/api'
    : 'http://localhost:8000/api',

  // Feature flags
  features: {
    testMode: process.env.NODE_ENV !== 'production',
    debugMode: process.env.NODE_ENV !== 'production',
    autoLogin: false, // Always disabled for security
  },

  // App metadata
  version: '1.0.0',
  environment: process.env.NODE_ENV || 'development'
}

export default config
