/**
 * ProviderCard component - displays provider logo, name, badge/button, and scope selector.
 */
import { ScopeSelector } from './ScopeSelector.js'

export function ProviderCard({ provider, isConnected, onConnect, onDisconnect }) {
  const card = document.createElement('div')
  card.className = 'provider-card'
  card.dataset.provider = provider.id

  card.innerHTML = `
    <div class="provider-card-header">
      <div class="provider-logo">
        <img src="${provider.logo}" alt="${provider.name}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" />
        <div class="provider-logo-fallback">${provider.name.charAt(0)}</div>
      </div>
      <div class="provider-status">
        ${isConnected 
          ? `<span class="connected-badge">✓ Connected</span>`
          : `<button class="connect-button">Connect</button>`
        }
      </div>
    </div>
    <div class="provider-card-body">
      <h3 class="provider-name">${provider.name}</h3>
      <div class="provider-actions">
        ${isConnected 
          ? `<button class="disconnect-button" data-action="disconnect">Disconnect</button>`
          : ''
        }
      </div>
    </div>
    <div class="provider-scope-container">
      <div class="scope-selector" data-provider="${provider.id}"></div>
    </div>
  `

  // Handle connect button
  const connectBtn = card.querySelector('.connect-button')
  if (connectBtn) {
    connectBtn.addEventListener('click', () => {
      if (onConnect) onConnect(provider.id)
    })
  }

  // Handle disconnect button
  const disconnectBtn = card.querySelector('.disconnect-button')
  if (disconnectBtn) {
    disconnectBtn.addEventListener('click', () => {
      if (onDisconnect) onDisconnect(provider.id)
    })
  }

  // Render scope selector
  const scopeContainer = card.querySelector('.scope-selector')
  if (scopeContainer) {
    const scopes = ['read', 'write', 'admin']
    const scopeSelector = ScopeSelector({
      providerId: provider.id,
      scopes,
      onChange: (selectedScopes) => {
        // Scope change handler
      }
    })
    scopeContainer.appendChild(scopeSelector)
  }

  return card
}
