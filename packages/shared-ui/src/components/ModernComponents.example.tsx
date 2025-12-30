'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Modern Components Examples - أمثلة المكونات الحديثة
// Comprehensive examples showcasing all modern UI components
// ═══════════════════════════════════════════════════════════════════════════════

import {
  GlassCard,
  ModernButton,
  AnimatedCard,
  GradientText,
  FloatingLabel,
  Shimmer,
  ShimmerGroup,
  ProgressRing,
  Tooltip,
} from '../index';
import { Heart, Sparkles, Rocket, Mail, Lock } from 'lucide-react';

export function ModernComponentsShowcase() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center space-y-4">
          <GradientText
            as="h1"
            size="2xl"
            variant="primary"
            animated
            className="text-5xl font-bold"
          >
            Modern UI Components
          </GradientText>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Beautiful, accessible, and highly customizable components
          </p>
        </div>

        {/* GlassCard Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Glass Cards
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard variant="light" blur="md" hover>
              <h3 className="text-lg font-semibold mb-2">Light Variant</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Subtle glassmorphism effect with light background
              </p>
            </GlassCard>

            <GlassCard variant="medium" blur="lg" hover>
              <h3 className="text-lg font-semibold mb-2">Medium Variant</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Balanced transparency with medium blur
              </p>
            </GlassCard>

            <GlassCard variant="dark" blur="xl" hover>
              <h3 className="text-lg font-semibold mb-2">Dark Variant</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Strong glass effect with extra blur
              </p>
            </GlassCard>
          </div>
        </section>

        {/* ModernButton Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Modern Buttons
          </h2>
          <div className="flex flex-wrap gap-4">
            <ModernButton variant="gradient" icon={Sparkles}>
              Gradient Button
            </ModernButton>

            <ModernButton variant="glow" icon={Heart} iconPosition="right">
              Glow Effect
            </ModernButton>

            <ModernButton variant="outline" size="lg">
              Outlined
            </ModernButton>

            <ModernButton variant="ghost" size="sm" icon={Rocket}>
              Ghost Style
            </ModernButton>

            <ModernButton variant="solid" loading>
              Loading...
            </ModernButton>

            <ModernButton variant="gradient" glow fullWidth>
              Full Width with Glow
            </ModernButton>
          </div>
        </section>

        {/* AnimatedCard Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Animated Cards
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatedCard variant="lift" intensity="medium">
              <h3 className="text-lg font-semibold mb-2">Lift Animation</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Hover to see the card lift with smooth transition
              </p>
            </AnimatedCard>

            <AnimatedCard variant="tilt" intensity="strong">
              <h3 className="text-lg font-semibold mb-2">Tilt Effect</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Card rotates and scales on hover
              </p>
            </AnimatedCard>

            <AnimatedCard variant="glow" intensity="medium">
              <h3 className="text-lg font-semibold mb-2">Glow Shadow</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Glowing shadow effect on interaction
              </p>
            </AnimatedCard>

            <AnimatedCard variant="border" intensity="subtle">
              <h3 className="text-lg font-semibold mb-2">Border Highlight</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Border changes color on hover
              </p>
            </AnimatedCard>

            <AnimatedCard variant="scale" intensity="medium">
              <h3 className="text-lg font-semibold mb-2">Scale Transform</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Card grows larger when hovered
              </p>
            </AnimatedCard>
          </div>
        </section>

        {/* GradientText Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Gradient Text
          </h2>
          <div className="space-y-4">
            <GradientText variant="primary" size="2xl">
              Primary Gradient Text
            </GradientText>
            <GradientText variant="rainbow" size="xl" animated>
              Animated Rainbow Gradient
            </GradientText>
            <GradientText variant="sunset" size="lg">
              Sunset Colors
            </GradientText>
            <GradientText variant="ocean" size="md">
              Ocean Waves
            </GradientText>
            <GradientText variant="forest" size="sm">
              Forest Green
            </GradientText>
          </div>
        </section>

        {/* FloatingLabel Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Floating Label Inputs
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
            <FloatingLabel
              label="Email Address"
              type="email"
              variant="outlined"
              icon={Mail}
              helperText="We'll never share your email"
            />

            <FloatingLabel
              label="Password"
              type="password"
              variant="filled"
              icon={Lock}
            />

            <FloatingLabel
              label="Username"
              variant="default"
              inputSize="lg"
            />

            <FloatingLabel
              label="Error Example"
              variant="outlined"
              error="This field is required"
            />
          </div>
        </section>

        {/* Shimmer Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Shimmer Loading
          </h2>
          <div className="space-y-6 max-w-2xl">
            <div>
              <h3 className="text-lg font-semibold mb-4">Text Lines</h3>
              <Shimmer variant="text" count={3} spacing="md" />
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Rectangular</h3>
              <Shimmer variant="rectangular" height={200} />
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Circular Avatar</h3>
              <Shimmer variant="circular" width={80} height={80} />
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Card Skeleton</h3>
              <ShimmerGroup>
                <div className="flex gap-4">
                  <Shimmer variant="circular" width={60} height={60} />
                  <div className="flex-1 space-y-3">
                    <Shimmer variant="text" width="80%" />
                    <Shimmer variant="text" width="60%" />
                  </div>
                </div>
              </ShimmerGroup>
            </div>
          </div>
        </section>

        {/* ProgressRing Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Progress Rings
          </h2>
          <div className="flex flex-wrap gap-8 justify-center">
            <ProgressRing progress={25} variant="primary" size="sm" />
            <ProgressRing progress={50} variant="success" size="md" label="Complete" />
            <ProgressRing progress={75} variant="warning" size="lg" thickness="thick" />
            <ProgressRing progress={100} variant="gradient" size="xl" />
          </div>
        </section>

        {/* Tooltip Examples */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Tooltips
          </h2>
          <div className="flex flex-wrap gap-6 justify-center">
            <Tooltip content="This is a dark tooltip" position="top">
              <button className="px-4 py-2 bg-gray-200 dark:bg-gray-800 rounded-lg">
                Hover me (Top)
              </button>
            </Tooltip>

            <Tooltip content="Light variant tooltip" position="bottom" variant="light">
              <button className="px-4 py-2 bg-gray-200 dark:bg-gray-800 rounded-lg">
                Hover me (Bottom)
              </button>
            </Tooltip>

            <Tooltip content="Primary colored tooltip" position="left" variant="primary">
              <button className="px-4 py-2 bg-gray-200 dark:bg-gray-800 rounded-lg">
                Hover me (Left)
              </button>
            </Tooltip>

            <Tooltip content="No arrow tooltip" position="right" arrow={false}>
              <button className="px-4 py-2 bg-gray-200 dark:bg-gray-800 rounded-lg">
                Hover me (Right)
              </button>
            </Tooltip>
          </div>
        </section>

        {/* Combined Example */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Combined Example
          </h2>
          <GlassCard variant="medium" blur="lg" className="max-w-2xl mx-auto">
            <AnimatedCard variant="lift" bordered={false} shadow={false}>
              <div className="space-y-6">
                <GradientText variant="primary" size="xl" as="h3">
                  Sign Up for Updates
                </GradientText>

                <div className="space-y-4">
                  <FloatingLabel
                    label="Your Email"
                    type="email"
                    variant="outlined"
                    icon={Mail}
                  />

                  <div className="flex items-center gap-4">
                    <ProgressRing
                      progress={66}
                      variant="gradient"
                      size="md"
                      label="Profile"
                    />

                    <div className="flex-1">
                      <Tooltip content="Complete your profile to unlock features" position="top">
                        <ModernButton variant="gradient" glow fullWidth icon={Sparkles}>
                          Get Started
                        </ModernButton>
                      </Tooltip>
                    </div>
                  </div>
                </div>
              </div>
            </AnimatedCard>
          </GlassCard>
        </section>
      </div>
    </div>
  );
}

export default ModernComponentsShowcase;
