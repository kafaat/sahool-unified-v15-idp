"use client";

/**
 * SAHOOL Service Health Dashboard
 * Real-time service health monitoring via Kong Gateway
 * لوحة مراقبة صحة الخدمات عبر بوابة Kong
 */

import React, { useEffect, useState, useCallback } from "react";
import { RefreshCw, CheckCircle, AlertTriangle, XCircle, Activity } from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ServiceHealth {
  name: string;
  nameAr: string;
  status: "healthy" | "degraded" | "unhealthy" | "checking";
  latencyMs: number;
  lastChecked: Date;
  endpoint: string;
}

interface ServiceHealthDashboardProps {
  className?: string;
  showTitle?: boolean;
  compact?: boolean;
  onServiceClick?: (service: ServiceHealth) => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Service Configuration (synced with Kong)
// ═══════════════════════════════════════════════════════════════════════════

const MONITORED_SERVICES = [
  {
    key: "field-management",
    name: "Field Management",
    nameAr: "إدارة الحقول",
    endpoint: "/api/v1/fields/healthz",
  },
  {
    key: "weather",
    name: "Weather Service",
    nameAr: "خدمة الطقس",
    endpoint: "/api/v1/weather/healthz",
  },
  {
    key: "vegetation",
    name: "Vegetation Analysis",
    nameAr: "تحليل الغطاء النباتي",
    endpoint: "/api/v1/vegetation/healthz",
  },
  {
    key: "irrigation",
    name: "Smart Irrigation",
    nameAr: "الري الذكي",
    endpoint: "/api/v1/irrigation/healthz",
  },
  {
    key: "advisory",
    name: "Advisory Service",
    nameAr: "خدمة الاستشارات",
    endpoint: "/api/v1/advisory/healthz",
  },
  {
    key: "tasks",
    name: "Task Service",
    nameAr: "إدارة المهام",
    endpoint: "/api/v1/tasks/healthz",
  },
  {
    key: "notifications",
    name: "Notifications",
    nameAr: "الإشعارات",
    endpoint: "/api/v1/notifications/healthz",
  },
  {
    key: "alerts",
    name: "Alert Service",
    nameAr: "خدمة التنبيهات",
    endpoint: "/api/v1/alerts/healthz",
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

const ServiceHealthDashboardInner = React.memo(function ServiceHealthDashboard({
  className = "",
  showTitle = true,
  compact = false,
  onServiceClick,
}: ServiceHealthDashboardProps) {
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  /**
   * Check health of a single service
   */
  const checkServiceHealth = useCallback(
    async (service: (typeof MONITORED_SERVICES)[0]): Promise<ServiceHealth> => {
      const startTime = performance.now();
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const response = await fetch(`${apiUrl}${service.endpoint}`, {
          method: "GET",
          signal: controller.signal,
          headers: {
            Accept: "application/json",
          },
        });

        clearTimeout(timeoutId);
        const latencyMs = Math.round(performance.now() - startTime);

        if (response.ok) {
          return {
            name: service.name,
            nameAr: service.nameAr,
            status: latencyMs > 2000 ? "degraded" : "healthy",
            latencyMs,
            lastChecked: new Date(),
            endpoint: service.endpoint,
          };
        } else {
          return {
            name: service.name,
            nameAr: service.nameAr,
            status: response.status >= 500 ? "unhealthy" : "degraded",
            latencyMs,
            lastChecked: new Date(),
            endpoint: service.endpoint,
          };
        }
      } catch {
        return {
          name: service.name,
          nameAr: service.nameAr,
          status: "unhealthy",
          latencyMs: Math.round(performance.now() - startTime),
          lastChecked: new Date(),
          endpoint: service.endpoint,
        };
      }
    },
    []
  );

  /**
   * Check all services health
   */
  const refreshHealth = useCallback(async () => {
    setIsRefreshing(true);

    // Set all to checking state
    setServices(
      MONITORED_SERVICES.map((s) => ({
        name: s.name,
        nameAr: s.nameAr,
        status: "checking" as const,
        latencyMs: 0,
        lastChecked: new Date(),
        endpoint: s.endpoint,
      }))
    );

    // Check all services in parallel
    const results = await Promise.all(
      MONITORED_SERVICES.map((service) => checkServiceHealth(service))
    );

    setServices(results);
    setLastRefresh(new Date());
    setIsRefreshing(false);
  }, [checkServiceHealth]);

  // Initial load and auto-refresh every 60 seconds
  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 60000);
    return () => clearInterval(interval);
  }, [refreshHealth]);

  /**
   * Get status icon
   */
  const getStatusIcon = (status: ServiceHealth["status"]) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "degraded":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case "unhealthy":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "checking":
        return <Activity className="h-5 w-5 text-blue-500 animate-pulse" />;
    }
  };

  /**
   * Get status color class
   */
  const getStatusColor = (status: ServiceHealth["status"]) => {
    switch (status) {
      case "healthy":
        return "bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800";
      case "degraded":
        return "bg-yellow-50 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800";
      case "unhealthy":
        return "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800";
      case "checking":
        return "bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800";
    }
  };

  /**
   * Get latency color
   */
  const getLatencyColor = (latencyMs: number) => {
    if (latencyMs < 200) return "text-green-600";
    if (latencyMs < 500) return "text-yellow-600";
    if (latencyMs < 1000) return "text-orange-600";
    return "text-red-600";
  };

  /**
   * Count services by status
   */
  const healthyCount = services.filter((s) => s.status === "healthy").length;
  const degradedCount = services.filter((s) => s.status === "degraded").length;
  const unhealthyCount = services.filter((s) => s.status === "unhealthy").length;

  return (
    <div className={`rounded-lg border bg-card p-4 ${className}`}>
      {/* Header */}
      {showTitle && (
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">Service Health</h3>
            <p className="text-sm text-muted-foreground">صحة الخدمات</p>
          </div>
          <button
            onClick={refreshHealth}
            disabled={isRefreshing}
            className="p-2 hover:bg-muted rounded-md transition-colors disabled:opacity-50"
            title="Refresh health status"
          >
            <RefreshCw
              className={`h-5 w-5 ${isRefreshing ? "animate-spin" : ""}`}
            />
          </button>
        </div>
      )}

      {/* Summary Bar */}
      <div className="flex items-center gap-4 mb-4 p-2 bg-muted/50 rounded-md">
        <div className="flex items-center gap-1">
          <CheckCircle className="h-4 w-4 text-green-500" />
          <span className="text-sm font-medium">{healthyCount}</span>
        </div>
        <div className="flex items-center gap-1">
          <AlertTriangle className="h-4 w-4 text-yellow-500" />
          <span className="text-sm font-medium">{degradedCount}</span>
        </div>
        <div className="flex items-center gap-1">
          <XCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm font-medium">{unhealthyCount}</span>
        </div>
        {lastRefresh && (
          <span className="text-xs text-muted-foreground mr-auto">
            آخر تحديث: {lastRefresh.toLocaleTimeString("ar-SA")}
          </span>
        )}
      </div>

      {/* Service Grid */}
      <div
        className={`grid gap-2 ${compact ? "grid-cols-2 sm:grid-cols-4" : "grid-cols-1 sm:grid-cols-2"}`}
      >
        {services.map((service) => (
          <div
            key={service.endpoint}
            className={`p-3 rounded-md border cursor-pointer transition-all hover:shadow-sm ${getStatusColor(service.status)} focus:outline-none focus:ring-2 focus:ring-blue-500`}
            onClick={() => onServiceClick?.(service)}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onServiceClick?.(service); } }}
            tabIndex={onServiceClick ? 0 : undefined}
            role={onServiceClick ? "button" : undefined}
            aria-label={`${service.nameAr} - ${service.name}: ${service.status === "healthy" ? "سليم" : service.status === "degraded" ? "متدهور" : service.status === "unhealthy" ? "معطل" : "جاري الفحص"}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusIcon(service.status)}
                <div>
                  <p className="text-sm font-medium">{service.name}</p>
                  {!compact && (
                    <p className="text-xs text-muted-foreground">
                      {service.nameAr}
                    </p>
                  )}
                </div>
              </div>
              {service.status !== "checking" && (
                <span className={`text-xs font-mono ${getLatencyColor(service.latencyMs)}`}>
                  {service.latencyMs}ms
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Overall Status */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Overall Status</span>
          <span
            className={`font-medium ${
              unhealthyCount > 0
                ? "text-red-600"
                : degradedCount > 0
                  ? "text-yellow-600"
                  : "text-green-600"
            }`}
          >
            {unhealthyCount > 0
              ? "System Issues"
              : degradedCount > 0
                ? "Partially Degraded"
                : "All Systems Operational"}
          </span>
        </div>
      </div>
    </div>
  );
});

export { ServiceHealthDashboardInner as ServiceHealthDashboard };
export default ServiceHealthDashboardInner;
export type { ServiceHealthDashboardProps };
