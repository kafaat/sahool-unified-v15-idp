/**
 * Dynamic ObservationMarker Component with Code Splitting
 * مكون علامة الملاحظة مع تقسيم الكود
 */

'use client';

import dynamic from 'next/dynamic';
import { MapLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { ObservationMarkerProps } from './ObservationMarker';

// Dynamic import with code splitting - leaflet + react-leaflet will be loaded on demand
const ObservationMarkerComponent = dynamic<ObservationMarkerProps>(
  () =>
    import('./ObservationMarker').then(
      (mod) => mod.ObservationMarker as ComponentType<ObservationMarkerProps>
    ),
  {
    loading: () => <MapLoadingSpinner height="200px" />,
    ssr: false,
  }
);

export const ObservationMarker = ObservationMarkerComponent;
export default ObservationMarkerComponent;
