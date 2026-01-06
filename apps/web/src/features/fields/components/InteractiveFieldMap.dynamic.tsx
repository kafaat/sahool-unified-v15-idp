/**
 * Dynamic InteractiveFieldMap Component with Code Splitting
 * مكون خريطة الحقول التفاعلية مع تقسيم الكود
 */

'use client';

import dynamic from 'next/dynamic';
import { MapLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { InteractiveFieldMapProps } from './InteractiveFieldMap';

// Dynamic import with code splitting - leaflet (~150KB) + react-leaflet will be loaded on demand
const InteractiveFieldMapComponent = dynamic<InteractiveFieldMapProps>(
  () => import('./InteractiveFieldMap').then((mod) => mod.InteractiveFieldMap as ComponentType<InteractiveFieldMapProps>),
  {
    loading: () => <MapLoadingSpinner height="600px" />,
    ssr: false,
  }
);

export const InteractiveFieldMap = InteractiveFieldMapComponent;
export default InteractiveFieldMapComponent;
