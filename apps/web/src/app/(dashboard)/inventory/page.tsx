/**
 * Inventory Management Page
 * صفحة إدارة المخزون
 */

import { Metadata } from 'next';
import InventoryClient from './InventoryClient';

export const metadata: Metadata = {
  title: 'Inventory Management | SAHOOL',
  description: 'Manage your farm inventory, supplies, and stock levels',
};

export default function InventoryPage() {
  return <InventoryClient />;
}
