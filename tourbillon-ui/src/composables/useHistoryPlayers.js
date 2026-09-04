// Shared history state: kept at module scope so navigating away from the
// players view and back does not restart the whole streaming load.
import { ref } from 'vue'
import { api } from '@/api/client'

const players = ref([])
const tournaments = ref([])
const editions = ref([])
const loading = ref(false)
const error = ref(null)
const loadedCount = ref(0)
// Distinct spellings seen across all editions: compared to the merged player
// count it gives the number of duplicates folded together
const spellingCount = ref(0)

let spellings = new Set()
let loadPromise = null
let loaded = false

// Strip diacritics so "Jose" and "José" are considered the same player
function foldAccents(text) {
  return (text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

// Compound names are typed inconsistently ("Jean-Paul", "Jean Paul", "JeanPaul"),
// so every separator (space, hyphen, apostrophe, dot) is dropped from the key.
// Must stay in sync with `_name_key()` in tourbillon/api/history.py, otherwise
// the players list and the player detail would not merge the same entries.
export function playerKey(name) {
  return foldAccents(name)
    .toLowerCase()
    .replace(/[\s\-'’.]+/g, '')
}

// Pick the nicest spelling: accents first, then the hyphenated form of
// compound names ("Jean-Paul" is preferred over "Jean Paul")
function betterName(current, candidate) {
  if (!current) return candidate
  const currentAccents = current !== foldAccents(current)
  const candidateAccents = candidate !== foldAccents(candidate)
  if (candidateAccents !== currentAccents) {
    return candidateAccents ? candidate : current
  }
  const currentHyphen = current.includes('-')
  const candidateHyphen = candidate.includes('-')
  if (candidateHyphen && !currentHyphen) return candidate
  return current
}

function mergeEdition(edition) {
  // Merge one edition into the aggregated player list, keeping it sorted.
  // Names are typed by hand, so entries are merged ignoring case and accents.
  const index = new Map(players.value.map((player) => [playerKey(player.name), player]))
  for (const row of edition.players) {
    const key = playerKey(row.name)
    if (!key) continue
    spellings.add(row.name)
    let entry = index.get(key)
    if (!entry) {
      entry = {
        name: row.name,
        firstname: row.firstname,
        lastname: row.lastname,
        participations: 0,
        wins: 0,
        points: 0,
        best_rank: null,
        years: [],
        // Distinct spellings folded into this player (used by the UI badge)
        spellings: [],
      }
      index.set(key, entry)
    }
    entry.participations += 1
    entry.wins += row.wins
    entry.points += row.points
    if (row.name && !entry.spellings.includes(row.name)) {
      entry.spellings.push(row.name)
    }
    // Keep the nicest spelling seen across the editions
    entry.firstname = betterName(entry.firstname, row.firstname)
    entry.lastname = betterName(entry.lastname, row.lastname)
    entry.name = `${entry.firstname} ${entry.lastname}`.trim()
    if (row.rank !== null && row.rank !== undefined) {
      if (entry.best_rank === null || row.rank < entry.best_rank) {
        entry.best_rank = row.rank
      }
    }
    entry.years.push(edition.year)
  }
  players.value = [...index.values()].sort((left, right) => left.name.localeCompare(right.name))
  spellingCount.value = spellings.size
}

async function runLoad() {
  loading.value = true
  error.value = null
  players.value = []
  editions.value = []
  loadedCount.value = 0
  spellings = new Set()
  spellingCount.value = 0
  try {
    tournaments.value = await api.listHistoryTournaments()
  } catch (err) {
    error.value = err.message
    loading.value = false
    loadPromise = null
    return
  }
  // Stream the editions one by one so results appear progressively
  for (const tournament of tournaments.value) {
    try {
      const edition = await api.getHistoryTournamentPlayers(tournament.filename)
      editions.value = [...editions.value, edition]
      mergeEdition(edition)
    } catch {
      // Ignore unreadable save files and keep streaming the others
    }
    loadedCount.value += 1
  }
  loading.value = false
  loaded = true
  loadPromise = null
}

export function useHistoryPlayers() {
  // Load once: a load already done or in flight is reused as is
  function load({ force = false } = {}) {
    if (force) {
      loaded = false
      loadPromise = null
    } else if (loaded || loadPromise) {
      return loadPromise ?? Promise.resolve()
    }
    loadPromise = runLoad()
    return loadPromise
  }

  return { players, tournaments, editions, loading, error, loadedCount, spellingCount, load }
}
