/**
 * Growing Degree Days (GDD) Page
 * صفحة درجات النمو الحراري
 */

import { Metadata } from 'next';
import GDDClient from './GDDClient';

export const metadata: Metadata = {
  title: 'Growing Degree Days | SAHOOL',
  description: 'Track growing degree days for optimal crop management and harvest timing',
};

export default function GDDPage() {
  return <GDDClient />;
}
