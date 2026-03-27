/**
 * Documents Page
 * صفحة الوثائق
 */

import { Metadata } from 'next';
import DocumentsClient from './DocumentsClient';

export const metadata: Metadata = {
  title: 'Documents | SAHOOL',
  description: 'الوثائق - Manage farm documents, licenses, and compliance records',
  keywords: ['documents', 'الوثائق', 'compliance', 'الامتثال', 'sahool'],
};

export default function DocumentsPage() {
  return <DocumentsClient />;
}
