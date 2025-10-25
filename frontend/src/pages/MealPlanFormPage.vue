<template>
  <q-page class="q-pa-lg">
    <!-- Breadcrumb Navigation -->
    <q-breadcrumbs class="q-mb-md">
      <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
      <q-breadcrumbs-el label="Meal Plans" icon="calendar_today" :to="{ name: 'meal-plans' }" />
      <q-breadcrumbs-el :label="isEditing ? 'Edit Meal Plan' : 'Create New Meal Plan'" />
    </q-breadcrumbs>

    <div class="row justify-between items-center q-mb-lg">
      <div class="text-h4">{{ isEditing ? 'Edit Meal Plan' : 'Create New Meal Plan' }}</div>
      <q-btn
        flat
        icon="arrow_back"
        label="Back to Meal Plans"
        :to="{ name: 'meal-plans' }"
      />
    </div>

    <!-- Form Card -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <q-form @submit="onSubmit" class="q-gutter-md">
          <!-- Meal Plan Name -->
          <q-input
            v-model="form.name"
            label="Meal Plan Name *"
            hint="Give your meal plan a descriptive name"
            outlined
            :rules="[val => !!val || 'Name is required']"
          >
            <template v-slot:prepend>
              <q-icon name="restaurant_menu" />
            </template>
          </q-input>

          <!-- Date Range -->
          <div class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-input
                v-model="form.start_date"
                label="Start Date *"
                type="date"
                outlined
                :rules="[val => !!val || 'Start date is required']"
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-6">
              <q-input
                v-model="form.end_date"
                label="End Date *"
                type="date"
                outlined
                :rules="[
                  val => !!val || 'End date is required',
                  val => !form.start_date || val >= form.start_date || 'End date must be after start date'
                ]"
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>
          </div>

          <!-- Quick Date Presets -->
          <div class="q-mb-md">
            <div class="text-subtitle2 q-mb-sm">Quick Presets:</div>
            <div class="q-gutter-sm">
              <q-btn
                size="sm"
                outline
                color="primary"
                label="This Week"
                @click="setThisWeek"
              />
              <q-btn
                size="sm"
                outline
                color="primary"
                label="Next Week"
                @click="setNextWeek"
              />
              <q-btn
                size="sm"
                outline
                color="primary"
                label="This Month"
                @click="setThisMonth"
              />
            </div>
          </div>

          <!-- Date Range Summary -->
          <q-banner v-if="form.start_date && form.end_date" class="bg-blue-1 text-blue-8">
            <template v-slot:avatar>
              <q-icon name="info" />
            </template>
            <div>
              <strong>{{ totalDays }}</strong> days from
              <strong>{{ formatDate(form.start_date) }}</strong> to
              <strong>{{ formatDate(form.end_date) }}</strong>
            </div>
          </q-banner>

          <!-- Form Actions -->
          <div class="row q-gutter-sm justify-end">
            <q-btn
              flat
              label="Cancel"
              color="grey"
              :to="{ name: 'meal-plans' }"
            />
            <q-btn
              type="submit"
              :label="isEditing ? 'Update Meal Plan' : 'Create Meal Plan'"
              color="primary"
              :loading="loading"
              :disable="!isFormValid"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <!-- Preview Card (when editing) -->
    <q-card v-if="isEditing && mealPlan" class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="preview" class="q-mr-sm" />
          Current Meal Plan Preview
        </div>

        <div class="row q-gutter-md">
          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Total Days</div>
                <div class="text-h6 text-primary">{{ mealPlan.total_days }}</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Assigned Meals</div>
                <div class="text-h6 text-secondary">{{ mealPlan.total_meals || 0 }}</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Created</div>
                <div class="text-body2">{{ formatDate(mealPlan.created_at) }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tips Card -->
    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="lightbulb" class="q-mr-sm" />
          Tips for Creating Meal Plans
        </div>

        <q-list>
          <q-item>
            <q-item-section avatar>
              <q-icon name="schedule" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Plan for a week at a time</q-item-label>
              <q-item-label caption>Weekly planning helps with grocery shopping and preparation</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="restaurant" color="secondary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>After creating, assign recipes to meals</q-item-label>
              <q-item-label caption>You can assign breakfast, lunch, dinner, and snacks for each day</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="shopping_cart" color="accent" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Generate shopping lists automatically</q-item-label>
              <q-item-label caption>Once meals are assigned, create shopping lists from your meal plans</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useMealPlanningStore } from 'src/stores/mealPlanning'

const $q = useQuasar()
const router = useRouter()
const mealPlanningStore = useMealPlanningStore()

// Props for editing
const props = defineProps({
  id: {
    type: String,
    default: null
  }
})

// Form state
const form = ref({
  name: '',
  start_date: '',
  end_date: ''
})

const loading = ref(false)
const mealPlan = ref(null)

// Computed properties
const isEditing = computed(() => !!props.id)

const isFormValid = computed(() => {
  const valid = form.value.name &&
         form.value.start_date &&
         form.value.end_date &&
         form.value.end_date >= form.value.start_date
  console.log('Form validation:', {
    name: form.value.name,
    start_date: form.value.start_date,
    end_date: form.value.end_date,
    valid
  })
  return valid
})

const totalDays = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  const start = new Date(form.value.start_date)
  const end = new Date(form.value.end_date)
  const diffTime = Math.abs(end - start)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
})

// Lifecycle
onMounted(async () => {
  if (isEditing.value) {
    await loadMealPlan()
  } else {
    // Set default to this week for new meal plans
    setThisWeek()
  }
})

// Methods
const safeNotify = (options) => {
  try {
    if ($q && $q.notify) {
      $q.notify(options)
    } else {
      console.log('Notification:', options.message)
    }
  } catch (error) {
    console.error('Notification error:', error)
    console.log('Notification message:', options.message)
  }
}

const loadMealPlan = async () => {
  try {
    loading.value = true
    mealPlan.value = await mealPlanningStore.fetchMealPlan(props.id)

    // Populate form with existing data
    form.value = {
      name: mealPlan.value.name,
      start_date: mealPlan.value.start_date,
      end_date: mealPlan.value.end_date
    }
  } catch (err) {
    console.error('Error loading meal plan:', err)
    safeNotify({
      type: 'negative',
      message: 'Failed to load meal plan'
    })
    router.push({ name: 'meal-plans' })
  } finally {
    loading.value = false
  }
}

const onSubmit = async () => {
  console.log('Form submission started', { form: form.value, isFormValid: isFormValid.value })

  loading.value = true

  try {
    if (isEditing.value) {
      console.log('Updating meal plan:', props.id, form.value)
      await mealPlanningStore.updateMealPlan(props.id, form.value)
      safeNotify({
        type: 'positive',
        message: 'Meal plan updated successfully!'
      })
    } else {
      console.log('Creating new meal plan:', form.value)
      const newMealPlan = await mealPlanningStore.createMealPlan(form.value)
      console.log('Meal plan created:', newMealPlan)
      safeNotify({
        type: 'positive',
        message: 'Meal plan created successfully!'
      })
      // Navigate to the new meal plan detail page
      router.push({ name: 'meal-plan-detail', params: { id: newMealPlan.id } })
      return
    }

    // Navigate back to meal plans list
    router.push({ name: 'meal-plans' })
  } catch (error) {
    console.error('Error in form submission:', error)
    safeNotify({
      type: 'negative',
      message: error.message || `Failed to ${isEditing.value ? 'update' : 'create'} meal plan`
    })
  } finally {
    loading.value = false
  }
}

const setThisWeek = () => {
  const today = new Date()
  const monday = new Date(today)
  monday.setDate(today.getDate() - today.getDay() + 1) // Get Monday

  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6) // Get Sunday

  form.value.start_date = formatDateForInput(monday)
  form.value.end_date = formatDateForInput(sunday)

  if (!form.value.name || form.value.name.includes('Week of')) {
    form.value.name = `Week of ${formatDate(monday)}`
  }
}

const setNextWeek = () => {
  const today = new Date()
  const nextMonday = new Date(today)
  nextMonday.setDate(today.getDate() - today.getDay() + 8) // Get next Monday

  const nextSunday = new Date(nextMonday)
  nextSunday.setDate(nextMonday.getDate() + 6) // Get next Sunday

  form.value.start_date = formatDateForInput(nextMonday)
  form.value.end_date = formatDateForInput(nextSunday)

  if (!form.value.name || form.value.name.includes('Week of')) {
    form.value.name = `Week of ${formatDate(nextMonday)}`
  }
}

const setThisMonth = () => {
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

  form.value.start_date = formatDateForInput(firstDay)
  form.value.end_date = formatDateForInput(lastDay)

  const monthName = firstDay.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  if (!form.value.name || form.value.name.includes('Week of')) {
    form.value.name = `${monthName} Meal Plan`
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateForInput = (date) => {
  return date.toISOString().split('T')[0]
}
</script>
