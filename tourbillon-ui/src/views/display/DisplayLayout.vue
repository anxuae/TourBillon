<script setup>
import { onBeforeUnmount, onMounted, provide, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useTournamentStore } from '@/stores/tournament'
import { api, openDrawSocket } from '@/api/client'

const store = useTournamentStore()
const router = useRouter()
const route = useRoute()

const rotationSeconds = ref(12)
provide('displayRotationSeconds', rotationSeconds)

let socket = null

function syncView(view) {
  if (!view || route.name === view) return
  router.replace({ name: view })
}

async function refreshRotationSettings() {
  try {
    const settings = await api.getSettings()
    const raw = Number(settings?.display?.rotation_seconds)
    if (Number.isFinite(raw) && raw > 0) {
      rotationSeconds.value = raw
    }
  } catch {
  }
}

function connectSocket() {
  if (socket) {
    socket.close()
  }
  socket = openDrawSocket()
  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === 'display_view_changed' && payload.view) {
        syncView(payload.view)
      } else if (payload.type === 'tournament_changed') {
        store.refreshAll()
      }
    } catch {
    }
  }
}

onMounted(async () => {
  store.refreshAll()
  await refreshRotationSettings()
  try {
    const payload = await api.getDisplayView()
    syncView(payload.view)
  } catch {
  }
  connectSocket()
})

onBeforeUnmount(() => {
  if (socket) {
    socket.close()
    socket = null
  }
})
</script>

<template>
  <div class="display-layout">
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.display-layout {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
}

main {
  padding: 2rem;
  height: 100vh;
  overflow: hidden;
}
</style>
