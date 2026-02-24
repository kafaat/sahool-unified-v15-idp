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
      // Dark mode specific colors
      colors: {
        sahool: {
          50: "#ECFDF5",
          100: "#D1FAE5",
          200: "#A7F3D0",
          300: "#6EE7B7",
          400: "#34D399",
          500: "#10B981",
          600: "#059669",
          700: "#047857",
          800: "#065F46",
          900: "#064E3B",
        },
      },
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
