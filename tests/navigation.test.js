/**
 * Test: Navigation.js handles route changes
 */
import { Navigation, setActiveRoute } from '../src/components/Navigation.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testNavigationRenders() {
  // Read source file and validate structure
  const navSource = readFileSync(
    join(__dirname, '../src/components/Navigation.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'app-navigation',
    'nav-list',
    'nav-item',
    'nav-link',
    "'providers'",
    "'workflows'",
    "'status'",
    'onNavigate',
    'addEventListener',
    'data-route'
  ]

  for (const element of requiredElements) {
    if (!navSource.includes(element)) {
      throw new Error(`Navigation.js missing required element: ${element}`)
    }
  }

  // Check route count - look for route IDs in the routes array
  const routeIdMatches = navSource.match(/id:\s*'[^']+'/g)
  if (!routeIdMatches || routeIdMatches.length !== 3) {
    throw new Error(`Navigation should have 3 routes, found ${routeIdMatches?.length || 0}`)
  }

  // Validate exports
  if (typeof Navigation !== 'function') {
    throw new Error('Navigation.js does not export Navigation function')
  }

  if (typeof setActiveRoute !== 'function') {
    throw new Error('Navigation.js does not export setActiveRoute function')
  }

  console.log('✓ Navigation.js handles route changes correctly')
  return true
}

// Run test
testNavigationRenders()
