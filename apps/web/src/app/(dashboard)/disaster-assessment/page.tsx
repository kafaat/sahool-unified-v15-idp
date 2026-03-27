import { Metadata } from 'next';
import DisasterAssessmentClient from './DisasterAssessmentClient';

export const metadata: Metadata = {
  title: 'تقييم الكوارث | SAHOOL',
  description: 'Disaster risk assessment and emergency response management',
};

export default function DisasterAssessmentPage() {
  return <DisasterAssessmentClient />;
}
