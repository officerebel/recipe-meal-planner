<template>
  <q-page class="q-pa-lg">
    <!-- Simple Test Header -->
    <div class="text-h4 q-mb-lg">🏠 Familie Beheer</div>

    <!-- Test Content -->
    <div class="q-mb-md">
      <p>✅ This page is loading correctly!</p>
      <p>📍 Route: /family-management</p>
      <p>🔧 Component: FamilyManagementPage.vue</p>
    </div>

    <!-- Action Buttons -->
    <div class="q-gutter-sm q-mb-lg">
      <q-btn
        color="primary"
        icon="add"
        label="Nieuwe Familie"
        @click="showCreateFamilyDialog = true"
      />
      <q-btn
        color="secondary"
        icon="person_add"
        label="Familie Lid Toevoegen"
        @click="showInviteDialog = true"
        :disable="!familyStore.currentFamily"
      />
      <q-btn
        v-if="familyStore.currentFamily"
        color="accent"
        icon="refresh"
        label="Vernieuwen"
        @click="refreshFamilyData"
        :loading="familyStore.loading"
      />
    </div>

    <!-- Debug Info -->
    <div
      class="q-mb-md q-pa-sm bg-grey-2 rounded-borders"
      style="font-family: monospace; font-size: 12px"
    >
      <div><strong>🔍 Debug Info:</strong></div>
      <div>Page Status: LOADED</div>
      <div>Component: FamilyManagementPage</div>
      <div>Route: {{ $route.path }}</div>
      <div>Time: {{ new Date().toLocaleTimeString() }}</div>
    </div>

    <!-- Current Family Info -->
    <q-card v-if="familyStore.currentFamily" class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="family_restroom" class="q-mr-sm" />
          Huidige Familie: {{ familyStore.currentFamily.name }}
        </div>

        <div class="text-body2 text-grey-7 q-mb-md">
          {{ familyStore.currentFamily.description || 'Geen beschrijving' }}
        </div>

        <div class="q-mb-md">
          <q-chip
            color="primary"
            text-color="white"
            icon="people"
          >
            {{ familyStore.familyMembers.length }} leden
          </q-chip>

          <q-chip
            color="secondary"
            text-color="white"
            icon="restaurant"
          >
            {{ familyStore.currentFamily.default_servings }} standaard porties
          </q-chip>
        </div>

        <!-- Family Members List with Role Management -->
        <div v-if="familyStore.familyMembers.length > 0">
          <div class="text-subtitle2 q-mb-sm">Familie Leden:</div>
          <q-list separator>
            <q-item
              v-for="member in familyStore.familyMembers"
              :key="member.id"
              class="q-pa-md"
            >
              <q-item-section avatar>
                <q-avatar :color="getRoleColor(member.role)" text-color="white">
                  <q-icon :name="getRoleIcon(member.role)" />
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label class="text-h6">
                  {{ member.user.first_name }} {{ member.user.last_name }}
                </q-item-label>
                <q-item-label caption>
                  {{ member.user.email }}
                </q-item-label>
                <q-item-label caption class="text-grey-6">
                  Lid sinds {{ formatDate(member.joined_at) }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="column items-end q-gutter-sm">
                  <!-- Role Badge -->
                  <q-chip
                    :color="getRoleColor(member.role)"
                    text-color="white"
                    :icon="getRoleIcon(member.role)"
                    size="sm"
                  >
                    {{ getRoleLabel(member.role) }}
                  </q-chip>

                  <!-- Admin Actions -->
                  <div v-if="canManageMembers && !isCurrentUser(member)" class="row q-gutter-xs">
                    <q-btn
                      flat
                      round
                      icon="edit"
                      size="sm"
                      color="primary"
                      @click="editMemberRole(member)"
                    >
                      <q-tooltip>Rol wijzigen</q-tooltip>
                    </q-btn>
                    <q-btn
                      flat
                      round
                      icon="delete"
                      size="sm"
                      color="negative"
                      @click="removeMember(member)"
                    >
                      <q-tooltip>Lid verwijderen</q-tooltip>
                    </q-btn>
                  </div>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
      </q-card-section>
    </q-card>

    <!-- No Family Message -->
    <q-card v-else class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="info" class="q-mr-sm" />
          Geen Familie
        </div>
        <div class="text-body2 text-grey-7 q-mb-md">
          Je bent nog geen lid van een familie. Maak een nieuwe familie aan of wacht op een uitnodiging.
        </div>
        <q-btn
          color="primary"
          icon="add"
          label="Eerste Familie Maken"
          @click="showCreateFamilyDialog = true"
        />
      </q-card-section>
    </q-card>

    <!-- Role Management Tutorial for Admins -->
    <q-card v-if="canManageMembers" class="q-mb-lg bg-blue-1">
      <q-card-section>
        <div class="text-h6 text-blue-8">
          <q-icon name="admin_panel_settings" class="q-mr-sm" />
          👑 Beheerder Functies
        </div>
        <div class="text-body2 q-mt-md">
          <strong>Als beheerder kun je:</strong>
        </div>
        <ul class="q-mt-sm q-mb-md">
          <li>Rollen van familieleden wijzigen (klik op het ✏️ icoon)</li>
          <li>Familieleden verwijderen (klik op het 🗑️ icoon)</li>
          <li>Nieuwe familieleden aanmaken</li>
          <li>Familie-instellingen beheren</li>
        </ul>
        <q-banner class="bg-orange-1 text-orange-8">
          <template v-slot:avatar>
            <q-icon name="info" />
          </template>
          <strong>Tip:</strong> Klik op de ✏️ knop naast een familielid om hun rol te wijzigen van Lid naar Kind, Kijker of Beheerder.
        </q-banner>
      </q-card-section>
    </q-card>

    <!-- Features Overview -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6">🎯 Familie Functies</div>
        <div class="row q-gutter-md q-mt-md">
          <div class="col-12 col-md-6">
            <q-list>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="restaurant_menu" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Gedeelde Recepten</q-item-label>
                  <q-item-label caption>Deel en beheer recepten samen</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="calendar_today" color="secondary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Maaltijd Planning</q-item-label>
                  <q-item-label caption>Plan maaltijden voor de hele familie</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <div class="col-12 col-md-6">
            <q-list>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="shopping_cart" color="accent" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Boodschappenlijsten</q-item-label>
                  <q-item-label caption>Automatische lijsten op basis van maaltijden</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="child_care" color="positive" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Kinderaccounts</q-item-label>
                  <q-item-label caption>Veilige accounts voor kinderen</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Create Family Dialog -->
    <q-dialog v-model="showCreateFamilyDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Nieuwe Familie Maken</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="createFamily" class="q-gutter-md">
            <q-input
              v-model="familyForm.name"
              label="Familie Naam *"
              outlined
              :rules="[(val) => !!val || 'Naam is verplicht']"
            />

            <q-input
              v-model="familyForm.description"
              label="Beschrijving"
              outlined
              type="textarea"
              rows="3"
            />

            <q-input
              v-model.number="familyForm.default_servings"
              label="Standaard Aantal Porties"
              outlined
              type="number"
              min="1"
              max="20"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Annuleren" @click="cancelCreateFamily" />
          <q-btn color="primary" label="Maken" @click="createFamily" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Create Family Member Dialog -->
    <q-dialog v-model="showInviteDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Familie Lid Aanmaken</div>
          <div class="text-caption text-grey-7">
            Maak een nieuw account aan voor een familielid
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="createFamilyMember" class="q-gutter-md">
            <q-input
              v-model="inviteForm.email"
              label="E-mail Adres *"
              outlined
              type="email"
              :rules="[(val) => !!val || 'E-mail is verplicht']"
            />

            <q-input
              v-model="inviteForm.first_name"
              label="Voornaam *"
              outlined
              :rules="[(val) => !!val || 'Voornaam is verplicht']"
            />

            <q-input
              v-model="inviteForm.last_name"
              label="Achternaam"
              outlined
            />

            <q-input
              v-model="inviteForm.password"
              label="Wachtwoord *"
              outlined
              type="password"
              :rules="[(val) => !!val || 'Wachtwoord is verplicht', (val) => val.length >= 6 || 'Minimaal 6 karakters']"
              hint="Minimaal 6 karakters"
            />

            <q-select
              v-model="inviteForm.role"
              :options="roleOptions"
              label="Rol"
              outlined
              emit-value
              map-options
            />

            <!-- Age field for child users -->
            <q-input
              v-if="inviteForm.role === 'child'"
              v-model.number="inviteForm.age"
              label="Leeftijd"
              outlined
              type="number"
              min="1"
              max="18"
              hint="Leeftijd van het kind"
            />

            <!-- Parental controls for child users -->
            <q-checkbox
              v-if="inviteForm.role === 'child'"
              v-model="inviteForm.parental_controls"
              label="Ouderlijk toezicht inschakelen"
              class="q-mt-md"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Annuleren" @click="cancelInvite" />
          <q-btn color="primary" label="Aanmaken" @click="createFamilyMember" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Success Dialog with Login Credentials -->
    <q-dialog v-model="showCredentialsDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6 text-positive">
            <q-icon name="check_circle" class="q-mr-sm" />
            Familie Lid Aangemaakt!
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="q-mb-md">
            <strong>{{ newMemberCredentials.name }}</strong> is succesvol toegevoegd aan de familie.
          </div>

          <q-separator class="q-my-md" />

          <div class="text-h6 q-mb-md">Inloggegevens:</div>

          <div class="q-pa-md bg-grey-1 rounded-borders">
            <div class="q-mb-sm">
              <strong>E-mail:</strong> {{ newMemberCredentials.email }}
            </div>
            <div class="q-mb-sm">
              <strong>Wachtwoord:</strong> {{ newMemberCredentials.password }}
            </div>
            <div class="q-mb-sm">
              <strong>Rol:</strong> {{ newMemberCredentials.role }}
            </div>
          </div>

          <div class="text-caption text-grey-7 q-mt-md">
            💡 Deel deze gegevens met het familielid zodat ze kunnen inloggen op de app.
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn color="primary" label="Begrepen" @click="closeCredentialsDialog" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Member Role Dialog -->
    <q-dialog v-model="showEditRoleDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Rol Wijzigen</div>
          <div class="text-caption text-grey-7">
            Wijzig de rol van {{ editingMember?.user?.first_name }} {{ editingMember?.user?.last_name }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveRoleChange" class="q-gutter-md">
            <q-select
              v-model="editRoleForm.role"
              :options="roleOptions"
              label="Nieuwe Rol *"
              outlined
              emit-value
              map-options
              :rules="[(val) => !!val || 'Rol is verplicht']"
            />

            <div class="text-caption text-grey-7">
              <strong>Huidige rol:</strong> {{ getRoleLabel(editingMember?.role) }}
            </div>

            <!-- Role permissions info -->
            <q-card flat bordered class="q-pa-sm bg-grey-1">
              <div class="text-caption text-grey-8">
                <strong>Rechten voor {{ getRoleLabel(editRoleForm.role) }}:</strong>
              </div>
              <ul class="text-caption text-grey-7 q-ma-none q-pl-md">
                <li v-for="permission in getRolePermissions(editRoleForm.role)" :key="permission">
                  {{ permission }}
                </li>
              </ul>
            </q-card>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Annuleren" @click="cancelEditRole" />
          <q-btn color="primary" label="Opslaan" @click="saveRoleChange" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useFamilyStore } from 'src/stores/families'

const $q = useQuasar()
const familyStore = useFamilyStore()

// State
const loading = ref(false)
const showCreateFamilyDialog = ref(false)
const showInviteDialog = ref(false)
const showCredentialsDialog = ref(false)
const showEditRoleDialog = ref(false)
const newMemberCredentials = ref({})
const editingMember = ref(null)

// Forms
const familyForm = ref({
  name: '',
  description: '',
  default_servings: 4,
})

const inviteForm = ref({
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  role: 'member',
  age: null,
  parental_controls: true,
})

const editRoleForm = ref({
  role: 'member'
})

// Options
const roleOptions = [
  { label: 'Lid', value: 'member' },
  { label: 'Kind', value: 'child' },
  { label: 'Kijker', value: 'viewer' },
  { label: 'Beheerder', value: 'admin' },
]

// Computed
const canManageMembers = computed(() => {
  if (!familyStore.currentFamily) return false
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  const currentMember = familyStore.familyMembers.find(m => m.user.id === currentUser.id)
  return currentMember?.role === 'admin'
})

// Methods
const createFamily = async () => {
  if (!familyForm.value.name) {
    $q.notify({
      type: 'negative',
      message: 'Familie naam is verplicht',
    })
    return
  }

  loading.value = true

  try {
    // Use families store to create family
    await familyStore.createFamily(familyForm.value)

    $q.notify({
      type: 'positive',
      message: `Familie "${familyForm.value.name}" succesvol aangemaakt!`,
    })

    cancelCreateFamily()
  } catch (error) {
    console.error('Error creating family:', error)
    $q.notify({
      type: 'negative',
      message: familyStore.error || 'Fout bij aanmaken familie',
    })
  } finally {
    loading.value = false
  }
}

const cancelCreateFamily = () => {
  showCreateFamilyDialog.value = false
  familyForm.value = {
    name: '',
    description: '',
    default_servings: 4,
  }
}

const createFamilyMember = async () => {
  if (!inviteForm.value.email || !inviteForm.value.first_name || !inviteForm.value.password) {
    $q.notify({
      type: 'negative',
      message: 'Vul alle verplichte velden in',
    })
    return
  }

  loading.value = true

  try {
    console.log('🔧 Creating family member with data:', inviteForm.value)

    // Use families store to create member
    const result = await familyStore.createMember(inviteForm.value)

    console.log('✅ Family member created successfully:', result)

    // Store credentials to show in success dialog
    newMemberCredentials.value = {
      name: `${inviteForm.value.first_name} ${inviteForm.value.last_name}`.trim(),
      email: inviteForm.value.email,
      password: inviteForm.value.password,
      role: roleOptions.find(r => r.value === inviteForm.value.role)?.label || inviteForm.value.role,
    }

    // Show success dialog with credentials
    showCredentialsDialog.value = true
    cancelInvite()

    $q.notify({
      type: 'positive',
      message: `Familie lid ${newMemberCredentials.value.name} succesvol aangemaakt!`,
    })
  } catch (error) {
    console.error('❌ Error creating family member:', error)
    console.error('❌ Error response:', error.response?.data)
    console.error('❌ Store error:', familyStore.error)

    $q.notify({
      type: 'negative',
      message: familyStore.error || error.response?.data?.error || 'Fout bij aanmaken familie lid',
    })
  } finally {
    loading.value = false
  }
}

const cancelInvite = () => {
  showInviteDialog.value = false
  inviteForm.value = {
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'member',
    age: null,
    parental_controls: true,
  }
}

const closeCredentialsDialog = () => {
  showCredentialsDialog.value = false
  newMemberCredentials.value = {}
}

const editMemberRole = (member) => {
  editingMember.value = member
  editRoleForm.value.role = member.role
  showEditRoleDialog.value = true
}

const cancelEditRole = () => {
  showEditRoleDialog.value = false
  editingMember.value = null
  editRoleForm.value.role = 'member'
}

const saveRoleChange = async () => {
  if (!editingMember.value || !editRoleForm.value.role) {
    $q.notify({
      type: 'negative',
      message: 'Selecteer een rol'
    })
    return
  }

  loading.value = true
  try {
    await familyStore.updateMemberRole(
      editingMember.value.id,
      editRoleForm.value.role
    )

    $q.notify({
      type: 'positive',
      message: `Rol van ${editingMember.value.user.first_name} gewijzigd naar ${getRoleLabel(editRoleForm.value.role)}`
    })

    cancelEditRole()
    await refreshFamilyData()
  } catch (error) {
    console.error('Error updating member role:', error)
    $q.notify({
      type: 'negative',
      message: familyStore.error || 'Fout bij wijzigen rol'
    })
  } finally {
    loading.value = false
  }
}

const removeMember = async (member) => {
  try {
    const confirmed = await new Promise((resolve) => {
      $q.dialog({
        title: 'Lid Verwijderen',
        message: `Weet je zeker dat je ${member.user.first_name} ${member.user.last_name} wilt verwijderen uit de familie?`,
        cancel: true,
        persistent: true
      }).onOk(() => resolve(true))
        .onCancel(() => resolve(false))
    })

    if (!confirmed) return

    loading.value = true
    await familyStore.removeMember(member.id)

    $q.notify({
      type: 'positive',
      message: `${member.user.first_name} is verwijderd uit de familie`
    })

    await refreshFamilyData()
  } catch (error) {
    console.error('Error removing member:', error)
    $q.notify({
      type: 'negative',
      message: familyStore.error || 'Fout bij verwijderen lid'
    })
  } finally {
    loading.value = false
  }
}

const getRolePermissions = (role) => {
  const permissions = {
    admin: [
      'Alle rechten',
      'Leden beheren',
      'Familie instellingen wijzigen',
      'Recepten beheren',
      'Maaltijdplannen maken',
      'Boodschappenlijsten beheren'
    ],
    member: [
      'Recepten bekijken en maken',
      'Maaltijdplannen maken',
      'Boodschappenlijsten beheren',
      'Maaltijden voorstellen'
    ],
    child: [
      'Recepten bekijken',
      'Maaltijden voorstellen',
      'Beperkte toegang (ouderlijk toezicht)'
    ],
    viewer: [
      'Alleen bekijken',
      'Geen bewerkingsrechten'
    ]
  }
  return permissions[role] || []
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('nl-NL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const isCurrentUser = (member) => {
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  return member.user.id === currentUser.id
}

// Helper methods for role display
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
    admin: 'Beheerder',
    member: 'Lid',
    child: 'Kind',
    viewer: 'Kijker'
  }
  return labels[role] || role
}

// Refresh family data
const refreshFamilyData = async () => {
  try {
    console.log('🔄 Refreshing family data...')
    await familyStore.fetchFamilies()
    if (familyStore.currentFamily) {
      await familyStore.fetchFamilyMembers(familyStore.currentFamily.id)
    }

    $q.notify({
      type: 'positive',
      message: 'Familie gegevens vernieuwd',
      timeout: 1000
    })
  } catch (error) {
    console.error('❌ Error refreshing family data:', error)
    $q.notify({
      type: 'negative',
      message: 'Fout bij vernieuwen van gegevens'
    })
  }
}

// Initialize family data when component loads
const initializePage = async () => {
  try {
    console.log('🏠 Initializing family management page...')
    await familyStore.initializeFamilyContext()
    console.log('✅ Family context initialized')
    console.log('📊 Current family:', familyStore.currentFamily)
    console.log('👥 Family members:', familyStore.familyMembers)

    // Show notification if no family exists
    if (familyStore.families.length === 0) {
      $q.notify({
        type: 'info',
        message: 'Welkom! Maak je eerste familie aan om te beginnen.',
        timeout: 3000
      })
    }
  } catch (error) {
    console.error('❌ Error initializing family context:', error)
    $q.notify({
      type: 'negative',
      message: 'Fout bij laden van familie gegevens'
    })
  }
}

// Initialize on component mount
initializePage()

// Log to console for debugging
console.log('🏠 FamilyManagementPage: Component loaded successfully')
console.log('🔍 Current route:', window.location.href)
console.log('📍 Vue route path:', window.location.hash)
</script>

<style scoped>
.q-card {
  border-radius: 12px;
}
</style>
