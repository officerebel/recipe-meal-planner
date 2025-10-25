<template>
  <q-page class="q-pa-lg">
    <!-- Breadcrumb Navigation -->
    <q-breadcrumbs class="q-mb-md">
      <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
      <q-breadcrumbs-el label="Meal Plans" icon="calendar_today" />
    </q-breadcrumbs>

    <div class="row justify-between items-center q-mb-lg">
      <div class="text-h4">Meal Plans</div>
      <q-btn
        color="primary"
        icon="add"
        label="Create Meal Plan"
        :to="{ name: 'meal-plan-create' }"
      />
    </div>

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
        <q-btn flat label="Retry" @click="loadMealPlans" />

      </template>
    </q-banner>

    <!-- Debug Info (Development Only) -->
    <q-card v-if="error && !hasAuthToken" class="bg-orange-1 q-mb-md">
      <q-card-section>
        <div class="text-subtitle2 text-orange-8">
          <q-icon name="bug_report" class="q-mr-sm" />
          Debug Info
        </div>
        <div class="text-body2 q-mt-sm">
          <strong>Issue:</strong> No authentication token found.<br>
          <strong>Solution:</strong> Click "Enable Test Mode" to use the app with test credentials.
        </div>
      </q-card-section>
    </q-card>

    <!-- Empty State -->
    <q-card v-else-if="mealPlans.length === 0" class="text-center q-py-xl">
      <q-card-section>
        <q-icon name="restaurant_menu" size="64px" color="grey-5" />
        <div class="text-h6 q-mt-md">No meal plans yet</div>
        <div class="text-body2 text-grey-7 q-mb-md">
          Create your first meal plan to get started with organized meal planning
        </div>
        <q-btn
          color="primary"
          icon="add"
          label="Create Your First Meal Plan"
          :to="{ name: 'meal-plan-create' }"
        />
      </q-card-section>
    </q-card>

    <!-- Meal Plans Grid -->
    <div v-else class="row q-gutter-md">
      <div v-for="mealPlan in mealPlans" :key="mealPlan.id" class="col-12 col-md-6 col-lg-4">
        <q-card class="meal-plan-card cursor-pointer" @click="viewMealPlan(mealPlan.id)">
          <q-card-section>
            <div class="text-h6 q-mb-sm">{{ mealPlan.name }}</div>
            <div class="text-body2 text-grey-7 q-mb-md">
              {{ formatDateRange(mealPlan.start_date, mealPlan.end_date) }}
            </div>

            <!-- Stats -->
            <div class="row q-gutter-md">
              <div class="col">
                <div class="text-caption text-grey-6">Days</div>
                <div class="text-h6 text-primary">{{ mealPlan.total_days }}</div>
              </div>
              <div class="col">
                <div class="text-caption text-grey-6">Meals</div>
                <div class="text-h6 text-secondary">{{ mealPlan.total_meals || 0 }}</div>
              </div>
            </div>

            <!-- Progress Bar -->
            <q-linear-progress
              v-if="mealPlan.total_days > 0"
              :value="(mealPlan.total_meals || 0) / (mealPlan.total_days * 3)"
              color="primary"
              class="q-mt-md"
            />
            <div class="text-caption text-grey-6 q-mt-xs">
              {{ Math.round(((mealPlan.total_meals || 0) / (mealPlan.total_days * 3)) * 100) }}%
              planned
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn
              flat
              icon="visibility"
              label="View"
              color="primary"
              @click.stop="viewMealPlan(mealPlan.id)"
            />
            <q-btn
              flat
              icon="edit"
              label="Edit"
              color="secondary"
              @click.stop="editMealPlan(mealPlan.id)"
            />
            <q-btn flat icon="delete" color="negative" @click.stop="confirmDelete(mealPlan)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Delete Meal Plan</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete "{{ mealPlanToDelete?.name }}"? This action cannot be
          undone.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn flat label="Delete" color="negative" @click="deleteMealPlan" :loading="deleting" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useMealPlanningStore } from 'src/stores/mealPlanning'


const $q = useQuasar()
const router = useRouter()
const mealPlanningStore = useMealPlanningStore()

// State
const showDeleteDialog = ref(false)
const mealPlanToDelete = ref(null)
const deleting = ref(false)

// Computed
const mealPlans = computed(() => {
  console.log('MealPlansPage: Computing meal plans:', mealPlanningStore.mealPlans.length, 'plans')
  return mealPlanningStore.mealPlans
})
const loading = computed(() => {
  console.log('MealPlansPage: Loading state:', mealPlanningStore.loading)
  return mealPlanningStore.loading
})
const error = computed(() => {
  console.log('MealPlansPage: Error state:', mealPlanningStore.error)
  return mealPlanningStore.error
})

const hasAuthToken = computed(() => {
  return !!localStorage.getItem('auth_token')
})

// Lifecycle
onMounted(() => {
  console.log('MealPlansPage: Component mounted, loading meal plans')
  loadMealPlans()
})

// Methods


const loadMealPlans = async () => {
  console.log('MealPlansPage: Loading meal plans')
  // Clear any previous errors
  mealPlanningStore.clearError()

  try {
    await mealPlanningStore.fetchMealPlans(true) // Force refresh to get latest data
    console.log('MealPlansPage: Meal plans loaded:', mealPlanningStore.mealPlans.length, 'plans')
  } catch (err) {
    console.error('MealPlansPage: Error loading meal plans:', err)
    // Error is already set in the store by fetchMealPlans
  }
}

const viewMealPlan = (id) => {
  console.log('MealPlansPage: Navigating to meal plan detail:', id)
  router.push({ name: 'meal-plan-detail', params: { id } })
}

const editMealPlan = (id) => {
  router.push({ name: 'meal-plan-edit', params: { id } })
}

const confirmDelete = (mealPlan) => {
  mealPlanToDelete.value = mealPlan
  showDeleteDialog.value = true
}

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

const deleteMealPlan = async () => {
  if (!mealPlanToDelete.value) return

  console.log('Deleting meal plan:', mealPlanToDelete.value.id)
  deleting.value = true
  try {
    await mealPlanningStore.deleteMealPlan(mealPlanToDelete.value.id)
    console.log('Meal plan deleted successfully')
    safeNotify({
      type: 'positive',
      message: 'Meal plan deleted successfully',
    })
    showDeleteDialog.value = false
    mealPlanToDelete.value = null
  } catch (err) {
    console.error('Error deleting meal plan:', err)
    safeNotify({
      type: 'negative',
      message: 'Failed to delete meal plan',
    })
  } finally {
    deleting.value = false
  }
}

const formatDateRange = (startDate, endDate) => {
  const start = new Date(startDate).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
  const end = new Date(endDate).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
  return `${start} - ${end}`
}
</script>

<style scoped>
.meal-plan-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.meal-plan-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
