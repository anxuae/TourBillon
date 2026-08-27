<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { api } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { teams, tournament, historyPlayers } = storeToRefs(store)

// One input row per player, sized after the tournament configuration.
const playersByTeam = computed(() =>
  tournament.value ? tournament.value.players_by_team : 1,
)

function emptyPlayers(count) {
  return Array.from({ length: count }, () => ({ firstname: '', lastname: '' }))
}

const playerInputs = ref(emptyPlayers(playersByTeam.value))
const teamNumberInput = ref(null)
const jokerInput = ref(0)

function nextAvailableTeamNumber() {
  const used = new Set(teams.value.map((team) => team.number))
  let candidate = 1
  while (used.has(candidate)) {
    candidate += 1
  }
  return candidate
}

function suggestTeamNumberIfEmpty() {
  if (!tournament.value) {
    teamNumberInput.value = null
    return
  }
  if (teamNumberInput.value === null || teamNumberInput.value === '') {
    teamNumberInput.value = nextAvailableTeamNumber()
  }
}

function pickRandomJoker() {
  const used = new Set(teams.value.map((team) => team.joker))
  const available = []
  for (let number = 1; number <= 1000; number += 1) {
    if (!used.has(number)) {
      available.push(number)
    }
  }
  if (!available.length) {
    jokerInput.value = 0
    return
  }
  const index = Math.floor(Math.random() * available.length)
  jokerInput.value = available[index]
}

function resetRegistrationMeta() {
  teamNumberInput.value = nextAvailableTeamNumber()
  jokerInput.value = 0
}

// Resize the input rows whenever the configuration changes.
watch(playersByTeam, (count) => {
  playerInputs.value = emptyPlayers(count)
})

watch(
  [teams, tournament],
  () => {
    suggestTeamNumberIfEmpty()
  },
  { immediate: true },
)

onMounted(() => {
  store.refreshHistoryPlayers()
  suggestTeamNumberIfEmpty()
})

// Unique known players (from previous editions), keyed by their full name.
// Both inputs share the SAME suggestion list of full names so that starting to
// type either a first or last name proposes complete players; picking one then
// fills both fields at once.
const knownPlayers = computed(() => {
  const map = new Map()
  for (const p of historyPlayers.value) {
    const fullname = `${p.firstname} ${p.lastname}`.trim()
    if (fullname && !map.has(fullname)) {
      map.set(fullname, { firstname: p.firstname, lastname: p.lastname })
    }
  }
  return map
})

const fullnameSuggestions = computed(() =>
  [...knownPlayers.value.keys()].sort(),
)

// When a field receives a value matching a known full name (typically after
// selecting a datalist option), split it across the first/last name fields.
function applyMatch(player) {
  const match = knownPlayers.value.get(player.firstname.trim())
    || knownPlayers.value.get(player.lastname.trim())
  if (match) {
    player.firstname = match.firstname
    player.lastname = match.lastname
  }
}

async function addTeam() {
  const players = playerInputs.value
    .map((p) => ({ firstname: p.firstname.trim(), lastname: p.lastname.trim() }))
    .filter((p) => p.firstname || p.lastname)
  const requestedNumber = teamNumberInput.value === '' || teamNumberInput.value === null
    ? null
    : Number(teamNumberInput.value)
  const requestedJoker = Number(jokerInput.value || 0)
  try {
    await api.createTeam({
      number: requestedNumber,
      joker: requestedJoker,
      players,
    })
    playerInputs.value = emptyPlayers(playersByTeam.value)
    await store.refreshTeams()
    await store.refreshTournament()
    resetRegistrationMeta()
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

async function removeTeam(number) {
  try {
    await api.deleteTeam(number)
    await store.refreshTeams()
    await store.refreshTournament()
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

function playerNames(team) {
  if (!team.players.length) {
    return '—'
  }
  return team.players.map((p) => `${p.firstname} ${p.lastname}`.trim()).join(', ')
}
</script>

<template>
  <section>
    <header class="head">
      <h1>Teams</h1>
    </header>

    <div class="card add-form">
      <h3>Register a team</h3>
      <div class="register-grid">
        <div class="team-number-panel">
          <label
            class="team-number-label"
            for="team-number-input"
          >Team number</label>
          <div class="team-number-row">
            <input
              id="team-number-input"
              v-model.number="teamNumberInput"
              class="team-number-input"
              type="number"
              min="1"
              :disabled="!tournament"
            >
            <button
              type="button"
              class="secondary quick-action-btn"
              aria-label="Auto fill team number"
              title="Auto fill team number"
              :disabled="!tournament"
              @click="teamNumberInput = nextAvailableTeamNumber()"
            >
              <span
                class="quick-action-icon"
                aria-hidden="true"
              >↻</span>
            </button>
          </div>
        </div>

        <div class="register-right">
          <div class="player-list">
            <div
              v-for="(player, index) in playerInputs"
              :key="index"
              class="row player-row"
            >
              <input
                v-model="player.firstname"
                list="player-suggestions"
                :placeholder="`Player ${index + 1} first name`"
                @change="applyMatch(player)"
                @keyup.enter="addTeam"
              >
              <input
                v-model="player.lastname"
                list="player-suggestions"
                :placeholder="`Player ${index + 1} last name`"
                @change="applyMatch(player)"
                @keyup.enter="addTeam"
              >
            </div>
          </div>
          <datalist id="player-suggestions">
            <option
              v-for="name in fullnameSuggestions"
              :key="name"
              :value="name"
            />
          </datalist>
          <p
            v-if="!tournament"
            class="muted"
          >
            Load or create a tournament first.
          </p>
        </div>

        <div class="register-actions">
          <label
            class="team-number-label"
            for="joker-input"
          >Joker</label>
          <div class="field-inline">
            <input
              id="joker-input"
              v-model.number="jokerInput"
              type="number"
              min="0"
              :disabled="!tournament"
            >
            <button
              type="button"
              class="secondary quick-action-btn"
              aria-label="Generate joker"
              title="Generate joker"
              :disabled="!tournament"
              @click="pickRandomJoker"
            >
              <span
                class="quick-action-icon"
                aria-hidden="true"
              >↻</span>
            </button>
          </div>
          <button
            :disabled="!tournament"
            @click="addTeam"
          >
            Add team
          </button>
        </div>
      </div>
    </div>

    <table v-if="teams.length">
      <thead>
        <tr>
          <th>Team</th>
          <th>Players</th>
          <th>Status</th>
          <th />
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="team in teams"
          :key="team.number"
        >
          <td>{{ team.number }}</td>
          <td>{{ playerNames(team) }}</td>
          <td><span class="badge">{{ team.status }}</span></td>
          <td class="right">
            <button
              class="danger-outline"
              @click="removeTeam(team.number)"
            >
              Remove
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p
      v-else
      class="muted"
    >
      No team registered yet.
    </p>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.head h1 {
  margin: 0;
}

.add-form {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.add-form h3 {
  margin-top: 0;
  margin-bottom: 0;
}

.register-grid {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) 180px;
  gap: 0.7rem;
  align-items: stretch;
}

.team-number-panel {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.team-number-label {
  font-size: 0.82rem;
  color: var(--color-muted);
}

.team-number-row {
  display: flex;
  align-items: stretch;
  gap: 0.45rem;
  flex: 1;
  min-height: 0;
}

.team-number-input {
  width: 100%;
  min-width: 0;
  flex: 1;
  min-height: 0;
  text-align: center;
  font-size: clamp(2.1rem, 3.2vw, 3rem);
  line-height: 1.1;
  font-weight: 700;
  padding: 0.3rem;
}

.team-number-row .quick-action-btn {
  align-self: stretch;
  flex: 0 0 2.8rem;
  width: 2.8rem;
  min-width: 2.8rem;
  height: auto;
  min-height: 0;
}

.quick-action-btn {
  flex: 0 0 2.25rem;
  width: 2.25rem;
  min-width: 2.25rem;
  height: auto;
  min-height: 0;
  align-self: stretch;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  font-size: 0.82rem;
}

.quick-action-icon {
  font-size: 1.05rem;
  line-height: 1;
}

.register-right {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding-top: 1.2rem;
}

.register-actions {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-inline {
  display: flex;
  align-items: stretch;
  gap: 0.55rem;
}

.field-inline input {
  width: 100%;
}

.player-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.player-row {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
}

.player-row input {
  width: 100%;
  padding-top: 0.4rem;
  padding-bottom: 0.4rem;
}

.right {
  text-align: right;
}

@media (max-width: 860px) {
  .register-grid {
    grid-template-columns: 1fr;
  }

  .register-right {
    padding-top: 0;
  }

  .team-number-input {
    min-height: 0;
    font-size: 2.1rem;
  }

  .player-row {
    grid-template-columns: 1fr;
  }
}
</style>
