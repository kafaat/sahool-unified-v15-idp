/**
 * Seed Catalog Page
 * صفحة كتالوج البذور
 */

import { Metadata } from 'next';
import SeedsClient from '@/features/seeds/components/SeedsClient';

export const metadata: Metadata = {
  title: 'Seed Catalog | SAHOOL',
  description: 'Browse seed varieties, view recommendations, and manage seed inventory',
};

export default function SeedsPage() {
  return <SeedsClient />;
}
