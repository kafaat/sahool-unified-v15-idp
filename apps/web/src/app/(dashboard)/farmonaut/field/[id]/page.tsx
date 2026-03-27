/**
 * Farmonaut Field Detail Page
 * صفحة تفاصيل الحقل - فارمونوت
 */

import { Metadata } from 'next';
import FieldDetailClient from './FieldDetailClient';

export const metadata: Metadata = {
  title: 'Field Detail | Farmonaut | SAHOOL',
  description: 'Detailed satellite analysis, JEEVN AI advisory, and field intelligence',
};

export default function FieldDetailPage({ params }: { params: { id: string } }) {
  return <FieldDetailClient fieldId={params.id} />;
}
