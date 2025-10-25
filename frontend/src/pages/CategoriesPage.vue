<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-lg">
      <div class="text-h4">Categorieën Beheer</div>
      <q-btn
        color="primary"
        icon="add"
        label="Nieuwe Categorie"
        @click="showCreateDialog = true"
      />
    </div>

    <!-- Categories Grid -->
    <div class="row q-gutter-md">
      <div class="col-12 col-md-6 col-lg-4">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="category" class="q-mr-sm" />
              Ingrediënt Categorieën
            </div>

            <!-- Loading State -->
            <div v-if="loading.ingredients" class="text-center q-py-md">
              <q-spinner-dots size="24px" color="primary" />
            </div>

            <!-- Categories List -->
            <q-list v-else separator>
              <q-item
                v-for="category in ingredientCategories"
                :key="category.value"
                class="category-item"
              >
                <q-item-section avatar>
                  <q-icon :name="category.icon" :color="category.color" />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ category.label }}</q-item-label>
                  <q-item-label caption>
                    {{ category.count }} ingrediënten
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn
                      flat
                      dense
                      round
                      icon="edit"
                      size="sm"
                      @click="editCategory(category, 'ingredient')"
                      :disable="category.isDefault"
                    />
                    <q-btn
                      flat
                      dense
                      round
                      icon="delete"
                      size="sm"
                      color="negative"
                      @click="deleteCategory(category, 'ingredient')"
                      :disable="category.isDefault || category.count > 0"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>

            <q-btn
              flat
              color="primary"
              icon="add"
              label="Ingrediënt Categorie Toevoegen"
              class="full-width q-mt-md"
              @click="openCreateDialog('ingredient')"
            />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="restaurant_menu" class="q-mr-sm" />
              Recept Categorieën
            </div>

            <!-- Loading State -->
            <div v-if="loading.recipes" class="text-center q-py-md">
              <q-spinner-dots size="24px" color="primary" />
            </div>

            <!-- Categories List -->
            <q-list v-else separator>
              <q-item
                v-for="category in recipeCategories"
                :key="category.value"
                class="category-item"
              >
                <q-item-section avatar>
                  <q-icon :name="category.icon" :color="category.color" />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ category.label }}</q-item-label>
                  <q-item-label caption>
                    {{ category.count }} recepten
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn
                      flat
                      dense
                      round
                      icon="edit"
                      size="sm"
                      @click="editCategory(category, 'recipe')"
                    />
                    <q-btn
                      flat
                      dense
                      round
                      icon="delete"
                      size="sm"
                      color="negative"
                      @click="deleteCategory(category, 'recipe')"
                      :disable="category.count > 0"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>

            <q-btn
              flat
              color="primary"
              icon="add"
              label="Recept Categorie Toevoegen"
              class="full-width q-mt-md"
              @click="openCreateDialog('recipe')"
            />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-6 col-lg-4">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="local_offer" class="q-mr-sm" />
              Tags Beheer
            </div>

            <!-- Loading State -->
            <div v-if="loading.tags" class="text-center q-py-md">
              <q-spinner-dots size="24px" color="primary" />
            </div>

            <!-- Tags List -->
            <q-list v-else separator>
              <q-item
                v-for="tag in recipeTags"
                :key="tag.value"
                class="category-item"
              >
                <q-item-section avatar>
                  <q-chip
                    :color="tag.color"
                    text-color="white"
                    size="sm"
                    :label="tag.label.charAt(0).toUpperCase()"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ tag.label }}</q-item-label>
                  <q-item-label caption>
                    {{ tag.count }} recepten
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn
                      flat
                      dense
                      round
                      icon="edit"
                      size="sm"
                      @click="editCategory(tag, 'tag')"
                    />
                    <q-btn
                      flat
                      dense
                      round
                      icon="delete"
                      size="sm"
                      color="negative"
                      @click="deleteCategory(tag, 'tag')"
                      :disable="tag.count > 0"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>

            <q-btn
              flat
              color="primary"
              icon="add"
              label="Tag Toevoegen"
              class="full-width q-mt-md"
              @click="openCreateDialog('tag')"
            />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <q-dialog v-model="showCreateDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">
            {{ editingCategory ? 'Categorie Bewerken' : 'Nieuwe Categorie' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveCategory" class="q-gutter-md">
            <q-input
              v-model="categoryForm.label"
              label="Naam *"
              outlined
              :rules="[val => !!val || 'Naam is verplicht']"
            />

            <q-input
              v-model="categoryForm.value"
              label="Waarde (automatisch gegenereerd)"
              outlined
              readonly
              hint="Wordt automatisch gegenereerd op basis van de naam"
            />

            <q-select
              v-model="categoryForm.icon"
              :options="iconOptions"
              label="Icoon"
              outlined
              emit-value
              map-options
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section avatar>
                    <q-icon :name="scope.opt.value" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ scope.opt.label }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

            <q-select
              v-model="categoryForm.color"
              :options="colorOptions"
              label="Kleur"
              outlined
              emit-value
              map-options
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section avatar>
                    <div
                      class="color-preview"
                      :style="{ backgroundColor: scope.opt.hex }"
                    ></div>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ scope.opt.label }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Annuleren" @click="cancelEdit" />
          <q-btn
            color="primary"
            label="Opslaan"
            @click="saveCategory"
            :loading="saving"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="delete" color="negative" text-color="white" />
          <span class="q-ml-sm">
            Weet je zeker dat je de categorie "{{ categoryToDelete?.label }}" wilt verwijderen?
          </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Annuleren" @click="showDeleteDialog = false" />
          <q-btn
            color="negative"
            label="Verwijderen"
            @click="confirmDelete"
            :loading="deleting"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRecipeStore } from 'src/stores/recipes'

const $q = useQuasar()
const recipeStore = useRecipeStore()

// State
const loading = ref({
  ingredients: false,
  recipes: false,
  tags: false
})

const saving = ref(false)
const deleting = ref(false)
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingCategory = ref(null)
const categoryToDelete = ref(null)
const currentType = ref('ingredient')

// Form
const categoryForm = ref({
  label: '',
  value: '',
  icon: 'category',
  color: 'primary'
})

// Note: Default ingredient categories are now loaded from the API via recipeStore.ingredientCategories

// Custom categories (stored in localStorage for demo)
const customCategories = ref({
  ingredient: [],
  recipe: [],
  tag: []
})

// Options for form
const iconOptions = [
  { label: 'Categorie', value: 'category' },
  { label: 'Eten', value: 'restaurant' },
  { label: 'Groenten', value: 'eco' },
  { label: 'Vlees', value: 'set_meal' },
  { label: 'Zuivel', value: 'egg' },
  { label: 'Keuken', value: 'kitchen' },
  { label: 'Diepvries', value: 'ac_unit' },
  { label: 'Bakkerij', value: 'bakery_dining' },
  { label: 'Dranken', value: 'local_drink' },
  { label: 'Kruiden', value: 'grass' },
  { label: 'Dessert', value: 'cake' },
  { label: 'Ontbijt', value: 'free_breakfast' },
  { label: 'Lunch', value: 'lunch_dining' },
  { label: 'Diner', value: 'dinner_dining' },
  { label: 'Snack', value: 'cookie' },
  { label: 'Gezond', value: 'favorite' },
  { label: 'Vegetarisch', value: 'eco' },
  { label: 'Veganistisch', value: 'nature' },
  { label: 'Glutenvrij', value: 'no_meals' },
  { label: 'Snel', value: 'speed' },
  { label: 'Makkelijk', value: 'thumb_up' },
  { label: 'Feest', value: 'celebration' },
  { label: 'Comfort', value: 'home' },
  { label: 'Internationaal', value: 'public' },
  { label: 'Seizoen', value: 'wb_sunny' },
  { label: 'Overig', value: 'more_horiz' }
]

const colorOptions = [
  { label: 'Primair', value: 'primary', hex: '#1976d2' },
  { label: 'Secundair', value: 'secondary', hex: '#26a69a' },
  { label: 'Accent', value: 'accent', hex: '#9c27b0' },
  { label: 'Positief', value: 'positive', hex: '#21ba45' },
  { label: 'Negatief', value: 'negative', hex: '#c10015' },
  { label: 'Info', value: 'info', hex: '#31ccec' },
  { label: 'Waarschuwing', value: 'warning', hex: '#f2c037' },
  { label: 'Rood', value: 'red', hex: '#f44336' },
  { label: 'Roze', value: 'pink', hex: '#e91e63' },
  { label: 'Paars', value: 'purple', hex: '#9c27b0' },
  { label: 'Diep Paars', value: 'deep-purple', hex: '#673ab7' },
  { label: 'Indigo', value: 'indigo', hex: '#3f51b5' },
  { label: 'Blauw', value: 'blue', hex: '#2196f3' },
  { label: 'Licht Blauw', value: 'light-blue', hex: '#03a9f4' },
  { label: 'Cyaan', value: 'cyan', hex: '#00bcd4' },
  { label: 'Teal', value: 'teal', hex: '#009688' },
  { label: 'Groen', value: 'green', hex: '#4caf50' },
  { label: 'Licht Groen', value: 'light-green', hex: '#8bc34a' },
  { label: 'Limoen', value: 'lime', hex: '#cddc39' },
  { label: 'Geel', value: 'yellow', hex: '#ffeb3b' },
  { label: 'Amber', value: 'amber', hex: '#ffc107' },
  { label: 'Oranje', value: 'orange', hex: '#ff9800' },
  { label: 'Diep Oranje', value: 'deep-orange', hex: '#ff5722' },
  { label: 'Bruin', value: 'brown', hex: '#795548' },
  { label: 'Grijs', value: 'grey', hex: '#9e9e9e' },
  { label: 'Blauw Grijs', value: 'blue-grey', hex: '#607d8b' }
]

// Computed
const ingredientCategories = computed(() => {
  // Get categories from store and add custom ones
  const storeCategories = recipeStore.ingredientCategories.map(cat => ({
    ...cat,
    icon: getCategoryIcon(cat.value),
    color: getCategoryColor(cat.value),
    isDefault: true,
    count: getIngredientCount(cat.value)
  }))

  const customCats = customCategories.value.ingredient.map(cat => ({
    ...cat,
    isDefault: false,
    count: getIngredientCount(cat.value)
  }))

  return [...storeCategories, ...customCats]
})

// Helper functions for category icons and colors
const getCategoryIcon = (value) => {
  const iconMap = {
    produce: 'eco',
    meat: 'set_meal',
    dairy: 'egg',
    pantry: 'kitchen',
    frozen: 'ac_unit',
    bakery: 'bakery_dining',
    beverages: 'local_drink',
    condiments: 'restaurant',
    spices: 'grass',
    other: 'more_horiz'
  }
  return iconMap[value] || 'category'
}

const getCategoryColor = (value) => {
  const colorMap = {
    produce: 'green',
    meat: 'red',
    dairy: 'orange',
    pantry: 'brown',
    frozen: 'light-blue',
    bakery: 'amber',
    beverages: 'blue',
    condiments: 'purple',
    spices: 'green',
    other: 'grey'
  }
  return colorMap[value] || 'primary'
}

const recipeCategories = computed(() => {
  // Get categories from store
  const storeCategories = recipeStore.categories.map(cat => ({
    value: cat.toLowerCase().replace(/\s+/g, '_'),
    label: cat,
    icon: 'restaurant_menu',
    color: 'primary',
    isDefault: true,
    count: getRecipeCount(cat)
  }))

  const customCats = customCategories.value.recipe.map(cat => ({
    ...cat,
    isDefault: false,
    count: getRecipeCount(cat.value)
  }))

  return [...storeCategories, ...customCats]
})

const recipeTags = computed(() => {
  // Get tags from store
  const storeTags = recipeStore.tags.map(tag => ({
    value: tag.toLowerCase().replace(/\s+/g, '_'),
    label: tag,
    color: getTagColor(tag),
    isDefault: true,
    count: getTagCount(tag)
  }))

  const customTags = customCategories.value.tag.map(tag => ({
    ...tag,
    isDefault: false,
    count: getTagCount(tag.value)
  }))

  return [...storeTags, ...customTags]
})

const getTagColor = (tag) => {
  const colors = ['primary', 'secondary', 'accent', 'positive', 'info', 'warning']
  const index = tag.length % colors.length
  return colors[index]
}

// Watch for form changes to auto-generate value
watch(() => categoryForm.value.label, (newLabel) => {
  if (newLabel && !editingCategory.value) {
    categoryForm.value.value = newLabel
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '_')
  }
})

// Methods
const loadCategories = async () => {
  loading.value.ingredients = true
  loading.value.recipes = true
  loading.value.tags = true

  try {
    // Load ingredient categories from API
    await recipeStore.fetchIngredientCategories()

    // Load recipe categories and tags
    await recipeStore.fetchCategories()
    await recipeStore.fetchTags()

    // Load custom categories from localStorage
    const stored = localStorage.getItem('customCategories')
    if (stored) {
      customCategories.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('Error loading categories:', error)
    $q.notify({
      type: 'negative',
      message: 'Fout bij laden van categorieën'
    })
  } finally {
    loading.value.ingredients = false
    loading.value.recipes = false
    loading.value.tags = false
  }
}

const saveCategories = () => {
  localStorage.setItem('customCategories', JSON.stringify(customCategories.value))
}

const getIngredientCount = (category) => {
  // Count ingredients with this category across all recipes
  let count = 0
  recipeStore.recipes.forEach(recipe => {
    if (recipe.ingredients) {
      count += recipe.ingredients.filter(ing => ing.category === category).length
    }
  })
  return count
}

const getRecipeCount = (category) => {
  // Count recipes with this category
  return recipeStore.recipes.filter(recipe =>
    recipe.categories && recipe.categories.includes(category)
  ).length
}

const getTagCount = (tag) => {
  // Count recipes with this tag
  return recipeStore.recipes.filter(recipe =>
    recipe.tags && recipe.tags.includes(tag)
  ).length
}

const openCreateDialog = (type) => {
  currentType.value = type
  editingCategory.value = null
  categoryForm.value = {
    label: '',
    value: '',
    icon: type === 'ingredient' ? 'category' : type === 'recipe' ? 'restaurant_menu' : 'local_offer',
    color: 'primary'
  }
  showCreateDialog.value = true
}

const editCategory = (category, type) => {
  currentType.value = type
  editingCategory.value = category
  categoryForm.value = { ...category }
  showCreateDialog.value = true
}

const saveCategory = async () => {
  if (!categoryForm.value.label) {
    $q.notify({
      type: 'negative',
      message: 'Naam is verplicht'
    })
    return
  }

  saving.value = true

  try {
    const categoryData = { ...categoryForm.value }

    if (editingCategory.value) {
      // Update existing category
      const categories = customCategories.value[currentType.value]
      const index = categories.findIndex(cat => cat.value === editingCategory.value.value)
      if (index !== -1) {
        categories[index] = categoryData
      }
    } else {
      // Create new category
      customCategories.value[currentType.value].push(categoryData)
    }

    saveCategories()

    $q.notify({
      type: 'positive',
      message: editingCategory.value ? 'Categorie bijgewerkt!' : 'Categorie toegevoegd!'
    })

    cancelEdit()
  } catch (error) {
    console.error('Error saving category:', error)
    $q.notify({
      type: 'negative',
      message: 'Fout bij opslaan van categorie'
    })
  } finally {
    saving.value = false
  }
}

const deleteCategory = (category, type) => {
  if (category.count > 0) {
    $q.notify({
      type: 'warning',
      message: 'Kan categorie niet verwijderen: nog in gebruik'
    })
    return
  }

  categoryToDelete.value = { ...category, type }
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (!categoryToDelete.value) return

  deleting.value = true

  try {
    const categories = customCategories.value[categoryToDelete.value.type]
    const index = categories.findIndex(cat => cat.value === categoryToDelete.value.value)

    if (index !== -1) {
      categories.splice(index, 1)
      saveCategories()

      $q.notify({
        type: 'positive',
        message: 'Categorie verwijderd!'
      })
    }

    showDeleteDialog.value = false
    categoryToDelete.value = null
  } catch (error) {
    console.error('Error deleting category:', error)
    $q.notify({
      type: 'negative',
      message: 'Fout bij verwijderen van categorie'
    })
  } finally {
    deleting.value = false
  }
}

const cancelEdit = () => {
  showCreateDialog.value = false
  editingCategory.value = null
  categoryForm.value = {
    label: '',
    value: '',
    icon: 'category',
    color: 'primary'
  }
}

onMounted(async () => {
  await loadCategories()
})
</script>

<style scoped>
.category-item {
  transition: background-color 0.2s;
}

.category-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #ddd;
}
</style>
