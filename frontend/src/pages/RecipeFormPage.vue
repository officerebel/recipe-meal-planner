<template>
  <q-page class="q-pa-lg">
    <!-- Breadcrumb Navigation -->
    <q-breadcrumbs class="q-mb-md">
      <q-breadcrumbs-el label="Home" icon="home" :to="{ name: 'home' }" />
      <q-breadcrumbs-el label="Recipes" icon="restaurant_menu" :to="{ name: 'recipes' }" />
      <q-breadcrumbs-el :label="isEditing ? 'Edit Recipe' : 'Create New Recipe'" />
    </q-breadcrumbs>

    <div class="row justify-between items-center q-mb-lg">
      <div class="text-h4">{{ isEditing ? 'Edit Recipe' : 'Create New Recipe' }}</div>
      <q-btn
        flat
        icon="arrow_back"
        label="Back to Recipes"
        :to="{ name: 'recipes' }"
      />
    </div>

    <!-- Form Card -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <q-form @submit="onSubmit" class="q-gutter-md">
          <!-- Basic Information -->
          <div class="text-h6 q-mb-md">Basic Information</div>

          <q-input
            v-model="form.title"
            label="Recipe Title *"
            hint="Give your recipe a descriptive name"
            outlined
            :rules="[val => !!val || 'Title is required']"
          >
            <template v-slot:prepend>
              <q-icon name="restaurant_menu" />
            </template>
          </q-input>

          <q-input
            v-model="form.description"
            label="Description"
            hint="Brief description of the recipe"
            type="textarea"
            rows="3"
            outlined
          >
            <template v-slot:prepend>
              <q-icon name="description" />
            </template>
          </q-input>

          <!-- Recipe Image -->
          <div class="text-h6 q-mb-md q-mt-lg">Recipe Image</div>

          <div class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-file
                v-model="form.image"
                label="Upload Recipe Image"
                outlined
                accept="image/*"
                max-file-size="5242880"
                @rejected="onImageRejected"
              >
                <template v-slot:prepend>
                  <q-icon name="image" />
                </template>
              </q-file>
            </div>

            <!-- Image Preview -->
            <div class="col-12 col-md-6" v-if="imagePreview">
              <q-card flat bordered>
                <q-img
                  :src="imagePreview"
                  style="height: 200px"
                  class="rounded-borders"
                >
                  <div class="absolute-bottom text-subtitle2 text-center">
                    Image Preview
                  </div>
                </q-img>
                <q-card-actions align="right">
                  <q-btn flat icon="delete" color="negative" @click="removeImage" />
                </q-card-actions>
              </q-card>
            </div>
          </div>

          <!-- Timing and Servings -->
          <div class="text-h6 q-mb-md q-mt-lg">Timing & Servings</div>

          <div class="row q-gutter-md">
            <div class="col-12 col-md-3">
              <q-input
                v-model.number="form.prep_time"
                label="Prep Time (minutes)"
                type="number"
                min="0"
                outlined
              >
                <template v-slot:prepend>
                  <q-icon name="schedule" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-3">
              <q-input
                v-model.number="form.cook_time"
                label="Cook Time (minutes)"
                type="number"
                min="0"
                outlined
              >
                <template v-slot:prepend>
                  <q-icon name="timer" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-3">
              <q-input
                v-model.number="form.total_time"
                label="Total Time (minutes)"
                type="number"
                min="0"
                outlined
                :hint="calculatedTotalTime ? `Calculated: ${calculatedTotalTime} min` : ''"
              >
                <template v-slot:prepend>
                  <q-icon name="access_time" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-3">
              <q-input
                v-model.number="form.servings"
                label="Servings"
                type="number"
                min="1"
                outlined
              >
                <template v-slot:prepend>
                  <q-icon name="people" />
                </template>
              </q-input>
            </div>
          </div>

          <!-- Nutritional Information -->
          <div class="text-h6 q-mb-md q-mt-lg">
            <q-icon name="local_dining" class="q-mr-sm" />
            Voedingswaarden (per portie)
          </div>
          <div class="row q-gutter-md">
            <div class="col-12 col-md-2">
              <q-input
                v-model.number="form.calories"
                label="Calorieën"
                type="number"
                min="0"
                outlined
                suffix="kcal"
              >
                <template v-slot:prepend>
                  <q-icon name="local_fire_department" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model.number="form.protein"
                label="Eiwit"
                type="number"
                min="0"
                step="0.1"
                outlined
                suffix="g"
              >
                <template v-slot:prepend>
                  <q-icon name="fitness_center" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model.number="form.carbohydrates"
                label="Koolhydraten"
                type="number"
                min="0"
                step="0.1"
                outlined
                suffix="g"
              >
                <template v-slot:prepend>
                  <q-icon name="grain" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model.number="form.fat"
                label="Vet"
                type="number"
                min="0"
                step="0.1"
                outlined
                suffix="g"
              >
                <template v-slot:prepend>
                  <q-icon name="opacity" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model.number="form.fiber"
                label="Vezels"
                type="number"
                min="0"
                step="0.1"
                outlined
                suffix="g"
              >
                <template v-slot:prepend>
                  <q-icon name="eco" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model.number="form.sodium"
                label="Natrium"
                type="number"
                min="0"
                step="0.1"
                outlined
                suffix="mg"
              >
                <template v-slot:prepend>
                  <q-icon name="water_drop" />
                </template>
              </q-input>
            </div>
          </div>

          <!-- Categories and Tags -->
          <div class="row items-center justify-between q-mt-lg q-mb-md">
            <div class="text-h6">Categorieën & Tags</div>
            <q-btn
              flat
              dense
              color="primary"
              icon="settings"
              label="Beheer Categorieën"
              size="sm"
              :to="{ name: 'categories' }"
            />
          </div>

          <div class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-select
                v-model="form.categories"
                label="Categorieën"
                :options="categoryOptions"
                multiple
                use-chips
                use-input
                new-value-mode="add-unique"
                outlined
                hint="Selecteer of voeg categorieën toe"
              >
                <template v-slot:prepend>
                  <q-icon name="category" />
                </template>
              </q-select>
            </div>
            <div class="col-12 col-md-6">
              <q-select
                v-model="form.tags"
                label="Tags"
                :options="tagOptions"
                multiple
                use-chips
                use-input
                new-value-mode="add-unique"
                outlined
                hint="Selecteer of voeg tags toe"
              >
                <template v-slot:prepend>
                  <q-icon name="local_offer" />
                </template>
              </q-select>
            </div>
          </div>

          <!-- Ingredients -->
          <div class="text-h6 q-mb-md q-mt-lg">Ingredients</div>

          <div v-for="(ingredient, index) in form.ingredients" :key="index" class="row q-gutter-sm q-mb-sm">
            <div class="col-12 col-md-2">
              <q-input
                v-model="ingredient.amount"
                label="Hoeveelheid"
                outlined
                dense
                placeholder="2 kopjes"
              />
            </div>
            <div class="col-12 col-md-4">
              <q-input
                v-model="ingredient.name"
                label="Ingrediënt Naam *"
                outlined
                dense
                :rules="[val => !!val || 'Ingrediënt naam is verplicht']"
                placeholder="Bloem"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-select
                v-model="ingredient.category"
                :options="ingredientCategoryOptions"
                label="Categorie"
                outlined
                dense
                emit-value
                map-options
                clearable
              >
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section avatar>
                      <q-icon :name="scope.opt.icon" :color="scope.opt.color" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ scope.opt.label }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>
            <div class="col-12 col-md-3">
              <q-input
                v-model="ingredient.notes"
                label="Notities"
                outlined
                dense
                placeholder="gehakt, optioneel"
              />
            </div>
            <div class="col-12 col-md-1">
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="removeIngredient(index)"
                :disable="form.ingredients.length <= 1"
              />
            </div>
          </div>

          <q-btn
            flat
            color="primary"
            icon="add"
            label="Add Ingredient"
            @click="addIngredient"
            class="q-mb-md"
          />

          <!-- Instructions -->
          <div class="text-h6 q-mb-md q-mt-lg">Instructions</div>

          <div v-for="(instruction, index) in form.instructions" :key="index" class="row q-gutter-sm q-mb-sm">
            <div class="col-1">
              <q-chip color="primary" text-color="white" :label="index + 1" />
            </div>
            <div class="col-10">
              <q-input
                v-model="form.instructions[index]"
                :label="`Step ${index + 1} *`"
                type="textarea"
                rows="2"
                outlined
                :rules="[val => !!val || 'Instruction is required']"
                placeholder="Describe this cooking step..."
              />
            </div>
            <div class="col-1">
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="removeInstruction(index)"
                :disable="form.instructions.length <= 1"
              />
            </div>
          </div>

          <q-btn
            flat
            color="primary"
            icon="add"
            label="Add Step"
            @click="addInstruction"
            class="q-mb-md"
          />

          <!-- Form Actions -->
          <div class="row q-gutter-sm justify-end q-mt-lg">
            <q-btn
              flat
              label="Cancel"
              color="grey"
              :to="{ name: 'recipes' }"
            />
            <q-btn
              type="submit"
              :label="isEditing ? 'Update Recipe' : 'Create Recipe'"
              color="primary"
              :loading="loading"
              :disable="!isFormValid"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <!-- Preview Card (when editing) -->
    <q-card v-if="isEditing && currentRecipe" class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="preview" class="q-mr-sm" />
          Recipe Preview
        </div>

        <div class="row q-gutter-md">
          <div class="col-12 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Ingredients</div>
                <div class="text-h6 text-primary">{{ currentRecipe.ingredient_count || 0 }}</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Total Time</div>
                <div class="text-h6 text-secondary">{{ currentRecipe.total_time || 0 }} min</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Servings</div>
                <div class="text-h6 text-accent">{{ currentRecipe.servings || 0 }}</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">Source</div>
                <div class="text-body2">{{ currentRecipe.source || 'Manual' }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useRecipeStore } from 'src/stores/recipes'

const $q = useQuasar()
const router = useRouter()
const recipeStore = useRecipeStore()

// Props for editing
const props = defineProps({
  id: {
    type: String,
    default: null
  }
})

// Form state
const form = ref({
  title: '',
  description: '',
  image: null,
  prep_time: null,
  cook_time: null,
  total_time: null,
  servings: null,
  calories: null,
  protein: null,
  carbohydrates: null,
  fat: null,
  fiber: null,
  sugar: null,
  sodium: null,
  categories: [],
  tags: [],
  ingredients: [
    { name: '', amount: '', notes: '', category: null }
  ],
  instructions: ['']
})

const loading = ref(false)
const currentRecipe = ref(null)
const imagePreview = ref(null)

// Computed properties
const isEditing = computed(() => !!props.id)

const isFormValid = computed(() => {
  const hasTitle = !!form.value.title
  const hasIngredients = form.value.ingredients.some(ing => ing.name)
  const hasInstructions = form.value.instructions.some(inst => inst.trim())

  return hasTitle && hasIngredients && hasInstructions
})

const calculatedTotalTime = computed(() => {
  const prep = form.value.prep_time || 0
  const cook = form.value.cook_time || 0
  return prep + cook > 0 ? prep + cook : null
})

const categoryOptions = computed(() => {
  // Get custom categories from localStorage
  const stored = localStorage.getItem('customCategories')
  const customCategories = stored ? JSON.parse(stored) : { recipe: [] }

  // Default Dutch recipe categories
  const defaultCategories = [
    'Ontbijt', 'Lunch', 'Diner', 'Tussendoortje', 'Nagerecht',
    'Vegetarisch', 'Veganistisch', 'Glutenvrij', 'Lactosevrij',
    'Gezond', 'Comfort Food', 'Snel & Makkelijk', 'Feestelijk',
    'Internationaal', 'Nederlands', 'Italiaans', 'Aziatisch',
    'Mexicaans', 'Frans', 'Grieks', 'Indiaas', 'Thais',
    'Seizoensgebonden', 'Zomer', 'Winter', 'Herfst', 'Lente',
    'Barbecue', 'Oven', 'Slowcooker', 'Airfryer', 'Magnetron'
  ]

  // Combine default, custom, and existing categories
  const existing = recipeStore.categories || []
  const custom = customCategories.recipe.map(cat => cat.label) || []
  const formCategories = form.value.categories || []

  return [...new Set([...defaultCategories, ...custom, ...existing, ...formCategories])]
})

const tagOptions = computed(() => {
  // Get custom tags from localStorage
  const stored = localStorage.getItem('customCategories')
  const customCategories = stored ? JSON.parse(stored) : { tag: [] }

  // Default Dutch tags
  const defaultTags = [
    'Favoriet', 'Nieuw', 'Getest', 'Familie Recept', 'Feest',
    'Romantisch', 'Kinderen', 'Budget', 'Luxe', 'Simpel',
    'Indrukwekkend', 'Traditioneel', 'Modern', 'Fusion',
    'Pittig', 'Mild', 'Zoet', 'Zuur', 'Hartig', 'Fris',
    'Warm', 'Koud', 'Knapperig', 'Romig', 'Licht', 'Zwaar',
    'Proteïnerijk', 'Koolhydraatarm', 'Vetarm', 'Vezelrijk',
    'Antioxidanten', 'Superfood', 'Detox', 'Energierijk'
  ]

  // Combine default, custom, and existing tags
  const existing = recipeStore.tags || []
  const custom = customCategories.tag.map(tag => tag.label) || []
  const formTags = form.value.tags || []

  return [...new Set([...defaultTags, ...custom, ...existing, ...formTags])]
})

const ingredientCategoryOptions = computed(() => {
  // Get custom ingredient categories from localStorage
  const stored = localStorage.getItem('customCategories')
  const customCategories = stored ? JSON.parse(stored) : { ingredient: [] }

  // Get categories from store (with icons and colors added)
  const storeCategories = recipeStore.ingredientCategories.map(cat => ({
    ...cat,
    icon: getCategoryIcon(cat.value),
    color: getCategoryColor(cat.value)
  }))

  // Combine store and custom categories
  const custom = customCategories.ingredient || []

  return [...storeCategories, ...custom]
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
  return iconMap[value] || 'more_horiz'
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
  return colorMap[value] || 'grey'
}

// Safe notification function
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

// Watch for calculated total time
watch(calculatedTotalTime, (newVal) => {
  if (newVal && !form.value.total_time) {
    form.value.total_time = newVal
  }
})

// Lifecycle
onMounted(async () => {
  // Load categories and tags
  await Promise.all([
    recipeStore.fetchCategories(),
    recipeStore.fetchTags(),
    recipeStore.fetchIngredientCategories()
  ])

  if (isEditing.value) {
    await loadRecipe()
  }
})

// Methods
const loadRecipe = async () => {
  try {
    loading.value = true
    currentRecipe.value = await recipeStore.fetchRecipe(props.id)

    // Populate form with existing data
    form.value = {
      title: currentRecipe.value.title || '',
      description: currentRecipe.value.description || '',
      prep_time: currentRecipe.value.prep_time,
      cook_time: currentRecipe.value.cook_time,
      total_time: currentRecipe.value.total_time,
      servings: currentRecipe.value.servings,
      categories: currentRecipe.value.categories || [],
      tags: currentRecipe.value.tags || [],
      ingredients: currentRecipe.value.ingredients?.length > 0
        ? currentRecipe.value.ingredients.map(ing => ({
            name: ing.name || '',
            amount: ing.amount || '',
            notes: ing.notes || ''
          }))
        : [{ name: '', amount: '', notes: '' }],
      instructions: currentRecipe.value.instructions?.length > 0
        ? [...currentRecipe.value.instructions]
        : ['']
    }
  } catch (err) {
    console.error('Error loading recipe:', err)
    safeNotify({
      type: 'negative',
      message: 'Failed to load recipe'
    })
    router.push({ name: 'recipes' })
  } finally {
    loading.value = false
  }
}

const onSubmit = async () => {
  loading.value = true

  try {
    // Clean up form data
    const recipeData = {
      title: form.value.title,
      description: form.value.description,
      image: form.value.image,
      prep_time: form.value.prep_time || null,
      cook_time: form.value.cook_time || null,
      total_time: form.value.total_time || null,
      servings: form.value.servings || null,
      categories: form.value.categories || [],
      tags: form.value.tags || [],
      ingredients: form.value.ingredients
        .filter(ing => ing.name.trim())
        .map((ing, index) => ({
          name: ing.name.trim(),
          amount: ing.amount.trim(),
          notes: ing.notes.trim(),
          order: index
        })),
      instructions: form.value.instructions
        .filter(inst => inst.trim())
        .map(inst => inst.trim()),
      source: 'manual'
    }

    if (isEditing.value) {
      // Use image-aware update method
      form.value.image
        ? await recipeStore.updateRecipeWithImage(props.id, recipeData)
        : await recipeStore.updateRecipe(props.id, recipeData)
      safeNotify({
        type: 'positive',
        message: 'Recipe updated successfully!'
      })
    } else {
      // Use image-aware create method
      const newRecipe = form.value.image
        ? await recipeStore.createRecipeWithImage(recipeData)
        : await recipeStore.createRecipe(recipeData)
      safeNotify({
        type: 'positive',
        message: 'Recipe created successfully!'
      })
      // Navigate to the new recipe detail page
      router.push({ name: 'recipe-detail', params: { id: newRecipe.id } })
      return
    }

    // Navigate back to recipes list
    router.push({ name: 'recipes' })
  } catch (error) {
    console.error('Error in form submission:', error)
    safeNotify({
      type: 'negative',
      message: error.message || `Failed to ${isEditing.value ? 'update' : 'create'} recipe`
    })
  } finally {
    loading.value = false
  }
}

const addIngredient = () => {
  form.value.ingredients.push({ name: '', amount: '', notes: '', category: null })
}

const removeIngredient = (index) => {
  if (form.value.ingredients.length > 1) {
    form.value.ingredients.splice(index, 1)
  }
}

const addInstruction = () => {
  form.value.instructions.push('')
}

const removeInstruction = (index) => {
  if (form.value.instructions.length > 1) {
    form.value.instructions.splice(index, 1)
  }
}

// Image handling methods
const onImageRejected = (rejectedEntries) => {
  safeNotify({
    type: 'negative',
    message: `Image rejected: ${rejectedEntries[0].failedPropValidation}`
  })
}

const removeImage = () => {
  form.value.image = null
  imagePreview.value = null
}

// Watch for image changes to create preview
watch(() => form.value.image, (newImage) => {
  if (newImage) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(newImage)
  } else {
    imagePreview.value = null
  }
})
</script>
