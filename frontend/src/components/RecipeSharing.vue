<template>
  <div class="recipe-sharing">
    <!-- Share Toggle Button -->
    <q-btn
      v-if="canShare"
      :icon="isShared ? 'family_restroom' : 'person'"
      :label="buttonLabel"
      :color="isShared ? 'positive' : 'secondary'"
      @click="toggleSharing"
      :loading="loading"
      :disable="loading"
      :size="size"
      :flat="flat"
      :outline="outline"
    >
      <q-tooltip v-if="showTooltip">
        {{ tooltipText }}
      </q-tooltip>
    </q-btn>

    <!-- Sharing Status Chip (alternative display) -->
    <q-chip
      v-else-if="showStatus"
      :icon="isShared ? 'family_restroom' : 'person'"
      :color="isShared ? 'positive' : 'grey-5'"
      text-color="white"
      :label="statusLabel"
      :size="size"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { recipeService } from 'src/services/recipeService'

const props = defineProps({
  recipe: {
    type: Object,
    required: true
  },
  currentUser: {
    type: Object,
    default: null
  },
  size: {
    type: String,
    default: 'md'
  },
  flat: {
    type: Boolean,
    default: false
  },
  outline: {
    type: Boolean,
    default: false
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  showStatus: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['sharing-changed', 'error'])

const $q = useQuasar()
const loading = ref(false)

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

const canShare = computed(() => {
  // Only recipe owner can share
  // This would need to be enhanced with actual user comparison
  return props.recipe && props.recipe.id
})

const isShared = computed(() => {
  return props.recipe?.is_shared_with_family || false
})

const buttonLabel = computed(() => {
  if (props.compact) {
    return isShared.value ? 'Familie' : 'Delen'
  }
  return isShared.value ? 'Gedeeld met familie' : 'Delen met familie'
})

const statusLabel = computed(() => {
  return isShared.value ? 'Gedeeld met familie' : 'Persoonlijk recept'
})

const tooltipText = computed(() => {
  return isShared.value
    ? 'Klik om niet meer te delen met familie'
    : 'Klik om te delen met familie'
})

const toggleSharing = async () => {
  if (!props.recipe) return

  loading.value = true

  try {
    console.log('🔄 Toggling family sharing for recipe:', props.recipe.id)

    const result = await recipeService.toggleFamilySharing(props.recipe.id)

    // Show success notification
    notify({
      type: 'positive',
      message: result.message,
      icon: result.is_shared_with_family ? 'family_restroom' : 'person',
      position: 'top'
    })

    // Emit event to parent component - let parent handle the update
    emit('sharing-changed', {
      recipeId: props.recipe.id,
      isShared: result.is_shared_with_family,
      result: result
    })

    console.log('✅ Recipe sharing toggled successfully:', result)

  } catch (error) {
    console.error('❌ Error toggling recipe sharing:', error)

    const errorMessage = error.message || 'Fout bij delen van recept'

    notify({
      type: 'negative',
      message: errorMessage,
      icon: 'error',
      position: 'top'
    })

    // Emit error event
    emit('error', {
      error: error,
      message: errorMessage
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recipe-sharing {
  display: inline-block;
}
</style>
