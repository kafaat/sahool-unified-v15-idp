'use client';

import React, { useState, useMemo } from 'react';
import {
  Search,
  Gauge,
  Zap,
  Settings,
  AlertTriangle,
  Calculator,
  Loader2,
  Leaf,
  Droplets,
} from 'lucide-react';
import { useVSCrops, useVSSoils } from '../hooks/useVirtualSensors';

export default function VirtualSensorsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'crops' | 'soils'>('crops');

  const {
    data: crops = [],
    isLoading: isLoadingCrops,
    isError: isCropsError,
    error: cropsError,
  } = useVSCrops();

  const {
    data: soils = [],
    isLoading: isLoadingSoils,
    isError: isSoilsError,
    error: soilsError,
  } = useVSSoils();

  const isLoading = isLoadingCrops || isLoadingSoils;
  const isError = isCropsError || isSoilsError;
  const errorMsg = cropsError ?? soilsError;

  const filteredCrops = useMemo(() => {
    if (!searchTerm) return crops;
    return crops.filter(
      (c) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.nameAr.includes(searchTerm)
    );
  }, [crops, searchTerm]);

  const filteredSoils = useMemo(() => {
    if (!searchTerm) return soils;
    return soils.filter(
      (s) =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.nameAr.includes(searchTerm)
    );
  }, [soils, searchTerm]);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-600 font-medium">جاري تحميل بيانات المستشعرات الافتراضية...</p>
          <p className="text-sm text-gray-400 mt-1">Loading virtual sensors data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            فشل في تحميل بيانات المستشعرات الافتراضية
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            {errorMsg instanceof Error ? errorMsg.message : 'Failed to load virtual sensors data'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 transition-colors"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">المستشعرات الافتراضية</h1>
          <p className="text-gray-500 mt-1">Virtual Sensors - Crop & Soil Parameters</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Calculator className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">حسابات متاحة</div>
              <div className="text-xl font-bold text-gray-900">5</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">أنواع المحاصيل</div>
              <div className="text-xl font-bold text-green-600">{crops.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Droplets className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">أنواع التربة</div>
              <div className="text-xl font-bold text-yellow-600">{soils.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">الخوارزميات</div>
              <div className="text-xl font-bold text-blue-600">
                ET0 / ETc / SM
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Computation cards */}
      <div className="bg-white rounded-lg border p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">الحسابات المتاحة</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4 bg-blue-50">
            <div className="flex items-center gap-2 mb-2">
              <Calculator className="w-5 h-5 text-blue-600" />
              <h3 className="font-medium text-gray-900">التبخر-نتح المرجعي (ET0)</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              حساب معدل التبخر-نتح المرجعي باستخدام معادلة بنمان-مونتيث
            </p>
            <p className="text-xs text-gray-400">Penman-Monteith equation</p>
          </div>
          <div className="border rounded-lg p-4 bg-green-50">
            <div className="flex items-center gap-2 mb-2">
              <Leaf className="w-5 h-5 text-green-600" />
              <h3 className="font-medium text-gray-900">التبخر-نتح الفعلي (ETc)</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              حساب احتياج المحصول الفعلي من المياه بناء على معامل المحصول (Kc)
            </p>
            <p className="text-xs text-gray-400">Crop coefficient method</p>
          </div>
          <div className="border rounded-lg p-4 bg-yellow-50">
            <div className="flex items-center gap-2 mb-2">
              <Droplets className="w-5 h-5 text-yellow-600" />
              <h3 className="font-medium text-gray-900">تقدير رطوبة التربة</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              تقدير رطوبة التربة الحالية باستخدام الميزان المائي
            </p>
            <p className="text-xs text-gray-400">Water balance estimation</p>
          </div>
        </div>
      </div>

      {/* Tabs for Crops / Soils */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        <button
          onClick={() => setActiveTab('crops')}
          className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
            activeTab === 'crops'
              ? 'bg-white text-green-700 shadow-sm font-medium'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Leaf className="w-4 h-4" />
          المحاصيل ({crops.length})
        </button>
        <button
          onClick={() => setActiveTab('soils')}
          className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
            activeTab === 'soils'
              ? 'bg-white text-green-700 shadow-sm font-medium'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Droplets className="w-4 h-4" />
          التربة ({soils.length})
        </button>
      </div>

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={activeTab === 'crops' ? 'بحث عن محصول...' : 'بحث عن نوع تربة...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
      </div>

      {/* Crops tab */}
      {activeTab === 'crops' && (
        <>
          {filteredCrops.length === 0 ? (
            <div className="bg-white rounded-lg border p-8 text-center">
              <Leaf className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد محاصيل</h3>
              <p className="text-gray-500 text-sm">
                {searchTerm ? 'لا توجد نتائج تطابق البحث' : 'لم يتم تحميل بيانات المحاصيل'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredCrops.map((crop) => (
                <div key={crop.type} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-gray-900">{crop.nameAr}</h3>
                      <p className="text-sm text-gray-500">{crop.name}</p>
                    </div>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {crop.stages?.length ?? 0} مراحل
                    </span>
                  </div>

                  {crop.stages && crop.stages.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-gray-500 mb-1">مراحل النمو ومعامل Kc:</p>
                      {crop.stages.map((stage) => (
                        <div key={stage.name} className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">{stage.nameAr}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-400">{stage.durationDays} يوم</span>
                            <span className="font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded text-xs">
                              Kc: {stage.kc}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-4 pt-3 border-t flex justify-between items-center">
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Gauge className="w-3 h-3" />
                      <span>نموذج فيزيائي</span>
                    </div>
                    <button
                      disabled
                      title="قريبا - Coming soon"
                      className="text-green-600 hover:text-green-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      حساب ETc
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Soils tab */}
      {activeTab === 'soils' && (
        <>
          {filteredSoils.length === 0 ? (
            <div className="bg-white rounded-lg border p-8 text-center">
              <Droplets className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد أنواع تربة</h3>
              <p className="text-gray-500 text-sm">
                {searchTerm ? 'لا توجد نتائج تطابق البحث' : 'لم يتم تحميل بيانات التربة'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSoils.map((soil) => (
                <div key={soil.type} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-gray-900">{soil.nameAr}</h3>
                      <p className="text-sm text-gray-500">{soil.name}</p>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">السعة الحقلية</span>
                      <span className="font-medium text-gray-700">{soil.fieldCapacity}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">نقطة الذبول</span>
                      <span className="font-medium text-gray-700">{soil.wiltingPoint}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">التوصيلية المشبعة</span>
                      <span className="font-medium text-gray-700">{soil.saturatedConductivity} mm/h</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">الماء المتاح</span>
                      <span className="font-medium text-blue-700">
                        {(soil.fieldCapacity - soil.wiltingPoint).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t flex justify-between items-center">
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Settings className="w-3 h-3" />
                      <span>خصائص هيدروليكية</span>
                    </div>
                    <button
                      disabled
                      title="قريبا - Coming soon"
                      className="text-green-600 hover:text-green-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      تقدير الرطوبة
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
