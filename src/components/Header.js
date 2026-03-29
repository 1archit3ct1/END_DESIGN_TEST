/**
 * Header component with Logo, Navigation, and User Menu.
 */
export function Header() {
  const header = document.createElement('header')
  header.className = 'app-header'

  header.innerHTML = `
    <div class="header-left">
      <div class="logo">
        <div class="logo-mark">N</div>
        <span class="logo-text">NextAura</span>
      </div>
      <nav class="main-nav">
        <a href="#providers" class="nav-link" data-route="providers">Providers</a>
        <a href="#workflows" class="nav-link" data-route="workflows">Workflows</a>
        <a href="#status" class="nav-link" data-route="status">Status</a>
      </nav>
    </div>
    <div class="header-right">
      <div class="user-menu" tabindex="0">
        <button class="user-button">
          <span class="user-avatar">U</span>
          <span class="user-label">User</span>
          <span class="user-arrow">▼</span>
        </button>
        <div class="user-dropdown">
          <a href="#profile" class="dropdown-item" data-action="profile">Profile</a>
          <a href="#settings" class="dropdown-item" data-action="settings">Settings</a>
          <div class="dropdown-divider"></div>
          <a href="#logout" class="dropdown-item" data-action="logout">Logout</a>
        </div>
      </div>
    </div>
  `

  return header
}
