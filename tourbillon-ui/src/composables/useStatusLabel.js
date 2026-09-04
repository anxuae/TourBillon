// Shared helper translating the business statuses returned by the API
// (`bye`, `won`, `lost`, `forfeit`, `in_progress`, ...) through the `status`
// section of the message catalogs. Unknown values fall back to the raw string
// so a new backend status is still readable instead of showing a missing key.
import { useI18n } from 'vue-i18n'

// Some backend statuses are structurally distinct but mean the same thing to
// the user. ``complete`` only differs from ``finished`` because the round is
// the last one of the tournament, which the UI already conveys through the
// round position: both are displayed as "finished". The raw codes stay
// untouched in the API and in the business logic.
const DISPLAY_ALIASES = {
  complete: 'finished',
}

export function useStatusLabel() {
  const { t, te } = useI18n()

  function statusLabel(raw) {
    const value = String(raw ?? '').trim()
    if (!value) {
      return ''
    }
    const alias = DISPLAY_ALIASES[value] ?? value
    const key = `status.${alias}`
    return te(key) ? t(key) : value
  }

  return { statusLabel }
}
