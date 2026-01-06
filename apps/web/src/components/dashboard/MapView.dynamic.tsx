/**
 * Dynamic MapView Component with Code Splitting
 * مكون خريطة الحقول مع تقسيم الكود
 */

'use client';

import dynamic from 'next/dynamic';
import { MapLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { Field } from '@/lib/api/types';

interface MapViewProps {
  tenantId?: string;
  onFieldSelect?: (fieldId: string | null) => void;
  fields?: Field[];
}

// Dynamic import with code splitting - maplibre-gl (~200KB) will be loaded on demand
const MapViewComponent = dynamic<MapViewProps>(
  () => import('./MapView').then((mod) => mod.MapView as ComponentType<MapViewProps>),
  {
    loading: () => <MapLoadingSpinner />,
    ssr: false,
  }
);

export const MapView = MapViewComponent;
export default MapViewComponent;
