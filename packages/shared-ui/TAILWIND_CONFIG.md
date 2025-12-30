# Tailwind CSS Configuration for Feedback Components

This document provides the necessary Tailwind CSS configuration for the feedback and notification components.

## Required Tailwind Animations

Add these custom animations to your `tailwind.config.js` or `tailwind.config.ts` file:

```javascript
module.exports = {
  theme: {
    extend: {
      keyframes: {
        // Toast & Alert Animations
        'slide-in-right': {
          '0%': {
            transform: 'translateX(100%) scale(0.95)',
            opacity: '0'
          },
          '100%': {
            transform: 'translateX(0) scale(1)',
            opacity: '1'
          },
        },
        'slide-down': {
          '0%': {
            transform: 'translateY(-10px)',
            opacity: '0'
          },
          '100%': {
            transform: 'translateY(0)',
            opacity: '1'
          },
        },

        // Progress Animations
        'progress-stripes': {
          '0%': {
            backgroundPosition: '1rem 0'
          },
          '100%': {
            backgroundPosition: '0 0'
          },
        },
        'progress-indeterminate': {
          '0%': {
            transform: 'translateX(-100%)'
          },
          '100%': {
            transform: 'translateX(400%)'
          },
        },
      },
      animation: {
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'progress-stripes': 'progress-stripes 1s linear infinite',
        'progress-indeterminate': 'progress-indeterminate 1.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
```

## Color Configuration

Ensure your Tailwind config includes the SAHOOL brand colors:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        sahool: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
      },
    },
  },
}
```

## Dark Mode Configuration

Enable dark mode in your Tailwind config:

```javascript
module.exports = {
  darkMode: 'class', // or 'media' for system preference
  // ... rest of config
}
```

## Complete Example Configuration

Here's a complete example configuration file:

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/@sahool/shared-ui/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        sahool: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
      },
      keyframes: {
        'slide-in-right': {
          '0%': {
            transform: 'translateX(100%) scale(0.95)',
            opacity: '0'
          },
          '100%': {
            transform: 'translateX(0) scale(1)',
            opacity: '1'
          },
        },
        'slide-down': {
          '0%': {
            transform: 'translateY(-10px)',
            opacity: '0'
          },
          '100%': {
            transform: 'translateY(0)',
            opacity: '1'
          },
        },
        'progress-stripes': {
          '0%': {
            backgroundPosition: '1rem 0'
          },
          '100%': {
            backgroundPosition: '0 0'
          },
        },
        'progress-indeterminate': {
          '0%': {
            transform: 'translateX(-100%)'
          },
          '100%': {
            transform: 'translateX(400%)'
          },
        },
      },
      animation: {
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'progress-stripes': 'progress-stripes 1s linear infinite',
        'progress-indeterminate': 'progress-indeterminate 1.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}

export default config
```

## Usage Notes

1. **Content Paths**: Make sure to include the `@sahool/shared-ui` package in your `content` array to ensure Tailwind processes all component styles.

2. **Dark Mode**: The components are designed to work with both `class` and `media` dark mode strategies.

3. **Purging**: All component styles are safe for production builds and will be properly purged when not in use.

4. **Custom Colors**: If you need to customize the SAHOOL brand colors, update the color palette in your config while maintaining the same shade structure (50-950).

## Testing the Configuration

After adding the configuration, test with this simple component:

```tsx
import { ModernToast, ToastProvider, useToast } from '@sahool/shared-ui';

function TestComponent() {
  const toast = useToast();

  return (
    <button onClick={() => toast.success('It works!', 'Configuration is correct')}>
      Test Toast
    </button>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <TestComponent />
    </ToastProvider>
  );
}
```
