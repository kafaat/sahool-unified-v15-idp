/**
 * Satellite Analysis Page
 * صفحة تحليل الأقمار الصناعية
 */

import { Metadata } from 'next';
import SatelliteClient from './SatelliteClient';

export const metadata: Metadata = {
  title: 'Satellite Analysis | SAHOOL',
  description: 'View satellite imagery and vegetation indices for your fields',
};

export default function SatellitePage() {
  return <SatelliteClient />;
}
