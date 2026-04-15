/**
 * SAHOOL Traceability Page
 * صفحة تتبع سلسلة التوريد
 */

import { Metadata } from 'next';
import TraceabilityClient from '@/features/traceability/components/TraceabilityClient';

export const metadata: Metadata = {
  title: 'Supply Chain Traceability | SAHOOL',
  description:
    'تتبع سلسلة التوريد - Track products from farm to table with QR codes and event timeline',
  keywords: ['traceability', 'تتبع', 'supply chain', 'سلسلة التوريد', 'QR', 'sahool'],
  openGraph: {
    title: 'Supply Chain Traceability | SAHOOL',
    description: 'Farm-to-table supply chain tracking and QR code management',
    type: 'website',
  },
};

export default function TraceabilityPage() {
  return <TraceabilityClient />;
}
