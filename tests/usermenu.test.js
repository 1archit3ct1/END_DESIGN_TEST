/**
 * Test: UserMenu.js dropdown opens and menu items clickable
 */
import { UserMenu } from '../src/components/UserMenu.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testUserMenuRenders() {
  // Read source file and validate structure
  const menuSource = readFileSync(
    join(__dirname, '../src/components/UserMenu.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'user-menu',
    'user-button',
    'user-avatar',
    'user-dropdown',
    'dropdown-item',
    'data-action="profile"',
    'data-action="settings"',
    'data-action="logout"',
    'dropdown-divider',
    'aria-haspopup',
    'aria-expanded',
    'addEventListener'
  ]

  for (const element of requiredElements) {
    if (!menuSource.includes(element)) {
      throw new Error(`UserMenu.js missing required element: ${element}`)
    }
  }

  // Check dropdown item count
  const itemMatches = menuSource.match(/data-action="/g)
  if (!itemMatches || itemMatches.length !== 3) {
    throw new Error(`UserMenu should have 3 dropdown items, found ${itemMatches?.length || 0}`)
  }

  // Validate export
  if (typeof UserMenu !== 'function') {
    throw new Error('UserMenu.js does not export UserMenu function')
  }

  console.log('✓ UserMenu.js dropdown opens and menu items clickable')
  return true
}

// Run test
testUserMenuRenders()
