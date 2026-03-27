/**
 * Variable Rate Application (VRA) Page
 * صفحة التطبيق المتغير
 */

import { Metadata } from 'next';
import VRAClient from './VRAClient';

export const metadata: Metadata = {
  title: 'Variable Rate Application | SAHOOL',
  description: 'Manage variable rate application maps for precision fertilization and seeding',
};

export default function VRAPage() {
  return <VRAClient />;
}
