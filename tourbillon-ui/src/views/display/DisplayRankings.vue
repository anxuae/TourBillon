<script setup>
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useDrawSocket } from '@/composables/useDrawSocket'

const rankings = ref([])
const rotationSeconds = inject('displayRotationSeconds', ref(12))
const containerRef = ref(null)
const tableRef = ref(null)

async function refreshRankings() {
  try {
    rankings.value = await api.getRankings()
  } catch {
    rankings.value = []
  }
}

const { connect, disconnect } = useDrawSocket({
  onOpen: () => {
    refreshRankings().catch(() => {})
  },
  onMessage: (message) => {
    if (
      message.type === 'score_updated'
      || message.type === 'round_created'
      || message.type === 'round_deleted'
      || message.type === 'tournament_changed'
      || message.type === 'teams_updated'
    ) {
      refreshRankings().catch(() => {})
    }
  },
})

onMounted(async () => {
  await refreshRankings()
  connect()
})

onBeforeUnmount(() => {
  disconnect()
})

const allRankings = computed(() => rankings.value)

function rankingsPageSize() {
  const containerHeight = containerRef.value?.clientHeight || window.innerHeight
  const headerHeight = tableRef.value?.tHead?.getBoundingClientRect().height || 56
  const measuredRow = tableRef.value?.tBodies?.[0]?.rows?.[0]
  const rowHeight = measuredRow?.getBoundingClientRect().height || 52
  const usable = Math.max(rowHeight, containerHeight - headerHeight)
  return Math.max(1, Math.floor(usable / rowHeight))
}

const { pageItems: visibleRankings, recalculatePageSize } = useAutoDisplayPaging(
  allRankings,
  rotationSeconds,
  rankingsPageSize,
)

watch(rankings, async () => {
  await nextTick()
  recalculatePageSize()
})
</script>

<template>
  <section ref="containerRef" class="display-section">
    <table v-if="rankings.length" ref="tableRef" class="display-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team</th>
          <th>Wins</th>
          <th>Points</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in visibleRankings" :key="row.team">
          <td>{{ row.rank }}</td>
          <td>{{ row.team }}</td>
          <td>{{ row.wins }}</td>
          <td>{{ row.points }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No ranking data.</p>
  </section>
</template>

<style scoped>
.display-section {
  height: 100%;
}

.display-table {
  width: 100%;
  font-size: clamp(1rem, 1.9vw, 2rem);
  color: var(--color-text);
  table-layout: fixed;
}

.display-table td,
.display-table th {
  color: var(--color-text);
  padding: clamp(0.45rem, 1.2vh, 0.9rem) clamp(0.5rem, 1.3vw, 1.1rem);
}

.display-table th {
  font-size: clamp(0.78rem, 1.25vw, 1.1rem);
}

.display-table td {
  font-size: clamp(1rem, 1.8vw, 1.9rem);
  font-weight: 600;
}
</style>
