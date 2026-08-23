<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '@/api/client'

const props = defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'saved'])

const form = ref(null)
const error = ref(null)
const saving = ref(false)

// The ``draws`` section is nested one level deeper (per algorithm) and is
// rendered separately; every other top-level key is a scalar section.
const DRAWS_KEY = 'draws'

// Load the settings each time the modal is opened.
watch(
  () => props.open,
  async (isOpen) => {
    if (!isOpen) return
    error.value = null
    try {
      form.value = await api.getSettings()
    } catch (err) {
      error.value = err.message
    }
  },
)

// Scalar sections (everything but ``draws``), as [name, fields] entries. The
// sections are defined by the backend, so nothing is redeclared here.
const scalarSections = computed(() =>
  form.value ? Object.entries(form.value).filter(([name]) => name !== DRAWS_KEY) : [],
)

function inputType(value) {
  if (typeof value === 'boolean') return 'checkbox'
  if (typeof value === 'number') return 'number'
  return 'text'
}

async function save() {
  saving.value = true
  error.value = null
  try {
    form.value = await api.updateSettings(form.value)
    emit('saved', form.value)
    emit('close')
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div v-if="open" class="overlay" @click.self="emit('close')">
    <div class="modal card" role="dialog" aria-modal="true" aria-label="Settings">
      <h2>Settings</h2>
      <p v-if="error" class="muted">Unable to load settings.</p>

      <form v-if="form" @submit.prevent="save">
        <fieldset v-for="[section, fields] in scalarSections" :key="section">
          <legend>{{ section }}</legend>
          <label v-for="(value, key) in fields" :key="key" class="field">
            <span class="label">{{ key }}</span>
            <input
              v-if="inputType(value) === 'checkbox'"
              type="checkbox"
              v-model="form[section][key]"
            />
            <input
              v-else-if="inputType(value) === 'number'"
              type="number"
              step="any"
              v-model.number="form[section][key]"
            />
            <input v-else type="text" v-model="form[section][key]" />
          </label>
        </fieldset>

        <fieldset v-for="(config, algo) in form.draws" :key="algo">
          <legend>Draw · {{ algo }}</legend>
          <label v-for="(value, option) in config" :key="option" class="field">
            <span class="label">{{ option }}</span>
            <input
              v-if="typeof value === 'boolean'"
              type="checkbox"
              v-model="form.draws[algo][option]"
            />
            <input
              v-else-if="typeof value === 'number'"
              type="number"
              step="any"
              v-model.number="form.draws[algo][option]"
            />
            <input v-else type="text" v-model="form.draws[algo][option]" />
          </label>
        </fieldset>

        <div class="actions">
          <button type="button" class="secondary" @click="emit('close')">Cancel</button>
          <button type="submit" :disabled="saving">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </form>
      <p v-else-if="!error" class="muted">Loading…</p>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: min(92vw, 520px);
  max-height: 85vh;
  overflow-y: auto;
  padding: 2rem;
}

.modal h2 {
  margin-top: 0;
}

fieldset {
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  margin: 0 0 1rem;
  padding: 0.75rem 1rem 1rem;
}

legend {
  font-weight: 600;
  padding: 0 0.5rem;
  text-transform: capitalize;
}

.field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.35rem 0;
}

.label {
  font-family: monospace;
  opacity: 0.85;
}

.field input[type='text'],
.field input[type='number'] {
  flex: 0 0 55%;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.secondary {
  background: none;
  border: 1px solid rgba(0, 0, 0, 0.2);
}
</style>
