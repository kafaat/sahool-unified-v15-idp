/**
 * Vitest Configuration
 * تكوين Vitest للمشروع
 */

import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./packages/shared-ui/src/test/setup.ts'],
    include: [
      'packages/**/*.{test,spec}.{ts,tsx}',
    ],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      // Exclude NestJS tests - they use Jest, not Vitest
      'apps/services/marketplace-service/**',
      // Exclude Python tests
      'apps/services/**/*.py',
    ],
  },
});
