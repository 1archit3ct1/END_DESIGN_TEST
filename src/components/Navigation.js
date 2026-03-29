/**
 * Navigation component for route switching.
 */
export function Navigation({ onNavigate }) {
  const nav = document.createElement('nav')
  nav.className = 'app-navigation'

  const routes = [
    { id: 'providers', label: 'Providers' },
    { id: 'workflows', label: 'Workflows' },
    { id: 'status', label: 'Status' }
  ]

  nav.innerHTML = `
    <ul class="nav-list">
      ${routes.map(route => `
        <li class="nav-item">
          <a href="#${route.id}" class="nav-link" data-route="${route.id}">
            ${route.label}
          </a>
        </li>
      `).join('')}
    </ul>
  `

  // Handle navigation clicks
  nav.addEventListener('click', (e) => {
    const link = e.target.closest('.nav-link')
    if (link) {
      e.preventDefault()
      const route = link.dataset.route
      if (onNavigate) {
        onNavigate(route)
      }
    }
  })

  return nav
}

/**
 * Update active navigation link.
 */
export function setActiveRoute(routeId) {
  const links = document.querySelectorAll('.nav-link')
  links.forEach(link => {
    if (link.dataset.route === routeId) {
      link.classList.add('active')
    } else {
      link.classList.remove('active')
    }
  })
}
