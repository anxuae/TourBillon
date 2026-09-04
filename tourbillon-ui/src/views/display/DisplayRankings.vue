<script setup>
import { computed, inject, nextTick, onMounted, ref, watch } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useEvents } from '@/events/eventsClient'
import { useRankingCriteria } from '@/composables/useRankingCriteria'
import { useRankingTeams } from '@/composables/useRankingTeams'
import TeamBadge from '@/components/TeamBadge.vue'

const rankings = ref([])
const teams = ref([])
const showRankingExtras = ref(false)
const rotationSeconds = inject('displayRotationSeconds', ref(12))
const containerRef = ref(null)
const tableRef = ref(null)

async function refreshRankings() {
  try {
    rankings.value = await api.getRankings()
  } catch {
    rankings.value = []
  }
}

async function refreshTeams() {
  try {
    teams.value = await api.listTeams()
  } catch {
    teams.value = []
  }
}

async function refreshSettings() {
  try {
    const settings = await api.getSettings()
    rankingColumns.applyOptionsFromSettings(settings)
    showRankingExtras.value = settings?.display?.show_ranking_criteria === true
  } catch {
    await rankingColumns.refreshRankingOptions()
    showRankingExtras.value = false
  }
}

const { subscribe } = useEvents()

for (const type of ['score_updated', 'round_created', 'round_deleted']) {
  subscribe(type, () => refreshRankings().catch(() => {}))
}
subscribe('teams_updated', () => {
  Promise.all([refreshTeams(), refreshRankings()]).catch(() => {})
})
subscribe('settings_updated', () => {
  Promise.all([refreshRankings(), refreshSettings()]).catch(() => {})
})
subscribe('tournament_changed', () => {
  Promise.all([refreshRankings(), refreshTeams(), refreshSettings()]).catch(() => {})
})


onMounted(async () => {
  await Promise.all([refreshRankings(), refreshTeams(), refreshSettings()])
})


const allRankings = computed(() => rankings.value)
const rankingColumns = useRankingCriteria(rankings)
const { isTieRank, showWins, showJoker, showBuchholz, showGoalAvg } = rankingColumns
const { teamPlayers } = useRankingTeams(teams)

function rankingsPageSize() {
  const containerHeight = containerRef.value?.clientHeight || window.innerHeight
  const headerHeight = tableRef.value?.tHead?.getBoundingClientRect().height || 56
  const measuredRow = tableRef.value?.tBodies?.[0]?.rows?.[0]
  const rowHeight = measuredRow?.getBoundingClientRect().height || 52
  const usable = Math.max(rowHeight, containerHeight - headerHeight)
  return Math.max(1, Math.floor(usable / rowHeight))
}

const { pageItems: visibleRankings, recalculatePageSize } = useAutoDisplayPaging(
  allRankings,
  rotationSeconds,
  rankingsPageSize,
)

watch(rankings, async () => {
  await nextTick()
  recalculatePageSize()
})
</script>

<template>
  <section
    ref="containerRef"
    class="display-section"
  >
    <table
      v-if="rankings.length"
      ref="tableRef"
      class="display-table"
    >
      <colgroup>
        <col class="col-rank">
        <col class="col-team">
        <col class="col-players">
        <col
          v-if="showWins"
          class="col-criteria"
        >
        <col class="col-points">
        <col
          v-if="showRankingExtras && showJoker"
          class="col-criteria"
        >
        <col
          v-if="showRankingExtras && showBuchholz"
          class="col-criteria"
        >
        <col
          v-if="showRankingExtras && showGoalAvg"
          class="col-criteria"
        >
      </colgroup>
      <thead>
        <tr>
          <th class="centered-cell">
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
            v-if="showRankingExtras && showJoker"
            class="centered-cell criteria-cell"
          >
            Joker
          </th>
          <th
            v-if="showRankingExtras && showBuchholz"
            class="centered-cell criteria-cell"
          >
            Buchholz
          </th>
          <th
            v-if="showRankingExtras && showGoalAvg"
            class="centered-cell criteria-cell goal-avg-cell"
          >
            Goal Avg
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in visibleRankings"
          :key="row.team"
        >
          <td class="centered-cell">
            <span>{{ row.rank }}</span>
            <span
              v-if="isTieRank(row.rank)"
              class="tie-indicator"
              aria-label="Tied rank"
            >⇄</span>
          </td>
          <td class="centered-cell">
            <TeamBadge
              :team="row.team"
              size="md"
            />
          </td>
          <td class="players-cell">
            <span
              v-for="player in teamPlayers(row.team)"
              :key="`${row.team}-${player}`"
              class="player-name"
            >
              {{ player }}
            </span>
            <span
              v-if="!teamPlayers(row.team).length"
              class="player-name"
            >
              —
            </span>
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
            v-if="showRankingExtras && showJoker"
            class="centered-cell criteria-cell"
          >
            {{ row.joker }}
          </td>
          <td
            v-if="showRankingExtras && showBuchholz"
            class="centered-cell criteria-cell"
          >
            {{ row.buchholz }}
          </td>
          <td
            v-if="showRankingExtras && showGoalAvg"
            class="centered-cell criteria-cell goal-avg-cell"
          >
            {{ row.goal_average }}
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>
      No ranking data.
    </p>
  </section>
</template>

<style scoped>
.display-section {
  height: 100%;
}

.display-table {
  width: 100%;
  font-size: clamp(1rem, 1.9vw, 2rem);
  color: var(--color-text);
  table-layout: fixed;
}

.display-table td,
.display-table th {
  color: var(--color-text);
  padding: clamp(0.45rem, 1.2vh, 0.9rem) clamp(0.5rem, 1.3vw, 1.1rem);
}

.display-table th {
  font-size: clamp(0.78rem, 1.25vw, 1.1rem);
}

.display-table td {
  font-size: clamp(1rem, 1.8vw, 1.9rem);
  font-weight: 600;
}

.col-rank {
  width: 7%;
}

.col-team {
  width: 8%;
}

.col-players {
  width: 36%;
}

.col-points {
  width: 8%;
}

.col-criteria {
  width: 8%;
}

.centered-cell {
  text-align: center;
}

.players-cell {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  white-space: normal;
  overflow-wrap: anywhere;
}

.criteria-cell {
  white-space: nowrap;
}

.goal-avg-cell {
  white-space: nowrap;
}

.player-name {
  line-height: 1.15;
}

.tie-indicator {
  margin-left: 0.55rem;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: clamp(0.62rem, 0.92vw, 0.88rem);
  font-weight: 700;
  letter-spacing: 0.01em;
  background: color-mix(in srgb, var(--color-primary) 16%, transparent);
  color: var(--color-primary-dark);
}
</style>
