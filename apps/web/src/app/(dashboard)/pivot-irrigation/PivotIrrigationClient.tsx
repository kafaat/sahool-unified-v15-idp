'use client';

/**
 * SAHOOL Pivot Irrigation Page Client Component
 * صفحة الري المحوري - Valley Style
 */

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  Droplets,
  Play,
  Pause,
  RotateCcw,
  Settings,
  PlusCircle,
  BarChart3,
  Grid3X3,
  Gauge,
  Clock,
} from 'lucide-react';

// Mock data for demonstration
const mockPivots = [
  {
    id: 'pivot_001',
    name: 'المحوري الرئيسي',
    nameEn: 'Main Pivot',
    fieldId: 'field_001',
    status: 'running',
    currentAngle: 127,
    speed: 75,
    direction: 'clockwise',
    areaHectares: 52.5,
    sectorsCount: 8,
    vriZonesCount: 48,
    waterUsageM3: 1250,
    lastIrrigation: '2026-01-22T14:30:00Z',
  },
  {
    id: 'pivot_002',
    name: 'محوري الحقل الشرقي',
    nameEn: 'East Field Pivot',
    fieldId: 'field_002',
    status: 'stopped',
    currentAngle: 0,
    speed: 0,
    direction: 'clockwise',
    areaHectares: 35.2,
    sectorsCount: 6,
    vriZonesCount: 36,
    waterUsageM3: 0,
    lastIrrigation: '2026-01-21T08:00:00Z',
  },
];

interface PivotVisualizationProps {
  pivot: (typeof mockPivots)[0];
}

function PivotVisualization({ pivot }: PivotVisualizationProps) {
  const sectors = Array.from({ length: pivot.sectorsCount }, (_, i) => ({
    id: `sector_${i}`,
    startAngle: (i * 360) / pivot.sectorsCount,
    endAngle: ((i + 1) * 360) / pivot.sectorsCount,
    color: `hsl(${120 + i * 10}, 70%, ${50 + (i % 2) * 10}%)`,
  }));

  return (
    <div className="relative aspect-square max-w-xs mx-auto">
      <svg viewBox="0 0 200 200" className="w-full h-full">
        {/* Background circle */}
        <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" strokeWidth="2" />

        {/* Sectors */}
        {sectors.map((sector) => {
          const startRad = ((sector.startAngle - 90) * Math.PI) / 180;
          const endRad = ((sector.endAngle - 90) * Math.PI) / 180;
          const x1 = 100 + 85 * Math.cos(startRad);
          const y1 = 100 + 85 * Math.sin(startRad);
          const x2 = 100 + 85 * Math.cos(endRad);
          const y2 = 100 + 85 * Math.sin(endRad);
          const largeArc = sector.endAngle - sector.startAngle > 180 ? 1 : 0;

          return (
            <path
              key={sector.id}
              d={`M 100 100 L ${x1} ${y1} A 85 85 0 ${largeArc} 1 ${x2} ${y2} Z`}
              fill={sector.color}
              fillOpacity={0.6}
              stroke="#fff"
              strokeWidth="1"
            />
          );
        })}

        {/* Center point */}
        <circle cx="100" cy="100" r="8" fill="#1e40af" />

        {/* Pivot arm */}
        {pivot.status === 'running' && (
          <line
            x1="100"
            y1="100"
            x2={100 + 80 * Math.cos(((pivot.currentAngle - 90) * Math.PI) / 180)}
            y2={100 + 80 * Math.sin(((pivot.currentAngle - 90) * Math.PI) / 180)}
            stroke="#1e40af"
            strokeWidth="4"
            strokeLinecap="round"
          >
            <animateTransform
              attributeName="transform"
              type="rotate"
              from={`${pivot.currentAngle} 100 100`}
              to={`${pivot.currentAngle + 360} 100 100`}
              dur="60s"
              repeatCount="indefinite"
            />
          </line>
        )}

        {/* Status indicator */}
        <circle cx="100" cy="100" r="4" fill={pivot.status === 'running' ? '#22c55e' : '#ef4444'} />
      </svg>
    </div>
  );
}

interface PivotCardProps {
  pivot: (typeof mockPivots)[0];
  onSelect: () => void;
  isSelected: boolean;
}

function PivotCard({ pivot, onSelect, isSelected }: PivotCardProps) {
  const t = useTranslations('pivotIrrigation');

  return (
    <div
      onClick={onSelect}
      className={`bg-white rounded-xl border-2 p-6 cursor-pointer transition-all ${
        isSelected
          ? 'border-sahool-green-500 ring-2 ring-sahool-green-200'
          : 'border-gray-200 hover:border-sahool-green-300'
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{pivot.name}</h3>
          <p className="text-sm text-gray-500">{pivot.nameEn}</p>
        </div>
        <div
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            pivot.status === 'running' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
          }`}
        >
          {pivot.status === 'running' ? t('running') : t('stopped')}
        </div>
      </div>

      <PivotVisualization pivot={pivot} />

      <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
        <div>
          <span className="text-gray-500">المساحة:</span>
          <span className="font-medium mr-1">{pivot.areaHectares} ha</span>
        </div>
        <div>
          <span className="text-gray-500">القطاعات:</span>
          <span className="font-medium mr-1">{pivot.sectorsCount}</span>
        </div>
        <div>
          <span className="text-gray-500">مناطق VRI:</span>
          <span className="font-medium mr-1">{pivot.vriZonesCount}</span>
        </div>
        <div>
          <span className="text-gray-500">{t('currentAngle')}:</span>
          <span className="font-medium mr-1">{pivot.currentAngle}°</span>
        </div>
      </div>
    </div>
  );
}

export default function PivotIrrigationClient() {
  const t = useTranslations('pivotIrrigation');
  const [selectedPivotId, setSelectedPivotId] = useState<string | null>(mockPivots[0]?.id || null);

  const selectedPivot = mockPivots.find((p) => p.id === selectedPivotId);
  const runningPivots = mockPivots.filter((p) => p.status === 'running').length;
  const totalWaterUsage = mockPivots.reduce((sum, p) => sum + p.waterUsageM3, 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{t('title')}</h1>
            <p className="text-gray-600 mt-1">{t('subtitle')}</p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
            <PlusCircle className="w-5 h-5" />
            <span>{t('addPivot')}</span>
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Droplets className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{mockPivots.length}</h3>
          <p className="text-sm text-gray-600">إجمالي المحاور | Total Pivots</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Play className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{runningPivots}</h3>
          <p className="text-sm text-gray-600">يعمل الآن | Running Now</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-cyan-100 rounded-lg">
              <Gauge className="w-6 h-6 text-cyan-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">
            {totalWaterUsage.toLocaleString()}
          </h3>
          <p className="text-sm text-gray-600">استهلاك المياه م³ | Water m³</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Grid3X3 className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">
            {mockPivots.reduce((sum, p) => sum + p.vriZonesCount, 0)}
          </h3>
          <p className="text-sm text-gray-600">مناطق VRI | VRI Zones</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pivot List - 1/3 width */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">المحاور المسجلة | Registered Pivots</h2>
          {mockPivots.map((pivot) => (
            <PivotCard
              key={pivot.id}
              pivot={pivot}
              onSelect={() => setSelectedPivotId(pivot.id)}
              isSelected={selectedPivotId === pivot.id}
            />
          ))}
        </div>

        {/* Pivot Details - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {selectedPivot ? (
            <>
              {/* Control Panel */}
              <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  لوحة التحكم | Control Panel
                </h2>

                <div className="flex flex-wrap gap-4 mb-6">
                  <button
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                      selectedPivot.status === 'running'
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {selectedPivot.status === 'running' ? (
                      <>
                        <Pause className="w-5 h-5" />
                        <span>{t('stopPivot')}</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5" />
                        <span>{t('startPivot')}</span>
                      </>
                    )}
                  </button>

                  <button className="flex items-center gap-2 px-6 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium transition-colors">
                    <RotateCcw className="w-5 h-5" />
                    <span>عكس الاتجاه</span>
                  </button>

                  <button className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors">
                    <Settings className="w-5 h-5" />
                    <span>الإعدادات</span>
                  </button>
                </div>

                {/* Speed Control */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    {t('speed')}: {selectedPivot.speed}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={selectedPivot.speed}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    readOnly
                  />
                </div>
              </div>

              {/* Tabs for Sectors, VRI Zones, Schedule */}
              <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
                <div className="flex gap-4 border-b border-gray-200 mb-6">
                  <button className="px-4 py-2 text-sahool-green-600 border-b-2 border-sahool-green-600 font-medium">
                    {t('sectors')}
                  </button>
                  <button className="px-4 py-2 text-gray-500 hover:text-gray-700">
                    {t('vriZones')}
                  </button>
                  <button className="px-4 py-2 text-gray-500 hover:text-gray-700">
                    {t('schedule')}
                  </button>
                  <button className="px-4 py-2 text-gray-500 hover:text-gray-700">
                    {t('statistics')}
                  </button>
                </div>

                {/* Sectors Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Array.from({ length: selectedPivot.sectorsCount }, (_, i) => (
                    <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">قطاع {i + 1}</span>
                        <span
                          className={`w-3 h-3 rounded-full ${
                            i < 3 ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        />
                      </div>
                      <div className="text-sm text-gray-600">
                        <div>
                          الزاوية: {(i * 360) / selectedPivot.sectorsCount}° -{' '}
                          {((i + 1) * 360) / selectedPivot.sectorsCount}°
                        </div>
                        <div>معدل التطبيق: 100%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  النشاط الأخير | Recent Activity
                </h2>
                <div className="space-y-4">
                  <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Play className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">بدأ دورة الري</p>
                      <p className="text-sm text-gray-500">
                        {new Date(selectedPivot.lastIrrigation).toLocaleString('ar-SA')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Clock className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">تحديث جدول الري</p>
                      <p className="text-sm text-gray-500">منذ 3 ساعات</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <BarChart3 className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">تحديث مناطق VRI</p>
                      <p className="text-sm text-gray-500">منذ يومين</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-xl border-2 border-gray-200 p-12 text-center">
              <Droplets className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">{t('noPivots')}</h3>
              <p className="text-gray-500 mb-4">قم بإضافة محوري جديد للبدء</p>
              <button className="flex items-center gap-2 px-6 py-3 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 mx-auto">
                <PlusCircle className="w-5 h-5" />
                <span>{t('addPivot')}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
