/**
 * Test: BuildConsole.jsx renders with start/stop buttons
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testBuildConsoleRenders() {
  // Read source file and validate structure
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for required elements in source
  const requiredElements = [
    'data-testid="build-console"',
    'data-testid="build-status"',
    'data-testid="start-build-button"',
    'data-testid="stop-build-button"',
    'data-testid="build-progress"',
    'data-testid="progress-bar-fill"',
    'data-testid="file-count"',
    'data-testid="task-progress"',
    'data-testid="build-logs"',
    'onBuildStart',
    'onBuildStop',
    'buildStatus',
    'completedTasks',
    'totalTasks',
    'generatedFiles',
    'currentTask',
  ]

  for (const element of requiredElements) {
    if (!buildConsoleSource.includes(element)) {
      throw new Error(`BuildConsole.jsx missing required element: ${element}`)
    }
  }

  // Check for status states
  const statusStates = ['idle', 'running', 'done', 'error']
  for (const status of statusStates) {
    if (!buildConsoleSource.includes(`'${status}'`) && !buildConsoleSource.includes(`"${status}"`)) {
      throw new Error(`BuildConsole.jsx missing status state: ${status}`)
    }
  }

  // Check for PropTypes validation
  const propTypesElements = [
    'PropTypes.func',
    'PropTypes.number',
    'PropTypes.string',
    'PropTypes.arrayOf',
    'PropTypes.oneOf',
  ]

  for (const element of propTypesElements) {
    if (!buildConsoleSource.includes(element)) {
      throw new Error(`BuildConsole.jsx missing PropTypes: ${element}`)
    }
  }

  // Check for CSS import
  if (!buildConsoleSource.includes('../styles/build-console.css')) {
    throw new Error('BuildConsole.jsx missing CSS import')
  }

  // Check for expand/collapse functionality
  if (!buildConsoleSource.includes('isExpanded') || !buildConsoleSource.includes('setIsExpanded')) {
    throw new Error('BuildConsole.jsx missing expand/collapse functionality')
  }

  // Check for auto-scroll functionality
  if (!buildConsoleSource.includes('scrollIntoView')) {
    throw new Error('BuildConsole.jsx missing auto-scroll functionality')
  }

  console.log('✓ BuildConsole.jsx renders correctly with start/stop buttons')
  return true
}

export function testBuildConsoleHasStartButton() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for Start Build button
  if (!buildConsoleSource.includes('Start Build') && !buildConsoleSource.includes('▶ Start')) {
    throw new Error('BuildConsole.jsx missing Start Build button')
  }

  // Check button is disabled when running
  if (!buildConsoleSource.includes('disabled={buildStatus === \'running\'}')) {
    throw new Error('BuildConsole.jsx Start button should be disabled when running')
  }

  console.log('✓ BuildConsole.jsx has Start Build button')
  return true
}

export function testBuildConsoleHasStopButton() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for Stop button
  if (!buildConsoleSource.includes('Stop') && !buildConsoleSource.includes('⏹')) {
    throw new Error('BuildConsole.jsx missing Stop button')
  }

  // Check stop button handler
  if (!buildConsoleSource.includes('handleStopClick') && !buildConsoleSource.includes('onBuildStop')) {
    throw new Error('BuildConsole.jsx missing Stop button handler')
  }

  console.log('✓ BuildConsole.jsx has Stop button')
  return true
}

export function testBuildConsoleHasStatusIndicator() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for status badge
  if (!buildConsoleSource.includes('status-badge')) {
    throw new Error('BuildConsole.jsx missing status badge')
  }

  // Check for status configurations
  const statusClasses = [
    'status-idle',
    'status-running',
    'status-done',
    'status-error',
  ]

  for (const className of statusClasses) {
    if (!buildConsoleSource.includes(className)) {
      throw new Error(`BuildConsole.jsx missing status class: ${className}`)
    }
  }

  console.log('✓ BuildConsole.jsx has status indicator')
  return true
}

export function testBuildConsoleHasProgressDisplay() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for progress elements
  const progressElements = [
    'build-progress',
    'progress-bar',
    'progress-fill',
    'progress-percent',
  ]

  for (const element of progressElements) {
    if (!buildConsoleSource.includes(element)) {
      throw new Error(`BuildConsole.jsx missing progress element: ${element}`)
    }
  }

  // Check for task count display
  if (!buildConsoleSource.includes('completedTasks') || !buildConsoleSource.includes('totalTasks')) {
    throw new Error('BuildConsole.jsx missing task count display')
  }

  // Check for percentage calculation
  if (!buildConsoleSource.includes('Math.round') && !buildConsoleSource.includes('* 100')) {
    throw new Error('BuildConsole.jsx missing percentage calculation')
  }

  console.log('✓ BuildConsole.jsx has progress display')
  return true
}

export function testBuildConsoleHasFileCount() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for file count display
  if (!buildConsoleSource.includes('generatedFiles')) {
    throw new Error('BuildConsole.jsx missing file count display')
  }

  // Check for file count testid
  if (!buildConsoleSource.includes('data-testid="file-count"')) {
    throw new Error('BuildConsole.jsx missing file count testid')
  }

  console.log('✓ BuildConsole.jsx has file count indicator')
  return true
}

export function testBuildConsoleHasLogs() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for logs section
  if (!buildConsoleSource.includes('build-logs')) {
    throw new Error('BuildConsole.jsx missing logs section')
  }

  // Check for log entry rendering
  if (!buildConsoleSource.includes('log-entry')) {
    throw new Error('BuildConsole.jsx missing log entry rendering')
  }

  // Check for log levels
  const logLevels = ['error', 'warn', 'info', 'success']
  for (const level of logLevels) {
    if (!buildConsoleSource.includes(`'${level}'`) && !buildConsoleSource.includes(`"${level}"`)) {
      throw new Error(`BuildConsole.jsx missing log level: ${level}`)
    }
  }

  console.log('✓ BuildConsole.jsx has logs display')
  return true
}

export function testBuildConsoleHasSkipTaskButton() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for Skip Task button
  if (!buildConsoleSource.includes('Skip Task') && !buildConsoleSource.includes('⏭')) {
    throw new Error('BuildConsole.jsx missing Skip Task button')
  }

  // Check for skip task testid
  if (!buildConsoleSource.includes('data-testid="skip-task-button"')) {
    throw new Error('BuildConsole.jsx missing skip-task-button testid')
  }

  // Check for onSkipTask prop
  if (!buildConsoleSource.includes('onSkipTask')) {
    throw new Error('BuildConsole.jsx missing onSkipTask prop')
  }

  // Check for currentTaskId prop (needed for skip functionality)
  if (!buildConsoleSource.includes('currentTaskId')) {
    throw new Error('BuildConsole.jsx missing currentTaskId prop')
  }

  // Check for handleSkipTaskClick handler
  if (!buildConsoleSource.includes('handleSkipTaskClick')) {
    throw new Error('BuildConsole.jsx missing handleSkipTaskClick handler')
  }

  console.log('✓ BuildConsole.jsx has Skip Task button')
  return true
}

export function testBuildConsoleHasRetryFailedTasksButton() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for Retry Failed Tasks button
  if (!buildConsoleSource.includes('Retry') && !buildConsoleSource.includes('🔄')) {
    throw new Error('BuildConsole.jsx missing Retry Failed Tasks button')
  }

  // Check for retry failed tasks testid
  if (!buildConsoleSource.includes('data-testid="retry-failed-tasks-button"')) {
    throw new Error('BuildConsole.jsx missing retry-failed-tasks-button testid')
  }

  // Check for onRetryFailedTasks prop
  if (!buildConsoleSource.includes('onRetryFailedTasks')) {
    throw new Error('BuildConsole.jsx missing onRetryFailedTasks prop')
  }

  // Check for failedTasks prop
  if (!buildConsoleSource.includes('failedTasks')) {
    throw new Error('BuildConsole.jsx missing failedTasks prop')
  }

  // Check for handleRetryFailedTasksClick handler
  if (!buildConsoleSource.includes('handleRetryFailedTasksClick')) {
    throw new Error('BuildConsole.jsx missing handleRetryFailedTasksClick handler')
  }

  console.log('✓ BuildConsole.jsx has Retry Failed Tasks button')
  return true
}

export function testBuildConsolePropTypes() {
  const buildConsoleSource = readFileSync(
    join(__dirname, '../src/components/BuildConsole.jsx'),
    'utf-8'
  )

  // Check for PropTypes export
  if (!buildConsoleSource.includes('BuildConsole.propTypes')) {
    throw new Error('BuildConsole.jsx missing propTypes definition')
  }

  // Check for required prop types
  const requiredPropTypes = [
    'onBuildStart',
    'onBuildStop',
    'buildStatus',
    'logs',
    'currentTask',
    'completedTasks',
    'totalTasks',
    'generatedFiles',
  ]

  for (const prop of requiredPropTypes) {
    if (!buildConsoleSource.includes(prop)) {
      throw new Error(`BuildConsole.jsx missing propType: ${prop}`)
    }
  }

  console.log('✓ BuildConsole.jsx has proper PropTypes')
  return true
}

export function testBuildConsoleCSS() {
  const cssSource = readFileSync(
    join(__dirname, '../src/styles/build-console.css'),
    'utf-8'
  )

  // Check for required CSS classes
  const requiredClasses = [
    '.build-console',
    '.build-console-header',
    '.build-console-body',
    '.status-badge',
    '.btn-start',
    '.btn-stop',
    '.build-progress',
    '.progress-bar',
    '.build-logs',
    '.log-entry',
  ]

  for (const className of requiredClasses) {
    if (!cssSource.includes(className)) {
      throw new Error(`build-console.css missing class: ${className}`)
    }
  }

  // Check for status state styles
  const statusStates = [
    '.status-idle',
    '.status-running',
    '.status-done',
    '.status-error',
  ]

  for (const state of statusStates) {
    if (!cssSource.includes(state)) {
      throw new Error(`build-console.css missing status state: ${state}`)
    }
  }

  // Check for animation
  if (!cssSource.includes('@keyframes pulse')) {
    throw new Error('build-console.css missing pulse animation')
  }

  console.log('✓ BuildConsole.css has all required styles')
  return true
}

// Run all tests
export function runBuildConsoleTests() {
  testBuildConsoleRenders()
  testBuildConsoleHasStartButton()
  testBuildConsoleHasStopButton()
  testBuildConsoleHasStatusIndicator()
  testBuildConsoleHasProgressDisplay()
  testBuildConsoleHasFileCount()
  testBuildConsoleHasLogs()
  testBuildConsoleHasSkipTaskButton()
  testBuildConsoleHasRetryFailedTasksButton()
  testBuildConsolePropTypes()
  testBuildConsoleCSS()
  console.log('\n✅ All BuildConsole tests passed!')
  return true
}

// Run tests
runBuildConsoleTests()
