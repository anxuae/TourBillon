<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { api, openDrawSocket, pushApiError } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'
import DrawBenchPanel from '@/components/DrawBenchPanel.vue'
import DrawMatchCard from '@/components/DrawMatchCard.vue'

const props = defineProps({
  showHeader: {
    type: Boolean,
    default: true,
  },
})
const emit = defineEmits(['cancel', 'issues-change', 'created'])

const store = useTournamentStore()
const { draws, tournament, teams } = storeToRefs(store)
const router = useRouter()

const selectedAlgorithm = ref('')

const progress = ref(0)
const message = ref('Idle')
const running = ref(false)
const stage = ref('config')
const draft = ref(null)
const swapSelection = ref([])
const dragged = ref(null)
const focusedMatchId = ref(null)
const committing = ref(false)
const hideFullMatches = ref(false)

let socket = null

onMounted(async () => {
  const tasks = []
  if (!draws.value.length) {
    tasks.push(store.refreshDraws())
  }
  if (!teams.value.length) {
    tasks.push(store.refreshTeams())
  }
  if (tasks.length) {
    await Promise.all(tasks)
  }
  if (draws.value.length && !selectedAlgorithm.value) {
    selectedAlgorithm.value = draws.value[0].name
  }
})

watch(
  () => tournament.value?.filename ?? null,
  (nextFilename, previousFilename) => {
    if (nextFilename !== previousFilename) {
      resetDrawState()
    }
  },
)

function connectSocket() {
  if (socket) {
    socket.close()
  }
  socket = openDrawSocket()
  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === 'draw_progress') {
        progress.value = Math.round(payload.percent || 0)
        message.value = payload.message || 'Running'
      } else if (payload.type === 'draw_error') {
        pushApiError(payload.message || 'Draw error')
        running.value = false
      } else if (payload.type === 'draw_preview_ready') {
        progress.value = 100
        message.value = 'Preview ready'
      } else if (payload.type === 'round_created') {
        if (committing.value) {
          message.value = `Round ${payload.round} created`
        }
      }
    } catch {
      // Ignore malformed events.
    }
  }
}

async function runDraw() {
  progress.value = 0
  message.value = 'Generating preview...'
  running.value = true
  connectSocket()

  try {
    const preview = await api.runDraw({
      algorithm: selectedAlgorithm.value || null,
      bye_teams: [],
    })
    draft.value = JSON.parse(JSON.stringify(preview))
    stage.value = 'review'
    message.value = 'Preview generated'
    progress.value = 100
  } catch {
    running.value = false
  } finally {
    running.value = false
  }
}

function teamMetricsMap() {
  const map = {}
  if (!draft.value) return map
  for (const match of draft.value.matches) {
    for (const metric of match.team_metrics || []) {
      map[metric.team] = metric
    }
  }
  return map
}

const metricsByTeam = computed(() => teamMetricsMap())

const groupedMatches = computed(() => {
  if (!draft.value) return []
  const groups = new Map()
  for (const match of draft.value.matches) {
    const key = match.group_wins
    if (!groups.has(key)) {
      groups.set(key, [])
    }
    groups.get(key).push(match)
  }
  return [...groups.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([wins, matches]) => ({ wins, matches }))
})

function hasEmptySlot(match) {
  return (match?.teams || []).some((teamId) => teamId == null)
}

const displayedGroupedMatches = computed(() => {
  if (!hideFullMatches.value) {
    return groupedMatches.value
  }

  return groupedMatches.value
    .map((group) => ({
      wins: group.wins,
      matches: group.matches.filter((match) => hasEmptySlot(match)),
    }))
    .filter((group) => group.matches.length > 0)
})

function groupToneClass(index) {
  return `group-tone-${index % 6}`
}

function slotKey(matchId, index) {
  return `${matchId}:${index}`
}

function findSlot(matchId, index) {
  const match = draft.value.matches.find((item) => item.id === matchId)
  if (!match) return null
  return { match, index }
}

function selectSlot(matchId, index) {
  const slot = findSlot(matchId, index)
  if (!slot || slot.match.teams[index] == null) return

  const key = slotKey(matchId, index)
  if (swapSelection.value.includes(key)) {
    swapSelection.value = swapSelection.value.filter((value) => value !== key)
    return
  }

  if (swapSelection.value.length === 2) {
    swapSelection.value = []
  }

  swapSelection.value.push(key)

  if (swapSelection.value.length === 2) {
    const [a, b] = swapSelection.value
    const [matchA, indexA] = a.split(':')
    const [matchB, indexB] = b.split(':')
    swapTeams(matchA, Number(indexA), matchB, Number(indexB))
    swapSelection.value = []
  }
}

function swapTeams(matchAId, indexA, matchBId, indexB) {
  const slotA = findSlot(matchAId, indexA)
  const slotB = findSlot(matchBId, indexB)
  if (!slotA || !slotB) return

  const temp = slotA.match.teams[indexA]
  slotA.match.teams[indexA] = slotB.match.teams[indexB]
  slotB.match.teams[indexB] = temp
}

function removeFromList(listRef, teamId) {
  const index = listRef.indexOf(teamId)
  if (index >= 0) listRef.splice(index, 1)
}

function matchLabel(matchId) {
  const text = String(matchId ?? '').trim()
  const compact = text.match(/^m(\d+)$/i)
  if (compact) {
    return `Match ${compact[1]}`
  }
  return `Match ${text}`
}

function liveMetricsForMatch(match) {
  const values = []
  for (const teamId of match?.teams || []) {
    if (teamId == null) continue
    const metric = metricsByTeam.value[teamId]
    if (metric) {
      values.push(metric)
    }
  }
  return values
}

function teamPowerScore(teamId) {
  const metric = metricsByTeam.value?.[teamId]
  if (!metric) {
    return 0
  }
  const score = Number(metric.power_score || 0)
  return Math.max(0, Math.min(5, score))
}

function teamPowerRoundedHalf(teamId) {
  return Math.round(teamPowerScore(teamId) * 2) / 2
}

function teamPowerArmFill(teamId, index) {
  const rounded = teamPowerRoundedHalf(teamId)
  const fill = rounded - (index - 1)
  return Math.max(0, Math.min(1, fill))
}

function hasMixedWins(match) {
  const wins = liveMetricsForMatch(match).map((metric) => metric.wins)
  if (wins.length <= 1) return false
  return new Set(wins).size > 1
}

function liveRematchPairs(match) {
  const teamIds = (match?.teams || []).filter((teamId) => teamId != null)
  const pairs = []

  for (let index = 0; index < teamIds.length; index += 1) {
    const teamId = teamIds[index]
    const metric = metricsByTeam.value?.[teamId]
    const previousOpponents = new Set(metric?.opponents || [])
    for (const opponent of teamIds.slice(index + 1)) {
      if (previousOpponents.has(opponent)) {
        pairs.push([teamId, opponent])
      }
    }
  }

  return pairs
}

function totalPairsCount(match) {
  const size = (match?.teams || []).filter((teamId) => teamId != null).length
  return size > 1 ? (size * (size - 1)) / 2 : 0
}

function hasRematch(match) {
  return liveRematchPairs(match).length > 0
}

function hasFullRematch(match) {
  const totalPairs = totalPairsCount(match)
  if (totalPairs === 0) return false
  return liveRematchPairs(match).length === totalPairs
}

function matchStars(match) {
  if (hasEmptySlot(match)) {
    return null
  }

  let stars = 3
  if (hasMixedWins(match)) stars -= 1
  if (hasRematch(match)) stars -= 1
  if (hasFullRematch(match)) stars -= 1

  return Math.max(0, stars)
}

function starLossReasons(match) {
  if (hasEmptySlot(match)) {
    return []
  }

  const reasons = []

  const metrics = [...liveMetricsForMatch(match)].sort((a, b) => a.team - b.team)
  const winsSummary = metrics.map((metric) => `${metric.team} (${metric.wins}W)`).join(', ')
  const pairs = liveRematchPairs(match).map((pair) => pair.join('-')).join(', ')

  if (hasMixedWins(match)) {
    reasons.push(`Different wins: ${winsSummary}`)
  }

  if (hasRematch(match)) {
    if (pairs) {
      reasons.push(`Already met pair(s): ${pairs}`)
    } else {
      reasons.push(`Already met teams in match: ${(match?.teams || []).filter((team) => team != null).join(', ')}`)
    }
  }
  if (hasFullRematch(match)) {
    reasons.push(`All teams already met each other: ${(match?.teams || []).filter((team) => team != null).join(', ')}`)
  }
  return reasons
}

function isMatchIncomplete(match) {
  return hasEmptySlot(match)
}

function moveTeamTo(teamId, target) {
  if (!draft.value) return

  const hadByeBefore = draft.value.byes.includes(teamId)
  if (target === 'bye' && !hadByeBefore && disableByeAction.value) {
    return
  }

  for (const match of draft.value.matches) {
    for (let index = 0; index < match.teams.length; index += 1) {
      if (match.teams[index] === teamId) {
        match.teams[index] = null
      }
    }
  }

  removeFromList(draft.value.byes, teamId)
  removeFromList(draft.value.forfeits, teamId)

  if (target === 'bye') {
    draft.value.byes.push(teamId)
  } else if (target === 'forfeit') {
    draft.value.forfeits.push(teamId)
  }
}

function onDragStartFromSlot(matchId, index, teamId) {
  if (teamId == null) return
  dragged.value = {
    type: 'slot',
    matchId,
    index,
    teamId,
  }
}

function onDragStartFromBench(teamId, source) {
  dragged.value = {
    type: 'bench',
    source,
    teamId,
  }
}

function allowDrop(event) {
  event.preventDefault()
}

function dropToSlot(matchId, index) {
  if (!dragged.value || !draft.value) return

  const target = findSlot(matchId, index)
  if (!target) return

  const targetTeam = target.match.teams[index]

  if (dragged.value.type === 'slot') {
    const source = findSlot(dragged.value.matchId, dragged.value.index)
    if (!source) return
    source.match.teams[dragged.value.index] = targetTeam
    target.match.teams[index] = dragged.value.teamId
  } else {
    removeFromList(draft.value.byes, dragged.value.teamId)
    removeFromList(draft.value.forfeits, dragged.value.teamId)
    target.match.teams[index] = dragged.value.teamId

    if (targetTeam != null) {
      if (dragged.value.source === 'bye') {
        draft.value.byes.push(targetTeam)
      } else {
        draft.value.forfeits.push(targetTeam)
      }
    }
  }

  dragged.value = null
}

function dropToBench(target) {
  if (!dragged.value) return

  moveTeamTo(dragged.value.teamId, target)
  dragged.value = null
}

const benchTeams = computed(() => {
  if (!draft.value) return []
  return [...draft.value.byes, ...draft.value.forfeits]
})

const teamsByMatch = computed(() => {
  return Number(tournament.value?.teams_by_match || 0)
})

const maxAllowedByes = computed(() => {
  if (!draft.value) return 0
  const perMatch = teamsByMatch.value
  if (!perMatch) return 0

  const registeredTeamsCount = teams.value.length
  const forfeitCount = new Set(draft.value.forfeits || []).size
  const activeTeamsCount = Math.max(0, registeredTeamsCount - forfeitCount)
  return activeTeamsCount % perMatch
})

const disableByeAction = computed(() => {
  if (!draft.value) return false
  const byeCount = new Set(draft.value.byes || []).size
  return byeCount >= maxAllowedByes.value
})

function normalizeDraftForCommit(sourceDraft) {
  if (!sourceDraft) {
    return { matches: [], byes: [], forfeits: [], invalidPartialMatches: [] }
  }

  const normalizedMatches = []
  const normalizedByes = [...sourceDraft.byes]
  const normalizedForfeits = [...sourceDraft.forfeits]
  const invalidPartialMatches = []

  for (const match of sourceDraft.matches || []) {
    const clean = (match.teams || []).filter((teamId) => teamId != null)

    if (clean.length === 0) {
      continue
    }

    if (clean.length === teamsByMatch.value) {
      normalizedMatches.push(clean)
      continue
    }

    if (clean.length === 1) {
      const solo = clean[0]
      if (!normalizedByes.includes(solo) && !normalizedForfeits.includes(solo)) {
        normalizedByes.push(solo)
      }
      continue
    }

    invalidPartialMatches.push(match.id)
  }

  return {
    matches: normalizedMatches,
    byes: normalizedByes,
    forfeits: normalizedForfeits,
    invalidPartialMatches,
  }
}

const normalizedDraft = computed(() => normalizeDraftForCommit(draft.value))

function assignBenchTeam(teamId, matchId, index) {
  const slot = findSlot(matchId, index)
  if (!slot || slot.match.teams[index] != null) return
  removeFromList(draft.value.byes, teamId)
  removeFromList(draft.value.forfeits, teamId)
  slot.match.teams[index] = teamId
}

const draftIssues = computed(() => {
  if (!draft.value) return []

  const issues = []
  const ids = []

  if (normalizedDraft.value.invalidPartialMatches.length) {
    issues.push('Some matches are partially filled with multiple teams')
  }

  for (const match of normalizedDraft.value.matches) {
    ids.push(...match)
  }

  ids.push(...normalizedDraft.value.byes)
  ids.push(...normalizedDraft.value.forfeits)

  if (teamsByMatch.value > 0 && normalizedDraft.value.byes.length >= teamsByMatch.value) {
    issues.push(`BYE count must be lower than ${teamsByMatch.value}`)
  }

  if (ids.length !== new Set(ids).size) {
    issues.push('A team is assigned multiple times')
  }

  const known = new Set(teams.value.map((team) => team.number))
  const unknown = ids.filter((teamId) => !known.has(teamId))
  if (unknown.length) {
    issues.push('Unknown team detected in draft')
  }

  if (known.size && ids.length !== known.size) {
    issues.push('Some teams are missing from draft assignment')
  }

  return [...new Set(issues)]
})

const canCommit = computed(() => stage.value === 'review' && draftIssues.value.length === 0)

watch(
  [draftIssues, stage],
  ([issues, currentStage]) => {
    emit('issues-change', currentStage === 'review' ? issues : [])
  },
  { immediate: true },
)

const alertItems = computed(() => {
  if (!draft.value) return []

  const hiddenCodes = new Set(['rematch', 'full_rematch'])
  const items = []
  for (const alert of draft.value.alerts || []) {
    if (hiddenCodes.has(alert.code)) continue
    items.push(alert)
  }

  for (const match of draft.value.matches || []) {
    for (const violation of match.violations || []) {
      if (hiddenCodes.has(violation)) continue
      items.push({
        code: violation,
        severity: 'warning',
        message: `${match.id}: ${violation}`,
        match_id: match.id,
      })
    }
  }

  return items
})

async function focusMatch(matchId) {
  focusedMatchId.value = matchId
  await nextTick()
  const element = document.getElementById(`draw-match-${matchId}`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

async function commitDraft() {
  if (!draft.value) return
  running.value = true
  committing.value = true
  message.value = 'Creating round...'
  try {
    const prepared = normalizeDraftForCommit(draft.value)
    const createdRound = await api.createRound({
      matches: prepared.matches,
      byes: prepared.byes,
      forfeits: prepared.forfeits,
    })
    emit('created')

    try {
      await Promise.all([
        store.refreshRounds(),
        store.refreshRankings(),
        store.refreshTournament(),
      ])
    } catch {
      // Keep modal close behavior even if a follow-up refresh fails.
    }

    resetDrawState()
    const targetRound = Number(createdRound?.number)
    await router.push({
      name: 'admin-round',
      query: Number.isInteger(targetRound) && targetRound > 0
        ? { round: String(targetRound) }
        : undefined,
    })
  } catch {
    pushApiError('Unable to create round from draft')
  } finally {
    committing.value = false
    running.value = false
  }
}

function resetDrawState() {
  stage.value = 'config'
  draft.value = null
  swapSelection.value = []
  dragged.value = null
  focusedMatchId.value = null
  progress.value = 0
  message.value = 'Idle'
  hideFullMatches.value = false
  running.value = false
  committing.value = false
}
</script>

<template>
  <section>
    <div class="draw-content-scroll">
      <header
        v-if="props.showHeader"
        class="head"
      >
        <h1>Draw</h1>
        <span class="badge">{{ tournament?.status || 'no tournament' }}</span>
      </header>

      <div class="top-row">
        <div class="card form">
          <div class="algorithm-panel">
            <h2 class="algorithm-title">Algorithm</h2>
            <div class="draw-toolbar">
              <div class="algorithm-field">
                <select v-model="selectedAlgorithm">
                  <option
                    v-for="draw in draws"
                    :key="draw.name"
                    :value="draw.name"
                  >
                    {{ draw.name }}
                  </option>
                </select>
              </div>

              <div class="toolbar-actions">
                <button
                  class="action-btn"
                  :disabled="running || !tournament"
                  @click="runDraw"
                >
                  Generate
                </button>
              </div>
            </div>
          </div>

          <div
            class="algorithm-progress"
            aria-live="polite"
          >
            <div class="progress-row">
              <div class="bar">
                <div
                  class="fill"
                  :style="{ width: `${progress}%` }"
                />
              </div>
            </div>
            <div class="progress-meta">
              <p class="muted progress-message">
                {{ message }}
              </p>
              <p class="progress-percent">{{ progress }}%</p>
            </div>
          </div>
        </div>

        <div class="top-row-bench">
          <DrawBenchPanel
            :byes="draft?.byes ?? []"
            :forfeits="draft?.forfeits ?? []"
            @drop-to-bench="dropToBench"
            @drag-start-from-bench="onDragStartFromBench"
            @allow-drop="allowDrop"
          />
        </div>
      </div>

      <div
        v-if="stage === 'review' && draft"
        class="card review-card"
      >
        <div class="review-head">
          <h2>Review & adjust</h2>
          <label class="toggle-row">
            <span>Hide full matches</span>
            <span class="toggle-switch">
              <input
                v-model="hideFullMatches"
                type="checkbox"
              >
              <span class="toggle-slider" />
            </span>
          </label>
        </div>
        <p class="muted">
          Click two teams to swap them. Move teams to BYE/FORFEIT, then reassign from bench to empty slots.
        </p>

        <div class="groups">
          <section
            v-for="(group, groupIndex) in displayedGroupedMatches"
            :key="group.wins"
            class="group-block"
            :class="groupToneClass(groupIndex)"
          >
            <div class="group-rail">
              <h3>
                <span class="group-wins">{{ group.wins }}</span>
                <span class="group-label-wrap">
                  <span class="group-label">wins group</span>
                </span>
              </h3>
            </div>
            <div
              class="matches-grid"
              :class="{ 'matches-grid-wide': teamsByMatch >= 4 }"
            >
              <DrawMatchCard
                v-for="match in group.matches"
                :key="match.id"
                :match="match"
                :is-match-incomplete="isMatchIncomplete"
                :teams-two-columns="teamsByMatch >= 4"
                :team-power-score="teamPowerScore"
                :team-power-arm-fill="teamPowerArmFill"
                :focused="focusedMatchId === match.id"
                :swap-selection="swapSelection"
                :metrics-by-team="metricsByTeam"
                :bench-teams="benchTeams"
                :slot-key="slotKey"
                :match-label="matchLabel"
                :match-stars="matchStars"
                :star-loss-reasons="starLossReasons"
                :disable-bye-action="disableByeAction"
                @select-slot="selectSlot"
                @allow-drop="allowDrop"
                @drop-to-slot="dropToSlot"
                @drag-start-from-slot="onDragStartFromSlot"
                @move-team-to="moveTeamTo"
                @assign-bench-team="assignBenchTeam"
              />
            </div>
          </section>
        </div>

        <p
          v-if="hideFullMatches && !displayedGroupedMatches.length"
          class="muted"
        >
          No match with empty slot.
        </p>

        <aside
          v-if="alertItems.length"
          class="alerts-panel"
        >
          <h4>Alerts</h4>
          <ul>
            <li
              v-for="(alert, index) in alertItems"
              :key="`${alert.code}-${alert.match_id || 'none'}-${index}`"
            >
              <button
                class="alert-link"
                @click="alert.match_id ? focusMatch(alert.match_id) : null"
              >
                {{ alert.message }}
              </button>
            </li>
          </ul>
        </aside>
      </div>
    </div>

    <div class="draw-modal-footer">
      <button
        class="action-btn"
        :disabled="running || !canCommit"
        @click="commitDraft"
      >
        Create round
      </button>
    </div>
  </section>
</template>

<style scoped>
section {
  height: 100%;
  min-height: 0;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.draw-content-scroll {
  min-height: 0;
  overflow-y: auto;
  flex: 1 1 auto;
  padding-right: 0.1rem;
}

.head {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.head h1 {
  margin: 0;
}

.form {
  margin-bottom: 0;
  min-height: var(--top-row-card-min-height);
  --toolbar-control-height: 38px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.top-row {
  --top-row-card-min-height: 140px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 520px);
  gap: 1rem;
  align-items: stretch;
  margin-bottom: 1rem;
}

.top-row-bench {
  min-width: 0;
  height: 100%;
  display: flex;
}

.top-row-bench :deep(.bench-zone) {
  margin-bottom: 0;
  height: 100%;
  flex: 1 1 auto;
}

.top-row-bench :deep(.bench-row) {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  height: 100%;
  align-items: stretch;
}

.top-row-bench :deep(.bench-subcard) {
  min-height: var(--top-row-card-min-height);
  height: 100%;
}

.draw-toolbar {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex-wrap: nowrap;
}

.algorithm-panel {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  flex: 1 1 auto;
  min-width: 0;
}

.algorithm-title {
  margin: 0;
}

.algorithm-field {
  width: 100%;
  min-width: 0;
  justify-content: flex-start;
}

.algorithm-field select {
  flex: 1 1 auto;
  width: 100%;
  min-height: var(--toolbar-control-height);
  height: var(--toolbar-control-height);
}

.algorithm-progress {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  margin-top: 0.8rem;
}

.toolbar-actions {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  justify-content: center;
  flex: 0 0 auto;
}

.toolbar-actions .action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--toolbar-control-height);
  height: var(--toolbar-control-height);
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
}

label.check {
  flex-direction: row;
  align-items: center;
  margin-top: 1.8rem;
}

.action-btn {
  min-width: 9.2rem;
}

.review-card {
  margin-bottom: 1rem;
}

.review-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.review-head h2 {
  margin: 0;
}

.toggle-row {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  gap: 0.6rem;
  color: var(--color-muted);
  font-size: 0.86rem;
  user-select: none;
  cursor: pointer;
}

.toggle-row input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-switch {
  position: relative;
  display: inline-flex;
  width: 2.2rem;
  height: 1.25rem;
  flex: 0 0 auto;
}

.toggle-slider {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: #cbd5e1;
  transition: background 0.2s ease;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  left: 2px;
  top: 50%;
  width: 0.85rem;
  height: 0.85rem;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transform: translateY(-50%);
  transition: transform 0.2s ease;
}

.toggle-switch input:checked + .toggle-slider {
  background: color-mix(in srgb, var(--color-primary) 70%, #1d4ed8);
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translate(0.95rem, -50%);
}

.toggle-switch input:focus-visible + .toggle-slider {
  outline: 2px solid color-mix(in srgb, var(--color-primary) 55%, white);
  outline-offset: 2px;
}

.groups {
  display: grid;
  gap: 1rem;
}

.group-block {
  display: grid;
  grid-template-columns: clamp(2.5rem, 3.4vw, 3rem) minmax(0, 1fr);
  align-items: stretch;
  column-gap: 0.65rem;
  border: 1px solid var(--group-border, var(--color-border));
  border-radius: 10px;
  padding: 0.75rem;
  background: var(--group-bg, rgba(0, 0, 0, 0.015));
}

.group-rail {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  border-right: 1px solid color-mix(in srgb, var(--group-border, var(--color-border)) 60%, white);
  padding-right: 0.55rem;
}

.group-rail h3 {
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: clamp(6.4rem, 14vw, 7.4rem);
  width: 100%;
}

.group-wins {
  font-family: 'Avenir Next', 'Segoe UI', sans-serif;
  font-size: clamp(1.95rem, 3.5vw, 2.55rem);
  font-weight: 700;
  line-height: 1;
  color: #334155;
}

.group-label-wrap {
  margin-top: clamp(0.55rem, 1.8vw, 1rem);
  width: 100%;
  min-height: clamp(2.7rem, 6.8vw, 3.5rem);
  display: flex;
  align-items: center;
  justify-content: center;
}

.group-label {
  font-family: 'Avenir Next', 'Segoe UI', sans-serif;
  display: inline-block;
  font-size: 0.72rem;
  line-height: 1;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  text-align: center;
  transform-origin: center;
  transform: rotate(-90deg);
  color: #64748b;
}

.group-tone-0 {
  --group-bg: color-mix(in srgb, #2c6bed 10%, white);
  --group-border: color-mix(in srgb, #2c6bed 35%, var(--color-border));
}

.group-tone-1 {
  --group-bg: color-mix(in srgb, #6a4cff 10%, white);
  --group-border: color-mix(in srgb, #6a4cff 35%, var(--color-border));
}

.group-tone-2 {
  --group-bg: color-mix(in srgb, #009688 10%, white);
  --group-border: color-mix(in srgb, #009688 35%, var(--color-border));
}

.group-tone-3 {
  --group-bg: color-mix(in srgb, #ff8f00 10%, white);
  --group-border: color-mix(in srgb, #ff8f00 35%, var(--color-border));
}

.group-tone-4 {
  --group-bg: color-mix(in srgb, #d81b60 10%, white);
  --group-border: color-mix(in srgb, #d81b60 35%, var(--color-border));
}

.group-tone-5 {
  --group-bg: color-mix(in srgb, #546e7a 10%, white);
  --group-border: color-mix(in srgb, #546e7a 35%, var(--color-border));
}

.matches-grid {
  --match-card-width-base: clamp(180px, 30vw, 220px);
  --match-card-width: var(--match-card-width-base);
  display: grid;
  width: 100%;
  gap: 0.75rem;
  grid-template-columns: repeat(auto-fill, minmax(var(--match-card-width), var(--match-card-width)));
  justify-content: flex-start;
  align-items: start;
  grid-auto-rows: auto;
}

.matches-grid.matches-grid-wide {
  --match-card-width: calc(var(--match-card-width-base) * 2 + 0.45rem);
}

.alerts-panel {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.alerts-panel ul {
  margin: 0.45rem 0 0;
  padding-left: 1rem;
}

.alert-link {
  background: none;
  border: none;
  color: inherit;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
}

.progress-row {
  display: block;
}

.progress-row .bar {
  margin: 0;
}

.progress-meta {
  margin-top: 0.2rem;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.progress-percent {
  margin: 0;
  margin-left: auto;
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-size: 0.85rem;
  color: var(--color-muted);
}

.progress-message {
  margin: 0;
  flex: 1 1 auto;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  background: var(--color-primary);
  transition: width 0.2s ease;
}

.draw-modal-footer {
  display: flex;
  flex: 0 0 auto;
  gap: 0.75rem;
  justify-content: flex-end;
  padding: 0.75rem 0 0;
  margin-top: auto;
}
</style>
