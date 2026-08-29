<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import ApiErrorBanner from '@/components/ApiErrorBanner.vue'
import { RouterView } from 'vue-router'
import { events } from '@/events/eventsClient'
onMounted(() => events.start())
onBeforeUnmount(() => events.stop())
</script>

<template>
  <ApiErrorBanner />
  <RouterView />
</template>
