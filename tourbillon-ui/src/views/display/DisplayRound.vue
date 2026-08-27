<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useDrawSocket } from '@/composables/useDrawSocket'

const currentRound = ref(null)
const rotationSeconds = inject('displayRotationSeconds', ref(12))
const containerRef = ref(null)

async function refreshRound() {
  try {
    const rounds = await api.listRounds()
    if (!rounds.length) {
      currentRound.value = null
      return
    }
    currentRound.value = rounds[rounds.length - 1]
  } catch {
    currentRound.value = null
  }
}

const { connect, disconnect } = useDrawSocket({
  onOpen: () => {
    refreshRound().catch(() => {})
  },
  onMessage: (message) => {
    if (
      message.type === 'score_updated'
      || message.type === 'round_created'
      || message.type === 'round_deleted'
      || message.type === 'tournament_changed'
    ) {
      refreshRound().catch(() => {})
    }
  },
})

onMounted(async () => {
  await refreshRound()
  connect()
})

onBeforeUnmount(() => {
  disconnect()
})

const allMatches = computed(() => currentRound.value?.matches || [])

function matchesPageSize() {
  const gap = 16
  const cardMinWidth = 280
  const cardHeight = 126
  const width = Math.max(cardMinWidth, containerRef.value?.clientWidth || window.innerWidth)
  const height = Math.max(cardHeight, containerRef.value?.clientHeight || window.innerHeight)

  const columns = Math.max(1, Math.floor((width + gap) / (cardMinWidth + gap)))
  const rows = Math.max(1, Math.floor((height + gap) / (cardHeight + gap)))
  return columns * rows
}

const { pageItems: visibleMatches } = useAutoDisplayPaging(
  allMatches,
  rotationSeconds,
  matchesPageSize,
)
</script>

<template>
  <section
    ref="containerRef"
    class="display-section"
  >
    <div
      v-if="currentRound"
      class="grid"
    >
      <article
        v-for="(match, index) in visibleMatches"
        :key="`${currentRound.number}-${index}`"
        class="match"
      >
        <h3>Location {{ match.location ?? '—' }}</h3>
        <p class="teams">
          {{ match.teams.join(' vs ') }}
        </p>
      </article>
    </div>
    <p
      v-if="currentRound?.byes?.length"
      class="status-row"
    >
      <span class="status-row-label">Byes:</span>
      <span class="status-row-list">
        <span
          v-for="teamId in currentRound.byes"
          :key="`display-bye-${teamId}`"
          class="status-badge status-bye"
        >
          Team {{ teamId }}
        </span>
      </span>
    </p>
    <p v-else-if="!currentRound">
      No round in progress.
    </p>
  </section>
</template>

<style scoped>
.display-section {
  height: 100%;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.match {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1rem;
}

.teams {
  font-size: 1.3rem;
  font-weight: 700;
}

.status-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.9rem;
}

.status-row-label {
  color: #dbeafe;
}

.status-row-list {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
}
</style>
