'use client';

import React, { useEffect, useState } from 'react';
import { wsClient, TimelineEvent, getEventIcon, getEventColor, formatEventType } from '@/lib/ws';
import { SkeletonEventItem } from './ui/Skeleton';

// Sample events for demo mode
const SAMPLE_EVENTS: TimelineEvent[] = [
  {
    event_id: 'evt_001',
    event_type: 'task_created',
    aggregate_id: 'task_001',
    tenant_id: 'tenant_1',
    timestamp: new Date().toISOString(),
    payload: { title: 'ري الطماطم', field_id: 'field_001' },
  },
  {
    event_id: 'evt_002',
    event_type: 'weather_alert_issued',
    aggregate_id: 'alert_001',
    tenant_id: 'tenant_1',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    payload: { type: 'موجة حارة', severity: 'warning', location: 'صنعاء' },
  },
  {
    event_id: 'evt_003',
    event_type: 'image_diagnosed',
    aggregate_id: 'diag_001',
    tenant_id: 'tenant_1',
    timestamp: new Date(Date.now() - 600000).toISOString(),
    payload: { disease_detected: true, confidence: 0.87, disease: 'البياض الدقيقي' },
  },
  {
    event_id: 'evt_004',
    event_type: 'task_completed',
    aggregate_id: 'task_005',
    tenant_id: 'tenant_1',
    timestamp: new Date(Date.now() - 900000).toISOString(),
    payload: { title: 'تقليم القات', field_id: 'field_003' },
  },
  {
    event_id: 'evt_005',
    event_type: 'ndvi_processed',
    aggregate_id: 'ndvi_001',
    tenant_id: 'tenant_1',
    timestamp: new Date(Date.now() - 1200000).toISOString(),
    payload: { field_id: 'field_002', ndvi: 0.45, status: 'warning' },
  },
];

function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diff = now.getTime() - then.getTime();

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (seconds < 60) return 'الآن';
  if (minutes < 60) return `منذ ${minutes} دقيقة`;
  if (hours < 24) return `منذ ${hours} ساعة`;
  return then.toLocaleDateString('ar-YE');
}

const EventCard = React.memo<{ event: TimelineEvent }>(function EventCard({ event }) {
  const icon = getEventIcon(event.event_type);
  const colorClass = getEventColor(event.event_type);
  const label = formatEventType(event.event_type);

  return (
    <div className={`p-3 rounded-lg border ${colorClass} transition-all hover:shadow-sm`} role="article" aria-label={`حدث: ${label}`}>
      <div className="flex items-start gap-3">
        {/* Icon */}
        <span className="text-xl" aria-hidden="true">{icon}</span>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm font-medium text-gray-800">{label}</span>
            <span className="text-xs text-gray-400">{formatTimeAgo(event.timestamp)}</span>
          </div>

          {/* Payload details */}
          <div className="mt-1 text-xs text-gray-500">
            {event.event_type === 'task_created' && (
              <span>📋 {(event.payload as any).title}</span>
            )}
            {event.event_type === 'task_completed' && (
              <span>✅ {(event.payload as any).title}</span>
            )}
            {event.event_type === 'weather_alert_issued' && (
              <span>⚠️ {(event.payload as any).type} - {(event.payload as any).location}</span>
            )}
            {event.event_type === 'image_diagnosed' && (
              <span>
                {(event.payload as any).disease_detected ? '🔴' : '🟢'}
                {' '}
                {(event.payload as any).disease || 'لا يوجد مرض'}
                {' '}
                ({Math.round((event.payload as any).confidence * 100)}%)
              </span>
            )}
            {event.event_type === 'ndvi_processed' && (
              <span>
                🛰️ NDVI: {(event.payload as any).ndvi}
                {' '}
                <span className={`px-1 rounded ${
                  (event.payload as any).status === 'healthy' ? 'bg-green-100 text-green-700' :
                  (event.payload as any).status === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {(event.payload as any).status === 'healthy' ? 'صحي' :
                   (event.payload as any).status === 'warning' ? 'تحذير' : 'حرج'}
                </span>
              </span>
            )}
          </div>

          {/* Aggregate ID */}
          <div className="mt-1 text-xs text-gray-300 font-mono truncate">
            {event.aggregate_id}
          </div>
        </div>
      </div>
    </div>
  );
});

interface EventTimelineProps {
  tenantId?: string;
}

export const EventTimeline = React.memo<EventTimelineProps>(function EventTimeline({ tenantId }) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set up WebSocket connection
    const unsubscribeEvent = wsClient.onEvent((event) => {
      setEvents((prev) => [event, ...prev].slice(0, 50));
    });

    const unsubscribeConnection = wsClient.onConnection((isConnected) => {
      setConnected(isConnected);
    });

    // Try to connect
    wsClient.connect();

    // Initialize with sample data after a short delay
    const timeout = setTimeout(() => {
      setEvents(SAMPLE_EVENTS);
      setLoading(false);
    }, 500);

    // Simulate new events for demo mode
    const interval = setInterval(() => {
      if (!wsClient.isConnected) {
        const eventTypes = ['task_created', 'task_completed', 'weather_alert_issued', 'ndvi_processed', 'image_diagnosed'] as const;
        const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)] ?? 'task_created';

        const newEvent: TimelineEvent = {
          event_id: `evt_${Date.now()}`,
          event_type: randomType,
          aggregate_id: `agg_${Math.random().toString(36).substr(2, 9)}`,
          tenant_id: tenantId || 'tenant_1',
          timestamp: new Date().toISOString(),
          payload: randomType === 'task_created'
            ? { title: 'مهمة جديدة', field_id: 'field_001' }
            : randomType === 'ndvi_processed'
            ? { field_id: 'field_002', ndvi: (Math.random() * 0.5 + 0.3).toFixed(2), status: Math.random() > 0.5 ? 'healthy' : 'warning' }
            : { title: 'حدث جديد' },
        };
        setEvents((prev) => [newEvent, ...prev].slice(0, 50));
      }
    }, 20000); // Every 20 seconds

    return () => {
      clearTimeout(timeout);
      clearInterval(interval);
      unsubscribeEvent();
      unsubscribeConnection();
      wsClient.disconnect();
    };
  }, [tenantId]);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <SkeletonEventItem key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Connection status */}
      <div className={`flex items-center gap-2 text-xs px-2 py-1 rounded-full w-fit ${
        connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
      }`}>
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></span>
        {connected ? 'متصل بالأحداث المباشرة' : 'وضع العرض التوضيحي'}
      </div>

      {/* Events list */}
      {events.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <span className="text-4xl">📊</span>
          <p className="mt-2">لا توجد أحداث</p>
        </div>
      ) : (
        <div className="space-y-2">
          {events.map((event) => (
            <EventCard key={event.event_id} event={event} />
          ))}
        </div>
      )}
    </div>
  );
});

export default EventTimeline;
