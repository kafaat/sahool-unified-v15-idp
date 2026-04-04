'use client';

import React, { useState, useMemo } from 'react';
import {
  Search,
  Award,
  TrendingUp,
  Wheat,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Scale,
  Droplets,
  Package,
  Calendar,
} from 'lucide-react';

type QualityGrade = 'A' | 'B' | 'C' | 'rejected';
type InspectionStatus = 'passed' | 'pending' | 'failed';

interface HarvestBatch {
  id: string;
  fieldName: string;
  fieldNameAr: string;
  crop: string;
  cropAr: string;
  harvestDate: string;
  quantity: number;
  unit: string;
  grade: QualityGrade;
  moistureContent: number;
  proteinContent: number;
  foreignMatter: number;
  inspectionStatus: InspectionStatus;
  certificationReady: boolean;
  storageLocation: string;
  storageLocationAr: string;
  pricePerTon: number;
}

const mockBatches: HarvestBatch[] = [
  {
    id: 'HB-001',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    crop: 'Wheat',
    cropAr: 'القمح',
    harvestDate: '2026-03-28',
    quantity: 12.5,
    unit: 'طن',
    grade: 'A',
    moistureContent: 11.2,
    proteinContent: 13.5,
    foreignMatter: 0.3,
    inspectionStatus: 'passed',
    certificationReady: true,
    storageLocation: 'Silo-01',
    storageLocationAr: 'صومعة 01',
    pricePerTon: 1950,
  },
  {
    id: 'HB-002',
    fieldName: 'Wheat Field',
    fieldNameAr: 'حقل القمح',
    crop: 'Wheat',
    cropAr: 'القمح',
    harvestDate: '2026-03-30',
    quantity: 18.3,
    unit: 'طن',
    grade: 'B',
    moistureContent: 13.8,
    proteinContent: 11.2,
    foreignMatter: 1.2,
    inspectionStatus: 'passed',
    certificationReady: false,
    storageLocation: 'Silo-02',
    storageLocationAr: 'صومعة 02',
    pricePerTon: 1750,
  },
  {
    id: 'HB-003',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    crop: 'Barley',
    cropAr: 'الشعير',
    harvestDate: '2026-04-01',
    quantity: 8.7,
    unit: 'طن',
    grade: 'A',
    moistureContent: 10.5,
    proteinContent: 9.8,
    foreignMatter: 0.5,
    inspectionStatus: 'pending',
    certificationReady: false,
    storageLocation: 'Warehouse-A',
    storageLocationAr: 'مستودع أ',
    pricePerTon: 1600,
  },
  {
    id: 'HB-004',
    fieldName: 'Palm Grove',
    fieldNameAr: 'بستان النخيل',
    crop: 'Dates (Barhi)',
    cropAr: 'تمور (برحي)',
    harvestDate: '2026-03-25',
    quantity: 3.2,
    unit: 'طن',
    grade: 'A',
    moistureContent: 22.0,
    proteinContent: 2.4,
    foreignMatter: 0.1,
    inspectionStatus: 'passed',
    certificationReady: true,
    storageLocation: 'Cold Storage 1',
    storageLocationAr: 'مبرد 1',
    pricePerTon: 8500,
  },
  {
    id: 'HB-005',
    fieldName: 'Greenhouse',
    fieldNameAr: 'الصوب الزراعية',
    crop: 'Tomato',
    cropAr: 'الطماطم',
    harvestDate: '2026-04-02',
    quantity: 5.1,
    unit: 'طن',
    grade: 'C',
    moistureContent: 94.0,
    proteinContent: 0.9,
    foreignMatter: 2.5,
    inspectionStatus: 'failed',
    certificationReady: false,
    storageLocation: 'Cold Storage 2',
    storageLocationAr: 'مبرد 2',
    pricePerTon: 2200,
  },
  {
    id: 'HB-006',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    crop: 'Wheat',
    cropAr: 'القمح',
    harvestDate: '2026-04-03',
    quantity: 6.8,
    unit: 'طن',
    grade: 'rejected',
    moistureContent: 18.5,
    proteinContent: 8.1,
    foreignMatter: 4.2,
    inspectionStatus: 'failed',
    certificationReady: false,
    storageLocation: 'Quarantine',
    storageLocationAr: 'حجر صحي',
    pricePerTon: 0,
  },
];

export default function HarvestQualityClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [gradeFilter, setGradeFilter] = useState<QualityGrade | 'all'>('all');

  const filteredBatches = useMemo(() => {
    return mockBatches.filter((batch) => {
      const matchesSearch =
        !searchTerm ||
        batch.fieldNameAr.includes(searchTerm) ||
        batch.cropAr.includes(searchTerm) ||
        batch.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesGrade = gradeFilter === 'all' || batch.grade === gradeFilter;
      return matchesSearch && matchesGrade;
    });
  }, [searchTerm, gradeFilter]);

  const getGradeBadge = (grade: QualityGrade) => {
    const styles: Record<QualityGrade, string> = {
      A: 'bg-green-100 text-green-800',
      B: 'bg-blue-100 text-blue-800',
      C: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800',
    };
    const labels: Record<QualityGrade, string> = { A: 'ممتاز', B: 'جيد', C: 'مقبول', rejected: 'مرفوض' };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-bold ${styles[grade]}`}>
        {grade !== 'rejected' ? grade + ' - ' : ''}{labels[grade]}
      </span>
    );
  };

  const getInspectionIcon = (status: InspectionStatus) => {
    if (status === 'passed') return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (status === 'pending') return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    return <XCircle className="w-4 h-4 text-red-500" />;
  };

  const getInspectionLabel = (status: InspectionStatus) => {
    const labels: Record<InspectionStatus, string> = { passed: 'ناجح', pending: 'قيد الفحص', failed: 'فاشل' };
    return labels[status];
  };

  const totalQuantity = mockBatches.reduce((s, b) => s + b.quantity, 0);
  const gradeACount = mockBatches.filter((b) => b.grade === 'A').length;
  const rejectedCount = mockBatches.filter((b) => b.grade === 'rejected').length;
  const totalValue = mockBatches.reduce((s, b) => s + b.quantity * b.pricePerTon, 0);

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">جودة الحصاد</h1>
          <p className="text-gray-500 mt-1">Harvest Quality</p>
        </div>
      </div>

      {/* Rejected alert */}
      {rejectedCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              {rejectedCount} دفعة مرفوضة وتحتاج مراجعة الجودة
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Wheat className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الكمية</div>
              <div className="text-xl font-bold text-gray-900">{totalQuantity.toFixed(1)} طن</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Award className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">درجة ممتازة (A)</div>
              <div className="text-xl font-bold text-yellow-600">{gradeACount} دفعات</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">القيمة الإجمالية</div>
              <div className="text-xl font-bold text-blue-600">
                {(totalValue / 1000).toFixed(0)} ألف ريال
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">معدل القبول</div>
              <div className="text-xl font-bold text-purple-600">
                {Math.round(((mockBatches.length - rejectedCount) / mockBatches.length) * 100)}%
              </div>
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
            placeholder="بحث بالحقل أو المحصول أو رقم الدفعة..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={gradeFilter}
          onChange={(e) => setGradeFilter(e.target.value as QualityGrade | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع الدرجات</option>
          <option value="A">ممتاز (A)</option>
          <option value="B">جيد (B)</option>
          <option value="C">مقبول (C)</option>
          <option value="rejected">مرفوض</option>
        </select>
      </div>

      {/* Batches Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredBatches.map((batch) => (
          <div
            key={batch.id}
            className={`bg-white rounded-lg border p-5 hover:shadow-md transition-shadow ${
              batch.grade === 'rejected' ? 'border-red-300' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-gray-400 font-mono">{batch.id}</span>
                  {batch.certificationReady && (
                    <span className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded text-xs">
                      جاهز للشهادة
                    </span>
                  )}
                </div>
                <h3 className="font-medium text-gray-900">{batch.cropAr}</h3>
                <p className="text-sm text-gray-500">{batch.fieldNameAr}</p>
              </div>
              {getGradeBadge(batch.grade)}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Scale className="w-4 h-4" />
                  <span>الكمية</span>
                </div>
                <span className="font-medium">{batch.quantity} {batch.unit}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Droplets className="w-4 h-4" />
                  <span>الرطوبة</span>
                </div>
                <span className={`font-medium ${batch.moistureContent > 14 ? 'text-red-600' : 'text-gray-900'}`}>
                  {batch.moistureContent}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">البروتين</span>
                <span className="font-medium">{batch.proteinContent}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">الشوائب</span>
                <span className={`font-medium ${batch.foreignMatter > 2 ? 'text-red-600' : 'text-gray-900'}`}>
                  {batch.foreignMatter}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">الفحص</span>
                <div className="flex items-center gap-1">
                  {getInspectionIcon(batch.inspectionStatus)}
                  <span className="text-gray-700">{getInspectionLabel(batch.inspectionStatus)}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Package className="w-4 h-4" />
                  <span>التخزين</span>
                </div>
                <span className="font-medium">{batch.storageLocationAr}</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t flex justify-between items-center">
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Calendar className="w-3 h-3" />
                <span>{new Date(batch.harvestDate).toLocaleDateString('ar-SA')}</span>
              </div>
              {batch.pricePerTon > 0 && (
                <span className="font-bold text-green-700">{batch.pricePerTon.toLocaleString()} ريال/طن</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
