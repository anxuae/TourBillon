<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AboutModal from '@/components/AboutModal.vue'

const aboutOpen = ref(false)

const interfaces = [
  {
    to: '/admin',
    title: 'Administration',
    text: 'Register teams, run draws and enter match results.',
    icon: '🛠️',
  },
  {
    to: '/display',
    title: 'Display',
    text: 'Full-screen live rankings and current round for the big screen.',
    icon: '📺',
  },
  {
    to: '/history',
    title: 'History',
    text: 'Year-over-year player statistics across all saved tournaments.',
    icon: '📚',
  },
]
</script>

<template>
  <main class="home">
    <header class="home-header">
      <h1>TourBillon</h1>
      <p class="muted">
        Swiss-system tournament manager for the Billon game.
      </p>
    </header>
    <div class="grid">
      <RouterLink
        v-for="item in interfaces"
        :key="item.to"
        :to="item.to"
        class="tile card"
      >
        <span class="icon">{{ item.icon }}</span>
        <h2>{{ item.title }}</h2>
        <p class="muted">
          {{ item.text }}
        </p>
      </RouterLink>
    </div>
    <footer class="home-footer">
      <button
        class="link"
        @click="aboutOpen = true"
      >
        About
      </button>
    </footer>
    <AboutModal
      :open="aboutOpen"
      @close="aboutOpen = false"
    />
  </main>
</template>

<style scoped>
.home {
  max-width: 960px;
  margin: 0 auto;
  padding: 4rem 1.5rem;
}

.home-header {
  text-align: center;
  margin-bottom: 3rem;
}

.home-header h1 {
  font-size: 2.75rem;
  margin: 0 0 0.5rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.tile {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.tile:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.icon {
  font-size: 2.5rem;
}

.tile h2 {
  margin: 0;
}

.home-footer {
  text-align: center;
  margin-top: 3rem;
}

.link {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  text-decoration: underline;
  opacity: 0.7;
  font: inherit;
}

.link:hover {
  opacity: 1;
}
</style>
