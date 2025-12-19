// ═══════════════════════════════════════════════════════════════════════════════
// Web Admin Tailwind Configuration
// Extends SAHOOL Unified Tailwind Config
// ═══════════════════════════════════════════════════════════════════════════════

import type { Config } from 'tailwindcss';
import sharedConfig from '@sahool/tailwind-config';

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
