<script setup>
import { computed, onBeforeUnmount, nextTick, ref } from 'vue'

const props = defineProps({
  // Single line of help text
  text: { type: String, default: '' },
  // Multiple lines, rendered one per row
  lines: { type: Array, default: () => [] },
  // Preferred horizontal anchoring of the bubble against the trigger
  align: { type: String, default: 'center' },
  // Accessible description of the trigger, defaults to the tooltip content
  label: { type: String, default: '' },
})

// Distance kept between the bubble and the viewport edges
const MARGIN = 8
// Vertical gap between the trigger and the bubble
const GAP = 7

const entries = computed(() => (props.lines.length ? props.lines : [props.text].filter(Boolean)))
const ariaLabel = computed(() => props.label || entries.value.join(' '))

const triggerRef = ref(null)
const bubbleRef = ref(null)
const open = ref(false)
const placed = ref(false)
const style = ref({})

function place() {
  const trigger = triggerRef.value
  const bubble = bubbleRef.value
  if (!trigger || !bubble) return

  const anchor = trigger.getBoundingClientRect()
  const { width, height } = bubble.getBoundingClientRect()
  const viewportWidth = document.documentElement.clientWidth
  const viewportHeight = document.documentElement.clientHeight

  // Preferred horizontal position, then clamped inside the viewport
  let left = props.align === 'right' ? anchor.right - width : anchor.left + (anchor.width - width) / 2
  left = Math.min(Math.max(left, MARGIN), Math.max(MARGIN, viewportWidth - width - MARGIN))

  // Below the trigger, unless it would overflow and there is more room above
  const belowTop = anchor.bottom + GAP
  const aboveTop = anchor.top - height - GAP
  const overflowsBelow = belowTop + height + MARGIN > viewportHeight
  let top = overflowsBelow && aboveTop >= MARGIN ? aboveTop : belowTop
  top = Math.min(Math.max(top, MARGIN), Math.max(MARGIN, viewportHeight - height - MARGIN))

  style.value = { left: `${Math.round(left)}px`, top: `${Math.round(top)}px` }
  placed.value = true
}

async function show() {
  if (!entries.value.length) return
  open.value = true
  placed.value = false
  await nextTick()
  place()
  // A fixed bubble would drift away from its trigger while the page moves
  window.addEventListener('scroll', hide, true)
  window.addEventListener('resize', hide)
}

function hide() {
  open.value = false
  placed.value = false
  window.removeEventListener('scroll', hide, true)
  window.removeEventListener('resize', hide)
}

onBeforeUnmount(hide)
</script>

<template>
  <span
    ref="triggerRef"
    class="info-tooltip has-tooltip"
    tabindex="0"
    :aria-label="ariaLabel"
    @mouseenter="show"
    @mouseleave="hide"
    @focusin="show"
    @focusout="hide"
  >
    <slot>
      <span
        class="info-icon"
        aria-hidden="true"
      >i</span>
    </slot>
    <Teleport to="body">
      <span
        v-if="open"
        ref="bubbleRef"
        class="app-tooltip"
        :class="{ placed }"
        :style="style"
        role="tooltip"
      >
        <span
          v-for="(entry, index) in entries"
          :key="`tooltip-${index}`"
        >{{ entry }}</span>
      </span>
    </Teleport>
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
</style>

<style>
/* Teleported to the body, so it cannot be scoped nor clipped by an ancestor */
.app-tooltip {
  position: fixed;
  width: max-content;
  max-width: 250px;
  z-index: 3000;
  opacity: 0;
  pointer-events: none;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
  font-size: 0.78rem;
  font-weight: 400;
  line-height: 1.3;
  text-align: left;
  text-transform: none;
  white-space: normal;
  transition: opacity 0.12s ease;
}

.app-tooltip span {
  display: block;
}

/* Revealed only once measured and positioned, to avoid a visible jump */
.app-tooltip.placed {
  opacity: 1;
}

@media print {
  .app-tooltip {
    display: none;
  }
}
</style>
