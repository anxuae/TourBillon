<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useTournamentStore } from '@/stores/tournament'
import { useStatusLabel } from '@/composables/useStatusLabel'
import { pushApiError } from '@/api/client'

const { t } = useI18n()
const { statusLabel } = useStatusLabel()
const store = useTournamentStore()
const { tournament, savedTournaments, loading } = storeToRefs(store)

// Default tournament title: "Tournoi Billon <today (YYYY-MM-DD)>".
function defaultTitle() {
  const today = new Date().toISOString().slice(0, 10)
  return `Tournoi Billon ${today}`
}

// New-tournament parameters, pre-filled with the usual defaults.
const params = reactive({
  title: defaultTitle(),
  teams_by_match: 2,
  points_by_match: 12,
  players_by_team: 2,
})

const dragging = ref(false)
const fileInput = ref(null)

// Save button state derived from the tournament flags.
const autoSave = computed(() => !!(tournament.value && tournament.value.auto_save))
const hasChanges = computed(() => !!(tournament.value && tournament.value.changed))
const saveLabel = computed(() => (autoSave.value ? t('tournament.autoSave') : t('common.save')))
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

function confirmReplaceWithUnsaved(actionLabel) {
  if (!hasChanges.value) return true
  return window.confirm(t('tournament.confirmUnsaved', { action: actionLabel }))
}

async function createTournament() {
  if (!confirmReplaceWithUnsaved(t('tournament.actionCreate'))) return
  try {
    await store.createTournament(cleanParams())
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

async function saveTournament() {
  try {
    await store.saveTournament()
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

async function deleteSavedFile(filename) {
  if (!filename) return
  const isCurrent = filename === currentFile.value
  if (isCurrent && !confirmReplaceWithUnsaved(t('tournament.actionDeleteCurrent'))) return
  const ok = window.confirm(t('tournament.confirmDeleteSave', { name: filename }))
  if (!ok) return
  try {
    await store.deleteTournamentSave(filename)
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

async function loadFile(filename) {
  if (!confirmReplaceWithUnsaved(t('tournament.actionLoad', { name: filename }))) return
  try {
    await store.loadTournament(filename)
  } catch {
    // API errors are handled globally by ApiErrorBanner.
  }
}

// Accept only YAML save files.
function isYaml(file) {
  return /\.ya?ml$/i.test(file.name)
}

async function handleFile(file) {
  if (!file) return
  if (!confirmReplaceWithUnsaved(t('tournament.actionLoad', { name: file.name }))) return
  if (!isYaml(file)) {
    pushApiError(t('tournament.onlyYaml'))
    return
  }
  try {
    await store.uploadTournament(file, false)
  } catch (err) {
    if (err.status === 409) {
      // A file with the same name already exists: ask before overwriting.
      const ok = window.confirm(t('tournament.confirmOverwrite', { name: file.name }))
      if (!ok) return
      try {
        await store.uploadTournament(file, true)
      } catch {
        // API errors are handled globally by ApiErrorBanner.
      }
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
    <h1>{{ t('tournament.title') }}</h1>

    <div
      v-if="tournament"
      class="card current"
    >
      <h2>{{ t('tournament.current') }}</h2>
      <p>
        <span class="badge">{{ statusLabel(tournament.status) }}</span>
        {{ t('tournament.summary', { teams: tournament.nb_teams, rounds: tournament.nb_rounds }) }}
      </p>
      <p class="muted">
        {{ t('tournament.config', {
          teamsByMatch: tournament.teams_by_match,
          pointsByMatch: tournament.points_by_match,
          playersByTeam: tournament.players_by_team,
        }) }}
      </p>
      <p
        v-if="tournament.filename"
        class="muted"
      >
        {{ t('tournament.fileLabel', { name: tournament.filename }) }}
      </p>
      <p class="hint">
        {{ t('tournament.hint') }}
      </p>
      <div class="save-row">
        <button
          type="button"
          class="action-btn"
          :disabled="saveDisabled"
          @click="saveTournament"
        >
          {{ saveLabel }}
        </button>
      </div>
    </div>

    <div class="grid">
      <form
        class="card"
        @submit.prevent="createTournament"
      >
        <h2>{{ t('tournament.newTitle') }}</h2>
        <label class="field">
          <span>{{ t('tournament.fieldTitle') }}</span>
          <input
            v-model="params.title"
            type="text"
          >
        </label>
        <label class="field">
          <span>{{ t('tournament.teamsPerMatch') }}</span>
          <input
            v-model.number="params.teams_by_match"
            type="number"
            min="2"
          >
        </label>
        <label class="field">
          <span>{{ t('tournament.pointsPerMatch') }}</span>
          <input
            v-model.number="params.points_by_match"
            type="number"
            min="1"
          >
        </label>
        <label class="field">
          <span>{{ t('tournament.playersPerTeam') }}</span>
          <input
            v-model.number="params.players_by_team"
            type="number"
            min="1"
          >
        </label>
        <button
          type="submit"
          class="action-btn create-btn"
          :disabled="loading"
        >
          {{ t('common.create') }}
        </button>
      </form>

      <form
        class="card"
        @submit.prevent
      >
        <h2>{{ t('tournament.loadTitle') }}</h2>

        <div
          class="dropzone compact"
          :class="{ dragging }"
          @click="fileInput.click()"
          @dragover.prevent="dragging = true"
          @dragenter.prevent="dragging = true"
          @dragleave.prevent="dragging = false"
          @drop.prevent="onDrop"
        >
          <svg
            class="drop-icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
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
            {{ t('tournament.dropPrefix') }} <strong>.yml</strong> / <strong>.yaml</strong> {{ t('tournament.dropSuffix') }}
            <br><span class="muted">{{ t('tournament.dropBrowse') }}</span>
          </p>
          <input
            ref="fileInput"
            type="file"
            accept=".yml,.yaml"
            class="hidden-input"
            @change="onPick"
          >
        </div>

        <p
          v-if="!savedTournaments.length"
          class="muted"
        >
          {{ t('tournament.noSaves') }}
        </p>
        <template v-else>
          <input
            v-if="showSearch"
            v-model="search"
            type="search"
            class="search-input"
            :placeholder="t('tournament.searchPlaceholder')"
          >
          <ul class="file-list scrollable">
            <li
              v-for="save in filteredTournaments"
              :key="save.filename"
              class="file-row"
              :class="{ current: save.filename === currentFile }"
            >
              <button
                type="button"
                class="file-item file-item-load"
                :disabled="loading"
                @click="loadFile(save.filename)"
              >
                <div class="file-info">
                  <span class="file-name">{{ save.filename }}</span>
                  <span class="muted">{{ t('tournament.saveSummary', { teams: save.nb_teams, rounds: save.nb_rounds }) }}</span>
                </div>
              </button>

              <button
                type="button"
                class="danger-outline file-delete-btn"
                :disabled="loading"
                :aria-label="t('tournament.deleteSaveAria', { name: save.filename })"
                @click="deleteSavedFile(save.filename)"
              >
                {{ t('common.delete') }}
              </button>
            </li>
            <li
              v-if="!filteredTournaments.length"
              class="muted no-match"
            >
              {{ t('tournament.noFileMatch', { query: search }) }}
            </li>
          </ul>
        </template>
      </form>
    </div>
  </section>
</template>

<style scoped>
.tournament {
  --action-btn-width: 9.2rem;
  --action-btn-height: 2.3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: none;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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

.current {
  padding: 1rem;
  gap: 0.45rem;
}

.current h2 {
  margin: 0;
}

.current p {
  margin: 0.15rem 0;
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

.action-btn {
  width: var(--action-btn-width);
  min-width: var(--action-btn-width);
  height: var(--action-btn-height);
  min-height: var(--action-btn-height);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.create-btn {
  align-self: center;
}

.hint {
  font-size: 0.85rem;
  color: var(--color-muted);
}

.save-row {
  margin-top: 0.35rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
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
.file-row {
  display: flex;
  align-items: stretch;
  gap: 0.5rem;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  transition: border-color 0.15s, background 0.15s;
}

.file-row:hover {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 6%, transparent);
}

/* Currently loaded save file. */
.file-row.current {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.file-item {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: transparent;
  color: inherit;
  border: 0;
  border-radius: calc(var(--radius) * 0.75);
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.file-item:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
}

.file-item.current {
  background: transparent;
}

.file-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
}

.file-delete-btn {
  flex: 0 0 auto;
  min-width: 5.8rem;
  align-self: center;
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
