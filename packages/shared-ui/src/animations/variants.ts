// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Framer Motion Variants
// Reusable motion variants for Framer Motion (optional dependency)
// متغيرات الحركة القابلة لإعادة الاستخدام
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Note: These variants are designed for Framer Motion.
 * They can be used if framer-motion is installed, otherwise use CSS animations.
 */

/**
 * Fade animations
 */
export const fadeVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

/**
 * Fade with scale animations
 */
export const fadeScaleVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 },
};

/**
 * Slide up animations
 */
export const slideUpVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

/**
 * Slide down animations
 */
export const slideDownVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
};

/**
 * Slide left animations
 */
export const slideLeftVariants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

/**
 * Slide right animations
 */
export const slideRightVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

/**
 * Scale in animations
 */
export const scaleInVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 },
};

/**
 * Bounce in animations
 */
export const bounceInVariants = {
  hidden: { opacity: 0, scale: 0.3 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 260,
      damping: 20,
    },
  },
  exit: { opacity: 0, scale: 0.3 },
};

/**
 * Rotate in animations
 */
export const rotateInVariants = {
  hidden: { opacity: 0, rotate: -180, scale: 0 },
  visible: {
    opacity: 1,
    rotate: 0,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 15,
    },
  },
  exit: { opacity: 0, rotate: 180, scale: 0 },
};

/**
 * Staggered container variants
 */
export const staggerContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

/**
 * Staggered item variants
 */
export const staggerItemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 24,
    },
  },
  exit: { opacity: 0, y: -20 },
};

/**
 * Page transition variants
 */
export const pageTransitionVariants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.2,
      ease: 'easeIn',
    },
  },
};

/**
 * Modal/Dialog variants
 */
export const modalVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 20,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: {
      duration: 0.2,
      ease: 'easeIn',
    },
  },
};

/**
 * Backdrop/Overlay variants
 */
export const backdropVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * Drawer/Sidebar variants
 */
export const drawerVariants = {
  left: {
    hidden: { x: '-100%' },
    visible: {
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
    exit: { x: '-100%' },
  },
  right: {
    hidden: { x: '100%' },
    visible: {
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
    exit: { x: '100%' },
  },
  top: {
    hidden: { y: '-100%' },
    visible: {
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
    exit: { y: '-100%' },
  },
  bottom: {
    hidden: { y: '100%' },
    visible: {
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    },
    exit: { y: '100%' },
  },
};

/**
 * Notification/Toast variants
 */
export const notificationVariants = {
  topRight: {
    hidden: { opacity: 0, x: 100, y: 0 },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 25,
      },
    },
    exit: {
      opacity: 0,
      x: 100,
      transition: {
        duration: 0.2,
      },
    },
  },
  topLeft: {
    hidden: { opacity: 0, x: -100, y: 0 },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 25,
      },
    },
    exit: {
      opacity: 0,
      x: -100,
      transition: {
        duration: 0.2,
      },
    },
  },
  bottomRight: {
    hidden: { opacity: 0, x: 100, y: 0 },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 25,
      },
    },
    exit: {
      opacity: 0,
      x: 100,
      transition: {
        duration: 0.2,
      },
    },
  },
  bottomLeft: {
    hidden: { opacity: 0, x: -100, y: 0 },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 25,
      },
    },
    exit: {
      opacity: 0,
      x: -100,
      transition: {
        duration: 0.2,
      },
    },
  },
};

/**
 * Collapse/Expand variants
 */
export const collapseVariants = {
  collapsed: {
    height: 0,
    opacity: 0,
    overflow: 'hidden',
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    overflow: 'visible',
    transition: {
      height: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
      opacity: {
        duration: 0.2,
      },
    },
  },
};

/**
 * Hover interaction variants
 */
export const hoverVariants = {
  scale: {
    rest: { scale: 1 },
    hover: {
      scale: 1.05,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 10,
      },
    },
    tap: { scale: 0.95 },
  },
  lift: {
    rest: { y: 0 },
    hover: {
      y: -4,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 10,
      },
    },
  },
  glow: {
    rest: { boxShadow: '0 0 0 rgba(34, 197, 94, 0)' },
    hover: {
      boxShadow: '0 10px 30px rgba(34, 197, 94, 0.3)',
      transition: {
        duration: 0.3,
      },
    },
  },
};

/**
 * Loading spinner variants
 */
export const spinnerVariants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Pulse variants
 */
export const pulseVariants = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Bounce variants
 */
export const bounceVariants = {
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Shimmer/Skeleton loading variants
 */
export const shimmerVariants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Spring configuration presets
 */
export const springPresets = {
  gentle: {
    type: 'spring' as const,
    stiffness: 120,
    damping: 20,
  },
  wobbly: {
    type: 'spring' as const,
    stiffness: 180,
    damping: 12,
  },
  stiff: {
    type: 'spring' as const,
    stiffness: 400,
    damping: 30,
  },
  slow: {
    type: 'spring' as const,
    stiffness: 80,
    damping: 20,
  },
  molasses: {
    type: 'spring' as const,
    stiffness: 60,
    damping: 20,
  },
};

/**
 * Transition presets
 */
export const transitionPresets = {
  fast: { duration: 0.15, ease: 'easeInOut' },
  normal: { duration: 0.3, ease: 'easeInOut' },
  slow: { duration: 0.5, ease: 'easeInOut' },
  spring: springPresets.gentle,
  bounce: springPresets.wobbly,
};
