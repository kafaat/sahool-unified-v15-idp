/**
 * Health Dashboard Component
 * لوحة معلومات صحة المحصول
 */

'use client';

import React, { useState } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  TrendingDown,
  
  Leaf,
  Search,
} from 'lucide-react';
import { useHealthSummary, useHealthRecords, useDiseaseAlerts } from '../hooks/useCropHealth';
import type { HealthFilters } from '../types';

export const HealthDashboard: React.FC = () => {
  const [filters] = useState<HealthFilters>({});

  const { data: summary, isLoading: summaryLoading } = useHealthSummary(filters);
  const { data: records, isLoading: recordsLoading } = useHealthRecords(filters);
  const { data: alerts } = useDiseaseAlerts();

  const statusConfig = {
    healthy: {
      label: 'صحية',
      labelEn: 'Healthy',
      icon: CheckCircle2,
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-200',
    },
    at_risk: {
      label: 'معرضة للخطر',
      labelEn: 'At Risk',
      icon: AlertTriangle,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
    },
    diseased: {
      label: 'مصابة',
      labelEn: 'Diseased',
      icon: TrendingDown,
      color: 'text-orange-600',
      bg: 'bg-orange-50',
      border: 'border-orange-200',
    },
    critical: {
      label: 'حرجة',
      labelEn: 'Critical',
      icon: AlertTriangle,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
    },
  };

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Leaf className="w-8 h-8 text-green-500" />
                صحة المحصول والتشخيص
              </h1>
              <p className="mt-1 text-sm text-gray-500">Crop Health & Diagnosis</p>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                data-testid="health-dashboard-search"
                type="text"
                placeholder="ابحث في الحقول..."
                className="pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent w-64"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alerts */}
        {alerts && alerts.length > 0 && (
          <div className="mb-6 space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                data-testid="disease-alert"
                className="bg-red-50 border-r-4 border-red-500 p-4 rounded-lg"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-red-900">{alert.disease.nameAr}</h4>
                    <p className="text-sm text-red-800 mt-1">{alert.messageAr}</p>
                    {alert.recommendationsAr && alert.recommendationsAr.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {alert.recommendationsAr.map((rec, idx) => (
                          <li key={idx} className="text-sm text-red-700">
                            • {rec}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <span className="text-xs text-red-600">
                    {new Date(alert.issuedAt).toLocaleDateString('ar-SA')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Summary Cards */}
        {summaryLoading ? (
          <div data-testid="health-dashboard-loading" className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        ) : summary ? (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Healthy Fields */}
              <div data-testid="stat-healthy-fields" className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">حقول صحية</p>
                    <p className="text-3xl font-bold text-green-600 mt-2">
                      {summary.healthyFields}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {((summary.healthyFields / summary.totalFields) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <CheckCircle2 className="w-12 h-12 text-green-500 opacity-20" />
                </div>
              </div>

              {/* At Risk */}
              <div data-testid="stat-at-risk" className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">معرضة للخطر</p>
                    <p className="text-3xl font-bold text-yellow-600 mt-2">
                      {summary.atRiskFields}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {((summary.atRiskFields / summary.totalFields) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <AlertTriangle className="w-12 h-12 text-yellow-500 opacity-20" />
                </div>
              </div>

              {/* Diseased */}
              <div data-testid="stat-diseased" className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">حقول مصابة</p>
                    <p className="text-3xl font-bold text-orange-600 mt-2">
                      {summary.diseasedFields}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {((summary.diseasedFields / summary.totalFields) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <TrendingDown className="w-12 h-12 text-orange-500 opacity-20" />
                </div>
              </div>

              {/* Average Health Score */}
              <div data-testid="stat-avg-health" className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">متوسط الصحة</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {summary.avgHealthScore.toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">من 100</p>
                  </div>
                  <Activity className="w-12 h-12 text-gray-400 opacity-20" />
                </div>
              </div>
            </div>

            {/* Top Diseases */}
            {summary.topDiseases && summary.topDiseases.length > 0 && (
              <div data-testid="top-diseases" className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  الأمراض الأكثر انتشاراً
                </h3>
                <div className="space-y-3">
                  {summary.topDiseases.map((item, idx) => (
                    <div
                      key={item.disease.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="flex items-center justify-center w-8 h-8 bg-gray-200 rounded-full text-sm font-semibold text-gray-700">
                          {idx + 1}
                        </span>
                        <div>
                          <p className="font-medium text-gray-900">{item.disease.nameAr}</p>
                          <p className="text-sm text-gray-600">{item.disease.name}</p>
                        </div>
                      </div>
                      <div className="text-left">
                        <p className="text-lg font-bold text-red-600">
                          {item.affectedFields}
                        </p>
                        <p className="text-xs text-gray-500">حقول متأثرة</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : null}

        {/* Health Records */}
        {recordsLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500" data-testid="loading-spinner"></div>
          </div>
        ) : records && records.length > 0 ? (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">سجلات الصحة</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {records.map((record) => {
                const config = statusConfig[record.status];
                const StatusIcon = config.icon;

                return (
                  <div
                    key={record.id}
                    data-testid="health-record"
                    className={`p-6 rounded-xl shadow-sm border-2 ${config.bg} ${config.border}`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {record.fieldNameAr}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">{record.cropTypeAr}</p>
                      </div>
                      <StatusIcon className={`w-6 h-6 ${config.color}`} />
                    </div>

                    <div className="space-y-3">
                      {/* Health Score */}
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-600">درجة الصحة</span>
                          <span className={`text-sm font-semibold ${config.color}`}>
                            {record.healthScore}/100
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              record.healthScore >= 80
                                ? 'bg-green-500'
                                : record.healthScore >= 60
                                ? 'bg-yellow-500'
                                : record.healthScore >= 40
                                ? 'bg-orange-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${record.healthScore}%` }}
                          />
                        </div>
                      </div>

                      {/* Status */}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">الحالة:</span>
                        <span className={`text-sm font-medium ${config.color}`}>
                          {config.label}
                        </span>
                      </div>

                      {/* Date */}
                      <div className="pt-3 border-t border-gray-200">
                        <p className="text-xs text-gray-500">
                          آخر فحص: {new Date(record.date).toLocaleDateString('ar-SA')}
                        </p>
                        {record.nextCheckDate && (
                          <p className="text-xs text-gray-500 mt-1">
                            الفحص القادم:{' '}
                            {new Date(record.nextCheckDate).toLocaleDateString('ar-SA')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
            <Leaf className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">لا توجد سجلات صحة متاحة</p>
            <p className="text-sm text-gray-500 mt-1">No health records available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthDashboard;
