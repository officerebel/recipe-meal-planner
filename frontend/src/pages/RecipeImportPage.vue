<template>
  <q-page class="q-pa-lg">
    <div class="text-h4 q-mb-lg">Import Recipe from PDF or Image</div>

    <!-- File Upload Area -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="upload_file" class="q-mr-sm" />
          Upload PDF or Image File
        </div>

        <!-- Instructions -->
        <q-banner class="bg-info text-white q-mb-md">
          <template v-slot:avatar>
            <q-icon name="info" />
          </template>
          <div>
            <strong>How it works:</strong>
            <ul class="q-ma-none q-pl-md">
              <li>Upload a PDF file or image (PNG, JPG, etc.) containing a recipe</li>
              <li>For images: OCR technology will extract text from the image</li>
              <li>Click "Preview" to see extracted recipe before saving</li>
              <li>Click "Import Recipe" to add directly to your collection</li>
            </ul>
          </div>
        </q-banner>

        <q-file
          v-model="selectedFile"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.webp"
          max-file-size="10485760"
          label="Choose PDF or image file"
          outlined
          clearable
          @rejected="onRejected"
          class="q-mb-md"
        >
          <template v-slot:prepend>
            <q-icon :name="getFileIcon(selectedFile)" />
          </template>
          <template v-slot:hint>
            Maximum file size: 10MB. Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP, WebP
          </template>
        </q-file>

        <!-- File Info -->
        <div v-if="selectedFile" class="q-mb-md">
          <q-chip color="primary" text-color="white" icon="description">
            {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </q-chip>

          <!-- Parsing Options -->
          <div class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">Parsing Options</div>
            <q-option-group
              v-model="parsingMode"
              :options="parsingOptions"
              color="primary"
              inline
            />
          </div>

          <!-- Language Detection -->
          <div class="q-mt-md">
            <q-select
              v-model="expectedLanguage"
              :options="languageOptions"
              label="Expected Language"
              outlined
              dense
              class="q-mb-sm"
            />
          </div>
        </div>

        <!-- Authentication Warning -->
        <q-banner v-if="!hasAuthToken" class="bg-warning text-white q-mb-md">
          <template v-slot:avatar>
            <q-icon name="warning" />
          </template>
          Authenticatie vereist voor PDF import. Log in om deze functie te gebruiken.
        </q-banner>

        <!-- Action Buttons -->
        <div class="q-gutter-sm">
          <q-btn
            color="secondary"
            label="Preview Recipe"
            icon="preview"
            :loading="loading && currentAction === 'preview'"
            :disable="!selectedFile || loading"
            @click="previewRecipe"
            size="md"
          />

          <q-btn
            color="primary"
            label="Import Recipe"
            icon="upload"
            :loading="loading && currentAction === 'import'"
            :disable="!selectedFile || loading"
            @click="importRecipe"
            size="md"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Preview/Result Area -->
    <q-card v-if="previewData || importedRecipe">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          {{ previewData ? 'Preview' : 'Imported Recipe' }}
        </div>

        <!-- Validation Results -->
        <div v-if="previewData && previewData.validationResult" class="q-mb-md">
          <q-banner
            :class="getValidationBannerClass(previewData.validationResult)"
            :icon="getValidationIcon(previewData.validationResult)"
          >
            <div class="text-weight-medium">
              Parsing Quality: {{ previewData.validationResult.score }}%
            </div>

            <div v-if="previewData.validationResult.errors.length > 0" class="q-mt-sm">
              <div class="text-weight-medium text-negative">Errors:</div>
              <ul class="q-ma-none q-pl-md">
                <li v-for="error in previewData.validationResult.errors" :key="error">
                  {{ error }}
                </li>
              </ul>
            </div>

            <div v-if="previewData.validationResult.warnings.length > 0" class="q-mt-sm">
              <div class="text-weight-medium text-warning">Warnings:</div>
              <ul class="q-ma-none q-pl-md">
                <li v-for="warning in previewData.validationResult.warnings" :key="warning">
                  {{ warning }}
                </li>
              </ul>
            </div>
          </q-banner>
        </div>

        <div v-if="previewData || importedRecipe" class="q-gutter-md">
          <div>
            <strong>Title:</strong> {{ getRecipeData().title }}
          </div>
          <div v-if="getRecipeData().prep_time">
            <strong>Prep Time:</strong> {{ getRecipeData().prep_time }} minutes
          </div>
          <div v-if="getRecipeData().cook_time">
            <strong>Cook Time:</strong> {{ getRecipeData().cook_time }} minutes
          </div>
          <div v-if="getRecipeData().servings">
            <strong>Servings:</strong> {{ getRecipeData().servings }}
          </div>

          <div v-if="getRecipeData().ingredients && getRecipeData().ingredients.length">
            <strong>Ingredients:</strong>
            <ul>
              <li v-for="ingredient in getRecipeData().ingredients" :key="ingredient.name">
                {{ ingredient.amount }} {{ ingredient.name }}
              </li>
            </ul>
          </div>

          <div v-if="getRecipeData().instructions && (Array.isArray(getRecipeData().instructions) ? getRecipeData().instructions.length : getRecipeData().instructions.trim().length)">
            <strong>Instructions:</strong>
            <ol v-if="Array.isArray(getRecipeData().instructions)">
              <li v-for="instruction in getRecipeData().instructions" :key="instruction">
                {{ instruction }}
              </li>
            </ol>
            <div v-else class="q-pl-md">
              {{ getRecipeData().instructions }}
            </div>
          </div>
        </div>

        <div v-if="previewData" class="q-mt-md">
          <q-btn
            color="primary"
            label="Save Recipe"
            icon="save"
            @click="savePreviewedRecipe"
          />
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRecipeStore } from 'src/stores/recipes'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'


// State
const selectedFile = ref(null)
const loading = ref(false)
const previewData = ref(null)
const parsingMode = ref('auto')
const expectedLanguage = ref('nl')

// Parsing options
const parsingOptions = [
  { label: 'Auto Detect', value: 'auto' },
  { label: 'Structured Recipe', value: 'structured' },
  { label: 'Free Text', value: 'freetext' }
]

const languageOptions = [
  { label: 'Dutch (Nederlands)', value: 'nl' },
  { label: 'English', value: 'en' },
  { label: 'Auto Detect', value: 'auto' }
]
const importedRecipe = ref(null)
const currentAction = ref('')

// Computed properties
const hasAuthToken = computed(() => {
  return !!localStorage.getItem('auth_token')
})

// Store and utilities
const recipeStore = useRecipeStore()
const $q = useQuasar()
const router = useRouter()



// Notification function
const showMessage = (message, type = 'positive') => {
  try {
    $q.notify({
      message,
      type,
      position: 'top'
    })
  } catch (error) {
    console.error('Notification error:', error)
    // Fallback to console log if notification fails
    console.log(`${type.toUpperCase()}: ${message}`)
  }
}

// Utility function to format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Get appropriate icon for file type
const getFileIcon = (file) => {
  if (!file) return 'upload_file'

  const extension = file.name.toLowerCase().split('.').pop()

  switch (extension) {
    case 'pdf':
      return 'picture_as_pdf'
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'webp':
    case 'bmp':
    case 'tiff':
      return 'image'
    default:
      return 'description'
  }
}

// Get current recipe data (preview or imported)
const getRecipeData = () => {
  return previewData.value || importedRecipe.value || {}
}



// Event handlers
const onRejected = (rejectedEntries) => {
  showMessage(`${rejectedEntries.length} file(s) did not pass validation constraints`, 'error')
}

const importRecipe = async () => {
  if (!selectedFile.value) return

  currentAction.value = 'import'
  loading.value = true

  try {
    const fileType = selectedFile.value.name.toLowerCase().split('.').pop()
    const isImage = ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'].includes(fileType)
    console.log(`Importing recipe from ${isImage ? 'image' : 'PDF'}:`, selectedFile.value.name)

    // Use the new enhanced import function
    const importResult = await recipeStore.importFromFile(selectedFile.value)

    // Extract the recipe from the import result
    const recipe = importResult.recipe || importResult
    importedRecipe.value = recipe
    previewData.value = null

    showMessage('Recipe imported successfully!', 'positive')

    // Navigate to the new recipe after a short delay
    if (recipe && recipe.id) {
      setTimeout(() => {
        router.push(`/recipes/${recipe.id}`)
      }, 1500)
    }

  } catch (error) {
    console.error('Import error:', error)
    showMessage(error.message || 'Failed to import recipe', 'negative')
  } finally {
    loading.value = false
    currentAction.value = ''
  }
}

const previewRecipe = async () => {
  console.log('Preview Recipe button clicked!')

  if (!selectedFile.value) {
    showMessage('Selecteer eerst een PDF bestand', 'warning')
    return
  }

  // Check authentication - but continue with mock data if not authenticated
  const token = localStorage.getItem('auth_token')
  if (!token) {
    console.log('No authentication token, will use mock data fallback')
  }

  currentAction.value = 'preview'
  loading.value = true

  try {
    console.log('Previewing recipe from PDF:', selectedFile.value.name)
    console.log('Parsing mode:', parsingMode.value)
    console.log('Expected language:', expectedLanguage.value)
    console.log('Authentication token available:', !!token)

    // Use enhanced store function with parsing options
    const recipe = await recipeStore.previewFromFile(selectedFile.value, {
      parsingMode: parsingMode.value,
      expectedLanguage: expectedLanguage.value
    })

    console.log('Recipe preview received:', recipe)

    if (!recipe) {
      throw new Error('No recipe data received')
    }

    // Validate the parsed recipe
    const validationResult = validateParsedRecipe(recipe)

    if (validationResult.warnings.length > 0) {
      showMessage(`Recept geparseerd met ${validationResult.warnings.length} waarschuwingen. Controleer de preview zorgvuldig.`, 'warning')
    }

    previewData.value = {
      ...recipe,
      validationResult
    }
    importedRecipe.value = null

    showMessage('Recept preview gegenereerd!', 'positive')

  } catch (error) {
    console.error('Preview error:', error)
    showMessage(error.message || 'Fout bij het genereren van preview', 'negative')
  } finally {
    loading.value = false
    currentAction.value = ''
  }
}

const validateParsedRecipe = (recipe) => {
  const warnings = []
  const errors = []

  // Check for missing essential fields
  if (!recipe.title || recipe.title.trim().length < 3) {
    errors.push('Recipe title is missing or too short')
  }

  if (!recipe.ingredients || recipe.ingredients.length === 0) {
    errors.push('No ingredients found')
  }

  if (!recipe.instructions || typeof recipe.instructions !== 'string' || recipe.instructions.trim().length < 10) {
    warnings.push('Instructions are very short or missing')
  }

  // Check for malformed ingredients
  if (recipe.ingredients) {
    const malformedIngredients = recipe.ingredients.filter(ing =>
      !ing.name || ing.name.length < 2 || /^\d+$/.test(ing.name)
    )

    if (malformedIngredients.length > 0) {
      warnings.push(`${malformedIngredients.length} ingredients may be malformed`)
    }
  }

  // Check for reasonable prep/cook times
  if (recipe.prep_time && (recipe.prep_time < 1 || recipe.prep_time > 480)) {
    warnings.push('Prep time seems unrealistic')
  }

  if (recipe.cook_time && (recipe.cook_time < 1 || recipe.cook_time > 720)) {
    warnings.push('Cook time seems unrealistic')
  }

  // Check for reasonable servings
  if (recipe.servings && (recipe.servings < 1 || recipe.servings > 20)) {
    warnings.push('Serving size seems unrealistic')
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    score: Math.max(0, 100 - (errors.length * 25) - (warnings.length * 10))
  }
}

const savePreviewedRecipe = async () => {
  if (!previewData.value) return

  loading.value = true

  try {
    // Create recipe from preview data (exclude validation result)
    const recipeData = { ...previewData.value }
    delete recipeData.validationResult
    const recipe = await recipeStore.createRecipe(recipeData)

    importedRecipe.value = recipe
    previewData.value = null

    showMessage('Recipe saved successfully!', 'positive')

    // Navigate to the new recipe after a short delay
    if (recipe && recipe.id) {
      setTimeout(() => {
        router.push(`/recipes/${recipe.id}`)
      }, 1500)
    }

  } catch (error) {
    console.error('Save error:', error)
    showMessage(error.message || 'Failed to save recipe', 'negative')
  } finally {
    loading.value = false
  }
}

const getValidationBannerClass = (validation) => {
  if (!validation.isValid) return 'bg-negative text-white'
  if (validation.score >= 80) return 'bg-positive text-white'
  if (validation.score >= 60) return 'bg-warning text-white'
  return 'bg-orange text-white'
}

const getValidationIcon = (validation) => {
  if (!validation.isValid) return 'error'
  if (validation.score >= 80) return 'check_circle'
  if (validation.score >= 60) return 'warning'
  return 'info'
}
</script>
