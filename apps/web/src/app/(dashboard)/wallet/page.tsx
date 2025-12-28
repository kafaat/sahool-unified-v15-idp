/**
 * SAHOOL Wallet Page
 * صفحة المحفظة
 */

import { Metadata } from 'next';
import WalletClient from './WalletClient';

export const metadata: Metadata = {
  title: 'Wallet & Payments | SAHOOL',
  description: 'المحفظة والمدفوعات - Manage your wallet, transactions, transfers, and payments',
  keywords: ['wallet', 'محفظة', 'payments', 'transactions', 'transfers', 'sahool'],
  openGraph: {
    title: 'Wallet & Payments | SAHOOL',
    description: 'Digital wallet and payment management',
    type: 'website',
  },
};

export default function WalletPage() {
  return <WalletClient />;
}
