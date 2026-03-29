/**
 * ScopeSelector component - Read, Write, Admin toggles.
 */
export function ScopeSelector({ providerId, scopes = ['read', 'write', 'admin'], onChange }) {
  const container = document.createElement('div')
  container.className = 'scope-selector'
  container.dataset.provider = providerId

  container.innerHTML = `
    <div class="scope-label">Scopes:</div>
    <div class="scope-toggles">
      ${scopes.map(scope => `
        <label class="scope-toggle">
          <input type="checkbox" data-scope="${scope}" class="scope-checkbox" />
          <span class="scope-name">${scope.charAt(0).toUpperCase() + scope.slice(1)}</span>
        </label>
      `).join('')}
    </div>
  `

  // Handle scope changes
  const checkboxes = container.querySelectorAll('.scope-checkbox')
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      const selectedScopes = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.scope)

      if (onChange) onChange(selectedScopes)
    })
  })

  return container
}

/**
 * Get selected scopes from a scope selector.
 */
export function getSelectedScopes(container) {
  const checkboxes = container.querySelectorAll('.scope-checkbox')
  return Array.from(checkboxes)
    .filter(cb => cb.checked)
    .map(cb => cb.dataset.scope)
}
