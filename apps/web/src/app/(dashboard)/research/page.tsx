/**
 * Research Trials Page
 * صفحة التجارب البحثية
 */

import { Metadata } from 'next';
import ResearchClient from './ResearchClient';

export const metadata: Metadata = {
  title: 'Research Trials | SAHOOL',
  description: 'Manage agricultural research trials and experiments',
};

export default function ResearchPage() {
  return <ResearchClient />;
}
