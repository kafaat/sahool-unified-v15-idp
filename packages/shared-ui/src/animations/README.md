# SAHOOL Animation System

A comprehensive, modern animation system built with CSS animations and optional Framer Motion support.

## Features

- **CSS-first**: Pure CSS animations with no external dependencies required
- **Performance**: Hardware-accelerated transforms and opacity
- **TypeScript**: Full type safety and IntelliSense support
- **Flexible**: Works with or without Framer Motion
- **Accessible**: Respects `prefers-reduced-motion`
- **RTL Support**: Works seamlessly with Arabic/RTL layouts

## Quick Start

### Basic Animations

```tsx
import { FadeIn, SlideUp, ScaleIn } from '@sahool/shared-ui';

// Simple fade in
<FadeIn>
  <Card>Content</Card>
</FadeIn>

// Slide up animation
<SlideUp duration="slow">
  <div>Slides up smoothly</div>
</SlideUp>

// Scale in with spring easing
<ScaleIn>
  <Button>Click me</Button>
</ScaleIn>
```

### Scroll-Triggered Animations

```tsx
import { AnimatedContainer } from '@sahool/shared-ui';

<AnimatedContainer
  animation={{ preset: 'slideUp', duration: 'normal', easing: 'ease-out' }}
  animateOnScroll
  scrollConfig={{ threshold: 0.3, triggerOnce: true }}
>
  <div>Animates when scrolled into view</div>
</AnimatedContainer>
```

### Staggered Lists

```tsx
import { StaggeredList, StaggeredGrid } from '@sahool/shared-ui';

// Staggered list
<StaggeredList
  animation="slideUp"
  staggerDelay={100}
  animateOnMount
>
  <Card>Item 1</Card>
  <Card>Item 2</Card>
  <Card>Item 3</Card>
</StaggeredList>

// Staggered grid
<StaggeredGrid
  columns={{ sm: 1, md: 2, lg: 3 }}
  animation="scaleIn"
  staggerDelay={75}
  animateOnScroll
  scrollConfig={{ triggerOnce: true }}
>
  {products.map(product => (
    <ProductCard key={product.id} product={product} />
  ))}
</StaggeredGrid>
```

### Page Transitions

```tsx
import { PageTransition, TransitionLayout, RouteTransition } from '@sahool/shared-ui';

// Next.js App Router
export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <PageTransition type="slide-up" transitionKey={pathname}>
      {children}
    </PageTransition>
  );
}

// With persistent layout
<TransitionLayout
  header={<Header />}
  footer={<Footer />}
  sidebar={<Sidebar />}
  transitionType="fade"
  transitionKey={currentPage}
>
  <YourPageContent />
</TransitionLayout>

// React Router
function App() {
  const location = useLocation();

  return (
    <RouteTransition routeKey={location.pathname} type="slide-up">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </RouteTransition>
  );
}
```

## Tailwind CSS Utilities

All animations are available as Tailwind classes:

```tsx
// Fade animations
<div className="animate-fade-in duration-300">Fades in</div>
<div className="animate-fade-out duration-500">Fades out</div>

// Slide animations
<div className="animate-slide-up duration-300">Slides up</div>
<div className="animate-slide-down duration-300">Slides down</div>
<div className="animate-slide-left duration-300">Slides left</div>
<div className="animate-slide-right duration-300">Slides right</div>

// Scale animations
<div className="animate-scale-in duration-300">Scales in</div>

// Bounce animations
<div className="animate-bounce-in duration-500">Bounces in</div>

// Loading animations
<div className="animate-spin">Spins</div>
<div className="animate-pulse">Pulses</div>
<div className="animate-shimmer">Shimmer effect</div>

// With delays
<div className="animate-fade-in delay-100">Delayed fade</div>
<div className="animate-slide-up delay-200">Delayed slide</div>

// Custom durations
<div className="animate-fade-in duration-150">Fast</div>
<div className="animate-fade-in duration-300">Normal</div>
<div className="animate-fade-in duration-500">Slow</div>
<div className="animate-fade-in duration-700">Slower</div>

// Custom easing
<div className="animate-fade-in ease-spring">Spring easing</div>
<div className="animate-fade-in ease-bounce">Bounce easing</div>
```

## Hover & Interaction Utilities

```tsx
import { HOVER_ANIMATIONS, FOCUS_ANIMATIONS, TRANSITION_PRESETS } from '@sahool/shared-ui';

// Pre-defined hover effects
<button className={HOVER_ANIMATIONS.scale}>
  Scales on hover
</button>

<div className={HOVER_ANIMATIONS.lift}>
  Lifts and shows shadow on hover
</div>

<div className={HOVER_ANIMATIONS.glow}>
  Glows on hover
</div>

// Focus effects
<input className={FOCUS_ANIMATIONS.ring} />
<button className={FOCUS_ANIMATIONS.glow}>
  Glows on focus
</button>

// Smooth transitions
<div className={TRANSITION_PRESETS.fast}>
  Fast transitions
</div>

<div className={TRANSITION_PRESETS.spring}>
  Spring transitions
</div>
```

## Animation Presets

### Available Presets

- `fadeIn` / `fadeOut`
- `slideUp` / `slideDown` / `slideLeft` / `slideRight`
- `scaleIn` / `scaleOut`
- `bounceIn`
- `rotateIn`

### Durations

- `fast` - 150ms
- `normal` - 300ms (default)
- `slow` - 500ms
- `slower` - 700ms

### Easing Functions

- `linear`
- `ease`
- `ease-in`
- `ease-out`
- `ease-in-out` (default)
- `spring` - Bouncy spring effect
- `bounce` - Bounce effect

### Delays

- `none` - 0ms (default)
- `short` - 100ms
- `medium` - 200ms
- `long` - 300ms

## Framer Motion Variants (Optional)

If you have Framer Motion installed, you can use the pre-configured variants:

```tsx
import { motion } from 'framer-motion';
import { fadeVariants, slideUpVariants, staggerContainerVariants, staggerItemVariants } from '@sahool/shared-ui';

// Simple fade
<motion.div
  variants={fadeVariants}
  initial="hidden"
  animate="visible"
  exit="exit"
>
  Content
</motion.div>

// Staggered children
<motion.div
  variants={staggerContainerVariants}
  initial="hidden"
  animate="visible"
>
  {items.map((item, i) => (
    <motion.div key={i} variants={staggerItemVariants}>
      {item}
    </motion.div>
  ))}
</motion.div>
```

## Advanced Usage

### Custom Animation Hook

```tsx
import { useScrollAnimation } from '@sahool/shared-ui';

function MyComponent() {
  const { isVisible, elementRef } = useScrollAnimation({
    threshold: 0.5,
    triggerOnce: true,
  });

  return (
    <div ref={elementRef as any}>
      {isVisible && <AnimatedContent />}
    </div>
  );
}
```

### Programmatic Animation

```tsx
import { getAnimationClasses, getAnimationStyles } from '@sahool/shared-ui';

function MyComponent() {
  const config = {
    preset: 'fadeIn' as const,
    duration: 'normal' as const,
    easing: 'ease-out' as const,
    delay: 'short' as const,
  };

  const classes = getAnimationClasses(config);
  const styles = getAnimationStyles(config);

  return (
    <div className={classes} style={styles}>
      Content
    </div>
  );
}
```

### Stagger Configuration

```tsx
import { getStaggerDelay, getStaggerStyle } from '@sahool/shared-ui';

const staggerConfig = {
  delayPerChild: 100,
  maxDelay: 500,
};

{items.map((item, index) => (
  <div
    key={index}
    className="animate-fade-in"
    style={getStaggerStyle(index, staggerConfig)}
  >
    {item}
  </div>
))}
```

## Performance Tips

1. **Use transforms and opacity**: These properties are hardware-accelerated
2. **Avoid animating layout properties**: Don't animate `width`, `height`, `top`, `left`
3. **Use `will-change` sparingly**: Only for animations that need extra performance
4. **Respect `prefers-reduced-motion`**: Always test with reduced motion enabled
5. **Trigger once on scroll**: Use `triggerOnce: true` for scroll animations

## Accessibility

The animation system respects user preferences:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS animations with graceful degradation
- IntersectionObserver API for scroll animations (with polyfill support)

## Examples

Check out the `/examples` directory for complete implementation examples:

- Basic animations
- Scroll-triggered content
- Page transitions
- Loading states
- Micro-interactions
- Staggered lists and grids

## Contributing

When adding new animations:

1. Add keyframe to Tailwind config
2. Add animation class mapping
3. Create variant in `variants.ts` (if using Framer Motion)
4. Export types and utilities
5. Update documentation
6. Add tests

## License

Part of the SAHOOL Unified Platform - Licensed under the project's main license.
