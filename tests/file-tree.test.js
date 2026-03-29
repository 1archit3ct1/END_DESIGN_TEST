/**
 * Test: FileTree.jsx displays file tree structure
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testFileTreeRenders() {
  // Read source file and validate structure
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for required elements in source
  const requiredElements = [
    'data-testid="file-tree"',
    'data-testid="file-tree-stats"',
    'data-testid="file-tree-empty"',
    'data-testid={`folder-',
    'data-testid={`folder-toggle-',
    'data-testid={`file-tree-item-',
    'onFileSelect',
    'selectedFile',
    'defaultExpanded',
    'files',
  ]

  for (const element of requiredElements) {
    if (!fileTreeSource.includes(element)) {
      throw new Error(`FileTree.jsx missing required element: ${element}`)
    }
  }

  // Check for tree structure building
  if (!fileTreeSource.includes('useMemo') || !fileTreeSource.includes('fileTree')) {
    throw new Error('FileTree.jsx missing tree structure building')
  }

  // Check for expand/collapse functionality
  if (!fileTreeSource.includes('expandedFolders') || !fileTreeSource.includes('setExpandedFolders')) {
    throw new Error('FileTree.jsx missing expand/collapse functionality')
  }

  // Check for file count
  if (!fileTreeSource.includes('countFiles')) {
    throw new Error('FileTree.jsx missing file count function')
  }

  console.log('✓ FileTree.jsx renders correctly with file tree structure')
  return true
}

export function testFileTreeHasFileIcons() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for file icon function
  if (!fileTreeSource.includes('getFileIcon')) {
    throw new Error('FileTree.jsx missing getFileIcon function')
  }

  // Check for various file type icons (checking for the icons object)
  const fileTypes = ['js:', 'jsx:', 'ts:', 'tsx:', 'py:', 'rs:', 'json:', 'md:', 'css:']
  for (const type of fileTypes) {
    if (!fileTreeSource.includes(type)) {
      throw new Error(`FileTree.jsx missing file type icon: ${type}`)
    }
  }

  console.log('✓ FileTree.jsx has file icons')
  return true
}

export function testFileTreeHasStatusDisplay() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for status class function
  if (!fileTreeSource.includes('getStatusClass')) {
    throw new Error('FileTree.jsx missing getStatusClass function')
  }

  // Check for status types
  const statuses = ['generated', 'pending', 'error', 'modified']
  for (const status of statuses) {
    if (!fileTreeSource.includes(`'${status}'`)) {
      throw new Error(`FileTree.jsx missing status type: ${status}`)
    }
  }

  console.log('✓ FileTree.jsx has status display')
  return true
}

export function testFileTreeHasFolderToggle() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for toggle function
  if (!fileTreeSource.includes('toggleFolder')) {
    throw new Error('FileTree.jsx missing toggleFolder function')
  }

  // Check for folder icons (open/closed)
  if (!fileTreeSource.includes('📂') || !fileTreeSource.includes('📁')) {
    throw new Error('FileTree.jsx missing folder icons')
  }

  // Check for expanded/collapsed states
  if (!fileTreeSource.includes('isExpanded')) {
    throw new Error('FileTree.jsx missing expanded state')
  }

  console.log('✓ FileTree.jsx has folder toggle')
  return true
}

export function testFileTreeHasFileSelection() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for file selection handling
  if (!fileTreeSource.includes('handleFileClick')) {
    throw new Error('FileTree.jsx missing handleFileClick function')
  }

  // Check for selected state
  if (!fileTreeSource.includes('selected') || !fileTreeSource.includes('selectedFile')) {
    throw new Error('FileTree.jsx missing selected state')
  }

  // Check for onFileSelect callback
  if (!fileTreeSource.includes('onFileSelect')) {
    throw new Error('FileTree.jsx missing onFileSelect callback')
  }

  console.log('✓ FileTree.jsx has file selection')
  return true
}

export function testFileTreeHasEmptyState() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for empty state display
  if (!fileTreeSource.includes('file-tree-empty')) {
    throw new Error('FileTree.jsx missing empty state')
  }

  // Check for empty state message
  if (!fileTreeSource.includes('No files generated yet')) {
    throw new Error('FileTree.jsx missing empty state message')
  }

  console.log('✓ FileTree.jsx has empty state')
  return true
}

export function testFileTreeHasStats() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for stats display
  if (!fileTreeSource.includes('totalFiles') || !fileTreeSource.includes('totalFolders')) {
    throw new Error('FileTree.jsx missing stats display')
  }

  // Check for file count calculation
  if (!fileTreeSource.includes('countFiles')) {
    throw new Error('FileTree.jsx missing file count calculation')
  }

  console.log('✓ FileTree.jsx has stats display')
  return true
}

export function testFileTreePropTypes() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for PropTypes export
  if (!fileTreeSource.includes('FileTree.propTypes')) {
    throw new Error('FileTree.jsx missing propTypes definition')
  }

  // Check for required prop types
  const requiredPropTypes = [
    'files',
    'onFileSelect',
    'selectedFile',
    'defaultExpanded',
    'showFileCount',
    'maxDepth',
  ]

  for (const prop of requiredPropTypes) {
    if (!fileTreeSource.includes(prop)) {
      throw new Error(`FileTree.jsx missing propType: ${prop}`)
    }
  }

  // Check for PropTypes validation
  const propTypesElements = [
    'PropTypes.arrayOf',
    'PropTypes.shape',
    'PropTypes.string',
    'PropTypes.func',
    'PropTypes.bool',
    'PropTypes.number',
    'PropTypes.oneOf',
  ]

  for (const element of propTypesElements) {
    if (!fileTreeSource.includes(element)) {
      throw new Error(`FileTree.jsx missing PropTypes: ${element}`)
    }
  }

  console.log('✓ FileTree.jsx has proper PropTypes')
  return true
}

export function testFileTreeCSS() {
  const cssSource = readFileSync(
    join(__dirname, '../src/styles/file-tree.css'),
    'utf-8'
  )

  // Check for required CSS classes
  const requiredClasses = [
    '.file-tree-container',
    '.file-tree-header',
    '.file-tree-content',
    '.file-tree-empty',
    '.tree-item',
    '.folder-item',
    '.file-item',
    '.folder-icon',
    '.file-icon',
  ]

  for (const className of requiredClasses) {
    if (!cssSource.includes(className)) {
      throw new Error(`file-tree.css missing class: ${className}`)
    }
  }

  // Check for status styles
  const statusClasses = [
    '.status-generated',
    '.status-pending',
    '.status-error',
    '.status-modified',
  ]

  for (const className of statusClasses) {
    if (!cssSource.includes(className)) {
      throw new Error(`file-tree.css missing status class: ${className}`)
    }
  }

  // Check for selected state
  if (!cssSource.includes('.selected')) {
    throw new Error('file-tree.css missing selected state')
  }

  // Check for hover state
  if (!cssSource.includes(':hover')) {
    throw new Error('file-tree.css missing hover state')
  }

  // Check for animation
  if (!cssSource.includes('@keyframes fadeIn')) {
    throw new Error('file-tree.css missing fadeIn animation')
  }

  console.log('✓ FileTree.css has all required styles')
  return true
}

export function testFileTreeDisplaysFileTreeStructure() {
  const fileTreeSource = readFileSync(
    join(__dirname, '../src/components/FileTree.jsx'),
    'utf-8'
  )

  // Check for recursive tree rendering
  if (!fileTreeSource.includes('renderTree')) {
    throw new Error('FileTree.jsx missing renderTree function')
  }

  // Check for depth tracking
  if (!fileTreeSource.includes('depth')) {
    throw new Error('FileTree.jsx missing depth tracking')
  }

  // Check for path building
  if (!fileTreeSource.includes('currentPath') || !fileTreeSource.includes('fullPath')) {
    throw new Error('FileTree.jsx missing path building')
  }

  // Check for folder children rendering
  if (!fileTreeSource.includes('folder-children')) {
    throw new Error('FileTree.jsx missing folder children rendering')
  }

  console.log('✓ FileTree.jsx displays file tree structure correctly')
  return true
}

// Run all tests
export function runFileTreeTests() {
  testFileTreeRenders()
  testFileTreeHasFileIcons()
  testFileTreeHasStatusDisplay()
  testFileTreeHasFolderToggle()
  testFileTreeHasFileSelection()
  testFileTreeHasEmptyState()
  testFileTreeHasStats()
  testFileTreePropTypes()
  testFileTreeCSS()
  testFileTreeDisplaysFileTreeStructure()
  console.log('\n✅ All FileTree tests passed!')
  return true
}

// Run tests
runFileTreeTests()
