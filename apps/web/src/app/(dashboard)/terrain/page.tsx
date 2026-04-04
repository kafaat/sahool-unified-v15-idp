/**
 * Terrain Analysis Page
 * صفحة تحليل التضاريس
 */

import { Metadata } from 'next';
import TerrainClient from './TerrainClient';

export const metadata: Metadata = {
  title: 'Terrain Analysis | SAHOOL',
  description: 'تحليل التضاريس - DEM processing, slope analysis, and field leveling optimization',
};

export default function TerrainPage() {
  return <TerrainClient />;
}
