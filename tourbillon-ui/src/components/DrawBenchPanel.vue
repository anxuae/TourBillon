<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  byes: {
    type: Array,
    default: () => [],
  },
  forfeits: {
    type: Array,
    default: () => [],
  },
  disableByeAction: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'drop-to-bench',
  'drag-start-from-bench',
])

function dropTo(target, event) {
  event?.preventDefault()
  if (target === 'bye' && props.disableByeAction) return
  emit('drop-to-bench', target)
}

function dragStart(teamId, source, event) {
  if (event?.dataTransfer) {
    // Required by Firefox to actually start the drag operation. 'copyMove'
    // also lets dragover handlers pick 'copy' to show the native green-plus
    // cursor on valid drop targets.
    event.dataTransfer.effectAllowed = 'copyMove'
    event.dataTransfer.setData('text/plain', String(teamId))
  }
  emit('drag-start-from-bench', teamId, source)
}

function allow(event, target) {
  // Fully handled here (preventDefault + dropEffect): this dropzone must not
  // forward the event to a parent handler that could unconditionally reset
  // dropEffect back to 'move', which would erase the not-allowed cursor.
  event.preventDefault()
  if (event.dataTransfer) {
    // 'none' renders a not-allowed cursor while hovering a full Bye zone;
    // 'copy' renders the native green-plus cursor (same as the file
    // dropzone) to signal that the drop is possible.
    event.dataTransfer.dropEffect = target === 'bye' && props.disableByeAction ? 'none' : 'copy'
  }
}
</script>

<template>
  <div class="bench-zone">
    <div class="bench-row">
      <div
        class="card bench-subcard"
        @dragover="allow($event, 'bye')"
        @drop="dropTo('bye', $event)"
      >
        <h2>{{ t('draw.benchBye') }}</h2>

        <div class="chips">
          <span
            v-for="teamId in props.byes"
            :key="`bye-${teamId}`"
            class="pill status-badge status-bye"
            draggable="true"
            @dragstart="dragStart(teamId, 'bye', $event)"
          >
            {{ t('draw.teamLabel', { number: teamId }) }}
          </span>
        </div>
      </div>

      <div
        class="card bench-subcard"
        @dragover="allow($event, 'forfeit')"
        @drop="dropTo('forfeit', $event)"
      >
        <h2>{{ t('draw.benchForfeit') }}</h2>
        <div class="chips">
          <span
            v-for="teamId in props.forfeits"
            :key="`forfeit-${teamId}`"
            class="pill status-badge status-forfeit"
            draggable="true"
            @dragstart="dragStart(teamId, 'forfeit', $event)"
          >
            {{ t('draw.teamLabel', { number: teamId }) }}
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
