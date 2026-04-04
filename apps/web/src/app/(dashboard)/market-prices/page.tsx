/**
 * SAHOOL Market Prices Page
 * صفحة أسعار السوق
 */

import { Metadata } from 'next';
import MarketPricesClient from '@/features/market-prices/components/MarketPricesClient';

export const metadata: Metadata = {
  title: 'Market Prices | SAHOOL',
  description:
    'أسعار السوق - Track agricultural commodity prices, trends, and market analytics',
  keywords: ['market prices', 'أسعار السوق', 'commodities', 'trends', 'sahool'],
  openGraph: {
    title: 'Market Prices | SAHOOL',
    description: 'Agricultural commodity price tracking and trend analysis',
    type: 'website',
  },
};

export default function MarketPricesPage() {
  return <MarketPricesClient />;
}
