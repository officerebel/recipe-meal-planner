import { api } from 'boot/axios'

/**
 * Mobile-optimized API service with retry logic and better error handling
 */
export class MobileApiService {
  constructor() {
    this.maxRetries = 3
    this.retryDelay = 1000 // Start with 1 second
    this.networkTimeout = 15000 // 15 seconds for mobile
  }

  /**
   * Check if we're online
   */
  isOnline() {
    return navigator.onLine
  }

  /**
   * Wait for network to come back online
   */
  async waitForOnline(timeout = 30000) {
    if (this.isOnline()) return true

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        window.removeEventListener('online', onlineHandler)
        reject(new Error('Network timeout: Still offline after 30 seconds'))
      }, timeout)

      const onlineHandler = () => {
        clearTimeout(timeoutId)
        window.removeEventListener('online', onlineHandler)
        resolve(true)
      }

      window.addEventListener('online', onlineHandler)
    })
  }

  /**
   * Exponential backoff delay
   */
  async delay(attempt) {
    const delayMs = this.retryDelay * Math.pow(2, attempt)
    return new Promise(resolve => setTimeout(resolve, delayMs))
  }

  /**
   * Check if error is retryable
   */
  isRetryableError(error) {
    // Network errors
    if (!error.response) return true

    // Server errors (5xx)
    if (error.response.status >= 500) return true

    // Rate limiting
    if (error.response.status === 429) return true

    // Timeout errors
    if (error.code === 'ECONNABORTED') return true

    return false
  }

  /**
   * Make API request with retry logic
   */
  async makeRequest(requestFn, options = {}) {
    const {
      maxRetries = this.maxRetries,
      onProgress = null
    } = options

    let lastError = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Check if we're online before attempting
        if (!this.isOnline()) {
          console.log('📱 Offline detected, waiting for connection...')
          await this.waitForOnline()
        }

        if (onProgress && attempt > 0) {
          onProgress(`Retrying... (${attempt}/${maxRetries})`)
        }

        // Make the actual request
        const result = await requestFn()

        if (onProgress && attempt > 0) {
          onProgress('Success!')
        }

        return result

      } catch (error) {
        lastError = error
        console.error(`📱 API request failed (attempt ${attempt + 1}/${maxRetries + 1}):`, error.message)

        // Don't retry on final attempt
        if (attempt === maxRetries) break

        // Don't retry non-retryable errors
        if (!this.isRetryableError(error)) {
          console.log('📱 Non-retryable error, not retrying')
          break
        }

        // Wait before retrying
        if (attempt < maxRetries) {
          const delayMs = this.retryDelay * Math.pow(2, attempt)
          console.log(`📱 Retrying in ${delayMs}ms...`)

          if (onProgress) {
            onProgress(`Retrying in ${Math.ceil(delayMs/1000)}s...`)
          }

          await this.delay(attempt)
        }
      }
    }

    // All retries failed
    throw this.enhanceError(lastError)
  }

  /**
   * Enhance error with mobile-friendly messages
   */
  enhanceError(error) {
    if (!error.response) {
      // Network error
      if (!this.isOnline()) {
        error.message = 'No internet connection. Please check your network and try again.'
      } else {
        error.message = 'Network error. Please check your connection and try again.'
      }
    } else if (error.response.status >= 500) {
      error.message = 'Server error. Please try again in a moment.'
    } else if (error.response.status === 429) {
      error.message = 'Too many requests. Please wait a moment and try again.'
    } else if (error.response.status === 401) {
      error.message = 'Session expired. Please log in again.'
    } else if (error.response.status === 403) {
      error.message = 'Access denied. Please check your permissions.'
    }

    return error
  }

  /**
   * Mobile-optimized POST request
   */
  async post(url, data, options = {}) {
    return this.makeRequest(async () => {
      const config = {
        timeout: this.networkTimeout,
        ...options
      }

      const response = await api.post(url, data, config)
      return response.data
    }, options)
  }

  /**
   * Mobile-optimized PUT request
   */
  async put(url, data, options = {}) {
    return this.makeRequest(async () => {
      const config = {
        timeout: this.networkTimeout,
        ...options
      }

      const response = await api.put(url, data, config)
      return response.data
    }, options)
  }

  /**
   * Mobile-optimized PATCH request
   */
  async patch(url, data, options = {}) {
    return this.makeRequest(async () => {
      const config = {
        timeout: this.networkTimeout,
        ...options
      }

      const response = await api.patch(url, data, config)
      return response.data
    }, options)
  }

  /**
   * Mobile-optimized GET request
   */
  async get(url, options = {}) {
    return this.makeRequest(async () => {
      const config = {
        timeout: this.networkTimeout,
        ...options
      }

      const response = await api.get(url, config)
      return response.data
    }, options)
  }

  /**
   * Mobile-optimized DELETE request
   */
  async delete(url, options = {}) {
    return this.makeRequest(async () => {
      const config = {
        timeout: this.networkTimeout,
        ...options
      }

      const response = await api.delete(url, config)
      return response.data
    }, options)
  }
}

// Export singleton instance
export const mobileApi = new MobileApiService()
