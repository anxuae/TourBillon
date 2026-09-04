<script setup>
// Shared team card: a squared badge showing a team id, optionally colored by
// the match result (won / lost / bye / forfeit). Used by both the admin and
// the display spaces so every view keeps the same status color code.
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  team: {
    type: [Number, String],
    required: true,
  },
  // '' keeps the neutral look (no result entered yet)
  status: {
    type: String,
    default: '',
    validator: (value) => ['', 'won', 'lost', 'bye', 'forfeit'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  showCrown: {
    type: Boolean,
    default: false,
  },
  points: {
    type: [Number, String, null],
    default: null,
  },
  label: {
    type: [String, null],
    default: null,
  },
})
</script>

<template>
  <div class="team-badge-wrapper">
    <span
      class="team-badge"
      :class="[`team-badge-${size}`, status ? `team-${status}` : '']"
    >{{ team }}</span>
    <span
      v-if="showCrown"
      class="crown"
      :class="`crown-${size}`"
      :aria-label="t('common.champion')"
    >👑</span>
    <span
      v-if="points !== null"
      class="points-badge"
      :class="`points-badge-${size}`"
    >{{ points }}</span>
    <span
      v-if="label"
      class="label-badge"
      :class="`label-badge-${size}`"
    >{{ label }}</span>
  </div>
</template>

<style scoped>
.team-badge-wrapper {
  position: relative;
  display: inline-block;
}

.team-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-weight: 900;
  font-family: 'Courier New', monospace;
  background: var(--color-surface);
  color: #1f2937;
  border: 2px solid rgba(148, 163, 184, 0.45);
  line-height: 1;
}

.team-badge-sm {
  min-width: 2.4rem;
  height: 2.4rem;
  padding: 0 0.4rem;
  border-radius: 8px;
  font-size: 1.05rem;
}

.team-badge-md {
  min-width: 5rem;
  height: 5rem;
  padding: 0 0.5rem;
  font-size: 2.3rem;
}

.team-badge-lg {
  min-width: 6.6rem;
  height: 6.6rem;
  padding: 0 0.6rem;
  border-radius: 12px;
  font-size: 3.2rem;
}

.team-badge.team-won {
  background: var(--status-won-bg, #e8f8ef);
  border-color: #34d399;
  color: #14532d;
}

.team-badge.team-lost {
  background: var(--status-lost-bg, #fdeaea);
  border-color: #f87171;
  color: #7f1d1d;
}

.team-badge.team-bye {
  background: var(--status-bye-bg, #fef7d8);
  border-color: #eab308;
  color: #713f12;
}

.team-badge.team-forfeit {
  background: var(--status-forfeit-bg, #d7dbe0);
  border-color: #475569;
  color: #1f2937;
}

/* Crown styling */
.crown {
  position: absolute;
  top: -1.5rem;
  right: -0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(25deg);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.crown-sm {
  font-size: 1.4rem;
}

.crown-md {
  font-size: 2.1rem;
}

.crown-lg {
  font-size: 2.8rem;
}

/* Points badge styling */
.points-badge {
  position: absolute;
  bottom: -0.4rem;
  right: -0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 1.6rem;
  height: 1.6rem;
  padding: 0 0.3rem;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  border: 2px solid rgba(255, 255, 255, 0.4);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.points-badge-sm {
  min-width: 1.3rem;
  height: 1.3rem;
  font-size: 0.65rem;
}

.points-badge-md {
  min-width: 1.8rem;
  height: 1.8rem;
  font-size: 0.8rem;
}

.points-badge-lg {
  min-width: 2.1rem;
  height: 2.1rem;
  font-size: 0.9rem;
}

/* Label badge styling */
.label-badge {
  position: absolute;
  bottom: -0.4rem;
  right: -0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.4);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  white-space: nowrap;
}

.label-badge-sm {
  font-size: 0.55rem;
  padding: 0.1rem 0.3rem;
}

.label-badge-md {
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
}

.label-badge-lg {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
}
</style>
