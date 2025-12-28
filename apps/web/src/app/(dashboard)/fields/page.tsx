/**
 * SAHOOL Fields Page
 * صفحة الحقول
 */

import { Metadata } from 'next';
import FieldsClient from './FieldsClient';

export const metadata: Metadata = {
  title: 'Fields Management | SAHOOL',
  description: 'إدارة الحقول - Manage your farm fields, monitor crops, and track field activities',
  keywords: ['fields', 'الحقول', 'farm management', 'crops', 'sahool'],
  openGraph: {
    title: 'Fields Management | SAHOOL',
    description: 'Farm fields management and monitoring',
    type: 'website',
  },
};

export default function FieldsPage() {
  return <FieldsClient />;
}
