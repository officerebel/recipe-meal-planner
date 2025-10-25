<template>
  <div class="image-upload-container">
    <!-- Image Preview -->
    <div v-if="imagePreview || modelValue" class="image-preview-container q-mb-md">
      <q-img
        :src="imagePreview || getImageUrl(modelValue)"
        :ratio="16/9"
        class="image-preview"
        fit="cover"
      >
        <div class="absolute-top-right q-pa-xs">
          <q-btn
            round
            dense
            color="negative"
            icon="close"
            size="sm"
            @click="removeImage"
          />
        </div>
      </q-img>
    </div>

    <!-- Upload Area -->
    <div
      v-else
      class="upload-area"
      :class="{ 'drag-over': isDragOver }"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <q-icon name="cloud_upload" size="48px" color="grey-5" />
      <div class="text-h6 q-mt-md">Upload Recipe Image</div>
      <div class="text-body2 text-grey-6">
        Drag & drop an image here, or click to select
      </div>
      <div class="text-caption text-grey-5 q-mt-sm">
        Supports JPG, PNG, WebP (max 5MB)
      </div>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileSelect"
    />

    <!-- Upload Progress -->
    <q-linear-progress
      v-if="uploading"
      :value="uploadProgress"
      color="primary"
      class="q-mt-md"
    />

    <!-- Error Message -->
    <div v-if="error" class="text-negative q-mt-sm">
      <q-icon name="error" class="q-mr-xs" />
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, File, null],
    default: null
  },
  maxSize: {
    type: Number,
    default: 5 * 1024 * 1024 // 5MB
  },
  allowedTypes: {
    type: Array,
    default: () => ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  }
})

const emit = defineEmits(['update:modelValue', 'upload-start', 'upload-complete', 'upload-error'])

// State
const fileInput = ref(null)
const imagePreview = ref(null)
const isDragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref(null)

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    processFile(file)
  }
}

const processFile = (file) => {
  error.value = null

  // Validate file type
  if (!props.allowedTypes.includes(file.type)) {
    error.value = 'Invalid file type. Please select a JPG, PNG, WebP, or GIF image.'
    return
  }

  // Validate file size
  if (file.size > props.maxSize) {
    error.value = `File too large. Maximum size is ${Math.round(props.maxSize / (1024 * 1024))}MB.`
    return
  }

  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)

  // Emit file
  emit('update:modelValue', file)
  emit('upload-start', file)

  // Simulate upload progress (in real app, this would be actual upload)
  simulateUpload()
}

const simulateUpload = () => {
  uploading.value = true
  uploadProgress.value = 0

  const interval = setInterval(() => {
    uploadProgress.value += 0.1
    if (uploadProgress.value >= 1) {
      clearInterval(interval)
      uploading.value = false
      emit('upload-complete')
    }
  }, 100)
}

const removeImage = () => {
  imagePreview.value = null
  emit('update:modelValue', null)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const getImageUrl = (image) => {
  if (!image) return null
  if (typeof image === 'string') return image
  if (image instanceof File) return URL.createObjectURL(image)
  return null
}
</script>

<style scoped>
.image-upload-container {
  width: 100%;
}

.upload-area {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #1976d2;
  background-color: #f5f9ff;
}

.upload-area.drag-over {
  border-color: #1976d2;
  background-color: #e3f2fd;
  transform: scale(1.02);
}

.image-preview-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview {
  border-radius: 8px;
  max-height: 300px;
}

@media (max-width: 600px) {
  .upload-area {
    padding: 1rem;
  }

  .image-preview {
    max-height: 200px;
  }
}
</style>
