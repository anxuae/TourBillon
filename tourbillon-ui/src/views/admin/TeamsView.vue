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
const localError = ref(null)

// Resize the input rows whenever the configuration changes.
watch(playersByTeam, (count) => {
  playerInputs.value = emptyPlayers(count)
})

onMounted(() => {
  store.refreshHistoryPlayers()
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
  localError.value = null
  const players = playerInputs.value
    .map((p) => ({ firstname: p.firstname.trim(), lastname: p.lastname.trim() }))
    .filter((p) => p.firstname || p.lastname)
  try {
    await api.createTeam({ players })
    playerInputs.value = emptyPlayers(playersByTeam.value)
    await store.refreshTeams()
    await store.refreshTournament()
  } catch (error) {
    localError.value = error.message
  }
}

async function removeTeam(number) {
  localError.value = null
  try {
    await api.deleteTeam(number)
    await store.refreshTeams()
    await store.refreshTournament()
  } catch (error) {
    localError.value = error.message
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
      <span class="badge">{{ teams.length }} registered</span>
    </header>

    <div class="card add-form">
      <h3>Register a team</h3>
      <div
        v-for="(player, index) in playerInputs"
        :key="index"
        class="row"
      >
        <input
          v-model="player.firstname"
          list="player-suggestions"
          :placeholder="`Player ${index + 1} first name`"
          @change="applyMatch(player)"
          @keyup.enter="addTeam"
        />
        <input
          v-model="player.lastname"
          list="player-suggestions"
          :placeholder="`Player ${index + 1} last name`"
          @change="applyMatch(player)"
          @keyup.enter="addTeam"
        />
      </div>
      <datalist id="player-suggestions">
        <option v-for="name in fullnameSuggestions" :key="name" :value="name" />
      </datalist>
      <div class="row">
        <button :disabled="!tournament" @click="addTeam">Add team</button>
      </div>
      <p v-if="!tournament" class="muted">Load or create a tournament first.</p>
      <p v-if="localError" class="error">{{ localError }}</p>
    </div>

    <table v-if="teams.length">
      <thead>
        <tr>
          <th>#</th>
          <th>Players</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="team in teams" :key="team.number">
          <td>{{ team.number }}</td>
          <td>{{ playerNames(team) }}</td>
          <td><span class="badge">{{ team.status }}</span></td>
          <td class="right">
            <button class="danger" @click="removeTeam(team.number)">Remove</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="muted">No team registered yet.</p>
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
}

.add-form h3 {
  margin-top: 0;
}

.row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.right {
  text-align: right;
}
</style>
