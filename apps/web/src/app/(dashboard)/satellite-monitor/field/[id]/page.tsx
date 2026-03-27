/**
 * Field Detail Page
 * صفحة تفاصيل الحقل - مراقبة الأقمار الصناعية
 */

import { Metadata } from 'next';
import FieldDetailClient from './FieldDetailClient';

export const metadata: Metadata = {
  title: 'Field Detail | Satellite Monitoring | SAHOOL',
  description: 'Detailed satellite analysis, AI advisory, and field intelligence',
};

export default async function FieldDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <FieldDetailClient fieldId={id} />;
}
