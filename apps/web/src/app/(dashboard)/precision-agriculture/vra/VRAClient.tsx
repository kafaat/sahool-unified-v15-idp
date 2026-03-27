'use client';

import React, { useState } from 'react';
import {
  Map,
  Layers,
  Plus,
  Download,
  Upload,
  Target,
  Droplets,
  Wheat,
  Settings,
} from 'lucide-react';

type VRAType = 'fertilizer' | 'seeding' | 'irrigation' | 'pesticide';
type VRAStatus = 'draft' | 'ready' | 'applied' | 'archived';

interface VRAMap {
  id: string;
  name: string;
  nameAr: string;
  fieldId: string;
  fieldName: string;
  type: VRAType;
  status: VRAStatus;
  zones: number;
  totalArea: number;
  createdAt: string;
  appliedAt?: string;
  minRate: number;
  maxRate: number;
  unit: string;
}

const mockVRAMaps: VRAMap[] = [
  {
    id: '1',
    name: 'Nitrogen VRA - North Field',
    nameAr: 'خريطة نيتروجين - الحقل الشمالي',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    type: 'fertilizer',
    status: 'ready',
    zones: 5,
    totalArea: 25.5,
    createdAt: '2025-01-20T10:00:00Z',
    minRate: 80,
    maxRate: 150,
    unit: 'كجم/هكتار',
  },
  {
    id: '2',
    name: 'Seeding Rate - South Field',
    nameAr: 'معدل البذر - الحقل الجنوبي',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    type: 'seeding',
    status: 'applied',
    zones: 4,
    totalArea: 18.2,
    createdAt: '2024-11-15T08:00:00Z',
    appliedAt: '2024-11-20T06:00:00Z',
    minRate: 120,
    maxRate: 180,
    unit: 'كجم/هكتار',
  },
  {
    id: '3',
    name: 'Irrigation Zones - Wheat Field',
    nameAr: 'مناطق الري - حقل القمح',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    type: 'irrigation',
    status: 'ready',
    zones: 6,
    totalArea: 32.0,
    createdAt: '2025-01-18T14:00:00Z',
    minRate: 15,
    maxRate: 35,
    unit: 'مم',
  },
  {
    id: '4',
    name: 'Phosphorus Application - Palm Grove',
    nameAr: 'تطبيق الفوسفور - بستان النخيل',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    type: 'fertilizer',
    status: 'draft',
    zones: 3,
    totalArea: 12.5,
    createdAt: '2025-01-24T09:00:00Z',
    minRate: 40,
    maxRate: 80,
    unit: 'كجم/هكتار',
  },
];

const vraTypes: Record<
  VRAType,
  { icon: React.ReactNode; label: string; labelAr: string; color: string }
> = {
  fertilizer: {
    icon: <Wheat className="w-5 h-5" />,
    label: 'Fertilizer',
    labelAr: 'سماد',
    color: 'bg-green-100 text-green-800',
  },
  seeding: {
    icon: <Target className="w-5 h-5" />,
    label: 'Seeding',
    labelAr: 'بذر',
    color: 'bg-amber-100 text-amber-800',
  },
  irrigation: {
    icon: <Droplets className="w-5 h-5" />,
    label: 'Irrigation',
    labelAr: 'ري',
    color: 'bg-blue-100 text-blue-800',
  },
  pesticide: {
    icon: <Settings className="w-5 h-5" />,
    label: 'Pesticide',
    labelAr: 'مبيد',
    color: 'bg-red-100 text-red-800',
  },
};

export default function VRAClient() {
  const [typeFilter, setTypeFilter] = useState<VRAType | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<VRAStatus | 'all'>('all');

  const filteredMaps = mockVRAMaps.filter((map) => {
    const matchesType = typeFilter === 'all' || map.type === typeFilter;
    const matchesStatus = statusFilter === 'all' || map.status === statusFilter;
    return matchesType && matchesStatus;
  });

  const getStatusBadge = (status: VRAStatus) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800',
      ready: 'bg-blue-100 text-blue-800',
      applied: 'bg-green-100 text-green-800',
      archived: 'bg-yellow-100 text-yellow-800',
    };
    const labels = {
      draft: 'مسودة',
      ready: 'جاهز',
      applied: 'مُطبق',
      archived: 'مؤرشف',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const readyCount = mockVRAMaps.filter((m) => m.status === 'ready').length;
  const appliedCount = mockVRAMaps.filter((m) => m.status === 'applied').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التطبيق المتغير</h1>
          <p className="text-gray-500 mt-1">Variable Rate Application (VRA)</p>
        </div>
        <div className="flex gap-2">
          <button className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Upload className="w-4 h-4" />
            <span>استيراد</span>
          </button>
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700">
            <Plus className="w-4 h-4" />
            <span>خريطة جديدة</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Map className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الخرائط</div>
              <div className="text-xl font-bold text-gray-900">{mockVRAMaps.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">جاهزة للتطبيق</div>
              <div className="text-xl font-bold text-blue-600">{readyCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مُطبقة</div>
              <div className="text-xl font-bold text-green-600">{appliedCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
              <Wheat className="w-5 h-5 text-sahool-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">المساحة الكلية</div>
              <div className="text-xl font-bold text-sahool-green-600">
                {mockVRAMaps.reduce((sum, m) => sum + m.totalArea, 0).toFixed(1)} هـ
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as VRAType | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الأنواع</option>
          <option value="fertilizer">سماد</option>
          <option value="seeding">بذر</option>
          <option value="irrigation">ري</option>
          <option value="pesticide">مبيد</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as VRAStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="draft">مسودة</option>
          <option value="ready">جاهز</option>
          <option value="applied">مُطبق</option>
          <option value="archived">مؤرشف</option>
        </select>
      </div>

      {/* VRA Map Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredMaps.map((map) => (
          <div
            key={map.id}
            className="bg-white rounded-lg border overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Map Preview Placeholder */}
            <div className="h-40 bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center">
              <div className="text-center">
                <Map className="w-12 h-12 text-green-600 mx-auto mb-2" />
                <p className="text-sm text-green-700">{map.zones} مناطق</p>
              </div>
            </div>

            <div className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{map.nameAr}</h3>
                  <p className="text-sm text-gray-500">{map.fieldName}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${vraTypes[map.type].color}`}
                  >
                    {vraTypes[map.type].labelAr}
                  </span>
                  {getStatusBadge(map.status)}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                  <span className="text-gray-500">المساحة:</span>
                  <span className="font-medium text-gray-900 mr-1">{map.totalArea} هـ</span>
                </div>
                <div>
                  <span className="text-gray-500">المناطق:</span>
                  <span className="font-medium text-gray-900 mr-1">{map.zones}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">نطاق المعدل:</span>
                  <span className="font-medium text-gray-900 mr-1">
                    {map.minRate} - {map.maxRate} {map.unit}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t">
                <span className="text-xs text-gray-400">
                  {new Date(map.createdAt).toLocaleDateString('ar-SA')}
                </span>
                <div className="flex gap-2">
                  <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-1 text-sahool-green-600 hover:bg-sahool-green-50 rounded-lg text-sm font-medium">
                    فتح
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
