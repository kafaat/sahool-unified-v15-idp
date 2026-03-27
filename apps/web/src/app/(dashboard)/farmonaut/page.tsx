/**
 * Farmonaut Satellite Monitoring Dashboard
 * لوحة مراقبة الأقمار الصناعية فارمونوت
 */

import { Metadata } from 'next';
import FarmonautClient from './FarmonautClient';

export const metadata: Metadata = {
  title: 'Farmonaut Satellite Monitoring | SAHOOL',
  description: 'Comprehensive satellite-based crop health monitoring, water stress detection, and field intelligence',
};

export default function FarmonautPage() {
  return <FarmonautClient />;
}
