import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

/**
 * Paginate a list on the giant screen and rotate through the pages.
 *
 * The rotation runs on a timer and can also be driven manually with the
 * up/down arrow keys, which move one page backward/forward and restart the
 * countdown. The keyboard binding lives here so every display view behaves
 * the same way without duplicating the listener.
 */
export function useAutoDisplayPaging(itemsRef, intervalSecondsRef, computePageSize) {
  const pageSize = ref(1)
  const pageIndex = ref(0)
  // Seconds left before the next automatic rotation, or ``null`` when the
  // rotation is disabled (single page or non-positive interval).
  const secondsUntilRotation = ref(null)

  let timer = null

  const totalPages = computed(() => {
    const count = itemsRef.value.length
    if (!count) return 1
    return Math.max(1, Math.ceil(count / pageSize.value))
  })

  const pageItems = computed(() => {
    const start = pageIndex.value * pageSize.value
    return itemsRef.value.slice(start, start + pageSize.value)
  })

  function clearTimer() {
    if (timer) {
      window.clearInterval(timer)
      timer = null
    }
  }

  function recalculatePageSize() {
    const next = Number(computePageSize())
    pageSize.value = Number.isFinite(next) && next > 0 ? Math.floor(next) : 1
    if (pageIndex.value >= totalPages.value) {
      pageIndex.value = 0
    }
  }

  function startTimer() {
    clearTimer()
    const seconds = Number(intervalSecondsRef.value)
    if (!Number.isFinite(seconds) || seconds <= 0 || totalPages.value <= 1) {
      secondsUntilRotation.value = null
      return
    }
    // A one-second tick drives both the countdown and the page change, so the
    // displayed value always matches the moment the rotation happens.
    const period = Math.max(1, Math.round(seconds))
    secondsUntilRotation.value = period
    timer = window.setInterval(() => {
      const remaining = (secondsUntilRotation.value ?? period) - 1
      if (remaining > 0) {
        secondsUntilRotation.value = remaining
        return
      }
      pageIndex.value = (pageIndex.value + 1) % totalPages.value
      secondsUntilRotation.value = period
    }, 1000)
  }

  function nextPage() {
    // Manual advance: move forward and restart the countdown from now
    pageIndex.value = (pageIndex.value + 1) % totalPages.value
    startTimer()
  }

  function previousPage() {
    // Manual rewind: move backward and restart the countdown from now
    pageIndex.value = (pageIndex.value - 1 + totalPages.value) % totalPages.value
    startTimer()
  }

  watch(itemsRef, () => {
    if (pageIndex.value >= totalPages.value) {
      pageIndex.value = 0
    }
    startTimer()
  })

  watch(totalPages, () => {
    if (pageIndex.value >= totalPages.value) {
      pageIndex.value = 0
    }
    startTimer()
  })

  watch(intervalSecondsRef, () => {
    startTimer()
  })

  function onKeydown(event) {
    // Arrow keys force the rotation to move on without waiting for the timer
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      nextPage()
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      previousPage()
    }
  }

  onMounted(() => {
    recalculatePageSize()
    window.addEventListener('resize', recalculatePageSize)
    window.addEventListener('keydown', onKeydown)
    startTimer()
  })

  onBeforeUnmount(() => {
    clearTimer()
    window.removeEventListener('resize', recalculatePageSize)
    window.removeEventListener('keydown', onKeydown)
  })

  return {
    pageSize,
    pageIndex,
    totalPages,
    pageItems,
    secondsUntilRotation,
    recalculatePageSize,
    nextPage,
    previousPage,
  }
}
