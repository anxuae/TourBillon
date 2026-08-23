<script setup>
import ApiErrorBanner from '@/components/ApiErrorBanner.vue'
import { RouterView } from 'vue-router'
</script>

<template>
  <ApiErrorBanner />
  <RouterView />
</template>
