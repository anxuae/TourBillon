<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  pageIndex: {
    type: Number,
    default: 0,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
  secondsUntilRotation: {
    type: Number,
    default: null,
  },
})

// The hint only makes sense when there is something to rotate through.
const paginated = computed(() => props.totalPages > 1)

// Countdown is hidden when the rotation is paused or not applicable.
const countdown = computed(() => {
  const value = Number(props.secondsUntilRotation)
  return paginated.value && Number.isFinite(value) && value > 0 ? value : null
})
</script>

<template>
  <p class="rotation-hint">
    <span class="rotation-keys">
      <span class="rotation-key">Esc</span>
    </span>
    <span>{{ t('display.escapeHint') }}</span>
    <span> - </span>
    <span class="rotation-keys">
      <span class="rotation-key">↑</span>
      <span class="rotation-key">↓</span>
    </span>
    <span>{{ t('display.rotationHint') }}</span>
    <span> - </span>
    <span
      v-if="paginated"
      class="rotation-page"
    >{{ t('display.pageIndicator', { current: props.pageIndex + 1, total: props.totalPages }) }}</span>
    <span> - </span>
    <span
      v-if="countdown !== null"
      class="rotation-page"
    >{{ t('display.rotationCountdown', { seconds: countdown }) }}</span>
  </p>
</template>

<style scoped>
.rotation-hint {
  position: fixed;
  right: 0.9rem;
  bottom: 0.5rem;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
  font-size: 0.7rem;
  line-height: 1;
  color: var(--color-muted);
  opacity: 0.55;
  pointer-events: none;
}

.rotation-keys {
  display: inline-flex;
  gap: 0.2rem;
}

.rotation-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1rem;
  padding: 0.1rem 0.2rem;
  border: 1px solid currentcolor;
  border-radius: 3px;
  font-size: 0.62rem;
}

.rotation-page {
  font-variant-numeric: tabular-nums;
}

@media print {
  .rotation-hint {
    display: none !important;
  }
}
</style>
