/**
 * Dynamic FieldMap Component with Code Splitting
 * مكون خريطة الحقل مع تقسيم الكود
 *
 * Ensures leaflet (~40KB gzipped) and react-leaflet (~10KB gzipped) are
 * never included in the initial page-load bundle. They are loaded on
 * demand the first time a FieldMap is rendered.
 */

'use client';

import dynamic from 'next/dynamic';
import { MapLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { Field } from '../types';

interface FieldMapProps {
  field?: Field;
  fields?: Field[];
  height?: string;
  onFieldClick?: (fieldId: string) => void;
}

// Dynamic import with code splitting - leaflet + react-leaflet will be loaded on demand
const FieldMapComponent = dynamic<FieldMapProps>(
  () => import('./FieldMap').then((mod) => mod.FieldMap as ComponentType<FieldMapProps>),
  {
    loading: () => <MapLoadingSpinner height="400px" />,
    ssr: false,
  }
);

export const FieldMap = FieldMapComponent;
export default FieldMapComponent;
