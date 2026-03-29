/**
 * WorkflowGate UI component - checklist, lock icon, unlock button.
 */
export function WorkflowGate({ requiredProviders = [], onUnlock }) {
  const container = document.createElement('div')
  container.className = 'workflow-gate'

  const allConnected = requiredProviders.length === 0

  container.innerHTML = `
    <div class="workflow-gate-header">
      <div class="gate-icon ${allConnected ? 'unlocked' : 'locked'}">
        ${allConnected ? '🔓' : '🔒'}
      </div>
      <h3 class="gate-title">${allConnected ? 'Workflow Unlocked' : 'Workflow Locked'}</h3>
    </div>
    <div class="workflow-gate-body">
      <div class="requirements-checklist">
        <h4 class="checklist-title">Required Providers:</h4>
        <ul class="checklist-items">
          ${requiredProviders.map(provider => `
            <li class="checklist-item" data-provider="${provider}">
              <span class="checkmark">${allConnected ? '✓' : '○'}</span>
              <span class="provider-name">${provider}</span>
            </li>
          `).join('')}
        </ul>
      </div>
      ${!allConnected ? `
        <div class="gate-message">
          <p>Connect all required providers to unlock the workflow.</p>
        </div>
      ` : `
        <button class="unlock-button" onclick="onUnlock && onUnlock()">
          Start Workflow
        </button>
      `}
    </div>
  `

  // Handle unlock button click
  const unlockBtn = container.querySelector('.unlock-button')
  if (unlockBtn) {
    unlockBtn.addEventListener('click', () => {
      if (onUnlock) onUnlock()
    })
  }

  return container
}

/**
 * Update gate status based on connected providers.
 */
export function updateGateStatus(container, connectedProviders) {
  const icon = container.querySelector('.gate-icon')
  const title = container.querySelector('.gate-title')
  const checklistItems = container.querySelectorAll('.checklist-item')

  checklistItems.forEach(item => {
    const provider = item.dataset.provider
    const isConnected = connectedProviders.includes(provider)
    const checkmark = item.querySelector('.checkmark')

    if (isConnected) {
      checkmark.textContent = '✓'
      item.classList.add('connected')
    } else {
      checkmark.textContent = '○'
      item.classList.remove('connected')
    }
  })

  const allConnected = connectedProviders.length >= checklistItems.length
  if (allConnected) {
    icon.classList.remove('locked')
    icon.classList.add('unlocked')
    icon.textContent = '🔓'
    title.textContent = 'Workflow Unlocked'
  } else {
    icon.classList.remove('unlocked')
    icon.classList.add('locked')
    icon.textContent = '🔒'
    title.textContent = 'Workflow Locked'
  }
}
