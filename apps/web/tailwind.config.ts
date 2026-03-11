import type { Config } from "tailwindcss";

// Use relative import to load shared config
import sharedConfig from "../../packages/tailwind-config";

const config: Config = {
  // Use shared config as base
  presets: [sharedConfig as Config],

  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/features/**/!(*.test|*.spec).{js,ts,jsx,tsx}",
    "./src/hooks/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}",
    "./src/stores/**/*.{ts,tsx}",
    "../../packages/shared-ui/src/**/*.{js,ts,jsx,tsx}",
  ],
  // Dark mode configuration - use class-based dark mode for better control
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        tajawal: ["var(--font-tajawal)", "sans-serif"],
        cairo: ["Cairo", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
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
  // Future flags for upcoming Tailwind CSS features
  future: {
    hoverOnlyWhenSupported: true,
  },
};

export default config;
