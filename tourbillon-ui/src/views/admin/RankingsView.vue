<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'
import { useRankingCriteria } from '@/composables/useRankingCriteria'
import { useRankingTeams } from '@/composables/useRankingTeams'

const store = useTournamentStore()
const { rounds, rankings, teams } = storeToRefs(store)

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
} = useRankingCriteria(rankings)

const { teamPlayers } = useRankingTeams(teams)

onMounted(async () => {
  await Promise.all([store.refreshRounds(), store.refreshTeams(), store.refreshRankings(), refreshRankingOptions()])
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
        <select
          v-model="selectedRound"
          @change="refreshRankings"
        >
          <option value="">
            Current
          </option>
          <option
            v-for="round in rounds"
            :key="round.number"
            :value="round.number"
          >
            After round {{ round.number }}
          </option>
        </select>
      </div>
    </header>

    <table v-if="rankings.length">
      <thead>
        <tr>
          <th class="centered-cell">Rank</th>
          <th class="centered-cell">Team</th>
          <th>Players</th>
          <th
            v-if="showWins"
            class="centered-cell"
          >
            Wins
          </th>
          <th class="centered-cell">Points</th>
          <th
            v-if="showJoker"
            class="centered-cell"
          >
            Joker
          </th>
          <th
            v-if="showBuchholz"
            class="centered-cell"
          >
            Buchholz
          </th>
          <th
            v-if="showGoalAvg"
            class="centered-cell"
          >
            Goal Avg
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rankings"
          :key="row.team"
        >
          <td class="centered-cell">
            <span>{{ row.rank }}</span>
            <span
              v-if="isTieRank(row.rank)"
              class="tie-indicator"
              aria-label="Tied rank"
              title="Tied rank"
            >⇄</span>
          </td>
          <td class="centered-cell">{{ row.team }}</td>
          <td>
            <span
              v-for="player in teamPlayers(row.team)"
              :key="`${row.team}-${player}`"
              class="player-name"
            >
              {{ player }}
            </span>
            <span v-if="!teamPlayers(row.team).length">—</span>
          </td>
          <td
            v-if="showWins"
            class="centered-cell"
          >
            {{ row.wins }}
          </td>
          <td class="centered-cell">{{ row.points }}</td>
          <td
            v-if="showJoker"
            class="centered-cell"
          >
            {{ row.joker }}
          </td>
          <td
            v-if="showBuchholz"
            class="centered-cell"
          >
            {{ row.buchholz }}
          </td>
          <td
            v-if="showGoalAvg"
            class="centered-cell"
          >
            {{ row.goal_average }}
          </td>
        </tr>
      </tbody>
    </table>
    <p
      v-else
      class="muted"
    >
      No ranking data available.
    </p>
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

.centered-cell {
  text-align: center;
}

.player-name {
  display: block;
  line-height: 1.15;
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
