import { openDrawSocket } from '@/api/client'

export function useDrawSocket({ onMessage, onOpen } = {}) {
  let socket = null
  let reconnectTimer = null
  let enabled = true

  function clearReconnect() {
    if (reconnectTimer) {
      window.clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  function disconnect() {
    enabled = false
    clearReconnect()
    if (socket) {
      socket.close()
      socket = null
    }
  }

  function connect() {
    enabled = true
    clearReconnect()

    if (socket) {
      socket.close()
    }

    socket = openDrawSocket()

    socket.addEventListener('open', () => {
      if (onOpen) {
        onOpen()
      }
    })

    socket.addEventListener('message', (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (onMessage) {
          onMessage(payload)
        }
      } catch {
      }
    })

    socket.addEventListener('close', () => {
      socket = null
      if (!enabled) return
      reconnectTimer = window.setTimeout(connect, 1000)
    })
  }

  return { connect, disconnect }
}
