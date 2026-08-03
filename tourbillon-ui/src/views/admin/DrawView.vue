<script setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { api, openDrawSocket } from '@/api/client'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { draws, tournament } = storeToRefs(store)

const selectedAlgorithm = ref('')
const maxDisparity = ref(1)
const allowRematch = ref(false)
const randomSeed = ref('')

const progress = ref(0)
const message = ref('Idle')
const running = ref(false)
const localError = ref(null)

let socket = null

onMounted(async () => {
  await store.refreshDraws()
  if (draws.value.length && !selectedAlgorithm.value) {
    selectedAlgorithm.value = draws.value[0].name
  }
})

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
        localError.value = payload.message || 'Draw error'
        running.value = false
      } else if (payload.type === 'round_created') {
        running.value = false
        progress.value = 100
        message.value = `Round ${payload.round} created`
      }
    } catch (error) {
      // Ignore malformed events.
    }
  }
}

async function runDraw() {
  localError.value = null
  progress.value = 0
  message.value = 'Starting draw...'
  running.value = true
  connectSocket()

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
    await store.refreshRounds()
    await store.refreshRankings()
    await store.refreshTournament()
  } catch (error) {
    localError.value = error.message
    running.value = false
  }
}
</script>

<template>
  <section>
    <header class="head">
      <h1>Draw</h1>
      <span class="badge">{{ tournament?.status || 'no tournament' }}</span>
    </header>

    <div class="card form">
      <div class="grid">
        <label>
          Algorithm
          <select v-model="selectedAlgorithm">
            <option v-for="draw in draws" :key="draw.name" :value="draw.name">
              {{ draw.name }}
            </option>
          </select>
        </label>

        <label>
          Max disparity
          <input v-model.number="maxDisparity" type="number" min="0" />
        </label>

        <label>
          Seed (optional)
          <input v-model="randomSeed" type="number" placeholder="42" />
        </label>

        <label class="check">
          <input v-model="allowRematch" type="checkbox" />
          Allow rematch
        </label>
      </div>

      <div class="actions">
        <button :disabled="running || !tournament" @click="runDraw">Run draw</button>
      </div>
      <p v-if="localError" class="error">{{ localError }}</p>
    </div>

    <div class="card progress-card">
      <div class="progress-head">
        <strong>Progress</strong>
        <span>{{ progress }}%</span>
      </div>
      <div class="bar">
        <div class="fill" :style="{ width: `${progress}%` }"></div>
      </div>
      <p class="muted">{{ message }}</p>
    </div>
  </section>
</template>

<style scoped>
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
  margin-bottom: 1rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
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

.actions {
  margin-top: 1rem;
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
</style>
