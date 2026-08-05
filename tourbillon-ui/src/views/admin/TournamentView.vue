<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTournamentStore } from '@/stores/tournament'

const store = useTournamentStore()
const { tournament, savedTournaments, loading } = storeToRefs(store)

// Default tournament title: "Tournoi Billon <today (YYYY-MM-DD)>".
function defaultTitle() {
  const today = new Date().toISOString().slice(0, 10)
  return `Tournoi Billon ${today}`
}

// New-tournament parameters, pre-filled with the usual defaults. These match
// the core Tournament defaults and are no longer stored in the settings.
const params = reactive({
  title: defaultTitle(),
  teams_by_match: 2,
  points_by_match: 12,
  players_by_team: 2,
})

const localError = ref(null)
const dragging = ref(false)
const fileInput = ref(null)

// Save button state derived from the tournament flags.
const autoSave = computed(() => !!(tournament.value && tournament.value.auto_save))
const hasChanges = computed(() => !!(tournament.value && tournament.value.changed))
const saveLabel = computed(() => (autoSave.value ? 'Auto Save' : 'Save'))
const saveDisabled = computed(() => loading.value || autoSave.value || !hasChanges.value)

// Base name of the currently loaded save file, if any.
const currentFile = computed(() => {
  const path = tournament.value && tournament.value.filename
  return path ? path.split(/[\\/]/).pop() : null
})

// Search query, shown only when there are more than 5 save files.
const search = ref('')
const showSearch = computed(() => savedTournaments.value.length > 5)

// Saved files sorted by last modification date (most recent first), then
// filtered by the search query when it applies.
const sortedTournaments = computed(() =>
  [...savedTournaments.value].sort((a, b) => (b.modified || 0) - (a.modified || 0)),
)

const filteredTournaments = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return sortedTournaments.value
  return sortedTournaments.value.filter((save) =>
    save.filename.toLowerCase().includes(query),
  )
})

onMounted(() => {
  store.refreshSavedTournaments()
})

function cleanParams() {
  // Numeric parameters: drop empty fields so the backend applies its own
  // defaults. The title is only used to name the save file.
  const out = {}
  for (const key of ['teams_by_match', 'points_by_match', 'players_by_team']) {
    const value = params[key]
    if (value !== null && value !== '') out[key] = Number(value)
  }
  if (params.title && params.title.trim()) out.title = params.title.trim()
  return out
}

async function createTournament() {
  localError.value = null
  try {
    await store.createTournament(cleanParams())
  } catch (err) {
    localError.value = err.message
  }
}

async function saveTournament() {
  localError.value = null
  try {
    await store.saveTournament()
  } catch (err) {
    localError.value = err.message
  }
}

async function loadFile(filename) {
  localError.value = null
  try {
    await store.loadTournament(filename)
  } catch (err) {
    localError.value = err.message
  }
}

// Accept only YAML save files.
function isYaml(file) {
  return /\.ya?ml$/i.test(file.name)
}

async function handleFile(file) {
  if (!file) return
  localError.value = null
  if (!isYaml(file)) {
    localError.value = 'Only .yml or .yaml save files are accepted.'
    return
  }
  try {
    await store.uploadTournament(file, false)
  } catch (err) {
    if (err.status === 409) {
      // A file with the same name already exists: ask before overwriting.
      const ok = window.confirm(
        `A save file named "${file.name}" already exists. Overwrite it?`,
      )
      if (!ok) return
      try {
        await store.uploadTournament(file, true)
      } catch (err2) {
        localError.value = err2.message
      }
    } else {
      localError.value = err.message
    }
  }
}

function onDrop(event) {
  dragging.value = false
  const file = event.dataTransfer.files && event.dataTransfer.files[0]
  handleFile(file)
}

function onPick(event) {
  const file = event.target.files && event.target.files[0]
  handleFile(file)
  event.target.value = ''
}
</script>

<template>
  <section class="tournament">
    <h1>Tournament</h1>

    <p v-if="localError" class="error">{{ localError }}</p>

    <div v-if="tournament" class="card current">
      <h2>Current tournament</h2>
      <p>
        <span class="badge">{{ tournament.status }}</span>
        {{ tournament.nb_teams }} teams · {{ tournament.nb_rounds }} rounds
      </p>
      <p class="muted">
        {{ tournament.teams_by_match }} teams/match ·
        {{ tournament.points_by_match }} points/match ·
        {{ tournament.players_by_team }} players/team
      </p>
      <p v-if="tournament.filename" class="muted">File: {{ tournament.filename }}</p>
      <p class="hint">
        A tournament is loaded: the other tabs are now available. Creating or
        loading another one will replace it.
      </p>
      <div class="save-row">
        <button
          type="button"
          class="save-btn"
          :class="{ 'auto-save': autoSave }"
          :disabled="saveDisabled"
          @click="saveTournament"
        >
          {{ saveLabel }}
        </button>
      </div>
    </div>

    <div class="grid">
      <form class="card" @submit.prevent="createTournament">
        <h2>New tournament</h2>
        <label class="field">
          <span>Title</span>
          <input type="text" v-model="params.title" />
        </label>
        <label class="field">
          <span>Teams per match</span>
          <input type="number" min="2" v-model.number="params.teams_by_match" />
        </label>
        <label class="field">
          <span>Points per match</span>
          <input type="number" min="1" v-model.number="params.points_by_match" />
        </label>
        <label class="field">
          <span>Players per team</span>
          <input type="number" min="1" v-model.number="params.players_by_team" />
        </label>
        <button type="submit" :disabled="loading">Create</button>
      </form>

      <form class="card" @submit.prevent>
        <h2>Load a tournament</h2>

        <div
          class="dropzone compact"
          :class="{ dragging }"
          @click="fileInput.click()"
          @dragover.prevent="dragging = true"
          @dragenter.prevent="dragging = true"
          @dragleave.prevent="dragging = false"
          @drop.prevent="onDrop"
        >
          <svg class="drop-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 3v10m0 0 4-4m-4 4-4-4M5 17v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <p class="drop-text">
            Drop a <strong>.yml</strong> / <strong>.yaml</strong> save file here
            <br /><span class="muted">or click to browse</span>
          </p>
          <input
            ref="fileInput"
            type="file"
            accept=".yml,.yaml"
            class="hidden-input"
            @change="onPick"
          />
        </div>

        <p v-if="!savedTournaments.length" class="muted">
          No save file found in the save directory.
        </p>
        <template v-else>
          <input
            v-if="showSearch"
            v-model="search"
            type="search"
            class="search-input"
            placeholder="Search a save file…"
          />
          <ul class="file-list scrollable">
            <li v-for="save in filteredTournaments" :key="save.filename">
              <button
                type="button"
                class="file-item"
                :class="{ current: save.filename === currentFile }"
                :disabled="loading"
                @click="loadFile(save.filename)"
              >
                <span class="file-name">{{ save.filename }}</span>
                <span class="muted">{{ save.nb_teams }} teams · {{ save.nb_rounds }} rounds</span>
              </button>
            </li>
            <li v-if="!filteredTournaments.length" class="muted no-match">
              No file matches “{{ search }}”.
            </li>
          </ul>
        </template>
      </form>
    </div>
  </section>
</template>

<style scoped>
.tournament {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 900px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.current .badge {
  margin-right: 0.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field input,
.field select {
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font: inherit;
}

button {
  align-self: flex-start;
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: #fff;
  font: inherit;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint {
  font-size: 0.85rem;
  color: var(--color-muted);
}

.save-row {
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

/* Green Save button: enabled when there are unsaved changes. */
.save-btn {
  background: #16a34a;
}

.save-btn:disabled {
  /* Keep the green tint when disabled because changes are already saved... */
  background: #16a34a;
  opacity: 0.5;
}

/* ...but turn grey when auto-save handles persistence automatically. */
.save-btn.auto-save:disabled {
  background: var(--color-muted, #9ca3af);
  opacity: 0.5;
}

.file-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

/* Scrollable file list: keeps the card compact with many save files. */
.file-list.scrollable {
  max-height: 320px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.search-input {
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font: inherit;
}

.no-match {
  padding: 0.5rem 0.25rem;
}

.file-item {
  width: 100%;
  align-self: stretch;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  color: inherit;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.file-item:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 6%, transparent);
}

/* Currently loaded save file. */
.file-item.current {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.file-name {
  font-weight: 600;
}

.dropzone {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 130px;
  padding: 1.25rem;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius);
  text-align: center;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.15s, background 0.15s;
}

.dropzone:hover {
  border-color: var(--color-primary);
}

/* Compact variant: leaves more room for the save-file list. */
.dropzone.compact {
  min-height: 76px;
  padding: 0.75rem;
}

.dropzone.compact .drop-icon {
  width: 60px;
  height: 60px;
}

.dropzone.compact .drop-text {
  font-size: 0.82rem;
}

.dropzone.dragging {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
}

/* Watermark drop icon sitting behind the text. */
.drop-icon {
  position: absolute;
  width: 96px;
  height: 96px;
  color: var(--color-border);
  opacity: 0.35;
  pointer-events: none;
}

.dropzone.dragging .drop-icon {
  color: var(--color-primary);
  opacity: 0.5;
}

.drop-text {
  position: relative;
  margin: 0;
  font-size: 0.9rem;
}

.hidden-input {
  display: none;
}
</style>
