<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { api } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { rounds } = storeToRefs(store)

const selectedRound = ref(null)
const pointsByMatch = ref({})
const localError = ref(null)

const currentRound = computed(() => {
  if (!rounds.value.length) {
    return null
  }
  const number = Number(selectedRound.value || rounds.value[rounds.value.length - 1].number)
  return rounds.value.find((item) => item.number === number) || null
})

onMounted(async () => {
  await store.refreshRounds()
  if (rounds.value.length) {
    selectedRound.value = rounds.value[rounds.value.length - 1].number
  }
})

function initPoints(match) {
  const key = String(match.location || match.teams.join('-'))
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
  localError.value = null
  const key = String(match.location || match.teams.join('-'))
  const points = pointsByMatch.value[key] || initPoints(match)
  try {
    await api.setMatchResult(roundNumber, index + 1, points)
    await store.refreshRounds()
    await store.refreshRankings(roundNumber)
  } catch (error) {
    localError.value = error.message
  }
}
</script>

<template>
  <section>
    <header class="head">
      <h1>Round</h1>
      <select v-if="rounds.length" v-model.number="selectedRound">
        <option v-for="round in rounds" :key="round.number" :value="round.number">
          Round {{ round.number }}
        </option>
      </select>
    </header>

    <p v-if="localError" class="error">{{ localError }}</p>

    <div v-if="currentRound" class="card">
      <h3>Round {{ currentRound.number }} <span class="badge">{{ currentRound.status }}</span></h3>
      <p v-if="currentRound.byes?.length" class="muted">Byes: {{ currentRound.byes.join(', ') }}</p>

      <table>
        <thead>
          <tr>
            <th>Match</th>
            <th>Teams</th>
            <th>Points</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(match, index) in currentRound.matches" :key="`${currentRound.number}-${index}`">
            <td>{{ match.location || index + 1 }}</td>
            <td>{{ match.teams.join(' vs ') }}</td>
            <td>
              <div class="points">
                <label v-for="team in match.teams" :key="team">
                  T{{ team }}
                  <input v-model.number="initPoints(match)[team]" type="number" min="0" />
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
  </section>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.head h1 {
  margin: 0;
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
</style>
