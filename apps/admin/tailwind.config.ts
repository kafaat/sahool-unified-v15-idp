// ═══════════════════════════════════════════════════════════════════════════════
// Web Admin Tailwind Configuration
// Extends SAHOOL Unified Tailwind Config
// ═══════════════════════════════════════════════════════════════════════════════

import type { Config } from "tailwindcss";

// Use relative import to avoid module resolution issues in CI
// eslint-disable-next-line @typescript-eslint/no-var-requires
const sharedConfig = require("../../packages/tailwind-config");

const config: Config = {
  // Use shared config as base
  presets: [sharedConfig as Config],

  // Enable class-based dark mode
  darkMode: "class",

  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    // Include shared UI components
    "../packages/shared-ui/src/**/*.{js,ts,jsx,tsx}",
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
      // Animation extensions
      animation: {
        "fade-in": "fadeIn 0.2s ease-out",
        "slide-in-from-top": "slideInFromTop 0.2s ease-out",
        "slide-in-from-right": "slideInFromRight 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideInFromTop: {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInFromRight: {
          "0%": { opacity: "0", transform: "translateX(100%)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
      },
    },
  },

  plugins: [],
};

export default config;
