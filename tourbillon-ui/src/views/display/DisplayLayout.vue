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

const autoSwitchEnabled = ref(true)

const { subscribe } = useEvents()

async function syncView(view, notifyApi = false) {
  if (!view || route.name === view) return
  router.replace({ name: view })
  if (notifyApi) {
    try {
      await api.setDisplayView(view)
    } catch {
      // Silently ignore API errors during auto-sync
    }
  }
}

function resolveAutoView() {
  if (!store.tournament) {
    return 'display-teams'
  }

  if (!store.rounds.length) {
    return 'display-teams'
  }

  const lastRound = store.rounds[store.rounds.length - 1]
  if (['complete', 'finished'].includes(lastRound.status)) {
    return 'display-rankings'
  }

  return 'display-round'
}

async function applyAutoView() {
  if (!autoSwitchEnabled.value) {
    return
  }
  await syncView(resolveAutoView(), true)
}

async function refreshRotationSettings() {
  try {
    const settings = await api.getSettings()
    const raw = Number(settings?.display?.rotation_seconds)
    const shouldAutoSwitch = settings?.display?.auto_switch !== false
    autoSwitchEnabled.value = shouldAutoSwitch
    if (Number.isFinite(raw) && raw > 0) {
      rotationSeconds.value = raw
    }
  } catch {
    // Keep the default rotation value when settings are unavailable.
  }
}

async function refreshStateAndAutoView() {
  await store.refreshAll()
  // Re-enable auto-switch on state changes (manual switch gets reset here)
  const settings = await api.getSettings()
  autoSwitchEnabled.value = settings?.display?.auto_switch !== false
  applyAutoView()
}

async function refreshSettingsAndView() {
  await refreshRotationSettings()
  await store.refreshAll()
  if (autoSwitchEnabled.value) {
    applyAutoView()
    return
  }
  try {
    const payload = await api.getDisplayView()
    syncView(payload.view)
  } catch {
    // Keep current view if display endpoint is temporarily unavailable.
  }
}

subscribe('display_view_changed', (payload) => {
  // Manual display view change from admin sidebar disables auto-switch
  // Auto-switch will re-enable on next state change (tournament/round update)
  autoSwitchEnabled.value = false
  if (payload.view) syncView(payload.view)
})

for (const type of ['teams_updated', 'round_created', 'round_deleted', 'score_updated', 'tournament_changed']) {
  subscribe(type, () => {
    refreshStateAndAutoView().catch(() => {})
  })
}

subscribe('settings_updated', () => {
  refreshSettingsAndView().catch(() => {})
})

onMounted(async () => {
  await refreshSettingsAndView()
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
