<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { rounds, rankings } = storeToRefs(store)

const selectedRound = ref('')

const currentRoundNumber = computed(() => {
  if (!selectedRound.value) {
    return undefined
  }
  return Number(selectedRound.value)
})

onMounted(async () => {
  await Promise.all([store.refreshRounds(), store.refreshRankings()])
})

async function refreshRankings() {
  await store.refreshRankings(currentRoundNumber.value)
}
</script>

<template>
  <section>
    <header class="head">
      <h1>Rankings</h1>
      <div class="row">
        <select v-model="selectedRound" @change="refreshRankings">
          <option value="">Current</option>
          <option v-for="round in rounds" :key="round.number" :value="round.number">
            After round {{ round.number }}
          </option>
        </select>
        <button class="secondary" @click="refreshRankings">Refresh</button>
      </div>
    </header>

    <table v-if="rankings.length">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team</th>
          <th>Wins</th>
          <th>Points</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rankings" :key="row.team">
          <td>{{ row.rank }}</td>
          <td>{{ row.team }}</td>
          <td>{{ row.wins }}</td>
          <td>{{ row.points }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="muted">No ranking data available.</p>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.head h1 {
  margin: 0;
}

.row {
  display: flex;
  gap: 0.5rem;
}
</style>
