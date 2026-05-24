import { Metadata } from 'next';
import SchedulerLogsClient from './SchedulerLogsClient';

export const metadata: Metadata = {
  title: 'سجلات المجدول | Scheduler Logs | SAHOOL',
  description:
    'Monitor daily CDSE satellite data fetch activity, success/failure counts, and index acquisition history.',
};

export default function SchedulerLogsPage() {
  return <SchedulerLogsClient />;
}
