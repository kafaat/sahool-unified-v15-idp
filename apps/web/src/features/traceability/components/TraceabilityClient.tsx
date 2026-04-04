'use client';

/**
 * SAHOOL Supply Chain Traceability Client
 * تتبع سلسلة التوريد
 */

import React, { useState } from 'react';
import {
  QrCode,
  Package,
  Truck,
  CheckCircle,
  Clock,
  MapPin,
  Plus,
  Search,
  ArrowLeft,
  Scan,
} from 'lucide-react';

interface TraceabilityBatch {
  id: string;
  batchCode: string;
  product: string;
  productAr: string;
  origin: string;
  originAr: string;
  quantity: number;
  unit: string;
  unitAr: string;
  status: 'harvested' | 'processing' | 'in-transit' | 'delivered';
  statusAr: string;
  harvestDate: string;
  destination: string;
  destinationAr: string;
  qrGenerated: boolean;
  events: TraceEvent[];
}

interface TraceEvent {
  id: string;
  type: string;
  typeAr: string;
  location: string;
  locationAr: string;
  timestamp: string;
  actor: string;
  actorAr: string;
  notes: string;
  notesAr: string;
}

const MOCK_BATCHES: TraceabilityBatch[] = [
  {
    id: 'TB-001', batchCode: 'SAH-2026-QMH-0412', product: 'Wheat', productAr: 'قمح', origin: 'Field F-003', originAr: 'حقل F-003', quantity: 12.5, unit: 'ton', unitAr: 'طن', status: 'in-transit', statusAr: 'قيد النقل', harvestDate: '2026-03-28', destination: 'Riyadh Mill', destinationAr: 'مطحنة الرياض', qrGenerated: true,
    events: [
      { id: 'E1', type: 'harvest', typeAr: 'حصاد', location: 'Field F-003', locationAr: 'حقل F-003', timestamp: '2026-03-28T06:00:00Z', actor: 'Farm Team A', actorAr: 'فريق المزرعة أ', notes: 'Machine harvest, moisture 12%', notesAr: 'حصاد آلي، رطوبة 12%' },
      { id: 'E2', type: 'quality-check', typeAr: 'فحص جودة', location: 'Storage Unit 2', locationAr: 'وحدة تخزين 2', timestamp: '2026-03-29T10:30:00Z', actor: 'Inspector Ali', actorAr: 'المفتش علي', notes: 'Grade A, protein 13.5%', notesAr: 'درجة أ، بروتين 13.5%' },
      { id: 'E3', type: 'dispatch', typeAr: 'شحن', location: 'Farm Gate', locationAr: 'بوابة المزرعة', timestamp: '2026-04-01T08:00:00Z', actor: 'Logistics Co.', actorAr: 'شركة النقل', notes: 'Truck #TRK-445', notesAr: 'شاحنة #TRK-445' },
    ],
  },
  {
    id: 'TB-002', batchCode: 'SAH-2026-TMR-0405', product: 'Dates (Sukkari)', productAr: 'تمور سكري', origin: 'Palm Grove PG-01', originAr: 'بستان نخيل PG-01', quantity: 2.8, unit: 'ton', unitAr: 'طن', status: 'delivered', statusAr: 'تم التسليم', harvestDate: '2026-03-15', destination: 'Export Terminal', destinationAr: 'محطة التصدير', qrGenerated: true,
    events: [
      { id: 'E4', type: 'harvest', typeAr: 'حصاد', location: 'Palm Grove PG-01', locationAr: 'بستان نخيل PG-01', timestamp: '2026-03-15T05:30:00Z', actor: 'Palm Team', actorAr: 'فريق النخيل', notes: 'Hand-picked, Rutab stage', notesAr: 'قطف يدوي، مرحلة الرطب' },
      { id: 'E5', type: 'packaging', typeAr: 'تعبئة', location: 'Packing House', locationAr: 'مصنع التعبئة', timestamp: '2026-03-17T09:00:00Z', actor: 'Packing Line 3', actorAr: 'خط تعبئة 3', notes: '1400 boxes packed', notesAr: 'تم تعبئة 1400 صندوق' },
    ],
  },
  {
    id: 'TB-003', batchCode: 'SAH-2026-TMA-0401', product: 'Tomato', productAr: 'طماطم', origin: 'Greenhouse GH-05', originAr: 'بيت محمي GH-05', quantity: 0.8, unit: 'ton', unitAr: 'طن', status: 'processing', statusAr: 'قيد المعالجة', harvestDate: '2026-04-02', destination: 'Local Market', destinationAr: 'السوق المحلي', qrGenerated: false,
    events: [
      { id: 'E6', type: 'harvest', typeAr: 'حصاد', location: 'Greenhouse GH-05', locationAr: 'بيت محمي GH-05', timestamp: '2026-04-02T07:00:00Z', actor: 'Greenhouse Team', actorAr: 'فريق البيوت المحمية', notes: 'Cherry tomato, ripe stage', notesAr: 'طماطم شيري، مرحلة النضج' },
    ],
  },
  {
    id: 'TB-004', batchCode: 'SAH-2026-SHR-0330', product: 'Barley', productAr: 'شعير', origin: 'Field F-009', originAr: 'حقل F-009', quantity: 8.0, unit: 'ton', unitAr: 'طن', status: 'harvested', statusAr: 'تم الحصاد', harvestDate: '2026-03-30', destination: 'Feed Factory', destinationAr: 'مصنع الأعلاف', qrGenerated: false,
    events: [
      { id: 'E7', type: 'harvest', typeAr: 'حصاد', location: 'Field F-009', locationAr: 'حقل F-009', timestamp: '2026-03-30T06:30:00Z', actor: 'Farm Team B', actorAr: 'فريق المزرعة ب', notes: 'Combine harvest, 11% moisture', notesAr: 'حصاد بالحصادة، رطوبة 11%' },
    ],
  },
];

const statusColors: Record<string, string> = {
  harvested: 'bg-amber-100 text-amber-700',
  processing: 'bg-blue-100 text-blue-700',
  'in-transit': 'bg-purple-100 text-purple-700',
  delivered: 'bg-green-100 text-green-700',
};

const statusIcons: Record<string, React.ReactNode> = {
  harvested: <Package className="w-4 h-4" />,
  processing: <Clock className="w-4 h-4" />,
  'in-transit': <Truck className="w-4 h-4" />,
  delivered: <CheckCircle className="w-4 h-4" />,
};

export default function TraceabilityClient() {
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);
  const selected = MOCK_BATCHES.find(b => b.id === selectedBatch);

  const stats = {
    total: MOCK_BATCHES.length,
    inTransit: MOCK_BATCHES.filter(b => b.status === 'in-transit').length,
    delivered: MOCK_BATCHES.filter(b => b.status === 'delivered').length,
    qrCodes: MOCK_BATCHES.filter(b => b.qrGenerated).length,
  };

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
          <button onClick={() => setSelectedBatch(null)} className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 mb-4">
            <ArrowLeft className="w-4 h-4" />
            العودة للقائمة
          </button>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">{selected.productAr} - {selected.batchCode}</h2>
            <p className="text-sm text-gray-500 mt-1">{selected.originAr} &rarr; {selected.destinationAr}</p>
          </div>
          {/* Events Timeline */}
          <h3 className="text-lg font-semibold text-gray-800 mb-4">سجل الأحداث</h3>
          <div className="relative pr-6 border-r-2 border-blue-200 space-y-6">
            {selected.events.map((event, i) => (
              <div key={event.id} className="relative">
                <div className="absolute -right-[33px] top-1 w-4 h-4 rounded-full bg-blue-600 border-2 border-white" />
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-gray-900">{event.typeAr}</span>
                    <span className="text-xs text-gray-500">{new Date(event.timestamp).toLocaleDateString('ar-SA')}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">
                    <MapPin className="w-3 h-3 inline ml-1" />
                    {event.locationAr}
                  </p>
                  <p className="text-sm text-gray-700">{event.notesAr}</p>
                  <p className="text-xs text-gray-400 mt-1">{event.actorAr}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border-2 border-gray-200">
          <div className="p-6">
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">رمز الدفعة</th>
                  <th className="pb-3 pr-4 font-medium">المنتج</th>
                  <th className="pb-3 pr-4 font-medium">المصدر</th>
                  <th className="pb-3 pr-4 font-medium">الكمية</th>
                  <th className="pb-3 pr-4 font-medium">الحالة</th>
                  <th className="pb-3 pr-4 font-medium">الوجهة</th>
                  <th className="pb-3 pr-4 font-medium">QR</th>
                  <th className="pb-3 font-medium">إجراءات</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_BATCHES.map(batch => (
                  <tr key={batch.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4 text-sm font-mono font-semibold text-gray-900">{batch.batchCode}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{batch.productAr}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{batch.originAr}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{batch.quantity} {batch.unitAr}</td>
                    <td className="py-4 pr-4">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${statusColors[batch.status]}`}>
                        {statusIcons[batch.status]}
                        {batch.statusAr}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{batch.destinationAr}</td>
                    <td className="py-4 pr-4">
                      {batch.qrGenerated ? (
                        <QrCode className="w-5 h-5 text-green-600" />
                      ) : (
                        <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">إنشاء</button>
                      )}
                    </td>
                    <td className="py-4">
                      <button onClick={() => setSelectedBatch(batch.id)} className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        تتبع
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
