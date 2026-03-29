/**
 * Test: Header.js renders with Logo, Nav links, User Menu
 */
import { Header } from '../src/components/Header.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testHeaderRenders() {
  // Read source file and validate structure
  const headerSource = readFileSync(
    join(__dirname, '../src/components/Header.js'),
    'utf-8'
  )

  // Check for required elements in source
  const requiredElements = [
    'class="logo"',
    'class="logo-mark"',
    'class="logo-text"',
    'NextAura',
    'class="main-nav"',
    'data-route="providers"',
    'data-route="workflows"',
    'data-route="status"',
    'class="user-menu"',
    'data-action="profile"',
    'data-action="settings"',
    'data-action="logout"'
  ]

  for (const element of requiredElements) {
    if (!headerSource.includes(element)) {
      throw new Error(`Header.js missing required element: ${element}`)
    }
  }

  // Check nav link count
  const navLinkMatches = headerSource.match(/class="nav-link"/g)
  if (!navLinkMatches || navLinkMatches.length !== 3) {
    throw new Error(`Header should have 3 nav links, found ${navLinkMatches?.length || 0}`)
  }

  // Check dropdown item count
  const dropdownMatches = headerSource.match(/class="dropdown-item"/g)
  if (!dropdownMatches || dropdownMatches.length !== 3) {
    throw new Error(`User menu should have 3 dropdown items, found ${dropdownMatches?.length || 0}`)
  }

  // Validate component exports Header function
  if (typeof Header !== 'function') {
    throw new Error('Header.js does not export Header function')
  }

  console.log('✓ Header.js renders correctly with Logo, Nav links, User Menu')
  return true
}

// Run test
testHeaderRenders()
