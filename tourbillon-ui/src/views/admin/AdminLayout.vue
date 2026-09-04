<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useTournamentStore } from '@/stores/tournament'
import SettingsModal from '@/components/SettingsModal.vue'
import { api } from '@/api/client'
import { useEvents } from '@/events/eventsClient'

const { t } = useI18n()
const store = useTournamentStore()
const { tournament } = storeToRefs(store)

const settingsOpen = ref(false)
const currentDisplayView = ref('display-rankings')
const { subscribe } = useEvents()

// The Tournament tab is always available (it creates/loads a tournament); the
// other tabs require a loaded tournament and stay disabled until then.
const tabs = computed(() => [
  { name: 'admin-tournament', label: t('nav.tournament'), always: true },
  { name: 'admin-teams', label: t('nav.teams') },
  { name: 'admin-round', label: t('nav.rounds') },
  { name: 'admin-draw', label: t('nav.draw') },
  { name: 'admin-rankings', label: t('nav.rankings') },
])

const displayTabs = computed(() => [
  { name: 'display-teams', label: t('nav.teams') },
  { name: 'display-round', label: t('nav.round') },
  { name: 'display-rankings', label: t('nav.rankings') },
])

const tabCounts = computed(() => {
  const counts = {
    'admin-tournament': tournament.value ? 1 : 0,
    'admin-teams': tournament.value ? store.teams.length : 0,
    'admin-round': tournament.value ? store.rounds.length : 0,
    'admin-draw': tournament.value ? (store.drawPreviewReady ? 1 : 0) : 0,
  }

  return counts
})

const canOpenRound = computed(() => {
  if (!tournament.value) return false
  return tournament.value.nb_teams >= tournament.value.teams_by_match
})

const canOpenDraw = computed(() => {
  if (!canOpenRound.value) return false
  if (!store.rounds.length) return true
  const lastRound = store.rounds[store.rounds.length - 1]
  return ['complete', 'finished'].includes(lastRound.status)
})

const canOpenRankings = computed(() => {
  if (!tournament.value) return false
  return store.rounds.some((round) => ['complete', 'finished'].includes(round.status))
})

function isTabEnabled(tab) {
  if (tab.always) return true
  if (!tournament.value) return false
  if (tab.name === 'admin-round') return canOpenRound.value
  if (tab.name === 'admin-draw') return canOpenDraw.value
  if (tab.name === 'admin-rankings') return canOpenRankings.value
  return true
}

function disabledTitle(tab) {
  if (!tournament.value) return t('nav.disabledNoTournament')
  if (tab.name === 'admin-round' && !canOpenRound.value) {
    return t('nav.disabledNeedTeams', { count: tournament.value.teams_by_match })
  }
  if (tab.name === 'admin-draw' && !canOpenDraw.value) {
    return t('nav.disabledFinishRound')
  }
  if (tab.name === 'admin-rankings' && !canOpenRankings.value) {
    return t('nav.disabledCompleteRound')
  }
  return t('nav.disabledUnavailable')
}

function hasCount(tabName) {
  return tabName in tabCounts.value
}

function countFor(tabName) {
  return tabCounts.value[tabName] ?? 0
}

function handleDisplayViewChanged(payload) {
  if (payload.view) {
    currentDisplayView.value = payload.view
  }
}

subscribe('display_view_changed', handleDisplayViewChanged)

async function refreshDisplayView() {
  try {
    const payload = await api.getDisplayView()
    currentDisplayView.value = payload.view || currentDisplayView.value
  } catch {
    // Keep current value when backend is temporarily unavailable.
  }
}

async function selectDisplayView(view) {
  currentDisplayView.value = view
  try {
    await api.setDisplayView(view)
  } catch {
    await refreshDisplayView()
  }
}

onMounted(() => {
  store.refreshAll()
  refreshDisplayView()
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
      <span class="role">{{ t('nav.admin') }}</span>
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
        {{ t('nav.display') }}
      </div>
      <nav>
        <button
          v-for="tab in displayTabs"
          :key="tab.name"
          type="button"
          class="nav-link"
          :aria-pressed="currentDisplayView === tab.name"
          :class="{ active: currentDisplayView === tab.name }"
          @click="selectDisplayView(tab.name)"
        >
          <span>{{ tab.label }}</span>
          <span
            v-if="currentDisplayView === tab.name"
            class="active-badge"
          >{{ t('nav.active') }}</span>
        </button>
      </nav>
      <button
        class="settings-btn"
        @click="settingsOpen = true"
      >
        ⚙ {{ t('nav.settings') }}
      </button>
    </aside>
    <main class="content">
      <RouterView v-slot="{ Component }">
        <KeepAlive>
          <component :is="Component" />
        </KeepAlive>
      </RouterView>
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
