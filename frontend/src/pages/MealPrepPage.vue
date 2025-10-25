<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-lg">
      <div class="text-h4">Meal Prep Sessions</div>
      <q-btn
        color="primary"
        icon="add"
        label="New Session"
        @click="showCreateDialog = true"
      />
    </div>

    <!-- Filters -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="row q-gutter-md items-center">
          <div class="col-12 col-md-3">
            <q-select
              v-model="statusFilter"
              :options="statusOptions"
              label="Status Filter"
              outlined
              dense
              clearable
            />
          </div>
          <div class="col-12 col-md-3">
            <q-input
              v-model="dateFilter"
              label="Date"
              type="date"
              outlined
              dense
              clearable
            />
          </div>
          <div class="col-12 col-md-4">
            <q-input
              v-model="searchQuery"
              label="Search sessions..."
              outlined
              dense
              clearable
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Loading State -->
    <div v-if="loading" class="text-center q-py-xl">
      <q-spinner-dots size="48px" color="primary" />
      <div class="text-subtitle2 q-mt-md">Loading meal prep sessions...</div>
    </div>

    <!-- Sessions List -->
    <div v-else-if="filteredSessions.length > 0" class="q-gutter-md">
      <q-card
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-card"
        :class="getSessionCardClass(session.status)"
      >
        <q-card-section>
          <div class="row items-start justify-between">
            <div class="col">
              <div class="text-h6 q-mb-sm">{{ session.name }}</div>
              <div class="text-subtitle2 text-grey-6 q-mb-sm">
                <q-icon name="event" class="q-mr-xs" />
                {{ formatDate(session.scheduled_date) }}
              </div>

              <!-- Status Badge -->
              <q-badge
                :color="getStatusColor(session.status)"
                :label="getStatusLabel(session.status)"
                class="q-mb-sm"
              />

              <!-- Duration Info -->
              <div v-if="session.estimated_duration" class="text-caption text-grey-6">
                <q-icon name="schedule" class="q-mr-xs" />
                Estimated: {{ session.estimated_duration }} minutes
                <span v-if="session.actual_duration">
                  | Actual: {{ session.actual_duration }} minutes
                </span>
              </div>
            </div>

            <div class="col-auto">
              <q-btn-group flat>
                <q-btn
                  flat
                  icon="visibility"
                  @click="viewSession(session)"
                  :disable="session.status === 'cancelled'"
                />
                <q-btn
                  flat
                  icon="edit"
                  @click="editSession(session)"
                  :disable="session.status === 'completed'"
                />
                <q-btn
                  flat
                  icon="play_arrow"
                  @click="startSession(session)"
                  :disable="session.status !== 'planned'"
                  color="positive"
                />
                <q-btn
                  flat
                  icon="check"
                  @click="completeSession(session)"
                  :disable="session.status !== 'in_progress'"
                  color="positive"
                />
              </q-btn-group>
            </div>
          </div>

          <!-- Tasks Preview -->
          <div v-if="session.tasks && session.tasks.length > 0" class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">Tasks ({{ session.tasks.length }})</div>
            <div class="row q-gutter-xs">
              <q-chip
                v-for="task in session.tasks.slice(0, 3)"
                :key="task.id"
                :color="task.completed ? 'positive' : 'grey-4'"
                :text-color="task.completed ? 'white' : 'grey-8'"
                size="sm"
                :icon="task.completed ? 'check' : 'schedule'"
              >
                {{ task.task_name }}
              </q-chip>
              <q-chip
                v-if="session.tasks.length > 3"
                color="grey-4"
                text-color="grey-8"
                size="sm"
              >
                +{{ session.tasks.length - 3 }} more
              </q-chip>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="session.notes" class="q-mt-sm">
            <div class="text-caption text-grey-6">{{ session.notes }}</div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center text-grey-6 q-py-xl">
      <q-icon name="kitchen" size="4rem" class="q-mb-md" />
      <div class="text-h6">No meal prep sessions found</div>
      <div class="text-subtitle2">Create your first meal prep session to get started</div>
      <q-btn
        color="primary"
        label="Create Session"
        class="q-mt-md"
        @click="showCreateDialog = true"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <q-dialog v-model="showCreateDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">
            {{ editingSession ? 'Edit Session' : 'New Meal Prep Session' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveSession" class="q-gutter-md">
            <q-input
              v-model="sessionForm.name"
              label="Session Name *"
              outlined
              :rules="[val => !!val || 'Name is required']"
            />

            <q-input
              v-model="sessionForm.scheduled_date"
              label="Scheduled Date *"
              type="date"
              outlined
              :rules="[val => !!val || 'Date is required']"
            />

            <q-input
              v-model.number="sessionForm.estimated_duration"
              label="Estimated Duration (minutes)"
              type="number"
              min="1"
              outlined
            />

            <q-input
              v-model="sessionForm.notes"
              label="Notes"
              type="textarea"
              rows="3"
              outlined
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelEdit" />
          <q-btn
            color="primary"
            label="Save"
            @click="saveSession"
            :loading="saving"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Session Detail Dialog -->
    <q-dialog v-model="showDetailDialog" persistent>
      <q-card style="min-width: 600px; max-width: 800px">
        <q-card-section v-if="selectedSession">
          <div class="text-h6">{{ selectedSession.name }}</div>
          <div class="text-subtitle2 text-grey-6">
            {{ formatDate(selectedSession.scheduled_date) }}
          </div>
        </q-card-section>

        <q-card-section v-if="selectedSession" class="q-pt-none">
          <!-- Session Info -->
          <div class="row q-gutter-md q-mb-lg">
            <div class="col">
              <q-badge
                :color="getStatusColor(selectedSession.status)"
                :label="getStatusLabel(selectedSession.status)"
              />
            </div>
            <div class="col-auto" v-if="selectedSession.estimated_duration">
              <div class="text-caption">
                Estimated: {{ selectedSession.estimated_duration }}min
              </div>
            </div>
            <div class="col-auto" v-if="selectedSession.actual_duration">
              <div class="text-caption">
                Actual: {{ selectedSession.actual_duration }}min
              </div>
            </div>
          </div>

          <!-- Tasks -->
          <div v-if="selectedSession.tasks && selectedSession.tasks.length > 0">
            <div class="text-subtitle1 q-mb-md">Tasks</div>
            <q-list bordered separator>
              <q-item
                v-for="task in selectedSession.tasks"
                :key="task.id"
                :class="{ 'bg-green-1': task.completed }"
              >
                <q-item-section avatar>
                  <q-checkbox
                    v-model="task.completed"
                    @update:model-value="updateTaskStatus(task)"
                    :disable="selectedSession.status === 'completed'"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ task.task_name }}</q-item-label>
                  <q-item-label caption>{{ task.recipe.title }}</q-item-label>
                </q-item-section>
                <q-item-section side v-if="task.estimated_time">
                  <q-item-label caption>{{ task.estimated_time }}min</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Notes -->
          <div v-if="selectedSession.notes" class="q-mt-lg">
            <div class="text-subtitle1 q-mb-sm">Notes</div>
            <div class="text-body2">{{ selectedSession.notes }}</div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" @click="showDetailDialog = false" />
          <q-btn
            v-if="selectedSession && selectedSession.status === 'planned'"
            color="positive"
            label="Start Session"
            @click="startSession(selectedSession)"
          />
          <q-btn
            v-if="selectedSession && selectedSession.status === 'in_progress'"
            color="positive"
            label="Complete Session"
            @click="completeSession(selectedSession)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// State
const sessions = ref([])
const loading = ref(true)
const saving = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingSession = ref(null)
const selectedSession = ref(null)

// Filters
const statusFilter = ref(null)
const dateFilter = ref(null)
const searchQuery = ref('')

// Form
const sessionForm = ref({
  name: '',
  scheduled_date: '',
  estimated_duration: null,
  notes: ''
})

// Options
const statusOptions = [
  { label: 'Planned', value: 'planned' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

// Computed
const filteredSessions = computed(() => {
  let filtered = sessions.value

  if (statusFilter.value) {
    filtered = filtered.filter(s => s.status === statusFilter.value)
  }

  if (dateFilter.value) {
    filtered = filtered.filter(s => s.scheduled_date === dateFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(s =>
      s.name.toLowerCase().includes(query) ||
      s.notes.toLowerCase().includes(query)
    )
  }

  return filtered.sort((a, b) => new Date(b.scheduled_date) - new Date(a.scheduled_date))
})

// Methods
const loadSessions = async () => {
  loading.value = true
  try {
    // Mock data for now - replace with actual API call
    sessions.value = [
      {
        id: '1',
        name: 'Sunday Meal Prep',
        scheduled_date: '2025-01-12',
        estimated_duration: 180,
        actual_duration: null,
        status: 'planned',
        notes: 'Prep for the week ahead',
        tasks: [
          {
            id: '1',
            task_name: 'Cook rice',
            recipe: { title: 'Basic Rice' },
            estimated_time: 30,
            completed: false
          },
          {
            id: '2',
            task_name: 'Chop vegetables',
            recipe: { title: 'Greek Salad' },
            estimated_time: 20,
            completed: false
          }
        ]
      },
      {
        id: '2',
        name: 'Weekend Batch Cooking',
        scheduled_date: '2025-01-05',
        estimated_duration: 240,
        actual_duration: 220,
        status: 'completed',
        notes: 'Completed successfully',
        tasks: [
          {
            id: '3',
            task_name: 'Make pasta sauce',
            recipe: { title: 'Spaghetti Carbonara' },
            estimated_time: 45,
            completed: true
          }
        ]
      }
    ]
  } catch (error) {
    console.error('Error loading sessions:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load meal prep sessions'
    })
  } finally {
    loading.value = false
  }
}

const viewSession = (session) => {
  selectedSession.value = session
  showDetailDialog.value = true
}

const editSession = (session) => {
  editingSession.value = session
  sessionForm.value = { ...session }
  showCreateDialog.value = true
}

const startSession = async (session) => {
  try {
    // Mock API call
    session.status = 'in_progress'
    session.started_at = new Date().toISOString()

    $q.notify({
      type: 'positive',
      message: 'Session started!'
    })
  } catch (error) {
    console.error('Error starting session:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to start session'
    })
  }
}

const completeSession = async (session) => {
  try {
    // Mock API call
    session.status = 'completed'
    session.completed_at = new Date().toISOString()

    // Calculate actual duration if started
    if (session.started_at) {
      const start = new Date(session.started_at)
      const end = new Date()
      session.actual_duration = Math.round((end - start) / (1000 * 60))
    }

    $q.notify({
      type: 'positive',
      message: 'Session completed!'
    })

    showDetailDialog.value = false
  } catch (error) {
    console.error('Error completing session:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to complete session'
    })
  }
}

const saveSession = async () => {
  saving.value = true
  try {
    if (editingSession.value) {
      // Update existing session
      Object.assign(editingSession.value, sessionForm.value)
    } else {
      // Create new session
      const newSession = {
        id: Date.now().toString(),
        ...sessionForm.value,
        status: 'planned',
        tasks: []
      }
      sessions.value.push(newSession)
    }

    $q.notify({
      type: 'positive',
      message: editingSession.value ? 'Session updated!' : 'Session created!'
    })

    cancelEdit()
  } catch (error) {
    console.error('Error saving session:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to save session'
    })
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  showCreateDialog.value = false
  editingSession.value = null
  sessionForm.value = {
    name: '',
    scheduled_date: '',
    estimated_duration: null,
    notes: ''
  }
}

const updateTaskStatus = async (task) => {
  try {
    // Mock API call
    if (task.completed) {
      task.completed_at = new Date().toISOString()
    } else {
      task.completed_at = null
    }

    $q.notify({
      type: 'positive',
      message: task.completed ? 'Task completed!' : 'Task marked as incomplete'
    })
  } catch (error) {
    console.error('Error updating task:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update task'
    })
  }
}

// Helper methods
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('nl-NL', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getStatusColor = (status) => {
  const colors = {
    planned: 'blue',
    in_progress: 'orange',
    completed: 'green',
    cancelled: 'red'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    planned: 'Planned',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled'
  }
  return labels[status] || status
}

const getSessionCardClass = (status) => {
  const classes = {
    planned: 'border-left-blue',
    in_progress: 'border-left-orange',
    completed: 'border-left-green',
    cancelled: 'border-left-red'
  }
  return classes[status] || ''
}

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.session-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.border-left-blue {
  border-left: 4px solid #1976d2;
}

.border-left-orange {
  border-left: 4px solid #f57c00;
}

.border-left-green {
  border-left: 4px solid #388e3c;
}

.border-left-red {
  border-left: 4px solid #d32f2f;
}
</style>
