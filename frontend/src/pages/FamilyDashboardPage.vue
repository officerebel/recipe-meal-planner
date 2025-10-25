<template>
  <q-page class="q-pa-lg">
    <!-- Family Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h4 text-primary">
          <q-icon name="family_restroom" class="q-mr-sm" />
          {{ familyStore.currentFamily?.name || 'Family Dashboard' }}
        </div>
        <div class="text-subtitle1 text-grey-7">
          Manage your family's meal planning together
        </div>
      </div>
      <q-btn
        v-if="isAdmin"
        color="primary"
        icon="settings"
        label="Family Settings"
        @click="$router.push({ name: 'settings', hash: '#family' })"
      />
    </div>

    <!-- Family Stats -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-3">
        <q-card class="text-center">
          <q-card-section>
            <q-icon name="people" size="2rem" color="primary" />
            <div class="text-h6 q-mt-sm">{{ familyStore.familyMembers.length }}</div>
            <div class="text-caption">Family Members</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-3">
        <q-card class="text-center">
          <q-card-section>
            <q-icon name="restaurant_menu" size="2rem" color="secondary" />
            <div class="text-h6 q-mt-sm">{{ familyRecipeCount }}</div>
            <div class="text-caption">Family Recipes</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-3">
        <q-card class="text-center">
          <q-card-section>
            <q-icon name="calendar_today" size="2rem" color="accent" />
            <div class="text-h6 q-mt-sm">{{ activeMealPlans }}</div>
            <div class="text-caption">Active Meal Plans</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-3">
        <q-card class="text-center">
          <q-card-section>
            <q-icon name="shopping_cart" size="2rem" color="positive" />
            <div class="text-h6 q-mt-sm">{{ activeShoppingLists }}</div>
            <div class="text-caption">Shopping Lists</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Family Members -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="people" class="q-mr-sm" />
          Family Members
        </div>

        <div class="row q-gutter-md">
          <div
            v-for="member in familyStore.familyMembers"
            :key="member.id"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card class="member-card" :class="getMemberCardClass(member)">
              <q-card-section class="text-center">
                <q-avatar
                  :color="getRoleColor(member.role)"
                  text-color="white"
                  size="64px"
                  class="q-mb-md"
                >
                  <q-icon :name="getRoleIcon(member.role)" size="32px" />
                </q-avatar>

                <div class="text-h6">{{ member.user.first_name }} {{ member.user.last_name }}</div>
                <div class="text-caption text-grey-6">{{ member.user.email }}</div>

                <q-chip
                  :color="getRoleColor(member.role)"
                  text-color="white"
                  :icon="getRoleIcon(member.role)"
                  class="q-mt-sm"
                  :clickable="isAdmin && !isCurrentUser(member)"
                  @click="isAdmin && !isCurrentUser(member) ? showRoleMenu(member) : null"
                >
                  {{ getRoleLabel(member.role) }}
                  <q-icon v-if="isAdmin && !isCurrentUser(member)" name="expand_more" size="xs" class="q-ml-xs" />
                </q-chip>

                <!-- Member Stats -->
                <div class="row q-gutter-sm q-mt-md">
                  <div class="col">
                    <div class="text-caption text-grey-6">Recipes</div>
                    <div class="text-body2">{{ getMemberRecipeCount(member) }}</div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-6">Meal Plans</div>
                    <div class="text-body2">{{ getMemberMealPlanCount(member) }}</div>
                  </div>
                </div>

                <!-- Role Management (Admin Only) -->
                <div v-if="isAdmin && !isCurrentUser(member)" class="q-mt-sm">
                  <q-select
                    :model-value="member.role"
                    :options="roleOptions"
                    dense
                    outlined
                    emit-value
                    map-options
                    style="min-width: 120px"
                    @update:model-value="(newRole) => changeRole(member, newRole)"
                  >
                    <template v-slot:prepend>
                      <q-icon name="admin_panel_settings" size="xs" />
                    </template>
                  </q-select>
                </div>

                <!-- Online Status -->
                <div class="q-mt-sm">
                  <q-chip
                    :color="isCurrentUser(member) ? 'positive' : 'grey-4'"
                    :text-color="isCurrentUser(member) ? 'white' : 'grey-8'"
                    size="sm"
                    :icon="isCurrentUser(member) ? 'online_prediction' : 'offline_bolt'"
                  >
                    {{ isCurrentUser(member) ? 'You' : 'Offline' }}
                  </q-chip>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Recent Family Activity -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="history" class="q-mr-sm" />
          Recent Family Activity
        </div>

        <q-timeline color="primary">
          <q-timeline-entry
            v-for="activity in recentActivity"
            :key="activity.id"
            :title="activity.title"
            :subtitle="activity.subtitle"
            :icon="activity.icon"
            :color="activity.color"
          >
            <div class="text-caption text-grey-6">{{ activity.time }}</div>
          </q-timeline-entry>
        </q-timeline>
      </q-card-section>
    </q-card>

    <!-- Family Preferences -->
    <q-card v-if="isAdmin">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="tune" class="q-mr-sm" />
          Family Preferences
        </div>

        <div class="row q-gutter-md">
          <div class="col-12 col-md-6">
            <q-input
              v-model="familySettings.default_servings"
              label="Default Servings"
              type="number"
              outlined
              min="1"
              max="20"
              @update:model-value="updateFamilySettings"
            />
          </div>
          <div class="col-12 col-md-6">
            <q-select
              v-model="familySettings.meal_planning_start_day"
              :options="dayOptions"
              label="Meal Planning Start Day"
              outlined
              emit-value
              map-options
              @update:model-value="updateFamilySettings"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useFamilyStore } from 'src/stores/families'
import { useRecipeStore } from 'src/stores/recipes'
import { useMealPlanningStore } from 'src/stores/mealPlanning'

// const router = useRouter() // Not used in this component
const $q = useQuasar()
const familyStore = useFamilyStore()
const recipeStore = useRecipeStore()
const mealPlanningStore = useMealPlanningStore()

// State
const familySettings = ref({
  default_servings: 4,
  meal_planning_start_day: 'monday'
})

const dayOptions = [
  { label: 'Monday', value: 'monday' },
  { label: 'Tuesday', value: 'tuesday' },
  { label: 'Wednesday', value: 'wednesday' },
  { label: 'Thursday', value: 'thursday' },
  { label: 'Friday', value: 'friday' },
  { label: 'Saturday', value: 'saturday' },
  { label: 'Sunday', value: 'sunday' }
]

const roleOptions = [
  { label: '👑 Admin', value: 'admin' },
  { label: '👤 Member', value: 'member' },
  { label: '👶 Child', value: 'child' },
  { label: '👁️ Viewer', value: 'viewer' }
]

// Computed
const isAdmin = computed(() => {
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  const currentMember = familyStore.familyMembers.find(m => m.user.id === currentUser.id)
  return currentMember?.role === 'admin'
})

const familyRecipeCount = computed(() => {
  return recipeStore.recipes.length
})

const activeMealPlans = computed(() => {
  return mealPlanningStore.mealPlans.length
})

const activeShoppingLists = computed(() => {
  const personalLists = mealPlanningStore.shoppingLists.personal || []
  const familyLists = mealPlanningStore.shoppingLists.family || []
  return personalLists.length + familyLists.length
})

const recentActivity = computed(() => {
  // Mock activity data - in real app, this would come from API
  return [
    {
      id: 1,
      title: 'New recipe added',
      subtitle: 'John added "Spaghetti Carbonara"',
      icon: 'restaurant_menu',
      color: 'primary',
      time: '2 hours ago'
    },
    {
      id: 2,
      title: 'Meal plan created',
      subtitle: 'Sarah created meal plan for next week',
      icon: 'calendar_today',
      color: 'secondary',
      time: '1 day ago'
    },
    {
      id: 3,
      title: 'Shopping list generated',
      subtitle: 'Family shopping list for this week',
      icon: 'shopping_cart',
      color: 'positive',
      time: '2 days ago'
    }
  ]
})

// Methods
const changeRole = async (member, newRole) => {
  if (member.role === newRole) return // No change needed

  try {
    // Show confirmation dialog for important role changes
    if (newRole === 'admin' || member.role === 'admin') {
      const confirmed = await new Promise((resolve) => {
        $q.dialog({
          title: 'Change Role',
          message: `Are you sure you want to change ${member.user.first_name}'s role from ${getRoleLabel(member.role)} to ${getRoleLabel(newRole)}?`,
          cancel: true,
          persistent: true
        }).onOk(() => resolve(true))
          .onCancel(() => resolve(false))
      })

      if (!confirmed) return
    }

    await familyStore.updateMemberRole(member.id, newRole)

    $q.notify({
      type: 'positive',
      message: `${member.user.first_name} is now ${getRoleLabel(newRole)}! 🎉`,
      timeout: 3000
    })

    // Refresh family data to show updated roles
    await familyStore.fetchFamilyMembers()
  } catch (error) {
    console.error('Error changing role:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to change role. Please try again.'
    })
  }
}

const showRoleMenu = (member) => {
  $q.dialog({
    title: `Change ${member.user.first_name}'s Role`,
    message: `Current role: ${getRoleLabel(member.role)}`,
    options: {
      type: 'radio',
      model: member.role,
      items: roleOptions
    },
    cancel: true,
    persistent: true
  }).onOk(newRole => {
    if (newRole !== member.role) {
      changeRole(member, newRole)
    }
  })
}

const getRoleColor = (role) => {
  const colors = {
    admin: 'red',
    member: 'blue',
    child: 'green',
    viewer: 'grey'
  }
  return colors[role] || 'grey'
}

const getRoleIcon = (role) => {
  const icons = {
    admin: 'admin_panel_settings',
    member: 'person',
    child: 'child_care',
    viewer: 'visibility'
  }
  return icons[role] || 'person'
}

const getRoleLabel = (role) => {
  const labels = {
    admin: 'Admin',
    member: 'Member',
    child: 'Child',
    viewer: 'Viewer'
  }
  return labels[role] || role
}

const getMemberCardClass = (member) => {
  if (isCurrentUser(member)) {
    return 'current-user-card'
  }
  return ''
}

const isCurrentUser = (member) => {
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  return member.user.id === currentUser.id
}

const getMemberRecipeCount = () => {
  // Mock data - in real app, filter recipes by user
  return Math.floor(Math.random() * 10) + 1
}

const getMemberMealPlanCount = () => {
  // Mock data - in real app, filter meal plans by user
  return Math.floor(Math.random() * 5) + 1
}

const updateFamilySettings = async () => {
  try {
    // Update family settings via API
    await familyStore.updateFamily(familyStore.currentFamily.id, familySettings.value)

    $q.notify({
      type: 'positive',
      message: 'Family settings updated'
    })
  } catch (error) {
    console.error('Error updating family settings:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update settings'
    })
  }
}

// Lifecycle
onMounted(async () => {
  await familyStore.initializeFamilyContext()
  await recipeStore.fetchRecipes()
  await mealPlanningStore.fetchMealPlans()
  await mealPlanningStore.fetchShoppingLists()

  // Load family settings
  if (familyStore.currentFamily) {
    familySettings.value = {
      default_servings: familyStore.currentFamily.default_servings || 4,
      meal_planning_start_day: familyStore.currentFamily.meal_planning_start_day || 'monday'
    }
  }
})
</script>

<style scoped>
.member-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.current-user-card {
  border: 2px solid #1976d2;
  background: linear-gradient(135deg, #f5f9ff 0%, #e3f2fd 100%);
}

.q-timeline {
  max-height: 300px;
  overflow-y: auto;
}
</style>
