// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Animation Examples
// Practical examples demonstrating animation utilities and components
// أمثلة عملية للرسوم المتحركة
// ═══════════════════════════════════════════════════════════════════════════════

import React from 'react';
import {
  AnimatedContainer,
  FadeIn,
  SlideUp,
  ScaleIn,
  BounceIn,
} from '../components/AnimatedContainer';
import {
  StaggeredList,
  StaggerSlideUp,
  StaggeredGrid,
} from '../components/StaggeredList';
import {
  PageTransition,
  TransitionLayout,
} from '../components/PageTransition';
import { HOVER_ANIMATIONS, FOCUS_ANIMATIONS } from './index';

/**
 * Example 1: Hero Section with Staggered Content
 */
export function HeroSectionExample() {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-sahool-brown-50">
      <div className="container mx-auto px-4">
        <StaggerSlideUp staggerDelay={150}>
          {/* Heading */}
          <h1 className="text-5xl md:text-7xl font-bold text-sahool-green-800 mb-6">
            مرحباً بكم في صحول
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-sahool-brown-700 mb-8 max-w-2xl">
            منصة موحدة للتعليم والإدارة المدرسية
          </p>

          {/* CTA Buttons */}
          <div className="flex gap-4 flex-wrap">
            <button className={`px-8 py-4 bg-sahool-green-600 text-white rounded-lg font-bold ${HOVER_ANIMATIONS.scale} ${FOCUS_ANIMATIONS.ring}`}>
              ابدأ الآن
            </button>
            <button className={`px-8 py-4 border-2 border-sahool-green-600 text-sahool-green-600 rounded-lg font-bold ${HOVER_ANIMATIONS.lift}`}>
              معرفة المزيد
            </button>
          </div>
        </StaggerSlideUp>
      </div>
    </section>
  );
}

/**
 * Example 2: Feature Cards Grid
 */
export function FeatureGridExample() {
  const features = [
    { id: 1, title: 'إدارة الطلاب', icon: '👨‍🎓', description: 'نظام شامل لإدارة بيانات الطلاب' },
    { id: 2, title: 'الحضور والغياب', icon: '✓', description: 'تتبع الحضور تلقائياً' },
    { id: 3, title: 'الدرجات', icon: '📊', description: 'إدارة وتحليل الدرجات' },
    { id: 4, title: 'التواصل', icon: '💬', description: 'تواصل فعال مع أولياء الأمور' },
    { id: 5, title: 'التقارير', icon: '📈', description: 'تقارير شاملة ومفصلة' },
    { id: 6, title: 'الجداول', icon: '📅', description: 'جدولة ذكية للحصص' },
  ];

  return (
    <section className="py-20 px-4">
      <div className="container mx-auto">
        <FadeIn>
          <h2 className="text-4xl font-bold text-center mb-4 text-sahool-green-800">
            الميزات الرئيسية
          </h2>
          <p className="text-xl text-center mb-12 text-sahool-brown-600">
            كل ما تحتاجه لإدارة مدرستك بكفاءة
          </p>
        </FadeIn>

        <StaggeredGrid
          columns={{ sm: 1, md: 2, lg: 3 }}
          animation="scaleIn"
          staggerDelay={100}
          animateOnScroll
          scrollConfig={{ threshold: 0.2, triggerOnce: true }}
          gap="2rem"
        >
          {features.map(feature => (
            <div
              key={feature.id}
              className={`p-6 bg-white rounded-xl shadow-lg border border-sahool-green-100 ${HOVER_ANIMATIONS.lift}`}
            >
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3 className="text-2xl font-bold mb-2 text-sahool-green-700">
                {feature.title}
              </h3>
              <p className="text-sahool-brown-600">{feature.description}</p>
            </div>
          ))}
        </StaggeredGrid>
      </div>
    </section>
  );
}

/**
 * Example 3: Stats Counter with Animations
 */
export function StatsCounterExample() {
  const stats = [
    { value: '10,000+', label: 'طالب', icon: '👨‍🎓' },
    { value: '500+', label: 'معلم', icon: '👨‍🏫' },
    { value: '50+', label: 'مدرسة', icon: '🏫' },
    { value: '99%', label: 'رضا المستخدمين', icon: '⭐' },
  ];

  return (
    <section className="py-20 px-4 bg-sahool-green-600 text-white">
      <div className="container mx-auto">
        <StaggeredList
          animation="bounceIn"
          staggerDelay={150}
          animateOnScroll
          scrollConfig={{ threshold: 0.5, triggerOnce: true }}
          as="div"
          className="grid grid-cols-2 md:grid-cols-4 gap-8"
        >
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-5xl mb-4">{stat.icon}</div>
              <div className="text-4xl md:text-5xl font-bold mb-2">
                {stat.value}
              </div>
              <div className="text-xl opacity-90">{stat.label}</div>
            </div>
          ))}
        </StaggeredList>
      </div>
    </section>
  );
}

/**
 * Example 4: Notification Toast with Animation
 */
export function NotificationToastExample({
  message,
  type = 'success',
  onClose,
}: {
  message: string;
  type?: 'success' | 'error' | 'info';
  onClose: () => void;
}) {
  const bgColor = {
    success: 'bg-sahool-green-100 border-sahool-green-500 text-sahool-green-800',
    error: 'bg-red-100 border-red-500 text-red-800',
    info: 'bg-blue-100 border-blue-500 text-blue-800',
  }[type];

  return (
    <AnimatedContainer
      animation={{ preset: 'slideLeft', duration: 'fast', easing: 'spring' }}
      animateOnMount
      className="fixed top-4 right-4 z-50"
    >
      <div className={`p-4 rounded-lg border-l-4 shadow-lg ${bgColor} max-w-md`}>
        <div className="flex items-center justify-between">
          <p className="font-medium">{message}</p>
          <button
            onClick={onClose}
            className={`ml-4 text-2xl ${HOVER_ANIMATIONS.scale}`}
          >
            ×
          </button>
        </div>
      </div>
    </AnimatedContainer>
  );
}

/**
 * Example 5: Loading State with Animations
 */
export function LoadingStateExample() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="inline-block animate-spin text-6xl mb-4 text-sahool-green-600">
          ⚙️
        </div>
        <div className="animate-pulse text-xl text-sahool-brown-600">
          جاري التحميل...
        </div>
      </div>
    </div>
  );
}

/**
 * Example 6: Modal Dialog with Backdrop
 */
export function ModalDialogExample({
  isOpen,
  onClose,
  title,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <FadeIn>
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={onClose}
        />
      </FadeIn>

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <ScaleIn duration="fast">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-sahool-green-800">
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className={`text-3xl text-gray-500 ${HOVER_ANIMATIONS.rotate}`}
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6">{children}</div>
          </div>
        </ScaleIn>
      </div>
    </>
  );
}

/**
 * Example 7: Scroll-Triggered Content Sections
 */
export function ScrollSectionsExample() {
  const sections = [
    {
      title: 'التخطيط السهل',
      content: 'خطط لدروسك وواجباتك بسهولة',
      image: '📝',
    },
    {
      title: 'التتبع الفوري',
      content: 'تابع تقدم طلابك في الوقت الفعلي',
      image: '📊',
    },
    {
      title: 'التقارير الذكية',
      content: 'احصل على رؤى عميقة من خلال التقارير التحليلية',
      image: '💡',
    },
  ];

  return (
    <div className="space-y-32 py-20">
      {sections.map((section, index) => (
        <AnimatedContainer
          key={index}
          animation={{
            preset: index % 2 === 0 ? 'slideRight' : 'slideLeft',
            duration: 'slow',
            easing: 'ease-out',
          }}
          animateOnScroll
          scrollConfig={{ threshold: 0.3, triggerOnce: true }}
        >
          <div className="container mx-auto px-4">
            <div className={`flex flex-col md:flex-row items-center gap-12 ${index % 2 === 0 ? '' : 'md:flex-row-reverse'}`}>
              <div className="flex-1">
                <div className="text-8xl mb-6">{section.image}</div>
                <h3 className="text-4xl font-bold mb-4 text-sahool-green-800">
                  {section.title}
                </h3>
                <p className="text-xl text-sahool-brown-600">
                  {section.content}
                </p>
              </div>
              <div className="flex-1">
                <div className="aspect-video bg-gradient-to-br from-sahool-green-100 to-sahool-brown-100 rounded-2xl shadow-xl" />
              </div>
            </div>
          </div>
        </AnimatedContainer>
      ))}
    </div>
  );
}

/**
 * Example 8: Complete Page with Transition Layout
 */
export function CompletePageExample({ currentPage }: { currentPage: string }) {
  return (
    <TransitionLayout
      header={
        <header className="bg-white shadow-sm py-4 px-6">
          <div className="container mx-auto flex items-center justify-between">
            <h1 className="text-2xl font-bold text-sahool-green-700">صحول</h1>
            <nav className="flex gap-6">
              <a href="#" className={HOVER_ANIMATIONS.scale}>الرئيسية</a>
              <a href="#" className={HOVER_ANIMATIONS.scale}>الميزات</a>
              <a href="#" className={HOVER_ANIMATIONS.scale}>الأسعار</a>
              <a href="#" className={HOVER_ANIMATIONS.scale}>اتصل بنا</a>
            </nav>
          </div>
        </header>
      }
      footer={
        <footer className="bg-sahool-green-800 text-white py-12 px-6">
          <div className="container mx-auto text-center">
            <p className="text-lg">© 2025 صحول. جميع الحقوق محفوظة.</p>
          </div>
        </footer>
      }
      transitionType="slide-up"
      transitionKey={currentPage}
    >
      <main className="container mx-auto px-4 py-12 min-h-screen">
        <h1 className="text-4xl font-bold mb-8">محتوى الصفحة: {currentPage}</h1>
        <p className="text-xl text-sahool-brown-600">
          هذا مثال على صفحة كاملة مع انتقالات سلسة بين المحتوى.
        </p>
      </main>
    </TransitionLayout>
  );
}

/**
 * Example 9: Interactive Card with Hover Effects
 */
export function InteractiveCardExample() {
  return (
    <div className={`
      relative p-8 bg-white rounded-2xl shadow-lg
      border border-sahool-green-100
      ${HOVER_ANIMATIONS.lift}
      ${HOVER_ANIMATIONS.glow}
      cursor-pointer
      transition-all duration-300
    `}>
      <div className="text-5xl mb-4">🎓</div>
      <h3 className="text-2xl font-bold mb-2 text-sahool-green-700">
        عنوان البطاقة
      </h3>
      <p className="text-sahool-brown-600 mb-4">
        وصف البطاقة مع تأثيرات تفاعلية عند التمرير
      </p>
      <button className={`
        px-6 py-3 bg-sahool-green-600 text-white rounded-lg font-bold
        ${HOVER_ANIMATIONS.scale}
        ${FOCUS_ANIMATIONS.ring}
      `}>
        اقرأ المزيد
      </button>
    </div>
  );
}

/**
 * Example 10: Skeleton Loading State
 */
export function SkeletonLoadingExample() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map(i => (
        <div key={i} className="p-6 bg-white rounded-xl shadow">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-gray-200 rounded-full animate-pulse" />
            <div className="flex-1 space-y-3">
              <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
              <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
