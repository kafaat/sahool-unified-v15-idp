/**
 * Field Details Page
 * صفحة تفاصيل الحقل
 */

import { Metadata } from 'next';
import FieldDetailsClient from './FieldDetailsClient';

export const metadata: Metadata = {
  title: 'Field Details | SAHOOL',
  description: 'View and manage field details, health metrics, and satellite data',
};

interface FieldDetailsPageProps {
  params: Promise<{ id: string }>;
}

export default async function FieldDetailsPage({ params }: FieldDetailsPageProps) {
  const { id } = await params;
  return <FieldDetailsClient fieldId={id} />;
}
