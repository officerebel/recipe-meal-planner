import { api } from 'boot/axios'

/**
 * Base API service class
 */
export class BaseApiService {
  constructor(baseEndpoint) {
    this.baseEndpoint = baseEndpoint
  }

  /**
   * Get all items with optional query parameters
   */
  async getAll(params = {}) {
    const response = await api.get(this.baseEndpoint, { params })
    return response.data
  }

  /**
   * Get a single item by ID
   */
  async getById(id) {
    console.log(`API: Getting ${this.baseEndpoint}${id}/`)
    try {
      const response = await api.get(`${this.baseEndpoint}${id}/`)
      console.log(`API: Successfully fetched ${this.baseEndpoint}${id}/:`, response.data)
      return response.data
    } catch (error) {
      console.error(`API: Error fetching ${this.baseEndpoint}${id}/:`, error)
      throw error
    }
  }

  /**
   * Create a new item
   */
  async create(data) {
    console.log(`API: Creating ${this.baseEndpoint} with data:`, data)
    try {
      const response = await api.post(`${this.baseEndpoint}`, data)
      console.log(`API: Successfully created ${this.baseEndpoint}:`, response.data)
      return response.data
    } catch (error) {
      console.error(`API: Error creating ${this.baseEndpoint}:`, error)
      throw error
    }
  }

  /**
   * Update an existing item
   */
  async update(id, data) {
    const response = await api.put(`${this.baseEndpoint}${id}/`, data)
    return response.data
  }

  /**
   * Partially update an existing item
   */
  async patch(id, data) {
    const response = await api.patch(`${this.baseEndpoint}${id}/`, data)
    return response.data
  }

  /**
   * Delete an item
   */
  async delete(id) {
    await api.delete(`${this.baseEndpoint}${id}/`)
  }

  /**
   * Call a custom action on an item
   */
  async action(id, actionName, data = {}, method = 'post') {
    const url = id
      ? `${this.baseEndpoint}${id}/${actionName}/`
      : `${this.baseEndpoint}${actionName}/`

    console.log(`API: Calling action ${method.toUpperCase()} ${url} with data:`, data)
    try {
      const response = await api[method](url, data)
      console.log(`API: Action ${method.toUpperCase()} ${url} successful:`, response.data)
      return response.data
    } catch (error) {
      console.error(`API: Error calling action ${method.toUpperCase()} ${url}:`, error)
      throw error
    }
  }
}
