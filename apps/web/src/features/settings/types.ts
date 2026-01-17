/**
 * Settings Feature - Type Definitions
 * تعريفات الأنواع لميزة الإعدادات
 */

// User profile
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  nameAr: string;
  phone?: string;
  avatar?: string;
  bio?: string;
  bioAr?: string;
  location?: {
    city: string;
    cityAr: string;
    region: string;
    regionAr: string;
    country: string;
    countryAr: string;
  };
  farmDetails?: {
    name: string;
    nameAr: string;
    totalArea: number; // hectares
    establishedYear?: number;
    farmType: "individual" | "family" | "company" | "cooperative";
    mainCrops: string[];
    mainCropsAr: string[];
  };
  language: "ar" | "en" | "both";
  timezone: string;
  dateFormat: "gregorian" | "hijri" | "both";
  role: "farmer" | "expert" | "admin" | "manager";
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

// Notification preferences
export interface NotificationPreferences {
  email: {
    enabled: boolean;
    alerts: boolean;
    updates: boolean;
    community: boolean;
    marketing: boolean;
    weeklyReport: boolean;
  };
  push: {
    enabled: boolean;
    alerts: boolean;
    updates: boolean;
    community: boolean;
    tasks: boolean;
    weather: boolean;
  };
  sms: {
    enabled: boolean;
    criticalOnly: boolean;
  };
}

// Security settings
export interface SecuritySettings {
  twoFactorEnabled: boolean;
  twoFactorMethod?: "2fa_app" | "sms" | "email";
  sessions: ActiveSession[];
  lastPasswordChange?: string;
  loginHistory: LoginHistory[];
}

// Active session
export interface ActiveSession {
  id: string;
  device: string;
  browser: string;
  os: string;
  ip: string;
  location?: string;
  lastActive: string;
  isCurrent: boolean;
}

// Login history
export interface LoginHistory {
  id: string;
  timestamp: string;
  device: string;
  browser: string;
  ip: string;
  location?: string;
  success: boolean;
}

// Privacy settings
export interface PrivacySettings {
  profileVisibility: "public" | "community" | "private";
  showEmail: boolean;
  showPhone: boolean;
  showLocation: boolean;
  showFarmDetails: boolean;
  allowMessages: "everyone" | "connections" | "none";
  dataSharing: {
    analytics: boolean;
    research: boolean;
    thirdParty: boolean;
  };
}

// Display preferences
export interface DisplayPreferences {
  theme: "light" | "dark" | "auto";
  language: "ar" | "en";
  rtl: boolean;
  fontSize: "small" | "medium" | "large";
  compactMode: boolean;
  showWeatherWidget: boolean;
  showQuickActions: boolean;
  defaultDashboard: "overview" | "fields" | "tasks" | "analytics";
}

// Integration settings
export interface IntegrationSettings {
  weatherProvider: "openweather" | "weatherapi" | "local";
  mapProvider: "google" | "mapbox" | "osm";
  connectedAccounts: ConnectedAccount[];
}

// Connected account
export interface ConnectedAccount {
  id: string;
  provider: string;
  providerAr: string;
  accountName: string;
  connectedAt: string;
  status: "active" | "expired" | "revoked";
}

// Subscription info
export interface SubscriptionInfo {
  plan: "free" | "basic" | "pro" | "enterprise";
  planAr: string;
  status: "active" | "trial" | "expired" | "cancelled";
  startDate: string;
  endDate?: string;
  autoRenew: boolean;
  features: {
    maxFields: number;
    maxIoTDevices: number;
    maxStorage: number; // GB
    advancedAnalytics: boolean;
    expertConsultation: boolean;
    apiAccess: boolean;
    customReports: boolean;
  };
  usage: {
    fields: number;
    iotDevices: number;
    storage: number; // GB
  };
}

// Settings update payload
export interface UpdateProfilePayload {
  name?: string;
  nameAr?: string;
  phone?: string;
  avatar?: string;
  bio?: string;
  bioAr?: string;
  location?: UserProfile["location"];
  farmDetails?: UserProfile["farmDetails"];
  language?: UserProfile["language"];
  timezone?: UserProfile["timezone"];
  dateFormat?: UserProfile["dateFormat"];
}

export interface UpdatePasswordPayload {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
