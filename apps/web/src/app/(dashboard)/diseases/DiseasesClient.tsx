'use client';

import React, { useState, useMemo } from 'react';
import { Bug, Search, AlertTriangle, CheckCircle, Clock, Leaf, Camera } from 'lucide-react';

type DiseaseStatus = 'active' | 'treated' | 'resolved' | 'monitoring';
type DiseaseSeverity = 'low' | 'medium' | 'high' | 'critical';

interface Disease {
  id: string;
  name: string;
  nameAr: string;
  cropType: string;
  cropTypeAr: string;
  fieldId: string;
  fieldName: string;
  severity: DiseaseSeverity;
  status: DiseaseStatus;
  affectedArea: number;
  detectedAt: string;
  treatment?: string;
  treatmentAr?: string;
}

const mockDiseases: Disease[] = [
  {
    id: '1',
    name: 'Wheat Rust',
    nameAr: 'صدأ القمح',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    severity: 'high',
    status: 'active',
    affectedArea: 2.5,
    detectedAt: '2025-01-24T10:00:00Z',
  },
  {
    id: '2',
    name: 'Powdery Mildew',
    nameAr: 'البياض الدقيقي',
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    severity: 'medium',
    status: 'treated',
    affectedArea: 1.2,
    detectedAt: '2025-01-20T08:30:00Z',
    treatment: 'Fungicide application',
    treatmentAr: 'رش مبيد فطري',
  },
  {
    id: '3',
    name: 'Aphid Infestation',
    nameAr: 'إصابة المن',
    cropType: 'Vegetables',
    cropTypeAr: 'خضروات',
    fieldId: 'field-3',
    fieldName: 'حقل الخضروات',
    severity: 'low',
    status: 'monitoring',
    affectedArea: 0.5,
    detectedAt: '2025-01-23T14:00:00Z',
  },
  {
    id: '4',
    name: 'Root Rot',
    nameAr: 'تعفن الجذور',
    cropType: 'Date Palm',
    cropTypeAr: 'نخيل',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    severity: 'critical',
    status: 'active',
    affectedArea: 0.8,
    detectedAt: '2025-01-25T06:00:00Z',
  },
  {
    id: '5',
    name: 'Leaf Spot',
    nameAr: 'تبقع الأوراق',
    cropType: 'Tomato',
    cropTypeAr: 'طماطم',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    severity: 'medium',
    status: 'resolved',
    affectedArea: 0.3,
    detectedAt: '2025-01-15T09:00:00Z',
    treatment: 'Removed affected plants',
    treatmentAr: 'إزالة النباتات المصابة',
  },
];

export default function DiseasesClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<DiseaseStatus | 'all'>('all');
  const [severityFilter, setSeverityFilter] = useState<DiseaseSeverity | 'all'>('all');

  const filteredDiseases = useMemo(() => {
    return mockDiseases.filter((disease) => {
      const matchesSearch =
        !searchTerm ||
        disease.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        disease.nameAr.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || disease.status === statusFilter;
      const matchesSeverity = severityFilter === 'all' || disease.severity === severityFilter;
      return matchesSearch && matchesStatus && matchesSeverity;
    });
  }, [searchTerm, statusFilter, severityFilter]);

  const getSeverityBadge = (severity: DiseaseSeverity) => {
    const styles = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    const labels = {
      low: 'منخفض',
      medium: 'متوسط',
      high: 'عالي',
      critical: 'حرج',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[severity]}`}>
        {labels[severity]}
      </span>
    );
  };

  const getStatusBadge = (status: DiseaseStatus) => {
    const styles = {
      active: 'bg-red-100 text-red-800',
      treated: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
      monitoring: 'bg-yellow-100 text-yellow-800',
    };
    const labels = {
      active: 'نشط',
      treated: 'تحت العلاج',
      resolved: 'تم الحل',
      monitoring: 'تحت المراقبة',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const activeCount = mockDiseases.filter((d) => d.status === 'active').length;
  const criticalCount = mockDiseases.filter((d) => d.severity === 'critical').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة الأمراض</h1>
          <p className="text-gray-500 mt-1">Disease Management</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700">
          <Camera className="w-4 h-4" />
          <span>تشخيص جديد</span>
        </button>
      </div>

      {/* Critical Alert */}
      {criticalCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              تنبيه: {criticalCount} إصابة حرجة تتطلب تدخل فوري
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Bug className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إصابات نشطة</div>
              <div className="text-xl font-bold text-red-600">{activeCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تحت العلاج</div>
              <div className="text-xl font-bold text-blue-600">
                {mockDiseases.filter((d) => d.status === 'treated').length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تحت المراقبة</div>
              <div className="text-xl font-bold text-yellow-600">
                {mockDiseases.filter((d) => d.status === 'monitoring').length}
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
              <div className="text-sm text-gray-500">تم الحل</div>
              <div className="text-xl font-bold text-green-600">
                {mockDiseases.filter((d) => d.status === 'resolved').length}
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
            placeholder="بحث عن مرض..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as DiseaseStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="active">نشط</option>
          <option value="treated">تحت العلاج</option>
          <option value="monitoring">تحت المراقبة</option>
          <option value="resolved">تم الحل</option>
        </select>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value as DiseaseSeverity | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الشدة</option>
          <option value="critical">حرج</option>
          <option value="high">عالي</option>
          <option value="medium">متوسط</option>
          <option value="low">منخفض</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المرض</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المحصول</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحقل</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  المساحة المتأثرة
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الشدة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredDiseases.map((disease) => (
                <tr key={disease.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                        <Bug className="w-5 h-5 text-red-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{disease.nameAr}</div>
                        <div className="text-sm text-gray-500">{disease.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{disease.cropTypeAr}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{disease.fieldName}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{disease.affectedArea} هكتار</td>
                  <td className="px-4 py-3">{getSeverityBadge(disease.severity)}</td>
                  <td className="px-4 py-3">{getStatusBadge(disease.status)}</td>
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
