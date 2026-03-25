'use client';

import React, { useState, useMemo } from 'react';
import {
  Droplet,
  Search,
  Plus,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
  Wind,
} from 'lucide-react';

type SprayStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'weather_hold';
type SprayType = 'pesticide' | 'herbicide' | 'fungicide' | 'fertilizer' | 'growth_regulator';

interface SprayRecord {
  id: string;
  fieldId: string;
  fieldName: string;
  type: SprayType;
  productName: string;
  productNameAr: string;
  dosage: string;
  status: SprayStatus;
  scheduledAt: string;
  completedAt?: string;
  windSpeed?: number;
  humidity?: number;
  applicator?: string;
}

const mockSprayRecords: SprayRecord[] = [
  {
    id: '1',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    type: 'fungicide',
    productName: 'Propiconazole',
    productNameAr: 'بروبيكونازول',
    dosage: '0.5 لتر/هكتار',
    status: 'scheduled',
    scheduledAt: '2025-01-26T06:00:00Z',
    windSpeed: 8,
    humidity: 65,
  },
  {
    id: '2',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    type: 'herbicide',
    productName: '2,4-D Amine',
    productNameAr: '2,4-D أمين',
    dosage: '1.5 لتر/هكتار',
    status: 'weather_hold',
    scheduledAt: '2025-01-25T07:00:00Z',
    windSpeed: 25,
    humidity: 45,
  },
  {
    id: '3',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    type: 'pesticide',
    productName: 'Cypermethrin',
    productNameAr: 'سايبرمثرين',
    dosage: '0.3 لتر/هكتار',
    status: 'completed',
    scheduledAt: '2025-01-24T06:00:00Z',
    completedAt: '2025-01-24T08:30:00Z',
    applicator: 'أحمد محمد',
  },
  {
    id: '4',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    type: 'fertilizer',
    productName: 'Foliar NPK',
    productNameAr: 'سماد ورقي NPK',
    dosage: '3 كجم/هكتار',
    status: 'in_progress',
    scheduledAt: '2025-01-25T05:00:00Z',
    applicator: 'محمد علي',
  },
  {
    id: '5',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    type: 'growth_regulator',
    productName: 'Gibberellic Acid',
    productNameAr: 'حمض الجبريليك',
    dosage: '10 جم/هكتار',
    status: 'scheduled',
    scheduledAt: '2025-01-27T06:00:00Z',
    windSpeed: 5,
    humidity: 70,
  },
];

const sprayTypes: Record<SprayType, { label: string; labelAr: string; color: string }> = {
  pesticide: { label: 'Pesticide', labelAr: 'مبيد حشري', color: 'bg-red-100 text-red-800' },
  herbicide: { label: 'Herbicide', labelAr: 'مبيد أعشاب', color: 'bg-orange-100 text-orange-800' },
  fungicide: { label: 'Fungicide', labelAr: 'مبيد فطري', color: 'bg-purple-100 text-purple-800' },
  fertilizer: { label: 'Fertilizer', labelAr: 'سماد ورقي', color: 'bg-green-100 text-green-800' },
  growth_regulator: {
    label: 'Growth Regulator',
    labelAr: 'منظم نمو',
    color: 'bg-blue-100 text-blue-800',
  },
};

export default function SprayClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<SprayStatus | 'all'>('all');

  const filteredRecords = useMemo(() => {
    return mockSprayRecords.filter((record) => {
      const matchesSearch =
        !searchTerm ||
        record.fieldName.includes(searchTerm) ||
        record.productNameAr.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || record.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [searchTerm, statusFilter]);

  const getStatusBadge = (status: SprayStatus) => {
    const styles = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800',
      weather_hold: 'bg-red-100 text-red-800',
    };
    const labels = {
      scheduled: 'مجدول',
      in_progress: 'جاري',
      completed: 'مكتمل',
      cancelled: 'ملغي',
      weather_hold: 'تأجيل (طقس)',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const scheduledCount = mockSprayRecords.filter((r) => r.status === 'scheduled').length;
  const weatherHoldCount = mockSprayRecords.filter((r) => r.status === 'weather_hold').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تخطيط الرش</h1>
          <p className="text-gray-500 mt-1">Spray Planning</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700">
          <Plus className="w-4 h-4" />
          <span>جدولة رش</span>
        </button>
      </div>

      {/* Weather Alert */}
      {weatherHoldCount > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Wind className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه: {weatherHoldCount} عملية رش مؤجلة بسبب ظروف الطقس
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مجدول</div>
              <div className="text-xl font-bold text-blue-600">{scheduledCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">جاري</div>
              <div className="text-xl font-bold text-yellow-600">
                {mockSprayRecords.filter((r) => r.status === 'in_progress').length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مكتمل</div>
              <div className="text-xl font-bold text-green-600">
                {mockSprayRecords.filter((r) => r.status === 'completed').length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تأجيل (طقس)</div>
              <div className="text-xl font-bold text-red-600">{weatherHoldCount}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن حقل أو منتج..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as SprayStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="scheduled">مجدول</option>
          <option value="in_progress">جاري</option>
          <option value="completed">مكتمل</option>
          <option value="weather_hold">تأجيل (طقس)</option>
          <option value="cancelled">ملغي</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحقل</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">النوع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المنتج</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الجرعة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الموعد</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredRecords.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                        <Droplet className="w-5 h-5 text-sahool-green-600" />
                      </div>
                      <div className="font-medium text-gray-900">{record.fieldName}</div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${sprayTypes[record.type].color}`}
                    >
                      {sprayTypes[record.type].labelAr}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">{record.productNameAr}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{record.dosage}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {new Date(record.scheduledAt).toLocaleDateString('ar-SA', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="px-4 py-3">{getStatusBadge(record.status)}</td>
                  <td className="px-4 py-3">
                    <button className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium">
                      التفاصيل
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
