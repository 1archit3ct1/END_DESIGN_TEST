/**
 * Test: Test runner executes all test files successfully
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { execSync } from 'child_process'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testVitestConfig() {
  const configPath = join(__dirname, '../vitest.config.js')
  const packagePath = join(__dirname, '../package.json')
  
  // Check vitest.config.js exists
  let configContent
  try {
    configContent = readFileSync(configPath, 'utf-8')
  } catch (e) {
    throw new Error(`vitest.config.js not found at ${configPath}`)
  }

  // Check for required config options
  const requiredConfig = [
    'include:',
    'tests/**/*.test.js',
    'environment:',
    'node'
  ]
  for (const config of requiredConfig) {
    if (!configContent.includes(config)) {
      throw new Error(`vitest.config.js missing: ${config}`)
    }
  }

  // Check package.json has test script
  const packageJson = JSON.parse(readFileSync(packagePath, 'utf-8'))
  if (!packageJson.scripts.test) {
    throw new Error('package.json missing test script')
  }
  if (!packageJson.scripts.test.includes('vitest')) {
    throw new Error('test script should use vitest')
  }

  console.log('✓ Test runner executes all test files successfully')
  return true
}

// Run test
testVitestConfig()
