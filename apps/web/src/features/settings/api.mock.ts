/**
 * Settings Feature - Mock Data (Development Fallback)
 * بيانات وهمية للإعدادات
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type {
  UserProfile,
  NotificationPreferences,
  SecuritySettings,
  PrivacySettings,
  DisplayPreferences,
  IntegrationSettings,
  SubscriptionInfo,
} from './types';

export const MOCK_USER_PROFILE: UserProfile = {
  id: 'user-1',
  email: 'farmer@sahool.sa',
  name: 'Ahmed Al-Qarni',
  nameAr: 'أحمد القرني',
  phone: '+966501234567',
  avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=Ahmed',
  bio: 'Experienced farmer specializing in sustainable agriculture',
  bioAr: 'مزارع ذو خبرة متخصص في الزراعة المستدامة',
  location: {
    city: 'Riyadh',
    cityAr: 'الرياض',
    region: 'Central Region',
    regionAr: 'المنطقة الوسطى',
    country: 'Saudi Arabia',
    countryAr: 'المملكة العربية السعودية',
  },
  farmDetails: {
    name: 'Al-Qarni Farm',
    nameAr: 'مزرعة القرني',
    totalArea: 50.5,
    establishedYear: 2010,
    farmType: 'family',
    mainCrops: ['Wheat', 'Barley', 'Dates'],
    mainCropsAr: ['قمح', 'شعير', 'تمور'],
  },
  language: 'both',
  timezone: 'Asia/Riyadh',
  dateFormat: 'both',
  role: 'farmer',
  isVerified: true,
  createdAt: '2023-01-15T10:00:00Z',
  updatedAt: new Date().toISOString(),
};

export const MOCK_NOTIFICATION_PREFERENCES: NotificationPreferences = {
  email: {
    enabled: true,
    alerts: true,
    updates: true,
    community: false,
    marketing: false,
    weeklyReport: true,
  },
  push: {
    enabled: true,
    alerts: true,
    updates: true,
    community: true,
    tasks: true,
    weather: true,
  },
  sms: {
    enabled: false,
    criticalOnly: true,
  },
};

export const MOCK_SECURITY_SETTINGS: SecuritySettings = {
  twoFactorEnabled: false,
  twoFactorMethod: undefined,
  sessions: [
    {
      id: 'session-1',
      device: 'Desktop',
      browser: 'Chrome 120',
      os: 'Windows 11',
      ip: '192.168.1.100',
      location: 'Riyadh, SA',
      lastActive: new Date().toISOString(),
      isCurrent: true,
    },
    {
      id: 'session-2',
      device: 'Mobile',
      browser: 'Safari 17',
      os: 'iOS 17',
      ip: '192.168.1.105',
      location: 'Riyadh, SA',
      lastActive: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      isCurrent: false,
    },
  ],
  lastPasswordChange: '2023-11-01T10:00:00Z',
  loginHistory: [
    {
      id: 'login-1',
      timestamp: new Date().toISOString(),
      device: 'Desktop',
      browser: 'Chrome 120',
      ip: '192.168.1.100',
      location: 'Riyadh, SA',
      success: true,
    },
    {
      id: 'login-2',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      device: 'Mobile',
      browser: 'Safari 17',
      ip: '192.168.1.105',
      location: 'Riyadh, SA',
      success: true,
    },
  ],
};

export const MOCK_PRIVACY_SETTINGS: PrivacySettings = {
  profileVisibility: 'community',
  showEmail: false,
  showPhone: false,
  showLocation: true,
  showFarmDetails: true,
  allowMessages: 'connections',
  dataSharing: {
    analytics: true,
    research: false,
    thirdParty: false,
  },
};

export const MOCK_DISPLAY_PREFERENCES: DisplayPreferences = {
  theme: 'auto',
  language: 'ar',
  rtl: true,
  fontSize: 'medium',
  compactMode: false,
  showWeatherWidget: true,
  showQuickActions: true,
  defaultDashboard: 'overview',
};

export const MOCK_INTEGRATION_SETTINGS: IntegrationSettings = {
  weatherProvider: 'openweather',
  mapProvider: 'google',
  connectedAccounts: [
    {
      id: 'acc-1',
      provider: 'Google',
      providerAr: 'جوجل',
      accountName: 'farmer@gmail.com',
      connectedAt: '2023-06-15T10:00:00Z',
      status: 'active',
    },
  ],
};

export const MOCK_SUBSCRIPTION_INFO: SubscriptionInfo = {
  plan: 'pro',
  planAr: 'احترافي',
  status: 'active',
  startDate: '2024-01-01T00:00:00Z',
  endDate: '2024-12-31T23:59:59Z',
  autoRenew: true,
  features: {
    maxFields: 50,
    maxIoTDevices: 20,
    maxStorage: 100,
    advancedAnalytics: true,
    expertConsultation: true,
    apiAccess: true,
    customReports: true,
  },
  usage: {
    fields: 12,
    iotDevices: 5,
    storage: 23.5,
  },
};
