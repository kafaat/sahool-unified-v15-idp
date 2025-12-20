/**
 * SAHOOL Admin Internationalization (i18n)
 * نظام التدويل للوحة الإدارة
 *
 * Features:
 * - Arabic (RTL) and English support
 * - Type-safe translations
 * - Pluralization
 * - Number and date formatting
 * - Dynamic locale switching
 */

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export type Locale = 'ar' | 'en';

export type TranslationKey = keyof typeof translations.ar;

export interface I18nConfig {
  defaultLocale: Locale;
  fallbackLocale: Locale;
  rtlLocales: Locale[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Translations
// ═══════════════════════════════════════════════════════════════════════════

export const translations = {
  ar: {
    // Common
    'common.loading': 'جاري التحميل...',
    'common.error': 'حدث خطأ',
    'common.retry': 'إعادة المحاولة',
    'common.save': 'حفظ',
    'common.cancel': 'إلغاء',
    'common.delete': 'حذف',
    'common.edit': 'تعديل',
    'common.add': 'إضافة',
    'common.search': 'بحث',
    'common.filter': 'تصفية',
    'common.export': 'تصدير',
    'common.import': 'استيراد',
    'common.refresh': 'تحديث',
    'common.close': 'إغلاق',
    'common.confirm': 'تأكيد',
    'common.back': 'رجوع',
    'common.next': 'التالي',
    'common.previous': 'السابق',
    'common.yes': 'نعم',
    'common.no': 'لا',
    'common.all': 'الكل',
    'common.none': 'لا شيء',
    'common.select': 'اختر',
    'common.noData': 'لا توجد بيانات',
    'common.noResults': 'لا توجد نتائج',

    // Navigation
    'nav.dashboard': 'لوحة التحكم',
    'nav.farms': 'المزارع',
    'nav.fields': 'الحقول',
    'nav.diseases': 'التشخيص',
    'nav.alerts': 'التنبيهات',
    'nav.irrigation': 'الري',
    'nav.sensors': 'الحساسات',
    'nav.yield': 'توقع الإنتاج',
    'nav.epidemic': 'الأوبئة',
    'nav.lab': 'المختبر',
    'nav.support': 'الدعم',
    'nav.settings': 'الإعدادات',
    'nav.users': 'المستخدمين',
    'nav.reports': 'التقارير',
    'nav.logout': 'تسجيل الخروج',

    // Dashboard
    'dashboard.title': 'لوحة التحكم',
    'dashboard.welcome': 'مرحباً',
    'dashboard.overview': 'نظرة عامة',
    'dashboard.stats.farms': 'المزارع',
    'dashboard.stats.area': 'المساحة الكلية',
    'dashboard.stats.diagnoses': 'التشخيصات',
    'dashboard.stats.alerts': 'التنبيهات النشطة',
    'dashboard.stats.health': 'الصحة العامة',
    'dashboard.stats.reviews': 'المراجعات',
    'dashboard.stats.activeFarms': 'المزارع النشطة',
    'dashboard.charts.yield': 'اتجاه الإنتاج',
    'dashboard.charts.activity': 'النشاط الأسبوعي',
    'dashboard.charts.crops': 'توزيع المحاصيل',
    'dashboard.quickActions': 'إجراءات سريعة',

    // Farms
    'farms.title': 'إدارة المزارع',
    'farms.add': 'إضافة مزرعة',
    'farms.edit': 'تعديل المزرعة',
    'farms.delete': 'حذف المزرعة',
    'farms.name': 'اسم المزرعة',
    'farms.location': 'الموقع',
    'farms.area': 'المساحة',
    'farms.owner': 'المالك',
    'farms.status': 'الحالة',
    'farms.crops': 'المحاصيل',
    'farms.health': 'الصحة',
    'farms.lastUpdate': 'آخر تحديث',

    // Diseases
    'diseases.title': 'تشخيص الأمراض',
    'diseases.recent': 'التشخيصات الأخيرة',
    'diseases.pending': 'قيد الانتظار',
    'diseases.confirmed': 'مؤكد',
    'diseases.rejected': 'مرفوض',
    'diseases.treated': 'تم العلاج',
    'diseases.confidence': 'نسبة الثقة',
    'diseases.severity': 'الشدة',
    'diseases.recommendation': 'التوصية',

    // Alerts
    'alerts.title': 'التنبيهات',
    'alerts.active': 'نشطة',
    'alerts.acknowledged': 'تم الاطلاع',
    'alerts.resolved': 'تم الحل',
    'alerts.critical': 'حرج',
    'alerts.warning': 'تحذير',
    'alerts.info': 'معلومات',
    'alerts.emergency': 'طوارئ',
    'alerts.categories.crop_health': 'صحة المحصول',
    'alerts.categories.weather': 'الطقس',
    'alerts.categories.irrigation': 'الري',
    'alerts.categories.pest': 'الآفات',
    'alerts.categories.disease': 'الأمراض',
    'alerts.categories.market': 'السوق',
    'alerts.categories.system': 'النظام',

    // Irrigation
    'irrigation.title': 'إدارة الري',
    'irrigation.schedule': 'جدول الري',
    'irrigation.active': 'جاري الري',
    'irrigation.completed': 'مكتمل',
    'irrigation.pending': 'مجدول',
    'irrigation.waterUsage': 'استهلاك المياه',
    'irrigation.duration': 'المدة',
    'irrigation.startTime': 'وقت البدء',
    'irrigation.endTime': 'وقت الانتهاء',

    // Sensors
    'sensors.title': 'الحساسات',
    'sensors.active': 'نشط',
    'sensors.inactive': 'غير نشط',
    'sensors.offline': 'غير متصل',
    'sensors.battery': 'البطارية',
    'sensors.signal': 'الإشارة',
    'sensors.lastReading': 'آخر قراءة',
    'sensors.types.temperature': 'درجة الحرارة',
    'sensors.types.humidity': 'الرطوبة',
    'sensors.types.soilMoisture': 'رطوبة التربة',
    'sensors.types.ph': 'الحموضة',
    'sensors.types.ec': 'الموصلية',

    // Auth
    'auth.login': 'تسجيل الدخول',
    'auth.logout': 'تسجيل الخروج',
    'auth.email': 'البريد الإلكتروني',
    'auth.password': 'كلمة المرور',
    'auth.rememberMe': 'تذكرني',
    'auth.forgotPassword': 'نسيت كلمة المرور؟',
    'auth.loginError': 'بيانات الدخول غير صحيحة',

    // Errors
    'error.network': 'خطأ في الاتصال',
    'error.server': 'خطأ في الخادم',
    'error.notFound': 'الصفحة غير موجودة',
    'error.unauthorized': 'غير مصرح',
    'error.forbidden': 'ممنوع الوصول',
    'error.validation': 'خطأ في البيانات',
    'error.unknown': 'خطأ غير معروف',

    // Time
    'time.today': 'اليوم',
    'time.yesterday': 'أمس',
    'time.thisWeek': 'هذا الأسبوع',
    'time.thisMonth': 'هذا الشهر',
    'time.lastWeek': 'الأسبوع الماضي',
    'time.lastMonth': 'الشهر الماضي',

    // Units
    'units.hectare': 'هكتار',
    'units.hectares': 'هكتارات',
    'units.meter': 'متر',
    'units.meters': 'أمتار',
    'units.kilometer': 'كيلومتر',
    'units.liter': 'لتر',
    'units.liters': 'لترات',
    'units.kg': 'كجم',
    'units.ton': 'طن',
    'units.percent': '%',
  },
  en: {
    // Common
    'common.loading': 'Loading...',
    'common.error': 'An error occurred',
    'common.retry': 'Retry',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.add': 'Add',
    'common.search': 'Search',
    'common.filter': 'Filter',
    'common.export': 'Export',
    'common.import': 'Import',
    'common.refresh': 'Refresh',
    'common.close': 'Close',
    'common.confirm': 'Confirm',
    'common.back': 'Back',
    'common.next': 'Next',
    'common.previous': 'Previous',
    'common.yes': 'Yes',
    'common.no': 'No',
    'common.all': 'All',
    'common.none': 'None',
    'common.select': 'Select',
    'common.noData': 'No data available',
    'common.noResults': 'No results found',

    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.farms': 'Farms',
    'nav.fields': 'Fields',
    'nav.diseases': 'Diagnosis',
    'nav.alerts': 'Alerts',
    'nav.irrigation': 'Irrigation',
    'nav.sensors': 'Sensors',
    'nav.yield': 'Yield Prediction',
    'nav.epidemic': 'Epidemics',
    'nav.lab': 'Laboratory',
    'nav.support': 'Support',
    'nav.settings': 'Settings',
    'nav.users': 'Users',
    'nav.reports': 'Reports',
    'nav.logout': 'Logout',

    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.welcome': 'Welcome',
    'dashboard.overview': 'Overview',
    'dashboard.stats.farms': 'Farms',
    'dashboard.stats.area': 'Total Area',
    'dashboard.stats.diagnoses': 'Diagnoses',
    'dashboard.stats.alerts': 'Active Alerts',
    'dashboard.stats.health': 'Overall Health',
    'dashboard.stats.reviews': 'Reviews',
    'dashboard.stats.activeFarms': 'Active Farms',
    'dashboard.charts.yield': 'Yield Trend',
    'dashboard.charts.activity': 'Weekly Activity',
    'dashboard.charts.crops': 'Crop Distribution',
    'dashboard.quickActions': 'Quick Actions',

    // Farms
    'farms.title': 'Farm Management',
    'farms.add': 'Add Farm',
    'farms.edit': 'Edit Farm',
    'farms.delete': 'Delete Farm',
    'farms.name': 'Farm Name',
    'farms.location': 'Location',
    'farms.area': 'Area',
    'farms.owner': 'Owner',
    'farms.status': 'Status',
    'farms.crops': 'Crops',
    'farms.health': 'Health',
    'farms.lastUpdate': 'Last Update',

    // Diseases
    'diseases.title': 'Disease Diagnosis',
    'diseases.recent': 'Recent Diagnoses',
    'diseases.pending': 'Pending',
    'diseases.confirmed': 'Confirmed',
    'diseases.rejected': 'Rejected',
    'diseases.treated': 'Treated',
    'diseases.confidence': 'Confidence',
    'diseases.severity': 'Severity',
    'diseases.recommendation': 'Recommendation',

    // Alerts
    'alerts.title': 'Alerts',
    'alerts.active': 'Active',
    'alerts.acknowledged': 'Acknowledged',
    'alerts.resolved': 'Resolved',
    'alerts.critical': 'Critical',
    'alerts.warning': 'Warning',
    'alerts.info': 'Info',
    'alerts.emergency': 'Emergency',
    'alerts.categories.crop_health': 'Crop Health',
    'alerts.categories.weather': 'Weather',
    'alerts.categories.irrigation': 'Irrigation',
    'alerts.categories.pest': 'Pest',
    'alerts.categories.disease': 'Disease',
    'alerts.categories.market': 'Market',
    'alerts.categories.system': 'System',

    // Irrigation
    'irrigation.title': 'Irrigation Management',
    'irrigation.schedule': 'Irrigation Schedule',
    'irrigation.active': 'Irrigating',
    'irrigation.completed': 'Completed',
    'irrigation.pending': 'Scheduled',
    'irrigation.waterUsage': 'Water Usage',
    'irrigation.duration': 'Duration',
    'irrigation.startTime': 'Start Time',
    'irrigation.endTime': 'End Time',

    // Sensors
    'sensors.title': 'Sensors',
    'sensors.active': 'Active',
    'sensors.inactive': 'Inactive',
    'sensors.offline': 'Offline',
    'sensors.battery': 'Battery',
    'sensors.signal': 'Signal',
    'sensors.lastReading': 'Last Reading',
    'sensors.types.temperature': 'Temperature',
    'sensors.types.humidity': 'Humidity',
    'sensors.types.soilMoisture': 'Soil Moisture',
    'sensors.types.ph': 'pH Level',
    'sensors.types.ec': 'Conductivity',

    // Auth
    'auth.login': 'Login',
    'auth.logout': 'Logout',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.rememberMe': 'Remember me',
    'auth.forgotPassword': 'Forgot password?',
    'auth.loginError': 'Invalid credentials',

    // Errors
    'error.network': 'Network error',
    'error.server': 'Server error',
    'error.notFound': 'Page not found',
    'error.unauthorized': 'Unauthorized',
    'error.forbidden': 'Access forbidden',
    'error.validation': 'Validation error',
    'error.unknown': 'Unknown error',

    // Time
    'time.today': 'Today',
    'time.yesterday': 'Yesterday',
    'time.thisWeek': 'This week',
    'time.thisMonth': 'This month',
    'time.lastWeek': 'Last week',
    'time.lastMonth': 'Last month',

    // Units
    'units.hectare': 'hectare',
    'units.hectares': 'hectares',
    'units.meter': 'meter',
    'units.meters': 'meters',
    'units.kilometer': 'kilometer',
    'units.liter': 'liter',
    'units.liters': 'liters',
    'units.kg': 'kg',
    'units.ton': 'ton',
    'units.percent': '%',
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════

const config: I18nConfig = {
  defaultLocale: 'ar',
  fallbackLocale: 'ar',
  rtlLocales: ['ar'],
};

let currentLocale: Locale = config.defaultLocale;

// ═══════════════════════════════════════════════════════════════════════════
// Core Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get current locale
 */
export function getLocale(): Locale {
  return currentLocale;
}

/**
 * Set current locale
 */
export function setLocale(locale: Locale): void {
  currentLocale = locale;

  if (typeof document !== 'undefined') {
    document.documentElement.lang = locale;
    document.documentElement.dir = isRtl(locale) ? 'rtl' : 'ltr';

    // Store preference
    localStorage.setItem('sahool_locale', locale);
  }
}

/**
 * Check if locale is RTL
 */
export function isRtl(locale: Locale = currentLocale): boolean {
  return config.rtlLocales.includes(locale);
}

/**
 * Get text direction
 */
export function getDirection(locale: Locale = currentLocale): 'rtl' | 'ltr' {
  return isRtl(locale) ? 'rtl' : 'ltr';
}

/**
 * Translate a key
 */
export function t(
  key: TranslationKey,
  params?: Record<string, string | number>
): string {
  const localeTranslations = translations[currentLocale] || translations[config.fallbackLocale];
  let text: string = localeTranslations[key] || translations[config.fallbackLocale][key] || key;

  // Replace parameters
  if (params) {
    Object.entries(params).forEach(([param, value]) => {
      text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), String(value));
    });
  }

  return text;
}

/**
 * Translate with pluralization
 */
export function tp(
  key: TranslationKey,
  count: number,
  params?: Record<string, string | number>
): string {
  const pluralKey = count === 1 ? key : (`${key}_plural` as TranslationKey);
  return t(pluralKey in translations[currentLocale] ? pluralKey : key, { count, ...params });
}

// ═══════════════════════════════════════════════════════════════════════════
// Number Formatting
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Format number according to locale
 */
export function formatNumber(
  value: number,
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat(currentLocale, options).format(value);
}

/**
 * Format currency
 */
export function formatCurrency(
  value: number,
  currency: string = 'YER'
): string {
  return new Intl.NumberFormat(currentLocale, {
    style: 'currency',
    currency,
  }).format(value);
}

/**
 * Format percentage
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat(currentLocale, {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
}

// ═══════════════════════════════════════════════════════════════════════════
// Date Formatting
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Format date according to locale
 */
export function formatDate(
  date: Date | string | number,
  options?: Intl.DateTimeFormatOptions
): string {
  const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  return new Intl.DateTimeFormat(currentLocale, {
    dateStyle: 'medium',
    ...options,
  }).format(d);
}

/**
 * Format time according to locale
 */
export function formatTime(
  date: Date | string | number,
  options?: Intl.DateTimeFormatOptions
): string {
  const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  return new Intl.DateTimeFormat(currentLocale, {
    timeStyle: 'short',
    ...options,
  }).format(d);
}

/**
 * Format datetime according to locale
 */
export function formatDateTime(
  date: Date | string | number,
  options?: Intl.DateTimeFormatOptions
): string {
  const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  return new Intl.DateTimeFormat(currentLocale, {
    dateStyle: 'medium',
    timeStyle: 'short',
    ...options,
  }).format(d);
}

/**
 * Get relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: Date | string | number): string {
  const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  const rtf = new Intl.RelativeTimeFormat(currentLocale, { numeric: 'auto' });

  if (diffDay > 0) return rtf.format(-diffDay, 'day');
  if (diffHour > 0) return rtf.format(-diffHour, 'hour');
  if (diffMin > 0) return rtf.format(-diffMin, 'minute');
  return rtf.format(-diffSec, 'second');
}

// ═══════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Initialize i18n
 */
export function initializeI18n(): Locale {
  if (typeof window !== 'undefined') {
    // Check stored preference
    const stored = localStorage.getItem('sahool_locale') as Locale | null;
    if (stored && (stored === 'ar' || stored === 'en')) {
      setLocale(stored);
      return stored;
    }

    // Check browser preference
    const browserLang = navigator.language.split('-')[0];
    if (browserLang === 'ar' || browserLang === 'en') {
      setLocale(browserLang as Locale);
      return browserLang as Locale;
    }
  }

  setLocale(config.defaultLocale);
  return config.defaultLocale;
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const i18n = {
  t,
  tp,
  getLocale,
  setLocale,
  isRtl,
  getDirection,
  formatNumber,
  formatCurrency,
  formatPercent,
  formatDate,
  formatTime,
  formatDateTime,
  formatRelativeTime,
  initialize: initializeI18n,
  translations,
};

export default i18n;
