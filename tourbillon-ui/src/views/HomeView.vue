<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AboutModal from '@/components/AboutModal.vue'

const { t } = useI18n()
const aboutOpen = ref(false)

const interfaces = computed(() => [
  {
    to: '/admin',
    title: t('home.adminTitle'),
    text: t('home.adminText'),
    icon: '🛠️',
  },
  {
    to: '/display',
    title: t('home.displayTitle'),
    text: t('home.displayText'),
    icon: '📺',
  },
  {
    to: '/history',
    title: t('home.historyTitle'),
    text: t('home.historyText'),
    icon: '📚',
  },
])
</script>

<template>
  <main class="home">
    <header class="home-header">
      <h1>TourBillon</h1>
      <p class="muted">
        {{ t('home.tagline') }}
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
        {{ t('home.about') }}
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
