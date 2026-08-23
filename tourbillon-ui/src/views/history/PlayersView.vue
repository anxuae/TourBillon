<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api/client'

const players = ref([])
const tournaments = ref([])
const query = ref('')
const loading = ref(false)
const error = ref(null)

const filteredPlayers = computed(() => {
  const text = query.value.trim().toLowerCase()
  if (!text) {
    return players.value
  }
  return players.value.filter((player) => player.name.toLowerCase().includes(text))
})

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const [playerRows, tournamentRows] = await Promise.all([
      api.listHistoryPlayers(),
      api.listHistoryTournaments(),
    ])
    players.value = playerRows
    tournaments.value = tournamentRows
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <header class="head">
      <div>
        <h1>Player History</h1>
        <p class="muted">{{ tournaments.length }} tournaments aggregated</p>
      </div>
      <input v-model="query" placeholder="Search player..." />
    </header>

    <p v-if="loading" class="muted">Loading history...</p>
    <p v-else-if="error" class="muted">Unable to load history data.</p>

    <table v-else-if="filteredPlayers.length">
      <thead>
        <tr>
          <th>Player</th>
          <th>Participations</th>
          <th>Total wins</th>
          <th>Total points</th>
          <th>Best rank</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="player in filteredPlayers" :key="player.name">
          <td>{{ player.name }}</td>
          <td>{{ player.participations }}</td>
          <td>{{ player.wins }}</td>
          <td>{{ player.points }}</td>
          <td>{{ player.best_rank ?? '—' }}</td>
          <td>
            <RouterLink :to="`/history/players/${encodeURIComponent(player.name)}`">
              <button class="secondary">Details</button>
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="muted">No player found.</p>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.head h1 {
  margin: 0;
}
</style>
