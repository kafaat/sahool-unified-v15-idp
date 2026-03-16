// ═══════════════════════════════════════════════════════════════════════════════
// Web Admin Tailwind Configuration
// Extends SAHOOL Unified Tailwind Config
// ═══════════════════════════════════════════════════════════════════════════════

import type { Config } from "tailwindcss";

// Use relative import to load shared config
import sharedConfig from "../../packages/tailwind-config";

const config: Config = {
  // Use shared config as base
  presets: [sharedConfig as Config],

  // Enable class-based dark mode
  darkMode: "class",

  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/hooks/**/*.{ts,tsx}",
    "./src/stores/**/*.{ts,tsx}",
    // Include shared UI components (two levels up from apps/admin/)
    "../../packages/shared-ui/src/**/*.{js,ts,jsx,tsx}",
  ],

  // App-specific theme extensions
  theme: {
    extend: {
      // Unified brand colors (aligned with governance/design/design-tokens.yaml)
      colors: {},
      animation: {
        "fade-in": "fadeIn 0.2s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
    },
  },

  plugins: [],
};

export default config;
