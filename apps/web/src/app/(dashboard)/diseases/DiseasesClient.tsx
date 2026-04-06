'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { Bug, Search, AlertTriangle, CheckCircle, Clock, Leaf, Camera, Loader2 } from 'lucide-react';
import { diseasesApi, type Disease, type DiseaseStatus, type DiseaseSeverity } from '@/features/diseases/api';
import { ApiError } from '@/lib/api/safe-fetch';

export default function DiseasesClient() {
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<DiseaseStatus | 'all'>('all');
  const [severityFilter, setSeverityFilter] = useState<DiseaseSeverity | 'all'>('all');

  const fetchDiseases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await diseasesApi.getDiseases();
      setDiseases(data);
    } catch (err) {
      const message = err instanceof ApiError ? err.messageAr : 'فشل في جلب بيانات الأمراض';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDiseases();
  }, [fetchDiseases]);

  const filteredDiseases = useMemo(() => {
    return diseases.filter((disease) => {
      const matchesSearch =
        !searchTerm ||
        disease.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        disease.nameAr.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || disease.status === statusFilter;
      const matchesSeverity = severityFilter === 'all' || disease.severity === severityFilter;
      return matchesSearch && matchesStatus && matchesSeverity;
    });
  }, [diseases, searchTerm, statusFilter, severityFilter]);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-sahool-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-500">جاري تحميل بيانات الأمراض...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">خطأ في تحميل البيانات</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={fetchDiseases}
            className="px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  const activeCount = diseases.filter((d) => d.status === 'active').length;
  const criticalCount = diseases.filter((d) => d.severity === 'critical').length;

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
                {diseases.filter((d) => d.status === 'treated').length}
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
                {diseases.filter((d) => d.status === 'monitoring').length}
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
                {diseases.filter((d) => d.status === 'resolved').length}
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
              {filteredDiseases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    لا توجد بيانات أمراض
                  </td>
                </tr>
              ) : (
                filteredDiseases.map((disease) => (
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
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
