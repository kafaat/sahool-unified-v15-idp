'use client';

/**
 * SAHOOL AI Vision Detection Client
 * الكشف البصري بالذكاء الاصطناعي
 */

import React, { useState } from 'react';
import {
  Eye,
  Upload,
  Bug,
  Leaf,
  AlertTriangle,
  Clock,
  Zap,
} from 'lucide-react';

interface DetectionResult {
  id: string;
  imageId: string;
  fieldName: string;
  detectionType: 'pest' | 'disease' | 'weed';
  detectionTypeAr: string;
  label: string;
  labelAr: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  severityAr: string;
  date: string;
  status: 'new' | 'reviewed' | 'treated';
  statusAr: string;
  recommendation: string;
  recommendationAr: string;
}

const MOCK_RESULTS: DetectionResult[] = [
  { id: 'VD-001', imageId: 'IMG-4521', fieldName: 'حقل القمح الشمالي', detectionType: 'disease', detectionTypeAr: 'مرض', label: 'Wheat Rust', labelAr: 'صدأ القمح', confidence: 0.94, severity: 'high', severityAr: 'عالي', date: '2026-04-04', status: 'new', statusAr: 'جديد', recommendation: 'Apply fungicide within 48 hours', recommendationAr: 'رش مبيد فطري خلال 48 ساعة' },
  { id: 'VD-002', imageId: 'IMG-4518', fieldName: 'حقل النخيل', detectionType: 'pest', detectionTypeAr: 'آفة', label: 'Red Palm Weevil', labelAr: 'سوسة النخيل الحمراء', confidence: 0.91, severity: 'critical', severityAr: 'حرج', date: '2026-04-04', status: 'reviewed', statusAr: 'تمت المراجعة', recommendation: 'Inject insecticide immediately', recommendationAr: 'حقن مبيد حشري فورا' },
  { id: 'VD-003', imageId: 'IMG-4510', fieldName: 'حقل الطماطم', detectionType: 'disease', detectionTypeAr: 'مرض', label: 'Early Blight', labelAr: 'لفحة مبكرة', confidence: 0.87, severity: 'medium', severityAr: 'متوسط', date: '2026-04-03', status: 'treated', statusAr: 'تمت المعالجة', recommendation: 'Remove affected leaves, apply copper-based fungicide', recommendationAr: 'إزالة الأوراق المصابة ورش مبيد فطري نحاسي' },
  { id: 'VD-004', imageId: 'IMG-4505', fieldName: 'حقل الشعير', detectionType: 'weed', detectionTypeAr: 'حشائش', label: 'Wild Oat', labelAr: 'شوفان بري', confidence: 0.82, severity: 'low', severityAr: 'منخفض', date: '2026-04-02', status: 'reviewed', statusAr: 'تمت المراجعة', recommendation: 'Apply selective herbicide', recommendationAr: 'رش مبيد حشائش انتقائي' },
  { id: 'VD-005', imageId: 'IMG-4498', fieldName: 'حقل القمح الجنوبي', detectionType: 'pest', detectionTypeAr: 'آفة', label: 'Aphid Colony', labelAr: 'مستعمرة من حشرة المن', confidence: 0.78, severity: 'medium', severityAr: 'متوسط', date: '2026-04-01', status: 'treated', statusAr: 'تمت المعالجة', recommendation: 'Release ladybugs or apply neem oil', recommendationAr: 'إطلاق حشرة أبو العيد أو رش زيت النيم' },
];

const severityColors: Record<string, string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

const typeIcons: Record<string, React.ReactNode> = {
  pest: <Bug className="w-4 h-4 text-red-500" />,
  disease: <Leaf className="w-4 h-4 text-orange-500" />,
  weed: <AlertTriangle className="w-4 h-4 text-yellow-500" />,
};

const statusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-700',
  reviewed: 'bg-purple-100 text-purple-700',
  treated: 'bg-green-100 text-green-700',
};

export default function VisionClient() {
  const [filter, setFilter] = useState<'all' | 'pest' | 'disease' | 'weed'>('all');

  const filtered = filter === 'all' ? MOCK_RESULTS : MOCK_RESULTS.filter(r => r.detectionType === filter);

  const stats = {
    total: MOCK_RESULTS.length,
    critical: MOCK_RESULTS.filter(r => r.severity === 'critical').length,
    pending: MOCK_RESULTS.filter(r => r.status === 'new').length,
    avgConfidence: Math.round((MOCK_RESULTS.reduce((s, r) => s + r.confidence, 0) / MOCK_RESULTS.length) * 100),
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الكشف البصري بالذكاء الاصطناعي</h1>
            <p className="text-gray-600 mt-1">AI Vision Detection</p>
          </div>
          <button className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
            <Upload className="w-5 h-5" />
            <span>رفع صورة للتحليل</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Eye className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">إجمالي الكشوفات</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <p className="text-sm text-gray-600">حالات حرجة</p>
          </div>
          <p className="text-3xl font-bold text-red-600">{stats.critical}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-orange-600" />
            <p className="text-sm text-gray-600">بانتظار المراجعة</p>
          </div>
          <p className="text-3xl font-bold text-orange-600">{stats.pending}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">متوسط الدقة</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{stats.avgConfidence}%</p>
        </div>
      </div>

      {/* Filter + Table */}
      <div className="bg-white rounded-xl border-2 border-gray-200">
        <div className="flex items-center gap-3 p-6 border-b border-gray-200">
          <span className="text-sm font-medium text-gray-600">تصفية:</span>
          {(['all', 'pest', 'disease', 'weed'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === f ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {f === 'all' ? 'الكل' : f === 'pest' ? 'آفات' : f === 'disease' ? 'أمراض' : 'حشائش'}
            </button>
          ))}
        </div>

        <div className="p-6">
          <table className="w-full text-right">
            <thead>
              <tr className="border-b border-gray-200 text-sm text-gray-500">
                <th className="pb-3 pr-4 font-medium">النوع</th>
                <th className="pb-3 pr-4 font-medium">الكشف</th>
                <th className="pb-3 pr-4 font-medium">الحقل</th>
                <th className="pb-3 pr-4 font-medium">الدقة</th>
                <th className="pb-3 pr-4 font-medium">الخطورة</th>
                <th className="pb-3 pr-4 font-medium">الحالة</th>
                <th className="pb-3 pr-4 font-medium">التوصية</th>
                <th className="pb-3 font-medium">التاريخ</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(result => (
                <tr key={result.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-2">
                      {typeIcons[result.detectionType]}
                      <span className="text-sm">{result.detectionTypeAr}</span>
                    </div>
                  </td>
                  <td className="py-4 pr-4">
                    <p className="font-semibold text-gray-900 text-sm">{result.labelAr}</p>
                    <p className="text-xs text-gray-500">{result.label}</p>
                  </td>
                  <td className="py-4 pr-4 text-sm text-gray-700">{result.fieldName}</td>
                  <td className="py-4 pr-4 text-sm font-medium text-gray-900">{Math.round(result.confidence * 100)}%</td>
                  <td className="py-4 pr-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${severityColors[result.severity]}`}>
                      {result.severityAr}
                    </span>
                  </td>
                  <td className="py-4 pr-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[result.status]}`}>
                      {result.statusAr}
                    </span>
                  </td>
                  <td className="py-4 pr-4 text-sm text-gray-600 max-w-[200px] truncate">{result.recommendationAr}</td>
                  <td className="py-4 text-sm text-gray-700">{result.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
