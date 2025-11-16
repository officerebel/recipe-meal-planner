<template>
  <div class="version-info" :class="{ 'version-info-minimal': minimal }">
    <q-btn
      v-if="minimal"
      flat
      dense
      round
      size="sm"
      icon="info"
      @click="showDialog = true"
    >
      <q-tooltip>Version Info</q-tooltip>
    </q-btn>

    <div v-else class="version-details">
      <div class="text-caption text-grey-6">
        v{{ versionInfo.version }} • {{ versionInfo.commit }} • {{ formatDate(versionInfo.buildTime) }}
      </div>
    </div>

    <q-dialog v-model="showDialog">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Version Information</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-list dense>
            <q-item>
              <q-item-section>
                <q-item-label caption>Version</q-item-label>
                <q-item-label>{{ versionInfo.version }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Commit</q-item-label>
                <q-item-label>{{ versionInfo.commit }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Branch</q-item-label>
                <q-item-label>{{ versionInfo.branch }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Build Time</q-item-label>
                <q-item-label>{{ formatDate(versionInfo.buildTime) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Environment</q-item-label>
                <q-item-label>{{ versionInfo.environment }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import version from 'src/version'

defineProps({
  minimal: {
    type: Boolean,
    default: false
  }
})

const versionInfo = ref(version)
const showDialog = ref(false)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('nl-NL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.version-info {
  display: inline-flex;
  align-items: center;
}

.version-info-minimal {
  opacity: 0.7;
}

.version-info-minimal:hover {
  opacity: 1;
}

.version-details {
  padding: 4px 8px;
}
</style>
