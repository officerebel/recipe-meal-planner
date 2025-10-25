<template>
  <q-page class="q-pa-md q-pa-lg-lg">
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-center q-pa-xl">
      <q-spinner-dots size="50px" color="primary" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center q-pa-xl">
      <q-icon name="error" size="64px" color="negative" class="q-mb-md" />
      <div class="text-h6 text-negative q-mb-md">Error Loading Recipe</div>
      <div class="text-body1 q-mb-lg">{{ error }}</div>
      <q-btn color="primary" label="Go Back" @click="$router.go(-1)" />
    </div>

    <!-- Recipe Content -->
    <div v-else-if="recipe" class="q-gutter-lg">
      <!-- Header -->
      <div class="row items-start justify-between q-col-gutter-md">
        <div>
          <div class="text-h4 q-mb-sm">{{ recipe.title }}</div>

          <!-- Categories -->
          <div
            class="text-subtitle1 text-grey-6 q-mb-sm"
            v-if="recipe.categories && recipe.categories.length > 0"
          >
            <div class="text-caption text-grey-6 q-mb-xs">Categories:</div>
            <q-chip
              v-for="category in recipe.categories"
              :key="category"
              color="primary"
              text-color="white"
              :label="formatCategoryName(category)"
              class="q-mr-sm"
            />
          </div>

          <!-- Tags -->
          <div class="text-subtitle1 text-grey-6" v-if="recipe.tags && recipe.tags.length > 0">
            <div class="text-caption text-grey-6 q-mb-xs">Tags:</div>
            <q-chip
              v-for="tag in recipe.tags"
              :key="tag"
              color="secondary"
              text-color="white"
              :label="formatTagName(tag)"
              class="q-mr-sm"
              size="sm"
            />
          </div>

          <!-- Sharing Status -->
          <div class="text-subtitle1 text-grey-6 q-mt-sm">
            <q-chip
              v-if="recipe.is_shared_with_family"
              icon="family_restroom"
              color="positive"
              text-color="white"
              label="Gedeeld met familie"
              size="sm"
            />
            <q-chip
              v-else
              icon="person"
              color="grey-5"
              text-color="white"
              label="Persoonlijk recept"
              size="sm"
            />
          </div>
        </div>
        <div class="q-gutter-sm column-xs row-sm">
          <!-- Family Sharing Component -->
          <RecipeSharing
            :recipe="recipe"
            @sharing-changed="onSharingChanged"
            @error="onSharingError"
            :compact="$q.screen.xs"
          />

          <q-btn
            color="primary"
            icon="edit"
            :label="$q.screen.xs ? '' : 'Edit'"
            :to="{ name: 'recipe-edit', params: { id: recipe.id } }"
            :size="$q.screen.xs ? 'sm' : 'md'"
          />
          <q-btn
            color="negative"
            icon="delete"
            :label="$q.screen.xs ? '' : 'Delete'"
            @click="confirmDelete"
            :size="$q.screen.xs ? 'sm' : 'md'"
          />
        </div>
      </div>

      <!-- Recipe Image -->
      <q-card class="q-mb-lg">
        <RecipeImage
          :src="recipe.image"
          :alt="recipe.title"
          style="max-height: 400px"
          class="rounded-borders"
        >
          <div
            v-if="recipe.image"
            class="absolute-bottom text-subtitle2 text-center q-pa-md bg-gradient"
          >
            {{ recipe.title }}
          </div>
        </RecipeImage>
      </q-card>

      <!-- Recipe Info Cards -->
      <div class="row q-gutter-md">
        <!-- Timing Info -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="schedule" class="q-mr-sm" />
                Timing
              </div>
              <div class="q-gutter-sm">
                <div v-if="recipe.prep_time" class="row items-center">
                  <q-icon name="restaurant" size="sm" class="q-mr-sm" />
                  <span>Prep: {{ recipe.prep_time }} minutes</span>
                </div>
                <div v-if="recipe.cook_time" class="row items-center">
                  <q-icon name="local_fire_department" size="sm" class="q-mr-sm" />
                  <span>Cook: {{ recipe.cook_time }} minutes</span>
                </div>
                <div v-if="recipe.total_time" class="row items-center">
                  <q-icon name="timer" size="sm" class="q-mr-sm" />
                  <span>Total: {{ recipe.total_time }} minutes</span>
                </div>
                <div v-if="recipe.servings" class="row items-center">
                  <q-icon name="people" size="sm" class="q-mr-sm" />
                  <span>Serves: {{ recipe.servings }}</span>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Nutritional Info -->
        <div class="col-12 col-md-4" v-if="hasNutritionalInfo">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="local_dining" class="q-mr-sm" />
                Voedingswaarden
                <span v-if="recipe.servings" class="text-caption text-grey-6"> (per portie) </span>
              </div>
              <div class="q-gutter-sm">
                <div v-if="recipe.calories" class="row items-center justify-between">
                  <span class="row items-center">
                    <q-icon name="local_fire_department" size="sm" class="q-mr-sm" />
                    Calorieën
                  </span>
                  <span class="text-weight-medium">{{ recipe.calories }} kcal</span>
                </div>
                <div v-if="recipe.protein" class="row items-center justify-between">
                  <span class="row items-center">
                    <q-icon name="fitness_center" size="sm" class="q-mr-sm" />
                    Eiwit
                  </span>
                  <span class="text-weight-medium">{{ recipe.protein }}g</span>
                </div>
                <div v-if="recipe.carbohydrates" class="row items-center justify-between">
                  <span class="row items-center">
                    <q-icon name="grain" size="sm" class="q-mr-sm" />
                    Koolhydraten
                  </span>
                  <span class="text-weight-medium">{{ recipe.carbohydrates }}g</span>
                </div>
                <div v-if="recipe.fat" class="row items-center justify-between">
                  <span class="row items-center">
                    <q-icon name="opacity" size="sm" class="q-mr-sm" />
                    Vet
                  </span>
                  <span class="text-weight-medium">{{ recipe.fat }}g</span>
                </div>
                <div v-if="recipe.fiber" class="row items-center justify-between">
                  <span class="row items-center">
                    <q-icon name="eco" size="sm" class="q-mr-sm" />
                    Vezels
                  </span>
                  <span class="text-weight-medium">{{ recipe.fiber }}g</span>
                </div>
                <div v-if="recipe.sodium" class="row items-center justify-between">
                  <span class="row items-center">
                    <q-icon name="water_drop" size="sm" class="q-mr-sm" />
                    Natrium
                  </span>
                  <span class="text-weight-medium">{{ recipe.sodium }}mg</span>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Source Info -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="source" class="q-mr-sm" />
                Source
              </div>
              <div class="q-gutter-sm">
                <div class="row items-center">
                  <q-icon :name="getSourceIcon(recipe.source)" size="sm" class="q-mr-sm" />
                  <span>{{ getSourceLabel(recipe.source) }}</span>
                </div>
                <div class="text-caption text-grey-6">
                  Created: {{ formatDate(recipe.created_at) }}
                </div>
                <div
                  v-if="recipe.updated_at !== recipe.created_at"
                  class="text-caption text-grey-6"
                >
                  Updated: {{ formatDate(recipe.updated_at) }}
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Tags -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="local_offer" class="q-mr-sm" />
                Tags
              </div>
              <div v-if="recipe.tags && recipe.tags.length > 0" class="q-gutter-xs">
                <q-chip
                  v-for="tag in recipe.tags"
                  :key="tag"
                  color="secondary"
                  text-color="white"
                  :label="tag"
                  size="sm"
                />
              </div>
              <div v-else class="text-grey-6">No tags</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Main Content -->
      <div class="row q-gutter-lg">
        <!-- Ingredients -->
        <div class="col-12 col-md-5">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="list" class="q-mr-sm" />
                Ingredients ({{ recipe.ingredients?.length || 0 }})
              </div>
              <q-list v-if="recipe.ingredients && recipe.ingredients.length > 0" separator>
                <q-item
                  v-for="(ingredient, index) in recipe.ingredients"
                  :key="index"
                  class="q-px-none"
                >
                  <q-item-section>
                    <div class="row items-center">
                      <div class="col-auto q-mr-md">
                        <q-checkbox v-model="checkedIngredients[index]" />
                      </div>
                      <div class="col">
                        <div :class="{ 'text-strike': checkedIngredients[index] }">
                          <strong v-if="ingredient.amount">{{ ingredient.amount }}</strong>
                          {{ ingredient.name }}
                          <span v-if="ingredient.notes" class="text-grey-6">
                            ({{ ingredient.notes }})
                          </span>
                        </div>
                      </div>
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-grey-6">No ingredients listed</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Instructions -->
        <div class="col-12 col-md-7">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="format_list_numbered" class="q-mr-sm" />
                Instructions
              </div>
              <q-list v-if="recipe.instructions && recipe.instructions.length > 0" separator>
                <q-item
                  v-for="(instruction, index) in recipe.instructions"
                  :key="index"
                  class="q-px-none q-py-md"
                >
                  <q-item-section avatar>
                    <q-avatar color="primary" text-color="white" size="md">
                      {{ index + 1 }}
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <div :class="{ 'text-strike': checkedInstructions[index] }">
                      {{ instruction }}
                    </div>
                  </q-item-section>
                  <q-item-section side>
                    <q-checkbox v-model="checkedInstructions[index]" />
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-grey-6">No instructions provided</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Description -->
      <q-card v-if="recipe.description">
        <q-card-section>
          <div class="text-h6 q-mb-md">
            <q-icon name="description" class="q-mr-sm" />
            Description
          </div>
          <div class="text-body1">{{ recipe.description }}</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="delete" color="negative" text-color="white" />
          <span class="q-ml-sm">Are you sure you want to delete this recipe?</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Delete" color="negative" @click="deleteRecipe" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useRecipeStore } from 'src/stores/recipes'
import RecipeSharing from 'src/components/RecipeSharing.vue'
import RecipeImage from 'src/components/RecipeImage.vue'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const $q = useQuasar()
const router = useRouter()
const recipeStore = useRecipeStore()

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

const recipe = ref(null)
const loading = ref(true)
const error = ref(null)

// Computed properties
const hasNutritionalInfo = computed(() => {
  if (!recipe.value) return false
  return !!(
    recipe.value.calories ||
    recipe.value.protein ||
    recipe.value.carbohydrates ||
    recipe.value.fat ||
    recipe.value.fiber ||
    recipe.value.sodium
  )
})

const showDeleteDialog = ref(false)

// Checkboxes for ingredients and instructions
const checkedIngredients = reactive({})
const checkedInstructions = reactive({})

onMounted(async () => {
  try {
    await fetchRecipe()
  } catch (err) {
    console.error('Error loading recipe:', err)

    // Handle specific error types
    if (err.response?.status === 404) {
      error.value = 'Recipe not found. It may have been deleted or you may not have access to it.'

      // Redirect to recipes page after a delay
      setTimeout(() => {
        router.push({ name: 'recipes' })
      }, 3000)
    } else if (err.response?.status === 401) {
      error.value = 'Authentication required. Please log in or enable test mode.'
    } else {
      error.value = err.message || 'Failed to load recipe'
    }
  } finally {
    loading.value = false
  }
})

const fetchRecipe = async () => {
  recipe.value = await recipeStore.fetchRecipe(props.id)
}

const onSharingChanged = (event) => {
  console.log('Recipe sharing changed:', event)

  // Update the recipe data with the new sharing status
  if (recipe.value && event.recipeId === recipe.value.id) {
    recipe.value.is_shared_with_family = event.isShared
  }
}

const onSharingError = (event) => {
  console.error('Recipe sharing error:', event)
  // Error handling is already done by the component
  // We could perform additional error handling here if needed
}

const getSourceIcon = (source) => {
  switch (source) {
    case 'pdf':
      return 'picture_as_pdf'
    case 'manual':
      return 'edit'
    case 'database':
      return 'storage'
    default:
      return 'source'
  }
}

const getSourceLabel = (source) => {
  switch (source) {
    case 'pdf':
      return 'PDF Import'
    case 'manual':
      return 'Manual Entry'
    case 'database':
      return 'Database Import'
    default:
      return source
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const confirmDelete = () => {
  showDeleteDialog.value = true
}

const deleteRecipe = async () => {
  try {
    await recipeStore.deleteRecipe(props.id)
    showDeleteDialog.value = false

    notify({
      type: 'positive',
      message: 'Recipe deleted successfully',
    })

    router.push({ name: 'recipes' })
  } catch (err) {
    notify({
      type: 'negative',
      message: err.message || 'Failed to delete recipe',
    })
  }
}

const formatCategoryName = (category) => {
  if (!category) return ''

  // Handle multi-word categories
  const categoryMap = {
    'main course': 'Main Course',
    appetizer: 'Appetizer',
    dessert: 'Dessert',
    salad: 'Salad',
    soup: 'Soup',
    beverage: 'Beverage',
    snack: 'Snack',
    'side dish': 'Side Dish',
    breakfast: 'Breakfast',
    lunch: 'Lunch',
    dinner: 'Dinner',
  }

  const lowerCategory = category.toLowerCase()
  return (
    categoryMap[lowerCategory] || category.charAt(0).toUpperCase() + category.slice(1).toLowerCase()
  )
}

const formatTagName = (tag) => {
  if (!tag) return ''

  // Handle common tag formatting
  const tagMap = {
    quick: 'Quick',
    easy: 'Easy',
    healthy: 'Healthy',
    vegetarian: 'Vegetarian',
    vegan: 'Vegan',
    'gluten-free': 'Gluten-Free',
    'dairy-free': 'Dairy-Free',
    'low-carb': 'Low-Carb',
    'high-protein': 'High-Protein',
    spicy: 'Spicy',
    sweet: 'Sweet',
    savory: 'Savory',
  }

  const lowerTag = tag.toLowerCase()
  return tagMap[lowerTag] || tag.charAt(0).toUpperCase() + tag.slice(1).toLowerCase()
}
</script>

<style scoped>
.text-strike {
  text-decoration: line-through;
  opacity: 0.6;
}

.bg-gradient {
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.3) 50%,
    rgba(0, 0, 0, 0) 100%
  );
}
</style>
