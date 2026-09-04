<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { playerKey, useHistoryPlayers } from '@/composables/useHistoryPlayers'

// State lives at module scope: coming back from a player detail does not reload
const { players, tournaments, editions, loading, error, loadedCount, spellingCount, load } =
  useHistoryPlayers()

const query = ref('')

function clearQuery() {
  query.value = ''
}

// Duplicates folded together: distinct spellings minus the merged players
const mergedCount = computed(() => Math.max(0, spellingCount.value - players.value.length))

// A player is flagged as merged when several spellings were folded together
function isMerged(player) {
  return (player.spellings?.length ?? 0) > 1
}

function mergedTooltip(player) {
  return `Merged spellings: ${(player.spellings || []).join(', ')}`
}

const filteredPlayers = computed(() => {
  const text = query.value.trim()
  if (!text) {
    return players.value
  }
  // Search ignores case and accents, like the merge does
  const needle = playerKey(text)
  return players.value.filter((player) => playerKey(player.name).includes(needle))
})

// Sorting: click a column to toggle ascending / descending
const sortKey = ref('name')
const sortAsc = ref(true)

function sortBy(key) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    // Numeric columns are more useful descending first
    sortAsc.value = key === 'name'
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return ''
  return sortAsc.value ? '▲' : '▼'
}

const sortedPlayers = computed(() => {
  const rows = [...filteredPlayers.value]
  const key = sortKey.value
  const factor = sortAsc.value ? 1 : -1
  return rows.sort((left, right) => {
    if (key === 'name') {
      return left.name.localeCompare(right.name) * factor
    }
    // Missing ranks always sink to the bottom whatever the direction
    const leftValue = left[key]
    const rightValue = right[key]
    if (leftValue === null || leftValue === undefined) return 1
    if (rightValue === null || rightValue === undefined) return -1
    if (leftValue === rightValue) {
      return left.name.localeCompare(right.name)
    }
    return (leftValue - rightValue) * factor
  })
})

const progressPercent = computed(() => {
  if (!tournaments.value.length) return 0
  return Math.round((loadedCount.value / tournaments.value.length) * 100)
})

// Chart data: attendance (players / teams) per edition, ordered by year
const chartEditions = computed(() =>
  [...editions.value].sort((left, right) => String(left.year).localeCompare(String(right.year))),
)

const chartPeak = computed(() => {
  const values = chartEditions.value.map((edition) => edition.players.length)
  return Math.max(1, ...values)
})

// Pick a round step (10, 20, 50...) so the axis keeps ~5 readable ticks
const chartStep = computed(() => {
  const target = chartPeak.value / 5
  const steps = [5, 10, 20, 25, 50, 100, 200, 500, 1000]
  return steps.find((step) => step >= target) ?? 1000
})

// Round the top of the scale up to the next step boundary
const chartMax = computed(() => {
  const step = chartStep.value
  return Math.max(step, Math.ceil(chartPeak.value / step) * step)
})

const chartTicks = computed(() => {
  const ticks = []
  for (let value = 0; value <= chartMax.value; value += chartStep.value) {
    ticks.push({ value, y: pointY(value) })
  }
  return ticks.reverse()
})

// Keep a vertical margin so the dots are never clipped by the viewBox
const CHART_TOP = 8
const CHART_BOTTOM = 92

function pointX(index, total) {
  return total > 1 ? (index * 100) / (total - 1) : 50
}

function pointY(count) {
  const ratio = count / chartMax.value
  return CHART_BOTTOM - ratio * (CHART_BOTTOM - CHART_TOP)
}

const chartDots = computed(() => {
  const rows = chartEditions.value
  return rows.map((edition, index) => ({
    key: edition.filename,
    year: edition.year,
    count: edition.players.length,
    teams: edition.nb_teams,
    x: pointX(index, rows.length),
    y: pointY(edition.players.length),
  }))
})

const chartPoints = computed(() =>
  chartDots.value.map((dot) => `${dot.x.toFixed(2)},${dot.y.toFixed(2)}`).join(' '),
)

const chartArea = computed(() => {
  const dots = chartDots.value
  if (!dots.length) return ''
  const firstX = dots[0].x.toFixed(2)
  const lastX = dots[dots.length - 1].x.toFixed(2)
  return `${firstX},100 ${chartPoints.value} ${lastX},100`
})

onMounted(() => {
  // No-op if the data is already loaded or a load is still in flight
  load()
})
</script>

<template>
  <section>
    <header class="head">
      <div>
        <h1>Player History</h1>
        <p class="muted">
          {{ loadedCount }} / {{ tournaments.length }} tournaments aggregated
          &middot; {{ players.length }} players
          &middot; {{ mergedCount }} merged
        </p>
      </div>
      <span class="player-search-control">
        <input
          v-model="query"
          placeholder="Search player..."
        >
        <button
          v-if="query"
          type="button"
          class="player-search-clear"
          aria-label="Clear search"
          title="Clear"
          @click="clearQuery"
        >
          ×
        </button>
      </span>
    </header>

    <div
      v-if="loading"
      class="progress"
    >
      <div
        class="progress-bar"
        :style="{ width: `${progressPercent}%` }"
      />
    </div>

    <p
      v-if="error"
      class="muted"
    >
      Unable to load history data.
    </p>

    <div
      v-if="chartEditions.length"
      class="chart-card"
    >
      <h2>Attendance over the years</h2>
      <div class="chart-body">
        <div class="chart-scale">
          <span
            v-for="tick in chartTicks"
            :key="`tick-${tick.value}`"
            class="chart-scale-item"
            :style="{ top: `${tick.y}%` }"
          >{{ tick.value }}</span>
        </div>
        <div class="chart-plot">
          <svg
            class="chart"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
          >
            <line
              v-for="tick in chartTicks"
              :key="`grid-${tick.value}`"
              class="chart-grid"
              x1="0"
              :y1="tick.y"
              x2="100"
              :y2="tick.y"
            />
            <polygon
              class="chart-area"
              :points="chartArea"
            />
            <polyline
              class="chart-line"
              :points="chartPoints"
            />
          </svg>
          <button
            v-for="dot in chartDots"
            :key="dot.key"
            type="button"
            class="chart-dot has-tooltip"
            :style="{ left: `${dot.x}%`, top: `${dot.y}%` }"
            :aria-label="`${dot.year}: ${dot.count} players`"
          >
            <span class="chart-tooltip app-tooltip">
              <strong>{{ dot.year }}</strong>
              <span>{{ dot.count }} players</span>
              <span>{{ dot.teams }} teams</span>
            </span>
          </button>
        </div>
      </div>
      <div class="chart-axis">
        <span
          v-for="dot in chartDots"
          :key="`label-${dot.key}`"
          class="chart-axis-item"
        >
          <small>{{ dot.year }}</small>
        </span>
      </div>
    </div>

    <table v-if="sortedPlayers.length">
      <thead>
        <tr>
          <th
            class="sortable"
            @click="sortBy('name')"
          >
            Player <span class="sort-icon">{{ sortIcon('name') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('participations')"
          >
            Participations <span class="sort-icon">{{ sortIcon('participations') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('wins')"
          >
            Total wins <span class="sort-icon">{{ sortIcon('wins') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('points')"
          >
            Total points <span class="sort-icon">{{ sortIcon('points') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('best_rank')"
          >
            Best rank <span class="sort-icon">{{ sortIcon('best_rank') }}</span>
          </th>
          <th />
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="player in sortedPlayers"
          :key="player.name"
        >
          <td>
            <span class="player-cell">
              <span>{{ player.name }}</span>
              <span
                v-if="isMerged(player)"
                class="badge merged-badge has-tooltip"
              >
                merged
                <span class="app-tooltip">{{ mergedTooltip(player) }}</span>
              </span>
            </span>
          </td>
          <td class="num">
            {{ player.participations }}
          </td>
          <td class="num">
            {{ player.wins }}
          </td>
          <td class="num">
            {{ player.points }}
          </td>
          <td class="num">
            {{ player.best_rank ?? '—' }}
          </td>
          <td>
            <RouterLink :to="`/history/players/${encodeURIComponent(player.name)}`">
              <button class="secondary">
                Details
              </button>
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
    <p
      v-else-if="!loading"
      class="muted"
    >
      No player found.
    </p>
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

.player-search-control {
  position: relative;
  display: inline-flex;
  flex: 0 0 auto;
}

.player-search-control input {
  width: 100%;
  padding-right: 1.7rem;
}

.player-search-clear {
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

.player-search-clear:hover {
  color: var(--color-text);
}

.num {
  text-align: center;
}

.player-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.merged-badge {
  position: relative;
  font-size: 0.7rem;
  cursor: help;
}

.merged-badge .app-tooltip {
  white-space: nowrap;
  text-align: left;
}

.merged-badge:hover .app-tooltip,
.merged-badge:focus-within .app-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, 0);
}

.sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.sortable:hover {
  color: var(--color-primary);
}

.sort-icon {
  font-size: 0.7em;
  opacity: 0.8;
}

.progress {
  height: 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary) 14%, transparent);
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-bar {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.25s ease;
}

.chart-card {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 1rem 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
}

.chart-card h2 {
  margin: 0 0 0.8rem;
  font-size: 1rem;
}

.chart-body {
  display: flex;
  align-items: stretch;
  gap: 0.5rem;
}

.chart-scale {
  position: relative;
  width: 2.2rem;
  flex: none;
  height: 180px;
}

.chart-scale-item {
  position: absolute;
  right: 0;
  transform: translateY(-50%);
  font-size: 0.7rem;
  color: var(--color-text);
  opacity: 0.65;
}

.chart-plot {
  position: relative;
  height: 180px;
  flex: 1;
}

.chart-grid {
  stroke: color-mix(in srgb, var(--color-text) 12%, transparent);
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.chart {
  width: 100%;
  height: 100%;
  display: block;
}

.chart-area {
  fill: color-mix(in srgb, var(--color-primary) 14%, transparent);
}

.chart-line {
  fill: none;
  stroke: var(--color-primary);
  stroke-width: 1.2;
  vector-effect: non-scaling-stroke;
}

/* Dots live outside the SVG so they stay perfectly round */
.chart-dot {
  position: absolute;
  width: 12px;
  height: 12px;
  padding: 0;
  margin: 0;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: var(--color-primary);
  border: 2px solid var(--color-surface);
  cursor: help;
  transition: transform 0.12s ease;
}

.chart-dot:hover,
.chart-dot:focus-visible {
  transform: translate(-50%, -50%) scale(1.3);
}

.app-tooltip {
  position: absolute;
  bottom: calc(100% + 0.5rem);
  left: 50%;
  transform: translate(-50%, -2px);
  min-width: 120px;
  z-index: 20;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 8px;
  padding: 0.45rem 0.6rem;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
  font-size: 0.78rem;
  line-height: 1.3;
  text-align: center;
  transition: opacity 0.12s ease, transform 0.12s ease, visibility 0.12s ease;
}

.app-tooltip span,
.app-tooltip strong {
  display: block;
}

.chart-dot.has-tooltip:hover .app-tooltip,
.chart-dot.has-tooltip:focus-within .app-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, 0);
}

.chart-axis {
  display: flex;
  justify-content: space-between;
  gap: 0.3rem;
  margin-top: 0.5rem;
  margin-left: 2.7rem;
}

.chart-axis-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.75rem;
  color: var(--color-text);
}

.chart-axis-item small {
  opacity: 0.65;
}
</style>
