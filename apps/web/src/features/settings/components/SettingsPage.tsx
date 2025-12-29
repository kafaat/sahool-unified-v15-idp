/**
 * Settings Page Component
 * صفحة الإعدادات
 */

'use client';

import React, { useState } from 'react';
import {
  User,
  Bell,
  Shield,

  Eye,
  Monitor,
  Link as LinkIcon,
  CreditCard,
  Settings as SettingsIcon,
} from 'lucide-react';
import { ProfileForm } from './ProfileForm';
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
  useSecuritySettings,
  useUpdatePassword,
  usePrivacySettings,
  useDisplayPreferences,
  useSubscriptionInfo,
} from '../hooks/useSettings';

type TabType =
  | 'profile'
  | 'notifications'
  | 'security'
  | 'privacy'
  | 'display'
  | 'integrations'
  | 'subscription';

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('profile');

  const tabs = [
    { id: 'profile', label: 'الملف الشخصي', labelEn: 'Profile', icon: User },
    { id: 'notifications', label: 'الإشعارات', labelEn: 'Notifications', icon: Bell },
    { id: 'security', label: 'الأمان', labelEn: 'Security', icon: Shield },
    { id: 'privacy', label: 'الخصوصية', labelEn: 'Privacy', icon: Eye },
    { id: 'display', label: 'العرض', labelEn: 'Display', icon: Monitor },
    { id: 'integrations', label: 'التكاملات', labelEn: 'Integrations', icon: LinkIcon },
    { id: 'subscription', label: 'الاشتراك', labelEn: 'Subscription', icon: CreditCard },
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <SettingsIcon className="w-8 h-8 text-gray-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">الإعدادات</h1>
              <p className="text-sm text-gray-600 mt-1">Settings</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sticky top-4">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as TabType)}
                      className={`
                        w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right transition-colors
                        ${
                          activeTab === tab.id
                            ? 'bg-green-50 text-green-700 font-medium'
                            : 'text-gray-700 hover:bg-gray-50'
                        }
                      `}
                    >
                      <Icon className="w-5 h-5" />
                      <div className="flex-1">
                        <p className="text-sm">{tab.label}</p>
                        <p className="text-xs text-gray-500">{tab.labelEn}</p>
                      </div>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              {activeTab === 'profile' && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    الملف الشخصي
                  </h2>
                  <ProfileForm />
                </div>
              )}

              {activeTab === 'notifications' && (
                <NotificationsTab />
              )}

              {activeTab === 'security' && (
                <SecurityTab />
              )}

              {activeTab === 'privacy' && (
                <PrivacyTab />
              )}

              {activeTab === 'display' && (
                <DisplayTab />
              )}

              {activeTab === 'integrations' && (
                <IntegrationsTab />
              )}

              {activeTab === 'subscription' && (
                <SubscriptionTab />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Notifications Tab
const NotificationsTab: React.FC = () => {
  const { data: prefs, isLoading } = useNotificationPreferences();
  const updatePrefs = useUpdateNotificationPreferences();

  if (isLoading || !prefs) {
    return <div>Loading...</div>;
  }

  const handleUpdate = async (section: keyof typeof prefs, field: string, value: boolean) => {
    const updated = {
      ...prefs,
      [section]: {
        ...prefs[section],
        [field]: value,
      },
    };
    await updatePrefs.mutateAsync(updated);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">إعدادات الإشعارات</h2>
      <div className="space-y-6">
        {/* Email Notifications */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            إشعارات البريد الإلكتروني
          </h3>
          <div className="space-y-3">
            {Object.entries(prefs.email).map(([key, value]) => (
              <label key={key} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <span className="text-sm text-gray-700">{key}</span>
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => handleUpdate('email', key, e.target.checked)}
                  className="w-4 h-4 text-green-600"
                />
              </label>
            ))}
          </div>
        </div>

        {/* Push Notifications */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            إشعارات الدفع
          </h3>
          <div className="space-y-3">
            {Object.entries(prefs.push).map(([key, value]) => (
              <label key={key} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <span className="text-sm text-gray-700">{key}</span>
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => handleUpdate('push', key, e.target.checked)}
                  className="w-4 h-4 text-green-600"
                />
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Security Tab
const SecurityTab: React.FC = () => {
  const { data: security, isLoading } = useSecuritySettings();
  const updatePassword = useUpdatePassword();
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: '',
  });

  if (isLoading || !security) {
    return <div>Loading...</div>;
  }

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) {
      alert('كلمات المرور الجديدة غير متطابقة');
      return;
    }
    try {
      await updatePassword.mutateAsync({
        currentPassword: passwords.current,
        newPassword: passwords.new,
        confirmPassword: passwords.confirm,
      });
      alert('تم تحديث كلمة المرور بنجاح');
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (_err) {
      alert('حدث خطأ أثناء تحديث كلمة المرور');
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">الأمان</h2>
      <div className="space-y-6">
        {/* Change Password */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            تغيير كلمة المرور
          </h3>
          <form onSubmit={handlePasswordUpdate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                كلمة المرور الحالية
              </label>
              <input
                type="password"
                value={passwords.current}
                onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                كلمة المرور الجديدة
              </label>
              <input
                type="password"
                value={passwords.new}
                onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تأكيد كلمة المرور الجديدة
              </label>
              <input
                type="password"
                value={passwords.confirm}
                onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              تحديث كلمة المرور
            </button>
          </form>
        </div>

        {/* Active Sessions */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            الجلسات النشطة
          </h3>
          <div className="space-y-3">
            {security.sessions.map((session) => (
              <div
                key={session.id}
                className="p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{session.device}</p>
                    <p className="text-sm text-gray-600">{session.location}</p>
                    <p className="text-xs text-gray-500">
                      Last active: {new Date(session.lastActive).toLocaleString('ar-SA')}
                    </p>
                  </div>
                  {session.isCurrent ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                      Current
                    </span>
                  ) : (
                    <button className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-xs font-medium">
                      Terminate
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Privacy Tab
const PrivacyTab: React.FC = () => {
  const { data: privacy, isLoading } = usePrivacySettings();
  // const updatePrivacy = useUpdatePrivacySettings();

  if (isLoading || !privacy) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">الخصوصية</h2>
      <p className="text-gray-600">Privacy settings content...</p>
    </div>
  );
};

// Display Tab
const DisplayTab: React.FC = () => {
  const { data: display, isLoading } = useDisplayPreferences();
  // const updateDisplay = useUpdateDisplayPreferences();

  if (isLoading || !display) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">إعدادات العرض</h2>
      <p className="text-gray-600">Display settings content...</p>
    </div>
  );
};

// Integrations Tab
const IntegrationsTab: React.FC = () => {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">التكاملات</h2>
      <p className="text-gray-600">Integrations content...</p>
    </div>
  );
};

// Subscription Tab
const SubscriptionTab: React.FC = () => {
  const { data: subscription, isLoading } = useSubscriptionInfo();

  if (isLoading || !subscription) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">الاشتراك</h2>
      <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-xl border border-gray-200">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">{subscription.planAr}</h3>
            <p className="text-sm text-gray-600 mt-1">{subscription.plan.toUpperCase()} Plan</p>
            <div className="mt-4 space-y-2">
              <p className="text-sm text-gray-700">
                الحقول: {subscription.usage.fields} / {subscription.features.maxFields}
              </p>
              <p className="text-sm text-gray-700">
                أجهزة IoT: {subscription.usage.iotDevices} / {subscription.features.maxIoTDevices}
              </p>
              <p className="text-sm text-gray-700">
                التخزين: {subscription.usage.storage} GB / {subscription.features.maxStorage} GB
              </p>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              subscription.status === 'active'
                ? 'bg-green-100 text-green-700'
                : subscription.status === 'trial'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {subscription.status}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
