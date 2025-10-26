<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <router-link to="/" class="text-white no-decoration">
            Recipe Meal Planner
          </router-link>
        </q-toolbar-title>

        <!-- Top Navigation Links - Hidden on mobile -->
        <div class="q-gutter-sm q-mr-md gt-sm">
          <q-btn
            v-for="link in linksList"
            :key="link.title"
            flat
            :icon="link.icon"
            :label="link.title"
            :to="link.route ? { name: link.route } : undefined"
            :href="link.link"
            :target="link.link ? '_blank' : undefined"
            @click="link.action ? link.action() : undefined"
            class="text-white"
          />
        </div>

        <q-btn flat round icon="help_outline" class="q-mr-sm gt-xs">
          <q-tooltip class="bg-dark text-white" anchor="bottom middle" self="top middle">
            <div class="text-body2 q-mb-sm">Keyboard Shortcuts:</div>
            <div class="text-caption">
              <div>Ctrl/Cmd + N: Create Recipe</div>
              <div>Ctrl/Cmd + I: Import Recipe</div>
              <div>Ctrl/Cmd + M: Create Meal Plan</div>
              <div>Ctrl/Cmd + /: Toggle Menu</div>
            </div>
          </q-tooltip>
        </q-btn>

        <!-- User Menu -->
        <q-btn-dropdown flat round icon="account_circle" class="q-mr-sm">
          <q-list>
            <q-item-label header>
              User Menu
            </q-item-label>
            <q-item clickable @click="handleProfile">
              <q-item-section avatar>
                <q-icon name="person" />
              </q-item-section>
              <q-item-section>Profile</q-item-section>
            </q-item>
            <q-item clickable @click="handleSettings">
              <q-item-section avatar>
                <q-icon name="settings" />
              </q-item-section>
              <q-item-section>Settings</q-item-section>
            </q-item>

            <q-separator />
            <q-item clickable @click="handleLogout">
              <q-item-section avatar>
                <q-icon name="logout" />
              </q-item-section>
              <q-item-section>Logout</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>

        <div class="text-caption gt-xs">v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header class="text-primary text-weight-bold">
          <q-icon name="restaurant" class="q-mr-sm" />
          Main Navigation
        </q-item-label>

        <EssentialLink v-for="link in linksList" :key="link.title" v-bind="link" />

        <q-separator class="q-my-md" />

        <q-item-label header class="text-grey-7">
          <q-icon name="add_circle" class="q-mr-sm" />
          Quick Actions
        </q-item-label>

        <EssentialLink v-for="link in secondaryLinks" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'


import EssentialLink from 'components/EssentialLink.vue'

const router = useRouter()
const $q = useQuasar()
const authStore = useAuthStore()
// const familyStore = useFamilyStore() // Not used directly in this component

// Navigation helper (removed - family management moved to Settings)

// Get current user role
const currentUserRole = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const familyMembers = JSON.parse(localStorage.getItem('familyMembers') || '[]')
  const currentMember = familyMembers.find(m => m.user.id === user.id)
  return currentMember?.role || 'member'
})

// Universal navigation - everyone sees the same main menu
const linksList = computed(() => {
  // Base navigation that EVERYONE sees (general menu)
  const baseLinks = [
    {
      title: 'Home',
      caption: 'Dashboard and overview',
      icon: 'home',
      route: 'home',
    },
    {
      title: 'Recipes',
      caption: 'Browse and manage recipes',
      icon: 'restaurant_menu',
      route: 'recipes',
    },
    {
      title: 'Meal Plans',
      caption: 'Plan your weekly meals',
      icon: 'calendar_today',
      route: 'meal-plans',
    },
    {
      title: 'Shopping Lists',
      caption: 'Generate grocery lists',
      icon: 'shopping_cart',
      route: 'shopping-lists',
    },
    {
      title: 'Meal Prep',
      caption: 'Plan batch cooking sessions',
      icon: 'kitchen',
      route: 'meal-prep',
    },
    {
      title: 'Categorieën',
      caption: 'Beheer categorieën en tags',
      icon: 'category',
      route: 'categories',
    },
    {
      title: 'Settings',
      caption: 'Account and family settings',
      icon: 'settings',
      route: 'settings',
    },
  ]

  return baseLinks
})

const leftDrawerOpen = ref(false)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

// Quick navigation functions
const quickCreateRecipe = () => {
  router.push({ name: 'recipe-create' })
  leftDrawerOpen.value = false
  $q.notify({
    type: 'info',
    message: 'Creating new recipe...',
    timeout: 1000
  })
}

const quickImportRecipe = () => {
  router.push({ name: 'recipe-import' })
  leftDrawerOpen.value = false
  $q.notify({
    type: 'info',
    message: 'Opening recipe import...',
    timeout: 1000
  })
}

const quickCreateMealPlan = () => {
  router.push({ name: 'meal-plan-create' })
  leftDrawerOpen.value = false
  $q.notify({
    type: 'info',
    message: 'Creating new meal plan...',
    timeout: 1000
  })
}

const secondaryLinks = computed(() => {
  const role = currentUserRole.value

  // Child users get no quick actions (simplified interface)
  if (role === 'child') {
    return []
  }

  // Viewer users get no creation actions
  if (role === 'viewer') {
    return []
  }

  // Full quick actions for members and admins
  return [
    {
      title: 'Create Recipe',
      caption: 'Add a new recipe manually',
      icon: 'add',
      action: quickCreateRecipe,
    },
    {
      title: 'Import Recipe',
      caption: 'Import from PDF',
      icon: 'upload_file',
      action: quickImportRecipe,
    },
    {
      title: 'Create Meal Plan',
      caption: 'Plan your weekly meals',
      icon: 'event_note',
      action: quickCreateMealPlan,
    },
    {
      title: 'Recipe App',
      caption: 'Open full recipe application',
      icon: 'open_in_new',
      action: () => router.push({ name: 'recipes' }),
    },
  ]
})

// Keyboard shortcuts
const handleKeyboardShortcuts = (event) => {
  // Only handle shortcuts when not in input fields
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
    return
  }

  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 'n':
        event.preventDefault()
        quickCreateRecipe()
        break
      case 'i':
        event.preventDefault()
        quickImportRecipe()
        break
      case 'm':
        event.preventDefault()
        quickCreateMealPlan()
        break
      case '/':
        event.preventDefault()
        toggleLeftDrawer()
        break
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyboardShortcuts)

  // Note: Auth initialization removed to prevent API calls
  // We're using simple token-based auth with localStorage
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyboardShortcuts)
})

// User menu actions
const handleProfile = () => {
  router.push({ name: 'settings' })
  $q.notify({
    type: 'info',
    message: 'Opening profile settings...',
    timeout: 1000
  })
}

const handleSettings = () => {
  router.push({ name: 'settings' })
}

const handleLogout = async () => {
  try {
    $q.loading.show({
      message: 'Logging out...'
    })

    // Use auth store logout method
    await authStore.logout()

    $q.notify({
      type: 'positive',
      message: 'Logged out successfully',
      timeout: 2000
    })

    router.push({ name: 'login' })
  } catch (error) {
    console.error('Logout error:', error)
    $q.notify({
      type: 'negative',
      message: 'Error logging out',
      timeout: 2000
    })
  } finally {
    $q.loading.hide()
  }
}
</script>

<style scoped>
.no-decoration {
  text-decoration: none;
}

.q-toolbar .q-btn {
  transition: background-color 0.2s;
}

.q-toolbar .q-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Mobile styles - keep hamburger menu visible */
@media (max-width: 768px) {
  .q-toolbar .q-btn:not([aria-label="Menu"]) {
    display: none;
  }

  /* Ensure hamburger menu is always visible */
  .q-toolbar .q-btn[aria-label="Menu"] {
    display: inline-flex !important;
  }
}
</style>
