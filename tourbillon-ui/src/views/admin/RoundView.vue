<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { api } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'

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

async function saveMatch(roundNumber, index, match) {
  const key = matchPointsKey(roundNumber, index, match)
  const points = pointsByMatch.value[key] || initPoints(roundNumber, index, match)
  try {
    await api.setMatchResult(roundNumber, index + 1, points)
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

async function deleteSelectedRound() {
  if (!currentRound.value) return
  const number = currentRound.value.number
  const ok = window.confirm(`Delete round ${number}?`)
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
      <h1>Round</h1>
    </header>

    <div class="round-controls">
      <div class="round-timeline-wrap">
        <button
          v-if="canScrollLeft"
          type="button"
          class="timeline-arrow left"
          aria-label="Scroll rounds left"
          @click="scrollTimeline(-1)"
        >
          ‹
        </button>

        <div
          ref="timelineRef"
          class="round-timeline"
          :class="{ 'has-left': canScrollLeft, 'has-right': canScrollRight }"
          aria-label="Rounds timeline"
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
            Round {{ round.number }}
          </button>
          <button
            type="button"
            class="round-pill new-round-pill"
            :disabled="!canCreateRound"
            @click="openDrawPopup"
          >
            New
          </button>
        </div>

        <button
          v-if="canScrollRight"
          type="button"
          class="timeline-arrow right"
          aria-label="Scroll rounds right"
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
        <span class="round-title-main">Round {{ currentRound.number }} <span class="badge">{{ currentRound.status }}</span></span>
        <label
          class="round-search"
          for="round-team-filter"
        >
          <span>Team</span>
          <span class="round-search-control">
            <input
              id="round-team-filter"
              v-model="teamFilterInput"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              placeholder="e.g. 12"
            >
            <button
              v-if="teamFilterInput"
              type="button"
              class="round-search-clear"
              aria-label="Clear team filter"
              title="Clear"
              @click="clearTeamFilter"
            >
              ×
            </button>
          </span>
        </label>
        <button
          class="danger-outline"
          @click="deleteSelectedRound"
        >
          Delete
        </button>
      </h3>
      <p
        v-if="currentRound.byes?.length"
        class="status-row"
      >
        <span class="status-row-label">Byes:</span>
        <span class="status-row-list">
          <span
            v-for="teamId in currentRound.byes"
            :key="`round-bye-${teamId}`"
            class="status-badge status-bye"
          >
            Team {{ teamId }}
          </span>
        </span>
      </p>

      <table>
        <thead>
          <tr>
            <th>Location</th>
            <th>Results</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="{ match, index } in filteredRoundMatches"
            :key="`${currentRound.number}-${index}`"
          >
            <td>{{ match.location ?? '—' }}</td>
            <td>
              <div class="results-lines">
                <div
                  v-for="team in match.teams"
                  :key="team"
                  class="result-line"
                >
                  <span class="team-chip">
                    <span class="team-chip-label">Team</span>
                    <span class="team-chip-number">{{ team }}</span>
                  </span>
                  <input
                    v-model.number="initPoints(currentRound.number, index, match)[team]"
                    type="number"
                    min="0"
                  >
                </div>
              </div>
            </td>
            <td>
              <span class="badge">{{ match.finished ? 'finished' : 'in_progress' }}</span>
            </td>
            <td>
              <button
                class="secondary action-btn"
                :disabled="!hasMatchChanges(currentRound.number, index, match)"
                @click="saveMatch(currentRound.number, index, match)"
              >
                Save
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
      No round available yet.
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

.result-line input {
  width: 80px;
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
