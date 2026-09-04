<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { api } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'
import { useStatusLabel } from '@/composables/useStatusLabel'

const { t } = useI18n()
const { statusLabel } = useStatusLabel()
const store = useTournamentStore()
const { rounds, tournament } = storeToRefs(store)
const router = useRouter()
const route = useRoute()

const selectedRound = ref(null)
const pointsByMatch = ref({})
const timelineRef = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const teamFilterInput = ref('')

function requestedRoundNumber() {
  const raw = route.query?.round
  const value = Array.isArray(raw) ? raw[0] : raw
  const number = Number(value)
  if (!Number.isInteger(number) || number <= 0) {
    return null
  }
  return number
}

function selectRequestedOrLatestRound() {
  if (!rounds.value.length) {
    selectedRound.value = null
    return
  }

  const requested = requestedRoundNumber()
  if (requested && rounds.value.some((item) => item.number === requested)) {
    selectedRound.value = requested
    return
  }

  selectedRound.value = rounds.value[rounds.value.length - 1].number
}

const currentRound = computed(() => {
  if (!rounds.value.length) {
    return null
  }
  const number = Number(selectedRound.value || rounds.value[rounds.value.length - 1].number)
  return rounds.value.find((item) => item.number === number) || null
})

const sortedRoundMatches = computed(() => {
  if (!currentRound.value) {
    return []
  }
  return currentRound.value.matches
    .map((match, index) => ({ match, index }))
    .sort((left, right) => {
      const leftLocation = left.match.location
      const rightLocation = right.match.location
      if (leftLocation == null && rightLocation == null) {
        return left.index - right.index
      }
      if (leftLocation == null) {
        return 1
      }
      if (rightLocation == null) {
        return -1
      }
      return leftLocation - rightLocation
    })
})

const filteredRoundMatches = computed(() => {
  const raw = String(teamFilterInput.value ?? '').trim()
  if (!raw) {
    return sortedRoundMatches.value
  }
  const teamNumber = Number(raw)
  if (!Number.isInteger(teamNumber) || teamNumber <= 0) {
    return []
  }
  return sortedRoundMatches.value.filter(({ match }) => match.teams.includes(teamNumber))
})

onMounted(async () => {
  if (!rounds.value.length) {
    await store.refreshRounds()
  }
  selectRequestedOrLatestRound()
  await nextTick()
  updateTimelineOverflow()
  window.addEventListener('resize', updateTimelineOverflow)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateTimelineOverflow)
})

watch(
  () => rounds.value.length,
  async (newLength, oldLength) => {
    if (newLength > 0 && newLength !== oldLength) {
      selectRequestedOrLatestRound()
    }
    await nextTick()
    updateTimelineOverflow()
  },
)

watch(
  () => route.query?.round,
  () => {
    selectRequestedOrLatestRound()
  },
)

function updateTimelineOverflow() {
  const el = timelineRef.value
  if (!el) {
    canScrollLeft.value = false
    canScrollRight.value = false
    return
  }
  canScrollLeft.value = el.scrollLeft > 2
  canScrollRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 2
}

function scrollTimeline(direction) {
  const el = timelineRef.value
  if (!el) return
  const amount = Math.max(140, Math.floor(el.clientWidth * 0.75))
  el.scrollBy({ left: direction * amount, behavior: 'smooth' })
}

function clearTeamFilter() {
  teamFilterInput.value = ''
}

function matchPointsKey(roundNumber, matchIndex, match) {
  return `${roundNumber}:${matchIndex}:${match.location ?? match.teams.join('-')}`
}

function initPoints(roundNumber, matchIndex, match) {
  const key = matchPointsKey(roundNumber, matchIndex, match)
  if (!pointsByMatch.value[key]) {
    const data = {}
    for (const team of match.teams) {
      data[team] = match.points[team] ?? 0
    }
    pointsByMatch.value[key] = data
  }
  return pointsByMatch.value[key]
}

function hasMatchChanges(roundNumber, matchIndex, match) {
  const key = matchPointsKey(roundNumber, matchIndex, match)
  const editedPoints = pointsByMatch.value[key]
  if (!editedPoints) {
    return false
  }
  for (const team of match.teams) {
    const initial = Number(match.points[team] ?? 0)
    const edited = Number(editedPoints[team] ?? 0)
    if (edited !== initial) {
      return true
    }
  }
  return false
}

function getMatchResultStatus(teamPoints, allTeamsPoints) {
  if (!allTeamsPoints || allTeamsPoints.length === 0) return null
  const maxPoints = Math.max(...allTeamsPoints)
  return teamPoints === maxPoints ? 'won' : 'lost'
}

async function saveMatch(roundNumber, index, match) {
  const key = matchPointsKey(roundNumber, index, match)
  const points = pointsByMatch.value[key] || initPoints(roundNumber, index, match)
  
  // Validate points: convert NaN and null to 0, ensure all values are integers
  const validatedPoints = {}
  for (const [teamId, value] of Object.entries(points)) {
    const numValue = Number(value)
    validatedPoints[parseInt(teamId)] = isNaN(numValue) ? 0 : Math.max(0, Math.floor(numValue))
  }
  
  try {
    await api.setMatchResult(roundNumber, index + 1, validatedPoints)
    await store.refreshRounds()
    await store.refreshRankings(roundNumber)
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

const canCreateRound = computed(() => {
  if (!tournament.value) return false
  if (tournament.value.nb_teams < tournament.value.teams_by_match) return false
  if (!rounds.value.length) return true

  const lastRound = rounds.value[rounds.value.length - 1]
  return lastRound.status === 'finished' || lastRound.status === 'complete'
})

function openDrawPopup() {
  if (!canCreateRound.value) {
    return
  }
  router.push({ name: 'admin-draw' })
}

function printRound() {
  window.print()
}

async function deleteSelectedRound() {
  if (!currentRound.value) return
  const number = currentRound.value.number
  const ok = window.confirm(t('round.confirmDelete', { number }))
  if (!ok) return

  try {
    await api.deleteRound(number)
    await Promise.all([
      store.refreshRounds(),
      store.refreshRankings(),
      store.refreshTournament(),
    ])
    if (rounds.value.length) {
      selectedRound.value = rounds.value[rounds.value.length - 1].number
    } else {
      selectedRound.value = null
    }
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}
</script>

<template>
  <section>
    <header class="head">
      <h1>{{ t('round.title') }}</h1>
    </header>

    <div class="round-controls">
      <div class="round-timeline-wrap">
        <button
          v-if="canScrollLeft"
          type="button"
          class="timeline-arrow left"
          :aria-label="t('round.scrollLeft')"
          @click="scrollTimeline(-1)"
        >
          ‹
        </button>

        <div
          ref="timelineRef"
          class="round-timeline"
          :class="{ 'has-left': canScrollLeft, 'has-right': canScrollRight }"
          :aria-label="t('round.timeline')"
          @scroll="updateTimelineOverflow"
        >
          <button
            v-for="round in rounds"
            :key="round.number"
            type="button"
            class="round-pill"
            :class="{ active: currentRound && currentRound.number === round.number }"
            @click="selectedRound = round.number"
          >
            {{ t('round.roundNumber', { number: round.number }) }}
          </button>
          <button
            type="button"
            class="round-pill new-round-pill"
            :disabled="!canCreateRound"
            @click="openDrawPopup"
          >
            {{ t('round.new') }}
          </button>
        </div>

        <button
          v-if="canScrollRight"
          type="button"
          class="timeline-arrow right"
          :aria-label="t('round.scrollRight')"
          @click="scrollTimeline(1)"
        >
          ›
        </button>
      </div>
    </div>

    <div
      v-if="currentRound"
      class="card"
    >
      <h3 class="round-title">
        <span class="round-title-main">{{ t('common.round') }} {{ currentRound.number }} <span class="badge">{{ statusLabel(currentRound.status) }}</span></span>
        <label
          class="round-search"
          for="round-team-filter"
        >
          <span>{{ t('common.team') }}</span>
          <span class="round-search-control">
            <input
              id="round-team-filter"
              v-model="teamFilterInput"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              :placeholder="t('round.filterPlaceholder')"
            >
            <button
              v-if="teamFilterInput"
              type="button"
              class="round-search-clear"
              :aria-label="t('round.clearFilter')"
              :title="t('common.clear')"
              @click="clearTeamFilter"
            >
              ×
            </button>
          </span>
        </label>
        <button
          class="print-btn"
          :title="t('round.printTitle')"
          @click="printRound"
        >
          {{ t('common.print') }}
        </button>
        <button
          class="danger-outline"
          @click="deleteSelectedRound"
        >
          {{ t('common.delete') }}
        </button>
      </h3>
      <p
        v-if="currentRound.byes?.length"
        class="status-row"
      >
        <span class="status-row-label">{{ t('round.byesLabel') }}</span>
        <span class="status-row-list">
          <span
            v-for="teamId in currentRound.byes"
            :key="`round-bye-${teamId}`"
            class="status-badge status-bye"
          >
            {{ t('round.teamNumber', { number: teamId }) }}
          </span>
        </span>
      </p>

      <table>
        <thead>
          <tr>
            <th>{{ t('common.location') }}</th>
            <th>{{ t('round.results') }}</th>
            <th>{{ t('common.status') }}</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="{ match, index } in filteredRoundMatches"
            :key="`${currentRound.number}-${index}`"
          >
            <td>{{ match.location ?? t('common.none') }}</td>
            <td>
              <div class="results-lines">
                <div
                  v-for="team in match.teams"
                  :key="team"
                  class="result-line"
                >
                  <span class="team-chip">
                    <span class="team-chip-label">{{ t('common.team') }}</span>
                    <span class="team-chip-number">{{ team }}</span>
                  </span>
                  <input
                    v-model.number="initPoints(currentRound.number, index, match)[team]"
                    type="number"
                    min="0"
                    class="points-input"
                    :class="initPoints(currentRound.number, index, match)[team] ? `input-${getMatchResultStatus(initPoints(currentRound.number, index, match)[team], match.teams.map(t => initPoints(currentRound.number, index, match)[t]))}` : 'input-empty'"
                  >
                </div>
              </div>
            </td>
            <td>
              <span class="badge">{{ statusLabel(match.finished ? 'finished' : 'in_progress') }}</span>
            </td>
            <td>
              <button
                class="secondary action-btn"
                :disabled="!hasMatchChanges(currentRound.number, index, match)"
                @click="saveMatch(currentRound.number, index, match)"
              >
                {{ t('common.save') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p
      v-else
      class="muted"
    >
      {{ t('round.empty') }}
    </p>
  </section>
</template>

<style scoped>
section {
  --round-action-width: 9.2rem;
  --round-pill-width: 6.8rem;
}

.head {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.head h1 {
  margin: 0;
}

.round-title {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.round-title-main {
  margin-right: auto;
}

.round-search {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
}

.round-search-control {
  position: relative;
  display: inline-flex;
  width: var(--round-action-width);
}

.round-search input {
  width: 100%;
  padding-right: 1.7rem;
}

.round-title .danger-outline {
  width: var(--round-action-width);
}

.round-title .print-btn {
  width: var(--round-action-width);
}

/* Printing keeps the round table only: controls and actions are dropped */
@media print {
  .head,
  .round-controls,
  .round-search,
  .print-btn,
  .danger-outline,
  .action-btn {
    display: none !important;
  }

  .card {
    border: none;
    box-shadow: none;
    padding: 0;
  }

  .points-input {
    border: 1px solid #000 !important;
    background: transparent !important;
    color: #000 !important;
  }
}

.action-btn {
  width: var(--round-action-width);
}

.round-search-clear {
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

.round-search-clear:hover {
  color: var(--color-text);
}

.results-lines {
  display: grid;
  grid-template-columns: repeat(2, minmax(140px, 1fr));
  gap: 0.4rem;
}

.result-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.team-chip {
  min-width: 4.6rem;
  display: inline-grid;
  grid-template-columns: auto 2ch;
  align-items: center;
  column-gap: 0.35rem;
  font-weight: 600;
  font-size: 0.85rem;
  font-variant-numeric: tabular-nums;
}

.team-chip-number {
  text-align: right;
}

.points-input {
  width: 80px !important;
  font-weight: 600 !important;
}

.points-input.input-won {
  background: var(--status-won-bg) !important;
  color: var(--status-won-fg) !important;
  border-color: var(--status-won-border) !important;
}

.points-input.input-lost {
  background: var(--status-lost-bg) !important;
  color: var(--status-lost-fg) !important;
  border-color: var(--status-lost-border) !important;
}

.points-input.input-empty {
  background: var(--color-surface) !important;
  color: var(--color-text) !important;
  border-color: var(--color-border) !important;
}

.status-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.status-row-label {
  color: var(--color-muted);
}

.status-row-list {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
}

@media (max-width: 980px) {
  .results-lines {
    grid-template-columns: 1fr;
  }
}

.round-timeline {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  padding: 0.25rem 0.1rem;
  margin-bottom: 0;
  scrollbar-width: thin;
  flex: 1 1 auto;
  min-width: 0;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 0.1rem;
}

.round-timeline-wrap {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex: 1 1 auto;
  min-width: 0;
}

.round-controls {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.timeline-arrow {
  position: static;
  transform: none;
  z-index: 0;
  width: 1.9rem;
  height: 1.9rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  flex: 0 0 auto;
}

.timeline-arrow.left {
  margin-right: 0.05rem;
}

.timeline-arrow.right {
  margin-left: 0.05rem;
}

.timeline-arrow:hover {
  border-color: var(--color-primary);
}

.round-pill {
  flex: 0 0 var(--round-pill-width);
  width: var(--round-pill-width);
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: transparent;
  color: var(--color-muted);
  font: inherit;
  text-align: center;
  scroll-snap-align: start;
  cursor: pointer;
}

.round-pill:hover {
  border-color: var(--color-primary);
  color: var(--color-text);
}

.round-pill.active {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 14%, transparent);
  color: var(--color-text);
  font-weight: 600;
}

.new-round-pill {
  border-style: dashed;
  font-weight: 600;
}
</style>
