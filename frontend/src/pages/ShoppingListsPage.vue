<template>
  <q-page class="q-pa-lg">
    <!-- Breadcrumb Navigation -->
    <q-breadcrumbs class="q-mb-md">
      <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
      <q-breadcrumbs-el label="Shopping Lists" icon="shopping_cart" />
    </q-breadcrumbs>

    <!-- Update Notification -->
    <q-banner v-if="showUpdateNotification" class="bg-info text-white q-mb-md">
      <template v-slot:avatar>
        <q-icon name="update" />
      </template>
      Maaltijdplan is gewijzigd. Boodschappenlijsten kunnen verouderd zijn.
      <template v-slot:action>
        <q-btn flat label="Alles Bijwerken" @click="updateAllShoppingLists" />
        <q-btn flat label="Sluiten" @click="showUpdateNotification = false" />
      </template>
    </q-banner>

    <!-- Mobile-friendly header -->
    <div class="row justify-between items-center q-mb-lg">
      <div class="text-h4 col-grow">Shopping Lists</div>
      <q-btn
        color="primary"
        icon="add"
        :label="$q.screen.xs ? '' : 'Generate Shopping List'"
        @click="showGenerateDialog = true"
        :round="$q.screen.xs"
        :size="$q.screen.xs ? 'md' : undefined"
      >
        <q-tooltip v-if="$q.screen.xs">Generate Shopping List</q-tooltip>
      </q-btn>
    </div>

    <!-- Personal vs Family Tabs -->
    <q-tabs v-model="activeTab" class="text-grey-7 q-mb-md">
      <q-tab name="personal" label="My Shopping Lists" icon="person" />
      <q-tab name="family" label="Family Shopping Lists" icon="family_restroom" />
    </q-tabs>

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
        <q-btn flat label="Retry" @click="loadShoppingLists" />

      </template>
    </q-banner>

    <!-- Empty State -->
    <q-card v-else-if="shoppingLists.length === 0" class="text-center q-py-xl">
      <q-card-section>
        <q-icon name="shopping_cart" size="64px" color="grey-5" />
        <div class="text-h6 q-mt-md">No shopping lists yet</div>
        <div class="text-body2 text-grey-7 q-mb-md">
          Generate shopping lists from your meal plans to organize your grocery shopping
        </div>
        <q-btn
          color="primary"
          icon="add"
          label="Generate Your First Shopping List"
          @click="showGenerateDialog = true"
        />
      </q-card-section>
    </q-card>

    <!-- Shopping Lists Grid - Mobile optimized -->
    <div v-else class="row q-gutter-md">
      <div
        v-for="shoppingList in shoppingLists"
        :key="shoppingList.id"
        class="col-12 col-sm-6 col-md-4"
      >
        <q-card
          class="shopping-list-card cursor-pointer"
          @click="viewShoppingList(shoppingList.id)"
        >
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <div class="text-h6">{{ shoppingList.name }}</div>
              <q-chip
                v-if="isShoppingListOutdated(shoppingList)"
                color="warning"
                text-color="white"
                size="sm"
                icon="update"
                label="Bijwerken?"
              />
            </div>
            <div class="text-body2 text-grey-7 q-mb-md">
              {{ formatDateRange(shoppingList.start_date, shoppingList.end_date) }}
            </div>

            <!-- Stats -->
            <div class="row q-gutter-md">
              <div class="col">
                <div class="text-caption text-grey-6">Items</div>
                <div class="text-h6 text-primary">{{ shoppingList.total_items || 0 }}</div>
              </div>
              <div class="col">
                <div class="text-caption text-grey-6">Purchased</div>
                <div class="text-h6 text-positive">{{ shoppingList.purchased_items || 0 }}</div>
              </div>
            </div>

            <!-- Progress Bar -->
            <q-linear-progress
              v-if="shoppingList.total_items > 0"
              :value="(shoppingList.purchased_items || 0) / shoppingList.total_items"
              color="positive"
              class="q-mt-md"
            />
            <div class="text-caption text-grey-6 q-mt-xs">
              {{
                Math.round(
                  ((shoppingList.purchased_items || 0) / (shoppingList.total_items || 1)) * 100,
                )
              }}% complete
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn
              flat
              icon="visibility"
              :label="$q.screen.xs ? '' : 'View'"
              color="primary"
              @click.stop="viewShoppingList(shoppingList.id)"
              :size="$q.screen.xs ? 'sm' : undefined"
            >
              <q-tooltip v-if="$q.screen.xs">View Shopping List</q-tooltip>
            </q-btn>
            <q-btn
              flat
              icon="delete"
              color="negative"
              @click.stop="confirmDelete(shoppingList)"
              :size="$q.screen.xs ? 'sm' : undefined"
            >
              <q-tooltip v-if="$q.screen.xs">Delete Shopping List</q-tooltip>
            </q-btn>
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Generate Shopping List Dialog -->
    <q-dialog v-model="showGenerateDialog" ref="generateDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="row items-center justify-between">
            <div class="text-h6">Generate Shopping List</div>
            <q-btn flat round dense icon="close" @click="showGenerateDialog = false" />
          </div>
        </q-card-section>

        <q-card-section>
          <q-form
            @submit.prevent="generateShoppingList"
            @validation-error="onValidationError"
            class="q-gutter-md"
          >
            <q-input
              v-model="newShoppingList.name"
              label="Shopping List Name *"
              outlined
              :rules="[(val) => !!val || 'Name is required']"
              :disable="generating"
            />

            <q-select
              v-model="newShoppingList.listType"
              :options="listTypeOptions"
              label="Shopping List Type *"
              outlined
              emit-value
              map-options
              :rules="[(val) => !!val || 'Please select a type']"
              :disable="generating"
            >
              <template v-slot:prepend>
                <q-icon :name="newShoppingList.listType === 'family' ? 'family_restroom' : 'person'" />
              </template>
            </q-select>

            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model="newShoppingList.start_date"
                  label="Start Date *"
                  type="date"
                  outlined
                  :rules="[(val) => !!val || 'Start date is required']"
                  :disable="generating"
                />
              </div>
              <div class="col">
                <q-input
                  v-model="newShoppingList.end_date"
                  label="End Date *"
                  type="date"
                  outlined
                  :rules="[(val) => !!val || 'End date is required']"
                  :disable="generating"
                />
              </div>
            </div>

            <q-select
              v-model="newShoppingList.meal_plan_ids"
              :options="mealPlanOptions"
              option-value="id"
              option-label="name"
              label="Select Meal Plans *"
              multiple
              outlined
              emit-value
              map-options
              :rules="[(val) => (val && val.length > 0) || 'At least one meal plan is required']"
              :disable="generating"
              @update:model-value="onMealPlansSelected"
            />

            <div class="row q-gutter-sm justify-end">
              <q-btn flat label="Cancel" @click="cancelGenerate" :disable="generating" />
              <q-btn
                type="submit"
                label="Generate"
                color="primary"
                :loading="generating"
                :disable="generating"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Delete Shopping List</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete "{{ shoppingListToDelete?.name }}"? This action cannot be
          undone.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn
            flat
            label="Delete"
            color="negative"
            @click="deleteShoppingList"
            :loading="deleting"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useMealPlanningStore } from 'src/stores/mealPlanning'


const $q = useQuasar()
const router = useRouter()
const mealPlanningStore = useMealPlanningStore()

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

// State
const showUpdateNotification = ref(false)
const loading = ref(false)
const error = ref(null)
const activeTab = ref('personal')
const showGenerateDialog = ref(false)
const showDeleteDialog = ref(false)
const shoppingListToDelete = ref(null)
const generating = ref(false)
const deleting = ref(false)
const generateDialog = ref(null)

const newShoppingList = ref({
  name: '',
  start_date: '',
  end_date: '',
  meal_plan_ids: [],
  listType: 'personal', // 'personal' or 'family'
})

const listTypeOptions = [
  { label: 'Personal Shopping List', value: 'personal', icon: 'person' },
  { label: 'Family Shopping List', value: 'family', icon: 'family_restroom' }
]

// Computed
const mealPlanOptions = computed(() => mealPlanningStore.mealPlans)

const shoppingLists = computed(() => {
  const lists = mealPlanningStore.shoppingLists[activeTab.value] || []
  console.log(`ShoppingLists computed: activeTab=${activeTab.value}, lists=`, lists)
  return lists
})



// Watch for tab changes to reload data
watch(activeTab, async (newTab) => {
  console.log('ShoppingLists: Tab changed to:', newTab)
  await loadShoppingLists(true) // Force refresh when switching tabs
})

// Lifecycle
onMounted(async () => {
  await loadShoppingLists()
  await loadMealPlans()

  // Check if there's a meal plan ID in the URL query params
  const urlParams = new URLSearchParams(window.location.search)
  const mealPlanId = urlParams.get('mealPlan')
  const shouldUpdate = urlParams.get('update')

  if (shouldUpdate === 'true') {
    showUpdateNotification.value = true
    notify({
      type: 'info',
      message: 'Maaltijdplan gewijzigd - controleer je boodschappenlijsten',
      timeout: 4000
    })
  }

  if (mealPlanId) {
    console.log('ShoppingLists: Pre-selecting meal plan from URL:', mealPlanId)
    // Wait a bit for meal plans to load, then pre-select
    setTimeout(() => {
      newShoppingList.value.meal_plan_ids = [mealPlanId]
      onMealPlansSelected([mealPlanId])
      showGenerateDialog.value = true
    }, 500)
  }
})

// Update methods


const updateAllShoppingLists = async () => {
  try {
    notify({
      type: 'info',
      message: 'Alle boodschappenlijsten worden bijgewerkt...',
      timeout: 2000
    })

    // For now, just reload the shopping lists
    // In a real implementation, you would call an API to regenerate all lists
    await loadShoppingLists(true) // Force refresh

    showUpdateNotification.value = false

    notify({
      type: 'positive',
      message: 'Boodschappenlijsten bijgewerkt!',
      timeout: 3000
    })
  } catch (error) {
    console.error('Error updating shopping lists:', error)
    notify({
      type: 'negative',
      message: 'Fout bij bijwerken boodschappenlijsten'
    })
  }
}

// Methods
const loadShoppingLists = async (forceRefresh = false) => {
  loading.value = true
  error.value = null

  try {
    await mealPlanningStore.fetchShoppingLists(forceRefresh, activeTab.value)
  } catch (err) {
    console.error('Error loading shopping lists:', err)
    error.value = 'Failed to load shopping lists'
  } finally {
    loading.value = false
  }
}

const loadMealPlans = async () => {
  console.log('ShoppingLists: Loading meal plans')
  try {
    await mealPlanningStore.fetchMealPlans()
    console.log('ShoppingLists: Meal plans loaded:', mealPlanningStore.mealPlans.length, 'plans')
    console.log('ShoppingLists: Meal plan options:', mealPlanOptions.value)
  } catch (err) {
    console.error('ShoppingLists: Error loading meal plans:', err)
  }
}

const onMealPlansSelected = (selectedIds) => {
  console.log('ShoppingLists: Meal plans selected:', selectedIds)

  if (!selectedIds || selectedIds.length === 0) {
    // Clear dates if no meal plans selected
    newShoppingList.value.start_date = ''
    newShoppingList.value.end_date = ''
    newShoppingList.value.name = ''
    return
  }

  // Find the selected meal plans
  const selectedPlans = mealPlanOptions.value.filter((plan) => selectedIds.includes(plan.id))
  console.log('ShoppingLists: Selected meal plans:', selectedPlans)

  if (selectedPlans.length > 0) {
    // Calculate the date range from all selected meal plans
    const startDates = selectedPlans.map((plan) => new Date(plan.start_date))
    const endDates = selectedPlans.map((plan) => new Date(plan.end_date))

    const earliestStart = new Date(Math.min(...startDates))
    const latestEnd = new Date(Math.max(...endDates))

    // Format dates as YYYY-MM-DD for the date inputs
    newShoppingList.value.start_date = earliestStart.toISOString().split('T')[0]
    newShoppingList.value.end_date = latestEnd.toISOString().split('T')[0]

    // Generate a suggested name
    if (selectedPlans.length === 1) {
      newShoppingList.value.name = `Shopping List for ${selectedPlans[0].name}`
    } else {
      const dateRange = `${earliestStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${latestEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
      newShoppingList.value.name = `Shopping List for ${dateRange}`
    }

    console.log('ShoppingLists: Auto-populated form:', {
      name: newShoppingList.value.name,
      start_date: newShoppingList.value.start_date,
      end_date: newShoppingList.value.end_date,
    })
  }
}

const generateShoppingList = async () => {
  console.log('ShoppingLists: Starting to generate shopping list with data:', newShoppingList.value)

  // Validate required fields
  if (!newShoppingList.value.name) {
    notify({
      type: 'negative',
      message: 'Please enter a shopping list name',
    })
    return
  }

  if (!newShoppingList.value.start_date || !newShoppingList.value.end_date) {
    notify({
      type: 'negative',
      message: 'Please select start and end dates',
    })
    return
  }

  // Meal plans are optional - can generate empty shopping list
  if (!newShoppingList.value.meal_plan_ids) {
    newShoppingList.value.meal_plan_ids = []
  }

  generating.value = true

  // Add a timeout to prevent infinite loading
  const timeoutId = setTimeout(() => {
    if (generating.value) {
      console.error('ShoppingLists: Request timed out after 30 seconds')
      generating.value = false
      notify({
        type: 'negative',
        message: 'Request timed out. Please try again.',
      })
    }
  }, 30000) // 30 second timeout

  try {
    console.log('ShoppingLists: Calling store.generateShoppingList')
    const result = await mealPlanningStore.generateShoppingList(newShoppingList.value)
    console.log('ShoppingLists: Shopping list generated successfully:', result)

    clearTimeout(timeoutId)

    notify({
      type: 'positive',
      message: 'Shopping list generated successfully!',
    })

    // Success! Close dialog and refresh
    console.log(
      'ShoppingLists: About to close dialog - showGenerateDialog.value is:',
      showGenerateDialog.value,
    )
    showGenerateDialog.value = false
    console.log(
      'ShoppingLists: Set showGenerateDialog.value to false - now it is:',
      showGenerateDialog.value,
    )

    resetGenerateForm()
    console.log('ShoppingLists: Form reset completed')

    // Reload shopping lists to show the new one (force refresh)
    console.log('ShoppingLists: About to reload shopping lists')
    const currentLists = mealPlanningStore.shoppingLists[activeTab.value] || []
    console.log('ShoppingLists: Current shopping lists before refresh:', currentLists.map(sl => ({ id: sl.id, name: sl.name })))
    await mealPlanningStore.fetchShoppingLists(true, activeTab.value) // Force refresh with scope
    const refreshedLists = mealPlanningStore.shoppingLists[activeTab.value] || []
    console.log('ShoppingLists: Shopping lists after refresh:', refreshedLists.map(sl => ({ id: sl.id, name: sl.name })))
    console.log('ShoppingLists: Shopping lists reloaded - dialog should be closed now')
  } catch (err) {
    clearTimeout(timeoutId)
    console.error('ShoppingLists: Error generating shopping list:', err)
    console.error('ShoppingLists: Error details:', {
      message: err.message,
      response: err.response?.data,
      status: err.response?.status,
    })

    let errorMessage = 'Failed to generate shopping list'
    if (err.response?.data?.error) {
      errorMessage = err.response.data.error
    } else if (err.message) {
      errorMessage = err.message
    }

    notify({
      type: 'negative',
      message: errorMessage,
    })
  } finally {
    generating.value = false
    console.log('ShoppingLists: Generate shopping list completed')
  }
}

const viewShoppingList = (id) => {
  router.push({ name: 'shopping-list-detail', params: { id } })
}

const confirmDelete = (shoppingList) => {
  console.log('ShoppingLists: Delete button clicked for:', shoppingList)
  shoppingListToDelete.value = shoppingList
  showDeleteDialog.value = true
  console.log('ShoppingLists: Delete dialog should be open now')
}

const deleteShoppingList = async () => {
  if (!shoppingListToDelete.value) return

  deleting.value = true
  try {
    await mealPlanningStore.deleteShoppingList(shoppingListToDelete.value.id)

    notify({
      type: 'positive',
      message: 'Shopping list deleted successfully',
    })

    showDeleteDialog.value = false
    shoppingListToDelete.value = null
    await loadShoppingLists(true) // Force refresh after deletion
  } catch (err) {
    console.error('Error deleting shopping list:', err)
    notify({
      type: 'negative',
      message: 'Failed to delete shopping list',
    })
  } finally {
    deleting.value = false
  }
}

const cancelGenerate = () => {
  showGenerateDialog.value = false
  resetGenerateForm()
}

const resetGenerateForm = () => {
  newShoppingList.value = {
    name: '',
    start_date: '',
    end_date: '',
    meal_plan_ids: [],
    listType: activeTab.value, // Default to current tab
  }
}

const onValidationError = (error) => {
  console.log('ShoppingLists: Form validation error:', error)
  notify({
    type: 'negative',
    message: 'Please fill in all required fields',
  })
}


const isShoppingListOutdated = (shoppingList) => {
  // Simple check: if shopping list is older than 1 day and we're showing update notification
  if (!showUpdateNotification.value) return false

  const shoppingListDate = new Date(shoppingList.generated_at || shoppingList.created_at)
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

  return shoppingListDate < oneDayAgo
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
.shopping-list-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.shopping-list-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
