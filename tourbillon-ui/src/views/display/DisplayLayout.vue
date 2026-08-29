<script setup>
import { onMounted, provide, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useTournamentStore } from '@/stores/tournament'
import { api } from '@/api/client'
import { useEvents } from '@/events/eventsClient'

const store = useTournamentStore()
const router = useRouter()
const route = useRoute()

const rotationSeconds = ref(12)
provide('displayRotationSeconds', rotationSeconds)

const { subscribe } = useEvents()

function syncView(view) {
  if (!view || route.name === view) return
  router.replace({ name: view })
}

async function refreshRotationSettings() {
  try {
    const settings = await api.getSettings()
    const raw = Number(settings?.display?.rotation_seconds)
    if (Number.isFinite(raw) && raw > 0) {
      rotationSeconds.value = raw
    }
  } catch {
    // Keep the default rotation value when settings are unavailable.
  }
}

subscribe('display_view_changed', (payload) => {
  if (payload.view) syncView(payload.view)
})

subscribe('tournament_changed', () => {
  store.refreshAll()
})

onMounted(async () => {
  store.refreshAll()
  await refreshRotationSettings()
  try {
    const payload = await api.getDisplayView()
    syncView(payload.view)
  } catch {
    // Keep current view if display endpoint is temporarily unavailable.
  }
})

</script>

<template>
  <div class="display-layout">
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.display-layout {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
}

main {
  padding: 2rem;
  height: 100vh;
  overflow: hidden;
}
</style>
