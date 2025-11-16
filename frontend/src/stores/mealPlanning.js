import { defineStore } from 'pinia'
import { api } from 'boot/axios'
import { mobileApi } from 'src/services/mobileApiService'
import {
  mealPlanningService,
  mealAssignmentService,
  shoppingListService,
} from 'src/services/mealPlanningService'

export const useMealPlanningStore = defineStore('mealPlanning', {
  state: () => ({
    mealPlans: [],
    currentMealPlan: null,
    mealAssignments: [],
    shoppingLists: {
      personal: [],
      family: []
    },
    currentShoppingList: null,
    loading: {
      mealPlans: false,
      mealPlan: false,
      assignments: false,
      shoppingLists: false,
      shoppingList: false,
    },
    error: null,
    cache: {
      mealPlansLastFetch: null,
      mealPlanDetails: {}, // Cache detailed meal plans
      assignmentsByDate: {}, // Cache assignments by date
      shoppingListsLastFetch: {
        personal: null,
        family: null
      },
    },
    cacheTimeout: 5 * 60 * 1000, // 5 minutes
  }),

  getters: {
    /**
     * Get meal plan by ID
     */
    getMealPlanById: (state) => (id) => {
      return state.mealPlans.find((plan) => plan.id === id)
    },

    /**
     * Get assignments for a specific date and meal plan
     */
    getAssignmentsForDate: (state) => (mealPlanId, date) => {
      return state.mealAssignments.filter(
        (assignment) =>
          assignment.daily_meals.meal_plan === mealPlanId && assignment.daily_meals.date === date,
      )
    },

    /**
     * Get assignments grouped by meal type for a date
     */
    getAssignmentsByMealType: (state) => (mealPlanId, date) => {
      const assignments = state.mealAssignments.filter(
        (assignment) =>
          assignment.daily_meals.meal_plan === mealPlanId && assignment.daily_meals.date === date,
      )

      return assignments.reduce((acc, assignment) => {
        if (!acc[assignment.meal_type]) {
          acc[assignment.meal_type] = []
        }
        acc[assignment.meal_type].push(assignment)
        return acc
      }, {})
    },

    /**
     * Get shopping list by ID
     */
    getShoppingListById: (state) => (id) => {
      // Search in both personal and family shopping lists
      const personalList = state.shoppingLists.personal.find((list) => list.id === id)
      if (personalList) return personalList

      const familyList = state.shoppingLists.family.find((list) => list.id === id)
      return familyList
    },
  },

  actions: {
    /**
     * Clear error state
     */
    clearError() {
      this.error = null
    },

    /**
     * Fetch all meal plans with caching
     */
    async fetchMealPlans(forceRefresh = false) {
      console.log('Store: Fetching all meal plans')

      // Check cache first
      const now = Date.now()
      if (!forceRefresh &&
          this.cache.mealPlansLastFetch &&
          (now - this.cache.mealPlansLastFetch) < this.cacheTimeout &&
          this.mealPlans.length > 0) {
        console.log('Store: Using cached meal plans')
        return this.mealPlans
      }

      this.loading.mealPlans = true
      this.error = null

      try {
        // Check if we have an auth token
        const token = localStorage.getItem('auth_token')
        console.log('Store: Auth token available:', !!token)

        const response = await mealPlanningService.getAll()
        console.log('Store: Meal plans fetched:', response)
        this.mealPlans = response.results || response
        this.cache.mealPlansLastFetch = now
        console.log('Store: Meal plans stored:', this.mealPlans.length, 'plans')
        return this.mealPlans
      } catch (error) {
        console.error('Store: Error fetching meal plans:', error)
        console.error('Store: Error details:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        this.error = error.response?.data?.detail || error.message || 'Failed to fetch meal plans'
        throw error
      } finally {
        this.loading.mealPlans = false
      }
    },

    /**
     * Fetch a single meal plan by ID with caching
     */
    async fetchMealPlan(id, forceRefresh = false) {
      console.log('Store: Fetching meal plan with ID:', id)

      // Check cache first
      if (!forceRefresh && this.cache.mealPlanDetails[id]) {
        const cached = this.cache.mealPlanDetails[id]
        const now = Date.now()
        if ((now - cached.timestamp) < this.cacheTimeout) {
          console.log('Store: Using cached meal plan details')
          this.currentMealPlan = cached.data
          return cached.data
        }
      }

      this.loading.mealPlan = true
      this.error = null

      try {
        console.log('Store: Calling mealPlanningService.getById')
        const mealPlan = await mealPlanningService.getById(id)
        console.log('Store: Meal plan fetched successfully:', mealPlan)

        this.currentMealPlan = mealPlan

        // Cache the detailed meal plan
        this.cache.mealPlanDetails[id] = {
          data: mealPlan,
          timestamp: Date.now()
        }

        // Update in list if it exists
        const index = this.mealPlans.findIndex((plan) => plan.id === id)
        if (index !== -1) {
          this.mealPlans[index] = mealPlan
        }

        return mealPlan
      } catch (error) {
        console.error('Store: Error fetching meal plan:', error)
        this.error = error.message || 'Failed to fetch meal plan'
        throw error
      } finally {
        this.loading.mealPlan = false
      }
    },

    /**
     * Create a new meal plan
     */
    async createMealPlan(mealPlanData, options = {}) {
      console.log('Store: Creating meal plan with data:', mealPlanData)
      this.loading.mealPlans = true
      this.error = null

      try {
        console.log('Store: Calling mobile-optimized create')
        const mealPlan = await mobileApi.post('meal-plans/', mealPlanData, {
          onProgress: options.onProgress,
          maxRetries: 3
        })
        console.log('Store: Meal plan created successfully:', mealPlan)
        this.mealPlans.unshift(mealPlan)

        // Clear cache to force refresh
        this.cache.mealPlansLastFetch = null

        return mealPlan
      } catch (error) {
        console.error('Store: Error creating meal plan:', error)
        this.error = error.message || 'Failed to create meal plan'
        throw error
      } finally {
        this.loading.mealPlans = false
      }
    },

    /**
     * Update an existing meal plan
     */
    async updateMealPlan(id, mealPlanData, options = {}) {
      this.loading.mealPlans = true
      this.error = null

      try {
        const mealPlan = await mobileApi.put(`meal-plans/${id}/`, mealPlanData, {
          onProgress: options.onProgress,
          maxRetries: 3
        })

        // Update in list
        const index = this.mealPlans.findIndex((plan) => plan.id === id)
        if (index !== -1) {
          this.mealPlans[index] = mealPlan
        }

        // Update current meal plan if it's the same
        if (this.currentMealPlan?.id === id) {
          this.currentMealPlan = mealPlan
        }

        return mealPlan
      } catch (error) {
        this.error = error.message || 'Failed to update meal plan'
        console.error('Error updating meal plan:', error)
        throw error
      } finally {
        this.loading.mealPlans = false
      }
    },

    /**
     * Delete a meal plan
     */
    async deleteMealPlan(id) {
      this.loading.mealPlans = true
      this.error = null

      try {
        await mealPlanningService.delete(id)

        // Remove from list
        this.mealPlans = this.mealPlans.filter((plan) => plan.id !== id)

        // Clear current meal plan if it's the deleted one
        if (this.currentMealPlan?.id === id) {
          this.currentMealPlan = null
        }
      } catch (error) {
        this.error = error.message || 'Failed to delete meal plan'
        console.error('Error deleting meal plan:', error)
        throw error
      } finally {
        this.loading.mealPlans = false
      }
    },

    /**
     * Assign a meal to a meal plan
     */
    async assignMeal(mealPlanId, assignmentData) {
      console.log('Store: assignMeal called with:', { mealPlanId, assignmentData })
      this.loading.assignments = true
      this.error = null

      try {
        console.log('Store: Calling mobile-optimized assignMeal')
        const assignment = await mobileApi.post(`meal-plans/${mealPlanId}/assign-meal/`, assignmentData, {
          maxRetries: 3
        })
        console.log('Store: Meal assigned successfully:', assignment)

        // Add to meal assignments list
        this.mealAssignments.push(assignment)

        // Update current meal plan if it matches
        if (this.currentMealPlan && this.currentMealPlan.id === mealPlanId) {
          console.log('Store: Updating current meal plan with new assignment')

          // Find or create the daily meals for the assignment date
          let dailyMeals = this.currentMealPlan.daily_meals?.find(dm => dm.date === assignmentData.date)

          if (!dailyMeals) {
            // Create new daily meals entry if it doesn't exist
            dailyMeals = {
              id: `temp-${Date.now()}`,
              date: assignmentData.date,
              meal_assignments: []
            }
            if (!this.currentMealPlan.daily_meals) {
              this.currentMealPlan.daily_meals = []
            }
            this.currentMealPlan.daily_meals.push(dailyMeals)
          }

          // Add the assignment to the daily meals
          if (!dailyMeals.meal_assignments) {
            dailyMeals.meal_assignments = []
          }
          dailyMeals.meal_assignments.push(assignment)

          console.log('Store: Current meal plan updated with new assignment')
        }

        // Clear cache to ensure fresh data on next fetch
        delete this.cache.mealPlanDetails[mealPlanId]

        return assignment
      } catch (error) {
        console.error('Store: Error assigning meal:', error)
        console.error('Store: Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        })
        this.error = error.message || 'Failed to assign meal'
        throw error
      } finally {
        this.loading.assignments = false
        console.log('Store: assignMeal completed')
      }
    },

    /**
     * Remove a meal assignment
     */
    async removeMealAssignment(assignmentId) {
      this.loading.assignments = true
      this.error = null

      try {
        await mealAssignmentService.delete(assignmentId)

        // Remove from list
        this.mealAssignments = this.mealAssignments.filter(
          (assignment) => assignment.id !== assignmentId,
        )
      } catch (error) {
        this.error = error.message || 'Failed to remove meal assignment'
        console.error('Error removing meal assignment:', error)
        throw error
      } finally {
        this.loading.assignments = false
      }
    },

    /**
     * Fetch meal plan summary
     */
    async fetchMealPlanSummary(mealPlanId) {
      try {
        return await mealPlanningService.getSummary(mealPlanId)
      } catch (error) {
        console.error('Error fetching meal plan summary:', error)
        throw error
      }
    },

    /**
     * Fetch all shopping lists
     */
    async fetchShoppingLists(forceRefresh = false, scope = 'personal') {
      // Check cache first with scope-aware caching
      const now = Date.now()
      if (!forceRefresh &&
          this.cache.shoppingListsLastFetch[scope] &&
          (now - this.cache.shoppingListsLastFetch[scope]) < this.cacheTimeout &&
          this.shoppingLists[scope].length > 0) {
        console.log(`Store: Using cached shopping lists for scope: ${scope}`)
        return this.shoppingLists[scope]
      }

      this.loading.shoppingLists = true
      this.error = null

      try {
        const response = await shoppingListService.getAll({ scope })
        console.log(`Store: Raw shopping lists response for scope ${scope}:`, response)
        this.shoppingLists[scope] = response.results || response
        console.log(`Store: Shopping lists after setting for scope ${scope}:`, this.shoppingLists[scope].map(sl => ({ id: sl.id, name: sl.name })))
        this.cache.shoppingListsLastFetch[scope] = now
        return this.shoppingLists[scope]
      } catch (error) {
        this.error = error.message || 'Failed to fetch shopping lists'
        console.error('Error fetching shopping lists:', error)
        throw error
      } finally {
        this.loading.shoppingLists = false
      }
    },

    /**
     * Generate a shopping list from meal plans
     */
    async generateShoppingList(shoppingListData) {
      this.loading.shoppingLists = true
      this.error = null

      try {
        const shoppingList = await mobileApi.post('shopping-lists/generate/', shoppingListData, {
          maxRetries: 3
        })
        // Don't add to local state here - let the page refresh to get the latest data
        // Clear cache to ensure fresh data on next fetch
        this.cache.shoppingListsLastFetch = {
          personal: null,
          family: null
        }
        return shoppingList
      } catch (error) {
        this.error = error.message || 'Failed to generate shopping list'
        console.error('Error generating shopping list:', error)
        throw error
      } finally {
        this.loading.shoppingLists = false
      }
    },

    /**
     * Fetch shopping list by category
     */
    async fetchShoppingListByCategory(shoppingListId) {
      try {
        return await shoppingListService.getByCategory(shoppingListId)
      } catch (error) {
        console.error('Error fetching categorized shopping list:', error)
        throw error
      }
    },

    /**
     * Delete a shopping list
     */
    async deleteShoppingList(shoppingListId) {
      this.loading.shoppingLists = true
      this.error = null

      try {
        await shoppingListService.delete(shoppingListId)

        // Remove from local state (both scopes)
        this.shoppingLists.personal = this.shoppingLists.personal.filter(list => list.id !== shoppingListId)
        this.shoppingLists.family = this.shoppingLists.family.filter(list => list.id !== shoppingListId)

        // Clear current shopping list if it's the deleted one
        if (this.currentShoppingList?.id === shoppingListId) {
          this.currentShoppingList = null
        }
      } catch (error) {
        this.error = error.message || 'Failed to delete shopping list'
        console.error('Error deleting shopping list:', error)
        throw error
      } finally {
        this.loading.shoppingLists = false
      }
    },

    /**
     * Update shopping list title
     */
    async updateShoppingListTitle(shoppingListId, newTitle) {
      try {
        // For now, simulate API call with a delay
        await new Promise(resolve => setTimeout(resolve, 200))

        // In a real implementation, this would call the API:
        // return await shoppingListService.updateTitle(shoppingListId, newTitle)

        // Update local state (check both scopes)
        console.log('Updating shopping list title:', { shoppingListId, newTitle })

        let shoppingList = this.shoppingLists.personal.find(list => list.id === shoppingListId)
        if (!shoppingList) {
          shoppingList = this.shoppingLists.family.find(list => list.id === shoppingListId)
        }

        if (shoppingList) {
          console.log('Found shopping list, updating title from:', shoppingList.name, 'to:', newTitle)
          shoppingList.name = newTitle
        } else {
          console.warn('Shopping list not found in store:', shoppingListId)
        }

        console.log(`Updated shopping list ${shoppingListId} title to: ${newTitle}`)
        return { success: true, name: newTitle }
      } catch (error) {
        console.error('Error updating shopping list title:', error)
        throw error
      }
    },

    /**
     * Update shopping list item category
     */
    async updateShoppingListItemCategory(itemId, newCategory) {
      try {
        // Make actual API call to update item category
        const response = await api.patch(`shopping-list-items/${itemId}/`, {
          category: newCategory
        })

        console.log(`Updated item ${itemId} category to: ${newCategory}`)
        return response.data
      } catch (error) {
        console.error('Error updating item category:', error)
        throw error
      }
    },

    /**
     * Toggle purchased status of shopping list item
     */
    async toggleItemPurchased(itemId, purchased = true) {
      try {
        // For now, simulate API call with a delay
        await new Promise(resolve => setTimeout(resolve, 100))

        // In a real implementation, this would call the API:
        // return await shoppingListItemService.togglePurchased(itemId, purchased)

        console.log(`Toggled item ${itemId} to purchased: ${purchased}`)
        return { success: true, purchased }
      } catch (error) {
        console.error('Error toggling item purchased status:', error)
        throw error
      }
    },

  },
})
