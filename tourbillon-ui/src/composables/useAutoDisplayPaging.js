import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

export function useAutoDisplayPaging(itemsRef, intervalSecondsRef, computePageSize) {
  const pageSize = ref(1)
  const pageIndex = ref(0)

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
      return
    }
    timer = window.setInterval(() => {
      pageIndex.value = (pageIndex.value + 1) % totalPages.value
    }, seconds * 1000)
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

  onMounted(() => {
    recalculatePageSize()
    window.addEventListener('resize', recalculatePageSize)
    startTimer()
  })

  onBeforeUnmount(() => {
    clearTimer()
    window.removeEventListener('resize', recalculatePageSize)
  })

  return {
    pageSize,
    pageIndex,
    totalPages,
    pageItems,
    recalculatePageSize,
  }
}
