<script setup>
import { onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()

onMounted(() => {
  store.refreshAll()
})
</script>

<template>
  <div class="display-layout">
    <header class="topbar">
      <RouterLink to="/" class="brand">TourBillon</RouterLink>
      <nav>
        <RouterLink to="/display/teams" active-class="active">Teams</RouterLink>
        <RouterLink to="/display/rankings" active-class="active">Rankings</RouterLink>
        <RouterLink to="/display/round" active-class="active">Round</RouterLink>
      </nav>
    </header>
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

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
}

nav {
  display: flex;
  gap: 1rem;
}

nav a {
  opacity: 0.7;
}

nav a.active {
  opacity: 1;
  font-weight: 600;
}

main {
  padding: 2rem;
}
</style>
