/**
 * Yield Tracking Page
 * صفحة تتبع المحصول
 */

import { Metadata } from 'next';
import YieldClient from './YieldClient';

export const metadata: Metadata = {
  title: 'Yield | SAHOOL',
  description: 'Track crop yields, view predictions and historical performance',
};

export default function YieldPage() {
  return <YieldClient />;
}
