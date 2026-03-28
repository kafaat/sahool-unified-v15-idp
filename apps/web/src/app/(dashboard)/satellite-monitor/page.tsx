/**
 * Satellite Monitoring Dashboard
 * لوحة مراقبة الأقمار الصناعية
 */

import { Metadata } from 'next';
import SatelliteMonitorClient from './SatelliteMonitorClient';

export const metadata: Metadata = {
  title: 'Satellite Monitoring | SAHOOL',
  description: 'Comprehensive satellite-based crop health monitoring, water stress detection, and field intelligence',
};

export default function SatelliteMonitorPage() {
  return <SatelliteMonitorClient />;
}
