/**
 * SAHOOL Service Switcher
 * نظام التبديل بين الخدمات للمقارنة والاختبار
 *
 * يتيح للمستخدم:
 * - التبديل بين الخدمات القديمة والجديدة
 * - مقارنة الأداء والنتائج
 * - اختبار الخدمات قبل الترقية
 */

import { logger } from "@/lib/logger";

export type ServiceType =
  | "satellite"
  | "weather"
  | "ndvi"
  | "fertilizer"
  | "irrigation"
  | "crop-health"
  | "community"
  | "notifications"
  | "tasks"
  | "equipment";

export type ServiceVersion = "legacy" | "modern" | "mock";

export interface ServiceConfig {
  name: string;
  nameAr: string;
  legacy?: {
    port: number;
    endpoint: string;
    status: "deprecated" | "active";
  };
  modern: {
    port: number;
    endpoint: string;
    status: "active" | "beta" | "development";
  };
  mock?: {
    port: number;
    endpoint: string;
  };
}

// تعريف جميع الخدمات مع نسخها المختلفة
export const SERVICE_REGISTRY: Record<ServiceType, ServiceConfig> = {
  satellite: {
    name: "Satellite Service",
    nameAr: "خدمة الأقمار الصناعية",
    legacy: {
      port: 8107,
      endpoint: "/ndvi",
      status: "deprecated",
    },
    modern: {
      port: 8090,
      endpoint: "/v1/satellite/analyze",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/ndvi",
    },
  },
  weather: {
    name: "Weather Service",
    nameAr: "خدمة الطقس",
    legacy: {
      port: 8108,
      endpoint: "/forecast",
      status: "deprecated",
    },
    modern: {
      port: 8092,
      endpoint: "/v1/weather/forecast",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/weather",
    },
  },
  ndvi: {
    name: "NDVI Engine",
    nameAr: "محرك NDVI",
    legacy: {
      port: 8107,
      endpoint: "/ndvi/{fieldId}",
      status: "deprecated",
    },
    modern: {
      port: 8090,
      endpoint: "/v1/analyze/{fieldId}",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/ndvi/summary",
    },
  },
  fertilizer: {
    name: "Fertilizer Advisor",
    nameAr: "مستشار التسميد",
    legacy: {
      port: 8105,
      endpoint: "/advise",
      status: "deprecated",
    },
    modern: {
      port: 8093,
      endpoint: "/v1/fertilizer/recommend",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/fertilizer",
    },
  },
  irrigation: {
    name: "Irrigation Smart",
    nameAr: "الري الذكي",
    modern: {
      port: 8094,
      endpoint: "/v1/irrigation/schedule",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/irrigation",
    },
  },
  "crop-health": {
    name: "Crop Health AI",
    nameAr: "صحة المحاصيل (AI)",
    legacy: {
      port: 8100,
      endpoint: "/diagnose",
      status: "deprecated",
    },
    modern: {
      port: 8095,
      endpoint: "/v1/diagnose",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/crop-health",
    },
  },
  community: {
    name: "Community Chat",
    nameAr: "الدردشة المجتمعية",
    legacy: {
      port: 8099,
      endpoint: "/ws",
      status: "deprecated",
    },
    modern: {
      port: 8097,
      endpoint: "/ws",
      status: "active",
    },
    mock: {
      port: 8081,
      endpoint: "/events",
    },
  },
  notifications: {
    name: "Notification Service",
    nameAr: "خدمة الإشعارات",
    legacy: {
      port: 8089,
      endpoint: "/notify",
      status: "deprecated",
    },
    modern: {
      port: 8110,
      endpoint: "/v1/notify",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/alerts",
    },
  },
  tasks: {
    name: "Task Service",
    nameAr: "خدمة المهام",
    modern: {
      port: 8103,
      endpoint: "/api/v1/tasks",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/tasks",
    },
  },
  equipment: {
    name: "Equipment Service",
    nameAr: "خدمة المعدات",
    modern: {
      port: 8101,
      endpoint: "/api/v1/equipment",
      status: "active",
    },
    mock: {
      port: 8000,
      endpoint: "/api/v1/equipment",
    },
  },
};

// الحالة الافتراضية للخدمات
const DEFAULT_SERVICE_VERSIONS: Record<ServiceType, ServiceVersion> = {
  satellite: "modern",
  weather: "modern",
  ndvi: "modern",
  fertilizer: "modern",
  irrigation: "modern",
  "crop-health": "modern",
  community: "modern",
  notifications: "modern",
  tasks: "modern",
  equipment: "modern",
};

// مفتاح التخزين المحلي
const STORAGE_KEY = "sahool_service_versions";

/**
 * الحصول على إعدادات الخدمات المحفوظة
 */
export function getServiceVersions(): Record<ServiceType, ServiceVersion> {
  if (typeof window === "undefined") {
    return DEFAULT_SERVICE_VERSIONS;
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return { ...DEFAULT_SERVICE_VERSIONS, ...JSON.parse(stored) };
    }
  } catch (e) {
    logger.error("Failed to load service versions:", e);
  }

  return DEFAULT_SERVICE_VERSIONS;
}

/**
 * حفظ إعدادات الخدمات
 */
export function setServiceVersions(
  versions: Partial<Record<ServiceType, ServiceVersion>>,
): void {
  if (typeof window === "undefined") return;

  try {
    const current = getServiceVersions();
    const updated = { ...current, ...versions };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

    // إرسال حدث للتحديث
    window.dispatchEvent(
      new CustomEvent("service-versions-changed", { detail: updated }),
    );
  } catch (e) {
    logger.error("Failed to save service versions:", e);
  }
}

/**
 * الحصول على نسخة خدمة محددة
 */
export function getServiceVersion(service: ServiceType): ServiceVersion {
  return getServiceVersions()[service];
}

/**
 * تعيين نسخة خدمة محددة
 */
export function setServiceVersion(
  service: ServiceType,
  version: ServiceVersion,
): void {
  setServiceVersions({ [service]: version });
}

/**
 * الحصول على URL الخدمة بناءً على النسخة المحددة
 */
export function getServiceUrl(
  service: ServiceType,
  baseHost: string = "localhost",
): string {
  const config = SERVICE_REGISTRY[service];
  const version = getServiceVersion(service);

  let serviceConfig;
  switch (version) {
    case "legacy":
      serviceConfig = config.legacy;
      break;
    case "mock":
      serviceConfig = config.mock;
      break;
    case "modern":
    default:
      serviceConfig = config.modern;
  }

  if (!serviceConfig) {
    // fallback to modern
    serviceConfig = config.modern;
  }

  return `http://${baseHost}:${serviceConfig.port}${serviceConfig.endpoint}`;
}

interface HealthCheckResult {
  healthy: boolean;
  latency: number;
}

interface ServiceHealth {
  legacy?: HealthCheckResult;
  modern: HealthCheckResult;
  mock?: HealthCheckResult;
}

/**
 * فحص صحة جميع الخدمات
 */
export async function checkServicesHealth(): Promise<
  Record<ServiceType, ServiceHealth>
> {
  const results: Record<string, ServiceHealth> = {};

  for (const [serviceType, config] of Object.entries(SERVICE_REGISTRY)) {
    const serviceHealth: ServiceHealth = {
      modern: await checkEndpointHealth(
        `http://localhost:${config.modern.port}/healthz`,
      ),
    };

    // فحص النسخة القديمة إذا وجدت
    if (config.legacy) {
      serviceHealth.legacy = await checkEndpointHealth(
        `http://localhost:${config.legacy.port}/healthz`,
      );
    }

    // فحص Mock إذا وجد
    if (config.mock) {
      serviceHealth.mock = await checkEndpointHealth(
        `http://localhost:${config.mock.port}/healthz`,
      );
    }

    results[serviceType] = serviceHealth;
  }

  return results as Record<ServiceType, ServiceHealth>;
}

/**
 * فحص صحة endpoint محدد
 */
async function checkEndpointHealth(
  url: string,
): Promise<{ healthy: boolean; latency: number }> {
  const start = performance.now();

  try {
    const response = await fetch(url, {
      method: "GET",
      signal: AbortSignal.timeout(5000),
    });

    const latency = performance.now() - start;
    return {
      healthy: response.ok,
      latency: Math.round(latency),
    };
  } catch {
    return {
      healthy: false,
      latency: -1,
    };
  }
}

interface ServiceComparisonResult<T> {
  data: T | null;
  latency: number;
  error?: string;
}

interface ComparisonResults<T> {
  legacy?: ServiceComparisonResult<T>;
  modern: ServiceComparisonResult<T>;
}

/**
 * مقارنة استجابة خدمتين
 */
export async function compareServices<T>(
  service: ServiceType,
  requestFn: (url: string) => Promise<T>,
): Promise<ComparisonResults<T>> {
  const config = SERVICE_REGISTRY[service];
  const results: ComparisonResults<T> = {
    modern: { data: null, latency: 0 },
  };

  // Modern service
  const modernStart = performance.now();
  try {
    const modernUrl = `http://localhost:${config.modern.port}${config.modern.endpoint}`;
    const data = await requestFn(modernUrl);
    results.modern = {
      data,
      latency: Math.round(performance.now() - modernStart),
    };
  } catch (error) {
    results.modern = {
      data: null,
      latency: Math.round(performance.now() - modernStart),
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }

  // Legacy service (if exists)
  if (config.legacy) {
    const legacyStart = performance.now();
    try {
      const legacyUrl = `http://localhost:${config.legacy.port}${config.legacy.endpoint}`;
      const data = await requestFn(legacyUrl);
      results.legacy = {
        data,
        latency: Math.round(performance.now() - legacyStart),
      };
    } catch (error) {
      results.legacy = {
        data: null,
        latency: Math.round(performance.now() - legacyStart),
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  return results;
}

/**
 * إعادة تعيين جميع الخدمات للإعدادات الافتراضية
 */
export function resetToDefaults(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(
    new CustomEvent("service-versions-changed", {
      detail: DEFAULT_SERVICE_VERSIONS,
    }),
  );
}

/**
 * تبديل جميع الخدمات لنسخة محددة
 */
export function switchAllServices(version: ServiceVersion): void {
  const updates: Partial<Record<ServiceType, ServiceVersion>> = {};

  for (const service of Object.keys(SERVICE_REGISTRY) as ServiceType[]) {
    const config = SERVICE_REGISTRY[service];

    // تأكد من وجود النسخة المطلوبة
    if (version === "legacy" && !config.legacy) continue;
    if (version === "mock" && !config.mock) continue;

    updates[service] = version;
  }

  setServiceVersions(updates);
}
