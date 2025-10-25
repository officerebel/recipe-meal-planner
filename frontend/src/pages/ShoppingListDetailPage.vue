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
        <q-btn flat label="Retry" @click="loadShoppingList" />
      </template>
    </q-banner>

    <!-- Shopping List Content -->
    <div v-else-if="shoppingList">
      <!-- Breadcrumb Navigation -->
      <q-breadcrumbs class="q-mb-md">
        <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
        <q-breadcrumbs-el label="Shopping Lists" icon="shopping_cart" :to="{ name: 'shopping-lists' }" />
        <q-breadcrumbs-el :label="shoppingList.name" />
      </q-breadcrumbs>

      <!-- Mobile-friendly Header -->
      <div class="q-mb-lg">
        <!-- Title Section -->
        <div class="row items-center q-mb-sm">
          <div class="col-grow">
            <div class="text-h4" v-if="!editingTitle">
              {{ shoppingList.name }}
              <q-btn flat round dense icon="edit" size="sm" @click="startEditTitle" class="q-ml-sm" />
            </div>
            <div v-else class="row items-center q-gutter-sm">
              <q-input
                v-model="editTitleValue"
                class="col-grow"
                style="font-size: 1.5rem; font-weight: 300;"
                dense
                autofocus
                @keyup.enter="saveTitle"
                @keyup.escape="cancelEditTitle"
              />
              <q-btn flat round dense icon="check" color="positive" @click="saveTitle" />
              <q-btn flat round dense icon="close" color="negative" @click="cancelEditTitle" />
            </div>
            <div class="text-subtitle1 text-grey-7">
              {{ formatDateRange(shoppingList.start_date, shoppingList.end_date) }}
            </div>
          </div>
        </div>

        <!-- Action Buttons - Mobile Responsive -->
        <div class="row q-gutter-sm justify-between">
          <q-btn
            flat
            icon="arrow_back"
            :label="$q.screen.xs ? '' : 'Back'"
            :to="{ name: 'shopping-lists' }"
            color="grey-7"
          >
            <q-tooltip v-if="$q.screen.xs">Back to Shopping Lists</q-tooltip>
          </q-btn>

          <div class="row q-gutter-xs">
            <q-btn
              color="secondary"
              icon="download"
              :label="$q.screen.xs ? '' : 'Export'"
              @click="exportAsTxt"
              :size="$q.screen.xs ? 'sm' : undefined"
            >
              <q-tooltip v-if="$q.screen.xs">Export as TXT</q-tooltip>
            </q-btn>
            <q-btn
              color="info"
              icon="print"
              :label="$q.screen.xs ? '' : 'Print'"
              @click="printShoppingList"
              :size="$q.screen.xs ? 'sm' : undefined"
            >
              <q-tooltip v-if="$q.screen.xs">Print Shopping List</q-tooltip>
            </q-btn>
            <q-btn
              color="positive"
              icon="check_all"
              :label="$q.screen.xs ? '' : 'Mark All'"
              @click="markAllPurchased"
              :size="$q.screen.xs ? 'sm' : undefined"
            >
              <q-tooltip v-if="$q.screen.xs">Mark All Purchased</q-tooltip>
            </q-btn>
          </div>
        </div>
      </div>

      <!-- Mobile-friendly Stats Cards -->
      <div class="row q-gutter-sm q-mb-lg">
        <div class="col-6 col-sm-3">
          <q-card>
            <q-card-section class="text-center q-pa-sm">
              <div class="text-h6 text-primary">{{ shoppingList.total_items || 0 }}</div>
              <div class="text-caption">Total</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-6 col-sm-3">
          <q-card>
            <q-card-section class="text-center q-pa-sm">
              <div class="text-h6 text-positive">{{ shoppingList.purchased_items || 0 }}</div>
              <div class="text-caption">Done</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-6 col-sm-3">
          <q-card>
            <q-card-section class="text-center q-pa-sm">
              <div class="text-h6 text-accent">{{ completionPercentage }}%</div>
              <div class="text-caption">Complete</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-6 col-sm-3">
          <q-card>
            <q-card-section class="text-center q-pa-sm">
              <div class="text-h6 text-info">{{ remainingItems }}</div>
              <div class="text-caption">Left</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Shopping List Items -->
      <q-card>
        <q-card-section>
          <div class="text-h6 q-mb-md">
            <q-icon name="shopping_cart" class="q-mr-sm" />
            Shopping Items
          </div>

          <!-- Filter Tabs -->
          <q-tabs v-model="activeTab" class="text-grey-7 q-mb-md">
            <q-tab name="all" label="All Items" />
            <q-tab name="remaining" label="Remaining" />
            <q-tab name="purchased" label="Purchased" />
          </q-tabs>

          <!-- Mobile-friendly Add Custom Item -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section class="q-py-sm">
              <div class="column q-gutter-sm">
                <!-- Item name - full width on mobile -->
                <q-input
                  v-model="newItemName"
                  label="Add custom item"
                  placeholder="e.g., Milk, Bread, Apples..."
                  outlined
                  dense
                  @keyup.enter="addCustomItem"
                >
                  <template v-slot:prepend>
                    <q-icon name="add_shopping_cart" />
                  </template>
                </q-input>

                <!-- Amount and Category row -->
                <div class="row q-gutter-sm">
                  <div class="col">
                    <q-input
                      v-model="newItemAmount"
                      label="Amount"
                      placeholder="2 lbs"
                      outlined
                      dense
                    />
                  </div>
                  <div class="col">
                    <q-select
                      v-model="newItemCategory"
                      :options="categoryOptions"
                      label="Category"
                      outlined
                      dense
                      emit-value
                      map-options
                    />
                  </div>
                  <div class="col-auto">
                    <q-btn
                      color="primary"
                      icon="add"
                      :label="$q.screen.xs ? '' : 'Add'"
                      @click="addCustomItem"
                      :disable="!newItemName.trim()"
                      :loading="addingItem"
                      :round="$q.screen.xs"
                    >
                      <q-tooltip v-if="$q.screen.xs">Add Item</q-tooltip>
                    </q-btn>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Data Quality Warning -->
          <q-banner v-if="hasLowQualityData" class="bg-warning text-dark q-mb-md">
            <template v-slot:avatar>
              <q-icon name="warning" />
            </template>
            <div>
              <strong>Data Quality Issue:</strong> This shopping list contains ingredients with poor names
              (likely from PDF parsing errors). You may want to manually edit or regenerate this list.
            </div>
            <template v-slot:action>
              <q-btn flat label="Hide Items with Poor Names" @click="toggleHidePoorQuality" />
            </template>
          </q-banner>

          <!-- Simple Shopping List Layout -->
          <div v-if="displayedItems.length > 0" class="shopping-list-items">
            <q-list separator>
              <q-item
                v-for="item in displayedItems"
                :key="item.id"
                class="shopping-item"
                :class="{ 'purchased': item.purchased }"
              >
                <q-item-section avatar>
                  <q-checkbox
                    :model-value="item.purchased"
                    @update:model-value="(val) => toggleItemPurchased(item, val)"
                    color="positive"
                    size="lg"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label
                    :class="{
                      'text-strike text-grey-6': item.purchased,
                      'text-orange-8': isLowQualityItem(item),
                      'text-h6': true
                    }"
                  >
                    {{ item.ingredient_name }}
                    <q-icon v-if="isLowQualityItem(item)" name="warning" size="xs" color="orange" class="q-ml-xs" />
                    <q-icon v-if="item.notes && item.notes.trim()" name="note" size="xs" color="blue-6" class="q-ml-xs">
                      <q-tooltip>This item has notes</q-tooltip>
                    </q-icon>
                  </q-item-label>
                  <q-item-label caption class="text-body2">
                    {{ item.total_amount }} {{ item.unit }}
                    <q-chip
                      v-if="item.category && item.category !== 'other'"
                      :label="getCategoryLabel(item.category)"
                      size="sm"
                      color="grey-3"
                      text-color="grey-8"
                      class="q-ml-sm"
                    />
                  </q-item-label>
                  <q-item-label caption v-if="item.notes && item.notes.trim()" class="text-grey-7 q-mt-xs">
                    <q-icon name="note" size="xs" class="q-mr-xs" color="blue-6" />
                    <span class="text-italic">{{ item.notes }}</span>
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <!-- Mobile: Vertical buttons -->
                  <div v-if="$q.screen.xs" class="column q-gutter-xs">
                    <q-btn
                      flat
                      dense
                      icon="edit"
                      size="sm"
                      color="primary"
                      @click="editItem(item)"
                    />
                    <q-btn
                      flat
                      dense
                      icon="delete"
                      size="sm"
                      color="negative"
                      @click="deleteItem(item)"
                    />
                  </div>

                  <!-- Desktop: Horizontal buttons -->
                  <div v-else class="row items-center q-gutter-xs">
                    <q-btn
                      flat
                      round
                      icon="edit"
                      size="sm"
                      color="grey-6"
                      @click="editItem(item)"
                    >
                      <q-tooltip>Edit item</q-tooltip>
                    </q-btn>
                    <q-btn
                      flat
                      round
                      icon="delete"
                      size="sm"
                      color="negative"
                      @click="deleteItem(item)"
                    >
                      <q-tooltip>Delete item</q-tooltip>
                    </q-btn>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center q-py-xl">
            <q-icon name="shopping_cart_checkout" size="64px" color="grey-5" />
            <div class="text-h6 q-mt-md text-grey-6">
              {{ getEmptyStateMessage() }}
            </div>
            <div v-if="hidePoorQuality && hasLowQualityData" class="text-body2 text-grey-6 q-mt-sm">
              Items with poor quality names are hidden.
              <q-btn flat dense color="primary" label="Show All Items" @click="hidePoorQuality = false" />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Source Meal Plans -->
      <q-card class="q-mt-lg" v-if="shoppingList.meal_plans && shoppingList.meal_plans.length > 0">
        <q-card-section>
          <div class="text-h6 q-mb-md">
            <q-icon name="calendar_today" class="q-mr-sm" />
            Source Meal Plans
          </div>
          <div class="row q-gutter-md">
            <div v-for="mealPlan in shoppingList.meal_plans" :key="mealPlan.id" class="col-12 col-md-6">
              <q-card flat bordered class="cursor-pointer" @click="viewMealPlan(mealPlan.id)">
                <q-card-section>
                  <div class="text-subtitle1">{{ mealPlan.name }}</div>
                  <div class="text-caption text-grey-6">
                    {{ formatDateRange(mealPlan.start_date, mealPlan.end_date) }}
                  </div>
                  <div class="text-caption">
                    {{ mealPlan.total_days }} days • {{ mealPlan.total_meals }} meals
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Edit Item Dialog - Mobile Optimized -->
    <q-dialog
      v-model="showEditDialog"
      persistent
      :maximized="$q.screen.xs"
      :full-width="$q.screen.xs"
    >
      <q-card :style="$q.screen.xs ? '' : 'min-width: 400px; max-width: 500px'">
        <q-card-section class="row items-center">
          <div class="text-h6">Edit Shopping List Item</div>
          <q-space />
          <q-btn
            v-if="$q.screen.xs"
            flat
            round
            dense
            icon="close"
            @click="cancelEdit"
          />
        </q-card-section>

        <q-card-section class="q-pt-none" :style="$q.screen.xs ? 'max-height: 70vh; overflow-y: auto' : ''">
          <q-form @submit="saveEditedItem" class="q-gutter-md">
            <q-input
              v-model="editForm.ingredient_name"
              label="Ingredient Name *"
              outlined
              :rules="[val => !!val || 'Ingredient name is required']"
            >
              <template v-slot:prepend>
                <q-icon name="restaurant" />
              </template>
            </q-input>

            <q-input
              v-model="editForm.total_amount"
              label="Amount"
              outlined
              hint="e.g., 2 cups, 500g, 1 tbsp"
            >
              <template v-slot:prepend>
                <q-icon name="straighten" />
              </template>
            </q-input>

            <q-input
              v-model="editForm.unit"
              label="Unit"
              outlined
              hint="e.g., cups, grams, pieces"
            >
              <template v-slot:prepend>
                <q-icon name="scale" />
              </template>
            </q-input>

            <q-select
              v-model="editForm.category"
              :options="categoryOptions"
              label="Category"
              outlined
              emit-value
              map-options
            >
              <template v-slot:prepend>
                <q-icon name="category" />
              </template>
            </q-select>

            <q-input
              v-model="editForm.notes"
              label="Notes"
              type="textarea"
              rows="2"
              outlined
              hint="Optional notes about this item"
            >
              <template v-slot:prepend>
                <q-icon name="note" />
              </template>
            </q-input>

            <q-toggle
              v-model="editForm.purchased"
              label="Mark as purchased"
              color="positive"
            />
          </q-form>
        </q-card-section>

        <q-card-actions
          :align="$q.screen.xs ? 'stretch' : 'right'"
          :class="$q.screen.xs ? 'q-pa-md' : ''"
        >
          <q-btn
            v-if="!$q.screen.xs"
            flat
            label="Cancel"
            color="grey"
            @click="cancelEdit"
          />
          <q-btn
            :label="$q.screen.xs ? 'Save Changes' : 'Save Changes'"
            color="primary"
            @click="saveEditedItem"
            :loading="savingEdit"
            :class="$q.screen.xs ? 'full-width' : ''"
            size="lg"
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
import { useRecipeStore } from 'src/stores/recipes'

const $q = useQuasar()
const router = useRouter()
const mealPlanningStore = useMealPlanningStore()
const recipeStore = useRecipeStore()

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

// State
const shoppingList = ref(null)
const loading = ref(false)
const error = ref(null)
const activeTab = ref('all')
const hidePoorQuality = ref(false)

// Drag and drop state (commented out - not used)
// const draggedItem = ref(null)
// const draggedIndex = ref(null)
// const dragOverIndex = ref(null)
// const dragOverDepartment = ref(null)

// Edit item state
const showEditDialog = ref(false)
const editingItem = ref(null)
const savingEdit = ref(false)
const editForm = ref({
  ingredient_name: '',
  total_amount: '',
  unit: '',
  category: 'other',
  notes: '',
  purchased: false
})

// Add custom item state
const newItemName = ref('')
const newItemAmount = ref('')
const newItemCategory = ref('other')
const addingItem = ref(false)

// Auto-predict category when ingredient name changes
watch(newItemName, (newName) => {
  if (newName && newName.trim().length > 2) {
    const predictedCategory = predictCategory(newName)
    newItemCategory.value = predictedCategory
  }
})

// Title editing state
const editingTitle = ref(false)
const editTitleValue = ref('')

// Category labels for display
const categoryLabels = {
  'produce': 'Groenten & Fruit',
  'bakery': 'Bakkerij',
  'meat': 'Vlees & Vis',
  'dairy': 'Zuivel & Eieren',
  'frozen': 'Diepvries',
  'pantry': 'Voorraadkast',
  'beverages': 'Dranken',
  'condiments': 'Kruiden & Sauzen',
  'other': 'Overig'
}

// Shopping departments for drag and drop (commented out - not used)
// const shoppingDepartments = [
//   { key: 'produce', name: 'Groenten & Fruit' },
//   { key: 'bakery', name: 'Bakkerij' },
//   { key: 'meat', name: 'Vlees & Vis' },
//   { key: 'dairy', name: 'Zuivel & Eieren' },
//   { key: 'frozen', name: 'Diepvries' },
//   { key: 'pantry', name: 'Voorraadkast' },
//   { key: 'beverages', name: 'Dranken' },
//   { key: 'condiments', name: 'Kruiden & Sauzen' },
//   { key: 'other', name: 'Overig' }
// ]

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

// Computed
const completionPercentage = computed(() => {
  if (!shoppingList.value || !shoppingList.value.total_items) return 0
  return Math.round((shoppingList.value.purchased_items / shoppingList.value.total_items) * 100)
})

const remainingItems = computed(() => {
  if (!shoppingList.value) return 0
  return (shoppingList.value.total_items || 0) - (shoppingList.value.purchased_items || 0)
})

const filteredItems = computed(() => {
  if (!shoppingList.value?.items) return []

  switch (activeTab.value) {
    case 'remaining':
      return shoppingList.value.items.filter(item => !item.purchased)
    case 'purchased':
      return shoppingList.value.items.filter(item => item.purchased)
    default:
      return shoppingList.value.items
  }
})

const hasLowQualityData = computed(() => {
  if (!shoppingList.value?.items) return false
  return shoppingList.value.items.some(item => isLowQualityItem(item))
})

const displayedItems = computed(() => {
  if (!hidePoorQuality.value) return filteredItems.value
  return filteredItems.value.filter(item => !isLowQualityItem(item))
})

// const itemsWithNotes = computed(() => {
//   if (!shoppingList.value?.items) return 0
//   return shoppingList.value.items.filter(item => item.notes && item.notes.trim()).length
// })

const categoryOptions = computed(() => recipeStore.ingredientCategories)

// Lifecycle
onMounted(() => {
  loadShoppingList()
  recipeStore.fetchIngredientCategories()
})

// Methods
const loadShoppingList = async () => {
  loading.value = true
  error.value = null

  try {
    // For now, we'll use the shopping lists from the store
    await mealPlanningStore.fetchShoppingLists(false, 'personal')
    await mealPlanningStore.fetchShoppingLists(false, 'family')

    // Search in both personal and family lists
    let foundList = mealPlanningStore.shoppingLists.personal.find(list => list.id === props.id)
    if (!foundList) {
      foundList = mealPlanningStore.shoppingLists.family.find(list => list.id === props.id)
    }

    if (foundList) {
      shoppingList.value = foundList

      // Ensure items have proper structure for checkbox functionality
      if (shoppingList.value.items) {
        shoppingList.value.items = shoppingList.value.items.map(item => ({
          ...item,
          purchased: item.purchased || false,
          purchased_at: item.purchased_at || null
        }))
      }
    } else {
      // Create mock data for testing if no shopping list found
      shoppingList.value = {
        id: props.id,
        name: 'Sample Shopping List',
        start_date: '2025-01-05',
        end_date: '2025-01-12',
        total_items: 2,
        purchased_items: 0,
        items: [
          {
            id: 'mock-1',
            ingredient_name: 'Milk',
            total_amount: '1 gallon',
            unit: 'gallon',
            category: 'dairy',
            notes: 'Custom item',
            purchased: false,
            purchased_at: null,
            is_custom: true
          },
          {
            id: 'mock-2',
            ingredient_name: 'Bread',
            total_amount: '1 loaf',
            unit: 'loaf',
            category: 'bakery',
            notes: '',
            purchased: false,
            purchased_at: null,
            is_custom: false
          }
        ],
        meal_plans: []
      }
    }
  } catch (err) {
    console.error('Error loading shopping list:', err)

    // Handle specific error types
    if (err.response?.status === 404) {
      error.value = 'Shopping list not found. It may have been deleted or you may not have access to it.'

      // Redirect to shopping lists page after a delay
      setTimeout(() => {
        router.push({ name: 'shopping-lists' })
      }, 3000)
    } else if (err.response?.status === 401) {
      error.value = 'Authentication required. Please log in or enable test mode.'
    } else {
      error.value = err.message || 'Failed to load shopping list'
    }
  } finally {
    loading.value = false
  }
}

const toggleItemPurchased = async (item, newValue = null) => {
  // Use provided value or toggle current state
  const targetValue = newValue !== null ? newValue : !item.purchased
  const wasAlreadyPurchased = item.purchased

  console.log(`Toggling item ${item.ingredient_name} from ${item.purchased} to ${targetValue}`)

  try {
    // Update local state immediately for responsive UI
    item.purchased = targetValue

    if (targetValue && !wasAlreadyPurchased) {
      // Item was just marked as purchased
      item.purchased_at = new Date().toISOString()
      shoppingList.value.purchased_items = (shoppingList.value.purchased_items || 0) + 1
    } else if (!targetValue && wasAlreadyPurchased) {
      // Item was just marked as not purchased
      item.purchased_at = null
      shoppingList.value.purchased_items = Math.max(0, (shoppingList.value.purchased_items || 0) - 1)
    }

    // Call the store method (which simulates API call)
    await mealPlanningStore.toggleItemPurchased(item.id, targetValue)

    notify({
      type: 'positive',
      message: item.purchased ? 'Item marked as purchased' : 'Item marked as not purchased',
      timeout: 1500
    })
  } catch (err) {
    console.error('Error toggling item:', err)

    // Revert the local state change on error
    item.purchased = wasAlreadyPurchased
    if (targetValue && !wasAlreadyPurchased) {
      // Revert purchased state
      item.purchased_at = null
      shoppingList.value.purchased_items = Math.max(0, (shoppingList.value.purchased_items || 0) - 1)
    } else if (!targetValue && wasAlreadyPurchased) {
      // Revert unpurchased state
      item.purchased_at = new Date().toISOString()
      shoppingList.value.purchased_items = (shoppingList.value.purchased_items || 0) + 1
    }

    notify({
      type: 'negative',
      message: 'Failed to update item status',
    })
  }
}

const markAllPurchased = async () => {
  if (!shoppingList.value?.items) return

  try {
    const unpurchasedItems = shoppingList.value.items.filter(item => !item.purchased)

    for (const item of unpurchasedItems) {
      await mealPlanningStore.toggleItemPurchased(item.id, true)
      item.purchased = true
      item.purchased_at = new Date().toISOString()
    }

    shoppingList.value.purchased_items = shoppingList.value.total_items

    notify({
      type: 'positive',
      message: `Marked ${unpurchasedItems.length} items as purchased`,
    })
  } catch (err) {
    console.error('Error marking all purchased:', err)
    notify({
      type: 'negative',
      message: 'Failed to mark all items as purchased',
    })
  }
}

const viewMealPlan = (mealPlanId) => {
  router.push({ name: 'meal-plan-detail', params: { id: mealPlanId } })
}

// Export shopping list as TXT file
const exportAsTxt = () => {
  if (!shoppingList.value?.items) return

  const listName = shoppingList.value.name || 'Shopping List'
  const dateRange = formatDateRange(shoppingList.value.start_date, shoppingList.value.end_date)

  let txtContent = `${listName}\n`
  txtContent += `${dateRange}\n`
  txtContent += `Generated: ${new Date().toLocaleDateString('nl-NL')}\n`
  txtContent += `\n${'='.repeat(50)}\n\n`

  // Group items by category
  const itemsByCategory = {}
  shoppingList.value.items.forEach(item => {
    const category = item.category || 'Overig'
    if (!itemsByCategory[category]) {
      itemsByCategory[category] = []
    }
    itemsByCategory[category].push(item)
  })

  // Generate content for each category
  Object.keys(itemsByCategory).sort().forEach(category => {
    txtContent += `${category.toUpperCase()}\n`
    txtContent += `${'-'.repeat(category.length)}\n`

    itemsByCategory[category].forEach(item => {
      const checkbox = item.purchased ? '☑' : '☐'
      const quantity = item.quantity ? `${item.quantity} ${item.unit || ''}`.trim() : ''
      const name = item.ingredient_name || item.name
      const notes = item.notes ? ` (${item.notes})` : ''

      txtContent += `${checkbox} ${quantity} ${name}${notes}\n`
    })
    txtContent += '\n'
  })

  // Add summary
  txtContent += `${'='.repeat(50)}\n`
  txtContent += `SAMENVATTING\n`
  txtContent += `Total items: ${shoppingList.value.total_items || 0}\n`
  txtContent += `Purchased: ${shoppingList.value.purchased_items || 0}\n`
  txtContent += `Remaining: ${remainingItems.value}\n`
  txtContent += `Complete: ${completionPercentage.value}%\n`

  // Create and download file
  const blob = new Blob([txtContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${listName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().split('T')[0]}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  notify({
    type: 'positive',
    message: 'Shopping list exported as TXT file!',
    timeout: 2000
  })
}

// Print shopping list
const printShoppingList = () => {
  if (!shoppingList.value?.items) return

  const printWindow = window.open('', '_blank')
  const listName = shoppingList.value.name || 'Shopping List'
  const dateRange = formatDateRange(shoppingList.value.start_date, shoppingList.value.end_date)

  let printContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${listName}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #1976d2; border-bottom: 2px solid #1976d2; }
        h2 { color: #424242; margin-top: 25px; }
        .item { margin: 5px 0; }
        .purchased { text-decoration: line-through; color: #888; }
        .summary { margin-top: 30px; padding: 15px; background: #f5f5f5; }
        @media print {
          body { margin: 0; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <h1>${listName}</h1>
      <p><strong>Period:</strong> ${dateRange}</p>
      <p><strong>Generated:</strong> ${new Date().toLocaleDateString('nl-NL')}</p>
  `

  // Group items by category
  const itemsByCategory = {}
  shoppingList.value.items.forEach(item => {
    const category = item.category || 'Overig'
    if (!itemsByCategory[category]) {
      itemsByCategory[category] = []
    }
    itemsByCategory[category].push(item)
  })

  // Generate content for each category
  Object.keys(itemsByCategory).sort().forEach(category => {
    printContent += `<h2>${category}</h2>`

    itemsByCategory[category].forEach(item => {
      const checkbox = item.purchased ? '☑' : '☐'
      const quantity = item.quantity ? `${item.quantity} ${item.unit || ''}`.trim() : ''
      const name = item.ingredient_name || item.name
      const notes = item.notes ? ` <em>(${item.notes})</em>` : ''
      const itemClass = item.purchased ? 'item purchased' : 'item'

      printContent += `<div class="${itemClass}">${checkbox} ${quantity} ${name}${notes}</div>`
    })
  })

  // Add summary
  printContent += `
    <div class="summary">
      <h3>Summary</h3>
      <p><strong>Total items:</strong> ${shoppingList.value.total_items || 0}</p>
      <p><strong>Purchased:</strong> ${shoppingList.value.purchased_items || 0}</p>
      <p><strong>Remaining:</strong> ${remainingItems.value}</p>
      <p><strong>Complete:</strong> ${completionPercentage.value}%</p>
    </div>
    </body>
    </html>
  `

  printWindow.document.write(printContent)
  printWindow.document.close()
  printWindow.focus()
  printWindow.print()
}



const isLowQualityItem = (item) => {
  const name = item.ingredient_name?.trim() || ''

  // Check for common PDF parsing errors
  return (
    name.length <= 3 ||                    // Very short names
    /^\d+$/.test(name) ||                  // Only numbers
    /^[0-9\s\-.]+$/.test(name) ||        // Only numbers, spaces, dashes, dots
    name.includes('�') ||                  // Unicode replacement characters
    /^[^a-zA-Z]*$/.test(name)             // No letters at all
  )
}

const toggleHidePoorQuality = () => {
  hidePoorQuality.value = !hidePoorQuality.value
}

const getEmptyStateMessage = () => {
  if (activeTab.value === 'remaining') return 'All items purchased!'
  if (activeTab.value === 'purchased') return 'No purchased items yet'
  if (hidePoorQuality.value && hasLowQualityData.value) return 'All items hidden due to poor quality'
  return 'No items in this shopping list'
}

// Drag and Drop Methods (commented out - not used in template)
// const onDragStart = (item, index, event) => {
//   draggedItem.value = item
//   draggedIndex.value = index
//   event.dataTransfer.effectAllowed = 'move'
//   event.dataTransfer.setData('text/plain', item.id)
//   event.target.style.opacity = '0.5'
//   notify({
//     type: 'info',
//     message: `Dragging "${item.ingredient_name}"`,
//     timeout: 1000
//   })
// }

// const onDragEnd = (event) => {
//   event.target.style.opacity = '1'
//   draggedItem.value = null
//   draggedIndex.value = null
//   dragOverIndex.value = null
// }

// const onDragOver = (index, event) => {
//   event.preventDefault()
//   event.dataTransfer.dropEffect = 'move'
//   if (draggedIndex.value !== index) {
//     dragOverIndex.value = index
//   }
// }

// const onDragLeave = () => {
//   dragOverIndex.value = null
// }

// const onDrop = async (dropIndex, event) => {
//   // Implementation commented out for build
// }

// const onDragOverDepartment = (departmentKey, event) => {
//   // Implementation commented out for build
// }

// const onDragLeaveDepartment = () => {
//   dragOverDepartment.value = null
// }

// const onDropToDepartment = async (departmentKey, event) => {
//   // Implementation commented out for build
// }

// const showItemMenu = () => {
//   // Menu is handled by q-menu component
// }

// Removed duplicate editItem function - using the complete version below

const cancelEdit = () => {
  showEditDialog.value = false
  editingItem.value = null
  editForm.value = {
    ingredient_name: '',
    total_amount: '',
    unit: '',
    category: 'other',
    notes: '',
    purchased: false
  }
}

// Intelligent category prediction
const predictCategory = (ingredientName) => {
  const name = ingredientName.toLowerCase().trim()

  // Dutch ingredient categorization
  const categoryMappings = {
    'produce': [
      // Fruits (Dutch)
      'appel', 'appels', 'peer', 'peren', 'banaan', 'bananen', 'sinaasappel', 'sinaasappels',
      'citroen', 'citroenen', 'limoen', 'limoenen', 'aardbei', 'aardbeien', 'framboos', 'frambozen',
      'blauwe bes', 'blauwe bessen', 'druif', 'druiven', 'ananas', 'mango', 'kiwi', 'meloen',
      'watermeloen', 'perzik', 'perziken', 'abrikoos', 'abrikozen', 'kers', 'kersen',

      // Vegetables (Dutch)
      'tomaat', 'tomaten', 'komkommer', 'komkommers', 'wortel', 'wortels', 'ui', 'uien',
      'knoflook', 'paprika', 'paprikas', 'courgette', 'courgettes', 'aubergine', 'aubergines',
      'broccoli', 'bloemkool', 'spinazie', 'sla', 'ijsbergsla', 'rucola', 'andijvie',
      'prei', 'selderij', 'radijs', 'radijsjes', 'biet', 'bieten', 'pompoen', 'zoete aardappel',
      'aardappel', 'aardappels', 'champignon', 'champignons', 'paddenstoel', 'paddestoelen'
    ],

    'meat': [
      'kip', 'kippenvlees', 'kipfilet', 'kippenborst', 'kippendij', 'kippenvleugel',
      'rund', 'rundvlees', 'biefstuk', 'gehakt', 'rundergehakt', 'varken', 'varkensvlees',
      'spek', 'bacon', 'ham', 'worst', 'worstjes', 'salami', 'chorizo',
      'zalm', 'tonijn', 'kabeljauw', 'zeebaars', 'garnaal', 'garnalen', 'mosselen',
      'vis', 'visfilet', 'haring', 'makreel', 'sardine', 'sardines'
    ],

    'dairy': [
      'melk', 'volle melk', 'halfvolle melk', 'magere melk', 'karnemelk', 'room', 'slagroom',
      'yoghurt', 'griekse yoghurt', 'kwark', 'kaas', 'goudse kaas', 'boerenkaas', 'mozzarella',
      'parmezaanse kaas', 'feta', 'camembert', 'brie', 'roomkaas', 'mascarpone',
      'ei', 'eieren', 'boter', 'margarine'
    ],

    'bakery': [
      'brood', 'wit brood', 'volkoren brood', 'roggebrood', 'stokbrood', 'bagel', 'croissant',
      'pistolet', 'bolletje', 'bolletjes', 'toast', 'crackers', 'beschuit', 'knäckebröd'
    ],

    'pantry': [
      'rijst', 'pasta', 'spaghetti', 'macaroni', 'penne', 'fusilli', 'couscous', 'quinoa',
      'bloem', 'zelfrijzend bakmeel', 'suiker', 'bruine suiker', 'honing', 'stroop',
      'olie', 'olijfolie', 'zonnebloemolie', 'azijn', 'balsamico', 'zout', 'peper',
      'bonen', 'kikkererwten', 'linzen', 'noten', 'amandelen', 'walnoten', 'pinda\'s'
    ],

    'frozen': [
      'diepvries', 'bevroren', 'ijs', 'ijsjes', 'sorbet', 'bevroren groenten',
      'bevroren fruit', 'pizza', 'diepvriespizza', 'fish sticks', 'vissticks'
    ],

    'beverages': [
      'water', 'spa', 'cola', 'fanta', 'sprite', 'sap', 'sinaasappelsap', 'appelsap',
      'koffie', 'thee', 'groene thee', 'bier', 'wijn', 'rode wijn', 'witte wijn'
    ],

    'condiments': [
      'ketchup', 'mayonaise', 'mosterd', 'saus', 'tomatensaus', 'pastasaus', 'pesto',
      'sojasaus', 'vissaus', 'worcestersaus', 'tabasco', 'sambal', 'harissa'
    ]
  }

  // Check each category for matches
  for (const [category, ingredients] of Object.entries(categoryMappings)) {
    for (const ingredient of ingredients) {
      if (name.includes(ingredient) || ingredient.includes(name)) {
        return category
      }
    }
  }

  // Default to 'other' if no match found
  return 'other'
}

const addCustomItem = async () => {
  if (!newItemName.value.trim()) {
    notify({
      type: 'negative',
      message: 'Please enter an item name'
    })
    return
  }

  addingItem.value = true

  try {
    // Create a new item object
    const newItem = {
      id: `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, // Generate unique ID
      ingredient_name: newItemName.value.trim(),
      total_amount: newItemAmount.value.trim() || '1',
      unit: '',
      category: newItemCategory.value,
      notes: 'Custom item',
      purchased: false,
      purchased_at: null,
      is_custom: true
    }

    // Add to the shopping list
    if (!shoppingList.value.items) {
      shoppingList.value.items = []
    }

    shoppingList.value.items.push(newItem)
    shoppingList.value.total_items = (shoppingList.value.total_items || 0) + 1

    // TODO: Make API call to save custom item to server
    // await mealPlanningStore.addCustomShoppingListItem(props.id, newItem)

    notify({
      type: 'positive',
      message: `Added "${newItem.ingredient_name}" to shopping list`
    })

    // Clear the form
    newItemName.value = ''
    newItemAmount.value = ''
    newItemCategory.value = 'other'

  } catch (error) {
    console.error('Error adding custom item:', error)
    notify({
      type: 'negative',
      message: 'Failed to add custom item'
    })
  } finally {
    addingItem.value = false
  }
}

// Title editing methods
const startEditTitle = () => {
  editTitleValue.value = shoppingList.value.name
  editingTitle.value = true
}

const cancelEditTitle = () => {
  editingTitle.value = false
  editTitleValue.value = ''
}

const saveTitle = async () => {
  if (!editTitleValue.value.trim()) {
    notify({
      type: 'negative',
      message: 'Title cannot be empty'
    })
    return
  }

  const newTitle = editTitleValue.value.trim()
  const originalTitle = shoppingList.value.name

  try {
    // Update local state immediately for better UX
    shoppingList.value.name = newTitle

    // Make API call to update title on server
    await mealPlanningStore.updateShoppingListTitle(props.id, newTitle)

    // Force refresh of shopping lists to ensure overview page updates
    await mealPlanningStore.fetchShoppingLists()

    editingTitle.value = false
    editTitleValue.value = ''

    notify({
      type: 'positive',
      message: 'Shopping list title updated'
    })
  } catch (error) {
    // Revert on error
    shoppingList.value.name = originalTitle
    console.error('Error updating title:', error)
    notify({
      type: 'negative',
      message: 'Failed to update title'
    })
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

const getCategoryLabel = (category) => {
  return categoryLabels[category] || category
}

const editItem = (item) => {
  editingItem.value = item
  editForm.value = {
    ingredient_name: item.ingredient_name,
    total_amount: item.total_amount,
    unit: item.unit,
    category: item.category || 'other',
    notes: item.notes || '',
    purchased: item.purchased
  }
  showEditDialog.value = true
}

const deleteItem = async (item) => {
  try {
    // Show confirmation dialog
    const confirmed = await new Promise((resolve) => {
      $q.dialog({
        title: 'Delete Item',
        message: `Are you sure you want to delete "${item.ingredient_name}"?`,
        cancel: true,
        persistent: true
      }).onOk(() => resolve(true))
        .onCancel(() => resolve(false))
    })

    if (!confirmed) return

    // Remove from local list immediately for responsive UI
    const itemIndex = shoppingList.value.items.findIndex(i => i.id === item.id)
    if (itemIndex > -1) {
      shoppingList.value.items.splice(itemIndex, 1)
      shoppingList.value.total_items = Math.max(0, (shoppingList.value.total_items || 0) - 1)

      if (item.purchased) {
        shoppingList.value.purchased_items = Math.max(0, (shoppingList.value.purchased_items || 0) - 1)
      }
    }

    // Call API to delete (simulated for now)
    await mealPlanningStore.deleteShoppingListItem(item.id)

    notify({
      type: 'positive',
      message: 'Item deleted successfully'
    })
  } catch (err) {
    console.error('Error deleting item:', err)
    notify({
      type: 'negative',
      message: 'Failed to delete item'
    })
    // Reload to restore state on error
    await loadShoppingList()
  }
}

const saveEditedItem = async () => {
  if (!editForm.value.ingredient_name.trim()) {
    notify({
      type: 'negative',
      message: 'Ingredient name is required'
    })
    return
  }

  savingEdit.value = true
  try {
    // Update local item immediately
    const item = editingItem.value
    Object.assign(item, editForm.value)

    // Call API to save changes (simulated for now)
    await mealPlanningStore.updateShoppingListItem(item.id, editForm.value)

    showEditDialog.value = false
    editingItem.value = null

    notify({
      type: 'positive',
      message: 'Item updated successfully'
    })
  } catch (err) {
    console.error('Error updating item:', err)
    notify({
      type: 'negative',
      message: 'Failed to update item'
    })
  } finally {
    savingEdit.value = false
  }
}
</script>

<style scoped>
/* Department-based shopping grid layout */
.department-based-shopping-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.department-section {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.department-section.drag-over-department {
  border: 2px solid #1976d2;
  background: #e3f2fd;
  transform: scale(1.02);
}

.department-header {
  text-align: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.department-items {
  min-height: 100px;
}

.empty-department-section {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.shopping-item {
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: grab;
  border: 2px solid transparent;
}

.shopping-item:hover {
  background-color: #f5f5f5;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.shopping-item.dragging {
  opacity: 0.5;
  transform: rotate(2deg);
  cursor: grabbing;
}

.shopping-item.drag-over {
  border-color: #1976d2;
  background-color: #e3f2fd;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.shopping-item.purchased {
  opacity: 0.7;
}

.drag-handle {
  cursor: grab;
  transition: color 0.2s;
}

.drag-handle:hover {
  color: #1976d2 !important;
}

.shopping-item:active .drag-handle {
  cursor: grabbing;
}

.shopping-list-container {
  position: relative;
}

.text-strike {
  text-decoration: line-through;
}

/* Add smooth animations for reordering */
.shopping-item {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Pulse animation for drag over */
.shopping-item.drag-over {
  animation: pulse 0.6s ease-in-out infinite alternate;
}

@keyframes pulse {
  from {
    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
  }
  to {
    box-shadow: 0 6px 16px rgba(25, 118, 210, 0.5);
  }
}
</style>

<style scoped>
.shopping-item {
  transition: background-color 0.2s;
}

.shopping-item.purchased {
  background-color: rgba(76, 175, 80, 0.1);
}

.shopping-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Mobile optimizations */
@media (max-width: 600px) {
  .q-page {
    padding: 8px !important;
  }

  .text-h4 {
    font-size: 1.5rem !important;
  }

  .q-card-section {
    padding: 12px !important;
  }
}

/* Touch-friendly checkboxes on mobile */
@media (max-width: 600px) {
  .q-checkbox {
    transform: scale(1.2);
  }
}
</style>
