<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useEvents } from '@/events/eventsClient'
import TeamBadge from '@/components/TeamBadge.vue'

const teams = ref([])
const rotationSeconds = inject('displayRotationSeconds', ref(12))
const containerRef = ref(null)

async function refreshTeams() {
  try {
    teams.value = await api.listTeams()
  } catch {
    teams.value = []
  }
}

const { subscribe } = useEvents()

subscribe('teams_updated', () => {
  refreshTeams().catch(() => {})
})
subscribe('tournament_changed', () => {
  refreshTeams().catch(() => {})
})


onMounted(async () => {
  await refreshTeams()
})


const allTeams = computed(() => [...teams.value].sort((left, right) => left.number - right.number))

function teamsPageSize() {
  const gap = 16
  const cardMinWidth = 340
  const width = Math.max(320, containerRef.value?.clientWidth || window.innerWidth)
  const cardHeight = width <= 640 ? 165 : 195
  const height = Math.max(cardHeight, containerRef.value?.clientHeight || window.innerHeight)

  const columns = Math.max(1, Math.floor((width + gap) / (cardMinWidth + gap)))
  const rows = Math.max(1, Math.floor((height + gap) / (cardHeight + gap)))
  return columns * rows
}

const { pageItems: visibleTeams } = useAutoDisplayPaging(
  allTeams,
  rotationSeconds,
  teamsPageSize,
)

function playerLabel(player) {
  const firstname = (player.firstname || '').trim()
  const lastname = (player.lastname || '').trim()
  if (!firstname && !lastname) {
    return '—'
  }
  return `${firstname} - ${lastname}`
}
</script>

<template>
  <section
    ref="containerRef"
    class="display-section"
  >
    <div
      v-if="teams.length"
      class="grid"
    >
      <article
        v-for="team in visibleTeams"
        :key="team.number"
        class="team-card"
      >
        <div class="team-number">
          <TeamBadge
            :team="team.number"
            size="lg"
          />
        </div>

        <div class="players-col">
          <p
            v-if="!team.players.length"
            class="player-line"
          >
            —
          </p>
          <p
            v-for="(player, index) in team.players"
            v-else
            :key="`${team.number}-${index}`"
            class="player-line"
          >
            {{ playerLabel(player) }}
          </p>
        </div>
      </article>
    </div>
    <p v-else>
      No teams available.
    </p>
  </section>
</template>

<style scoped>
.display-section {
  height: 100%;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  grid-auto-rows: 195px;
  gap: 1rem;
}

.team-card {
  display: grid;
  grid-template-columns: 112px 1fr;
  height: 100%;
  gap: 1rem;
  align-items: stretch;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1rem;
}

.team-number {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: clamp(2.3rem, 5vw, 3.4rem);
  font-weight: 800;
  line-height: 1;
}

.players-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.4rem;
  min-width: 0;
}

.player-line {
  margin: 0;
  font-size: clamp(1rem, 2.2vw, 1.35rem);
  font-weight: 600;
}

@media (max-width: 640px) {
  .grid {
    grid-auto-rows: 165px;
  }

  .team-card {
    grid-template-columns: 90px 1fr;
    gap: 0.75rem;
    padding: 0.85rem;
  }
}
</style>
