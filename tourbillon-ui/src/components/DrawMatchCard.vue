<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  match: {
    type: Object,
    required: true,
  },
  isMatchIncomplete: {
    type: Function,
    required: true,
  },
  teamsTwoColumns: {
    type: Boolean,
    default: false,
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
  disableByeAction: {
    type: Boolean,
    default: false,
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
      <span class="match-title">{{ props.matchLabel(props.match.id) }}</span>
      <span
        v-if="!props.isMatchIncomplete(props.match)"
        class="quality-wrap"
        :class="{ 'has-tooltip': props.starLossReasons(props.match).length > 0 }"
        :aria-label="t('draw.starsAria', { count: props.matchStars(props.match) ?? 0 })"
      >
        <span class="quality-label">{{ t('common.quality') }}</span>
        <span
          class="star-meter"
          role="img"
          :aria-label="t('draw.starQuality')"
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
          class="quality-tooltip app-tooltip"
          role="tooltip"
        >
          <span
            v-for="reason in props.starLossReasons(props.match)"
            :key="`${props.match.id}-${reason}`"
          >{{ reason }}</span>
        </span>
      </span>
    </header>

    <div
      class="teams-grid"
      :class="{ 'teams-grid-two-columns': props.teamsTwoColumns }"
    >
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
            <small class="team-stats">
              W{{ props.metricsByTeam[teamId]?.wins ?? 0 }} ·
              P{{ props.metricsByTeam[teamId]?.points ?? 0 }}
            </small>
            <span
              class="power-wrap has-tooltip"
              :aria-label="t('draw.powerAria', { score: props.teamPowerScore(teamId) })"
            >
              <span
                class="power-arms"
                role="img"
                :aria-label="t('draw.teamPowerLevel')"
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
              <span
                class="power-tooltip app-tooltip"
                role="tooltip"
              >
                Power {{ props.teamPowerScore(teamId) }} / 5
              </span>
            </span>
          </div>
          <span class="team-number">{{ teamId }}</span>
          <div class="chip-actions">
            <button
              class="mini status-action status-bye"
              :disabled="props.disableByeAction"
              @click.stop="moveTo(teamId, 'bye')"
            >
              {{ t('draw.bye') }}
            </button>
            <button
              class="mini status-action status-forfeit"
              @click.stop="moveTo(teamId, 'forfeit')"
            >
              {{ t('draw.forfeit') }}
            </button>
          </div>
        </template>
        <template v-else>
          <span>{{ t('draw.emptySlot') }}</span>
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
  </article>
</template>

<style scoped>
.match-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.65rem;
  height: auto;
  display: flex;
  flex-direction: column;
  overflow: visible;
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

.match-title {
  font-family: 'Avenir Next', 'Segoe UI', sans-serif;
  font-size: 1.08rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  line-height: 1.05;
  color: #64748b;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.65);
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

.app-tooltip {
  position: absolute;
  top: calc(100% + 0.35rem);
  right: 0;
  min-width: 250px;
  max-width: 340px;
  z-index: 20;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-2px);
  pointer-events: none;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
  font-size: 0.78rem;
  line-height: 1.25;
  transition: opacity 0.12s ease, transform 0.12s ease, visibility 0.12s ease;
}

.quality-tooltip {
  min-width: 250px;
}

.quality-tooltip span {
  display: block;
}

.quality-wrap.has-tooltip:hover .quality-tooltip,
.quality-wrap.has-tooltip:focus-within .quality-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.teams-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.45rem;
}

.teams-grid.teams-grid-two-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.team-chip {
  border: 1px solid var(--color-border);
  border-radius: 7px;
  padding: 0.45rem;
  min-height: 5.4rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.team-chip.empty {
  background: rgba(0, 0, 0, 0.03);
}

.team-chip.empty .bench-assign {
  margin-top: auto;
}

.team-chip.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 30%, transparent);
}

.team-stats {
  margin: 0;
}

.team-number {
  margin-top: auto;
  margin-bottom: auto;
  text-align: center;
  font-size: 1.56rem;
  line-height: 1;
  font-weight: 800;
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

.power-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.power-wrap.has-tooltip {
  cursor: help;
}

.power-tooltip {
  min-width: max-content;
  right: 0;
}

.power-wrap.has-tooltip:hover .power-tooltip,
.power-wrap.has-tooltip:focus-within .power-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
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
  margin-top: 0;
  justify-content: center;
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

</style>
