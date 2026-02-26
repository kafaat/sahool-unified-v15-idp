/**
 * Alerts Feature - Mock Data (Development Fallback)
 * بيانات وهمية للتنبيهات
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { Alert, AlertStats, AlertCount } from "./types";

export const MOCK_ALERTS: Alert[] = [
  {
    id: "alert-1",
    title: "High Temperature Warning",
    titleAr: "تحذير من درجات حرارة عالية",
    message:
      "Temperature expected to exceed 40\u00b0C tomorrow. Consider adjusting irrigation schedule.",
    messageAr:
      "من المتوقع أن تتجاوز درجة الحرارة 40 درجة مئوية غداً. يُنصح بتعديل جدول الري.",
    severity: "warning",
    category: "weather",
    status: "active",
    fieldId: "field-1",
    fieldName: "North Field",
    fieldNameAr: "الحقل الشمالي",
    metadata: {
      expectedTemp: 42,
      source: "weather_service",
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
  },
  {
    id: "alert-2",
    title: "Pest Detection",
    titleAr: "اكتشاف آفات",
    message:
      "Early signs of aphid infestation detected in Field #3. Immediate action recommended.",
    messageAr:
      "تم اكتشاف علامات مبكرة لإصابة بالمن في الحقل رقم 3. يوصى باتخاذ إجراء فوري.",
    severity: "critical",
    category: "pest",
    status: "active",
    fieldId: "field-3",
    fieldName: "East Field",
    fieldNameAr: "الحقل الشرقي",
    metadata: {
      pestType: "aphid",
      severity: "moderate",
      affectedArea: 25,
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
  },
  {
    id: "alert-3",
    title: "Irrigation System Maintenance",
    titleAr: "صيانة نظام الري",
    message:
      "Scheduled maintenance for irrigation system in Field #5 tomorrow at 8 AM.",
    messageAr: "صيانة مجدولة لنظام الري في الحقل رقم 5 غداً الساعة 8 صباحاً.",
    severity: "info",
    category: "irrigation",
    status: "acknowledged",
    fieldId: "field-5",
    fieldName: "South Field",
    fieldNameAr: "الحقل الجنوبي",
    metadata: {
      maintenanceType: "scheduled",
      duration: 120,
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 24 hours ago
    acknowledgedAt: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
  {
    id: "alert-4",
    title: "Low Soil Moisture",
    titleAr: "انخفاض رطوبة التربة",
    message:
      "Soil moisture levels below optimal range in Field #2. Irrigation needed.",
    messageAr:
      "مستويات رطوبة التربة أقل من النطاق الأمثل في الحقل رقم 2. يلزم الري.",
    severity: "warning",
    category: "irrigation",
    status: "active",
    fieldId: "field-2",
    fieldName: "West Field",
    fieldNameAr: "الحقل الغربي",
    metadata: {
      currentMoisture: 15,
      optimalRange: "25-35",
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 minutes ago
  },
  {
    id: "alert-5",
    title: "Market Price Update",
    titleAr: "تحديث أسعار السوق",
    message:
      "Coffee prices increased by 15% in the local market. Good time to sell.",
    messageAr: "ارتفعت أسعار البن بنسبة 15% في السوق المحلي. وقت جيد للبيع.",
    severity: "info",
    category: "market",
    status: "active",
    metadata: {
      priceChange: 15,
      crop: "coffee",
      market: "local",
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 minutes ago
  },
];

export const MOCK_STATS: AlertStats = {
  total: 5,
  bySeverity: {
    info: 2,
    warning: 2,
    critical: 1,
    emergency: 0,
  },
  byCategory: {
    crop_health: 0,
    weather: 1,
    irrigation: 2,
    pest: 1,
    disease: 0,
    market: 1,
    system: 0,
  },
  byStatus: {
    active: 4,
    acknowledged: 1,
    resolved: 0,
    dismissed: 0,
  },
  trend: "stable",
  trendPercentage: 0,
};

export const MOCK_COUNT: AlertCount = {
  count: 4,
  bySeverity: {
    info: 2,
    warning: 2,
    critical: 1,
    emergency: 0,
  },
};
