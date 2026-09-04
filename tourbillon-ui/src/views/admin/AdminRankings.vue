<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'
import { useRankingCriteria } from '@/composables/useRankingCriteria'
import { useRankingTeams } from '@/composables/useRankingTeams'

const store = useTournamentStore()
const { rounds, rankings, teams } = storeToRefs(store)

const selectedRound = ref('')
const teamFilterInput = ref('')

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

const filteredRankings = computed(() => {
  const raw = String(teamFilterInput.value ?? '').trim()
  if (!raw) {
    return rankings.value
  }
  const teamNumber = Number(raw)
  if (!Number.isInteger(teamNumber) || teamNumber <= 0) {
    return []
  }
  return rankings.value.filter((row) => row.team === teamNumber)
})

function clearTeamFilter() {
  teamFilterInput.value = ''
}

function printRankings() {
  window.print()
}

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
        <label
          class="team-search"
          for="rankings-team-filter"
        >
          <span>Team</span>
          <span class="team-search-control">
            <input
              id="rankings-team-filter"
              v-model="teamFilterInput"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              placeholder="e.g. 12"
            >
            <button
              v-if="teamFilterInput"
              type="button"
              class="team-search-clear"
              aria-label="Clear team filter"
              title="Clear"
              @click="clearTeamFilter"
            >
              ×
            </button>
          </span>
        </label>
        <button
          class="print-btn"
          title="Print the rankings"
          @click="printRankings"
        >
          Print
        </button>
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

    <table v-if="filteredRankings.length">
      <thead>
        <tr>
          <th class="rank-cell">
            Rank
          </th>
          <th class="centered-cell">
            Team
          </th>
          <th>Players</th>
          <th
            v-if="showWins"
            class="centered-cell criteria-cell"
          >
            Wins
          </th>
          <th class="centered-cell criteria-cell">
            Points
          </th>
          <th
            v-if="showJoker"
            class="centered-cell criteria-cell"
          >
            Joker
          </th>
          <th
            v-if="showBuchholz"
            class="centered-cell criteria-cell"
          >
            Buchholz
          </th>
          <th
            v-if="showGoalAvg"
            class="centered-cell criteria-cell"
          >
            Goal Avg
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in filteredRankings"
          :key="row.team"
        >
          <td class="rank-cell">
            <span>{{ row.rank }}</span>
            <span
              v-if="isTieRank(row.rank)"
              class="tie-indicator"
              aria-label="Tied rank"
              title="Tied rank"
            >⇄</span>
          </td>
          <td class="centered-cell">
            {{ row.team }}
          </td>
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
            class="centered-cell criteria-cell"
          >
            {{ row.wins }}
          </td>
          <td class="centered-cell criteria-cell">
            {{ row.points }}
          </td>
          <td
            v-if="showJoker"
            class="centered-cell criteria-cell"
          >
            {{ row.joker }}
          </td>
          <td
            v-if="showBuchholz"
            class="centered-cell criteria-cell"
          >
            {{ row.buchholz }}
          </td>
          <td
            v-if="showGoalAvg"
            class="centered-cell criteria-cell"
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
      {{ teamFilterInput ? 'No team matches this filter.' : 'No ranking data available.' }}
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
  align-items: center;
  gap: 0.5rem;
}

.team-search {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
}

.team-search-control {
  position: relative;
  display: inline-flex;
  width: 9.2rem;
}

.team-search input,
.row select,
.row .print-btn {
  height: 2.35rem;
  line-height: 1.2;
  box-sizing: border-box;
}

.row select,
.row .print-btn {
  width: 9.2rem;
}

.team-search input {
  width: 100%;
  padding-right: 1.7rem;
}

.team-search-clear {
  position: absolute;
  right: 0.25rem;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: var(--color-muted);
  width: 1.2rem;
  height: 1.2rem;
  line-height: 1;
  padding: 0;
  cursor: pointer;
}

.team-search-clear:hover {
  color: var(--color-text);
}

.centered-cell {
  text-align: center;
}

.rank-cell {
  width: 4.5rem;
  white-space: nowrap;
}

/* Every ranking criteria shares the same column width */
.criteria-cell {
  width: 6.5rem;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
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

/* Printing keeps the ranking table only: controls are dropped */
@media print {
  .row {
    display: none !important;
  }
}
</style>
