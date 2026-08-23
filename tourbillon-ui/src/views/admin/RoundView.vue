<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { api, openDrawSocket, pushApiError } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { rounds, tournament, draws } = storeToRefs(store)

const selectedRound = ref(null)
const pointsByMatch = ref({})
const timelineRef = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const drawModalOpen = ref(false)
const selectedAlgorithm = ref('')
const maxDisparity = ref(1)
const allowRematch = ref(false)
const randomSeed = ref('')
const drawProgress = ref(0)
const drawMessage = ref('Idle')
const drawRunning = ref(false)

let drawSocket = null

const currentRound = computed(() => {
  if (!rounds.value.length) {
    return null
  }
  const number = Number(selectedRound.value || rounds.value[rounds.value.length - 1].number)
  return rounds.value.find((item) => item.number === number) || null
})

onMounted(async () => {
  await Promise.all([store.refreshRounds(), store.refreshDraws()])
  if (rounds.value.length) {
    selectedRound.value = rounds.value[rounds.value.length - 1].number
  }
  if (draws.value.length && !selectedAlgorithm.value) {
    selectedAlgorithm.value = draws.value[0].name
  }
  await nextTick()
  updateTimelineOverflow()
  window.addEventListener('resize', updateTimelineOverflow)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateTimelineOverflow)
  closeDrawSocket()
})

watch(
  () => rounds.value.length,
  async () => {
    await nextTick()
    updateTimelineOverflow()
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

async function saveMatch(roundNumber, index, match) {
  const key = matchPointsKey(roundNumber, index, match)
  const points = pointsByMatch.value[key] || initPoints(roundNumber, index, match)
  try {
    await api.setMatchResult(roundNumber, index + 1, points)
    await store.refreshRounds()
    await store.refreshRankings(roundNumber)
  } catch {
  }
}

const canCreateRound = computed(() => {
  if (!tournament.value) return false
  return tournament.value.nb_teams >= tournament.value.teams_by_match
})

function openAddRoundModal() {
  drawProgress.value = 0
  drawMessage.value = 'Idle'
  if (draws.value.length && !selectedAlgorithm.value) {
    selectedAlgorithm.value = draws.value[0].name
  }
  drawModalOpen.value = true
}

function closeAddRoundModal() {
  if (drawRunning.value) return
  drawModalOpen.value = false
}

function closeDrawSocket() {
  if (drawSocket) {
    drawSocket.close()
    drawSocket = null
  }
}

function connectDrawSocket() {
  closeDrawSocket()
  drawSocket = openDrawSocket()
  drawSocket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === 'draw_progress') {
        drawProgress.value = Math.round(payload.percent || 0)
        drawMessage.value = payload.message || 'Running'
      } else if (payload.type === 'draw_error') {
        pushApiError(payload.message || 'Draw error')
      } else if (payload.type === 'round_created') {
        drawProgress.value = 100
        drawMessage.value = `Round ${payload.round} created`
      }
    } catch {
    }
  }
}

async function addNewRound() {
  drawProgress.value = 0
  drawMessage.value = 'Starting draw...'
  drawRunning.value = true
  connectDrawSocket()

  const config = {}
  if (selectedAlgorithm.value !== 'random') {
    config.max_disparity = Number(maxDisparity.value)
    config.allow_rematch = allowRematch.value
  }
  if (randomSeed.value.trim()) {
    config.seed = Number(randomSeed.value)
  }

  try {
    await api.createRound({
      algorithm: selectedAlgorithm.value || null,
      config,
      bye_teams: [],
    })
    await Promise.all([
      store.refreshRounds(),
      store.refreshRankings(),
      store.refreshTournament(),
    ])
    if (rounds.value.length) {
      selectedRound.value = rounds.value[rounds.value.length - 1].number
    }
    drawModalOpen.value = false
  } catch {
  } finally {
    drawRunning.value = false
    closeDrawSocket()
  }
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
  }
}
</script>

<template>
  <section>
    <header class="head">
      <h1>Round</h1>
    </header>

    <div class="round-controls">
      <div v-if="rounds.length" class="round-timeline-wrap">
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

      <button class="add-round-btn" :disabled="!canCreateRound" @click="openAddRoundModal">
        Add new round
      </button>
    </div>

    <div v-if="currentRound" class="card">
      <h3 class="round-title">
        <span>Round {{ currentRound.number }} <span class="badge">{{ currentRound.status }}</span></span>
        <button class="danger" @click="deleteSelectedRound">Delete round</button>
      </h3>
      <p v-if="currentRound.byes?.length" class="muted">Byes: {{ currentRound.byes.join(', ') }}</p>

      <table>
        <thead>
          <tr>
            <th>Location</th>
            <th>Teams</th>
            <th>Points</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(match, index) in currentRound.matches" :key="`${currentRound.number}-${index}`">
            <td>{{ match.location ?? '—' }}</td>
            <td>{{ match.teams.join(' vs ') }}</td>
            <td>
              <div class="points">
                <label v-for="team in match.teams" :key="team">
                  T{{ team }}
                  <input v-model.number="initPoints(currentRound.number, index, match)[team]" type="number" min="0" />
                </label>
              </div>
            </td>
            <td>
              <span class="badge">{{ match.finished ? 'finished' : 'in_progress' }}</span>
            </td>
            <td>
              <button class="secondary" @click="saveMatch(currentRound.number, index, match)">Save</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="muted">No round available yet.</p>

    <div v-if="drawModalOpen" class="overlay" @click.self="closeAddRoundModal">
      <div class="modal card" role="dialog" aria-modal="true" aria-label="Add new round">
        <h2>Add new round</h2>

        <div class="draw-grid">
          <label>
            Algorithm
            <select v-model="selectedAlgorithm" :disabled="drawRunning">
              <option v-for="draw in draws" :key="draw.name" :value="draw.name">
                {{ draw.name }}
              </option>
            </select>
          </label>

          <label v-if="selectedAlgorithm !== 'random'">
            Max disparity
            <input v-model.number="maxDisparity" type="number" min="0" :disabled="drawRunning" />
          </label>

          <label>
            Seed (optional)
            <input v-model="randomSeed" type="number" placeholder="42" :disabled="drawRunning" />
          </label>

          <label v-if="selectedAlgorithm !== 'random'" class="check">
            <input v-model="allowRematch" type="checkbox" :disabled="drawRunning" />
            Allow rematch
          </label>
        </div>

        <div class="progress-card">
          <div class="progress-head">
            <strong>Progress</strong>
            <span>{{ drawProgress }}%</span>
          </div>
          <div class="bar">
            <div class="fill" :style="{ width: `${drawProgress}%` }"></div>
          </div>
          <p class="muted">{{ drawMessage }}</p>
        </div>

        <div class="modal-actions">
          <button class="secondary" :disabled="drawRunning" @click="closeAddRoundModal">Cancel</button>
          <button :disabled="drawRunning || !tournament || !selectedAlgorithm" @click="addNewRound">
            {{ drawRunning ? 'Running…' : 'Run draw' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
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
  justify-content: space-between;
  gap: 0.75rem;
}

.danger {
  background: transparent;
  border: 1px solid #c62828;
  color: #c62828;
}

.danger:hover {
  background: rgba(198, 40, 40, 0.08);
}

.points {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.points label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
}

.points input {
  width: 70px;
}

.round-timeline {
  position: relative;
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  padding: 0.25rem 0.1rem 0.6rem;
  margin-bottom: 0;
  scrollbar-width: thin;
  flex: 1 1 auto;
  min-width: 0;
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
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.add-round-btn {
  flex: 0 0 auto;
}

.round-timeline.has-left::before,
.round-timeline.has-right::after {
  content: '';
  position: sticky;
  top: 0;
  width: 28px;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.round-timeline.has-left::before {
  left: 0;
  background: linear-gradient(to right, var(--color-bg), transparent);
}

.round-timeline.has-right::after {
  right: 0;
  margin-left: auto;
  background: linear-gradient(to left, var(--color-bg), transparent);
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
  flex: 0 0 auto;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: transparent;
  color: var(--color-muted);
  font: inherit;
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

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: min(92vw, 560px);
  max-height: 85vh;
  overflow-y: auto;
  padding: 1.25rem;
}

.modal h2 {
  margin-top: 0;
}

.draw-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
}

.draw-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
}

.draw-grid label.check {
  flex-direction: row;
  align-items: center;
  margin-top: 1.8rem;
}

.progress-card {
  margin-top: 1rem;
}

.progress-head {
  display: flex;
  justify-content: space-between;
}

.bar {
  width: 100%;
  height: 12px;
  border-radius: 999px;
  background: #e8ecf5;
  overflow: hidden;
  margin: 0.6rem 0;
}

.fill {
  height: 100%;
  background: linear-gradient(90deg, #2c6bed, #6ea8ff);
  transition: width 0.2s ease;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
