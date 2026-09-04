<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAutoDisplayPaging } from '@/composables/useAutoDisplayPaging'
import { useEvents } from '@/events/eventsClient'
import TeamBadge from '@/components/TeamBadge.vue'

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
    const points = match.points || {}
    const values = match.teams.map((id) => points[id])
    // Check if any score has been entered (not all zero)
    const hasScores = values.some((value) => value !== null && value !== undefined && value !== 0)

    for (const teamId of match.teams) {
      const teamPoints = points[teamId]
      cards.push({
        type: 'team',
        key: `team-${teamId}`,
        teamId,
        location: match.location ?? '—',
        points: hasScores && teamPoints !== null && teamPoints !== undefined ? teamPoints : null,
        opponents: match.teams
          .filter((t) => t !== teamId)
          .map((oppId) => ({
            id: oppId,
            status: matchResultStatus(match, oppId),
            points: hasScores && points[oppId] !== null && points[oppId] !== undefined ? points[oppId] : null,
          })),
        status: matchResultStatus(match, teamId),
      })
    }
  }
  return cards.sort((left, right) => left.teamId - right.teamId)
})

const specialCards = computed(() => {
  // Merge all special status teams into a single card with labels
  const byes = currentRound.value?.byes ?? []
  const forfeits = currentRound.value?.forfeits ?? []

  if (!byes.length && !forfeits.length) {
    return []
  }

  const allSpecialTeams = [
    ...byes.map((id) => ({ id, label: 'bye' })),
    ...forfeits.map((id) => ({ id, label: 'forfeit' })),
  ]

  return [
    {
      type: 'special',
      key: 'special-combined',
      teams: allSpecialTeams.sort((a, b) => a.id - b.id),
    },
  ]
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
          <TeamBadge
            :team="card.teamId"
            :status="card.status"
            :show-crown="card.status === 'won'"
            :points="card.points"
            size="lg"
          />
          <TeamBadge
            v-for="opponent in card.opponents"
            :key="`opp-${opponent.id}`"
            :team="opponent.id"
            :status="opponent.status"
            :show-crown="opponent.status === 'won'"
            :points="opponent.points"
            size="md"
          />
        </div>
        <div
          v-else
          class="card-numbers"
        >
          <TeamBadge
            v-for="team in card.teams"
            :key="`${card.key}-${team.id}`"
            :team="team.id"
            :status="team.label"
            :label="team.label"
            size="lg"
          />
        </div>

        <div class="card-location">
          <span
            class="location-label"
            :class="card.type === 'team' ? '' : 'location-label-special'"
          >{{ card.type === 'team' ? 'Location' : 'Special' }}</span>
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

.card-location {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  padding: 0 0.25rem;
  line-height: 1.1;
}

.location-label {
  font-size: 1.2rem;
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
  font-size: 3.2rem;
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