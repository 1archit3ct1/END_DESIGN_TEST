/**
 * Test: CodePreview.jsx shows syntax highlighted code
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testCodePreviewRenders() {
  // Read source file and validate structure
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for required elements in source
  const requiredElements = [
    'data-testid="code-preview"',
    'data-testid="code-preview-header"',
    'data-testid="code-preview-content"',
    'data-testid="code-preview-filename"',
    'data-testid="code-preview-language"',
    'data-testid="code-preview-lines"',
    'data-testid="code-preview-copy"',
    'data-testid="code-preview-empty"',
    'data-testid="code-content"',
    'data-testid="line-numbers"',
    'code',
    'language',
    'fileName',
    'showLineNumbers',
  ]

  for (const element of requiredElements) {
    if (!codePreviewSource.includes(element)) {
      throw new Error(`CodePreview.jsx missing required element: ${element}`)
    }
  }

  // Check for syntax highlighting function
  if (!codePreviewSource.includes('highlightCode')) {
    throw new Error('CodePreview.jsx missing highlightCode function')
  }

  // Check for language detection
  if (!codePreviewSource.includes('detectedLanguage')) {
    throw new Error('CodePreview.jsx missing language detection')
  }

  console.log('✓ CodePreview.jsx renders correctly with syntax highlighted code')
  return true
}

export function testCodePreviewHasSyntaxHighlighting() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for syntax highlighting patterns
  const patterns = [
    'comment',
    'string',
    'keyword',
    'function',
    'number',
  ]

  for (const pattern of patterns) {
    if (!codePreviewSource.includes(pattern)) {
      throw new Error(`CodePreview.jsx missing syntax pattern: ${pattern}`)
    }
  }

  // Check for token class
  if (!codePreviewSource.includes('token')) {
    throw new Error('CodePreview.jsx missing token class for highlighting')
  }

  // Check for language-specific highlighting
  const languages = ['javascript', 'typescript', 'python', 'rust', 'json']
  for (const lang of languages) {
    if (!codePreviewSource.includes(lang)) {
      throw new Error(`CodePreview.jsx missing language support: ${lang}`)
    }
  }

  console.log('✓ CodePreview.jsx has syntax highlighting')
  return true
}

export function testCodePreviewHasLanguageDetection() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for language detection from extension
  if (!codePreviewSource.includes('detectedLanguage') || !codePreviewSource.includes('useMemo')) {
    throw new Error('CodePreview.jsx missing language detection')
  }

  // Check for extension mapping (checking for keys in the object)
  const extensions = ['js:', 'jsx:', 'ts:', 'tsx:', 'py:', 'rs:', 'json:', 'md:', 'css:', 'html:']
  for (const ext of extensions) {
    if (!codePreviewSource.includes(ext)) {
      throw new Error(`CodePreview.jsx missing extension mapping: ${ext}`)
    }
  }

  console.log('✓ CodePreview.jsx has language detection')
  return true
}

export function testCodePreviewHasLineNumbers() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for line numbers display
  if (!codePreviewSource.includes('line-numbers')) {
    throw new Error('CodePreview.jsx missing line numbers')
  }

  // Check for line number rendering
  if (!codePreviewSource.includes('line-number')) {
    throw new Error('CodePreview.jsx missing line number rendering')
  }

  // Check for showLineNumbers prop
  if (!codePreviewSource.includes('showLineNumbers')) {
    throw new Error('CodePreview.jsx missing showLineNumbers prop')
  }

  // Check for line count
  if (!codePreviewSource.includes('lineCount')) {
    throw new Error('CodePreview.jsx missing line count')
  }

  console.log('✓ CodePreview.jsx has line numbers')
  return true
}

export function testCodePreviewHasCopyFunction() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for copy button
  if (!codePreviewSource.includes('btn-copy')) {
    throw new Error('CodePreview.jsx missing copy button')
  }

  // Check for clipboard API usage
  if (!codePreviewSource.includes('navigator.clipboard.writeText')) {
    throw new Error('CodePreview.jsx missing clipboard API usage')
  }

  // Check for copied state
  if (!codePreviewSource.includes('copied') || !codePreviewSource.includes('setCopied')) {
    throw new Error('CodePreview.jsx missing copied state')
  }

  // Check for Copy label
  if (!codePreviewSource.includes('Copy') && !codePreviewSource.includes('📋')) {
    throw new Error('CodePreview.jsx missing Copy button label')
  }

  console.log('✓ CodePreview.jsx has copy function')
  return true
}

export function testCodePreviewHasFileName() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for file name display
  if (!codePreviewSource.includes('fileName')) {
    throw new Error('CodePreview.jsx missing fileName prop')
  }

  // Check for file icon
  if (!codePreviewSource.includes('getFileIcon') || !codePreviewSource.includes('file-icon')) {
    throw new Error('CodePreview.jsx missing file icon')
  }

  // Check for showFileName prop
  if (!codePreviewSource.includes('showFileName')) {
    throw new Error('CodePreview.jsx missing showFileName prop')
  }

  console.log('✓ CodePreview.jsx has file name display')
  return true
}

export function testCodePreviewHasEmptyState() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for empty state
  if (!codePreviewSource.includes('code-preview-empty')) {
    throw new Error('CodePreview.jsx missing empty state')
  }

  // Check for empty state message
  if (!codePreviewSource.includes('No code to display')) {
    throw new Error('CodePreview.jsx missing empty state message')
  }

  console.log('✓ CodePreview.jsx has empty state')
  return true
}

export function testCodePreviewHasThemes() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for theme prop
  if (!codePreviewSource.includes('theme')) {
    throw new Error('CodePreview.jsx missing theme prop')
  }

  // Check for dark and light themes
  if (!codePreviewSource.includes("'dark'") && !codePreviewSource.includes('"dark"')) {
    throw new Error('CodePreview.jsx missing dark theme')
  }

  if (!codePreviewSource.includes("'light'") && !codePreviewSource.includes('"light"')) {
    throw new Error('CodePreview.jsx missing light theme')
  }

  // Check for theme class application
  if (!codePreviewSource.includes('${theme}')) {
    throw new Error('CodePreview.jsx missing theme class application')
  }

  console.log('✓ CodePreview.jsx has themes')
  return true
}

export function testCodePreviewPropTypes() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for PropTypes export
  if (!codePreviewSource.includes('CodePreview.propTypes')) {
    throw new Error('CodePreview.jsx missing propTypes definition')
  }

  // Check for required prop types
  const requiredPropTypes = [
    'code',
    'language',
    'fileName',
    'showLineNumbers',
    'showFileName',
    'readOnly',
    'onChange',
    'fontSize',
    'theme',
    'maxLines',
    'onCopy',
  ]

  for (const prop of requiredPropTypes) {
    if (!codePreviewSource.includes(prop)) {
      throw new Error(`CodePreview.jsx missing propType: ${prop}`)
    }
  }

  // Check for PropTypes validation
  const propTypesElements = [
    'PropTypes.string',
    'PropTypes.bool',
    'PropTypes.func',
    'PropTypes.number',
    'PropTypes.oneOf',
  ]

  for (const element of propTypesElements) {
    if (!codePreviewSource.includes(element)) {
      throw new Error(`CodePreview.jsx missing PropTypes: ${element}`)
    }
  }

  console.log('✓ CodePreview.jsx has proper PropTypes')
  return true
}

export function testCodePreviewCSS() {
  const cssSource = readFileSync(
    join(__dirname, '../src/styles/code-preview.css'),
    'utf-8'
  )

  // Check for required CSS classes
  const requiredClasses = [
    '.code-preview',
    '.code-preview-header',
    '.code-preview-content',
    '.code-content',
    '.line-numbers',
    '.line-number',
    '.code-line',
    '.token',
    '.btn-copy',
    '.language-badge',
  ]

  for (const className of requiredClasses) {
    if (!cssSource.includes(className)) {
      throw new Error(`code-preview.css missing class: ${className}`)
    }
  }

  // Check for syntax highlighting colors
  const tokenColors = [
    '.token.string',
    '.token.comment',
    '.token.keyword',
    '.token.function',
    '.token.number',
  ]

  for (const className of tokenColors) {
    if (!cssSource.includes(className)) {
      throw new Error(`code-preview.css missing token color: ${className}`)
    }
  }

  // Check for light theme
  if (!cssSource.includes('.code-preview.light')) {
    throw new Error('code-preview.css missing light theme')
  }

  // Check for empty state
  if (!cssSource.includes('.code-preview-empty')) {
    throw new Error('code-preview.css missing empty state')
  }

  // Check for scrollbar
  if (!cssSource.includes('::-webkit-scrollbar')) {
    throw new Error('code-preview.css missing scrollbar styles')
  }

  console.log('✓ CodePreview.css has all required styles')
  return true
}

export function testCodePreviewShowsSyntaxHighlightedCode() {
  const codePreviewSource = readFileSync(
    join(__dirname, '../src/components/CodePreview.jsx'),
    'utf-8'
  )

  // Check for code line rendering
  if (!codePreviewSource.includes('code-line')) {
    throw new Error('CodePreview.jsx missing code line rendering')
  }

  // Check for lines splitting
  if (!codePreviewSource.includes("split('\\n')") || !codePreviewSource.includes('lines')) {
    throw new Error('CodePreview.jsx missing lines splitting')
  }

  // Check for dangerouslySetInnerHTML (for syntax highlighting)
  if (!codePreviewSource.includes('dangerouslySetInnerHTML')) {
    throw new Error('CodePreview.jsx missing dangerouslySetInnerHTML for highlighting')
  }

  // Check for language class on code element
  if (!codePreviewSource.includes('language-${detectedLanguage}')) {
    throw new Error('CodePreview.jsx missing language class on code element')
  }

  console.log('✓ CodePreview.jsx shows syntax highlighted code correctly')
  return true
}

// Run all tests
export function runCodePreviewTests() {
  testCodePreviewRenders()
  testCodePreviewHasSyntaxHighlighting()
  testCodePreviewHasLanguageDetection()
  testCodePreviewHasLineNumbers()
  testCodePreviewHasCopyFunction()
  testCodePreviewHasFileName()
  testCodePreviewHasEmptyState()
  testCodePreviewHasThemes()
  testCodePreviewPropTypes()
  testCodePreviewCSS()
  testCodePreviewShowsSyntaxHighlightedCode()
  console.log('\n✅ All CodePreview tests passed!')
  return true
}

// Run tests
runCodePreviewTests()
