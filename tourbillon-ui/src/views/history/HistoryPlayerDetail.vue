<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

const route = useRoute()

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

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    detail.value = await api.getHistoryPlayer(route.params.name)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <h1>{{ detail?.name || route.params.name }}</h1>

    <p
      v-if="loading"
      class="muted"
    >
      Loading player detail...
    </p>
    <p
      v-else-if="error"
      class="muted"
    >
      Unable to load player detail.
    </p>

    <template v-else>
      <p
        v-if="spellings.length > 1"
        class="merge-note"
      >
        Merged from {{ spellings.length }} spellings:
        <span
          v-for="spelling in spellings"
          :key="spelling"
          class="spelling"
        >{{ spelling }}</span>
      </p>

      <table v-if="sortedEditions.length">
        <thead>
          <tr>
            <th>Year</th>
            <th>Registered as</th>
            <th>Team</th>
            <th>Rank</th>
            <th>Wins</th>
            <th>Points</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in sortedEditions"
            :key="`${row.year}-${row.team}`"
          >
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
        No edition data available.
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
</style>
