<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="history-layout">
    <header class="topbar">
      <RouterLink
        to="/"
        class="brand"
      >
        TourBillon
      </RouterLink>
      <nav>
        <RouterLink
          to="/history/players"
          active-class="active"
        >
          Players
        </RouterLink>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.history-layout {
  min-height: 100vh;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
}

nav a.active {
  font-weight: 700;
}

main {
  padding: 2rem;
}
</style>
