/**
 * Alert Mock Data
 * بيانات التنبيهات الوهمية
 */

import { generateId, randomItem, randomPastDate, arabicNames } from "./utils";

export type AlertSeverity = "low" | "medium" | "high" | "critical";
export type AlertType =
  | "pest"
  | "disease"
  | "weather"
  | "irrigation"
  | "harvest"
  | "soil";
export type AlertStatus = "active" | "acknowledged" | "resolved";

export interface MockAlert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  fieldId: string;
  fieldName: string;
  timestamp: string;
  status: AlertStatus;
  isRead: boolean;
  metadata?: Record<string, unknown>;
}

const alertMessages: Record<AlertType, { title: string; messages: string[] }> =
  {
    pest: {
      title: "تنبيه آفات",
      messages: [
        "تم اكتشاف حشرات ضارة في الحقل",
        "ارتفاع في نشاط الآفات الزراعية",
        "يُنصح برش المبيدات الحشرية",
      ],
    },
    disease: {
      title: "تنبيه أمراض",
      messages: [
        "ظهور أعراض مرضية على المحصول",
        "انتشار فطري محتمل",
        "يُنصح بفحص النباتات المصابة",
      ],
    },
    weather: {
      title: "تنبيه طقس",
      messages: [
        "توقعات بموجة حر شديدة",
        "احتمال هطول أمطار غزيرة",
        "رياح قوية متوقعة",
      ],
    },
    irrigation: {
      title: "تنبيه ري",
      messages: [
        "مستوى الرطوبة منخفض جداً",
        "الحقل يحتاج للري الفوري",
        "كفاءة نظام الري منخفضة",
      ],
    },
    harvest: {
      title: "تنبيه حصاد",
      messages: [
        "المحصول جاهز للحصاد",
        "الوقت المثالي للحصاد خلال الأسبوع القادم",
        "نضج المحصول يقترب",
      ],
    },
    soil: {
      title: "تنبيه تربة",
      messages: [
        "مستوى المغذيات منخفض",
        "درجة حموضة التربة غير مناسبة",
        "يُنصح بتحليل التربة",
      ],
    },
  };

/**
 * Generate a single mock alert
 */
export function generateMockAlert(
  overrides: Partial<MockAlert> = {},
): MockAlert {
  const type = randomItem<AlertType>([
    "pest",
    "disease",
    "weather",
    "irrigation",
    "harvest",
    "soil",
  ]);
  const alertData = alertMessages[type];

  return {
    id: generateId(),
    type,
    severity: randomItem<AlertSeverity>(["low", "medium", "high", "critical"]),
    title: alertData.title,
    message: randomItem(alertData.messages),
    fieldId: generateId(),
    fieldName: `حقل ${randomItem(arabicNames.crops)}`,
    timestamp: randomPastDate(7).toISOString(),
    status: randomItem<AlertStatus>(["active", "acknowledged", "resolved"]),
    isRead: Math.random() > 0.5,
    ...overrides,
  };
}

/**
 * Generate multiple mock alerts
 */
export function generateMockAlerts(count: number = 10): MockAlert[] {
  return Array.from({ length: count }, () => generateMockAlert());
}

/**
 * Generate alerts with specific distribution
 */
export function generateAlertsByStatus(
  activeCount: number,
  acknowledgedCount: number,
  resolvedCount: number,
): MockAlert[] {
  const alerts: MockAlert[] = [];

  for (let i = 0; i < activeCount; i++) {
    alerts.push(generateMockAlert({ status: "active", isRead: false }));
  }
  for (let i = 0; i < acknowledgedCount; i++) {
    alerts.push(generateMockAlert({ status: "acknowledged", isRead: true }));
  }
  for (let i = 0; i < resolvedCount; i++) {
    alerts.push(generateMockAlert({ status: "resolved", isRead: true }));
  }

  return alerts.sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
  );
}
