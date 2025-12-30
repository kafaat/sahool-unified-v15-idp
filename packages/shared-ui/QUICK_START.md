# Quick Start Guide - Modern Components

## 🚀 Quick Import

```tsx
import {
  GlassCard,
  ModernButton,
  AnimatedCard,
  GradientText,
  FloatingLabel,
  Shimmer,
  ProgressRing,
  Tooltip
} from '@sahool/shared-ui';
```

---

## 📋 Most Common Use Cases

### 1. Login Form with Modern Design

```tsx
import { GlassCard, FloatingLabel, ModernButton } from '@sahool/shared-ui';
import { Mail, Lock } from 'lucide-react';

function LoginForm() {
  return (
    <GlassCard variant="medium" blur="lg">
      <form className="space-y-4">
        <FloatingLabel
          label="Email"
          type="email"
          icon={Mail}
          variant="outlined"
        />
        <FloatingLabel
          label="Password"
          type="password"
          icon={Lock}
          variant="outlined"
        />
        <ModernButton variant="gradient" fullWidth>
          Sign In
        </ModernButton>
      </form>
    </GlassCard>
  );
}
```

### 2. Loading States

```tsx
import { Shimmer, ShimmerGroup } from '@sahool/shared-ui';

function LoadingCard() {
  return (
    <ShimmerGroup loading={isLoading}>
      <div className="flex gap-4">
        <Shimmer variant="circular" width={60} height={60} />
        <div className="flex-1 space-y-2">
          <Shimmer variant="text" width="80%" />
          <Shimmer variant="text" width="60%" />
        </div>
      </div>
    </ShimmerGroup>
  );
}
```

### 3. Dashboard Card with Progress

```tsx
import { AnimatedCard, ProgressRing, GradientText } from '@sahool/shared-ui';

function StatsCard() {
  return (
    <AnimatedCard variant="lift" intensity="medium">
      <div className="flex items-center justify-between">
        <div>
          <GradientText variant="primary" size="xl" as="h3">
            Course Progress
          </GradientText>
          <p className="text-gray-600">75% Complete</p>
        </div>
        <ProgressRing
          progress={75}
          variant="gradient"
          size="lg"
        />
      </div>
    </AnimatedCard>
  );
}
```

### 4. Interactive Buttons

```tsx
import { ModernButton, Tooltip } from '@sahool/shared-ui';
import { Save, Trash } from 'lucide-react';

function ActionButtons() {
  return (
    <div className="flex gap-2">
      <Tooltip content="Save changes" position="top">
        <ModernButton variant="gradient" icon={Save}>
          Save
        </ModernButton>
      </Tooltip>

      <Tooltip content="Delete item" position="top" variant="light">
        <ModernButton variant="outline" icon={Trash}>
          Delete
        </ModernButton>
      </Tooltip>
    </div>
  );
}
```

### 5. Hero Section

```tsx
import { GradientText, ModernButton } from '@sahool/shared-ui';
import { Sparkles } from 'lucide-react';

function Hero() {
  return (
    <div className="text-center space-y-6">
      <GradientText
        variant="rainbow"
        size="2xl"
        as="h1"
        animated
        className="text-6xl"
      >
        Welcome to SAHOOL
      </GradientText>
      <p className="text-xl text-gray-600">
        Modern Educational Platform
      </p>
      <ModernButton
        variant="gradient"
        icon={Sparkles}
        glow
        size="lg"
      >
        Get Started
      </ModernButton>
    </div>
  );
}
```

---

## 🎨 Color Variants Quick Reference

### ModernButton
- `gradient` - Colorful gradient background
- `glow` - Solid with glow effect
- `outline` - Transparent with border
- `ghost` - No background
- `solid` - Standard solid background

### GradientText
- `primary` - SAHOOL blue to purple
- `secondary` - Purple to pink to red
- `rainbow` - Multi-color gradient
- `sunset` - Orange to pink to purple
- `ocean` - Blue to cyan to teal
- `forest` - Green to emerald to teal

### ProgressRing
- `primary` - SAHOOL brand color
- `success` - Green
- `warning` - Yellow
- `danger` - Red
- `gradient` - Purple gradient

---

## 🌓 Dark Mode

All components automatically support dark mode:

```tsx
// Add to your root layout or _app.tsx
<html className="dark"> {/* or class="dark" based on user preference */}
  <body>
    {/* All modern components will adapt */}
  </body>
</html>
```

---

## ⚡ Animation Control

### Disable animations globally:
```css
/* Add to your global CSS */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Per component:
```tsx
// Most components respect className overrides
<AnimatedCard className="transition-none">
  {/* No animations */}
</AnimatedCard>
```

---

## 🔍 Troubleshooting

### Components not styled correctly?

1. **Check Tailwind config:**
```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './node_modules/@sahool/shared-ui/**/*.{js,ts,jsx,tsx}',
  ],
}
```

2. **Check animations in config:**
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      animation: {
        'shimmer': 'shimmer 1.5s ease-in-out infinite',
        'gradient': 'gradient 3s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
    },
  },
}
```

### Icons not showing?

Install lucide-react:
```bash
npm install lucide-react
```

---

## 📱 Responsive Design

All components are responsive by default:

```tsx
// Stack on mobile, row on desktop
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <AnimatedCard variant="lift">Card 1</AnimatedCard>
  <AnimatedCard variant="lift">Card 2</AnimatedCard>
  <AnimatedCard variant="lift">Card 3</AnimatedCard>
</div>

// Responsive button
<ModernButton
  fullWidth  // Full width on mobile
  className="md:w-auto"  // Auto width on desktop
>
  Click Me
</ModernButton>
```

---

## 🎯 Best Combinations

1. **Card + Progress + Gradient Text**
   - Great for dashboards and stats

2. **GlassCard + FloatingLabel + ModernButton**
   - Perfect for forms and authentication

3. **AnimatedCard + Tooltip + Icons**
   - Excellent for feature showcases

4. **Shimmer + Conditional Rendering**
   - Ideal for loading states

---

## 📚 More Examples

See `ModernComponents.example.tsx` for comprehensive examples and `MODERN_COMPONENTS.md` for detailed documentation.
