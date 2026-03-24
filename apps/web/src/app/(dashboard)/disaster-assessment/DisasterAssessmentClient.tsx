'use client';

import React, { useMemo } from 'react';
import {
  AlertTriangle,
  Shield,
  CloudRain,
  Thermometer,
  Wind,
  MapPin,
  Clock,
  FileText,
} from 'lucide-react';
import {
  useDisasterRisks,
  useDisasterEvents,
  useDisasterStats,
} from '@/features/disaster-assessment';
import type { RiskAssessment, DisasterEvent } from '@/features/disaster-assessment';

export default function DisasterAssessmentClient() {
  // Fetch data using React Query hooks
  const { data: risks = [], isLoading: risksLoading, error: risksError } = useDisasterRisks();
  const { data: events = [], isLoading: eventsLoading } = useDisasterEvents();
  const { data: stats } = useDisasterStats();

  const isLoading = risksLoading || eventsLoading;

  const getRiskColor = (level: RiskAssessment['riskLevel']) => {
    const colors = {
      low: 'text-green-600 bg-green-100 border-green-200',
      medium: 'text-yellow-600 bg-yellow-100 border-yellow-200',
      high: 'text-orange-600 bg-orange-100 border-orange-200',
      critical: 'text-red-600 bg-red-100 border-red-200',
    };
    return colors[level];
  };

  const getRiskLabel = (level: RiskAssessment['riskLevel']) => {
    const labels = {
      low: 'منخفض',
      medium: 'متوسط',
      high: 'مرتفع',
      critical: 'حرج',
    };
    return labels[level];
  };

  const getRiskIcon = (type: RiskAssessment['type']) => {
    const icons: Record<string, React.ReactNode> = {
      drought: <Thermometer className="w-5 h-5" />,
      flood: <CloudRain className="w-5 h-5" />,
      frost: <Thermometer className="w-5 h-5" />,
      storm: <Wind className="w-5 h-5" />,
      pest: <AlertTriangle className="w-5 h-5" />,
      disease: <AlertTriangle className="w-5 h-5" />,
    };
    return icons[type] || <AlertTriangle className="w-5 h-5" />;
  };

  const getSeverityColor = (severity: DisasterEvent['severity']) => {
    const colors: Record<DisasterEvent['severity'], string> = {
      minor: 'text-yellow-600 bg-yellow-100',
      moderate: 'text-orange-600 bg-orange-100',
      severe: 'text-red-600 bg-red-100',
      catastrophic: 'text-purple-600 bg-purple-100',
    };
    return colors[severity];
  };

  const getSeverityLabel = (severity: DisasterEvent['severity']) => {
    const labels: Record<DisasterEvent['severity'], string> = {
      minor: 'طفيف',
      moderate: 'متوسط',
      severe: 'شديد',
      catastrophic: 'كارثي',
    };
    return labels[severity];
  };

  const getStatusColor = (status: DisasterEvent['status']) => {
    const colors: Record<DisasterEvent['status'], string> = {
      active: 'text-red-600 bg-red-100',
      monitoring: 'text-blue-600 bg-blue-100',
      resolved: 'text-green-600 bg-green-100',
      closed: 'text-gray-600 bg-gray-100',
    };
    return colors[status];
  };

  const getStatusLabel = (status: DisasterEvent['status']) => {
    const labels: Record<DisasterEvent['status'], string> = {
      active: 'نشط',
      monitoring: 'قيد المراقبة',
      resolved: 'تم الحل',
      closed: 'مغلق',
    };
    return labels[status];
  };

  const localStats = useMemo(() => {
    const criticalRisks = risks.filter(
      (r) => r.riskLevel === 'critical' || r.riskLevel === 'high'
    ).length;
    const totalPotentialLoss = risks.reduce((acc, r) => acc + r.potentialLoss, 0);
    const activeEvents = events.filter((e) => e.status !== 'resolved').length;
    return { criticalRisks, totalPotentialLoss, activeEvents, totalRisks: risks.length };
  }, [risks, events]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (risksError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات تقييم الكوارث</p>
          <p className="text-gray-500 text-sm">Failed to load disaster assessment data</p>
        </div>
      </div>
    );
  }

  const criticalRisks = stats?.criticalRisks ?? localStats.criticalRisks;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تقييم الكوارث</h1>
          <p className="text-gray-500 mt-1">Disaster Risk Assessment & Emergency Response</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
            <FileText className="w-4 h-4" />
            تقرير المخاطر
          </button>
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            إبلاغ عن حادث
          </button>
        </div>
      </div>

      {/* Alert Banner */}
      {criticalRisks > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-800">تنبيه: مخاطر حرجة نشطة</h3>
            <p className="text-red-700 text-sm mt-1">
              يوجد {criticalRisks} مخاطر عالية/حرجة تتطلب اهتماماً فورياً. راجع خطط التخفيف أدناه.
            </p>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مخاطر حرجة/عالية</div>
              <div className="text-lg font-bold text-red-600">{criticalRisks}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي المخاطر</div>
              <div className="text-lg font-bold text-amber-600">
                {stats?.activeRisks ?? localStats.totalRisks}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">حوادث نشطة</div>
              <div className="text-lg font-bold text-purple-600">
                {stats?.activeEvents ?? localStats.activeEvents}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Thermometer className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">الخسائر المحتملة</div>
              <div className="text-lg font-bold text-blue-600">
                {((stats?.totalPotentialLoss ?? localStats.totalPotentialLoss) / 1000).toFixed(0)}K
                ريال
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Cards */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">تقييم المخاطر الحالية</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {risks.length === 0 ? (
            <div className="col-span-full text-center py-8 text-gray-500">لا توجد مخاطر مسجلة</div>
          ) : (
            risks.map((risk) => (
              <div
                key={risk.id}
                className={`bg-white rounded-lg border-2 p-4 ${getRiskColor(risk.riskLevel)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center ${getRiskColor(risk.riskLevel)}`}
                    >
                      {getRiskIcon(risk.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{risk.typeAr}</h3>
                      <p className="text-sm text-gray-500">{risk.affectedAreaAr}</p>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(risk.riskLevel)}`}
                  >
                    {getRiskLabel(risk.riskLevel)}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                  <div>
                    <span className="text-gray-500">الاحتمالية:</span>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-2 bg-gray-200 rounded-full">
                        <div
                          className={`h-full rounded-full ${risk.probability >= 70 ? 'bg-red-500' : risk.probability >= 40 ? 'bg-yellow-500' : 'bg-green-500'}`}
                          style={{ width: `${risk.probability}%` }}
                        />
                      </div>
                      <span className="font-medium">{risk.probability}%</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">الخسائر المحتملة:</span>
                    <div className="font-medium mt-1">
                      {risk.potentialLoss.toLocaleString()} ريال
                    </div>
                  </div>
                </div>

                {risk.mitigationPlan && (
                  <div className="bg-white/50 rounded-lg p-3 text-sm">
                    <span className="text-gray-500">خطة التخفيف:</span>
                    <p className="text-gray-700 mt-1">{risk.mitigationPlan}</p>
                  </div>
                )}

                <div className="flex items-center justify-between mt-3 pt-3 border-t text-xs text-gray-500">
                  <span>آخر تحديث: {risk.lastUpdated}</span>
                  <button className="text-sahool-green-600 hover:text-sahool-green-700 font-medium">
                    عرض التفاصيل
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">الحوادث الأخيرة</h2>
        </div>
        <div className="divide-y">
          {events.length === 0 ? (
            <div className="p-8 text-center text-gray-500">لا توجد حوادث مسجلة</div>
          ) : (
            events.map((event) => (
              <div key={event.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center ${getSeverityColor(event.severity)}`}
                    >
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{event.typeAr}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <MapPin className="w-4 h-4" />
                        <span>{event.locationAr}</span>
                        <span className="text-gray-300">|</span>
                        <Clock className="w-4 h-4" />
                        <span>{event.date}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm text-gray-500">الأضرار المقدرة</div>
                      <div className="font-semibold text-gray-900">
                        {event.damageEstimate.toLocaleString()} ريال
                      </div>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(event.severity)}`}
                      >
                        {getSeverityLabel(event.severity)}
                      </span>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(event.status)}`}
                      >
                        {getStatusLabel(event.status)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Risk Map Placeholder */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">خريطة المخاطر</h2>
        </div>
        <div className="aspect-video bg-gradient-to-br from-amber-100 via-orange-100 to-red-100 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-16 h-16 text-red-700 mx-auto mb-4" />
            <p className="text-red-800 font-medium">خريطة توزيع المخاطر الجغرافية</p>
            <p className="text-red-700 text-sm">Geographic Risk Distribution Map</p>
          </div>
        </div>
      </div>
    </div>
  );
}
