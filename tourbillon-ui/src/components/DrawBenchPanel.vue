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
})

const emit = defineEmits([
  'drop-to-bench',
  'drag-start-from-bench',
  'allow-drop',
])

function dropTo(target) {
  emit('drop-to-bench', target)
}

function dragStart(teamId, source) {
  emit('drag-start-from-bench', teamId, source)
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
        <h2>Bye</h2>

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
        <h2>Forfeit</h2>
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
  margin-bottom: 0;
  height: 100%;
}

.bench-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  height: 100%;
  align-items: stretch;
}

.bench-subcard {
  min-height: 120px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.bench-subcard h2 {
  margin: 0 0 0.55rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-content: flex-start;
}

.pill {
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
}
</style>
