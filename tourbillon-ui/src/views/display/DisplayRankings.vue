<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { rankings } = storeToRefs(store)

onMounted(async () => {
  await store.refreshRankings()
  setInterval(() => {
    store.refreshRankings()
  }, 5000)
})
</script>

<template>
  <section>
    <h1>Live Rankings</h1>
    <table v-if="rankings.length" class="display-table">
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
          <td>#{{ row.team }}</td>
          <td>{{ row.wins }}</td>
          <td>{{ row.points }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No ranking data.</p>
  </section>
</template>

<style scoped>
h1 {
  font-size: 2rem;
}

.display-table {
  font-size: 1.2rem;
}
</style>
