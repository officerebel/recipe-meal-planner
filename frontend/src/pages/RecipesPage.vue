<template>
  <q-page class="q-pa-lg">
    <!-- Breadcrumb Navigation -->
    <q-breadcrumbs class="q-mb-md">
      <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
      <q-breadcrumbs-el label="Recipes" icon="restaurant_menu" />
    </q-breadcrumbs>

    <!-- Search Bar - Always Visible (Updated for mobile UX) -->
    <div class="sticky-search q-mb-md">
      <q-input
        v-model="searchQuery"
        placeholder="Search recipes..."
        outlined
        dense
        clearable
        class="search-input"
      >
        <template v-slot:prepend>
          <q-icon name="search" />
        </template>
      </q-input>
    </div>

    <div class="row justify-between items-center q-mb-lg">
      <div class="text-h4">Recipes</div>
      <div class="q-gutter-sm">
        <q-btn
          color="secondary"
          icon="upload_file"
          label="Import Recipe"
          :to="{ name: 'recipe-import' }"
          class="gt-xs"
        />
        <q-btn
          color="secondary"
          icon="upload_file"
          :to="{ name: 'recipe-import' }"
          class="lt-sm"
          round
        />
        <q-btn
          color="primary"
          icon="add"
          label="Create Recipe"
          :to="{ name: 'recipe-create' }"
          class="gt-xs"
        />
        <q-btn
          color="primary"
          icon="add"
          :to="{ name: 'recipe-create' }"
          class="lt-sm"
          round
        />
      </div>
    </div>

    <!-- Personal vs Family Tabs -->
    <q-tabs v-model="activeTab" class="text-grey-7 q-mb-md">
      <q-tab name="personal" label="My Recipes" icon="person" />
      <q-tab name="family" label="Family Recipes" icon="family_restroom" />
    </q-tabs>

    <!-- Additional Filters - Collapsible on Mobile -->
    <q-expansion-item
      icon="tune"
      label="Filters & Sort"
      class="q-mb-lg"
      header-class="text-primary"
    >
      <q-card>
        <q-card-section>
          <div class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-select
                v-model="selectedCategory"
                :options="categoryOptions"
                label="Category"
                outlined
                dense
                clearable
                emit-value
                map-options
              />
            </div>
            <div class="col-12 col-md-6">
              <q-select
                v-model="sortBy"
                :options="sortOptions"
                label="Sort by"
                outlined
                dense
                emit-value
                map-options
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-expansion-item>

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
        <q-btn flat label="Retry" @click="loadRecipes" />
      </template>
    </q-banner>

    <!-- Empty State -->
    <q-card v-else-if="filteredRecipes.length === 0" class="text-center q-py-xl">
      <q-card-section>
        <q-icon name="restaurant_menu" size="64px" color="grey-5" />
        <div class="text-h6 q-mt-md">
          {{ searchQuery || selectedCategory ? 'No recipes found' : 'No recipes yet' }}
        </div>
        <div class="text-body2 text-grey-7 q-mb-md">
          {{ searchQuery || selectedCategory
            ? 'Try adjusting your search or filters'
            : 'Start by importing or creating your first recipe' }}
        </div>
        <div class="q-gutter-sm" v-if="!searchQuery && !selectedCategory">
          <q-btn
            color="secondary"
            icon="upload_file"
            label="Import Recipe"
            :to="{ name: 'recipe-import' }"
          />
          <q-btn
            color="primary"
            icon="add"
            label="Create Recipe"
            :to="{ name: 'recipe-create' }"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Recipes Grid -->
    <div v-else class="row q-gutter-md">
      <div v-for="recipe in filteredRecipes" :key="recipe.id" class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card class="recipe-card cursor-pointer" @click="viewRecipe(recipe.id)">
          <!-- Recipe Image -->
          <q-img
            v-if="recipe.image"
            :src="getRecipeImageUrl(recipe.image)"
            height="200px"
            class="recipe-image"
          >
            <div class="absolute-bottom-right q-pa-sm">
              <q-chip color="white" text-color="dark" size="sm">
                <q-icon name="image" size="xs" />
              </q-chip>
            </div>
          </q-img>
          <div v-else class="recipe-image-placeholder">
            <q-icon name="restaurant_menu" size="64px" color="grey-4" />
          </div>

          <q-card-section>
            <div class="text-h6 q-mb-sm">{{ recipe.title }}</div>
            <div class="text-body2 text-grey-7 q-mb-md" v-if="recipe.description">
              {{ truncateText(recipe.description, 100) }}
            </div>

            <!-- Categories -->
            <div class="q-mb-sm" v-if="recipe.categories && recipe.categories.length > 0">
              <q-chip
                v-for="category in recipe.categories.slice(0, 2)"
                :key="category"
                size="sm"
                color="primary"
                text-color="white"
                class="q-mr-xs"
              >
                {{ formatCategoryName(category) }}
              </q-chip>
              <q-chip
                v-if="recipe.categories.length > 2"
                size="sm"
                color="grey"
                text-color="white"
              >
                +{{ recipe.categories.length - 2 }}
              </q-chip>
            </div>

            <!-- Recipe Info -->
            <div class="row q-gutter-sm text-caption text-grey-6">
              <div v-if="recipe.prep_time">
                <q-icon name="schedule" size="xs" />
                {{ recipe.prep_time }}min prep
              </div>
              <div v-if="recipe.cook_time">
                <q-icon name="whatshot" size="xs" />
                {{ recipe.cook_time }}min cook
              </div>
              <div v-if="recipe.servings">
                <q-icon name="people" size="xs" />
                {{ recipe.servings }} servings
              </div>
            </div>

            <!-- Source -->
            <div class="text-caption text-grey-5 q-mt-sm" v-if="recipe.source">
              <q-icon name="source" size="xs" />
              {{ recipe.source }}
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn
              flat
              icon="visibility"
              label="View"
              color="primary"
              @click.stop="viewRecipe(recipe.id)"
            />
            <q-btn
              flat
              icon="edit"
              label="Edit"
              color="secondary"
              @click.stop="editRecipe(recipe.id)"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Pagination -->
    <div class="row justify-center q-mt-lg" v-if="totalPages > 1">
      <q-pagination
        v-model="currentPage"
        :max="totalPages"
        :max-pages="6"
        boundary-numbers
        @update:model-value="loadRecipes"
      />
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getRecipeImageUrl } from 'src/utils/imageUtils'
import { useRecipeStore } from 'src/stores/recipes'

const router = useRouter()
const recipeStore = useRecipeStore()



// State
const loading = ref(false)
const error = ref(null)
const activeTab = ref('personal')
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('created_at')
const currentPage = ref(1)

// Options
const categoryOptions = computed(() => {
  const categories = recipeStore.categories || []
  return categories.map(cat => ({
    label: cat,
    value: cat.toLowerCase()
  }))
})

const sortOptions = [
  { label: 'Newest First', value: 'created_at' },
  { label: 'Oldest First', value: '-created_at' },
  { label: 'Name A-Z', value: 'title' },
  { label: 'Name Z-A', value: '-title' },
  { label: 'Prep Time', value: 'prep_time' },
  { label: 'Cook Time', value: 'cook_time' },
]

// Computed
const recipes = computed(() => recipeStore.recipes || [])
const totalPages = computed(() => Math.ceil((recipeStore.totalCount || 0) / 20))

const filteredRecipes = computed(() => recipes.value)

// Watchers
watch([searchQuery, selectedCategory], () => {
  currentPage.value = 1
  loadRecipes()
}, { debounce: 300 })

watch(sortBy, () => {
  loadRecipes()
})

watch(activeTab, () => {
  currentPage.value = 1
  loadRecipes()
})

// Lifecycle
onMounted(async () => {
  // Load categories first
  await recipeStore.fetchCategories()
  // Then load recipes
  loadRecipes()
})

// Methods
const loadRecipes = async () => {
  loading.value = true
  error.value = null

  try {
    // Update store filters with personal/family scope
    recipeStore.updateFilters({
      search: searchQuery.value,
      category: selectedCategory.value,
      page: currentPage.value,
      scope: activeTab.value // 'personal' or 'family'
    })

    await recipeStore.fetchRecipes(true)
  } catch (err) {
    console.error('Error loading recipes:', err)
    error.value = 'Failed to load recipes'
  } finally {
    loading.value = false
  }
}

const viewRecipe = (id) => {
  router.push({ name: 'recipe-detail', params: { id } })
}

const editRecipe = (id) => {
  router.push({ name: 'recipe-edit', params: { id } })
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatCategoryName = (category) => {
  if (!category) return ''

  // Handle multi-word categories
  const categoryMap = {
    'main course': 'Main Course',
    'appetizer': 'Appetizer',
    'dessert': 'Dessert',
    'salad': 'Salad',
    'soup': 'Soup',
    'beverage': 'Beverage',
    'snack': 'Snack',
    'side dish': 'Side Dish',
    'breakfast': 'Breakfast',
    'lunch': 'Lunch',
    'dinner': 'Dinner'
  }

  const lowerCategory = category.toLowerCase()
  return categoryMap[lowerCategory] || category.charAt(0).toUpperCase() + category.slice(1).toLowerCase()
}
</script>

<style scoped>
.sticky-search {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  padding: 8px 0;
  margin: -16px -16px 16px -16px;
  padding-left: 16px;
  padding-right: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-input {
  max-width: 100%;
}

.recipe-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  height: 100%;
}

.recipe-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.recipe-image {
  border-radius: 8px 8px 0 0;
}

.recipe-image-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  border-radius: 8px 8px 0 0;
}

/* Mobile optimizations */
@media (max-width: 600px) {
  .sticky-search {
    margin: -24px -24px 16px -24px;
    padding-left: 24px;
    padding-right: 24px;
  }

  .recipe-card {
    margin-bottom: 16px;
  }
}
</style>
