// ═══════════════════════════════════════════════════════════════════════════════
// Dashboard Tailwind Configuration
// Extends SAHOOL Unified Tailwind Config
// ═══════════════════════════════════════════════════════════════════════════════

const sharedConfig = require("@sahool/tailwind-config");

/** @type {import('tailwindcss').Config} */
module.exports = {
  // Use shared config as base
  presets: [sharedConfig],

  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    // Include shared UI components
    "../../packages/shared-ui/src/**/*.{js,ts,jsx,tsx}",
  ],

  // App-specific theme extensions
  theme: {
    extend: {
      // Dashboard-specific customizations can go here
    },
  },

  plugins: [],
};
