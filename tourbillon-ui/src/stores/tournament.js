import { defineStore } from 'pinia'
import { api } from '@/api/client'

export const useTournamentStore = defineStore('tournament', {
  state: () => ({
    tournament: null,
    teams: [],
    rounds: [],
    rankings: [],
    draws: [],
    historyPlayers: [],
    loading: false,
    error: null,
  }),
  getters: {
    exists: (state) => state.tournament !== null,
    status: (state) => (state.tournament ? state.tournament.status : null),
    currentRound: (state) =>
      state.rounds.length ? state.rounds[state.rounds.length - 1] : null,
  },
  actions: {
    async wrap(promise) {
      this.loading = true
      this.error = null
      try {
        return await promise
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async refreshTournament() {
      try {
        this.tournament = await api.getTournament()
      } catch (error) {
        this.tournament = null
      }
    },
    async refreshTeams() {
      this.teams = await api.listTeams()
    },
    async refreshRounds() {
      this.rounds = await api.listRounds()
    },
    async refreshRankings(round) {
      this.rankings = await api.getRankings(round)
    },
    async refreshDraws() {
      this.draws = await api.listDraws()
    },
    async refreshHistoryPlayers() {
      try {
        this.historyPlayers = await api.listHistoryPlayers()
      } catch (error) {
        this.historyPlayers = []
      }
    },
    async refreshAll() {
      await this.refreshTournament()
      if (this.tournament) {
        await Promise.all([
          this.refreshTeams(),
          this.refreshRounds(),
          this.refreshRankings(),
        ])
      }
    },
  },
})
