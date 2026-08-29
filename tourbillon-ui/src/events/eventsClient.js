import { onUnmounted } from 'vue'

let socket = null
let reconnectTimer = null
let started = false
let reconnectDelay = 1000

const listeners = new Map()

function clearReconnectTimer() {
  if (reconnectTimer !== null) {
    window.clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

function emit(event) {
  if (!event || typeof event.type !== 'string') return

  const handlers = listeners.get(event.type)
  if (!handlers) return

  for (const handler of [...handlers]) {
    try {
      handler(event)
    } catch (error) {
      console.error('[events] listener failed', error)
    }
  }
}

function scheduleReconnect() {
  if (!started || reconnectTimer !== null) return

  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null
    connect()
  }, reconnectDelay)

  reconnectDelay = Math.min(reconnectDelay * 2, 10000)
}

function connect() {
  if (!started || socket) return

  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const nextSocket = new WebSocket(`${proto}://${window.location.host}/ws/events`)
  socket = nextSocket

  nextSocket.addEventListener('open', () => {
    if (socket !== nextSocket) return
    reconnectDelay = 1000
  })

  nextSocket.addEventListener('message', (message) => {
    if (socket !== nextSocket) return

    try {
      emit(JSON.parse(message.data))
    } catch {
      // Ignore malformed websocket payloads.
    }
  })

  nextSocket.addEventListener('error', () => {
    // close() triggers the common reconnect path.
    if (socket === nextSocket) nextSocket.close()
  })

  nextSocket.addEventListener('close', () => {
    if (socket === nextSocket) socket = null
    scheduleReconnect()
  })
}

function start() {
  started = true
  clearReconnectTimer()
  connect()
}

function stop() {
  started = false
  clearReconnectTimer()
  reconnectDelay = 1000

  const current = socket
  socket = null
  if (current) current.close()
}

function on(type, handler) {
  if (!listeners.has(type)) listeners.set(type, new Set())
  const handlers = listeners.get(type)
  handlers.add(handler)

  return () => {
    handlers.delete(handler)
    if (handlers.size === 0) listeners.delete(type)
  }
}

export function useEvents() {
  const subscriptions = []

  function subscribe(type, handler) {
    const unsubscribe = on(type, handler)
    subscriptions.push(unsubscribe)
    return unsubscribe
  }

  onUnmounted(() => {
    for (const unsubscribe of subscriptions.splice(0)) unsubscribe()
  })

  return { subscribe }
}

export const events = {
  start,
  stop,
  on,
}
