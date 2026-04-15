/**
 * Session Management Page for Admin Dashboard
 * Allows administrators to view and manage active sessions
 *
 * صفحة إدارة الجلسات - للمشرفين لعرض وإدارة الجلسات النشطة
 */

'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/components/ui/Toast';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';

interface Session {
  id: string;
  userId: string;
  userEmail: string;
  ipAddress: string;
  userAgent: string;
  createdAt: string;
  lastActivity: string;
  expiresAt: string;
  isCurrent: boolean;
  location?: {
    city?: string;
    country?: string;
  };
}

export default function SessionManagementPage() {
  const { toast } = useToast();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // The page supports Arabic/English toggling via the locale button in the header.
  const [locale, setLocale] = useState<'en' | 'ar'>('ar');

  useEffect(() => {
    fetchSessions();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/admin/sessions');
      if (!response.ok) throw new Error('Failed to fetch sessions');

      const data = await response.json();
      setSessions(data.sessions || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const revokeSession = async (sessionId: string) => {
    if (
      !confirm(
        locale === 'ar'
          ? 'هل أنت متأكد من إلغاء هذه الجلسة؟'
          : 'Are you sure you want to revoke this session?'
      )
    ) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to revoke session');

      // Refresh sessions list
      await fetchSessions();
    } catch {
      toast.error('Failed to revoke session', 'فشل إلغاء الجلسة');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return format(date, 'PPp', { locale: locale === 'ar' ? ar : undefined });
  };

  const getBrowserName = (userAgent: string): string => {
    if (userAgent.includes('Chrome')) return 'Chrome';
    if (userAgent.includes('Firefox')) return 'Firefox';
    if (userAgent.includes('Safari')) return 'Safari';
    if (userAgent.includes('Edge')) return 'Edge';
    return 'Unknown';
  };

  const getDeviceType = (userAgent: string): string => {
    if (userAgent.includes('Mobile')) return '📱 Mobile';
    if (userAgent.includes('Tablet')) return '📱 Tablet';
    return '💻 Desktop';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{locale === 'ar' ? 'جارٍ التحميل...' : 'Loading...'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {locale === 'ar' ? 'إدارة الجلسات' : 'Session Management'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {locale === 'ar'
              ? 'عرض وإدارة الجلسات النشطة لجميع المستخدمين'
              : 'View and manage active sessions for all users'}
          </p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => setLocale(locale === 'en' ? 'ar' : 'en')}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
          >
            {locale === 'en' ? '🇸🇦 العربية' : '🇬🇧 English'}
          </button>

          <button
            onClick={fetchSessions}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            {locale === 'ar' ? '🔄 تحديث' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {locale === 'ar' ? 'إجمالي الجلسات' : 'Total Sessions'}
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
            {sessions.length}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {locale === 'ar' ? 'المستخدمون النشطون' : 'Active Users'}
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
            {new Set(sessions.map((s) => s.userId)).size}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {locale === 'ar' ? 'الجلسة الحالية' : 'Current Session'}
          </div>
          <div className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
            ✓ {locale === 'ar' ? 'نشطة' : 'Active'}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Sessions Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {locale === 'ar' ? 'المستخدم' : 'User'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {locale === 'ar' ? 'الجهاز' : 'Device'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {locale === 'ar' ? 'عنوان IP' : 'IP Address'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {locale === 'ar' ? 'النشاط الأخير' : 'Last Activity'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {locale === 'ar' ? 'إجراءات' : 'Actions'}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {sessions.map((session) => (
                <tr
                  key={session.id}
                  className={session.isCurrent ? 'bg-green-50 dark:bg-green-900/10' : ''}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {session.userEmail}
                    </div>
                    {session.isCurrent && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300">
                        {locale === 'ar' ? 'الجلسة الحالية' : 'Current Session'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      {getDeviceType(session.userAgent)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {getBrowserName(session.userAgent)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">{session.ipAddress}</div>
                    {session.location && (
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {session.location.city}, {session.location.country}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      {formatDate(session.lastActivity)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {!session.isCurrent && (
                      <button
                        onClick={() => revokeSession(session.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                      >
                        {locale === 'ar' ? '🚫 إلغاء' : '🚫 Revoke'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {sessions.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              {locale === 'ar' ? 'لا توجد جلسات نشطة' : 'No active sessions'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
