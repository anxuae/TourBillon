// Lightweight fetch-based client for the TourBillon REST API.

async function request(method, url, body) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) {
    options.body = JSON.stringify(body)
  }
  const response = await fetch(url, options)
  if (!response.ok) {
    let detail = response.statusText
    try {
      const data = await response.json()
      detail = data.detail || detail
    } catch (error) {
      // Ignore body parsing errors.
    }
    throw new Error(`${response.status}: ${detail}`)
  }
  if (response.status === 204) {
    return null
  }
  return response.json()
}

export const api = {
  // Tournament
  getTournament: () => request('GET', '/api/tournament'),
  createTournament: (payload) => request('POST', '/api/tournament', payload),
  loadTournament: (filename) => request('POST', '/api/tournament/load', { filename }),
  saveTournament: () => request('POST', '/api/tournament/save'),

  // Teams
  listTeams: () => request('GET', '/api/teams'),
  createTeam: (payload) => request('POST', '/api/teams', payload),
  deleteTeam: (number) => request('DELETE', `/api/teams/${number}`),

  // Rounds
  listRounds: () => request('GET', '/api/rounds'),
  getRound: (number) => request('GET', `/api/rounds/${number}`),
  createRound: (payload) => request('POST', '/api/rounds', payload),
  setMatchResult: (round, match, points) =>
    request('PUT', `/api/rounds/${round}/matches/${match}`, { points }),

  // Rankings
  getRankings: (round) =>
    request('GET', round ? `/api/rankings?round=${round}` : '/api/rankings'),

  // Draws
  listDraws: () => request('GET', '/api/draws'),

  // History
  listHistoryTournaments: () => request('GET', '/api/history/tournaments'),
  listHistoryPlayers: () => request('GET', '/api/history/players'),
  getHistoryPlayer: (name) =>
    request('GET', `/api/history/players/${encodeURIComponent(name)}`),
}

// Open the draw-progress WebSocket.
export function openDrawSocket() {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return new WebSocket(`${proto}://${window.location.host}/ws/draw`)
}
