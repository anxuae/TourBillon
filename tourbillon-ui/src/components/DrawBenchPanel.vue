<script setup>
const props = defineProps({
  byes: {
    type: Array,
    default: () => [],
  },
  forfeits: {
    type: Array,
    default: () => [],
  },
  suggestedByeTeams: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits([
  'drop-to-bench',
  'drag-start-from-bench',
  'move-suggested-to-bye',
  'allow-drop',
])

function dropTo(target) {
  emit('drop-to-bench', target)
}

function dragStart(teamId, source) {
  emit('drag-start-from-bench', teamId, source)
}

function moveSuggested(teamId) {
  emit('move-suggested-to-bye', teamId)
}

function allow(event) {
  emit('allow-drop', event)
}
</script>

<template>
  <div class="bench-zone">
    <div class="bench-row">
      <div
        class="card bench-subcard"
        @dragover="allow"
        @drop="dropTo('bye')"
      >
        <h2>BYE</h2>

        <div
          v-if="props.suggestedByeTeams.length"
          class="bye-suggestions"
        >
          <p class="muted">
            Suggested from single-team matches
          </p>
          <div class="chips">
            <button
              v-for="teamId in props.suggestedByeTeams"
              :key="`suggested-bye-${teamId}`"
              class="mini status-action status-bye"
              @click="moveSuggested(teamId)"
            >
              Add team {{ teamId }}
            </button>
          </div>
        </div>

        <div class="chips">
          <span
            v-for="teamId in props.byes"
            :key="`bye-${teamId}`"
            class="pill status-badge status-bye"
            draggable="true"
            @dragstart="dragStart(teamId, 'bye')"
          >
            Team {{ teamId }}
          </span>
        </div>
      </div>

      <div
        class="card bench-subcard"
        @dragover="allow"
        @drop="dropTo('forfeit')"
      >
        <h2>FORFEIT</h2>
        <div class="chips">
          <span
            v-for="teamId in props.forfeits"
            :key="`forfeit-${teamId}`"
            class="pill status-badge status-forfeit"
            draggable="true"
            @dragstart="dragStart(teamId, 'forfeit')"
          >
            Team {{ teamId }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bench-zone {
  margin-bottom: 1rem;
}

.bench-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.bench-subcard {
  min-height: 120px;
}

.bye-suggestions {
  margin-bottom: 0.75rem;
}

.bye-suggestions .chips {
  margin-top: 0.45rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.pill {
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
}

@media (max-width: 900px) {
  .bench-row {
    grid-template-columns: 1fr;
  }
}
</style>
