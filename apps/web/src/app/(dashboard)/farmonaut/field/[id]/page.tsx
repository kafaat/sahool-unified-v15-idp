/**
 * Field Detail Page
 * صفحة تفاصيل الحقل - مراقبة الأقمار الصناعية
 */

import { Metadata } from 'next';
import FieldDetailClient from './FieldDetailClient';

export const metadata: Metadata = {
  title: 'Field Detail | Satellite Monitoring | SAHOOL',
  description: 'Detailed satellite analysis, JEEVN AI advisory, and field intelligence',
};

export default function FieldDetailPage({ params }: { params: { id: string } }) {
  return <FieldDetailClient fieldId={params.id} />;
}
