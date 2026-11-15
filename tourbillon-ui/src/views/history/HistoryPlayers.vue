<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { playerKey, useHistoryPlayers } from '@/composables/useHistoryPlayers'

const { t } = useI18n()

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
  return t('history.mergedTooltip', { list: (player.spellings || []).join(', ') })
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

// Chart data: attendance (players / teams) per edition, ordered by year
const chartEditions = computed(() =>
  [...editions.value].sort((left, right) => String(left.year).localeCompare(String(right.year))),
)

const chartMix = computed(() => {
  const seen = new Set()
  return chartEditions.value.map((edition) => {
    let experienced = 0
    let beginners = 0
    const keys = new Set()

    for (const row of edition.players) {
      const key = playerKey(row.name)
      if (!key) continue
      keys.add(key)
      if (seen.has(key)) {
        experienced += 1
      } else {
        beginners += 1
      }
    }

    for (const key of keys) {
      seen.add(key)
    }

    return {
      key: edition.filename,
      year: edition.year,
      experienced,
      beginners,
      total: edition.players.length,
    }
  })
})

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

function centerX(index, total) {
  const step = 100 / total
  return (index + 0.5) * step
}

const chartDots = computed(() => {
  const rows = chartEditions.value
  return rows.map((edition, index) => ({
    key: edition.filename,
    year: edition.year,
    count: edition.players.length,
    teams: edition.nb_teams,
    experienced: chartMix.value[index]?.experienced ?? 0,
    beginners: chartMix.value[index]?.beginners ?? 0,
    x: centerX(index, rows.length || 1),
    y: pointY(edition.players.length),
  }))
})

const chartBars = computed(() => {
  const rows = chartEditions.value
  const visibleYears = Math.max(rows.length, 1)
  const width = Math.max(2.2, Math.min(5.5, 15 / visibleYears))

  return rows.map((edition, index) => {
    const mix = chartMix.value[index] ?? { experienced: 0, beginners: 0, total: 0 }
    const total = Math.max(Number(edition.players.length || 0), 1)
    const x = centerX(index, visibleYears) - width / 2
    const baseY = CHART_BOTTOM
    const totalTopY = pointY(total)
    const totalHeight = Math.max(0, baseY - totalTopY)

    const greenHeight = total > 0 && mix.beginners ? (mix.beginners / total) * totalHeight : 0
    const blueHeight = total > 0 && mix.experienced ? (mix.experienced / total) * totalHeight : 0
    const greenY = baseY - greenHeight
    const blueY = greenY - blueHeight

    return {
      key: `${edition.filename}-bar`,
      x,
      width,
      total,
      experienced: mix.experienced,
      beginners: mix.beginners,
      blueHeight,
      greenHeight,
      blueY,
      greenY,
    }
  })
})

const roundChartPeak = computed(() => {
  const values = chartEditions.value.map((edition) => Number(edition.nb_rounds ?? 0))
  return Math.max(1, ...values)
})

const roundChartStep = computed(() => {
  const target = roundChartPeak.value / 5
  const steps = [1, 2, 3, 4, 5, 10, 20, 25, 50, 100, 200]
  return steps.find((value) => value >= target) ?? 200
})

const roundChartMax = computed(() => {
  const step = roundChartStep.value
  return Math.max(step, Math.ceil(roundChartPeak.value / step) * step)
})

const roundChartTicks = computed(() => {
  const ticks = []
  for (let value = 0; value <= roundChartMax.value; value += roundChartStep.value) {
    ticks.push({ value, y: pointYFor(value, roundChartMax.value) })
  }
  return ticks.reverse()
})

function pointYFor(count, maxValue) {
  const ratio = maxValue > 0 ? count / maxValue : 0
  return CHART_BOTTOM - ratio * (CHART_BOTTOM - CHART_TOP)
}

const roundChartDots = computed(() => {
  const rows = chartEditions.value
  return rows.map((edition, index) => ({
    key: `${edition.filename}-rounds`,
    year: edition.year,
    count: Number(edition.nb_rounds ?? 0),
    x: centerX(index, rows.length || 1),
    y: pointYFor(Number(edition.nb_rounds ?? 0), roundChartMax.value),
  }))
})

const roundChartPoints = computed(() =>
  roundChartDots.value.map((dot) => `${dot.x.toFixed(2)},${dot.y.toFixed(2)}`).join(' '),
)

onMounted(() => {
  // No-op if the data is already loaded or a load is still in flight
  load()
})
</script>

<template>
  <section>
    <header class="head">
      <div>
        <h1>{{ t('history.title') }}</h1>
        <p class="muted">
          {{ t('history.aggregated', { loaded: loadedCount, total: tournaments.length }) }}
          &middot; {{ t('history.playersCount', { count: players.length }) }}
          &middot; {{ t('history.mergedCount', { count: mergedCount }) }}
        </p>
      </div>
      <span class="player-search-control">
        <input
          v-model="query"
          :placeholder="t('history.searchPlaceholder')"
        >
        <button
          v-if="query"
          type="button"
          class="player-search-clear"
          :aria-label="t('history.clearSearch')"
          :title="t('common.clear')"
          @click="clearQuery"
        >
          ×
        </button>
      </span>
    </header>

    <p
      v-if="error"
      class="muted"
    >
      {{ t('history.loadError') }}
    </p>

    <div
      v-if="chartEditions.length"
      class="charts-stack"
    >
      <div class="chart-card">
        <div class="chart-header">
          <h2>{{ t('history.chartTitle') }}</h2>
          <div class="chart-legend" aria-label="History player segments">
            <span class="chart-legend-item has-tooltip" tabindex="0">
              <span class="legend-swatch legend-experienced" />
              <span>{{ t('history.legendExperienced') }}</span>
              <span class="app-tooltip">{{ t('history.legendExperiencedHelp') }}</span>
            </span>
            <span class="chart-legend-item has-tooltip" tabindex="0">
              <span class="legend-swatch legend-beginners" />
              <span>{{ t('history.legendBeginners') }}</span>
              <span class="app-tooltip">{{ t('history.legendBeginnersHelp') }}</span>
            </span>
          </div>
        </div>
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
              <g v-for="bar in chartBars" :key="bar.key">
                <rect
                  class="chart-bar chart-bar-beginners"
                  :x="bar.x"
                  :y="bar.greenY"
                  :width="bar.width"
                  :height="bar.greenHeight"
                />
                <rect
                  class="chart-bar chart-bar-experienced"
                  :x="bar.x"
                  :y="bar.blueY"
                  :width="bar.width"
                  :height="bar.blueHeight"
                />
              </g>
            </svg>
            <button
              v-for="dot in chartDots"
              :key="dot.key"
              type="button"
              class="chart-dot has-tooltip"
              :style="{ left: `${dot.x}%`, top: `${dot.y}%` }"
              :aria-label="t('history.chartDotAria', { year: dot.year, count: dot.count })"
            >
              <span class="chart-tooltip app-tooltip">
                <strong>{{ dot.year }}</strong>
                <span>{{ t('history.chartPlayers', { count: dot.count }) }}</span>
                <span>{{ t('history.chartTeams', { count: dot.teams }) }}</span>
                <span>{{ t('history.chartMixTooltip', { experienced: dot.experienced, beginners: dot.beginners }) }}</span>
              </span>
            </button>
          </div>
        </div>
        <div class="chart-axis">
          <span
            v-for="dot in chartDots"
            :key="`label-${dot.key}`"
            class="chart-axis-item rotated-label"
          >
            <small>{{ dot.year }}</small>
          </span>
        </div>
      </div>

      <div class="chart-card rounds-card">
        <div class="chart-header">
          <h2>{{ t('history.roundsChartTitle') }}</h2>
        </div>
        <div class="chart-body">
          <div class="chart-scale">
            <span
              v-for="tick in roundChartTicks"
              :key="`round-tick-${tick.value}`"
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
                v-for="tick in roundChartTicks"
                :key="`round-grid-${tick.value}`"
                class="chart-grid"
                x1="0"
                :y1="tick.y"
                x2="100"
                :y2="tick.y"
              />
              <polyline
                class="chart-line chart-line-rounds"
                :points="roundChartPoints"
              />
            </svg>
            <button
              v-for="dot in roundChartDots"
              :key="dot.key"
              type="button"
              class="chart-dot chart-dot-rounds has-tooltip"
              :style="{ left: `${dot.x}%`, top: `${dot.y}%` }"
              :aria-label="t('history.roundsChartDotAria', { year: dot.year, count: dot.count })"
            >
              <span class="chart-tooltip app-tooltip">
                <strong>{{ dot.year }}</strong>
                <span>{{ t('history.roundsChartHint', { count: dot.count }) }}</span>
              </span>
            </button>
          </div>
        </div>
        <div class="chart-axis">
          <span
            v-for="dot in roundChartDots"
            :key="`round-label-${dot.key}`"
            class="chart-axis-item rotated-label"
          >
            <small>{{ dot.year }}</small>
          </span>
        </div>
      </div>
    </div>

    <table v-if="sortedPlayers.length">
      <thead>
        <tr>
          <th
            class="sortable"
            @click="sortBy('name')"
          >
            {{ t('common.player') }} <span class="sort-icon">{{ sortIcon('name') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('participations')"
          >
            {{ t('history.colParticipations') }} <span class="sort-icon">{{ sortIcon('participations') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('wins')"
          >
            {{ t('history.colTotalWins') }} <span class="sort-icon">{{ sortIcon('wins') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('points')"
          >
            {{ t('history.colTotalPoints') }} <span class="sort-icon">{{ sortIcon('points') }}</span>
          </th>
          <th
            class="num sortable"
            @click="sortBy('best_rank')"
          >
            {{ t('history.colBestRank') }} <span class="sort-icon">{{ sortIcon('best_rank') }}</span>
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
                {{ t('history.merged') }}
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
                {{ t('common.details') }}
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
      {{ t('history.empty') }}
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

.charts-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.chart-card {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 1rem 1.2rem;
  margin-bottom: 0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
}

.chart-card h2 {
  margin: 0;
  font-size: 1rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.8rem;
}

.chart-legend {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--color-text);
}

.chart-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  position: relative;
  cursor: help;
}

.chart-legend-item .app-tooltip {
  white-space: normal;
  width: 13rem;
  text-align: left;
  bottom: calc(100% + 0.55rem);
  left: 50%;
}

.chart-legend-item:hover .app-tooltip,
.chart-legend-item:focus .app-tooltip,
.chart-legend-item:focus-within .app-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, 0);
}

.legend-swatch {
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 0.2rem;
  display: inline-block;
}

.legend-experienced {
  background: rgba(124, 58, 237, 0.7);
}

.legend-beginners {
  background: rgba(22, 163, 74, 0.7);
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

.chart-bar {
  opacity: 0.9;
}

.chart-bar-experienced {
  fill: rgba(124, 58, 237, 0.8);
}

.chart-bar-beginners {
  fill: rgba(22, 163, 74, 0.8);
}

.chart-bar-rounds {
  fill: rgba(96, 165, 250, 0.8);
}

.chart-line {
  fill: none;
  stroke: var(--color-primary);
  stroke-width: 1.2;
  vector-effect: non-scaling-stroke;
}

.chart-line-rounds {
  stroke: var(--color-primary);
}

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

.chart-dot-rounds {
  background: var(--color-primary);
  border: 2px solid var(--color-surface);
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

.rotated-label {
  transform: rotate(-25deg);
  transform-origin: center;
  white-space: nowrap;
}

.chart-axis-item small {
  opacity: 0.65;
}
</style>
