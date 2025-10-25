// Image utility functions for handling recipe images

/**
 * Get the full URL for a recipe image
 * @param {string} imagePath - The image path from the API
 * @returns {string} - Full image URL
 */
export function getImageUrl(imagePath) {
  if (!imagePath) return null

  // If it's already a full URL, return as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }

  // Get the base URL from environment or axios config
  const baseURL = process.env.NODE_ENV === 'production'
    ? 'https://proud-mercy-production.up.railway.app'
    : 'http://localhost:8000'

  // Remove leading slash if present to avoid double slashes
  const cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath

  return `${baseURL}/${cleanPath}`
}

/**
 * Get a placeholder image URL
 * @returns {string} - Placeholder image URL
 */
export function getPlaceholderImage() {
  return '/placeholder-recipe.jpg'
}

/**
 * Get recipe image with fallback to placeholder
 * @param {string} imagePath - The image path from the API
 * @returns {string} - Image URL or placeholder
 */
export function getRecipeImageUrl(imagePath) {
  return getImageUrl(imagePath) || getPlaceholderImage()
}
