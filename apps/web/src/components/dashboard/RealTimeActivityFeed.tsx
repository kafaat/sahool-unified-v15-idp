'use client';

/**
 * Real-Time Activity Feed — موجز النشاط المباشر
 *
 * Live activity feed showing field operations, weather alerts, tasks,
 * and irrigation events. Conceptually connected to WebSocket for real-time
 * updates. Arabic-first with relative timestamps.
 */

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Activity,
  Sprout,
  CloudRain,
  AlertTriangle,
  CheckSquare,
  Droplets,
  Bell,
  Thermometer,
  Bug,
  Wheat,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type EventType = 'field' | 'weather' | 'alert' | 'task' | 'irrigation';

export interface ActivityEvent {
  id: string;
  type: EventType;
  titleAr: string;
  titleEn: string;
  descriptionAr: string;
  descriptionEn: string;
  timestamp: Date;
  fieldId?: string;
  fieldNameAr?: string;
  severity?: 'info' | 'warning' | 'critical';
}

export interface RealTimeActivityFeedProps {
  events?: ActivityEvent[];
  maxItems?: number;
  /** WebSocket URL (conceptual -- not connected in this component) */
  wsUrl?: string;
  onEventClick?: (event: ActivityEvent) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const EVENT_CONFIG: Record<
  EventType,
  { icon: typeof Activity; labelAr: string; colorClasses: string; dotColor: string }
> = {
  field: {
    icon: Sprout,
    labelAr: 'حقل',
    colorClasses: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    dotColor: 'bg-green-500',
  },
  weather: {
    icon: CloudRain,
    labelAr: 'طقس',
    colorClasses: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    dotColor: 'bg-blue-500',
  },
  alert: {
    icon: AlertTriangle,
    labelAr: 'تنبيه',
    colorClasses: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
    dotColor: 'bg-red-500',
  },
  task: {
    icon: CheckSquare,
    labelAr: 'مهمة',
    colorClasses: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
    dotColor: 'bg-purple-500',
  },
  irrigation: {
    icon: Droplets,
    labelAr: 'ري',
    colorClasses: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400',
    dotColor: 'bg-cyan-500',
  },
};

const SEVERITY_CLASSES: Record<string, string> = {
  info: 'border-r-gray-300 dark:border-r-gray-600',
  warning: 'border-r-yellow-400 dark:border-r-yellow-500',
  critical: 'border-r-red-500 dark:border-r-red-400',
};

function relativeTimeAr(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 30) return 'الان';
  if (diffSec < 60) return `منذ ${diffSec} ثانية`;
  if (diffMin === 1) return 'منذ دقيقة';
  if (diffMin < 60) return `منذ ${diffMin} دقيقة`;
  if (diffHr === 1) return 'منذ ساعة';
  if (diffHr < 24) return `منذ ${diffHr} ساعة`;
  if (diffDay === 1) return 'منذ يوم';
  return `منذ ${diffDay} يوم`;
}

// ---------------------------------------------------------------------------
// Mock events generator
// ---------------------------------------------------------------------------

function generateMockEvents(): ActivityEvent[] {
  const now = Date.now();
  return [
    {
      id: 'evt-001',
      type: 'alert',
      titleAr: 'تنبيه: سوسة النخيل الحمراء',
      titleEn: 'Alert: Red Palm Weevil detected',
      descriptionAr: 'تم رصد اصابة محتملة في القطعة ب-٣',
      descriptionEn: 'Potential infestation detected in Block B-3',
      timestamp: new Date(now - 2 * 60 * 1000),
      fieldId: 'field-004',
      fieldNameAr: 'نخيل التراث',
      severity: 'critical',
    },
    {
      id: 'evt-002',
      type: 'irrigation',
      titleAr: 'بدء دورة الري',
      titleEn: 'Irrigation cycle started',
      descriptionAr: 'تم تشغيل نظام الري بالتنقيط - ٢٥ مم',
      descriptionEn: 'Drip irrigation system activated - 25mm',
      timestamp: new Date(now - 5 * 60 * 1000),
      fieldId: 'field-001',
      fieldNameAr: 'مزرعة الراشد',
      severity: 'info',
    },
    {
      id: 'evt-003',
      type: 'weather',
      titleAr: 'تحذير: موجة حرارة',
      titleEn: 'Warning: Heat wave approaching',
      descriptionAr: 'درجة الحرارة المتوقعة ٤٥°م خلال ٤٨ ساعة',
      descriptionEn: 'Expected temperature 45C in 48 hours',
      timestamp: new Date(now - 15 * 60 * 1000),
      severity: 'warning',
    },
    {
      id: 'evt-004',
      type: 'field',
      titleAr: 'تحديث NDVI',
      titleEn: 'NDVI update received',
      descriptionAr: 'قراءة جديدة: ٠.٧٢ - تحسن بنسبة ٥٪',
      descriptionEn: 'New reading: 0.72 - 5% improvement',
      timestamp: new Date(now - 30 * 60 * 1000),
      fieldId: 'field-001',
      fieldNameAr: 'مزرعة الراشد',
      severity: 'info',
    },
    {
      id: 'evt-005',
      type: 'task',
      titleAr: 'اكتمال مهمة التسميد',
      titleEn: 'Fertilization task completed',
      descriptionAr: 'تم تطبيق يوريا ٤٦٪ بمعدل ٤٦ كجم/هـ',
      descriptionEn: 'Applied Urea 46% at 46 kg/ha',
      timestamp: new Date(now - 45 * 60 * 1000),
      fieldId: 'field-003',
      fieldNameAr: 'حقول الشروق',
      severity: 'info',
    },
    {
      id: 'evt-006',
      type: 'irrigation',
      titleAr: 'انتهاء دورة الري',
      titleEn: 'Irrigation cycle completed',
      descriptionAr: 'تم ري ٣.٨ هكتار - استهلاك ٩٥٠ م٣',
      descriptionEn: '3.8 ha irrigated - 950 m3 consumed',
      timestamp: new Date(now - 1.5 * 3600 * 1000),
      fieldId: 'field-002',
      fieldNameAr: 'الوادي الاخضر',
      severity: 'info',
    },
    {
      id: 'evt-007',
      type: 'alert',
      titleAr: 'نقص نيتروجين',
      titleEn: 'Nitrogen deficiency detected',
      descriptionAr: 'مستوى النيتروجين ١٨ جزء/مليون - اقل من الحد ٢٥',
      descriptionEn: 'Nitrogen level 18ppm - below threshold 25',
      timestamp: new Date(now - 2 * 3600 * 1000),
      fieldId: 'field-005',
      fieldNameAr: 'النور الزراعية',
      severity: 'warning',
    },
    {
      id: 'evt-008',
      type: 'weather',
      titleAr: 'تحديث بيانات الطقس',
      titleEn: 'Weather data updated',
      descriptionAr: 'الحرارة ٣٢°م | الرطوبة ٤٥٪ | رياح ١٢ كم/س',
      descriptionEn: 'Temp 32C | Humidity 45% | Wind 12 km/h',
      timestamp: new Date(now - 3 * 3600 * 1000),
      severity: 'info',
    },
    {
      id: 'evt-009',
      type: 'field',
      titleAr: 'رصد حشرات',
      titleEn: 'Pest scouting completed',
      descriptionAr: 'لم يتم رصد اصابات في حقل الذرة',
      descriptionEn: 'No infestations found in corn field',
      timestamp: new Date(now - 5 * 3600 * 1000),
      fieldId: 'field-007',
      fieldNameAr: 'حقول سبأ',
      severity: 'info',
    },
    {
      id: 'evt-010',
      type: 'task',
      titleAr: 'جدولة حصاد',
      titleEn: 'Harvest scheduled',
      descriptionAr: 'تم جدولة حصاد القمح - الاسبوع القادم',
      descriptionEn: 'Wheat harvest scheduled - next week',
      timestamp: new Date(now - 8 * 3600 * 1000),
      fieldId: 'field-001',
      fieldNameAr: 'مزرعة الراشد',
      severity: 'info',
    },
  ];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function RealTimeActivityFeed({
  events: externalEvents,
  maxItems = 20,
  onEventClick,
}: RealTimeActivityFeedProps) {
  const [events, setEvents] = useState<ActivityEvent[]>(
    () => externalEvents ?? generateMockEvents()
  );
  const feedRef = useRef<HTMLDivElement>(null);
  const [isLive, setIsLive] = useState(true);

  // Sync external events if provided
  useEffect(() => {
    if (externalEvents) {
      setEvents(externalEvents.slice(0, maxItems));
    }
  }, [externalEvents, maxItems]);

  // Simulated live event injection (demo only, when no external events)
  useEffect(() => {
    if (externalEvents || !isLive) return;

    const demoEvents: Omit<ActivityEvent, 'id' | 'timestamp'>[] = [
      {
        type: 'irrigation',
        titleAr: 'قراءة رطوبة التربة',
        titleEn: 'Soil moisture reading',
        descriptionAr: 'رطوبة التربة ٣٨٪ - ضمن النطاق الطبيعي',
        descriptionEn: 'Soil moisture 38% - within normal range',
        fieldNameAr: 'مزرعة الراشد',
        severity: 'info',
      },
      {
        type: 'weather',
        titleAr: 'تحديث سرعة الرياح',
        titleEn: 'Wind speed update',
        descriptionAr: 'سرعة الرياح ارتفعت الى ٢٠ كم/س',
        descriptionEn: 'Wind speed increased to 20 km/h',
        severity: 'info',
      },
      {
        type: 'field',
        titleAr: 'صورة قمر صناعي جديدة',
        titleEn: 'New satellite image',
        descriptionAr: 'صورة Sentinel-2 متاحة للتحليل',
        descriptionEn: 'Sentinel-2 image available for analysis',
        severity: 'info',
      },
    ];

    const interval = setInterval(() => {
      const template = demoEvents[Math.floor(Math.random() * demoEvents.length)];
      const newEvent: ActivityEvent = {
        ...template,
        id: `evt-live-${Date.now()}`,
        timestamp: new Date(),
      };

      setEvents((prev) => [newEvent, ...prev].slice(0, maxItems));
    }, 15000);

    return () => clearInterval(interval);
  }, [externalEvents, isLive, maxItems]);

  // Auto-scroll to top on new event
  useEffect(() => {
    if (feedRef.current && isLive) {
      feedRef.current.scrollTop = 0;
    }
  }, [events.length, isLive]);

  // Sorted by timestamp desc
  const sortedEvents = useMemo(
    () => [...events].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime()),
    [events]
  );

  const toggleLive = useCallback(() => setIsLive((v) => !v), []);

  return (
    <div
      dir="rtl"
      className="flex h-full flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 bg-gray-50 px-5 py-3 dark:border-gray-700 dark:bg-gray-900/50">
        <div className="flex items-center gap-2">
          <Bell className="h-5 w-5 text-emerald-600" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            موجز النشاط المباشر
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleLive}
            className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              isLive
                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isLive ? 'animate-pulse bg-green-500' : 'bg-gray-400'
              }`}
            />
            {isLive ? 'مباشر' : 'متوقف'}
          </button>
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {sortedEvents.length} حدث
          </span>
        </div>
      </div>

      {/* Feed */}
      <div
        ref={feedRef}
        className="flex-1 overflow-y-auto"
        style={{ maxHeight: 520 }}
      >
        {sortedEvents.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-gray-400 dark:text-gray-500">
            لا توجد احداث
          </div>
        ) : (
          <div className="divide-y divide-gray-50 dark:divide-gray-700/50">
            {sortedEvents.map((event) => {
              const config = EVENT_CONFIG[event.type];
              const Icon = config.icon;
              const severityClass =
                SEVERITY_CLASSES[event.severity ?? 'info'];

              return (
                <div
                  key={event.id}
                  onClick={() => onEventClick?.(event)}
                  className={`border-r-4 px-4 py-3 transition-colors ${severityClass} ${
                    onEventClick
                      ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30'
                      : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div
                      className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${config.colorClasses}`}
                    >
                      <Icon className="h-4 w-4" />
                    </div>

                    {/* Content */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {event.titleAr}
                        </p>
                        <span className="shrink-0 text-xs text-gray-400 dark:text-gray-500">
                          {relativeTimeAr(event.timestamp)}
                        </span>
                      </div>
                      <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                        {event.descriptionAr}
                      </p>
                      <div className="mt-1.5 flex items-center gap-2">
                        <span
                          className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-medium ${config.colorClasses}`}
                        >
                          {config.labelAr}
                        </span>
                        {event.fieldNameAr && (
                          <span className="text-[10px] text-gray-400 dark:text-gray-500">
                            {event.fieldNameAr}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
