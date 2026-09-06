<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Single line of help text
  text: { type: String, default: '' },
  // Multiple lines, rendered one per row
  lines: { type: Array, default: () => [] },
  // Horizontal anchoring of the bubble against the trigger
  align: { type: String, default: 'center' },
  // Accessible description of the trigger, defaults to the tooltip content
  label: { type: String, default: '' },
})

const entries = computed(() => (props.lines.length ? props.lines : [props.text].filter(Boolean)))
const ariaLabel = computed(() => props.label || entries.value.join(' '))
</script>

<template>
  <span
    class="info-tooltip has-tooltip"
    :class="`align-${align}`"
    tabindex="0"
    :aria-label="ariaLabel"
  >
    <slot>
      <span
        class="info-icon"
        aria-hidden="true"
      >i</span>
    </slot>
    <span
      v-if="entries.length"
      class="app-tooltip"
      role="tooltip"
    >
      <span
        v-for="(entry, index) in entries"
        :key="`tooltip-${index}`"
      >{{ entry }}</span>
    </span>
  </span>
</template>

<style scoped>
.info-tooltip {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: help;
  vertical-align: middle;
}

.info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  margin-left: 0.3rem;
  border: 1px solid currentcolor;
  border-radius: 50%;
  font-size: 0.65rem;
  font-style: italic;
  font-weight: 700;
  line-height: 1;
  opacity: 0.65;
  text-transform: none;
}

.info-tooltip:hover .info-icon,
.info-tooltip:focus-visible .info-icon {
  opacity: 1;
}

.app-tooltip {
  position: absolute;
  top: calc(100% + 0.45rem);
  width: max-content;
  max-width: 250px;
  z-index: 30;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
  font-size: 0.78rem;
  font-weight: 400;
  line-height: 1.3;
  text-transform: none;
  white-space: normal;
  transition: opacity 0.12s ease, transform 0.12s ease, visibility 0.12s ease;
}

.app-tooltip span {
  display: block;
}

.align-center .app-tooltip {
  left: 50%;
  transform: translate(-50%, -2px);
  text-align: center;
}

.align-right .app-tooltip {
  right: 0;
  transform: translateY(-2px);
  text-align: left;
}

.info-tooltip:hover .app-tooltip,
.info-tooltip:focus-within .app-tooltip {
  opacity: 1;
  visibility: visible;
}

.align-center:hover .app-tooltip,
.align-center:focus-within .app-tooltip {
  transform: translate(-50%, 0);
}

.align-right:hover .app-tooltip,
.align-right:focus-within .app-tooltip {
  transform: translateY(0);
}

@media print {
  .app-tooltip {
    display: none;
  }
}
</style>
