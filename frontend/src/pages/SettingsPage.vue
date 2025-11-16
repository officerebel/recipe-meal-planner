<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- Header -->
      <div class="settings-header">
        <q-icon name="settings" size="64px" color="primary" />
        <h1 class="text-h4 text-primary q-mt-sm">Settings</h1>
        <p class="text-subtitle1 text-grey-7">Manage your account preferences</p>
      </div>

      <!-- Settings Form -->
      <q-card class="settings-card">
        <q-card-section class="q-pa-lg">
          <q-tabs v-model="activeTab" class="text-grey-7 q-mb-md">
            <q-tab name="profile" label="Profile" icon="person" />
            <q-tab name="family" label="Family" icon="family_restroom" />
            <q-tab name="security" label="Security" icon="security" />
            <q-tab name="preferences" label="Preferences" icon="tune" />
          </q-tabs>

          <q-tab-panels v-model="activeTab" animated>
            <!-- Profile Tab -->
            <q-tab-panel name="profile">
              <q-form @submit.prevent="updateProfile" class="q-gutter-md">
                <div class="text-h6 q-mb-md">Profile Information</div>

                <q-input
                  v-model="profile.firstName"
                  label="First Name"
                  outlined
                  :loading="loading"
                >
                  <template v-slot:prepend>
                    <q-icon name="person" />
                  </template>
                </q-input>

                <q-input
                  v-model="profile.lastName"
                  label="Last Name"
                  outlined
                  :loading="loading"
                >
                  <template v-slot:prepend>
                    <q-icon name="person_outline" />
                  </template>
                </q-input>

                <q-input
                  v-model="profile.email"
                  type="email"
                  label="Email Address"
                  outlined
                  readonly
                  :loading="loading"
                >
                  <template v-slot:prepend>
                    <q-icon name="email" />
                  </template>
                </q-input>

                <q-btn
                  type="submit"
                  color="primary"
                  label="Update Profile"
                  :loading="loading"
                />
              </q-form>
            </q-tab-panel>

            <!-- Family Tab -->
            <q-tab-panel name="family">
              <div class="text-h6 q-mb-md">Family Management</div>

              <!-- Family Info Card -->
              <q-card v-if="familyStore.currentFamily" flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle1 text-weight-medium q-mb-sm">
                    <q-icon name="family_restroom" class="q-mr-sm" />
                    {{ familyStore.currentFamily.name }}
                  </div>
                  <div class="text-body2 text-grey-7 q-mb-md">
                    {{ familyStore.currentFamily.description || 'No description' }}
                  </div>
                  <div class="row q-gutter-sm">
                    <q-chip color="primary" text-color="white" icon="people">
                      {{ familyStore.familyMembers.length }} members
                    </q-chip>
                    <q-chip color="secondary" text-color="white" icon="restaurant">
                      {{ familyStore.currentFamily.default_servings }} servings
                    </q-chip>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Debug Info (remove in production) -->
              <q-card v-if="$q.dev" flat bordered class="q-mb-md bg-grey-1">
                <q-card-section class="text-caption">
                  <div><strong>Debug Info:</strong></div>
                  <div>Current User Role: {{ familyStore.currentUserRole }}</div>
                  <div>Can Manage Members: {{ canManageMembers }}</div>
                  <div>Family Members Count: {{ familyStore.familyMembers.length }}</div>
                  <div>Current Family: {{ familyStore.currentFamily?.name || 'None' }}</div>
                </q-card-section>
              </q-card>

              <!-- Family Members -->
              <div v-if="familyStore.familyMembers.length > 0" class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Family Members</div>
                <q-list separator>
                  <q-item
                    v-for="member in familyStore.familyMembers"
                    :key="member.id"
                    class="q-pa-sm"
                  >
                    <q-item-section avatar>
                      <q-avatar :color="getRoleColor(member.role)" text-color="white" size="sm">
                        <q-icon :name="getRoleIcon(member.role)" />
                      </q-avatar>
                    </q-item-section>

                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        {{ member.user.first_name }} {{ member.user.last_name }}
                      </q-item-label>
                      <q-item-label caption>
                        {{ getRoleLabel(member.role) }}
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <!-- Debug info for this member -->
                      <div v-if="$q.dev" class="text-caption text-grey-6 q-mb-xs">
                        canManage: {{ canManageMembers }}, isCurrentUser: {{ isCurrentUser(member) }}
                      </div>

                      <!-- Show role management for admins, but not for current user -->
                      <div v-if="canManageMembers && !isCurrentUser(member)">
                        <!-- Quick Role Selector for Mobile -->
                        <div v-if="$q.screen.xs" class="column q-gutter-xs">
                          <q-select
                            :model-value="member.role"
                            :options="roleOptions"
                            dense
                            outlined
                            emit-value
                            map-options
                            style="min-width: 100px"
                            @update:model-value="(newRole) => quickUpdateRole(member, newRole)"
                          />
                          <div class="row q-gutter-xs">
                            <q-btn
                              flat
                              round
                              icon="person"
                              size="xs"
                              color="secondary"
                              @click="editMemberProfile(member)"
                            >
                              <q-tooltip>Edit profile</q-tooltip>
                            </q-btn>
                            <q-btn
                              flat
                              round
                              icon="delete"
                              size="xs"
                              color="negative"
                              @click="removeMember(member)"
                            >
                              <q-tooltip>Remove member</q-tooltip>
                            </q-btn>
                          </div>
                        </div>

                        <!-- Desktop Buttons -->
                        <div v-else class="row q-gutter-xs">
                          <q-btn
                            flat
                            round
                            icon="person"
                            size="sm"
                            color="secondary"
                            @click="editMemberProfile(member)"
                          >
                            <q-tooltip>Edit profile</q-tooltip>
                          </q-btn>
                          <q-btn
                            flat
                            round
                            icon="admin_panel_settings"
                            size="sm"
                            color="primary"
                            @click="editMemberRole(member)"
                          >
                            <q-tooltip>Change role</q-tooltip>
                          </q-btn>
                          <q-btn
                            flat
                            round
                            icon="lock_reset"
                            size="sm"
                            color="orange"
                            @click="resetMemberPassword(member)"
                          >
                            <q-tooltip>Reset password</q-tooltip>
                          </q-btn>
                          <q-btn
                            flat
                            round
                            icon="delete"
                            size="sm"
                            color="negative"
                            @click="removeMember(member)"
                          >
                            <q-tooltip>Remove member</q-tooltip>
                          </q-btn>
                        </div>
                      </div>

                      <!-- Show current user indicator -->
                      <div v-else-if="isCurrentUser(member)" class="text-caption text-grey-6">
                        (You)
                      </div>

                      <!-- Show no permissions message for non-admins -->
                      <div v-else-if="!canManageMembers" class="text-caption text-grey-6">
                        No permissions
                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- Family Actions -->
              <div class="row q-gutter-sm">
                <q-btn
                  color="primary"
                  icon="person_add"
                  label="Add Member"
                  @click="showAddMemberDialog = true"
                  :disable="!familyStore.currentFamily"
                />
                <q-btn
                  v-if="!familyStore.currentFamily"
                  color="secondary"
                  icon="add"
                  label="Create Family"
                  @click="showCreateFamilyDialog = true"
                />
              </div>

              <!-- No Family Message -->
              <q-card v-if="!familyStore.currentFamily" flat bordered class="text-center q-pa-lg">
                <q-icon name="family_restroom" size="48px" color="grey-5" />
                <div class="text-h6 q-mt-md text-grey-6">No Family</div>
                <div class="text-body2 text-grey-7 q-mb-md">
                  Create a family to share recipes and meal plans
                </div>
              </q-card>
            </q-tab-panel>

            <!-- Security Tab -->
            <q-tab-panel name="security">
              <q-form @submit.prevent="changePassword" class="q-gutter-md">
                <div class="text-h6 q-mb-md">Change Password</div>

                <q-input
                  v-model="security.currentPassword"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  label="Current Password"
                  outlined
                >
                  <template v-slot:prepend>
                    <q-icon name="lock" />
                  </template>
                  <template v-slot:append>
                    <q-icon
                      :name="showCurrentPassword ? 'visibility_off' : 'visibility'"
                      class="cursor-pointer"
                      @click="showCurrentPassword = !showCurrentPassword"
                    />
                  </template>
                </q-input>

                <q-input
                  v-model="security.newPassword"
                  :type="showNewPassword ? 'text' : 'password'"
                  label="New Password"
                  outlined
                >
                  <template v-slot:prepend>
                    <q-icon name="lock_outline" />
                  </template>
                  <template v-slot:append>
                    <q-icon
                      :name="showNewPassword ? 'visibility_off' : 'visibility'"
                      class="cursor-pointer"
                      @click="showNewPassword = !showNewPassword"
                    />
                  </template>
                </q-input>

                <q-input
                  v-model="security.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  label="Confirm New Password"
                  outlined
                >
                  <template v-slot:prepend>
                    <q-icon name="lock_reset" />
                  </template>
                  <template v-slot:append>
                    <q-icon
                      :name="showConfirmPassword ? 'visibility_off' : 'visibility'"
                      class="cursor-pointer"
                      @click="showConfirmPassword = !showConfirmPassword"
                    />
                  </template>
                </q-input>

                <q-btn
                  type="submit"
                  color="primary"
                  label="Change Password"
                  :loading="loading"
                />
              </q-form>
            </q-tab-panel>

            <!-- Preferences Tab -->
            <q-tab-panel name="preferences">
              <div class="text-h6 q-mb-md">App Preferences</div>

              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label>Dark Mode</q-item-label>
                    <q-item-label caption>Use dark theme</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-toggle v-model="preferences.darkMode" color="primary" />
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Email Notifications</q-item-label>
                    <q-item-label caption>Receive email updates</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-toggle v-model="preferences.emailNotifications" color="primary" />
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Auto-save Recipes</q-item-label>
                    <q-item-label caption>Automatically save recipe drafts</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-toggle v-model="preferences.autoSave" color="primary" />
                  </q-item-section>
                </q-item>
              </q-list>

              <q-btn
                color="primary"
                label="Save Preferences"
                @click="savePreferences"
                :loading="loading"
                class="q-mt-md"
              />
            </q-tab-panel>
          </q-tab-panels>

          <!-- Success Message -->
          <q-banner v-if="success" class="bg-positive text-white q-mt-md">
            <template v-slot:avatar>
              <q-icon name="check_circle" />
            </template>
            {{ success }}
          </q-banner>

          <!-- Error Message -->
          <q-banner v-if="error" class="bg-negative text-white q-mt-md">
            <template v-slot:avatar>
              <q-icon name="error" />
            </template>
            {{ error }}
          </q-banner>

          <!-- Back Button -->
          <div class="text-center q-mt-lg">
            <q-btn
              flat
              color="primary"
              label="Back to App"
              @click="goBack"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Family Management Dialogs -->
    <!-- Create Family Dialog -->
    <q-dialog v-model="showCreateFamilyDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Create New Family</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-input
            v-model="familyName"
            label="Family Name"
            outlined
            autofocus
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="showCreateFamilyDialog = false" />
          <q-btn color="primary" label="Create" @click="createFamily" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add Member Dialog -->
    <q-dialog v-model="showAddMemberDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Create Family Member</div>
        </q-card-section>
        <q-card-section class="q-pt-none q-gutter-md">
          <q-input
            v-model="memberFirstName"
            label="First Name"
            outlined
          />
          <q-input
            v-model="memberLastName"
            label="Last Name"
            outlined
          />
          <q-input
            v-model="memberEmail"
            label="Email Address"
            type="email"
            outlined
          />
          <q-input
            v-model="memberUsername"
            label="Username"
            outlined
          />
          <q-input
            v-model="memberPassword"
            label="Password"
            type="password"
            outlined
          />
          <q-select
            v-model="memberRole"
            :options="roleOptions"
            label="Role"
            outlined
            emit-value
            map-options
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelAddMember" />
          <q-btn color="primary" label="Create User" @click="createMember" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Role Dialog -->
    <q-dialog v-model="showEditRoleDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Change Member Role</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-select
            v-model="newRole"
            :options="roleOptions"
            label="New Role"
            outlined
            emit-value
            map-options
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="showEditRoleDialog = false" />
          <q-btn color="primary" label="Save" @click="saveRoleChange" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Profile Dialog -->
    <q-dialog v-model="showEditProfileDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Edit Member Profile</div>
        </q-card-section>
        <q-card-section class="q-pt-none q-gutter-md">
          <q-input
            v-model="editProfileForm.firstName"
            label="First Name"
            outlined
          />
          <q-input
            v-model="editProfileForm.lastName"
            label="Last Name"
            outlined
          />
          <q-input
            v-model="editProfileForm.email"
            label="Email Address"
            type="email"
            outlined
          />
          <q-input
            v-model="editProfileForm.username"
            label="Username"
            outlined
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelEditProfile" />
          <q-btn color="primary" label="Save Changes" @click="saveProfileChanges" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Reset Password Dialog -->
    <q-dialog v-model="showResetPasswordDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Reset Password</div>
          <div class="text-subtitle2 q-mt-sm">
            Reset password for {{ editingMember?.user?.first_name }} {{ editingMember?.user?.last_name }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form @submit.prevent="confirmPasswordReset" class="q-gutter-md">
            <q-input
              v-model="newPasswordForMember"
              label="New Password"
              type="password"
              outlined
              :rules="[
                val => !!val || 'Password is required',
                val => val.length >= 6 || 'Password must be at least 6 characters'
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="lock" />
              </template>
            </q-input>

            <q-input
              v-model="confirmPasswordForMember"
              label="Confirm New Password"
              type="password"
              outlined
              :rules="[
                val => !!val || 'Please confirm the password',
                val => val === newPasswordForMember || 'Passwords do not match'
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="lock_outline" />
              </template>
            </q-input>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelPasswordReset" />
          <q-btn
            color="primary"
            label="Reset Password"
            @click="confirmPasswordReset"
            :loading="loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { useFamilyStore } from 'src/stores/families'
import { api } from 'boot/axios'

const router = useRouter()
const $q = useQuasar()
const authStore = useAuthStore()
const familyStore = useFamilyStore()

// State
const activeTab = ref('profile')
const loading = ref(false)
const error = ref('')
const success = ref('')

// Form data
const profile = ref({
  firstName: '',
  lastName: '',
  email: ''
})

const security = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const preferences = ref({
  darkMode: false,
  emailNotifications: true,
  autoSave: true
})

// Password visibility
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Family management state
const showCreateFamilyDialog = ref(false)
const showAddMemberDialog = ref(false)
const showEditRoleDialog = ref(false)
const showEditProfileDialog = ref(false)
const showResetPasswordDialog = ref(false)
const editingMember = ref(null)
const newPasswordForMember = ref('')
const confirmPasswordForMember = ref('')
const editProfileForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  username: ''
})
const familyName = ref('')
const memberFirstName = ref('')
const memberLastName = ref('')
const memberEmail = ref('')
const memberUsername = ref('')
const memberPassword = ref('')
const memberRole = ref('member')
const newRole = ref('member')

const roleOptions = [
  { label: 'Admin', value: 'admin' },
  { label: 'Member', value: 'member' },
  { label: 'Child', value: 'child' },
  { label: 'Viewer', value: 'viewer' }
]

// Simple notification function
const showMessage = (message) => {
  console.log(message)
  setTimeout(() => alert(message), 100)
}

// Methods
const loadUserProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      router.push('/login')
      return
    }

    // Fetch user profile from API
    const response = await api.get('auth/user/')
    const userData = response.data

    // Update profile form with real data
    profile.value = {
      firstName: userData.first_name || '',
      lastName: userData.last_name || '',
      email: userData.email || ''
    }

    console.log('User profile loaded:', userData)
  } catch (error) {
    console.error('Error loading user profile:', error)
    error.value = 'Failed to load user profile'

    // If unauthorized, redirect to login
    if (error.response?.status === 401) {
      await authStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    // Update profile via API
    const response = await api.patch('auth/user/', {
      first_name: profile.value.firstName,
      last_name: profile.value.lastName,
      email: profile.value.email
    })

    // Update auth store with new user data
    authStore.user = response.data

    success.value = 'Profile updated successfully!'
    showMessage('Profile updated successfully!')
  } catch (error) {
    console.error('Error updating profile:', error)
    error.value = error.response?.data?.message || 'Failed to update profile'
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  if (security.value.newPassword !== security.value.confirmPassword) {
    error.value = 'New passwords do not match'
    return
  }

  if (security.value.newPassword.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true
  error.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    showMessage('Password changed successfully!')

    // Clear form
    security.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch {
    error.value = 'Failed to change password'
  } finally {
    loading.value = false
  }
}

const savePreferences = async () => {
  loading.value = true
  error.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Save to localStorage
    localStorage.setItem('user_preferences', JSON.stringify(preferences.value))

    showMessage('Preferences saved successfully!')
  } catch {
    error.value = 'Failed to save preferences'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.go(-1)
}

// Removed duplicate canManageMembers - using the one below

// Family management methods
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

const isCurrentUser = (member) => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return member.user?.id === user.id
}

const editMemberRole = (member) => {
  editingMember.value = member
  newRole.value = member.role
  showEditRoleDialog.value = true
}

const editMemberProfile = (member) => {
  editingMember.value = member
  editProfileForm.value = {
    firstName: member.user.first_name || '',
    lastName: member.user.last_name || '',
    email: member.user.email || '',
    username: member.user.username || ''
  }
  showEditProfileDialog.value = true
}

const resetMemberPassword = (member) => {
  editingMember.value = member
  newPasswordForMember.value = ''
  confirmPasswordForMember.value = ''
  showResetPasswordDialog.value = true
}

const cancelEditProfile = () => {
  showEditProfileDialog.value = false
  editingMember.value = null
  editProfileForm.value = {
    firstName: '',
    lastName: '',
    email: '',
    username: ''
  }
}

const cancelPasswordReset = () => {
  showResetPasswordDialog.value = false
  editingMember.value = null
  newPasswordForMember.value = ''
  confirmPasswordForMember.value = ''
}

const confirmPasswordReset = async () => {
  if (!editingMember.value) return

  if (newPasswordForMember.value !== confirmPasswordForMember.value) {
    $q.notify({
      type: 'negative',
      message: 'Passwords do not match'
    })
    return
  }

  if (newPasswordForMember.value.length < 6) {
    $q.notify({
      type: 'negative',
      message: 'Password must be at least 6 characters'
    })
    return
  }

  loading.value = true
  try {
    // Call API to reset member password
    // First get the family ID from the member
    const familyId = editingMember.value.family
    await api.patch(`families/${familyId}/reset-member-password/`, {
      member_id: editingMember.value.id,
      new_password: newPasswordForMember.value
    })

    $q.notify({
      type: 'positive',
      message: `Password reset successfully for ${editingMember.value.user.first_name}`
    })

    showResetPasswordDialog.value = false
    editingMember.value = null
    newPasswordForMember.value = ''
    confirmPasswordForMember.value = ''
  } catch (error) {
    console.error('Error resetting password:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to reset password. Please try again.'
    })
  } finally {
    loading.value = false
  }
}

const saveProfileChanges = async () => {
  if (!editingMember.value) return

  loading.value = true
  try {
    // Update member profile via family store
    await familyStore.updateMember(familyStore.currentFamily.id, {
      member_id: editingMember.value.id,
      first_name: editProfileForm.value.firstName,
      last_name: editProfileForm.value.lastName,
      email: editProfileForm.value.email,
      username: editProfileForm.value.username
    })

    cancelEditProfile()

    $q.notify({
      type: 'positive',
      message: 'Profile updated successfully!'
    })

    // Refresh family members to show updated info
    await familyStore.fetchFamilyMembers()

    console.log('Profile updated, family members:', familyStore.familyMembers)
  } catch (error) {
    console.error('Error updating profile:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update profile'
    })
  } finally {
    loading.value = false
  }
}

const removeMember = async (member) => {
  try {
    const confirmed = await new Promise((resolve) => {
      $q.dialog({
        title: 'Remove Member',
        message: `Are you sure you want to remove ${member.user.first_name} ${member.user.last_name}?`,
        cancel: true,
        persistent: true
      }).onOk(() => resolve(true))
        .onCancel(() => resolve(false))
    })

    if (!confirmed) return

    await familyStore.removeMember(member.id)
    $q.notify({
      type: 'positive',
      message: 'Member removed successfully'
    })
  } catch (error) {
    console.error('Error removing member:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to remove member'
    })
  }
}

const createFamily = async () => {
  if (!familyName.value.trim()) {
    $q.notify({
      type: 'negative',
      message: 'Please enter a family name'
    })
    return
  }

  loading.value = true
  try {
    await familyStore.createFamily({
      name: familyName.value.trim(),
      description: '',
      default_servings: 4
    })

    showCreateFamilyDialog.value = false
    familyName.value = ''

    $q.notify({
      type: 'positive',
      message: 'Family created successfully!'
    })
  } catch (error) {
    console.error('Error creating family:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to create family'
    })
  } finally {
    loading.value = false
  }
}

const createMember = async () => {
  // Validate required fields
  if (!memberFirstName.value.trim() || !memberLastName.value.trim() ||
      !memberEmail.value.trim() || !memberUsername.value.trim() ||
      !memberPassword.value.trim()) {
    $q.notify({
      type: 'negative',
      message: 'Please fill in all fields'
    })
    return
  }

  loading.value = true
  try {
    // Create the member using the family store
    await familyStore.createMember({
      first_name: memberFirstName.value.trim(),
      last_name: memberLastName.value.trim(),
      email: memberEmail.value.trim(),
      username: memberUsername.value.trim(),
      password: memberPassword.value,
      role: memberRole.value
    })

    // Clear form and close dialog
    cancelAddMember()

    $q.notify({
      type: 'positive',
      message: 'Family member created successfully!'
    })
  } catch (error) {
    console.error('Error creating member:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.error || 'Failed to create family member'
    })
  } finally {
    loading.value = false
  }
}

const cancelAddMember = () => {
  showAddMemberDialog.value = false
  memberFirstName.value = ''
  memberLastName.value = ''
  memberEmail.value = ''
  memberUsername.value = ''
  memberPassword.value = ''
  memberRole.value = 'member'
}

const saveRoleChange = async () => {
  if (!editingMember.value || !newRole.value) {
    return
  }

  loading.value = true
  try {
    await familyStore.updateMemberRole(editingMember.value.id, newRole.value)

    showEditRoleDialog.value = false
    editingMember.value = null

    $q.notify({
      type: 'positive',
      message: 'Role updated successfully!'
    })
  } catch (error) {
    console.error('Error updating role:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update role'
    })
  } finally {
    loading.value = false
  }
}

// Family management computed properties
const canManageMembers = computed(() => {
  // Use the store getter for current user role
  const role = familyStore.currentUserRole
  let canManage = role === 'admin'

  // Fallback: check if any family member with current user ID has admin role
  if (!canManage && familyStore.familyMembers.length > 0) {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    const adminMember = familyStore.familyMembers.find(m =>
      m.user?.id === currentUser.id && m.role === 'admin'
    )
    canManage = !!adminMember
  }

  // Temporary override: if we have family members and one is admin, allow management
  if (!canManage && familyStore.familyMembers.length > 0) {
    const hasAdmin = familyStore.familyMembers.some(m => m.role === 'admin')
    if (hasAdmin) {
      canManage = true // Force enable for testing
    }
  }

  console.log('Settings: canManageMembers check:', {
    currentUserRole: role,
    canManage,
    currentFamily: familyStore.currentFamily,
    familyMembers: familyStore.familyMembers
  })

  return canManage
})

// Removed duplicate updateMemberRole - using saveRoleChange instead

// Quick role update for mobile (no dialog)
const quickUpdateRole = async (member, newRole) => {
  if (member.role === newRole) return // No change

  try {
    await familyStore.updateMemberRole(member.id, newRole)

    $q.notify({
      type: 'positive',
      message: `${member.user.first_name} is now ${getRoleLabel(newRole)}`,
      timeout: 2000
    })

    await familyStore.fetchFamilyMembers()
  } catch (error) {
    console.error('Error updating member role:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update role'
    })
  }
}

// Load user profile and family data on component mount
onMounted(async () => {
  console.log('Settings: Component mounted, loading data...')

  await loadUserProfile()

  console.log('Settings: Initializing family context...')
  await familyStore.initializeFamilyContext()

  console.log('Settings: Family context initialized:', {
    currentFamily: familyStore.currentFamily,
    familyMembers: familyStore.familyMembers,
    currentUserRole: familyStore.currentUserRole
  })
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.settings-container {
  width: 100%;
  max-width: 600px;
}

.settings-header {
  text-align: center;
  margin-bottom: 2rem;
}

.settings-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cursor-pointer {
  cursor: pointer;
}

h1 {
  margin: 0.5rem 0;
}

p {
  margin: 0;
}
</style>
