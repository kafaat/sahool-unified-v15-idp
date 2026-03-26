import { Metadata } from 'next';
import ComplianceClient from './ComplianceClient';

export const metadata: Metadata = {
  title: 'الامتثال والجودة | SAHOOL',
  description: 'GlobalGAP compliance management and quality certification tracking',
};

export default function CompliancePage() {
  return <ComplianceClient />;
}
