import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { SUPPORTED_LOCALES, setLocale } from '@/i18n'

/** Expose the active locale and the list of selectable languages. */
export function useLocale() {
  const { locale } = useI18n()

  const selectedLocale = computed({
    get: () => locale.value,
    set: (code) => setLocale(code),
  })

  return { selectedLocale, locales: SUPPORTED_LOCALES }
}
