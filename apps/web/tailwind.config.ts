import type { Config } from "tailwindcss";

const config: Config = {
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
      colors: {
        // SAHOOL Brand Colors
        sahool: {
          green: {
            50: "#f0fdf4",
            100: "#dcfce7",
            200: "#bbf7d0",
            300: "#86efac",
            400: "#4ade80",
            500: "#22c55e",
            600: "#16a34a",
            700: "#15803d",
            800: "#166534",
            900: "#14532d",
          },
        },
      },
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
