/**
 * UserMenu component with dropdown (Profile, Settings, Logout).
 */
export function UserMenu({ onProfile, onSettings, onLogout }) {
  const menu = document.createElement('div')
  menu.className = 'user-menu'
  menu.tabIndex = 0

  menu.innerHTML = `
    <button class="user-button" aria-haspopup="true" aria-expanded="false">
      <span class="user-avatar">U</span>
      <span class="user-label">User</span>
      <span class="user-arrow">▼</span>
    </button>
    <div class="user-dropdown" role="menu">
      <a href="#profile" class="dropdown-item" data-action="profile" role="menuitem">
        Profile
      </a>
      <a href="#settings" class="dropdown-item" data-action="settings" role="menuitem">
        Settings
      </a>
      <div class="dropdown-divider"></div>
      <a href="#logout" class="dropdown-item" data-action="logout" role="menuitem">
        Logout
      </a>
    </div>
  `

  const button = menu.querySelector('.user-button')
  const dropdown = menu.querySelector('.user-dropdown')

  // Toggle dropdown on button click
  button.addEventListener('click', (e) => {
    e.stopPropagation()
    const isExpanded = button.getAttribute('aria-expanded') === 'true'
    button.setAttribute('aria-expanded', !isExpanded)
    dropdown.classList.toggle('open')
  })

  // Handle dropdown item clicks
  dropdown.addEventListener('click', (e) => {
    const item = e.target.closest('.dropdown-item')
    if (item) {
      const action = item.dataset.action
      dropdown.classList.remove('open')
      button.setAttribute('aria-expanded', 'false')

      if (action === 'profile' && onProfile) onProfile()
      if (action === 'settings' && onSettings) onSettings()
      if (action === 'logout' && onLogout) onLogout()
    }
  })

  // Close dropdown on outside click
  document.addEventListener('click', (e) => {
    if (!menu.contains(e.target)) {
      dropdown.classList.remove('open')
      button.setAttribute('aria-expanded', 'false')
    }
  })

  // Keyboard navigation
  menu.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      dropdown.classList.remove('open')
      button.setAttribute('aria-expanded', 'false')
    }
  })

  return menu
}
