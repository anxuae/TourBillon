<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '@/api/client'
  import { useHistoryPlayers } from '@/composables/useHistoryPlayers'

const { t } = useI18n()
const route = useRoute()
// Forcing a reload keeps the players list (module-scope cache) in sync once
// a spelling has been rewritten from this view.
const { load: reloadHistoryPlayers } = useHistoryPlayers()

const detail = ref(null)
const loading = ref(false)
const error = ref(null)

const sortedEditions = computed(() => {
  if (!detail.value?.editions) {
    return []
  }
  return [...detail.value.editions].sort((left, right) => Number(left.year) - Number(right.year))
})

// Distinct spellings found in the save files: several of them means entries
// were merged, which lets the operator spot a wrong merge. The normalized
// display name is used (not the raw one) so a mere casing difference in the
// save file is not reported as a distinct spelling.
const spellings = computed(() => {
  const names = new Set()
  for (const row of sortedEditions.value) {
    const name = row.name || row.raw_name
    if (name) names.add(name)
  }
  return [...names]
})

function isDifferent(row) {
  const name = row?.name || row?.raw_name
  return Boolean(name) && name !== detail.value?.name
}

async function loadDetail() {
  loading.value = true
  error.value = null
  try {
    detail.value = await api.getHistoryPlayer(route.params.name)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// --- Bulk edit: rewrite the spelling directly in the save file(s) ---------
// This is a deliberate exception to the usual read-only history: hand-typed
// names are sometimes misspelled, and this view is the only place where
// every edition of a player is seen side by side, so it is also the most
// convenient place to fix a spelling once and for all (see backend
// `history.rename_players`).

function rowKey(row) {
  return `${row.filename}-${row.team}-${row.index}`
}

const selected = ref(new Set())

function toggleRow(row) {
  const key = rowKey(row)
  const next = new Set(selected.value)
  if (next.has(key)) {
    next.delete(key)
  } else {
    next.add(key)
  }
  selected.value = next
}

const allSelected = computed(
  () => sortedEditions.value.length > 0 && selected.value.size === sortedEditions.value.length,
)

function toggleSelectAll() {
  selected.value = allSelected.value ? new Set() : new Set(sortedEditions.value.map(rowKey))
}

const selectedRows = computed(() =>
  sortedEditions.value.filter((row) => selected.value.has(rowKey(row))),
)

const editing = ref(false)
const editFirstname = ref('')
const editLastname = ref('')
const saving = ref(false)
const saveError = ref(null)
const saveSuccess = ref(null)

function openEditPanel() {
  // Pre-fill with the current detail's nicest spelling, tweak from there
  const [firstname, ...rest] = (detail.value?.name || '').split(' ')
  editFirstname.value = firstname || ''
  editLastname.value = rest.join(' ')
  saveError.value = null
  saveSuccess.value = null
  editing.value = true
}

function closeEditPanel() {
  editing.value = false
}

async function applyBulkEdit() {
  saving.value = true
  saveError.value = null
  saveSuccess.value = null
  try {
    // Group the selected editions by save file: the API rewrites one file
    // at a time.
    const byFilename = new Map()
    for (const row of selectedRows.value) {
      const edits = byFilename.get(row.filename) || []
      edits.push({
        team: row.team,
        index: row.index,
        firstname: editFirstname.value.trim() || null,
        lastname: editLastname.value.trim() || null,
      })
      byFilename.set(row.filename, edits)
    }
    for (const [filename, edits] of byFilename) {
      await api.renameHistoryPlayers(filename, edits)
    }
    saveSuccess.value = t('history.renameSuccess', { count: selectedRows.value.length })
    selected.value = new Set()
    editing.value = false
    await loadDetail()
    reloadHistoryPlayers({ force: true })
  } catch (err) {
    saveError.value = err.message || t('history.renameError')
  } finally {
    saving.value = false
  }
}

onMounted(loadDetail)
</script>

<template>
  <section>
    <h1>{{ detail?.name || route.params.name }}</h1>

    <p
      v-if="loading"
      class="muted"
    >
      {{ t('history.detailLoading') }}
    </p>
    <p
      v-else-if="error"
      class="muted"
    >
      {{ t('history.detailError') }}
    </p>

    <template v-else>
      <p
        v-if="spellings.length > 1"
        class="merge-note"
      >
        {{ t('history.mergedFrom', { count: spellings.length }) }}
        <span
          v-for="spelling in spellings"
          :key="spelling"
          class="spelling"
        >{{ spelling }}</span>
      </p>

      <p
        v-if="saveSuccess"
        class="save-note success"
      >
        {{ saveSuccess }}
      </p>

      <div
        v-if="sortedEditions.length"
        class="toolbar"
      >
        <button
          type="button"
          class="secondary"
          @click="toggleSelectAll"
        >
          {{ t('history.selectAll') }}
        </button>
        <button
          type="button"
          :disabled="!selectedRows.length"
          @click="openEditPanel"
        >
          {{ t('history.editSelected', { count: selectedRows.length }) }}
        </button>
      </div>

      <div
        v-if="editing"
        class="edit-panel"
      >
        <header>
          <h2>{{ t('history.bulkEditTitle') }}</h2>
          <button
            type="button"
            class="close"
            :aria-label="t('common.close')"
            @click="closeEditPanel"
          >
            ×
          </button>
        </header>
        <p class="muted hint">
          {{ t('history.bulkEditHint') }}
        </p>
        <p
          v-if="saveError"
          class="save-note error"
        >
          {{ saveError }}
        </p>
        <div class="edit-fields">
          <label>
            {{ t('history.firstname') }}
            <input v-model="editFirstname">
          </label>
          <label>
            {{ t('history.lastname') }}
            <input v-model="editLastname">
          </label>
        </div>
        <div class="edit-actions">
          <button
            type="button"
            class="secondary"
            :disabled="saving"
            @click="closeEditPanel"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            type="button"
            :disabled="saving"
            @click="applyBulkEdit"
          >
            {{ t('history.apply') }}
          </button>
        </div>
      </div>

      <table v-if="sortedEditions.length">
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
              >
            </th>
            <th>{{ t('common.year') }}</th>
            <th>{{ t('history.colRegisteredAs') }}</th>
            <th>{{ t('common.team') }}</th>
            <th>{{ t('common.rank') }}</th>
            <th>{{ t('common.wins') }}</th>
            <th>{{ t('common.points') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in sortedEditions"
            :key="rowKey(row)"
          >
            <td>
              <input
                type="checkbox"
                :checked="selected.has(rowKey(row))"
                @change="toggleRow(row)"
              >
            </td>
            <td>{{ row.year }}</td>
            <td :class="{ different: isDifferent(row) }">
              {{ row.raw_name || '—' }}
            </td>
            <td>{{ row.team }}</td>
            <td>{{ row.rank ?? '—' }}</td>
            <td>{{ row.wins }}</td>
            <td>{{ row.points }}</td>
          </tr>
        </tbody>
      </table>
      <p
        v-else
        class="muted"
      >
        {{ t('history.noEditions') }}
      </p>
    </template>
  </section>
</template>

<style scoped>
.merge-note {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.9rem;
  font-size: 0.85rem;
  color: var(--color-text);
}

.spelling {
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 35%, transparent);
  border-radius: 999px;
  padding: 0.1rem 0.55rem;
}

/* Highlight a spelling that differs from the retained name */
.different {
  font-style: italic;
  opacity: 0.85;
}

.toolbar {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}

.save-note {
  margin-bottom: 0.8rem;
  font-size: 0.85rem;
}

.save-note.success {
  color: var(--color-primary);
}

.save-note.error {
  color: var(--status-lost-text, #b42318);
}

.edit-panel {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  margin-bottom: 1rem;
  background: var(--color-background-soft);
}

.edit-panel header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.edit-panel h2 {
  margin: 0;
  font-size: 1rem;
}

.edit-panel .close {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.1rem 0.4rem;
}

.hint {
  margin: 0.2rem 0 0.7rem;
}

.edit-fields {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 0.8rem;
}

.edit-fields label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}
</style>
