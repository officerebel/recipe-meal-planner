import { defineStore } from 'pinia'
import { recipeService } from 'src/services/recipeService'
import { mobileApi } from 'src/services/mobileApiService'
import { api } from 'boot/axios'

export const useRecipeStore = defineStore('recipes', {
  state: () => ({
    recipes: [],
    currentRecipe: null,
    categories: [
      'Hoofdgerecht',
      'Voorgerecht',
      'Nagerecht',
      'Salade',
      'Soep',
      'Drank',
      'Tussendoortje',
      'Ontbijt',
      'Lunch',
      'Diner',
      'Bijgerecht',
      'Saus',
      'Brood',
      'Pasta'
    ],
    ingredientCategories: [
      { value: 'produce', label: 'Groenten & Fruit' },
      { value: 'meat', label: 'Vlees & Vis' },
      { value: 'dairy', label: 'Zuivel & Eieren' },
      { value: 'pantry', label: 'Voorraadkast' },
      { value: 'frozen', label: 'Diepvries' },
      { value: 'bakery', label: 'Bakkerij' },
      { value: 'beverages', label: 'Dranken' },
      { value: 'condiments', label: 'Kruiden & Sauzen' },
      { value: 'spices', label: 'Specerijen & Kruiden' },
      { value: 'other', label: 'Overig' }
    ],
    tags: [
      'Snel',
      'Makkelijk',
      'Gezond',
      'Vegetarisch',
      'Veganistisch',
      'Glutenvrij',
      'Zuivelvrij',
      'Koolhydraatarm',
      'Eiwitrijk',
      'Pittig',
      'Zoet',
      'Comfort Food',
      'Feestdag',
      'Zomer',
      'Winter'
    ],
    statistics: null,
    loading: false,
    error: null,
    searchFilters: {
      search: '',
      category: '',
      tag: '',
      source: '',
      scope: 'personal', // 'personal' or 'family'
      page: 1,
      pageSize: 20,
    },
    pagination: {
      count: 0,
      next: null,
      previous: null,
      currentPage: 1,
      totalPages: 1,
    },
  }),

  getters: {
    /**
     * Get recipes filtered by current search criteria
     */
    filteredRecipes: (state) => {
      let filtered = [...state.recipes]

      if (state.searchFilters.search) {
        const searchTerm = state.searchFilters.search.toLowerCase()
        filtered = filtered.filter(
          (recipe) =>
            recipe.title.toLowerCase().includes(searchTerm) ||
            recipe.description.toLowerCase().includes(searchTerm) ||
            recipe.ingredients.some((ingredient) =>
              ingredient.name.toLowerCase().includes(searchTerm),
            ),
        )
      }

      if (state.searchFilters.category) {
        filtered = filtered.filter((recipe) =>
          recipe.categories.includes(state.searchFilters.category),
        )
      }

      if (state.searchFilters.tag) {
        filtered = filtered.filter((recipe) => recipe.tags.includes(state.searchFilters.tag))
      }

      if (state.searchFilters.source) {
        filtered = filtered.filter((recipe) => recipe.source === state.searchFilters.source)
      }

      return filtered
    },

    /**
     * Check if there are any active filters
     */
    hasActiveFilters: (state) => {
      return (
        state.searchFilters.search ||
        state.searchFilters.category ||
        state.searchFilters.tag ||
        state.searchFilters.source
      )
    },

    /**
     * Get recipe by ID
     */
    getRecipeById: (state) => (id) => {
      return state.recipes.find((recipe) => recipe.id === id)
    },
  },

  actions: {
    /**
     * Fetch recipes with current filters
     */
    async fetchRecipes(resetPagination = false) {
      this.loading = true
      this.error = null

      try {
        if (resetPagination) {
          this.searchFilters.page = 1
        }

        const params = { ...this.searchFilters }
        // Remove empty filters
        Object.keys(params).forEach((key) => {
          if (!params[key]) delete params[key]
        })

        const response = await recipeService.search(params)

        if (resetPagination || this.searchFilters.page === 1) {
          this.recipes = response.results || []
        } else {
          // Append for pagination
          this.recipes.push(...(response.results || []))
        }

        // Update pagination info
        this.pagination = {
          count: response.count || 0,
          next: response.next,
          previous: response.previous,
          currentPage: this.searchFilters.page,
          totalPages: Math.ceil((response.count || 0) / this.searchFilters.pageSize),
        }
      } catch (error) {
        this.error = error.message || 'Failed to fetch recipes'
        console.error('Error fetching recipes:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single recipe by ID
     */
    async fetchRecipe(id) {
      this.loading = true
      this.error = null

      try {
        const recipe = await recipeService.getById(id)
        this.currentRecipe = recipe

        // Update recipe in list if it exists
        const index = this.recipes.findIndex((r) => r.id === id)
        if (index !== -1) {
          this.recipes[index] = recipe
        }

        return recipe
      } catch (error) {
        this.error = error.message || 'Failed to fetch recipe'
        console.error('Error fetching recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new recipe
     */
    async createRecipe(recipeData) {
      this.loading = true
      this.error = null

      try {
        const recipe = await mobileApi.post('recipes/', recipeData, {
          maxRetries: 3
        })
        this.recipes.unshift(recipe)
        return recipe
      } catch (error) {
        this.error = error.message || 'Failed to create recipe'
        console.error('Error creating recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing recipe
     */
    async updateRecipe(id, recipeData) {
      this.loading = true
      this.error = null

      try {
        const recipe = await recipeService.update(id, recipeData)

        // Update in list
        const index = this.recipes.findIndex((r) => r.id === id)
        if (index !== -1) {
          this.recipes[index] = recipe
        }

        // Update current recipe if it's the same
        if (this.currentRecipe?.id === id) {
          this.currentRecipe = recipe
        }

        return recipe
      } catch (error) {
        this.error = error.message || 'Failed to update recipe'
        console.error('Error updating recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete a recipe
     */
    async deleteRecipe(id) {
      this.loading = true
      this.error = null

      try {
        await recipeService.delete(id)

        // Remove from list
        this.recipes = this.recipes.filter((r) => r.id !== id)

        // Clear current recipe if it's the deleted one
        if (this.currentRecipe?.id === id) {
          this.currentRecipe = null
        }
      } catch (error) {
        this.error = error.message || 'Failed to delete recipe'
        console.error('Error deleting recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Import recipe from PDF or image file
     */
    async importFromFile(file, onProgress = null) {
      this.loading = true
      this.error = null

      try {
        const importResult = await recipeService.importFromFile(file, onProgress)
        // Handle the backend response structure: { recipe: {...}, import_metadata: {...} }
        const recipe = importResult.recipe || importResult
        this.recipes.unshift(recipe)
        return importResult  // Return the full result so the frontend can access both recipe and metadata
      } catch (error) {
        this.error = error.message || 'Failed to import recipe'
        console.error('Error importing recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Import recipe from PDF (backward compatibility)
     */
    async importFromPdf(file, onProgress = null) {
      return this.importFromFile(file, onProgress)
    },

    /**
     * Preview recipe from file (PDF or image)
     */
    async previewFromFile(file, options = {}) {
      this.loading = true
      this.error = null

      try {
        // Create FormData for file upload
        const formData = new FormData()
        formData.append('file', file)

        // Add parsing options if provided
        if (options.parsingMode) {
          formData.append('parsing_mode', options.parsingMode)
        }
        if (options.expectedLanguage) {
          formData.append('expected_language', options.expectedLanguage)
        }

        // Add preview flag to indicate this is a preview request
        formData.append('preview', 'true')

        console.log('Calling preview API for file:', file.name)

        // Call the import API with preview flag
        const response = await api.post('/recipes/import/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        console.log('Preview API response:', response.data)
        return response.data

      } catch (error) {
        this.error = error.response?.data?.detail || error.message || 'Failed to preview recipe'
        console.error('Error previewing recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Preview recipe from PDF (backward compatibility)
     */
    async previewFromPdf(file, options = {}) {
      return this.previewFromFile(file, options)
    },

    /**
     * Fetch categories
     */
    async fetchCategories() {
      try {
        const apiCategories = await recipeService.getCategories()
        // Merge predefined categories with API categories
        const allCategories = [...new Set([...this.categories, ...apiCategories])]
        this.categories = allCategories.sort()
      } catch (error) {
        console.error('Error fetching categories:', error)
        // Keep predefined categories if API fails
      }
    },

    /**
     * Fetch tags
     */
    async fetchTags() {
      try {
        const apiTags = await recipeService.getTags()
        // Merge predefined tags with API tags
        const allTags = [...new Set([...this.tags, ...apiTags])]
        this.tags = allTags.sort()
      } catch (error) {
        console.error('Error fetching tags:', error)
        // Keep predefined tags if API fails
      }
    },

    /**
     * Fetch ingredient categories
     */
    async fetchIngredientCategories() {
      try {
        const apiCategories = await recipeService.getIngredientCategories()
        this.ingredientCategories = apiCategories
      } catch (error) {
        console.error('Error fetching ingredient categories:', error)
        // Keep predefined categories if API fails
      }
    },

    /**
     * Fetch statistics
     */
    async fetchStatistics() {
      try {
        this.statistics = await recipeService.getStatistics()
      } catch (error) {
        console.error('Error fetching statistics:', error)
      }
    },

    /**
     * Update search filters
     */
    updateFilters(filters) {
      this.searchFilters = { ...this.searchFilters, ...filters }
    },

    /**
     * Clear all filters
     */
    clearFilters() {
      this.searchFilters = {
        search: '',
        category: '',
        tag: '',
        source: '',
        scope: 'personal',
        page: 1,
        pageSize: 20,
      }
    },

    /**
     * Load more recipes (pagination)
     */
    async loadMore() {
      if (this.pagination.next && !this.loading) {
        this.searchFilters.page += 1
        await this.fetchRecipes(false)
      }
    },

    /**
     * Create recipe with image
     */
    async createRecipeWithImage(recipeData) {
      this.loading = true
      this.error = null

      try {
        const recipe = await recipeService.createWithImage(recipeData)
        this.recipes.unshift(recipe)
        return recipe
      } catch (error) {
        this.error = error.message || 'Failed to create recipe'
        console.error('Error creating recipe with image:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update recipe with image
     */
    async updateRecipeWithImage(id, recipeData) {
      this.loading = true
      this.error = null

      try {
        const recipe = await recipeService.updateWithImage(id, recipeData)

        // Update in list
        const index = this.recipes.findIndex((r) => r.id === id)
        if (index !== -1) {
          this.recipes[index] = recipe
        }

        // Update current recipe if it's the same
        if (this.currentRecipe?.id === id) {
          this.currentRecipe = recipe
        }

        return recipe
      } catch (error) {
        this.error = error.message || 'Failed to update recipe'
        console.error('Error updating recipe with image:', error)
        throw error
      } finally {
        this.loading = false
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
