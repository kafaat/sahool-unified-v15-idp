/**
 * Support Page
 * صفحة الدعم الفني
 */

import { Metadata } from 'next';
import SupportClient from './SupportClient';

export const metadata: Metadata = {
  title: 'Support | SAHOOL',
  description: 'Get help and support, submit tickets and view FAQs',
};

export default function SupportPage() {
  return <SupportClient />;
}
