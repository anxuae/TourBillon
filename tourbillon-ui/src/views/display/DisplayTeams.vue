<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { teams } = storeToRefs(store)

onMounted(async () => {
  await store.refreshTeams()
})

function playerNames(team) {
  if (!team.players.length) {
    return '—'
  }
  return team.players.map((p) => `${p.firstname} ${p.lastname}`.trim()).join(', ')
}
</script>

<template>
  <section>
    <h1>Registered Teams</h1>
    <table v-if="teams.length" class="display-table">
      <thead>
        <tr>
          <th>Team</th>
          <th>Players</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="team in teams" :key="team.number">
          <td>#{{ team.number }}</td>
          <td>{{ playerNames(team) }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No teams available.</p>
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
