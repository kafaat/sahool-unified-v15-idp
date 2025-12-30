# Modern UI Components Documentation

## Overview

The SAHOOL Shared UI library includes a collection of modern, accessible, and customizable components built with React, TypeScript, and Tailwind CSS. All components support dark mode and include smooth animations.

---

## 🎨 Components

### 1. GlassCard

A glassmorphism card with backdrop blur and transparency effects.

**Features:**
- Multiple blur levels (sm, md, lg, xl)
- Light, medium, and dark variants
- Optional border and shadow
- Hover effects with scale animation

**Props:**
```typescript
interface GlassCardProps {
  children: ReactNode;
  variant?: 'light' | 'medium' | 'dark'; // Default: 'medium'
  blur?: 'sm' | 'md' | 'lg' | 'xl'; // Default: 'md'
  border?: boolean; // Default: true
  shadow?: boolean; // Default: true
  hover?: boolean; // Default: false
}
```

**Usage:**
```tsx
import { GlassCard } from '@sahool/shared-ui';

<GlassCard variant="medium" blur="lg" hover>
  <h3>Card Title</h3>
  <p>Card content with glassmorphism effect</p>
</GlassCard>
```

---

### 2. ModernButton

Advanced button with gradients, glow effects, and loading states.

**Features:**
- Multiple variants (gradient, glow, outline, ghost, solid)
- Three sizes with responsive scaling
- Loading state with spinner
- Icon support (left or right)
- Full-width option
- Optional glow effect
- Hover and active animations

**Props:**
```typescript
interface ModernButtonProps {
  variant?: 'gradient' | 'glow' | 'outline' | 'ghost' | 'solid';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  glow?: boolean;
  children: ReactNode;
}
```

**Usage:**
```tsx
import { ModernButton } from '@sahool/shared-ui';
import { Sparkles } from 'lucide-react';

<ModernButton
  variant="gradient"
  icon={Sparkles}
  glow
  onClick={handleClick}
>
  Get Started
</ModernButton>
```

---

### 3. AnimatedCard

Interactive card with hover animations and micro-interactions.

**Features:**
- Five animation variants (lift, tilt, glow, border, scale)
- Three intensity levels
- Shine effect overlay
- Smooth transitions
- Keyboard accessible

**Props:**
```typescript
interface AnimatedCardProps {
  children: ReactNode;
  variant?: 'lift' | 'tilt' | 'glow' | 'border' | 'scale';
  intensity?: 'subtle' | 'medium' | 'strong';
  bordered?: boolean;
  shadow?: boolean;
}
```

**Usage:**
```tsx
import { AnimatedCard } from '@sahool/shared-ui';

<AnimatedCard variant="lift" intensity="medium">
  <h3>Interactive Card</h3>
  <p>Hover to see the animation</p>
</AnimatedCard>
```

---

### 4. GradientText

Text with gradient colors and optional animation.

**Features:**
- Six color variants
- Five size options
- Animated gradient option
- Renders as any heading or text element
- Background-clip text technique

**Props:**
```typescript
interface GradientTextProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'rainbow' | 'sunset' | 'ocean' | 'forest';
  animated?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  as?: 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p';
}
```

**Usage:**
```tsx
import { GradientText } from '@sahool/shared-ui';

<GradientText
  variant="rainbow"
  size="2xl"
  as="h1"
  animated
>
  Welcome to SAHOOL
</GradientText>
```

---

### 5. FloatingLabel

Modern floating label input with smooth animations.

**Features:**
- Three visual variants
- Three size options
- Icon support (left or right)
- Error and helper text
- Auto-floating on focus/value
- Fully accessible with ARIA attributes

**Props:**
```typescript
interface FloatingLabelProps {
  label: string;
  error?: string;
  helperText?: string;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  variant?: 'default' | 'filled' | 'outlined';
  inputSize?: 'sm' | 'md' | 'lg';
}
```

**Usage:**
```tsx
import { FloatingLabel } from '@sahool/shared-ui';
import { Mail } from 'lucide-react';

<FloatingLabel
  label="Email Address"
  type="email"
  variant="outlined"
  icon={Mail}
  helperText="We'll never share your email"
  error={errors.email}
/>
```

---

### 6. Shimmer

Modern shimmer loading effect with customizable shapes.

**Features:**
- Four shape variants
- Multiple loading instances
- Three animation speeds
- Dark mode support
- Spacing control
- ShimmerGroup component for complex layouts

**Props:**
```typescript
interface ShimmerProps {
  variant?: 'text' | 'rectangular' | 'circular' | 'rounded';
  width?: string | number;
  height?: string | number;
  count?: number;
  spacing?: 'sm' | 'md' | 'lg';
  speed?: 'slow' | 'normal' | 'fast';
}

interface ShimmerGroupProps {
  children?: ReactNode;
  loading?: boolean;
}
```

**Usage:**
```tsx
import { Shimmer, ShimmerGroup } from '@sahool/shared-ui';

// Simple shimmer
<Shimmer variant="text" count={3} spacing="md" />

// Complex skeleton
<ShimmerGroup loading={isLoading}>
  <div className="flex gap-4">
    <Shimmer variant="circular" width={60} height={60} />
    <div className="flex-1">
      <Shimmer variant="text" width="80%" />
      <Shimmer variant="text" width="60%" />
    </div>
  </div>
</ShimmerGroup>
```

---

### 7. ProgressRing

Circular progress indicator with smooth animations.

**Features:**
- Five color variants including gradient
- Four size options
- Three thickness levels
- Animated progress updates
- Optional value display
- Custom label support
- Custom children for center content

**Props:**
```typescript
interface ProgressRingProps {
  progress: number; // 0-100
  size?: 'sm' | 'md' | 'lg' | 'xl';
  thickness?: 'thin' | 'medium' | 'thick';
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'gradient';
  showValue?: boolean;
  label?: string;
  animated?: boolean;
  children?: ReactNode;
}
```

**Usage:**
```tsx
import { ProgressRing } from '@sahool/shared-ui';

<ProgressRing
  progress={75}
  variant="gradient"
  size="lg"
  label="Complete"
/>

// With custom content
<ProgressRing progress={50} variant="primary" showValue={false}>
  <div className="text-center">
    <div className="text-2xl font-bold">50</div>
    <div className="text-xs">Tasks</div>
  </div>
</ProgressRing>
```

---

### 8. Tooltip

Modern tooltip with arrow, animations, and positioning.

**Features:**
- Four position options
- Three visual variants
- Configurable delay
- Optional arrow
- Smooth fade animations
- Keyboard accessible
- Auto-positioning support

**Props:**
```typescript
interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  variant?: 'dark' | 'light' | 'primary';
  delay?: number;
  arrow?: boolean;
  disabled?: boolean;
}
```

**Usage:**
```tsx
import { Tooltip, TooltipProvider } from '@sahool/shared-ui';

<Tooltip
  content="Click to save"
  position="top"
  variant="dark"
  delay={300}
>
  <button>Save</button>
</Tooltip>

// With provider for global settings
<TooltipProvider delayDuration={200}>
  <Tooltip content="Delete item">
    <button>Delete</button>
  </Tooltip>
</TooltipProvider>
```

---

## 🎯 Common Features

All modern components include:

### ✅ Accessibility
- ARIA attributes for screen readers
- Keyboard navigation support
- Focus management
- Semantic HTML
- Proper roles and labels

### 🌓 Dark Mode
- Full dark mode support using Tailwind's `dark:` prefix
- Automatic color adjustments
- Consistent theming

### 🎨 Customization
- Tailwind CSS classes
- `className` prop for custom styling
- CSS variables support
- Extendable theme

### ⚡ Performance
- Optimized animations using CSS transforms
- `will-change` and `transform-gpu` for hardware acceleration
- Minimal re-renders with React.forwardRef
- Lazy loading compatible

---

## 🔧 Installation & Setup

1. **Install dependencies:**
```bash
npm install @sahool/shared-ui
# or
yarn add @sahool/shared-ui
```

2. **Configure Tailwind CSS:**

Make sure your Tailwind config includes the shared-ui content:

```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './node_modules/@sahool/shared-ui/**/*.{js,ts,jsx,tsx}',
  ],
  // ... rest of config
}
```

3. **Import components:**
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

## 🎨 Theming

The components use the `sahool` color palette from Tailwind. You can customize it:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        sahool: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ... your custom colors
          600: '#0284c7',
          // ...
        },
      },
    },
  },
}
```

---

## 🚀 Best Practices

1. **Combine Components:** Mix and match components for rich UIs
2. **Use forwardRef:** All components support refs for DOM access
3. **Accessibility First:** Always provide labels and ARIA attributes
4. **Performance:** Use `loading` states to improve perceived performance
5. **Dark Mode:** Test components in both light and dark modes
6. **Responsive Design:** Components are mobile-first and responsive

---

## 📚 Examples

See `ModernComponents.example.tsx` for comprehensive usage examples.

---

## 🤝 Contributing

When adding new modern components:

1. Follow the existing component structure
2. Include TypeScript interfaces
3. Support dark mode
4. Add ARIA attributes
5. Use forwardRef for DOM access
6. Include smooth animations
7. Export from `index.ts`
8. Document in this file

---

## 📝 License

Part of the SAHOOL Unified Platform - Educational Institution Management System
