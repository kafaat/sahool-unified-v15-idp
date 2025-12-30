/**
 * Vitest Workspace Configuration
 * تكوين مساحة العمل لـ Vitest
 *
 * Each project uses its own vitest config for proper alias resolution
 */

import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  // Shared UI package
  {
    test: {
      name: 'shared-ui',
      root: './packages/shared-ui',
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
    },
  },
  // Web App - uses its own vitest.config.ts
  'apps/web/vitest.config.ts',
  // Admin App - if it has tests
  {
    test: {
      name: 'admin',
      root: './apps/admin',
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      globals: true,
      environment: 'jsdom',
    },
  },
]);
