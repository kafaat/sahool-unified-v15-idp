/**
 * Field Scouting Page
 * صفحة الاستكشاف الميداني
 */

import { Metadata } from 'next';
import ScoutingClient from './ScoutingClient';

export const metadata: Metadata = {
  title: 'Field Scouting | SAHOOL',
  description: 'الاستكشاف الميداني - Field scouting reports, observations, and issue tracking',
};

export default function ScoutingPage() {
  return <ScoutingClient />;
}
