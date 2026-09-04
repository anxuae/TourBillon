import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import fr from './locales/fr.json'

// Frontend-only preference (the backend settings never carry UI preferences).
export const LOCALE_STORAGE_KEY = 'tourbillon.locale'

export const SUPPORTED_LOCALES = [
  { code: 'en', label: 'English' },
  { code: 'fr', label: 'Français' },
]

const FALLBACK_LOCALE = 'en'

function isSupported(code) {
  return SUPPORTED_LOCALES.some((locale) => locale.code === code)
}

/** Resolve the initial locale: stored preference, then browser, then fallback. */
function detectLocale() {
  try {
    const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY)
    if (isSupported(stored)) {
      return stored
    }
  } catch (err) {
    // Private browsing or disabled storage: fall through to detection.
    void err
  }
  const browser = String(window.navigator?.language || '').slice(0, 2)
  return isSupported(browser) ? browser : FALLBACK_LOCALE
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLocale(),
  fallbackLocale: FALLBACK_LOCALE,
  messages: { en, fr },
})

/** Change the active locale and persist it for the next visits. */
export function setLocale(code) {
  if (!isSupported(code)) {
    return
  }
  i18n.global.locale.value = code
  document.documentElement.setAttribute('lang', code)
  try {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, code)
  } catch (err) {
    // Persistence is best effort only.
    void err
  }
}

export function currentLocale() {
  return i18n.global.locale.value
}

document.documentElement.setAttribute('lang', i18n.global.locale.value)

export default i18n
