/**
 * Task status writer - writes task_status.json on connect/revoke.
 */

const TASK_STATUS_KEY = 'task_status'

/**
 * Write task status entry.
 */
export function writeTaskStatus(entry) {
  const status = getTaskStatus()

  // Add entry to history
  if (!status.history) status.history = []
  status.history.push({
    ...entry,
    id: generateId(),
    writtenAt: new Date().toISOString()
  })

  // Update meta
  status.meta = status.meta || {}
  status.meta.lastUpdated = new Date().toISOString()
  status.meta.eventCount = status.history.length

  // Store in sessionStorage (browser) or localStorage for persistence
  try {
    sessionStorage.setItem(TASK_STATUS_KEY, JSON.stringify(status))
  } catch (e) {
    console.warn('Failed to write task_status:', e)
  }

  return status
}

/**
 * Get current task status.
 */
export function getTaskStatus() {
  try {
    const stored = sessionStorage.getItem(TASK_STATUS_KEY)
    if (stored) return JSON.parse(stored)
  } catch (e) {
    console.warn('Failed to read task_status:', e)
  }

  return {
    version: '1.0',
    meta: {
      createdAt: new Date().toISOString(),
      lastUpdated: null,
      eventCount: 0
    },
    history: []
  }
}

/**
 * Clear task status.
 */
export function clearTaskStatus() {
  try {
    sessionStorage.removeItem(TASK_STATUS_KEY)
  } catch (e) {
    console.warn('Failed to clear task_status:', e)
  }
}

/**
 * Generate unique ID.
 */
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Download task_status.json as file.
 */
export function downloadTaskStatus() {
  const status = getTaskStatus()
  const blob = new Blob([JSON.stringify(status, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'task_status.json'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
