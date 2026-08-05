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
    savedTournaments: [],
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
    async refreshSavedTournaments() {
      try {
        this.savedTournaments = await api.listHistoryTournaments()
      } catch (error) {
        this.savedTournaments = []
      }
    },
    async createTournament(params) {
      this.tournament = await this.wrap(api.createTournament(params))
      await this.refreshAll()
      return this.tournament
    },
    async loadTournament(filename) {
      this.tournament = await this.wrap(api.loadTournament(filename))
      await this.refreshAll()
      return this.tournament
    },
    async saveTournament(filename) {
      // Persist the current tournament, optionally under a new file name. The
      // backend returns the resolved path, which we mirror on the tournament.
      const res = await this.wrap(api.saveTournament(filename))
      await this.refreshTournament()
      await this.refreshSavedTournaments()
      return res
    },
    async uploadTournament(file, overwrite = false) {
      // May throw an Error with ``status === 409`` when the file name already
      // exists and overwrite is false: the caller handles the confirmation.
      this.tournament = await api.uploadTournament(file, overwrite)
      await this.refreshSavedTournaments()
      await this.refreshAll()
      return this.tournament
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
