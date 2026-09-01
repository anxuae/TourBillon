<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import ApiErrorBanner from '@/components/ApiErrorBanner.vue'
import { RouterView, useRoute } from 'vue-router'
import { events } from '@/events/eventsClient'

const route = useRoute()
const showApiErrorBanner = computed(() => !String(route.name || '').startsWith('display'))

onMounted(() => events.start())
onBeforeUnmount(() => events.stop())
</script>

<template>
  <ApiErrorBanner v-if="showApiErrorBanner" />
  <RouterView />
</template>
