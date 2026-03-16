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
        // Source of truth: governance/design/design-tokens.yaml
        sahool: {
          50: "#E8F5E9",
          100: "#C8E6C9",
          200: "#A5D6A7",
          300: "#81C784",
          400: "#66BB6A",
          500: "#4CAF50",   // Main primary
          600: "#43A047",
          700: "#388E3C",
          800: "#2E7D32",
          900: "#1B5E20",
          950: "#0D3B10",
        },
        // Alias: Components use sahool-green-* classes (e.g. bg-sahool-green-600)
        "sahool-green": {
          50: "#E8F5E9",
          100: "#C8E6C9",
          200: "#A5D6A7",
          300: "#81C784",
          400: "#66BB6A",
          500: "#4CAF50",
          600: "#43A047",
          700: "#388E3C",
          800: "#2E7D32",
          900: "#1B5E20",
          950: "#0D3B10",
        },
        // SAHOOL Earth/Brown tones (agriculture soil theme)
        "sahool-brown": {
          50: "#fdf8f0",
          100: "#f5e6d3",
          200: "#e8cba4",
          300: "#d4a76e",
          400: "#c08a45",
          500: "#a67c3e",
          600: "#8b6831",
          700: "#6f5327",
          800: "#573f1e",
          900: "#3d2c15",
          950: "#2a1e0e",
        },
        // Semantic Colors (aligned with design tokens)
        primary: {
          DEFAULT: "#4CAF50",
          light: "#66BB6A",
          dark: "#388E3C",
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
          DEFAULT: "#4CAF50",
          light: "#81C784",
          dark: "#388E3C",
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
