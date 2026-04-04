/**
 * Soil Map Page
 * صفحة خريطة التربة
 */

import { Metadata } from 'next';
import SoilMapClient from './SoilMapClient';

export const metadata: Metadata = {
  title: 'Soil Map | SAHOOL',
  description: 'خريطة التربة - Interactive soil type map with agro-ecological zones and analysis',
};

export default function SoilMapPage() {
  return <SoilMapClient />;
}
