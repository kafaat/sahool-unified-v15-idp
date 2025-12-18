/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        sahool: {
          primary: '#059669',    // Emerald 600
          secondary: '#0891b2',  // Cyan 600
          accent: '#d97706',     // Amber 600
          danger: '#dc2626',     // Red 600
          warning: '#f59e0b',    // Amber 500
          success: '#10b981',    // Emerald 500
        },
      },
      fontFamily: {
        arabic: ['IBM Plex Sans Arabic', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
