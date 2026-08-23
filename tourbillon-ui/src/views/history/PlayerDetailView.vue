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

    <p v-if="loading" class="muted">Loading player detail...</p>
    <p v-else-if="error" class="muted">Unable to load player detail.</p>

    <table v-else-if="sortedEditions.length">
      <thead>
        <tr>
          <th>Year</th>
          <th>Team</th>
          <th>Rank</th>
          <th>Wins</th>
          <th>Points</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in sortedEditions" :key="`${row.year}-${row.team}`">
          <td>{{ row.year }}</td>
          <td>{{ row.team }}</td>
          <td>{{ row.rank ?? '—' }}</td>
          <td>{{ row.wins }}</td>
          <td>{{ row.points }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="muted">No edition data available.</p>
  </section>
</template>
