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
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',   // Primary
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        // Yemen Flag Colors
        yemen: {
          red: '#CE1126',
          white: '#FFFFFF',
          black: '#000000',
        },
        // Semantic Colors
        primary: {
          DEFAULT: '#16a34a',
          light: '#22c55e',
          dark: '#15803d',
        },
        secondary: {
          DEFAULT: '#0891b2',
          light: '#06b6d4',
          dark: '#0e7490',
        },
        accent: {
          DEFAULT: '#d97706',
          light: '#f59e0b',
          dark: '#b45309',
        },
        success: {
          DEFAULT: '#10b981',
          light: '#34d399',
          dark: '#059669',
        },
        warning: {
          DEFAULT: '#f59e0b',
          light: '#fbbf24',
          dark: '#d97706',
        },
        danger: {
          DEFAULT: '#dc2626',
          light: '#ef4444',
          dark: '#b91c1c',
        },
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Typography - الخطوط العربية
      // ─────────────────────────────────────────────────────────────────────────
      fontFamily: {
        arabic: ['Tajawal', 'Cairo', 'IBM Plex Sans Arabic', 'sans-serif'],
        tajawal: ['Tajawal', 'Cairo', 'sans-serif'],
        cairo: ['Cairo', 'Tajawal', 'sans-serif'],
        ibm: ['IBM Plex Sans Arabic', 'Tajawal', 'sans-serif'],
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Spacing & Layout
      // ─────────────────────────────────────────────────────────────────────────
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Border Radius
      // ─────────────────────────────────────────────────────────────────────────
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Box Shadow
      // ─────────────────────────────────────────────────────────────────────────
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'inner-sm': 'inset 0 1px 2px 0 rgb(0 0 0 / 0.05)',
      },

      // ─────────────────────────────────────────────────────────────────────────
      // Animation
      // ─────────────────────────────────────────────────────────────────────────
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
