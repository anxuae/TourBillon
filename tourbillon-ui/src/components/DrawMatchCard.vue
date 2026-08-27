<script setup>
const props = defineProps({
  match: {
    type: Object,
    required: true,
  },
  isMatchIncomplete: {
    type: Function,
    required: true,
  },
  focused: {
    type: Boolean,
    default: false,
  },
  swapSelection: {
    type: Array,
    default: () => [],
  },
  metricsByTeam: {
    type: Object,
    required: true,
  },
  teamPowerScore: {
    type: Function,
    required: true,
  },
  teamPowerArmFill: {
    type: Function,
    required: true,
  },
  benchTeams: {
    type: Array,
    default: () => [],
  },
  slotKey: {
    type: Function,
    required: true,
  },
  matchLabel: {
    type: Function,
    required: true,
  },
  matchStars: {
    type: Function,
    required: true,
  },
  starLossReasons: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits([
  'select-slot',
  'allow-drop',
  'drop-to-slot',
  'drag-start-from-slot',
  'move-team-to',
  'assign-bench-team',
])

function selectSlot(index) {
  emit('select-slot', props.match.id, index)
}

function allowDrop(event) {
  emit('allow-drop', event)
}

function dropToSlot(index) {
  emit('drop-to-slot', props.match.id, index)
}

function dragStart(index, teamId) {
  emit('drag-start-from-slot', props.match.id, index, teamId)
}

function moveTo(teamId, target) {
  emit('move-team-to', teamId, target)
}

function assignBench(teamId, index) {
  emit('assign-bench-team', teamId, props.match.id, index)
}
</script>

<template>
  <article
    :id="`draw-match-${props.match.id}`"
    class="match-card"
    :class="{ focused: props.focused }"
  >
    <header>
      <strong>{{ props.matchLabel(props.match.id) }}</strong>
      <span
        v-if="!props.isMatchIncomplete(props.match)"
        class="quality-wrap"
        :class="{ 'has-tooltip': props.starLossReasons(props.match).length > 0 }"
        :aria-label="`${props.matchStars(props.match) ?? 0} stars`"
      >
        <span class="quality-label">Quality</span>
        <span
          class="star-meter"
          role="img"
          aria-label="Star quality level"
        >
          <span
            v-for="index in 3"
            :key="`${props.match.id}-s-${index}`"
            class="star"
            :class="{ active: index <= (props.matchStars(props.match) ?? 0) }"
          >★</span>
        </span>
        <span
          v-if="props.starLossReasons(props.match).length > 0"
          class="quality-tooltip"
          role="tooltip"
        >
          <span
            v-for="reason in props.starLossReasons(props.match)"
            :key="`${props.match.id}-${reason}`"
          >{{ reason }}</span>
        </span>
      </span>
    </header>

    <div class="teams-grid">
      <div
        v-for="(teamId, teamIndex) in props.match.teams"
        :key="`${props.match.id}-${teamIndex}`"
        class="team-chip"
        :class="{ empty: teamId == null, selected: props.swapSelection.includes(props.slotKey(props.match.id, teamIndex)) }"
        :draggable="teamId != null"
        @click="selectSlot(teamIndex)"
        @dragover="allowDrop"
        @drop="dropToSlot(teamIndex)"
        @dragstart="dragStart(teamIndex, teamId)"
      >
        <template v-if="teamId != null">
          <div class="team-head-row">
            <span class="team-main">Team {{ teamId }}</span>
            <span
              class="power-arms"
              :title="`Power ${props.teamPowerScore(teamId).toFixed(2)} / 5`"
              :aria-label="`Power ${props.teamPowerScore(teamId).toFixed(2)} out of 5`"
            >
              <span
                v-for="index in 5"
                :key="`${props.match.id}-${teamId}-arm-${index}`"
                class="power-arm"
              >
                <span class="power-arm-base">⬢</span>
                <span
                  class="power-arm-fill"
                  :style="{ width: `${props.teamPowerArmFill(teamId, index) * 100}%` }"
                >⬢</span>
              </span>
            </span>
          </div>
          <small>
            W{{ props.metricsByTeam[teamId]?.wins ?? 0 }} ·
            P{{ props.metricsByTeam[teamId]?.points ?? 0 }}
          </small>
          <div class="chip-actions">
            <button
              class="mini status-action status-bye"
              @click.stop="moveTo(teamId, 'bye')"
            >
              BYE
            </button>
            <button
              class="mini status-action status-forfeit"
              @click.stop="moveTo(teamId, 'forfeit')"
            >
              FORFEIT
            </button>
          </div>
        </template>
        <template v-else>
          <span>Empty slot</span>
          <div class="bench-assign">
            <button
              v-for="benchTeam in props.benchTeams"
              :key="`${props.match.id}-${teamIndex}-${benchTeam}`"
              class="mini"
              @click.stop="assignBench(benchTeam, teamIndex)"
            >
              + {{ benchTeam }}
            </button>
          </div>
        </template>
      </div>
    </div>

    <ul
      v-if="props.match.violations.length"
      class="violations"
    >
      <li
        v-for="violation in props.match.violations"
        :key="violation"
      >
        ⚠ {{ violation }}
      </li>
    </ul>
  </article>
</template>

<style scoped>
.match-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.65rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: auto;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.match-card.focused {
  border-color: color-mix(in srgb, var(--color-primary) 70%, #204da8);
  box-shadow:
    0 0 0 2px color-mix(in srgb, var(--color-primary) 30%, transparent),
    0 6px 14px rgba(0, 0, 0, 0.14);
}

.match-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.quality-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  position: relative;
}

.quality-label {
  font-weight: 600;
  font-size: 0.82rem;
  color: #5a6679;
}

.star-meter {
  display: inline-flex;
  align-items: center;
  gap: 0.1rem;
}

.star {
  font-size: 0.95rem;
  line-height: 1;
  color: #c7ceda;
}

.star.active {
  color: #d4af37;
  text-shadow: 0 0 1px rgba(0, 0, 0, 0.25);
}

.quality-wrap.has-tooltip {
  cursor: help;
}

.quality-tooltip {
  position: absolute;
  top: calc(100% + 0.35rem);
  right: 0;
  min-width: 250px;
  max-width: 340px;
  z-index: 20;
  display: none;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
  font-size: 0.78rem;
  line-height: 1.25;
}

.quality-tooltip span {
  display: block;
}

.quality-wrap.has-tooltip:hover .quality-tooltip,
.quality-wrap.has-tooltip:focus-within .quality-tooltip {
  display: block;
}

.teams-grid {
  display: grid;
  gap: 0.45rem;
}

.team-chip {
  border: 1px solid var(--color-border);
  border-radius: 7px;
  padding: 0.45rem;
  cursor: pointer;
  display: grid;
  gap: 0.2rem;
}

.team-chip.empty {
  background: rgba(0, 0, 0, 0.03);
}

.team-chip.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 30%, transparent);
}

.team-main {
  font-weight: 700;
}

.team-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
}

.power-arms {
  display: inline-flex;
  align-items: center;
  gap: 0.12rem;
}

.power-arm {
  position: relative;
  display: inline-block;
  font-size: 0.9rem;
  line-height: 1;
  width: 1em;
  height: 1em;
}

.power-arm-base {
  display: inline-block;
  color: #d5dbe8;
  opacity: 1;
  -webkit-text-stroke: 0.2px rgba(15, 23, 42, 0.2);
}

.power-arm-fill {
  position: absolute;
  left: 0;
  top: 0;
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  color: #a855f7;
  -webkit-text-stroke: 0.2px rgba(88, 28, 135, 0.45);
  text-shadow: 0 0 2px rgba(168, 85, 247, 0.45);
  opacity: 1;
}

.chip-actions {
  display: flex;
  gap: 0.35rem;
  margin-top: 0.25rem;
  justify-content: flex-end;
}

.mini {
  font-size: 0.75rem;
  padding: 0.2rem 0.45rem;
}

.chip-actions .status-action {
  width: 5.4rem;
  min-width: 5.4rem;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.2rem 0.45rem;
}

.bench-assign {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.violations {
  margin: 0.4rem 0 0;
  padding-left: 1.1rem;
}
</style>
