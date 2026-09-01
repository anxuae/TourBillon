import { computed } from 'vue'

export function useRankingTeams(teamsRef) {
  const teamsByNumber = computed(() => new Map(teamsRef.value.map((team) => [team.number, team])))

  function playerLabel(player) {
    const firstname = (player.firstname || '').trim()
    const lastname = (player.lastname || '').trim()
    return [firstname, lastname].filter(Boolean).join(' ')
  }

  function teamPlayers(teamNumber) {
    const team = teamsByNumber.value.get(teamNumber)
    if (!team) {
      return []
    }
    return team.players.map((player) => playerLabel(player)).filter(Boolean)
  }

  return {
    teamsByNumber,
    playerLabel,
    teamPlayers,
  }
}
