/**
 * Season Management Page
 * صفحة إدارة المواسم
 */

import { Metadata } from 'next';
import SeasonsClient from './SeasonsClient';

export const metadata: Metadata = {
  title: 'Season Management | SAHOOL',
  description: 'إدارة المواسم - Plan agricultural seasons, track progress and yields',
  keywords: ['seasons', 'المواسم', 'planning', 'تخطيط', 'yield', 'إنتاج', 'sahool'],
};

export default function SeasonsPage() {
  return <SeasonsClient />;
}
