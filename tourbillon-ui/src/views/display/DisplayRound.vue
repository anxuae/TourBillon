<script setup>
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'

const currentRound = ref(null)

async function refreshRound() {
  const rounds = await api.listRounds()
  if (!rounds.length) {
    currentRound.value = null
    return
  }
  currentRound.value = rounds[rounds.length - 1]
}

onMounted(async () => {
  await refreshRound()
  setInterval(refreshRound, 5000)
})
</script>

<template>
  <section>
    <h1>Current Round</h1>
    <div v-if="currentRound" class="grid">
      <article
        v-for="(match, index) in currentRound.matches"
        :key="`${currentRound.number}-${index}`"
        class="match"
      >
        <h3>Location {{ match.location || index + 1 }}</h3>
        <p class="teams">{{ match.teams.join(' vs ') }}</p>
      </article>
    </div>
    <p v-if="currentRound?.byes?.length">Byes: {{ currentRound.byes.join(', ') }}</p>
    <p v-else-if="!currentRound">No round in progress.</p>
  </section>
</template>

<style scoped>
h1 {
  font-size: 2rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.match {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1rem;
}

.teams {
  font-size: 1.3rem;
  font-weight: 700;
}
</style>
