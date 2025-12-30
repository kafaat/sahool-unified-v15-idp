import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/shared-ui/src/**/*.{js,ts,jsx,tsx}',
  ],
  // Dark mode configuration - use data-attribute based dark mode for better control
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // SAHOOL Brand Colors
        sahool: {
          green: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e',
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
          },
          brown: {
            50: '#fdf8f6',
            100: '#f2e8e5',
            200: '#eaddd7',
            300: '#e0cec7',
            400: '#d2bab0',
            500: '#bfa094',
            600: '#a18072',
            700: '#977669',
            800: '#846358',
            900: '#43302b',
          },
        },
      },
      fontFamily: {
        tajawal: ['Tajawal', 'sans-serif'],
        cairo: ['Cairo', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      // ═══════════════════════════════════════════════════════════════════
      // SAHOOL Animation Utilities
      // Comprehensive animation system with CSS animations
      // ═══════════════════════════════════════════════════════════════════

      // Animation classes
      animation: {
        // Fade animations
        'fade-in': 'fadeIn 0.3s ease-in-out forwards',
        'fade-out': 'fadeOut 0.3s ease-in-out forwards',

        // Slide animations
        'slide-up': 'slideUp 0.3s ease-out forwards',
        'slide-down': 'slideDown 0.3s ease-out forwards',
        'slide-left': 'slideLeft 0.3s ease-out forwards',
        'slide-right': 'slideRight 0.3s ease-out forwards',

        // Scale animations
        'scale-in': 'scaleIn 0.3s ease-out forwards',
        'scale-out': 'scaleOut 0.3s ease-out forwards',

        // Bounce animations
        'bounce-in': 'bounceIn 0.5s ease-out forwards',

        // Rotate animations
        'rotate-in': 'rotateIn 0.5s ease-out forwards',

        // Loading animations
        'spin': 'spin 1s linear infinite',
        'pulse': 'pulse 2s ease-in-out infinite',
        'bounce': 'bounce 1s infinite',
        'ping': 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite',

        // Shimmer/Skeleton
        'shimmer': 'shimmer 2s linear infinite',

        // Infinite variants
        'fade-in-infinite': 'fadeIn 2s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },

      // Keyframe definitions
      keyframes: {
        // Fade
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },

        // Slide
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideLeft: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideRight: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },

        // Scale
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleOut: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(0.9)', opacity: '0' },
        },

        // Bounce
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)', opacity: '0.8' },
          '70%': { transform: 'scale(0.9)', opacity: '0.9' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounce: {
          '0%, 100%': {
            transform: 'translateY(-25%)',
            animationTimingFunction: 'cubic-bezier(0.8, 0, 1, 1)',
          },
          '50%': {
            transform: 'translateY(0)',
            animationTimingFunction: 'cubic-bezier(0, 0, 0.2, 1)',
          },
        },

        // Rotate
        rotateIn: {
          '0%': { transform: 'rotate(-200deg) scale(0)', opacity: '0' },
          '100%': { transform: 'rotate(0) scale(1)', opacity: '1' },
        },

        // Spin
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },

        // Pulse
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },

        // Ping
        ping: {
          '75%, 100%': {
            transform: 'scale(2)',
            opacity: '0',
          },
        },

        // Shimmer
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },

      // Custom timing functions (easing)
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },

      // Animation delays
      transitionDelay: {
        '0': '0ms',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
        '700': '700ms',
        '1000': '1000ms',
      },

      // Animation durations
      transitionDuration: {
        '0': '0ms',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '400': '400ms',
        '500': '500ms',
        '700': '700ms',
        '1000': '1000ms',
      },
    },
  },
  plugins: [],
  // Performance: Disable unused features
  corePlugins: {
    // Enable all core plugins, but can be customized if needed
  },
  // Future flags for upcoming Tailwind CSS features
  future: {
    hoverOnlyWhenSupported: true,
  },
};

export default config;
