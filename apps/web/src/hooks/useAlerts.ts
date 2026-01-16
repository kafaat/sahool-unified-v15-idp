/**
 * SAHOOL useAlerts Hook
 * جلب التنبيهات - محدث لاستخدام API Client الجديد
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { apiClient } from "@/lib/api";
import { Alert } from "../types";
import { logger } from "@/lib/logger";

// API Alert response type
interface ApiAlert {
  id: string;
  title?: string;
  type?: string;
  titleAr?: string;
  message?: string;
  description?: string;
  messageAr?: string;
  severity?: Alert["severity"];
  category?: Alert["category"];
  status?: Alert["status"];
  fieldId?: string;
  fieldName?: string;
  createdAt?: string;
  acknowledged?: boolean;
  actionUrl?: string;
}

// Default alerts for fallback/demo
const DEFAULT_ALERTS: Alert[] = [
  {
    id: "1",
    title: "Low NDVI Detected",
    titleAr: "انخفاض NDVI مكتشف",
    message: "Field 12 shows declining vegetation health",
    messageAr: "الحقل 12 يظهر تراجع في صحة النبات",
    severity: "warning",
    category: "ndvi",
    status: "active",
    fieldId: "12",
    fieldName: "الحقل 12",
    createdAt: new Date().toISOString(),
    read: false,
  },
  {
    id: "2",
    title: "Irrigation Overdue",
    titleAr: "تأخر موعد الري",
    message: "Zone A irrigation is 2 days overdue",
    messageAr: "تأخر ري المنطقة A بيومين",
    severity: "critical",
    category: "irrigation",
    status: "active",
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    read: false,
  },
  {
    id: "3",
    title: "Weather Alert",
    titleAr: "تنبيه طقس",
    message: "High temperatures expected tomorrow",
    messageAr: "متوقع ارتفاع الحرارة غداً",
    severity: "info",
    category: "weather",
    status: "acknowledged",
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    read: true,
  },
];

// Helper function to map API alerts to our Alert type
const mapApiAlert = (alert: ApiAlert): Alert => ({
  id: alert.id,
  title: alert.title || alert.type || "Alert",
  titleAr: alert.titleAr || alert.title || "تنبيه",
  message: alert.message || alert.description || "",
  messageAr: alert.messageAr || alert.message || "",
  severity: alert.severity || "info",
  category: alert.category || "system",
  status: alert.status || "active",
  fieldId: alert.fieldId,
  fieldName: alert.fieldName,
  createdAt: alert.createdAt || new Date().toISOString(),
  read: alert.acknowledged ?? false,
  actionUrl: alert.actionUrl,
});

export function useAlerts(tenantId?: string) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const alertsRef = useRef<Alert[]>([]);

  // Keep alerts ref in sync
  useEffect(() => {
    alertsRef.current = alerts;
  }, [alerts]);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        setIsLoading(true);

        // Try to fetch from API
        if (tenantId) {
          const response = await apiClient.getAlerts({
            tenantId,
            status: "active",
          });
          if (response.success && response.data) {
            // Map API alerts to our Alert type
            const mappedAlerts: Alert[] = response.data.map(mapApiAlert);
            setAlerts(mappedAlerts);
            setError(null);
            return;
          }
        }

        // Fallback to demo data
        await new Promise((resolve) => setTimeout(resolve, 300));
        setAlerts(DEFAULT_ALERTS);
        setError(null);
      } catch (err) {
        logger.error("[useAlerts] Failed to fetch alerts:", err);
        setAlerts(DEFAULT_ALERTS);
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setIsLoading(false);
      }
    }

    fetchAlerts();
  }, [tenantId]);

  const dismiss = useCallback(async (id: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, read: true, status: "acknowledged" as const } : a,
      ),
    );

    try {
      await apiClient.acknowledgeAlert(id);
    } catch (error) {
      logger.error("Failed to acknowledge alert:", error);
    }
  }, []);

  const dismissAll = useCallback(async () => {
    // Use ref to get current alerts and avoid stale closure
    const activeAlertIds = alertsRef.current
      .filter((a) => !a.read)
      .map((a) => a.id);
    setAlerts((prev) =>
      prev.map((a) => ({ ...a, read: true, status: "acknowledged" as const })),
    );

    // Acknowledge all in background
    for (const id of activeAlertIds) {
      try {
        await apiClient.acknowledgeAlert(id);
      } catch (err) {
        // Log individual failures but don't throw
        logger.warn(`Failed to acknowledge alert ${id}:`, err);
      }
    }
  }, []);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      if (tenantId) {
        const response = await apiClient.getAlerts({
          tenantId,
          status: "active",
        });
        if (response.success && response.data) {
          const mappedAlerts: Alert[] = response.data.map(mapApiAlert);
          setAlerts(mappedAlerts);
          setError(null);
        } else {
          setError(response.error || "Failed to refresh alerts");
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh");
    } finally {
      setIsLoading(false);
    }
  }, [tenantId]);

  return { alerts, isLoading, error, dismiss, dismissAll, refresh };
}

export default useAlerts;
