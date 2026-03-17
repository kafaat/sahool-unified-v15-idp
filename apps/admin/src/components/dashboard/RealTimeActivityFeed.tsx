"use client";

/**
 * SAHOOL Real-Time Activity Feed
 * Live activity stream from platform services via WebSocket
 * بث النشاطات المباشرة من خدمات المنصة
 */

import React, { useEffect, useState, useRef } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  CloudRain,
  Droplets,
  Eye,
  Leaf,
  MapPin,
  Settings,
  Truck,
  Users,
  Zap,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ActivityEvent {
  id: string;
  type: ActivityType;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  severity: "info" | "warning" | "success" | "error";
  service: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

type ActivityType =
  | "field_created"
  | "field_updated"
  | "ndvi_analysis"
  | "weather_alert"
  | "irrigation_scheduled"
  | "task_completed"
  | "equipment_maintenance"
  | "user_login"
  | "diagnosis_result"
  | "alert_triggered"
  | "system_event";

interface RealTimeActivityFeedProps {
  className?: string;
  maxItems?: number;
  showFilters?: boolean;
  wsUrl?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Activity Type Configuration
// ═══════════════════════════════════════════════════════════════════════════

const ACTIVITY_CONFIG: Record<
  ActivityType,
  { icon: React.ReactNode; color: string }
> = {
  field_created: {
    icon: <MapPin className="h-4 w-4" />,
    color: "text-green-500",
  },
  field_updated: {
    icon: <MapPin className="h-4 w-4" />,
    color: "text-blue-500",
  },
  ndvi_analysis: {
    icon: <Leaf className="h-4 w-4" />,
    color: "text-emerald-500",
  },
  weather_alert: {
    icon: <CloudRain className="h-4 w-4" />,
    color: "text-orange-500",
  },
  irrigation_scheduled: {
    icon: <Droplets className="h-4 w-4" />,
    color: "text-cyan-500",
  },
  task_completed: {
    icon: <CheckCircle className="h-4 w-4" />,
    color: "text-green-500",
  },
  equipment_maintenance: {
    icon: <Truck className="h-4 w-4" />,
    color: "text-yellow-500",
  },
  user_login: {
    icon: <Users className="h-4 w-4" />,
    color: "text-purple-500",
  },
  diagnosis_result: {
    icon: <Eye className="h-4 w-4" />,
    color: "text-pink-500",
  },
  alert_triggered: {
    icon: <AlertTriangle className="h-4 w-4" />,
    color: "text-red-500",
  },
  system_event: {
    icon: <Settings className="h-4 w-4" />,
    color: "text-gray-500",
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Mock Data Generator (for demo when WS not connected)
// ═══════════════════════════════════════════════════════════════════════════

const generateMockEvent = (): ActivityEvent => {
  const types: ActivityType[] = [
    "field_created",
    "field_updated",
    "ndvi_analysis",
    "weather_alert",
    "irrigation_scheduled",
    "task_completed",
    "diagnosis_result",
    "alert_triggered",
  ];

  const mockEvents: Record<ActivityType, Partial<ActivityEvent>> = {
    field_created: {
      title: "New Field Created",
      titleAr: "تم إنشاء حقل جديد",
      description: "Field #F-2024-001 added in Sana'a region",
      descriptionAr: "تم إضافة الحقل #F-2024-001 في منطقة صنعاء",
      severity: "success",
      service: "field-management",
    },
    field_updated: {
      title: "Field Boundary Updated",
      titleAr: "تم تحديث حدود الحقل",
      description: "Boundary adjusted for field #F-2023-045",
      descriptionAr: "تم تعديل حدود الحقل #F-2023-045",
      severity: "info",
      service: "field-management",
    },
    ndvi_analysis: {
      title: "NDVI Analysis Complete",
      titleAr: "اكتمل تحليل NDVI",
      description: "Analysis ready for 15 fields in Dhamar",
      descriptionAr: "التحليل جاهز لـ 15 حقل في ذمار",
      severity: "success",
      service: "vegetation-analysis",
    },
    weather_alert: {
      title: "Weather Warning",
      titleAr: "تحذير طقس",
      description: "Heavy rain expected in next 48 hours",
      descriptionAr: "أمطار غزيرة متوقعة خلال 48 ساعة",
      severity: "warning",
      service: "weather",
    },
    irrigation_scheduled: {
      title: "Irrigation Scheduled",
      titleAr: "تم جدولة الري",
      description: "Auto-irrigation set for Field #7 at 05:00",
      descriptionAr: "تم ضبط الري التلقائي للحقل #7 في 05:00",
      severity: "info",
      service: "irrigation-smart",
    },
    task_completed: {
      title: "Task Completed",
      titleAr: "تم إكمال المهمة",
      description: "Fertilizer application completed for wheat field",
      descriptionAr: "اكتمل تطبيق السماد لحقل القمح",
      severity: "success",
      service: "task-service",
    },
    equipment_maintenance: {
      title: "Equipment Maintenance Due",
      titleAr: "صيانة معدات مستحقة",
      description: "Tractor #T-005 maintenance in 3 days",
      descriptionAr: "صيانة الجرار #T-005 بعد 3 أيام",
      severity: "warning",
      service: "equipment-service",
    },
    user_login: {
      title: "User Login",
      titleAr: "تسجيل دخول مستخدم",
      description: "Admin user logged in from Sana'a",
      descriptionAr: "تسجيل دخول مدير من صنعاء",
      severity: "info",
      service: "user-service",
    },
    diagnosis_result: {
      title: "Crop Diagnosis Ready",
      titleAr: "تشخيص المحصول جاهز",
      description: "Disease analysis complete: No issues detected",
      descriptionAr: "اكتمل تحليل الأمراض: لا توجد مشاكل",
      severity: "success",
      service: "crop-intelligence",
    },
    alert_triggered: {
      title: "Critical Alert",
      titleAr: "تنبيه حرج",
      description: "Soil moisture critically low in Field #12",
      descriptionAr: "رطوبة التربة منخفضة بشكل حرج في الحقل #12",
      severity: "error",
      service: "alert-service",
    },
    system_event: {
      title: "System Event",
      titleAr: "حدث نظام",
      description: "Scheduled backup completed",
      descriptionAr: "اكتمل النسخ الاحتياطي المجدول",
      severity: "info",
      service: "system",
    },
  };

  const typeIndex = Math.floor(Math.random() * types.length);
  const type = types[typeIndex] ?? "system_event";
  const mockData = mockEvents[type] ?? mockEvents.system_event;

  return {
    id: `evt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    type: type as ActivityType,
    title: mockData.title || "",
    titleAr: mockData.titleAr || "",
    description: mockData.description || "",
    descriptionAr: mockData.descriptionAr || "",
    severity: mockData.severity || "info",
    service: mockData.service || "system",
    timestamp: new Date(),
  };
};

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export function RealTimeActivityFeed({
  className = "",
  maxItems = 20,
  showFilters = true,
  wsUrl,
}: RealTimeActivityFeedProps) {
  const [activities, setActivities] = useState<ActivityEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [filter, setFilter] = useState<ActivityType | "all">("all");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mockIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPausedRef = useRef(isPaused);
  isPausedRef.current = isPaused;

  /**
   * Initialize WebSocket or mock data
   * Uses refs to avoid re-render loops from callback dependencies
   */
  useEffect(() => {
    let mockFallbackTimeout: NodeJS.Timeout | null = null;

    const addEvent = (event: ActivityEvent) => {
      if (isPausedRef.current) return;
      setActivities((prev) => [event, ...prev].slice(0, maxItems));
    };

    const startMockGeneration = () => {
      // Prevent double mock generation
      if (mockIntervalRef.current) return;

      const initialEvents = Array.from({ length: 5 }, () => generateMockEvent());
      setActivities(initialEvents);

      mockIntervalRef.current = setInterval(() => {
        if (!isPausedRef.current) {
          addEvent(generateMockEvent());
        }
      }, 5000);
    };

    const connectWebSocket = () => {
      const url = wsUrl || process.env.NEXT_PUBLIC_WS_URL || `${typeof window !== "undefined" && window.location.protocol === "https:" ? "wss:" : "ws:"}//${typeof window !== "undefined" ? window.location.host : "localhost:8081"}/ws`;

      try {
        const ws = new WebSocket(url);

        ws.onopen = () => {
          setIsConnected(true);
          ws.send(
            JSON.stringify({
              type: "subscribe",
              channels: ["activities", "alerts", "tasks", "weather"],
            })
          );
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "activity") {
              addEvent({
                id: data.id || `evt-${Date.now()}`,
                type: data.activityType || "system_event",
                title: data.title || "",
                titleAr: data.titleAr || data.title || "",
                description: data.description || "",
                descriptionAr: data.descriptionAr || data.description || "",
                severity: data.severity || "info",
                service: data.service || "system",
                timestamp: new Date(data.timestamp || Date.now()),
                metadata: data.metadata,
              });
            }
          } catch {
            // Failed to parse WebSocket message - non-critical, continue
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = () => {
          setIsConnected(false);
        };

        wsRef.current = ws;
      } catch {
        startMockGeneration();
      }
    };

    connectWebSocket();

    // Fallback to mock data if no WS connection after 3 seconds
    mockFallbackTimeout = setTimeout(() => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        startMockGeneration();
      }
    }, 3000);

    return () => {
      if (mockFallbackTimeout) clearTimeout(mockFallbackTimeout);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (mockIntervalRef.current) clearInterval(mockIntervalRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [wsUrl, maxItems]);

  /**
   * Get severity badge color
   */
  const getSeverityBadge = (severity: ActivityEvent["severity"]) => {
    switch (severity) {
      case "success":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "warning":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      default:
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
    }
  };

  /**
   * Format relative time
   */
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return "الآن";
    if (diff < 3600) return `${Math.floor(diff / 60)} دقيقة`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} ساعة`;
    return date.toLocaleDateString("ar-SA");
  };

  /**
   * Filter activities
   */
  const filteredActivities =
    filter === "all"
      ? activities
      : activities.filter((a) => a.type === filter);

  return (
    <div className={`rounded-lg border bg-card ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <div>
            <h3 className="font-semibold">Live Activity</h3>
            <p className="text-xs text-muted-foreground">النشاطات المباشرة</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Connection Status */}
          <div
            className={`flex items-center gap-1 text-xs ${isConnected ? "text-green-600" : "text-gray-500"}`}
          >
            <Zap className="h-3 w-3" />
            {isConnected ? "متصل" : "غير متصل"}
          </div>

          {/* Pause/Resume */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`px-2 py-1 text-xs rounded ${isPaused ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}
          >
            {isPaused ? "متوقف" : "مباشر"}
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="p-2 border-b overflow-x-auto">
          <div className="flex gap-1">
            <button
              onClick={() => setFilter("all")}
              className={`px-2 py-1 text-xs rounded whitespace-nowrap ${filter === "all" ? "bg-primary text-primary-foreground" : "bg-muted"}`}
            >
              الكل
            </button>
            {Object.keys(ACTIVITY_CONFIG)
              .slice(0, 6)
              .map((type) => (
                <button
                  key={type}
                  onClick={() => setFilter(type as ActivityType)}
                  className={`px-2 py-1 text-xs rounded whitespace-nowrap ${filter === type ? "bg-primary text-primary-foreground" : "bg-muted"}`}
                >
                  {type.replace(/_/g, " ")}
                </button>
              ))}
          </div>
        </div>
      )}

      {/* Activity List */}
      <div className="max-h-[400px] overflow-y-auto">
        {filteredActivities.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>لا توجد نشاطات</p>
          </div>
        ) : (
          <ul className="divide-y">
            {filteredActivities.map((activity) => {
              const config = ACTIVITY_CONFIG[activity.type];
              return (
                <li
                  key={activity.id}
                  className="p-3 hover:bg-muted/50 transition-colors animate-fadeIn"
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 ${config.color}`}>{config.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium truncate">
                          {activity.titleAr}
                        </p>
                        <span
                          className={`px-1.5 py-0.5 text-xs rounded ${getSeverityBadge(activity.severity)}`}
                        >
                          {activity.service}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {activity.descriptionAr}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {formatTime(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="p-2 border-t text-center">
        <button
          onClick={() => setActivities([])}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          مسح الكل
        </button>
      </div>
    </div>
  );
}

export default RealTimeActivityFeed;
