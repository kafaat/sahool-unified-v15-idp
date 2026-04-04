/**
 * SAHOOL Cooperatives Management Page
 * صفحة إدارة التعاونيات
 */

import { Metadata } from 'next';
import CooperativesClient from '@/features/cooperatives/components/CooperativesClient';

export const metadata: Metadata = {
  title: 'Cooperatives Management | SAHOOL',
  description:
    'إدارة التعاونيات - Manage agricultural cooperatives, members, and shared resources',
  keywords: ['cooperatives', 'التعاونيات', 'members', 'أعضاء', 'shared resources', 'sahool'],
  openGraph: {
    title: 'Cooperatives Management | SAHOOL',
    description: 'Agricultural cooperative management and resource sharing',
    type: 'website',
  },
};

export default function CooperativesPage() {
  return <CooperativesClient />;
}
