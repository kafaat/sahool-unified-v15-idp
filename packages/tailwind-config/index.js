// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Unified Tailwind Configuration
// تكوين Tailwind الموحد لمنصة سهول
// ═══════════════════════════════════════════════════════════════════════════════

/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      // ─────────────────────────────────────────────────────────────────────────
      // Colors - ألوان موحدة
      // ─────────────────────────────────────────────────────────────────────────
      colors: {
        // SAHOOL Brand Colors (Green Agriculture Theme)
        sahool: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a", // Primary
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        // Semantic Colors
        primary: {
          DEFAULT: "#16a34a",
          light: "#22c55e",
          dark: "#15803d",
        },
        secondary: {
          DEFAULT: "#0891b2",
          light: "#06b6d4",
          dark: "#0e7490",
        },
        accent: {
          DEFAULT: "#d97706",
          light: "#f59e0b",
          dark: "#b45309",
        },
        success: {
          DEFAULT: "#10b981",
          light: "#34d399",
          dark: "#059669",
        },
        warning: {
          DEFAULT: "#f59e0b",
          light: "#fbbf24",
          dark: "#d97706",
        },
        danger: {
          DEFAULT: "#dc2626",
          light: "#ef4444",
          dark: "#b91c1c",
        },
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Typography - الخطوط العربية
      // ─────────────────────────────────────────────────────────────────────────
      fontFamily: {
        arabic: ["var(--font-tajawal)", "Cairo", "sans-serif"],
        tajawal: ["var(--font-tajawal)", "Cairo", "sans-serif"],
        cairo: ["Cairo", "var(--font-tajawal)", "sans-serif"],
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Animation
      // ─────────────────────────────────────────────────────────────────────────
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
