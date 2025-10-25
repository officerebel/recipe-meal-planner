<template>
  <q-item
    clickable
    :href="props.link"
    :target="props.link ? '_blank' : undefined"
    @click="handleClick"
  >
    <q-item-section v-if="props.icon" avatar>
      <q-icon :name="props.icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ props.title }}</q-item-label>
      <q-item-label caption>{{ props.caption }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true,
  },

  caption: {
    type: String,
    default: '',
  },

  link: {
    type: String,
    default: '',
  },

  route: {
    type: String,
    default: '',
  },

  icon: {
    type: String,
    default: '',
  },

  action: {
    type: Function,
    default: null,
  },
})

import { useRouter } from 'vue-router'

const router = useRouter()

const handleClick = (event) => {
  console.log('🔗 EssentialLink clicked:', props.title, 'Route:', props.route, 'Link:', props.link)

  if (props.action) {
    event.preventDefault()
    props.action()
  } else if (props.route) {
    event.preventDefault()
    // Manually handle route navigation
    console.log('📍 Navigating to route:', props.route)
    router.push({ name: props.route })
  } else if (props.link) {
    // Let the browser handle external links
    return true
  } else {
    console.warn('⚠️ No route or link defined for:', props.title)
  }
}
</script>
