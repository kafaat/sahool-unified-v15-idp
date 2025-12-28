'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  SERVICE_REGISTRY,
  ServiceType,
  ServiceVersion,
  getServiceVersions,
  setServiceVersion,
  resetToDefaults,
  switchAllServices,
  checkServicesHealth,
} from '@/lib/services/service-switcher';

interface ServiceHealth {
  healthy: boolean;
  latency: number;
}

interface HealthStatus {
  legacy?: ServiceHealth;
  modern: ServiceHealth;
  mock?: ServiceHealth;
}

/**
 * ServiceSwitcher Component
 * مكون التبديل بين الخدمات للمقارنة والاختبار
 */
export const ServiceSwitcher = React.memo(function ServiceSwitcher() {
  const [versions, setVersions] = useState<Record<ServiceType, ServiceVersion>>(getServiceVersions);
  const [healthStatus, setHealthStatus] = useState<Record<string, HealthStatus>>({});
  const [loading, setLoading] = useState(false);
  const [showOnlyConflicting, setShowOnlyConflicting] = useState(true);

  // الخدمات المتعارضة فقط (التي لها legacy و modern)
  const conflictingServices = Object.entries(SERVICE_REGISTRY).filter(
    ([_, config]) => config.legacy && config.modern
  ) as [ServiceType, typeof SERVICE_REGISTRY[ServiceType]][];

  // الخدمات للعرض
  const displayServices = showOnlyConflicting
    ? conflictingServices
    : (Object.entries(SERVICE_REGISTRY) as [ServiceType, typeof SERVICE_REGISTRY[ServiceType]][]);

  useEffect(() => {
    const handleChange = (e: Event) => {
      const customEvent = e as CustomEvent;
      setVersions(customEvent.detail);
    };

    window.addEventListener('service-versions-changed', handleChange);
    return () => {
      window.removeEventListener('service-versions-changed', handleChange);
    };
  }, []);

  const handleVersionChange = useCallback((service: ServiceType, version: ServiceVersion) => {
    setServiceVersion(service, version);
    setVersions((prev) => ({ ...prev, [service]: version }));
  }, []);

  const handleCheckHealth = useCallback(async () => {
    setLoading(true);
    try {
      const results = await checkServicesHealth();
      setHealthStatus(results);
    } catch (error) {
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleReset = useCallback(() => {
    resetToDefaults();
    setVersions(getServiceVersions());
  }, []);

  const handleSwitchAll = useCallback((version: ServiceVersion) => {
    switchAllServices(version);
    setVersions(getServiceVersions());
  }, []);

  const getStatusColor = (health?: ServiceHealth) => {
    if (!health) return 'bg-gray-200';
    if (!health.healthy) return 'bg-red-500';
    if (health.latency > 500) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusBadge = (status: 'deprecated' | 'active' | 'beta' | 'development') => {
    const colors = {
      deprecated: 'bg-red-100 text-red-700',
      active: 'bg-green-100 text-green-700',
      beta: 'bg-yellow-100 text-yellow-700',
      development: 'bg-blue-100 text-blue-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-4xl mx-auto" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 border-b pb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">⚙️ مبدّل الخدمات</h2>
          <p className="text-sm text-gray-500 mt-1">
            التبديل بين الخدمات القديمة والحديثة للمقارنة والاختبار
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCheckHealth}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="فحص صحة الخدمات"
          >
            {loading ? '⏳ جاري الفحص...' : '🔍 فحص الصحة'}
          </button>
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400"
            aria-label="إعادة تعيين الخدمات للإعدادات الافتراضية"
          >
            ↩️ إعادة تعيين
          </button>
        </div>
      </div>

      {/* Quick Switch */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <p className="text-sm font-medium text-gray-700 mb-3">تبديل سريع لجميع الخدمات:</p>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={() => handleSwitchAll('modern')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
          >
            ✅ الخدمات الحديثة
          </button>
          <button
            onClick={() => handleSwitchAll('legacy')}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600"
          >
            🕰️ الخدمات القديمة
          </button>
          <button
            onClick={() => handleSwitchAll('mock')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
          >
            🎭 خدمات المحاكاة
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2 mb-4">
        <input
          type="checkbox"
          id="showConflicting"
          checked={showOnlyConflicting}
          onChange={(e) => setShowOnlyConflicting(e.target.checked)}
          className="rounded border-gray-300"
        />
        <label htmlFor="showConflicting" className="text-sm text-gray-600">
          عرض الخدمات المتعارضة فقط ({conflictingServices.length} خدمة)
        </label>
      </div>

      {/* Services List */}
      <div className="space-y-4">
        {displayServices.map(([serviceType, config]) => {
          const health = healthStatus[serviceType];
          const currentVersion = versions[serviceType];

          return (
            <div
              key={serviceType}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-800">{config.nameAr}</h3>
                  <p className="text-xs text-gray-500">{config.name}</p>
                </div>

                {/* Version Selector */}
                <div className="flex gap-2">
                  {config.legacy && (
                    <button
                      onClick={() => handleVersionChange(serviceType, 'legacy')}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                        currentVersion === 'legacy'
                          ? 'bg-orange-500 text-white'
                          : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                      }`}
                    >
                      قديم ({config.legacy.port})
                    </button>
                  )}
                  <button
                    onClick={() => handleVersionChange(serviceType, 'modern')}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                      currentVersion === 'modern'
                        ? 'bg-green-500 text-white'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    حديث ({config.modern.port})
                  </button>
                  {config.mock && (
                    <button
                      onClick={() => handleVersionChange(serviceType, 'mock')}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                        currentVersion === 'mock'
                          ? 'bg-purple-500 text-white'
                          : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                      }`}
                    >
                      محاكاة ({config.mock.port})
                    </button>
                  )}
                </div>
              </div>

              {/* Service Details */}
              <div className="mt-3 grid grid-cols-3 gap-4 text-xs">
                {/* Legacy Info */}
                {config.legacy && (
                  <div className="bg-orange-50 rounded p-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">قديم</span>
                      <span className={`px-2 py-0.5 rounded text-xs ${getStatusBadge(config.legacy.status)}`}>
                        {config.legacy.status === 'deprecated' ? 'متقادم' : 'نشط'}
                      </span>
                    </div>
                    <p className="text-gray-600">المنفذ: {config.legacy.port}</p>
                    <p className="text-gray-500 truncate" title={config.legacy.endpoint}>
                      {config.legacy.endpoint}
                    </p>
                    {health?.legacy && (
                      <div className="flex items-center gap-1 mt-1">
                        <span
                          className={`w-2 h-2 rounded-full ${getStatusColor(health.legacy)}`}
                        ></span>
                        <span>
                          {health.legacy.healthy
                            ? `${health.legacy.latency}ms`
                            : 'غير متصل'}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Modern Info */}
                <div className="bg-green-50 rounded p-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">حديث</span>
                    <span className={`px-2 py-0.5 rounded text-xs ${getStatusBadge(config.modern.status)}`}>
                      {config.modern.status === 'active' ? 'نشط' : config.modern.status}
                    </span>
                  </div>
                  <p className="text-gray-600">المنفذ: {config.modern.port}</p>
                  <p className="text-gray-500 truncate" title={config.modern.endpoint}>
                    {config.modern.endpoint}
                  </p>
                  {health?.modern && (
                    <div className="flex items-center gap-1 mt-1">
                      <span
                        className={`w-2 h-2 rounded-full ${getStatusColor(health.modern)}`}
                      ></span>
                      <span>
                        {health.modern.healthy ? `${health.modern.latency}ms` : 'غير متصل'}
                      </span>
                    </div>
                  )}
                </div>

                {/* Mock Info */}
                {config.mock && (
                  <div className="bg-purple-50 rounded p-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">محاكاة</span>
                      <span className="px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-700">
                        تطوير
                      </span>
                    </div>
                    <p className="text-gray-600">المنفذ: {config.mock.port}</p>
                    <p className="text-gray-500 truncate" title={config.mock.endpoint}>
                      {config.mock.endpoint}
                    </p>
                    {health?.mock && (
                      <div className="flex items-center gap-1 mt-1">
                        <span
                          className={`w-2 h-2 rounded-full ${getStatusColor(health.mock)}`}
                        ></span>
                        <span>
                          {health.mock.healthy ? `${health.mock.latency}ms` : 'غير متصل'}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t">
        <p className="text-xs text-gray-500 mb-2">دليل الحالة:</p>
        <div className="flex gap-4 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500"></span> متصل
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-500"></span> بطيء
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500"></span> غير متصل
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-gray-200"></span> غير مفحوص
          </span>
        </div>
      </div>
    </div>
  );
});

export default ServiceSwitcher;
