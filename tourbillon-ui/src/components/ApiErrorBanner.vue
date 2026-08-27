<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { API_ERROR_CLEAR_EVENT, API_ERROR_EVENT } from '@/api/client'

const message = ref('')
const queue = ref([])

const AUTO_HIDE_MS = 8000
let hideTimer = null

const pendingCount = computed(() => queue.value.length)
const pendingLabel = computed(() => {
  if (pendingCount.value <= 0) {
    return ''
  }
  if (pendingCount.value === 1) {
    return '1 more error'
  }
  return `${pendingCount.value} more errors`
})

function clearHideTimer() {
  if (hideTimer) {
    window.clearTimeout(hideTimer)
    hideTimer = null
  }
}

function scheduleAutoHide() {
  clearHideTimer()
  hideTimer = window.setTimeout(() => {
    dismissCurrentMessage()
  }, AUTO_HIDE_MS)
}

function showNextMessage() {
  if (message.value || !queue.value.length) {
    return
  }
  message.value = queue.value.shift()
  scheduleAutoHide()
}

function dismissCurrentMessage() {
  message.value = ''
  showNextMessage()
}

function onApiError(event) {
  const detail = event?.detail
  if (!detail || !detail.message) {
    return
  }
  queue.value.push(String(detail.message))
  showNextMessage()
}

function onApiErrorClear() {
  clearHideTimer()
  queue.value = []
  message.value = ''
}

function close() {
  clearHideTimer()
  dismissCurrentMessage()
}

onMounted(() => {
  window.addEventListener(API_ERROR_EVENT, onApiError)
  window.addEventListener(API_ERROR_CLEAR_EVENT, onApiErrorClear)
})

onBeforeUnmount(() => {
  clearHideTimer()
  window.removeEventListener(API_ERROR_EVENT, onApiError)
  window.removeEventListener(API_ERROR_CLEAR_EVENT, onApiErrorClear)
})
</script>

<template>
  <div
    v-if="message"
    class="api-error-banner"
    role="alert"
    aria-live="assertive"
  >
    <span class="message">{{ message }}</span>
    <div class="actions">
      <span
        v-if="pendingCount > 0"
        class="pending-badge"
      >{{ pendingLabel }}</span>
      <button
        type="button"
        class="close-btn"
        @click="close"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<style scoped>
.api-error-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #b42318;
  color: #fff;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
}

.message {
  min-width: 0;
}

.actions {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
}

.pending-badge {
  border: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  border-radius: 999px;
  padding: 0.15rem 0.5rem;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.close-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #fff;
  border-radius: 8px;
  padding: 0.2rem 0.55rem;
  line-height: 1;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}
</style>