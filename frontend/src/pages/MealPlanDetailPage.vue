<template>
  <q-page class="q-pa-lg">
    <!-- Loading State -->
    <div v-if="loading" class="row justify-center q-py-xl">
      <q-spinner-dots size="50px" color="primary" />
    </div>

    <!-- Error State -->
    <q-banner v-else-if="error" class="bg-negative text-white q-mb-md">
      <template v-slot:avatar>
        <q-icon name="error" />
      </template>
      {{ error }}
      <template v-slot:action>
        <q-btn v-if="isNotFoundError" flat label="Go to Meal Plans" @click="$router.push({ name: 'meal-plans' })" />
        <q-btn v-else flat label="Retry" @click="loadMealPlan" />

      </template>
    </q-banner>

    <!-- Meal Plan Content -->
    <div v-else-if="mealPlan">
      <!-- Breadcrumb Navigation -->
      <q-breadcrumbs class="q-mb-md">
        <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
        <q-breadcrumbs-el label="Meal Plans" icon="calendar_today" :to="{ name: 'meal-plans' }" />
        <q-breadcrumbs-el :label="mealPlan.name" />
      </q-breadcrumbs>

      <!-- Header -->
      <div class="row justify-between items-center q-mb-lg">
        <div>
          <div class="text-h4">{{ mealPlan.name }}</div>
          <div class="text-subtitle1 text-grey-7">
            {{ formatDateRange(mealPlan.start_date, mealPlan.end_date) }}
          </div>
        </div>
        <div class="q-gutter-sm">
          <q-btn flat icon="arrow_back" label="Back to Meal Plans" :to="{ name: 'meal-plans' }" />
          <q-btn
            color="secondary"
            icon="edit"
            label="Edit"
            :to="{ name: 'meal-plan-edit', params: { id: mealPlan.id } }"
          />
          <q-btn
            color="primary"
            icon="shopping_cart"
            label="Generate Shopping List"
            @click="generateShoppingList"
          />
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card>
            <q-card-section class="text-center">
              <div class="text-h6 text-primary">{{ mealPlan.total_days }}</div>
              <div class="text-caption">Total Days</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card>
            <q-card-section class="text-center">
              <div class="text-h6 text-secondary">{{ mealPlan.total_meals || 0 }}</div>
              <div class="text-caption">Meals Planned</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card>
            <q-card-section class="text-center">
              <div class="text-h6 text-accent">{{ completionPercentage }}%</div>
              <div class="text-caption">Complete</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card>
            <q-card-section class="text-center">
              <div class="text-h6 text-info">{{ remainingMeals }}</div>
              <div class="text-caption">Meals Remaining</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Calendar View -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 q-mb-md">
            <q-icon name="calendar_month" class="q-mr-sm" />
            Meal Calendar
          </div>

          <div class="calendar-grid">
            <div v-for="day in calendarDays" :key="day.date" class="calendar-day">
              <div class="day-header">
                <div class="text-subtitle2">{{ formatDayHeader(day.date) }}</div>
                <div class="text-caption text-grey-6">{{ formatDate(day.date) }}</div>
              </div>

              <div class="meals-container">
                <div
                  v-for="mealType in mealTypes"
                  :key="mealType"
                  class="meal-slot"
                  :class="{ 'has-meal': day.meals[mealType] }"
                >
                  <div class="meal-type-label">{{ mealType }}</div>
                  <div v-if="day.meals[mealType]" class="meal-content">
                    <div class="meal-name">
                      {{ day.meals[mealType].recipe?.title || 'Unknown Recipe' }}
                    </div>
                    <div class="meal-servings">
                      {{ day.meals[mealType].servings_planned }} servings
                    </div>
                    <q-btn
                      flat
                      dense
                      round
                      icon="close"
                      size="xs"
                      color="negative"
                      @click="removeMeal(day.meals[mealType].id)"
                      class="remove-meal-btn"
                    />
                  </div>
                  <div v-else class="empty-meal">
                    <q-btn
                      flat
                      dense
                      icon="add"
                      label="Add Meal"
                      size="sm"
                      @click="showAddMealDialog(day.date, mealType)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Add Meal Dialog -->
      <q-dialog
        v-model="showAddMeal"
        @hide="onDialogHide"
        persistent
        :key="`add-meal-${selectedDate}-${selectedMealType}`"
      >
        <q-card style="min-width: 400px">
          <q-card-section>
            <div class="text-h6">Add Meal</div>
            <div class="text-subtitle2">{{ selectedDate }} - {{ selectedMealType }}</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="addMeal" class="q-gutter-md">
              <!-- Recipe Search -->
              <q-input
                v-model="recipeSearchQuery"
                placeholder="Search recipes..."
                outlined
                dense
                clearable
                :disable="addingMeal"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>

              <q-select
                v-model="newMeal.recipe_id"
                :options="filteredRecipeOptions"
                option-value="id"
                option-label="title"
                label="Recipe *"
                outlined
                emit-value
                map-options
                :rules="[(val) => !!val || 'Recipe is required']"
                :disable="addingMeal"
                use-input
                @filter="filterRecipes"
              />

              <q-input
                v-model.number="newMeal.servings_planned"
                label="Servings *"
                type="number"
                min="1"
                outlined
                :rules="[(val) => val > 0 || 'Servings must be greater than 0']"
                :disable="addingMeal"
              />

              <q-input
                v-model="newMeal.notes"
                label="Notes (optional)"
                type="textarea"
                outlined
                rows="2"
                :disable="addingMeal"
              />

              <div class="row q-gutter-sm justify-end">
                <q-btn flat label="Cancel" @click="cancelAddMeal" :disable="addingMeal" />
                <q-btn
                  type="submit"
                  label="Add Meal"
                  color="primary"
                  :loading="addingMeal"
                  :disable="!newMeal.recipe_id || newMeal.servings_planned <= 0"
                />
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useMealPlanningStore } from 'src/stores/mealPlanning'
import { useRecipeStore } from 'src/stores/recipes'


const $q = useQuasar()
const router = useRouter()
const mealPlanningStore = useMealPlanningStore()
const recipesStore = useRecipeStore()

// Create a safe notify function
const notify = (options) => {
  try {
    if ($q && $q.notify) {
      $q.notify(options)
    } else {
      console.log('Notification:', options.message)
    }
  } catch (error) {
    console.log('Notification error:', error.message, '- Message:', options.message)
  }
}

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

// State
const mealPlan = ref(null)
const loading = ref(false)
const error = ref(null)
const showAddMeal = ref(false)
const selectedDate = ref('')
const selectedMealType = ref('')
const addingMeal = ref(false)
const recipeSearchQuery = ref('')
const newMeal = ref({
  recipe_id: null,
  servings_planned: 1,
  notes: '',
})

const mealTypes = ['breakfast', 'lunch', 'dinner']

// Computed
const completionPercentage = computed(() => {
  if (!mealPlan.value) return 0
  const totalSlots = mealPlan.value.total_days * 3
  const filledSlots = mealPlan.value.total_meals || 0
  return Math.round((filledSlots / totalSlots) * 100)
})

const remainingMeals = computed(() => {
  if (!mealPlan.value) return 0
  const totalSlots = mealPlan.value.total_days * 3
  const filledSlots = mealPlan.value.total_meals || 0
  return totalSlots - filledSlots
})

const calendarDays = computed(() => {
  console.log('Detail: Computing calendar days, mealPlan:', mealPlan.value)
  if (!mealPlan.value) return []

  const days = []
  const startDate = new Date(mealPlan.value.start_date)
  const endDate = new Date(mealPlan.value.end_date)

  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().split('T')[0]
    const dayMeals = {}

    // Initialize empty meals for each type
    mealTypes.forEach((type) => {
      dayMeals[type] = null
    })

    // Fill in actual meals if they exist
    if (mealPlan.value.daily_meals) {
      const dailyMeal = mealPlan.value.daily_meals.find((dm) => dm.date === dateStr)
      if (dailyMeal && dailyMeal.meal_assignments) {
        dailyMeal.meal_assignments.forEach((assignment) => {
          dayMeals[assignment.meal_type] = assignment
        })
      }
    }

    days.push({
      date: dateStr,
      meals: dayMeals,
    })
  }

  console.log('Detail: Calendar days computed:', days.length, 'days')
  return days
})

const recipeOptions = computed(() => recipesStore.recipes)

const filteredRecipeOptions = computed(() => {
  if (!recipeSearchQuery.value) {
    return recipeOptions.value
  }

  const query = recipeSearchQuery.value.toLowerCase()
  return recipeOptions.value.filter(recipe =>
    recipe.title.toLowerCase().includes(query) ||
    (recipe.description && recipe.description.toLowerCase().includes(query)) ||
    (recipe.ingredients && recipe.ingredients.some(ingredient =>
      ingredient.toLowerCase().includes(query)
    ))
  )
})



const isNotFoundError = computed(() => {
  return error.value && error.value.includes('not found')
})

// Methods
const updateShoppingLists = async () => {
  try {
    notify({
      type: 'info',
      message: 'Boodschappenlijsten worden bijgewerkt...',
      timeout: 2000,
    })

    // Navigate to shopping lists page with update parameter
    router.push({
      name: 'shopping-lists',
      query: {
        update: 'true',
        mealPlan: props.id,
      },
    })
  } catch (error) {
    console.error('Error updating shopping lists:', error)
    notify({
      type: 'negative',
      message: 'Fout bij bijwerken boodschappenlijsten',
    })
  }
}



// Lifecycle
onMounted(async () => {
  console.log('MealPlanDetailPage: Component mounted with ID:', props.id)
  await loadMealPlan()
  await loadRecipes()
})

// Methods
const loadMealPlan = async () => {
  console.log('Detail: Loading meal plan with ID:', props.id)
  loading.value = true
  error.value = null

  try {
    // Force refresh to get latest data
    mealPlan.value = await mealPlanningStore.fetchMealPlan(props.id, true)
    console.log('Detail: Meal plan loaded successfully:', mealPlan.value)
  } catch (err) {
    console.error('Detail: Error loading meal plan:', err)

    // Handle specific error types
    if (err.response?.status === 404) {
      error.value = 'Meal plan not found. It may have been deleted or you may not have access to it.'

      // Show notification and redirect after delay
      notify({
        type: 'warning',
        message: 'Meal plan not found. Redirecting to meal plans page...',
        timeout: 3000
      })

      // Redirect to meal plans page after a delay
      setTimeout(() => {
        router.push({ name: 'meal-plans' })
      }, 3000)
    } else if (err.response?.status === 401) {
      error.value = 'Authentication required. Please enable test mode or log in.'
    } else {
      error.value = err.message || 'Failed to load meal plan'
    }
  } finally {
    loading.value = false
  }
}

const loadRecipes = async () => {
  console.log('Detail: Loading recipes')
  try {
    await recipesStore.fetchRecipes()
    console.log('Detail: Recipes loaded:', recipesStore.recipes.length, 'recipes')
  } catch (err) {
    console.error('Error loading recipes:', err)
  }
}

const showAddMealDialog = (date, mealType) => {
  // Prevent opening dialog if already adding a meal
  if (addingMeal.value) {
    console.log('Detail: Already adding meal, preventing dialog open')
    return
  }

  // Check if meal slot is already occupied
  const dayData = calendarDays.value.find((day) => day.date === date)
  if (dayData && dayData.meals[mealType]) {
    const recipeName = dayData.meals[mealType].recipe?.title || 'Unknown Recipe'
    notify({
      type: 'info',
      message: `${recipeName} is already assigned to ${mealType} on ${formatDate(date)}. Remove it first to assign a different meal.`,
      timeout: 4000,
    })
    return
  }

  console.log('Detail: Opening add meal dialog for', date, mealType)
  console.log('Detail: Available recipes:', recipesStore.recipes.length)
  console.log('Detail: Auth token available:', !!localStorage.getItem('auth_token'))

  // Check if recipes are loaded
  if (recipesStore.recipes.length === 0) {
    notify({
      type: 'warning',
      message: 'Geen recepten beschikbaar. Zorg eerst dat je bent ingelogd en recepten hebt.',
    })
  }

  // Reset dialog state completely
  selectedDate.value = date
  selectedMealType.value = mealType
  newMeal.value = {
    recipe_id: null,
    servings_planned: 1,
    notes: '',
  }

  // Use nextTick to ensure state is properly set before showing dialog
  nextTick(() => {
    showAddMeal.value = true
  })
}

const filterRecipes = (val, update) => {
  update(() => {
    recipeSearchQuery.value = val
  })
}

const addMeal = async () => {
  console.log('Detail: ADD MEAL BUTTON CLICKED!')
  console.log('Detail: Form data:', newMeal.value)
  console.log('Detail: Selected date:', selectedDate.value)
  console.log('Detail: Selected meal type:', selectedMealType.value)

  // Prevent multiple submissions
  if (addingMeal.value) {
    console.log('Detail: Already adding meal, ignoring duplicate request')
    return
  }

  // Check authentication first
  const token = localStorage.getItem('auth_token')
  if (!token) {
    console.log('Detail: No authentication token')
    notify({
      type: 'warning',
      message: 'Authenticatie vereist. Klik op het gebruikersmenu en selecteer "Enable Test Mode"',
    })
    return
  }

  // Validate form data
  if (!newMeal.value.recipe_id) {
    console.log('Detail: Recipe not selected')
    notify({
      type: 'negative',
      message: 'Selecteer een recept',
    })
    return
  }

  if (!newMeal.value.servings_planned || newMeal.value.servings_planned <= 0) {
    console.log('Detail: Invalid servings')
    notify({
      type: 'negative',
      message: 'Voer een geldig aantal porties in',
    })
    return
  }

  console.log('Detail: Adding meal with data:', {
    mealPlanId: props.id,
    date: selectedDate.value,
    meal_type: selectedMealType.value,
    recipe_id: newMeal.value.recipe_id,
    servings_planned: newMeal.value.servings_planned,
    notes: newMeal.value.notes,
  })

  addingMeal.value = true

  try {
    const result = await mealPlanningStore.assignMeal(props.id, {
      date: selectedDate.value,
      meal_type: selectedMealType.value,
      recipe_id: newMeal.value.recipe_id,
      servings_planned: newMeal.value.servings_planned,
      notes: newMeal.value.notes,
    })

    console.log('Detail: Meal assigned successfully:', result)

    // Show success notification with shopping list update option
    notify({
      type: 'positive',
      message: 'Maaltijd succesvol toegevoegd!',
      actions: [
        {
          label: 'Boodschappenlijst Bijwerken',
          color: 'white',
          handler: () => {
            updateShoppingLists()
          },
        },
      ],
      timeout: 5000,
    })

    // Close dialog and reset state immediately for better UX
    showAddMeal.value = false
    resetDialogState()

    // Reload meal plan to get updated data in background
    await loadMealPlan()
  } catch (err) {
    console.error('Detail: Error adding meal:', err)
    console.error('Detail: Error details:', {
      status: err.response?.status,
      statusText: err.response?.statusText,
      data: err.response?.data,
    })

    // Extract error message from API response
    let errorMessage = 'Fout bij toevoegen maaltijd'
    if (err.response?.status === 401) {
      errorMessage = 'Authenticatie vereist. Klik op "Enable Test Mode" in het gebruikersmenu.'
    } else if (err.response?.data?.error) {
      errorMessage = err.response.data.error
    } else if (err.response?.data?.message) {
      errorMessage = err.response.data.message
    } else if (err.response?.data?.detail) {
      errorMessage = err.response.data.detail
    } else if (err.message) {
      errorMessage = err.message
    }

    console.log('Detail: Error message:', errorMessage)

    // Check if it's a "already assigned" error
    if (errorMessage.includes('already assigned') || errorMessage.includes('al toegewezen')) {
      // Reload to show current state first
      await loadMealPlan()

      // Close dialog for "already assigned" since it's not a retry-able error
      showAddMeal.value = false
      resetDialogState()

      notify({
        type: 'warning',
        message: errorMessage,
      })
    } else {
      notify({
        type: 'negative',
        message: errorMessage,
      })
      // Keep dialog open for other errors so user can retry
    }
  } finally {
    addingMeal.value = false
    console.log('Detail: addMeal function completed')
  }
}

// Helper function to reset dialog state
const resetDialogState = () => {
  selectedDate.value = ''
  selectedMealType.value = ''
  recipeSearchQuery.value = ''
  newMeal.value = {
    recipe_id: null,
    servings_planned: 1,
    notes: '',
  }
}

// Handle dialog hide event
const onDialogHide = () => {
  console.log('Detail: Dialog hide event triggered')
  if (!addingMeal.value) {
    resetDialogState()
  }
}

// Handle cancel button click
const cancelAddMeal = () => {
  console.log('Detail: Cancel add meal clicked')
  showAddMeal.value = false
  resetDialogState()
}

const removeMeal = async (assignmentId) => {
  try {
    await mealPlanningStore.removeMealAssignment(assignmentId)
    await loadMealPlan()

    $q.notify({
      type: 'positive',
      message: 'Meal removed successfully!',
    })
  } catch (err) {
    console.error('Error removing meal:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to remove meal',
    })
  }
}

const generateShoppingList = () => {
  router.push({ name: 'shopping-lists', query: { mealPlan: props.id } })
}

const formatDateRange = (startDate, endDate) => {
  const start = new Date(startDate).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })
  const end = new Date(endDate).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
  return `${start} - ${end}`
}

const formatDayHeader = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
  })
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}
</script>

<style scoped>
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.calendar-day {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  background: white;
}

.day-header {
  text-align: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.meals-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meal-slot {
  border: 1px dashed #d0d0d0;
  border-radius: 4px;
  padding: 8px;
  min-height: 60px;
  position: relative;
}

.meal-slot.has-meal {
  border: 1px solid #1976d2;
  background: #f3f8ff;
}

.meal-type-label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-transform: capitalize;
  margin-bottom: 4px;
}

.meal-content {
  position: relative;
}

.meal-name {
  font-weight: 500;
  margin-bottom: 2px;
}

.meal-servings {
  font-size: 12px;
  color: #666;
}

.remove-meal-btn {
  position: absolute;
  top: -4px;
  right: -4px;
}

.empty-meal {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}
</style>
