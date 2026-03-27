/**
 * Farmonaut Add Field Page
 * صفحة إضافة حقل جديد - فارمونوت
 */

import { Metadata } from 'next';
import AddFieldClient from './AddFieldClient';

export const metadata: Metadata = {
  title: 'Add Field | Satellite Monitoring | SAHOOL',
  description: 'Add a new field for satellite monitoring',
};

export default function AddFieldPage() {
  return <AddFieldClient />;
}
