'use client';

import React, { useMemo } from 'react';
import { CheckCircle, AlertTriangle, Calendar, TrendingUp, Award } from 'lucide-react';
import { useCompliance, useCertifications, useComplianceStats } from '@/features/compliance';
import type { ComplianceItem, Certification } from '@/features/compliance';

export default function ComplianceClient() {
  // Fetch data using React Query hooks
  const {
    data: compliance = [],
    isLoading: complianceLoading,
    error: complianceError,
  } = useCompliance();
  const { data: certifications = [], isLoading: certsLoading } = useCertifications();
  const { data: stats } = useComplianceStats();

  const isLoading = complianceLoading || certsLoading;

  const getStatusColor = (status: ComplianceItem['status']) => {
    const colors: Record<ComplianceItem['status'], string> = {
      compliant: 'text-green-600 bg-green-100',
      partial: 'text-yellow-600 bg-yellow-100',
      non_compliant: 'text-red-600 bg-red-100',
      pending_review: 'text-blue-600 bg-blue-100',
      not_applicable: 'text-gray-600 bg-gray-100',
    };
    return colors[status];
  };

  const getStatusLabel = (status: ComplianceItem['status']) => {
    const labels: Record<ComplianceItem['status'], string> = {
      compliant: 'متوافق',
      partial: 'جزئي',
      non_compliant: 'غير متوافق',
      pending_review: 'قيد المراجعة',
      not_applicable: 'غير مطبق',
    };
    return labels[status];
  };

  const getCertStatusColor = (status: Certification['status']) => {
    const colors: Record<Certification['status'], string> = {
      active: 'text-green-600 bg-green-100',
      expired: 'text-red-600 bg-red-100',
      pending: 'text-yellow-600 bg-yellow-100',
      revoked: 'text-orange-600 bg-orange-100',
    };
    return colors[status];
  };

  const getCertStatusLabel = (status: Certification['status']) => {
    const labels: Record<Certification['status'], string> = {
      active: 'نشطة',
      expired: 'منتهية',
      pending: 'قيد الإصدار',
      revoked: 'ملغاة',
    };
    return labels[status];
  };

  const localStats = useMemo(() => {
    const overallScore =
      compliance.length > 0
        ? Math.round(compliance.reduce((acc, c) => acc + c.score, 0) / compliance.length)
        : 0;
    const compliantCount = compliance.filter((c) => c.status === 'compliant').length;
    const activeCerts = certifications.filter((c) => c.status === 'active').length;
    // Compute min next audit using Date parsing so mixed ISO/locale strings
    // don't cause incorrect string-compare ordering. Skip items with an
    // invalid or past date (null-safe).
    const auditTimestamps = compliance
      .map((c) => Date.parse(c.nextAudit))
      .filter((t): t is number => Number.isFinite(t));
    const nextAudit = auditTimestamps.length
      ? new Date(Math.min(...auditTimestamps)).toISOString().slice(0, 10)
      : 'N/A';
    return { overallScore, compliantCount, activeCerts, nextAudit };
  }, [compliance, certifications]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (complianceError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات الامتثال</p>
          <p className="text-gray-500 text-sm">Failed to load compliance data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">الامتثال والجودة</h1>
          <p className="text-gray-500 mt-1">GlobalGAP Compliance & Quality Management</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors">
            تقرير التدقيق
          </button>
          <button className="px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
            + فحص جديد
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">نسبة الامتثال</div>
              <div className="text-lg font-bold text-green-600">
                {stats?.overallScore ?? localStats.overallScore}%
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متطلبات متوافقة</div>
              <div className="text-lg font-bold text-blue-600">
                {stats?.compliantCount ?? localStats.compliantCount}/
                {stats?.totalRequirements ?? compliance.length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Award className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">شهادات نشطة</div>
              <div className="text-lg font-bold text-purple-600">
                {stats?.activeCertifications ?? localStats.activeCerts}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">التدقيق القادم</div>
              <div className="text-lg font-bold text-amber-600">{localStats.nextAudit}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Checklist */}
        <div className="lg:col-span-2 bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">قائمة الامتثال</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    الفئة
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    المتطلب
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    الحالة
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    النتيجة
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    التدقيق القادم
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {compliance.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                      لا توجد بيانات امتثال
                    </td>
                  </tr>
                ) : (
                  compliance.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-900">{item.categoryAr}</div>
                        <div className="text-xs text-gray-500">{item.category}</div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-gray-900">{item.requirementAr}</div>
                        {(item.notesAr ?? item.notes) && (
                          <div className="text-xs text-amber-600 mt-1">
                            {item.notesAr ?? item.notes}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}
                        >
                          {getStatusLabel(item.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${item.score >= 90 ? 'bg-green-500' : item.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                              style={{ width: `${item.score}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{item.score}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-gray-500">
                        {item.nextAudit}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Certifications */}
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">الشهادات</h2>
          </div>
          <div className="divide-y">
            {certifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">لا توجد شهادات</div>
            ) : (
              certifications.map((cert) => (
                <div key={cert.id} className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Award className="w-5 h-5 text-sahool-green-600" />
                      <div>
                        <h3 className="font-medium text-gray-900">{cert.nameAr}</h3>
                        <p className="text-xs text-gray-500">{cert.name}</p>
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getCertStatusColor(cert.status)}`}
                    >
                      {getCertStatusLabel(cert.status)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <div>الجهة: {cert.issuerAr}</div>
                    {cert.status === 'active' && (
                      <>
                        <div>تاريخ الإصدار: {cert.issueDate}</div>
                        <div>تاريخ الانتهاء: {cert.expiryDate}</div>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Compliance Score Chart Placeholder */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">تطور نسبة الامتثال</h2>
        </div>
        <div className="p-4">
          <div className="h-64 bg-gradient-to-t from-green-50 to-white flex items-end justify-around px-8">
            {[78, 82, 85, 88, 90, 92].map((score, i) => (
              <div key={i} className="flex flex-col items-center gap-2">
                <div
                  className="w-12 bg-sahool-green-500 rounded-t-lg transition-all hover:bg-sahool-green-600"
                  style={{ height: `${score * 2}px` }}
                />
                <span className="text-xs text-gray-500">
                  {['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'][i]}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
