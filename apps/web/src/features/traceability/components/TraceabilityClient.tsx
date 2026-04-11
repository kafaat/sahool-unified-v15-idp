'use client';

/**
 * SAHOOL Supply Chain Traceability Client
 * تتبع سلسلة التوريد
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  QrCode,
  Package,
  Truck,
  CheckCircle,
  Clock,
  MapPin,
  Plus,
  ArrowLeft,
  Scan,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { traceabilityApi } from '../api';
import type { TraceabilityBatch, TraceabilityEvent, TraceabilityBatchStatus } from '../api';

/**
 * Strip bidi/control/zero-width characters from user-supplied strings
 * before rendering to prevent visual spoofing of batch codes and locations.
 */
function sanitizeDisplay(input: string | null | undefined): string {
  if (!input) return '';
  // eslint-disable-next-line no-control-regex
  return String(input).replace(/[\u0000-\u001F\u007F\u200B-\u200F\u202A-\u202E\u2066-\u2069]/g, '').slice(0, 300);
}

// ---------------------------------------------------------------------------
// Query Keys
// ---------------------------------------------------------------------------

const traceabilityKeys = {
  all: ['traceability'] as const,
  batches: () => [...traceabilityKeys.all, 'batches'] as const,
  events: (batchId?: string) => [...traceabilityKeys.all, 'events', batchId] as const,
  batch: (id: string) => [...traceabilityKeys.all, 'batch', id] as const,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const statusColors: Record<TraceabilityBatchStatus, string> = {
  harvested: 'bg-amber-100 text-amber-700',
  processing: 'bg-blue-100 text-blue-700',
  in_transit: 'bg-purple-100 text-purple-700',
  delivered: 'bg-green-100 text-green-700',
  recalled: 'bg-red-100 text-red-700',
};

const statusLabels: Record<TraceabilityBatchStatus, string> = {
  harvested: 'تم الحصاد',
  processing: 'قيد المعالجة',
  in_transit: 'قيد النقل',
  delivered: 'تم التسليم',
  recalled: 'تم الاسترجاع',
};

const statusIcons: Record<TraceabilityBatchStatus, React.ReactNode> = {
  harvested: <Package className="w-4 h-4" />,
  processing: <Clock className="w-4 h-4" />,
  in_transit: <Truck className="w-4 h-4" />,
  delivered: <CheckCircle className="w-4 h-4" />,
  recalled: <AlertTriangle className="w-4 h-4" />,
};

const eventLabels: Record<string, string> = {
  harvest: 'حصاد',
  processing: 'معالجة',
  quality_check: 'فحص جودة',
  transport: 'نقل',
  delivery: 'تسليم',
};

// ---------------------------------------------------------------------------
// Events Sub-component
// ---------------------------------------------------------------------------

function BatchEvents({ batchId }: { batchId: string }) {
  const { data: events, isLoading } = useQuery({
    queryKey: traceabilityKeys.events(batchId),
    queryFn: () => traceabilityApi.getEvents(batchId),
    enabled: !!batchId,
  });

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm py-4">
        <Loader2 className="w-4 h-4 animate-spin" />
        جاري تحميل الأحداث...
      </div>
    );
  }

  if (!events || events.length === 0) {
    return <p className="text-sm text-gray-500 py-4">لا توجد أحداث مسجلة لهذه الدفعة</p>;
  }

  return (
    <div className="relative pr-6 border-r-2 border-blue-200 space-y-6">
      {events.map((event: TraceabilityEvent) => (
        <div key={event.id} className="relative">
          <div className="absolute -right-[33px] top-1 w-4 h-4 rounded-full bg-blue-600 border-2 border-white" />
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-900">
                {eventLabels[event.eventType] ?? event.eventType}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(event.timestamp).toLocaleDateString('ar-SA')}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-1">
              <MapPin className="w-3 h-3 inline ml-1" />
              {sanitizeDisplay(event.location)}
            </p>
            <p className="text-xs text-gray-400 mt-1">{sanitizeDisplay(event.actor)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function TraceabilityClient() {
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);

  const {
    data: batches,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: traceabilityKeys.batches(),
    queryFn: () => traceabilityApi.getBatches(),
    staleTime: 1000 * 60 * 5,
  });

  const records = batches ?? [];
  const selected = records.find((b) => b.id === selectedBatch);

  const stats = {
    total: records.length,
    inTransit: records.filter((b) => b.status === 'in_transit').length,
    delivered: records.filter((b) => b.status === 'delivered').length,
    qrCodes: records.filter((b) => !!b.qrCode).length,
  };

  // ── Loading State ──────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
          <p className="text-gray-600 text-sm">جاري تحميل بيانات التتبع...</p>
          <p className="text-gray-400 text-xs">Loading traceability data...</p>
        </div>
      </div>
    );
  }

  // ── Error State ────────────────────────────────────────────────────
  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3 max-w-md">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-gray-900 font-semibold">تعذر تحميل بيانات التتبع</p>
          <p className="text-gray-500 text-sm">
            {error instanceof Error ? error.message : 'Failed to load traceability data'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">تتبع سلسلة التوريد</h1>
            <p className="text-gray-600 mt-1">Supply Chain Traceability</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-5 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-semibold">
              <Scan className="w-5 h-5" />
              <span>مسح QR</span>
            </button>
            <button className="flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
              <Plus className="w-5 h-5" />
              <span>دفعة جديدة</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Package className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">إجمالي الدفعات</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Truck className="w-5 h-5 text-purple-600" />
            <p className="text-sm text-gray-600">قيد النقل</p>
          </div>
          <p className="text-3xl font-bold text-purple-600">{stats.inTransit}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">تم التسليم</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{stats.delivered}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <QrCode className="w-5 h-5 text-gray-700" />
            <p className="text-sm text-gray-600">رموز QR مولدة</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.qrCodes}</p>
        </div>
      </div>

      {/* Content */}
      {selectedBatch && selected ? (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <button
            onClick={() => setSelectedBatch(null)}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            العودة للقائمة
          </button>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">
              {sanitizeDisplay(selected.cropType)} - {sanitizeDisplay(selected.batchCode)}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {sanitizeDisplay(selected.fieldId) || '-'} &rarr;{' '}
              {statusLabels[selected.status] ?? sanitizeDisplay(selected.status)}
            </p>
          </div>
          {/* Events Timeline */}
          <h3 className="text-lg font-semibold text-gray-800 mb-4">سجل الأحداث</h3>
          <BatchEvents batchId={selected.id} />
        </div>
      ) : (
        <div className="bg-white rounded-xl border-2 border-gray-200">
          <div className="p-6">
            {records.length === 0 ? (
              <div className="text-center py-10 text-gray-500">
                <p className="text-sm">لا توجد دفعات مسجلة حالياً</p>
                <p className="text-xs text-gray-400 mt-1">No batches found</p>
              </div>
            ) : (
              <table className="w-full text-right">
                <thead>
                  <tr className="border-b border-gray-200 text-sm text-gray-500">
                    <th className="pb-3 pr-4 font-medium">رمز الدفعة</th>
                    <th className="pb-3 pr-4 font-medium">المنتج</th>
                    <th className="pb-3 pr-4 font-medium">المصدر</th>
                    <th className="pb-3 pr-4 font-medium">الكمية</th>
                    <th className="pb-3 pr-4 font-medium">الحالة</th>
                    <th className="pb-3 pr-4 font-medium">QR</th>
                    <th className="pb-3 font-medium">إجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((batch: TraceabilityBatch) => (
                    <tr key={batch.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 pr-4 text-sm font-mono font-semibold text-gray-900">
                        {sanitizeDisplay(batch.batchCode)}
                      </td>
                      <td className="py-4 pr-4 text-sm text-gray-700">{sanitizeDisplay(batch.cropType)}</td>
                      <td className="py-4 pr-4 text-sm text-gray-700">{sanitizeDisplay(batch.fieldId) || '-'}</td>
                      <td className="py-4 pr-4 text-sm text-gray-700">
                        {Number.isFinite(batch.quantity) ? batch.quantity : 0} {sanitizeDisplay(batch.unit)}
                      </td>
                      <td className="py-4 pr-4">
                        <span
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${statusColors[batch.status] ?? 'bg-gray-100 text-gray-700'}`}
                        >
                          {statusIcons[batch.status]}
                          {statusLabels[batch.status] ?? sanitizeDisplay(batch.status)}
                        </span>
                      </td>
                      <td className="py-4 pr-4">
                        {batch.qrCode ? (
                          <QrCode className="w-5 h-5 text-green-600" />
                        ) : (
                          <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
                            إنشاء
                          </button>
                        )}
                      </td>
                      <td className="py-4">
                        <button
                          onClick={() => setSelectedBatch(batch.id)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          تتبع
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
