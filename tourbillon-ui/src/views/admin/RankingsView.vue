<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'
import { useRankingColumns } from '@/composables/useRankingColumns'

const store = useTournamentStore()
const { rounds, rankings } = storeToRefs(store)

const selectedRound = ref('')

const currentRoundNumber = computed(() => {
  if (!selectedRound.value) {
    return undefined
  }
  return Number(selectedRound.value)
})

const {
  isTieRank,
  showWins,
  showJoker,
  showBuchholz,
  showGoalAvg,
  refreshRankingOptions,
} = useRankingColumns(rankings)

onMounted(async () => {
  await Promise.all([store.refreshRounds(), store.refreshRankings(), refreshRankingOptions()])
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
      </div>
    </header>

    <table v-if="rankings.length">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team</th>
          <th v-if="showWins">Wins</th>
          <th>Points</th>
          <th v-if="showJoker">Joker</th>
          <th v-if="showBuchholz">Buchholz</th>
          <th v-if="showGoalAvg">Goal Avg</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rankings" :key="row.team">
          <td>
            <span>{{ row.rank }}</span>
            <span v-if="isTieRank(row.rank)" class="tie-indicator" aria-label="Tied rank" title="Tied rank">⇄</span>
          </td>
          <td>{{ row.team }}</td>
          <td v-if="showWins">{{ row.wins }}</td>
          <td>{{ row.points }}</td>
          <td v-if="showJoker">{{ row.joker }}</td>
          <td v-if="showBuchholz">{{ row.buchholz }}</td>
          <td v-if="showGoalAvg">{{ row.goal_average }}</td>
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

.tie-indicator {
  margin-left: 0.45rem;
  padding: 0.08rem 0.42rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  background: color-mix(in srgb, var(--color-primary) 14%, transparent);
  color: var(--color-primary-dark);
}
</style>
