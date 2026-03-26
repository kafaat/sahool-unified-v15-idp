/**
 * SAHOOL Marketplace Page
 * صفحة السوق الزراعي
 */

import { Metadata } from 'next';
import MarketplaceClient from './MarketplaceClient';

export const metadata: Metadata = {
  title: 'Agricultural Marketplace | SAHOOL',
  description: 'السوق الزراعي - Buy and sell agricultural products, equipment, and supplies',
  keywords: ['marketplace', 'السوق', 'agricultural products', 'buy', 'sell', 'sahool'],
  openGraph: {
    title: 'Agricultural Marketplace | SAHOOL',
    description: 'Agricultural marketplace for buying and selling farm products',
    type: 'website',
  },
};

export default function MarketplacePage() {
  return <MarketplaceClient />;
}
