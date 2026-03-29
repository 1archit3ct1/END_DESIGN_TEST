/**
 * ConnectionStatus UI component - live indicator, timestamp, disconnect button.
 */
export function ConnectionStatus({ providerId, isConnected, lastSynced, onDisconnect }) {
  const container = document.createElement('div')
  container.className = 'connection-status'
  container.dataset.provider = providerId

  const statusTime = lastSynced ? formatTimeAgo(lastSynced) : 'Never'

  container.innerHTML = `
    <div class="status-indicator">
      <span class="live-dot ${isConnected ? 'live' : 'offline'}"></span>
      <span class="status-text">${isConnected ? 'Connected' : 'Disconnected'}</span>
    </div>
    <div class="status-details">
      <span class="last-synced">Last synced: ${statusTime}</span>
      ${isConnected ? `
        <button class="disconnect-btn" data-provider="${providerId}">
          Disconnect
        </button>
      ` : ''}
    </div>
  `

  // Handle disconnect button click
  const disconnectBtn = container.querySelector('.disconnect-btn')
  if (disconnectBtn) {
    disconnectBtn.addEventListener('click', () => {
      if (onDisconnect) onDisconnect(providerId)
    })
  }

  return container
}

/**
 * Update connection status display.
 */
export function updateConnectionStatus(container, isConnected, lastSynced) {
  const liveDot = container.querySelector('.live-dot')
  const statusText = container.querySelector('.status-text')
  const lastSyncedEl = container.querySelector('.last-synced')
  const disconnectBtn = container.querySelector('.disconnect-btn')

  if (isConnected) {
    liveDot.classList.add('live')
    liveDot.classList.remove('offline')
    statusText.textContent = 'Connected'

    if (!disconnectBtn) {
      // Add disconnect button
      const details = container.querySelector('.status-details')
      const btn = document.createElement('button')
      btn.className = 'disconnect-btn'
      btn.textContent = 'Disconnect'
      btn.dataset.provider = container.dataset.provider
      details.appendChild(btn)
    }
  } else {
    liveDot.classList.remove('live')
    liveDot.classList.add('offline')
    statusText.textContent = 'Disconnected'

    if (disconnectBtn) {
      disconnectBtn.remove()
    }
  }

  if (lastSynced) {
    lastSyncedEl.textContent = `Last synced: ${formatTimeAgo(lastSynced)}`
  }
}

/**
 * Format timestamp as time ago.
 */
function formatTimeAgo(timestamp) {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = Math.floor((now - time) / 1000) // seconds

  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}
