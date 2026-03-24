/**
 * Dynamic ScoutingMode Component with Code Splitting
 * مكون وضع الكشافة الحقلية مع تقسيم الكود
 */

'use client';

import dynamic from 'next/dynamic';
import { MapLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { ScoutingModeProps } from './ScoutingMode';

// Dynamic import with code splitting - leaflet (~150KB) + react-leaflet will be loaded on demand
const ScoutingModeComponent = dynamic<ScoutingModeProps>(
  () =>
    import('./ScoutingMode').then((mod) => mod.ScoutingMode as ComponentType<ScoutingModeProps>),
  {
    loading: () => <MapLoadingSpinner height="600px" />,
    ssr: false,
  }
);

export const ScoutingMode = ScoutingModeComponent;
export default ScoutingModeComponent;
