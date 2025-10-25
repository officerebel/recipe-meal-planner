<template>
  <q-page class="q-pa-lg">
    <div class="row q-gutter-lg">
      <!-- Welcome Section -->
      <div class="col-12">
        <q-card class="bg-primary text-white">
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="col">
                <div class="text-h4 q-mb-sm">Welcome to Recipe Meal Planner</div>
                <div class="text-subtitle1">
                  Organize your recipes, plan your meals, and generate shopping lists effortlessly.
                </div>
              </div>

            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Meals Section -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <!-- View Tabs -->
            <q-tabs v-model="activeView" class="text-grey-7 q-mb-md">
              <q-tab name="day" label="Dag Weergave" icon="today" />
              <q-tab name="week" label="Week Weergave" icon="view_week" />
            </q-tabs>

            <q-tab-panels v-model="activeView" animated>
              <!-- Day View -->
              <q-tab-panel name="day">
                <div class="row items-center justify-between q-mb-md">
                  <q-btn
                    flat
                    round
                    icon="chevron_left"
                    @click="previousDay"
                    :disable="isToday && selectedDateOffset === 0"
                    class="date-navigation"
                  />

                  <div class="text-center">
                    <div class="text-h6">
                      <q-icon name="today" class="q-mr-sm" />
                      {{ selectedDateLabel }}
                    </div>
                    <div class="text-subtitle2 text-grey-6">
                      {{ selectedDateFormatted }}
                    </div>
                  </div>

                  <q-btn
                    flat
                    round
                    icon="chevron_right"
                    @click="nextDay"
                    class="date-navigation"
                  />
                </div>

                <!-- Loading State -->
                <div v-if="loading.meals" class="text-center q-py-xl">
                  <q-spinner-dots size="48px" color="primary" />
                  <div class="text-subtitle2 q-mt-md">Maaltijden laden...</div>
                </div>

                <!-- Meals for Selected Day -->
                <div v-else-if="selectedDayMeals.length > 0" class="q-gutter-md">
                  <div
                    v-for="meal in selectedDayMeals"
                    :key="`${meal.meal_type}-${meal.recipe.id}`"
                    class="meal-card"
                  >
                    <q-card
                      class="cursor-pointer"
                      @click="$router.push({ name: 'recipe-detail', params: { id: meal.recipe.id } })"
                    >
                      <q-card-section class="row items-center">
                        <div class="col-auto q-mr-md">
                          <q-avatar
                            :color="getMealColor(meal.meal_type)"
                            text-color="white"
                            :icon="getMealIcon(meal.meal_type)"
                          />
                        </div>
                        <div class="col">
                          <div class="text-subtitle1 text-weight-medium">
                            {{ meal.recipe.title }}
                          </div>
                          <div class="text-caption text-grey-6 text-capitalize">
                            {{ getMealTypeLabel(meal.meal_type) }}
                            <span v-if="meal.servings_planned">
                              • {{ meal.servings_planned }} porties
                            </span>
                          </div>
                          <div v-if="meal.notes" class="text-caption text-grey-7 q-mt-xs">
                            {{ meal.notes }}
                          </div>
                        </div>
                        <div class="col-auto">
                          <q-icon name="chevron_right" color="grey-5" />
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>

                <div v-else-if="!loading.meals" class="text-center text-grey-6 q-py-xl">
                  <q-icon name="restaurant" size="4rem" class="q-mb-md" />
                  <div class="text-h6">Geen maaltijden gepland</div>
                  <div class="text-subtitle2">
                    Voeg maaltijden toe aan je planning
                  </div>
                  <div class="q-mt-md q-gutter-sm">
                    <q-btn
                      color="primary"
                      label="Maaltijd Plannen"
                      @click="$router.push('/meal-plans')"
                    />
                    <q-btn
                      color="secondary"
                      label="Boodschappenlijst Maken"
                      @click="generateShoppingList"
                      :disable="!hasAnyMeals"
                    />
                  </div>
                </div>
              </q-tab-panel>

              <!-- Week View -->
              <q-tab-panel name="week">
                <div class="row items-center justify-between q-mb-md">
                  <q-btn
                    flat
                    round
                    icon="chevron_left"
                    @click="previousWeek"
                  />

                  <div class="text-h6 text-center">
                    <q-icon name="view_week" class="q-mr-sm" />
                    Week {{ weekNumber }} - {{ weekDateRange }}
                  </div>

                  <q-btn
                    flat
                    round
                    icon="chevron_right"
                    @click="nextWeek"
                  />
                </div>

                <!-- Week Loading State -->
                <div v-if="loading.week" class="text-center q-py-xl">
                  <q-spinner-grid size="48px" color="primary" />
                  <div class="text-subtitle2 q-mt-md">Week overzicht laden...</div>
                </div>

                <!-- Week Grid -->
                <div v-else class="week-grid">
                  <div
                    v-for="day in weekDays"
                    :key="day.dateString"
                    class="day-column"
                  >
                    <div class="day-header">
                      <div class="text-subtitle2 text-weight-medium">
                        {{ day.dayName }}
                      </div>
                      <div class="text-caption text-grey-6">
                        {{ day.dayNumber }}
                      </div>
                    </div>

                    <div class="day-meals">
                      <div
                        v-for="meal in day.meals"
                        :key="`${day.dateString}-${meal.meal_type}-${meal.recipe.id}`"
                        class="week-meal-card"
                        @click="$router.push({ name: 'recipe-detail', params: { id: meal.recipe.id } })"
                      >
                        <div class="meal-type-indicator">
                          <q-icon
                            :name="getMealIcon(meal.meal_type)"
                            :color="getMealColor(meal.meal_type)"
                            size="xs"
                          />
                        </div>
                        <div class="meal-title">{{ meal.recipe.title }}</div>
                        <div class="meal-time text-caption text-grey-6">
                          {{ meal.recipe.prep_time || 0 }}min
                        </div>
                      </div>

                      <div v-if="day.meals.length === 0" class="no-meals text-center text-grey-5">
                        <q-icon name="restaurant" size="sm" />
                        <div class="text-caption">Geen maaltijden</div>
                      </div>
                    </div>
                  </div>
                </div>
              </q-tab-panel>
            </q-tab-panels>
          </q-card-section>
        </q-card>
      </div>

      <!-- Statistics Section -->
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="analytics" class="q-mr-sm" />
              Statistics
            </div>
            <div v-if="statistics" class="row q-gutter-md">
              <div class="col">
                <q-card class="bg-blue-1">
                  <q-card-section class="text-center">
                    <div class="text-h4 text-blue">{{ statistics.total_recipes }}</div>
                    <div class="text-caption">Total Recipes</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col">
                <q-card class="bg-green-1">
                  <q-card-section class="text-center">
                    <div class="text-h4 text-green">{{ statistics.total_meal_plans }}</div>
                    <div class="text-caption">Meal Plans</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Recent Recipes Section -->
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="restaurant_menu" class="q-mr-sm" />
              Recent Recipes
            </div>
            <div v-if="recentRecipes.length > 0" class="q-gutter-sm">
              <div
                v-for="recipe in recentRecipes"
                :key="recipe.id"
                class="cursor-pointer"
                @click="$router.push({ name: 'recipe-detail', params: { id: recipe.id } })"
              >
                <q-card class="recipe-card">
                  <q-card-section>
                    <div class="text-subtitle1 text-weight-medium">
                      {{ recipe.title }}
                    </div>
                    <div class="text-caption text-grey-6">
                      {{ recipe.categories.join(', ') }}
                    </div>
                    <div class="text-caption">
                      <q-icon name="schedule" size="xs" />
                      {{ recipe.prep_time || 0 }}min prep
                      <span v-if="recipe.cook_time">
                        + {{ recipe.cook_time }}min cook
                      </span>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
            <div v-else class="text-grey-6">
              No recipes yet. Start by importing or creating your first recipe!
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useRecipeStore } from 'src/stores/recipes'
import { useMealPlanningStore } from 'src/stores/mealPlanning'


const $router = useRouter()
const $q = useQuasar()
const recipeStore = useRecipeStore()
const mealPlanningStore = useMealPlanningStore()

const statistics = ref(null)
const recentRecipes = ref([])
const selectedDateOffset = ref(0) // 0 = today, 1 = tomorrow, -1 = yesterday
const selectedWeekOffset = ref(0) // 0 = this week, 1 = next week, -1 = last week
const allMealsData = ref(new Map()) // Cache meals for different dates
const activeView = ref('day') // 'day' or 'week'
const loading = ref({
  meals: false,
  week: false,
  statistics: false,
  recipes: false
})

const selectedDate = computed(() => {
  const now = new Date()
  now.setDate(now.getDate() + selectedDateOffset.value)
  return now
})

const selectedDateString = computed(() => {
  return selectedDate.value.toISOString().split('T')[0] // YYYY-MM-DD format
})

const selectedDateFormatted = computed(() => {
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }
  return selectedDate.value.toLocaleDateString('nl-NL', options)
})

const selectedDateLabel = computed(() => {
  if (selectedDateOffset.value === 0) return 'Vandaag'
  if (selectedDateOffset.value === 1) return 'Morgen'
  if (selectedDateOffset.value === -1) return 'Gisteren'

  const daysDiff = Math.abs(selectedDateOffset.value)
  if (selectedDateOffset.value > 0) {
    return `Over ${daysDiff} dagen`
  } else {
    return `${daysDiff} dagen geleden`
  }
})

const isToday = computed(() => selectedDateOffset.value === 0)

const selectedDayMeals = computed(() => {
  return allMealsData.value.get(selectedDateString.value) || []
})

const hasAnyMeals = computed(() => {
  for (const meals of allMealsData.value.values()) {
    if (meals.length > 0) return true
  }
  return false
})



// Week view computed properties
const weekStartDate = computed(() => {
  const now = new Date()
  const dayOfWeek = now.getDay() // 0 = Sunday, 1 = Monday, etc.
  const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek // Get Monday of current week

  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() + mondayOffset + (selectedWeekOffset.value * 7))
  return weekStart
})

const weekNumber = computed(() => {
  const date = weekStartDate.value
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1)
  const pastDaysOfYear = (date - firstDayOfYear) / 86400000
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7)
})

const weekDateRange = computed(() => {
  const start = weekStartDate.value
  const end = new Date(start)
  end.setDate(start.getDate() + 6)

  const options = { day: 'numeric', month: 'short' }
  const startStr = start.toLocaleDateString('nl-NL', options)
  const endStr = end.toLocaleDateString('nl-NL', options)

  return `${startStr} - ${endStr}`
})

const weekDays = computed(() => {
  const days = []
  const startDate = weekStartDate.value

  const dayNames = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']

  for (let i = 0; i < 7; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    const dateString = date.toISOString().split('T')[0]
    const meals = allMealsData.value.get(dateString) || []

    days.push({
      dateString,
      dayName: dayNames[i],
      dayNumber: date.getDate(),
      date,
      meals: meals.sort((a, b) => {
        const mealOrder = { breakfast: 0, lunch: 1, dinner: 2, snack: 3, dessert: 4 }
        return (mealOrder[a.meal_type] || 5) - (mealOrder[b.meal_type] || 5)
      })
    })
  }

  return days
})

// Helper methods for meal display
const getMealIcon = (mealType) => {
  const icons = {
    'breakfast': 'free_breakfast',
    'lunch': 'lunch_dining',
    'dinner': 'dinner_dining',
    'snack': 'cookie',
    'dessert': 'cake'
  }
  return icons[mealType] || 'restaurant'
}

const getMealColor = (mealType) => {
  const colors = {
    'breakfast': 'orange',
    'lunch': 'green',
    'dinner': 'blue',
    'snack': 'purple',
    'dessert': 'pink'
  }
  return colors[mealType] || 'grey'
}

const getMealTypeLabel = (mealType) => {
  const labels = {
    'breakfast': 'Ontbijt',
    'lunch': 'Lunch',
    'dinner': 'Diner',
    'snack': 'Tussendoortje',
    'dessert': 'Nagerecht'
  }
  return labels[mealType] || mealType
}

// Navigation methods
const previousDay = () => {
  selectedDateOffset.value -= 1
  loadMealsForSelectedDate()
}

const nextDay = () => {
  selectedDateOffset.value += 1
  loadMealsForSelectedDate()
}

// Week navigation methods
const previousWeek = () => {
  selectedWeekOffset.value -= 1
  loadWeekMeals()
}

const nextWeek = () => {
  selectedWeekOffset.value += 1
  loadWeekMeals()
}



const generateShoppingList = async () => {
  try {
    // Get current week's meal plans
    const currentMealPlans = mealPlanningStore.mealPlans || []

    if (currentMealPlans.length === 0) {
      $q.notify({
        type: 'warning',
        message: 'Geen maaltijdplannen gevonden om een boodschappenlijst te maken'
      })
      return
    }

    // Navigate to shopping list creation with current meal plans
    $router.push({
      name: 'shopping-lists',
      query: {
        generate: 'true',
        mealPlans: currentMealPlans.map(mp => mp.id).join(',')
      }
    })
  } catch (error) {
    console.error('Error generating shopping list:', error)
    $q.notify({
      type: 'negative',
      message: 'Fout bij het maken van boodschappenlijst'
    })
  }
}

const loadMealsForSelectedDate = async () => {
  const dateString = selectedDateString.value

  // Check if we already have data for this date
  if (allMealsData.value.has(dateString)) {
    return
  }

  loading.value.meals = true

  try {
    // Fetch all meal plans if not already loaded
    if (!mealPlanningStore.mealPlans.length) {
      await mealPlanningStore.fetchMealPlans()
    }

    const allMealPlans = mealPlanningStore.mealPlans || []
    const mealsForDate = []

    for (const mealPlan of allMealPlans) {
      // Check if selected date falls within this meal plan's date range
      if (dateString >= mealPlan.start_date && dateString <= mealPlan.end_date) {
        try {
          // Fetch detailed meal plan to get daily_meals
          const detailedMealPlan = await mealPlanningStore.fetchMealPlan(mealPlan.id)

          if (detailedMealPlan && detailedMealPlan.daily_meals) {
            const dayMealPlan = detailedMealPlan.daily_meals.find(dm => dm.date === dateString)
            if (dayMealPlan && dayMealPlan.meal_assignments) {
              mealsForDate.push(...dayMealPlan.meal_assignments)
            }
          }
        } catch (error) {
          console.error(`Error fetching detailed meal plan ${mealPlan.id}:`, error)
        }
      }
    }

    // Cache the meals for this date
    allMealsData.value.set(dateString, mealsForDate)
  } catch (error) {
    console.error('Error loading meals for selected date:', error)
  } finally {
    loading.value.meals = false
  }
}

const loadWeekMeals = async () => {
  loading.value.week = true

  try {
    // Get all dates for the current week
    const weekStart = weekStartDate.value
    const datesToLoad = []

    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStart)
      date.setDate(weekStart.getDate() + i)
      const dateString = date.toISOString().split('T')[0]

      if (!allMealsData.value.has(dateString)) {
        datesToLoad.push(dateString)
      }
    }

    if (datesToLoad.length === 0) return

    // Fetch all meal plans if not already loaded
    if (!mealPlanningStore.mealPlans.length) {
      await mealPlanningStore.fetchMealPlans()
    }

    const allMealPlans = mealPlanningStore.mealPlans || []

    // Load meals for each date in the week
    for (const dateString of datesToLoad) {
      const mealsForDate = []

      for (const mealPlan of allMealPlans) {
        if (dateString >= mealPlan.start_date && dateString <= mealPlan.end_date) {
          try {
            const detailedMealPlan = await mealPlanningStore.fetchMealPlan(mealPlan.id)

            if (detailedMealPlan && detailedMealPlan.daily_meals) {
              const dayMealPlan = detailedMealPlan.daily_meals.find(dm => dm.date === dateString)
              if (dayMealPlan && dayMealPlan.meal_assignments) {
                mealsForDate.push(...dayMealPlan.meal_assignments)
              }
            }
          } catch (error) {
            console.error(`Error fetching detailed meal plan ${mealPlan.id}:`, error)
          }
        }
      }

      allMealsData.value.set(dateString, mealsForDate)
    }
  } catch (error) {
    console.error('Error loading week meals:', error)
  } finally {
    loading.value.week = false
  }
}

const loadInitialData = async () => {
  try {
    // Load today's meals first
    await loadMealsForSelectedDate()

    // Load current week meals for week view
    await loadWeekMeals()

    // Pre-load tomorrow's meals for faster navigation
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowString = tomorrow.toISOString().split('T')[0]

    if (!allMealsData.value.has(tomorrowString)) {
      // Load tomorrow's meals in background
      setTimeout(async () => {
        const originalOffset = selectedDateOffset.value
        selectedDateOffset.value = 1
        await loadMealsForSelectedDate()
        selectedDateOffset.value = originalOffset
      }, 1000)
    }
  } catch (error) {
    console.error('Error loading initial meal data:', error)
  }
}

onMounted(async () => {
  try {
    // Fetch statistics
    await recipeStore.fetchStatistics()
    statistics.value = recipeStore.statistics

    // Fetch recent recipes (first page)
    await recipeStore.fetchRecipes(true)
    recentRecipes.value = recipeStore.recipes.slice(0, 6) // Show first 6 recipes

    // Load initial meal data
    await loadInitialData()
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  }
})
</script>
<style scoped>
.meal-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.meal-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.recipe-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.recipe-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.text-capitalize {
  text-transform: capitalize;
}

.date-navigation {
  min-width: 300px;
}

.date-navigation .q-btn {
  transition: all 0.2s;
}

.date-navigation .q-btn:hover:not(.disabled) {
  background-color: rgba(25, 118, 210, 0.1);
  transform: scale(1.1);
}

/* Week View Styles */
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.day-column {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  min-height: 200px;
}

.day-header {
  background-color: #f5f5f5;
  padding: 8px 12px;
  text-align: center;
  border-bottom: 1px solid #e0e0e0;
}

.day-meals {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.week-meal-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.week-meal-card:hover {
  background-color: #f0f8ff;
  border-color: #1976d2;
  transform: translateY(-1px);
}

.meal-type-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.meal-title {
  font-weight: 500;
  line-height: 1.2;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meal-time {
  font-size: 10px;
}

.no-meals {
  padding: 20px 8px;
  opacity: 0.6;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .week-grid {
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
  }
}

@media (max-width: 1024px) {
  .week-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .day-column {
    min-height: 180px;
  }

  .week-meal-card {
    padding: 6px;
    font-size: 11px;
  }
}

@media (max-width: 768px) {
  .week-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }

  .day-column {
    min-height: 160px;
  }

  .day-header {
    padding: 6px 8px;
  }

  .meal-title {
    font-size: 11px;
  }

  .meal-time {
    font-size: 9px;
  }
}

@media (max-width: 600px) {
  .week-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }

  .day-column {
    min-height: 140px;
  }
}

@media (max-width: 480px) {
  .week-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .day-column {
    min-height: 120px;
  }

  .day-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .week-meal-card {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .meal-type-indicator {
    margin-bottom: 0;
    flex-shrink: 0;
  }

  .meal-title {
    flex: 1;
    margin-bottom: 0;
  }

  .meal-time {
    flex-shrink: 0;
  }
}
</style>
