<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/api/client'

const { t } = useI18n()

const props = defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const info = ref(null)
const error = ref(null)

// Fetch the version lazily the first time the modal is opened.
watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen && info.value === null && error.value === null) {
      try {
        info.value = await api.getVersion()
      } catch (err) {
        error.value = err.message
      }
    }
  },
)
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
      :aria-label="t('about.ariaLabel')"
    >
      <h2>{{ t('about.title') }}</h2>
      <p
        v-if="error"
        class="muted"
      >
        {{ t('about.loadError') }}
      </p>
      <template v-else-if="info">
        <p class="name">
          {{ info.name }}
        </p>
        <p class="version">
          {{ t('about.version', { version: info.version }) }}
        </p>
      </template>
      <p
        v-else
        class="muted"
      >
        {{ t('common.loading') }}
      </p>
      <p class="muted tagline">
        {{ t('home.tagline') }}
      </p>
      <div class="actions">
        <button @click="emit('close')">
          {{ t('common.close') }}
        </button>
      </div>
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
  width: min(90vw, 360px);
  text-align: center;
  padding: 2rem;
}

.modal h2 {
  margin-top: 0;
}

.name {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0.5rem 0 0.25rem;
}

.version {
  margin: 0;
  font-variant-numeric: tabular-nums;
}

.tagline {
  margin-top: 1rem;
}

.actions {
  margin-top: 1.5rem;
}
</style>
