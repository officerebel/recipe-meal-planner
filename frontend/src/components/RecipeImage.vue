<template>
  <div class="recipe-image-container">
    <q-img
      v-if="!imageError && imageUrl"
      :src="imageUrl"
      :alt="alt"
      :style="style"
      :class="imageClass"
      @error="handleImageError"
      :loading="loading"
      :placeholder-src="placeholderUrl"
    >
      <template v-slot:error>
        <div class="absolute-full flex flex-center bg-grey-3 text-grey-6">
          <div class="text-center">
            <q-icon name="image_not_supported" size="48px" class="q-mb-sm" />
            <div class="text-caption">Afbeelding niet beschikbaar</div>
          </div>
        </div>
      </template>

      <template v-slot:loading>
        <div class="absolute-full flex flex-center bg-grey-2">
          <q-spinner-dots size="40px" color="primary" />
        </div>
      </template>

      <slot />
    </q-img>

    <!-- Fallback when no image URL -->
    <div
      v-else
      class="recipe-image-placeholder flex flex-center bg-grey-3 text-grey-6"
      :style="style"
      :class="imageClass"
    >
      <div class="text-center">
        <q-icon name="restaurant" size="48px" class="q-mb-sm" />
        <div class="text-caption">Geen afbeelding</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getRecipeImageUrl } from 'src/utils/imageUtils'

const props = defineProps({
  src: {
    type: String,
    default: null
  },
  alt: {
    type: String,
    default: 'Recipe image'
  },
  style: {
    type: [String, Object],
    default: null
  },
  class: {
    type: String,
    default: ''
  },
  loading: {
    type: String,
    default: 'lazy'
  },
  placeholder: {
    type: String,
    default: null
  }
})

const imageError = ref(false)

const imageUrl = computed(() => {
  if (!props.src) return null
  return getRecipeImageUrl(props.src)
})

const placeholderUrl = computed(() => {
  // Use a data URL for a simple placeholder to avoid 404s
  return props.placeholder || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5SZWNpcGUgSW1hZ2U8L3RleHQ+PC9zdmc+'
})

const imageClass = computed(() => {
  return `recipe-image ${props.class}`.trim()
})

const handleImageError = (error) => {
  console.warn('Recipe image failed to load:', props.src, error)
  imageError.value = true
}
</script>

<style scoped>
.recipe-image-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.recipe-image-placeholder {
  width: 100%;
  height: 100%;
  min-height: 200px;
  border-radius: 4px;
  border: 2px dashed #e0e0e0;
}

.recipe-image {
  border-radius: 4px;
}
</style>
