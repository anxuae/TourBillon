<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'
import SettingsModal from '@/components/SettingsModal.vue'
import { api, openDrawSocket } from '@/api/client'

const store = useTournamentStore()
const { tournament } = storeToRefs(store)

const settingsOpen = ref(false)
const displayView = ref('display-rankings')
let displaySocket = null

// The Tournament tab is always available (it creates/loads a tournament); the
// other tabs require a loaded tournament and stay disabled until then.
const tabs = [
  { name: 'admin-tournament', label: 'Tournament', always: true },
  { name: 'admin-teams', label: 'Teams' },
  { name: 'admin-round', label: 'Rounds' },
  { name: 'admin-rankings', label: 'Rankings' },
]

const displayTabs = [
  { name: 'display-teams', label: 'Teams' },
  { name: 'display-round', label: 'Round' },
  { name: 'display-rankings', label: 'Rankings' },
]

const tabCounts = computed(() => ({
  'admin-tournament': tournament.value ? 1 : 0,
  'admin-teams': tournament.value ? store.teams.length : 0,
  'admin-round': tournament.value ? store.rounds.length : 0,
}))

const canOpenRound = computed(() => {
  if (!tournament.value) return false
  return tournament.value.nb_teams >= tournament.value.teams_by_match
})

const canOpenRankings = computed(() => {
  if (!tournament.value) return false
  return store.rounds.some((round) => ['complete', 'finished'].includes(round.status))
})

function isTabEnabled(tab) {
  if (tab.always) return true
  if (!tournament.value) return false
  if (tab.name === 'admin-round') return canOpenRound.value
  if (tab.name === 'admin-rankings') return canOpenRankings.value
  return true
}

function disabledTitle(tab) {
  if (!tournament.value) return 'Load or create a tournament first'
  if (tab.name === 'admin-round' && !canOpenRound.value) {
    return `Register at least ${tournament.value.teams_by_match} teams first`
  }
  if (tab.name === 'admin-rankings' && !canOpenRankings.value) {
    return 'Complete at least one round first'
  }
  return 'Unavailable'
}

function hasCount(tabName) {
  return tabName in tabCounts.value
}

function countFor(tabName) {
  return tabCounts.value[tabName] ?? 0
}

function connectDisplaySocket() {
  if (displaySocket) {
    displaySocket.close()
  }
  displaySocket = openDrawSocket()
  displaySocket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === 'display_view_changed' && payload.view) {
        displayView.value = payload.view
      }
    } catch {
      // Ignore malformed websocket payload.
    }
  }
}

async function refreshDisplayView() {
  try {
    const payload = await api.getDisplayView()
    displayView.value = payload.view || displayView.value
  } catch {
    // Keep current value when backend is temporarily unavailable.
  }
}

async function selectDisplayView(view) {
  displayView.value = view
  try {
    await api.setDisplayView(view)
  } catch {
    await refreshDisplayView()
  }
}

onMounted(() => {
  store.refreshAll()
  refreshDisplayView()
  connectDisplaySocket()
})

onBeforeUnmount(() => {
  if (displaySocket) {
    displaySocket.close()
    displaySocket = null
  }
})
</script>

<template>
  <div class="admin">
    <aside class="sidebar">
      <RouterLink
        to="/"
        class="brand"
      >
        TourBillon
      </RouterLink>
      <span class="role">Admin</span>
      <nav>
        <template
          v-for="tab in tabs"
          :key="tab.name"
        >
          <RouterLink
            v-if="isTabEnabled(tab)"
            :to="{ name: tab.name }"
            class="nav-link"
            active-class="active"
          >
            <span>{{ tab.label }}</span>
            <span
              v-if="hasCount(tab.name)"
              class="tab-count"
            >{{ countFor(tab.name) }}</span>
          </RouterLink>
          <span
            v-else
            class="nav-link disabled"
            :title="disabledTitle(tab)"
          >
            <span>{{ tab.label }}</span>
            <span
              v-if="hasCount(tab.name)"
              class="tab-count"
            >{{ countFor(tab.name) }}</span>
          </span>
        </template>
      </nav>
      <hr class="separator">
      <div class="section-label">
        Display
      </div>
      <nav>
        <button
          v-for="tab in displayTabs"
          :key="tab.name"
          type="button"
          class="nav-link"
          :aria-pressed="displayView === tab.name"
          :class="{ active: displayView === tab.name }"
          @click="selectDisplayView(tab.name)"
        >
          <span>{{ tab.label }}</span>
          <span
            v-if="displayView === tab.name"
            class="active-badge"
          >active</span>
        </button>
      </nav>
      <button
        class="settings-btn"
        @click="settingsOpen = true"
      >
        ⚙ Settings
      </button>
    </aside>
    <main class="content">
      <RouterView />
    </main>
    <SettingsModal
      :open="settingsOpen"
      @close="settingsOpen = false"
      @saved="store.refreshAll()"
    />
  </div>
</template>

<style scoped>
.admin {
  display: grid;
  grid-template-columns: 220px 1fr;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow: hidden;
}

.brand {
  font-size: 1.35rem;
  font-weight: 700;
}

.role {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
}

.separator {
  width: 100%;
  border: 0;
  border-top: 1px solid var(--color-border);
  margin: 0.5rem 0 0.25rem;
}

.section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
  margin-top: 0.25rem;
}

nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius);
  color: var(--color-muted);
  font-weight: 500;
  width: 100%;
  background: none;
  border: 0;
  font: inherit;
  cursor: pointer;
}

.nav-link:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.nav-link.active {
  background: color-mix(in srgb, var(--color-bg) 85%, var(--color-surface));
  color: var(--color-text);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.16);
  transform: translateY(1px);
}

.nav-link.active:hover {
  background: color-mix(in srgb, var(--color-bg) 80%, var(--color-surface));
}

.active-badge {
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--color-text) 20%, transparent);
  color: var(--color-muted);
  font-size: 0.66rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.nav-link.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

.tab-count {
  min-width: 1.35rem;
  height: 1.35rem;
  padding: 0 0.35rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
  background: color-mix(in srgb, var(--color-text) 12%, transparent);
  color: inherit;
}

.nav-link.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
}

.settings-btn {
  margin-top: auto;
  width: 100%;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 0.5rem 0.75rem;
  color: var(--color-muted);
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.settings-btn:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.content {
  min-height: 0;
  padding: 2rem;
  overflow-y: auto;
}
</style>
