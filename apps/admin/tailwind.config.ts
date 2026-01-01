// ═══════════════════════════════════════════════════════════════════════════════
// Web Admin Tailwind Configuration
// Extends SAHOOL Unified Tailwind Config
// ═══════════════════════════════════════════════════════════════════════════════

import type { Config } from 'tailwindcss';

// Use relative import to avoid module resolution issues in CI
// eslint-disable-next-line @typescript-eslint/no-var-requires
const sharedConfig = require('../../packages/tailwind-config');

const config: Config = {
  // Use shared config as base
  presets: [sharedConfig as Config],

  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    // Include shared UI components
    '../packages/shared-ui/src/**/*.{js,ts,jsx,tsx}',
  ],

  // App-specific theme extensions
  theme: {
    extend: {
      // Web admin-specific customizations can go here
    },
  },

  plugins: [],
};

export default config;
