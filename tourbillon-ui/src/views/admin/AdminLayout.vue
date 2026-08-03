<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'
import SettingsModal from '@/components/SettingsModal.vue'

const store = useTournamentStore()
const { tournament, error } = storeToRefs(store)

const settingsOpen = ref(false)

const tabs = [
  { name: 'admin-teams', label: 'Teams' },
  { name: 'admin-draw', label: 'Draw' },
  { name: 'admin-round', label: 'Round' },
  { name: 'admin-rankings', label: 'Rankings' },
]

onMounted(() => {
  store.refreshAll()
})
</script>

<template>
  <div class="admin">
    <aside class="sidebar">
      <RouterLink to="/" class="brand">TourBillon</RouterLink>
      <span class="role">Admin</span>
      <nav>
        <RouterLink
          v-for="tab in tabs"
          :key="tab.name"
          :to="{ name: tab.name }"
          class="nav-link"
          active-class="active"
        >
          {{ tab.label }}
        </RouterLink>
      </nav>
      <div class="status">
        <template v-if="tournament">
          <span class="badge">{{ tournament.status }}</span>
          <p class="muted">{{ tournament.nb_teams }} teams · {{ tournament.nb_rounds }} rounds</p>
        </template>
        <p v-else class="muted">No tournament loaded</p>
      </div>
      <button class="settings-btn" @click="settingsOpen = true">⚙ Settings</button>
    </aside>
    <main class="content">
      <p v-if="error" class="error">{{ error }}</p>
      <RouterView />
    </main>
    <SettingsModal :open="settingsOpen" @close="settingsOpen = false" @saved="store.refreshAll()" />
  </div>
</template>

<style scoped>
.admin {
  display: grid;
  grid-template-columns: 220px 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 1rem;
}

.nav-link {
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius);
  color: var(--color-muted);
  font-weight: 500;
}

.nav-link:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.nav-link.active {
  background: var(--color-primary);
  color: #fff;
}

.status {
  margin-top: auto;
}

.settings-btn {
  margin-top: 0.75rem;
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
  padding: 2rem;
  overflow-y: auto;
}
</style>
