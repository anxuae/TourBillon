<script setup>
import { onBeforeUnmount, onMounted, provide, ref } from 'vue'
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

async function syncView(view, notifyApi = false, manual = false) {
  if (!view || route.name === view) return
  router.replace({ name: view })
  if (notifyApi) {
    try {
      await api.setDisplayView(view, manual)
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
  // Auto-computed: mark the server-side view as non-manual so a freshly
  // opened Display tab keeps recomputing it too (see refreshSettingsAndView).
  await syncView(resolveAutoView(), true, false)
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
  // The server remembers whether the current view was an explicit admin
  // choice (sidebar) or computed by the auto-switch logic. A freshly opened
  // Display tab must honor a manual choice as-is, instead of unconditionally
  // recomputing the auto view from the tournament state (which would also
  // silently override the admin's choice for every other open Display tab).
  let current = null
  try {
    current = await api.getDisplayView()
  } catch {
    current = null
  }
  if (current?.manual) {
    autoSwitchEnabled.value = false
    syncView(current.view)
    return
  }
  if (autoSwitchEnabled.value) {
    applyAutoView()
    return
  }
  if (current) {
    syncView(current.view)
  }
}

subscribe('display_view_changed', (payload) => {
  // Only an explicit admin pick (sidebar) disables this tab's auto-switch.
  // Events caused by another Display tab's own auto-switch sync must not
  // disable this one too, otherwise auto-switch breaks across every screen
  // as soon as more than one Display tab is open.
  if (payload.manual) {
    autoSwitchEnabled.value = false
  }
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

// Escape leaves the full screen display space and goes back to the home screen.
function onKeydown(event) {
  if (event.key === 'Escape') {
    event.preventDefault()
    router.push({ name: 'home' })
  }
}

onMounted(async () => {
  window.addEventListener('keydown', onKeydown)
  await refreshSettingsAndView()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
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
