/**
 * SAHOOL Admin - Real-time data hook
 * خطاف البيانات اللحظية
 *
 * Integrates WebSocket events with the query cache
 * to auto-invalidate data when real-time updates arrive.
 */

"use client";

import { useEffect } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { invalidateQueries } from "./use-api-query";

type RealtimeEvent =
  | "alert"
  | "sensor"
  | "irrigation"
  | "diagnosis"
  | "farm_update"
  | "weather"
  | "task";

const EVENT_TO_CACHE_KEYS: Record<RealtimeEvent, string[]> = {
  alert: ["alerts", "dashboard"],
  sensor: ["sensors", "fields"],
  irrigation: ["irrigation", "fields"],
  diagnosis: ["diagnoses", "dashboard"],
  farm_update: ["fields", "dashboard"],
  weather: ["weather"],
  task: ["tasks"],
};

/**
 * Hook that connects WebSocket events to the query cache.
 * When a real-time event arrives, it invalidates the related cache keys
 * so hooks like useDashboardStats, useFields, etc. auto-refetch.
 *
 * @example
 * ```tsx
 * // In your layout or root component:
 * function AdminLayout({ children }) {
 *   useRealtimeSync(['alert', 'farm_update', 'task']);
 *   return <>{children}</>;
 * }
 * ```
 */
export function useRealtimeSync(events: RealtimeEvent[] = []) {
  const { isConnected, subscribe } = useWebSocket({ autoConnect: true });

  useEffect(() => {
    if (!isConnected) return;

    const effectiveEvents =
      events.length > 0
        ? events
        : (Object.keys(EVENT_TO_CACHE_KEYS) as RealtimeEvent[]);

    const unsubscribers = effectiveEvents.map((event) =>
      subscribe(event, () => {
        const keys = EVENT_TO_CACHE_KEYS[event];
        if (keys) {
          for (const key of keys) {
            invalidateQueries(key);
          }
        }
      }),
    );

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [isConnected, subscribe, events]);

  return { isConnected };
}
