/**
 * ProviderGrid component - displays 6 provider cards in responsive grid.
 */
import { ProviderCard } from './ProviderCard.js'

const PROVIDERS = [
  { id: 'google', name: 'Google', logo: '/providers/google.svg' },
  { id: 'github', name: 'GitHub', logo: '/providers/github.svg' },
  { id: 'twitter', name: 'Twitter', logo: '/providers/twitter.svg' },
  { id: 'instagram', name: 'Instagram', logo: '/providers/instagram.svg' },
  { id: 'discord', name: 'Discord', logo: '/providers/discord.svg' },
  { id: 'meta', name: 'Meta', logo: '/providers/meta.svg' }
]

export function ProviderGrid({ onConnect, onDisconnect, connectedProviders = [] }) {
  const grid = document.createElement('div')
  grid.className = 'provider-grid'

  grid.innerHTML = `
    <div class="provider-grid-header">
      <h2 class="provider-grid-title">Connect Providers</h2>
      <p class="provider-grid-subtitle">Select and connect your OAuth providers</p>
    </div>
    <div class="provider-cards-container">
      ${PROVIDERS.map(provider => `
        <div class="provider-card-wrapper" data-provider="${provider.id}">
        </div>
      `).join('')}
    </div>
  `

  const cardWrappers = grid.querySelectorAll('.provider-card-wrapper')

  PROVIDERS.forEach((provider, index) => {
    const wrapper = cardWrappers[index]
    const isConnected = connectedProviders.includes(provider.id)

    const card = ProviderCard({
      provider,
      isConnected,
      onConnect: () => onConnect && onConnect(provider.id),
      onDisconnect: () => onDisconnect && onDisconnect(provider.id)
    })

    wrapper.appendChild(card)
  })

  return grid
}

/**
 * Get list of all providers.
 */
export function getProviders() {
  return [...PROVIDERS]
}
