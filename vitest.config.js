import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['tests/**/*.test.js'],
    exclude: ['node_modules', 'dist'],
    environment: 'node',
    reporters: 'verbose',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.js']
    }
  }
})
