import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { api, SETTINGS_UPDATED_EVENT } from '@/api/client'

export function useRankingColumns(rankingsRef) {
  const rankingOptions = ref({
    rank_by_wins: true,
    rank_by_joker: true,
    rank_by_buchholz: true,
    rank_by_goal_avg: true,
  })

  const tieRanks = computed(() => {
    const counts = new Map()
    for (const row of rankingsRef.value) {
      counts.set(row.rank, (counts.get(row.rank) || 0) + 1)
    }
    return new Set([...counts.entries()].filter(([, count]) => count > 1).map(([rank]) => rank))
  })

  function isTieRank(rank) {
    return tieRanks.value.has(rank)
  }

  const showWins = computed(() => rankingOptions.value.rank_by_wins !== false)
  const showJoker = computed(() => rankingOptions.value.rank_by_joker !== false)
  const showBuchholz = computed(() => rankingOptions.value.rank_by_buchholz !== false)
  const showGoalAvg = computed(() => rankingOptions.value.rank_by_goal_avg !== false)

  async function refreshRankingOptions() {
    try {
      const settings = await api.getSettings()
      rankingOptions.value = {
        rank_by_wins: settings?.tournament?.rank_by_wins,
        rank_by_joker: settings?.tournament?.rank_by_joker,
        rank_by_buchholz: settings?.tournament?.rank_by_buchholz,
        rank_by_goal_avg: settings?.tournament?.rank_by_goal_avg,
      }
    } catch {
      rankingOptions.value = {
        rank_by_wins: true,
        rank_by_joker: true,
        rank_by_buchholz: true,
        rank_by_goal_avg: true,
      }
    }
  }

  function applyOptionsFromSettings(settings) {
    rankingOptions.value = {
      rank_by_wins: settings?.tournament?.rank_by_wins,
      rank_by_joker: settings?.tournament?.rank_by_joker,
      rank_by_buchholz: settings?.tournament?.rank_by_buchholz,
      rank_by_goal_avg: settings?.tournament?.rank_by_goal_avg,
    }
  }

  function onSettingsUpdated(event) {
    applyOptionsFromSettings(event?.detail)
  }

  onMounted(() => {
    window.addEventListener(SETTINGS_UPDATED_EVENT, onSettingsUpdated)
  })

  onBeforeUnmount(() => {
    window.removeEventListener(SETTINGS_UPDATED_EVENT, onSettingsUpdated)
  })

  return {
    tieRanks,
    isTieRank,
    showWins,
    showJoker,
    showBuchholz,
    showGoalAvg,
    refreshRankingOptions,
  }
}
