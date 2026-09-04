<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/api/client'
import { useLocale } from '@/composables/useLocale'

const { t, te } = useI18n()
const { selectedLocale, locales } = useLocale()

// Section and option names come from the backend as technical keys. They are
// translated when a matching entry exists and shown raw otherwise, so a new
// backend key stays readable instead of displaying a missing translation.
function sectionLabel(name) {
  const key = `settings.sections.${name}`
  return te(key) ? t(key) : name
}

function fieldLabel(name) {
  const key = `settings.fields.${name}`
  return te(key) ? t(key) : name
}

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

// The language selector is a UI-only preference rendered on top of this section.
const GENERAL_KEY = 'general'

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
// sections are defined by the backend, so nothing is redeclared here; only the
// general one is pinned first because it hosts the language selector.
const scalarSections = computed(() => {
  if (!form.value) {
    return []
  }
  const sections = Object.entries(form.value).filter(([name]) => name !== DRAWS_KEY)
  return sections.sort(([a], [b]) => Number(b === GENERAL_KEY) - Number(a === GENERAL_KEY))
})

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
  <div
    v-if="open"
    class="overlay"
    @click.self="emit('close')"
  >
    <div
      class="modal card"
      role="dialog"
      aria-modal="true"
      :aria-label="t('settings.title')"
    >
      <h2>{{ t('settings.title') }}</h2>
      <p
        v-if="error"
        class="muted"
      >
        {{ t('settings.loadError') }}
      </p>

      <form
        v-if="form"
        class="settings-form"
        @submit.prevent="save"
      >
        <div class="settings-scroll">
          <fieldset
            v-for="[section, fields] in scalarSections"
            :key="section"
          >
            <legend>{{ sectionLabel(section) }}</legend>
            <!-- UI-only preference: stored in the browser, never sent to the API -->
            <label
              v-if="section === GENERAL_KEY"
              class="field"
            >
              <span class="label">{{ t('settings.language') }}</span>
              <select v-model="selectedLocale">
                <option
                  v-for="locale in locales"
                  :key="locale.code"
                  :value="locale.code"
                >
                  {{ locale.label }}
                </option>
              </select>
            </label>
            <label
              v-for="(value, key) in fields"
              :key="key"
              class="field"
            >
              <span class="label">{{ fieldLabel(key) }}</span>
              <input
                v-if="inputType(value) === 'checkbox'"
                v-model="form[section][key]"
                type="checkbox"
                class="visually-hidden"
              >
              <span
                v-if="inputType(value) === 'checkbox'"
                class="field-switch"
                aria-hidden="true"
              >
                <span class="field-switch-slider" />
              </span>
              <input
                v-else-if="inputType(value) === 'number'"
                v-model.number="form[section][key]"
                type="number"
                step="any"
              >
              <input
                v-else
                v-model="form[section][key]"
                type="text"
              >
            </label>
          </fieldset>

          <fieldset
            v-for="(config, algo) in form.draws"
            :key="algo"
          >
            <legend>{{ t('settings.drawSection', { algorithm: algo }) }}</legend>
            <label
              v-for="(value, option) in config"
              :key="option"
              class="field"
            >
              <span class="label">{{ fieldLabel(option) }}</span>
              <input
                v-if="typeof value === 'boolean'"
                v-model="form.draws[algo][option]"
                type="checkbox"
                class="visually-hidden"
              >
              <span
                v-if="typeof value === 'boolean'"
                class="field-switch"
                aria-hidden="true"
              >
                <span class="field-switch-slider" />
              </span>
              <input
                v-else-if="typeof value === 'number'"
                v-model.number="form.draws[algo][option]"
                type="number"
                step="any"
              >
              <input
                v-else
                v-model="form.draws[algo][option]"
                type="text"
              >
            </label>
          </fieldset>
        </div>

        <div class="actions">
          <button
            type="button"
            class="secondary action-btn"
            @click="emit('close')"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            type="submit"
            class="action-btn"
            :disabled="saving"
          >
            {{ saving ? t('common.saving') : t('common.save') }}
          </button>
        </div>
      </form>
      <p
        v-else-if="!error"
        class="muted"
      >
        {{ t('common.loading') }}
      </p>
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
  overflow: hidden;
  padding: 2rem;
  display: flex;
  flex-direction: column;
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

.settings-form {
  min-height: 0;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
}

.settings-scroll {
  min-height: 0;
  overflow-y: auto;
  padding-right: 0.2rem;
}

legend {
  font-weight: 600;
  padding: 0 0.5rem;
}

.field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.35rem 0;
}

.field:has(.visually-hidden) {
  cursor: pointer;
}

.label {
  opacity: 0.85;
}

.visually-hidden {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
  pointer-events: none;
}

.field-switch {
  position: relative;
  display: inline-flex;
  width: 2.2rem;
  height: 1.25rem;
  flex: 0 0 auto;
}

.field-switch-slider {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: #cbd5e1;
  transition: background 0.2s ease;
}

.field-switch-slider::before {
  content: '';
  position: absolute;
  left: 2px;
  top: 50%;
  width: 0.85rem;
  height: 0.85rem;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transform: translateY(-50%);
  transition: transform 0.2s ease;
}

.field .visually-hidden:checked + .field-switch .field-switch-slider {
  background: color-mix(in srgb, var(--color-primary) 70%, #1d4ed8);
}

.field .visually-hidden:checked + .field-switch .field-switch-slider::before {
  transform: translate(0.95rem, -50%);
}

.field .visually-hidden:focus-visible + .field-switch .field-switch-slider {
  outline: 2px solid color-mix(in srgb, var(--color-primary) 55%, white);
  outline-offset: 2px;
}

.field input[type='text'],
.field input[type='number'],
.field select {
  flex: 0 0 55%;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.action-btn {
  width: 9.2rem;
  min-width: 9.2rem;
  min-height: 2.3rem;
}

.secondary {
  background: none;
  border: 1px solid rgba(0, 0, 0, 0.2);
}
</style>
