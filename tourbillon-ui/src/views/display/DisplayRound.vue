<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useEvents } from '@/events/eventsClient'

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

const { subscribe } = useEvents()

for (const type of ['score_updated', 'round_created', 'round_deleted', 'tournament_changed']) {
  subscribe(type, () => refreshRound().catch(() => {}))
}

onMounted(async () => {
  await refreshRound()
})

const allMatches = computed(() => {
  if (!currentRound.value?.matches) return []
  return currentRound.value.matches.map((match) => ({
    ...match,
    teams: [...match.teams].sort((a, b) => a - b),
  }))
})

function matchResultStatus(match, teamId) {
  // Neutral until every team of the match has a score entered
  const points = match.points || {}
  const values = match.teams.map((id) => points[id])
  if (values.some((value) => value === null || value === undefined)) return ''
  // No result entered yet when every score is still zero
  if (values.every((value) => value === 0)) return ''
  const best = Math.max(...values)
  return points[teamId] === best ? 'won' : 'lost'
}

const teamCards = computed(() => {
  // Flatten all teams from all matches into individual cards, sorted by team number
  const cards = []
  for (const match of allMatches.value) {
    for (const teamId of match.teams) {
      cards.push({
        type: 'team',
        key: `team-${teamId}`,
        teamId,
        location: match.location ?? '—',
        opponents: match.teams
          .filter((t) => t !== teamId)
          .map((oppId) => ({ id: oppId, status: matchResultStatus(match, oppId) })),
        status: matchResultStatus(match, teamId),
      })
    }
  }
  return cards.sort((left, right) => left.teamId - right.teamId)
})

const specialCards = computed(() => {
  // One extra card per special status, gathering all concerned teams
  const cards = []
  const byes = currentRound.value?.byes ?? []
  if (byes.length) {
    cards.push({
      type: 'special',
      key: 'special-bye',
      label: 'Bye',
      status: 'bye',
      teams: [...byes].sort((a, b) => a - b),
    })
  }
  const forfeits = currentRound.value?.forfeits ?? []
  if (forfeits.length) {
    cards.push({
      type: 'special',
      key: 'special-forfeit',
      label: 'Forfeit',
      status: 'forfeit',
      teams: [...forfeits].sort((a, b) => a - b),
    })
  }
  return cards
})

// Special cards open the rotation cycle, ahead of the first team
const allCards = computed(() => [...specialCards.value, ...teamCards.value])

function cardsPageSize() {
  // One card per row, based on height
  const cardHeight = 140
  const height = containerRef.value?.clientHeight || window.innerHeight
  return Math.max(1, Math.floor(height / cardHeight))
}

const { pageItems: visibleCards, nextPage, previousPage } = useAutoDisplayPaging(
  allCards,
  rotationSeconds,
  cardsPageSize,
)

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
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <section
    ref="containerRef"
    class="display-section"
  >
    <div
      v-if="currentRound && visibleCards.length"
      class="cards-container"
    >
      <div
        v-for="card in visibleCards"
        :key="card.key"
        class="team-card"
        :class="card.type === 'special' ? 'team-card-special' : ''"
      >
        <div
          v-if="card.type === 'team'"
          class="card-numbers"
        >
          <span
            class="team-badge team-badge-main"
            :class="card.status ? `team-${card.status}` : ''"
          >{{ card.teamId }}</span>
          <span
            v-for="opponent in card.opponents"
            :key="`opp-${opponent.id}`"
            class="team-badge"
            :class="opponent.status ? `team-${opponent.status}` : ''"
          >{{ opponent.id }}</span>
        </div>
        <div
          v-else
          class="card-numbers"
        >
          <span
            v-for="teamId in card.teams"
            :key="`${card.key}-${teamId}`"
            class="team-badge team-badge-main"
            :class="`team-${card.status}`"
          >{{ teamId }}</span>
        </div>

        <div class="card-location">
          <span
            class="location-label"
            :class="card.type === 'team' ? '' : 'location-label-special'"
          >{{ card.type === 'team' ? 'Location' : card.label }}</span>
          <span
            v-if="card.type === 'team'"
            class="location-value"
          >{{ card.location }}</span>
        </div>
      </div>
    </div>
    <p v-if="!currentRound">
      No round in progress.
    </p>
  </section>
</template>

<style scoped>
.display-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.cards-container {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  flex: 1;
}

.team-card {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: center;
  padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  min-height: 120px;
}

.card-numbers {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.9rem;
}

.team-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 5rem;
  height: 5rem;
  border-radius: 10px;
  font-size: 2.3rem;
  font-weight: 900;
  font-family: 'Courier New', monospace;
  background: var(--color-surface);
  color: #1f2937;
  border: 2px solid rgba(255, 255, 255, 0.35);
}

.team-badge-main {
  width: 6.6rem;
  height: 6.6rem;
  border-radius: 12px;
  font-size: 3.2rem;
  margin-right: 0.6rem;
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

.card-location {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  padding: 0 0.25rem;
  line-height: 1.1;
}

.location-label {
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #cbd5e1;
}

.location-label-special {
  font-size: 2rem;
  font-weight: 900;
  color: #f1f5f9;
  letter-spacing: 0.14em;
}

/* Keep special cards visually detached from the first team card */
.team-card-special + .team-card:not(.team-card-special) {
  margin-top: 2.4rem;
}

.location-value {
  font-size: 2.6rem;
  font-weight: 900;
  color: #f1f5f9;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.1em;
  text-align: center;
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