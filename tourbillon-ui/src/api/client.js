// Lightweight fetch-based client for the TourBillon REST API.

export const API_ERROR_EVENT = 'tourbillon:api-error'
export const API_ERROR_CLEAR_EVENT = 'tourbillon:api-error-clear'
export const SETTINGS_UPDATED_EVENT = 'tourbillon:settings-updated'

export function pushApiError(message, status = null) {
  window.dispatchEvent(new CustomEvent(API_ERROR_EVENT, { detail: { message, status } }))
}

export function clearApiError() {
  window.dispatchEvent(new CustomEvent(API_ERROR_CLEAR_EVENT))
}

export function notifySettingsUpdated(settings) {
  window.dispatchEvent(new CustomEvent(SETTINGS_UPDATED_EVENT, { detail: settings }))
}

async function request(method, url, body, requestOptions = {}) {
  const { suppressErrorStatuses = [] } = requestOptions

  const fetchOptions = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) {
    fetchOptions.body = JSON.stringify(body)
  }
  const response = await fetch(url, fetchOptions)
  if (!response.ok) {
    let detail = response.statusText
    try {
      const data = await response.json()
      detail = data.detail || detail
    } catch {
      // Ignore body parsing errors.
    }
    const message = `${response.status}: ${detail}`
    const err = new Error(message)
    err.status = response.status
    err.detail = detail
    if (!suppressErrorStatuses.includes(response.status)) {
      pushApiError(message, response.status)
    }
    throw err
  }
  if (response.status === 204) {
    return null
  }
  return response.json()
}

// Upload a file as multipart/form-data. On error, throws an Error whose
// ``status`` property carries the HTTP status (e.g. 409 for a name conflict).
async function upload(url, file) {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(url, { method: 'POST', body: form })
  if (!response.ok) {
    let detail = response.statusText
    try {
      const data = await response.json()
      detail = data.detail || detail
    } catch {
      // Ignore body parsing errors.
    }
    const message = `${response.status}: ${detail}`
    pushApiError(message, response.status)
    const err = new Error(message)
    err.status = response.status
    throw err
  }
  return response.json()
}

export const api = {
  // Tournament
  getTournament: () =>
    request('GET', '/api/tournament', undefined, { suppressErrorStatuses: [404] }),
  createTournament: (payload) => request('POST', '/api/tournament', payload),
  loadTournament: (filename) => request('POST', '/api/tournament/load', { filename }),
  saveTournament: (filename) =>
    request(
      'POST',
      filename
        ? `/api/tournament/save?filename=${encodeURIComponent(filename)}`
        : '/api/tournament/save',
    ),
  deleteTournamentFile: () => request('DELETE', '/api/tournament/file'),
  deleteTournamentSave: (filename) =>
    request('DELETE', `/api/tournament/files/${encodeURIComponent(filename)}`),
  uploadTournament: (file, overwrite = false) =>
    upload(`/api/tournament/upload?overwrite=${overwrite ? 'true' : 'false'}`, file),

  // Teams
  listTeams: () => request('GET', '/api/teams'),
  createTeam: (payload) => request('POST', '/api/teams', payload),
  deleteTeam: (number) => request('DELETE', `/api/teams/${number}`),

  // Rounds
  listRounds: () => request('GET', '/api/rounds'),
  getRound: (number) => request('GET', `/api/rounds/${number}`),
  createRound: (payload) => request('POST', '/api/rounds', payload),
  deleteRound: (number) => request('DELETE', `/api/rounds/${number}`),
  setMatchResult: (round, match, points) =>
    request('PUT', `/api/rounds/${round}/matches/${match}`, { points }),

  // Rankings
  getRankings: (round) =>
    request('GET', round ? `/api/rankings?round=${round}` : '/api/rankings'),

  // Draws
  listDraws: () => request('GET', '/api/draws'),
  runDraw: (payload) => request('POST', '/api/draws/run', payload),

  // Settings
  getSettings: () => request('GET', '/api/settings'),
  updateSettings: async (values) => {
    const settings = await request('PUT', '/api/settings', values)
    notifySettingsUpdated(settings)
    return settings
  },

  // Display
  getDisplayView: () => request('GET', '/api/display/view'),
  setDisplayView: (view) => request('PUT', '/api/display/view', { view }),

  // History
  listHistoryTournaments: () => request('GET', '/api/history/tournaments'),
  listHistoryPlayers: () => request('GET', '/api/history/players'),  getHistoryPlayer: (name) =>
    request('GET', `/api/history/players/${encodeURIComponent(name)}`),

  // About
  getVersion: () => request('GET', '/api/version'),
}

// Open the draw-progress WebSocket.
export function openDrawSocket() {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return new WebSocket(`${proto}://${window.location.host}/ws/draw`)
}
