import { Metadata } from 'next';
import LogisticsClient from './LogisticsClient';

export const metadata: Metadata = {
  title: 'إدارة اللوجستيات | SAHOOL',
  description: 'Manage farm logistics, transportation, and delivery tracking',
};

export default function LogisticsPage() {
  return <LogisticsClient />;
}
