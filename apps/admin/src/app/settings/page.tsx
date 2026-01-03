'use client';

// Settings Page - Admin Dashboard
// صفحة الإعدادات - لوحة تحكم المدير

import { useState, useEffect } from 'react';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { cn } from '@/lib/utils';
import { logger } from '../../lib/logger';
import {
  User,
  Lock,
  Bell,
  Globe,
  Settings as SettingsIcon,
  Users,
  Shield,
  Database,
  Flag,
  Save,
  Eye,
  EyeOff,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Trash2,
  Edit,
  Plus,
  Check,
  X,
} from 'lucide-react';

// Mock admin users data
const mockAdmins = [
  {
    id: '1',
    name: 'محمد أحمد',
    nameEn: 'Mohammed Ahmed',
    email: 'mohammed@sahool.io',
    role: 'مدير النظام',
    roleEn: 'System Admin',
    status: 'active',
    lastLogin: '2025-12-24T10:30:00',
  },
  {
    id: '2',
    name: 'فاطمة سعيد',
    nameEn: 'Fatima Said',
    email: 'fatima@sahool.io',
    role: 'مشرف',
    roleEn: 'Supervisor',
    status: 'active',
    lastLogin: '2025-12-24T09:15:00',
  },
  {
    id: '3',
    name: 'علي حسن',
    nameEn: 'Ali Hassan',
    email: 'ali@sahool.io',
    role: 'مدقق',
    roleEn: 'Reviewer',
    status: 'inactive',
    lastLogin: '2025-12-20T14:20:00',
  },
];

export default function SettingsPage() {
  // Profile state
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [profileData, setProfileData] = useState({
    name: 'محمد أحمد',
    nameEn: 'Mohammed Ahmed',
    email: 'admin@sahool.io',
    phone: '+967 777 123 456',
    location: 'صنعاء، اليمن',
  });
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // User preferences state
  const [preferences, setPreferences] = useState({
    language: 'ar',
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    weeklyReports: true,
    criticalAlerts: true,
  });

  // System settings state
  const [systemSettings, setSystemSettings] = useState({
    apiEndpoint: 'https://api.sahool.io/v1',
    maxUploadSize: '10',
    sessionTimeout: '30',
    enableAnalytics: true,
    enableDiagnostics: true,
    maintenanceMode: false,
    autoBackup: true,
    backupFrequency: 'daily',
  });

  // Feature flags state
  const [featureFlags, setFeatureFlags] = useState({
    newDashboard: true,
    aiDiagnosis: true,
    weatherPrediction: false,
    cropRecommendation: true,
    marketPricing: false,
    satelliteImagery: true,
  });

  // Admins state
  const [admins, setAdmins] = useState(mockAdmins);
  const [selectedTab, setSelectedTab] = useState<'profile' | 'preferences' | 'system' | 'users'>('profile');

  // Save handlers
  const handleSaveProfile = () => {
    logger.log('Saving profile:', profileData);
    alert('تم حفظ الملف الشخصي بنجاح');
  };

  const handleSavePassword = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('كلمة المرور الجديدة وتأكيد كلمة المرور غير متطابقين');
      return;
    }
    logger.log('Changing password');
    alert('تم تغيير كلمة المرور بنجاح');
    setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
  };

  const handleSavePreferences = () => {
    logger.log('Saving preferences:', preferences);
    alert('تم حفظ التفضيلات بنجاح');
  };

  const handleSaveSystemSettings = () => {
    logger.log('Saving system settings:', systemSettings);
    alert('تم حفظ إعدادات النظام بنجاح');
  };

  // Admin table columns
  const adminColumns = [
    {
      key: 'name',
      header: 'الاسم',
      render: (admin: typeof mockAdmins[0]) => (
        <div>
          <p className="font-medium text-gray-900">{admin.name}</p>
          <p className="text-xs text-gray-500">{admin.nameEn}</p>
        </div>
      ),
    },
    {
      key: 'email',
      header: 'البريد الإلكتروني',
      render: (admin: typeof mockAdmins[0]) => (
        <span className="text-gray-700">{admin.email}</span>
      ),
    },
    {
      key: 'role',
      header: 'الدور',
      render: (admin: typeof mockAdmins[0]) => (
        <div>
          <p className="font-medium text-gray-900">{admin.role}</p>
          <p className="text-xs text-gray-500">{admin.roleEn}</p>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (admin: typeof mockAdmins[0]) => (
        <span
          className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            admin.status === 'active'
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-100 text-gray-700'
          )}
        >
          {admin.status === 'active' ? 'نشط' : 'غير نشط'}
        </span>
      ),
    },
    {
      key: 'lastLogin',
      header: 'آخر تسجيل دخول',
      render: (admin: typeof mockAdmins[0]) => (
        <span className="text-sm text-gray-600">
          {new Date(admin.lastLogin).toLocaleDateString('ar-EG', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          })}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'الإجراءات',
      render: (admin: typeof mockAdmins[0]) => (
        <div className="flex items-center gap-2">
          <button className="p-1 hover:bg-gray-100 rounded transition-colors">
            <Edit className="w-4 h-4 text-blue-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded transition-colors">
            <Trash2 className="w-4 h-4 text-red-600" />
          </button>
        </div>
      ),
      className: 'w-24',
    },
  ];

  return (
    <div className="p-6">
      <Header title="الإعدادات" subtitle="إدارة إعدادات النظام والحساب" />

      {/* Tabs Navigation */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-1">
        <div className="flex gap-1">
          <button
            onClick={() => setSelectedTab('profile')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all',
              selectedTab === 'profile'
                ? 'bg-sahool-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <User className="w-5 h-5" />
            الملف الشخصي
          </button>
          <button
            onClick={() => setSelectedTab('preferences')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all',
              selectedTab === 'preferences'
                ? 'bg-sahool-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <SettingsIcon className="w-5 h-5" />
            التفضيلات
          </button>
          <button
            onClick={() => setSelectedTab('system')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all',
              selectedTab === 'system'
                ? 'bg-sahool-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <Database className="w-5 h-5" />
            إعدادات النظام
          </button>
          <button
            onClick={() => setSelectedTab('users')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all',
              selectedTab === 'users'
                ? 'bg-sahool-600 text-white'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <Users className="w-5 h-5" />
            إدارة المستخدمين
          </button>
        </div>
      </div>

      {/* Profile Tab */}
      {selectedTab === 'profile' && (
        <div className="mt-6 space-y-6">
          {/* Profile Information Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-sahool-100 rounded-lg">
                <User className="w-5 h-5 text-sahool-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">المعلومات الشخصية</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  الاسم بالعربية
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={profileData.name}
                    onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Name in English
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={profileData.nameEn}
                    onChange={(e) => setProfileData({ ...profileData, nameEn: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  البريد الإلكتروني
                </label>
                <div className="relative">
                  <input
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  رقم الهاتف
                </label>
                <div className="relative">
                  <input
                    type="tel"
                    value={profileData.phone}
                    onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  الموقع
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={profileData.location}
                    onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={handleSaveProfile}
                className="flex items-center gap-2 px-6 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
              >
                <Save className="w-4 h-4" />
                حفظ التغييرات
              </button>
            </div>
          </div>

          {/* Change Password Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-red-100 rounded-lg">
                <Lock className="w-5 h-5 text-red-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">تغيير كلمة المرور</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  كلمة المرور القديمة
                </label>
                <div className="relative">
                  <input
                    type={showOldPassword ? 'text' : 'password'}
                    value={passwordData.oldPassword}
                    onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
                    className="w-full pl-10 pr-10 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <button
                    type="button"
                    onClick={() => setShowOldPassword(!showOldPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    {showOldPassword ? (
                      <EyeOff className="w-4 h-4 text-gray-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  كلمة المرور الجديدة
                </label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={passwordData.newPassword}
                    onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                    className="w-full pl-10 pr-10 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    {showNewPassword ? (
                      <EyeOff className="w-4 h-4 text-gray-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  تأكيد كلمة المرور
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={passwordData.confirmPassword}
                    onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                    className="w-full pl-10 pr-10 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-4 h-4 text-gray-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={handleSavePassword}
                className="flex items-center gap-2 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Lock className="w-4 h-4" />
                تغيير كلمة المرور
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preferences Tab */}
      {selectedTab === 'preferences' && (
        <div className="mt-6 space-y-6">
          {/* Language & Display Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Globe className="w-5 h-5 text-blue-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">اللغة والعرض</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  اللغة الافتراضية
                </label>
                <select
                  value={preferences.language}
                  onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                >
                  <option value="ar">العربية</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Bell className="w-5 h-5 text-yellow-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">الإشعارات</h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">إشعارات البريد الإلكتروني</p>
                    <p className="text-sm text-gray-500">تلقي التحديثات عبر البريد الإلكتروني</p>
                  </div>
                </div>
                <button
                  onClick={() => setPreferences({ ...preferences, emailNotifications: !preferences.emailNotifications })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    preferences.emailNotifications ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      preferences.emailNotifications ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">إشعارات الرسائل القصيرة</p>
                    <p className="text-sm text-gray-500">تلقي التنبيهات عبر الرسائل النصية</p>
                  </div>
                </div>
                <button
                  onClick={() => setPreferences({ ...preferences, smsNotifications: !preferences.smsNotifications })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    preferences.smsNotifications ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      preferences.smsNotifications ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">الإشعارات الفورية</p>
                    <p className="text-sm text-gray-500">تلقي الإشعارات الفورية في المتصفح</p>
                  </div>
                </div>
                <button
                  onClick={() => setPreferences({ ...preferences, pushNotifications: !preferences.pushNotifications })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    preferences.pushNotifications ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      preferences.pushNotifications ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">التقارير الأسبوعية</p>
                    <p className="text-sm text-gray-500">استلام ملخص أسبوعي للنشاطات</p>
                  </div>
                </div>
                <button
                  onClick={() => setPreferences({ ...preferences, weeklyReports: !preferences.weeklyReports })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    preferences.weeklyReports ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      preferences.weeklyReports ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-red-600" />
                  <div>
                    <p className="font-medium text-gray-900">التنبيهات الحرجة</p>
                    <p className="text-sm text-gray-500">تنبيهات فورية للمشاكل الحرجة (موصى به)</p>
                  </div>
                </div>
                <button
                  onClick={() => setPreferences({ ...preferences, criticalAlerts: !preferences.criticalAlerts })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    preferences.criticalAlerts ? 'bg-red-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      preferences.criticalAlerts ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={handleSavePreferences}
                className="flex items-center gap-2 px-6 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
              >
                <Save className="w-4 h-4" />
                حفظ التفضيلات
              </button>
            </div>
          </div>
        </div>
      )}

      {/* System Settings Tab */}
      {selectedTab === 'system' && (
        <div className="mt-6 space-y-6">
          {/* API Configuration Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Database className="w-5 h-5 text-purple-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">إعدادات API</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  نقطة نهاية API الرئيسية
                </label>
                <input
                  type="text"
                  value={systemSettings.apiEndpoint}
                  onChange={(e) => setSystemSettings({ ...systemSettings, apiEndpoint: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 font-mono text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  الحد الأقصى لحجم التحميل (MB)
                </label>
                <input
                  type="number"
                  value={systemSettings.maxUploadSize}
                  onChange={(e) => setSystemSettings({ ...systemSettings, maxUploadSize: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  مهلة الجلسة (دقيقة)
                </label>
                <input
                  type="number"
                  value={systemSettings.sessionTimeout}
                  onChange={(e) => setSystemSettings({ ...systemSettings, sessionTimeout: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  تكرار النسخ الاحتياطي
                </label>
                <select
                  value={systemSettings.backupFrequency}
                  onChange={(e) => setSystemSettings({ ...systemSettings, backupFrequency: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                >
                  <option value="hourly">كل ساعة</option>
                  <option value="daily">يومي</option>
                  <option value="weekly">أسبوعي</option>
                  <option value="monthly">شهري</option>
                </select>
              </div>
            </div>
          </div>

          {/* System Options Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-green-100 rounded-lg">
                <SettingsIcon className="w-5 h-5 text-green-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">خيارات النظام</h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">تفعيل التحليلات</p>
                    <p className="text-sm text-gray-500">تتبع استخدام المنصة والإحصائيات</p>
                  </div>
                </div>
                <button
                  onClick={() => setSystemSettings({ ...systemSettings, enableAnalytics: !systemSettings.enableAnalytics })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    systemSettings.enableAnalytics ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      systemSettings.enableAnalytics ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">تفعيل التشخيصات</p>
                    <p className="text-sm text-gray-500">جمع بيانات الأخطاء وتقارير الأداء</p>
                  </div>
                </div>
                <button
                  onClick={() => setSystemSettings({ ...systemSettings, enableDiagnostics: !systemSettings.enableDiagnostics })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    systemSettings.enableDiagnostics ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      systemSettings.enableDiagnostics ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">النسخ الاحتياطي التلقائي</p>
                    <p className="text-sm text-gray-500">نسخ البيانات تلقائياً حسب الجدول المحدد</p>
                  </div>
                </div>
                <button
                  onClick={() => setSystemSettings({ ...systemSettings, autoBackup: !systemSettings.autoBackup })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    systemSettings.autoBackup ? 'bg-blue-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      systemSettings.autoBackup ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-center gap-3">
                  <X className="w-5 h-5 text-yellow-600" />
                  <div>
                    <p className="font-medium text-gray-900">وضع الصيانة</p>
                    <p className="text-sm text-gray-500">تعطيل الوصول مؤقتاً للصيانة</p>
                  </div>
                </div>
                <button
                  onClick={() => setSystemSettings({ ...systemSettings, maintenanceMode: !systemSettings.maintenanceMode })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    systemSettings.maintenanceMode ? 'bg-yellow-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      systemSettings.maintenanceMode ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Feature Flags Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Flag className="w-5 h-5 text-indigo-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">المميزات التجريبية</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">لوحة التحكم الجديدة</p>
                  <p className="text-xs text-gray-500">تصميم محدث مع ميزات إضافية</p>
                </div>
                <button
                  onClick={() => setFeatureFlags({ ...featureFlags, newDashboard: !featureFlags.newDashboard })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    featureFlags.newDashboard ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      featureFlags.newDashboard ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">التشخيص بالذكاء الاصطناعي</p>
                  <p className="text-xs text-gray-500">تحسين دقة التشخيص</p>
                </div>
                <button
                  onClick={() => setFeatureFlags({ ...featureFlags, aiDiagnosis: !featureFlags.aiDiagnosis })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    featureFlags.aiDiagnosis ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      featureFlags.aiDiagnosis ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">توقعات الطقس المتقدمة</p>
                  <p className="text-xs text-gray-500">تنبؤات دقيقة للطقس</p>
                </div>
                <button
                  onClick={() => setFeatureFlags({ ...featureFlags, weatherPrediction: !featureFlags.weatherPrediction })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    featureFlags.weatherPrediction ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      featureFlags.weatherPrediction ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">توصيات المحاصيل</p>
                  <p className="text-xs text-gray-500">اقتراحات ذكية للزراعة</p>
                </div>
                <button
                  onClick={() => setFeatureFlags({ ...featureFlags, cropRecommendation: !featureFlags.cropRecommendation })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    featureFlags.cropRecommendation ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      featureFlags.cropRecommendation ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">أسعار السوق</p>
                  <p className="text-xs text-gray-500">تتبع أسعار المحاصيل</p>
                </div>
                <button
                  onClick={() => setFeatureFlags({ ...featureFlags, marketPricing: !featureFlags.marketPricing })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    featureFlags.marketPricing ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      featureFlags.marketPricing ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">الصور الفضائية</p>
                  <p className="text-xs text-gray-500">تحليل بيانات الأقمار الصناعية</p>
                </div>
                <button
                  onClick={() => setFeatureFlags({ ...featureFlags, satelliteImagery: !featureFlags.satelliteImagery })}
                  className={cn(
                    'relative w-12 h-6 rounded-full transition-colors',
                    featureFlags.satelliteImagery ? 'bg-sahool-600' : 'bg-gray-300'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                      featureFlags.satelliteImagery ? 'right-0.5' : 'right-6'
                    )}
                  />
                </button>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleSaveSystemSettings}
              className="flex items-center gap-2 px-6 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
            >
              <Save className="w-4 h-4" />
              حفظ إعدادات النظام
            </button>
          </div>
        </div>
      )}

      {/* Users Management Tab */}
      {selectedTab === 'users' && (
        <div className="mt-6 space-y-6">
          {/* Admin Users Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-cyan-100 rounded-lg">
                  <Users className="w-5 h-5 text-cyan-700" />
                </div>
                <h2 className="text-lg font-bold text-gray-900">المستخدمين الإداريين</h2>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors">
                <Plus className="w-4 h-4" />
                إضافة مستخدم
              </button>
            </div>

            <DataTable
              columns={adminColumns}
              data={admins}
              keyExtractor={(admin) => admin.id}
              emptyMessage="لا يوجد مستخدمين إداريين"
            />
          </div>

          {/* Roles & Permissions Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Shield className="w-5 h-5 text-orange-700" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">الأدوار والصلاحيات</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border-2 border-sahool-200 rounded-lg bg-sahool-50">
                <div className="flex items-center gap-2 mb-3">
                  <Shield className="w-5 h-5 text-sahool-700" />
                  <h3 className="font-bold text-gray-900">مدير النظام</h3>
                </div>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-sahool-600" />
                    صلاحيات كاملة
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-sahool-600" />
                    إدارة المستخدمين
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-sahool-600" />
                    تعديل الإعدادات
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-sahool-600" />
                    عرض التقارير
                  </li>
                </ul>
                <div className="mt-4 pt-4 border-t border-sahool-200">
                  <p className="text-xs text-gray-500">عدد المستخدمين: 1</p>
                </div>
              </div>

              <div className="p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
                <div className="flex items-center gap-2 mb-3">
                  <Eye className="w-5 h-5 text-blue-700" />
                  <h3 className="font-bold text-gray-900">مشرف</h3>
                </div>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-blue-600" />
                    إدارة المزارع
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-blue-600" />
                    إدارة التشخيصات
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-blue-600" />
                    عرض التقارير
                  </li>
                  <li className="flex items-center gap-2">
                    <X className="w-4 h-4 text-gray-400" />
                    تعديل الإعدادات
                  </li>
                </ul>
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <p className="text-xs text-gray-500">عدد المستخدمين: 1</p>
                </div>
              </div>

              <div className="p-4 border-2 border-gray-200 rounded-lg bg-gray-50">
                <div className="flex items-center gap-2 mb-3">
                  <Eye className="w-5 h-5 text-gray-700" />
                  <h3 className="font-bold text-gray-900">مدقق</h3>
                </div>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-gray-600" />
                    عرض المزارع
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-gray-600" />
                    عرض التشخيصات
                  </li>
                  <li className="flex items-center gap-2">
                    <X className="w-4 h-4 text-gray-400" />
                    التعديل
                  </li>
                  <li className="flex items-center gap-2">
                    <X className="w-4 h-4 text-gray-400" />
                    الحذف
                  </li>
                </ul>
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500">عدد المستخدمين: 1</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
