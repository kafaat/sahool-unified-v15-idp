/**
 * React Type Augmentations for React 19 Compatibility
 * Fixes JSX component type issues with React 19
 */

import 'react';

declare module 'react' {
  // Augment the global JSX namespace to fix React 19 compatibility
  namespace JSX {
    interface ElementAttributesProperty {
      props: Record<string, unknown>;
    }
  }
}

// Ensure this file is treated as a module
export {};
