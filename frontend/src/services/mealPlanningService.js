import { BaseApiService } from './api'

/**
 * Meal Planning API service
 */
export class MealPlanningService extends BaseApiService {
  constructor() {
    super('meal-plans/')
  }

  /**
   * Assign a recipe to a meal slot
   */
  async assignMeal(mealPlanId, assignmentData) {
    console.log('Service: Assigning meal:', mealPlanId, assignmentData)
    try {
      const result = await this.action(mealPlanId, 'assign-meal', assignmentData)
      console.log('Service: Meal assigned successfully:', result)
      return result
    } catch (error) {
      console.error('Service: Error assigning meal:', error)
      throw error
    }
  }

  /**
   * Get meal plan summary with statistics
   */
  async getSummary(mealPlanId) {
    return this.action(mealPlanId, 'summary', {}, 'get')
  }
}

/**
 * Meal Assignment API service
 */
export class MealAssignmentService extends BaseApiService {
  constructor() {
    super('meal-assignments/')
  }
}

/**
 * Shopping List API service
 */
export class ShoppingListService extends BaseApiService {
  constructor() {
    super('shopping-lists/')
  }

  /**
   * Generate shopping list from meal plans
   */
  async generate(data) {
    return this.create(data)
  }

  /**
   * Get shopping list items organized by category
   */
  async getByCategory(shoppingListId) {
    return this.action(shoppingListId, 'by-category', {}, 'get')
  }
}

/**
 * Shopping List Item API service
 */
export class ShoppingListItemService extends BaseApiService {
  constructor() {
    super('shopping-list-items/')
  }

  /**
   * Toggle purchased status of an item
   */
  async togglePurchased(itemId, purchased = true) {
    return this.action(itemId, 'toggle-purchased', { purchased }, 'patch')
  }
}

// Export singleton instances
export const mealPlanningService = new MealPlanningService()
export const mealAssignmentService = new MealAssignmentService()
export const shoppingListService = new ShoppingListService()
export const shoppingListItemService = new ShoppingListItemService()
