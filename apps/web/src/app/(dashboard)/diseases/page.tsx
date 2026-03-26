/**
 * Diseases Management Page
 * صفحة إدارة الأمراض
 */

import { Metadata } from 'next';
import DiseasesClient from './DiseasesClient';

export const metadata: Metadata = {
  title: 'Diseases | SAHOOL',
  description: 'Track and manage crop diseases, get diagnosis and treatment recommendations',
};

export default function DiseasesPage() {
  return <DiseasesClient />;
}
