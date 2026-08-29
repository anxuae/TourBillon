<script setup>
import { computed, inject, nextTick, onMounted, ref, watch } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useEvents } from '@/events/eventsClient'
import { useRankingColumns } from '@/composables/useRankingColumns'

const rankings = ref([])
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

async function refreshRankingOptions() {
  await rankingColumns.refreshRankingOptions()
}

const { subscribe } = useEvents()

for (const type of ['score_updated', 'round_created', 'round_deleted', 'teams_updated']) {
  subscribe(type, () => refreshRankings().catch(() => {}))
}
subscribe('settings_updated', () => {
  Promise.all([refreshRankings(), refreshRankingOptions()]).catch(() => {})
})
subscribe('tournament_changed', () => {
  Promise.all([refreshRankings(), refreshRankingOptions()]).catch(() => {})
})


onMounted(async () => {
  await Promise.all([refreshRankings(), refreshRankingOptions()])
})


const allRankings = computed(() => rankings.value)
const rankingColumns = useRankingColumns(rankings)
const { isTieRank, showWins, showJoker, showBuchholz, showGoalAvg } = rankingColumns

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
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team</th>
          <th v-if="showWins">
            Wins
          </th>
          <th>Points</th>
          <th v-if="showJoker">
            Joker
          </th>
          <th v-if="showBuchholz">
            Buchholz
          </th>
          <th v-if="showGoalAvg">
            Goal Avg
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in visibleRankings"
          :key="row.team"
        >
          <td>
            <span>{{ row.rank }}</span>
            <span
              v-if="isTieRank(row.rank)"
              class="tie-indicator"
              aria-label="Tied rank"
              title="Tied rank"
            >⇄</span>
          </td>
          <td>{{ row.team }}</td>
          <td v-if="showWins">
            {{ row.wins }}
          </td>
          <td>{{ row.points }}</td>
          <td v-if="showJoker">
            {{ row.joker }}
          </td>
          <td v-if="showBuchholz">
            {{ row.buchholz }}
          </td>
          <td v-if="showGoalAvg">
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
