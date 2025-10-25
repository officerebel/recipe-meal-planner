<template>
  <q-page class="q-pa-lg">
    <!-- Child-friendly header -->
    <div class="text-center q-mb-xl">
      <div class="text-h3 text-primary q-mb-md">
        <q-icon name="child_care" size="48px" class="q-mr-sm" />
        Hallo {{ childName }}! 👋
      </div>
      <div class="text-h6 text-grey-7">
        Wat wil je vandaag eten?
      </div>
    </div>

    <!-- Quick actions for children -->
    <div class="row q-gutter-lg justify-center">
      <!-- View Recipes -->
      <div class="col-12 col-md-4">
        <q-card class="child-card text-center cursor-pointer" @click="viewRecipes">
          <q-card-section class="q-pa-xl">
            <q-icon name="restaurant_menu" size="64px" color="primary" />
            <div class="text-h5 q-mt-md">Recepten Bekijken</div>
            <div class="text-body2 text-grey-6 q-mt-sm">
              Bekijk alle lekkere recepten van de familie
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Suggest Meals -->
      <div class="col-12 col-md-4" v-if="canSuggestMeals">
        <q-card class="child-card text-center cursor-pointer" @click="suggestMeal">
          <q-card-section class="q-pa-xl">
            <q-icon name="lightbulb" size="64px" color="orange" />
            <div class="text-h5 q-mt-md">Maaltijd Voorstellen</div>
            <div class="text-body2 text-grey-6 q-mt-sm">
              Stel voor wat we deze week gaan eten
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- View Meal Plan -->
      <div class="col-12 col-md-4">
        <q-card class="child-card text-center cursor-pointer" @click="viewMealPlan">
          <q-card-section class="q-pa-xl">
            <q-icon name="calendar_today" size="64px" color="green" />
            <div class="text-h5 q-mt-md">Deze Week</div>
            <div class="text-body2 text-grey-6 q-mt-sm">
              Bekijk wat we deze week gaan eten
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Favorite Recipes -->
    <div class="q-mt-xl" v-if="favoriteRecipes.length > 0">
      <div class="text-h5 q-mb-md text-center">
        <q-icon name="favorite" color="red" class="q-mr-sm" />
        Jouw Favoriete Recepten
      </div>

      <div class="row q-gutter-md">
        <div
          v-for="recipe in favoriteRecipes.slice(0, 3)"
          :key="recipe.id"
          class="col-12 col-md-4"
        >
          <q-card class="recipe-card cursor-pointer" @click="viewRecipe(recipe.id)">
            <q-img
              :src="getRecipeImageUrl(recipe.image)"
              height="150px"
              class="recipe-image"
            >
              <div class="absolute-bottom bg-transparent">
                <div class="text-h6 text-white">{{ recipe.title }}</div>
              </div>
            </q-img>
            <q-card-section>
              <div class="row items-center">
                <q-icon name="schedule" size="sm" class="q-mr-xs" />
                <span class="text-caption">{{ recipe.total_time || recipe.prep_time || '?' }} min</span>
                <q-space />
                <q-rating
                  v-model="recipe.rating"
                  size="sm"
                  color="orange"
                  readonly
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Meal Suggestion Dialog -->
    <q-dialog v-model="showSuggestionDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Wat wil je voorstellen? 🍽️</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="submitSuggestion" class="q-gutter-md">
            <q-select
              v-model="suggestion.recipe_id"
              :options="recipeOptions"
              option-value="id"
              option-label="title"
              label="Kies een recept"
              outlined
              emit-value
              map-options
            />

            <q-select
              v-model="suggestion.meal_type"
              :options="mealTypeOptions"
              label="Voor welke maaltijd?"
              outlined
              emit-value
              map-options
            />

            <q-input
              v-model="suggestion.reason"
              label="Waarom wil je dit eten? (optioneel)"
              outlined
              type="textarea"
              rows="2"
              hint="Bijvoorbeeld: 'Dit is mijn favoriete pasta!'"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Annuleren" @click="showSuggestionDialog = false" />
          <q-btn
            color="primary"
            label="Voorstellen"
            @click="submitSuggestion"
            :loading="submitting"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecipeImageUrl } from 'src/utils/imageUtils'
import { useQuasar } from 'quasar'
import { useRecipeStore } from 'src/stores/recipes'
import { useFamilyStore } from 'src/stores/families'

const $q = useQuasar()
const router = useRouter()
const recipeStore = useRecipeStore()
const familyStore = useFamilyStore()

// State
const showSuggestionDialog = ref(false)
const submitting = ref(false)
const suggestion = ref({
  recipe_id: null,
  meal_type: 'dinner',
  reason: ''
})

// Computed
const childName = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.first_name || user.username || 'Vriend'
})

const canSuggestMeals = computed(() => {
  return familyStore.hasPermission('suggest_meals')
})

const favoriteRecipes = computed(() => {
  // For now, return random recipes. In a real app, this would be user's favorites
  return recipeStore.recipes.slice(0, 6)
})

const recipeOptions = computed(() => {
  return recipeStore.recipes.map(recipe => ({
    id: recipe.id,
    title: recipe.title
  }))
})

const mealTypeOptions = [
  { label: 'Ontbijt 🥞', value: 'breakfast' },
  { label: 'Lunch 🥪', value: 'lunch' },
  { label: 'Diner 🍽️', value: 'dinner' },
  { label: 'Tussendoortje 🍪', value: 'snack' }
]

// Methods
const viewRecipes = () => {
  router.push({ name: 'recipes' })
}

const viewMealPlan = () => {
  router.push({ name: 'meal-plans' })
}

const viewRecipe = (id) => {
  router.push({ name: 'recipe-detail', params: { id } })
}

const suggestMeal = () => {
  showSuggestionDialog.value = true
}

const submitSuggestion = async () => {
  if (!suggestion.value.recipe_id) {
    $q.notify({
      type: 'warning',
      message: 'Kies eerst een recept!'
    })
    return
  }

  submitting.value = true

  try {
    // TODO: Implement meal suggestion API
    // For now, just show a success message

    $q.notify({
      type: 'positive',
      message: 'Bedankt voor je voorstel! Papa/Mama zal het bekijken. 😊',
      timeout: 3000
    })

    showSuggestionDialog.value = false
    suggestion.value = {
      recipe_id: null,
      meal_type: 'dinner',
      reason: ''
    }
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Er ging iets mis. Probeer het nog eens.'
    })
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await recipeStore.fetchRecipes()
  await familyStore.initializeFamilyContext()
})
</script>

<style scoped>
.child-card {
  border-radius: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.child-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.recipe-card {
  border-radius: 12px;
  overflow: hidden;
}

.recipe-image {
  border-radius: 12px 12px 0 0;
}
</style>
