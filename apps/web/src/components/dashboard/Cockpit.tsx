/**
 * SAHOOL Dashboard Cockpit Component
 * الشاشة الرئيسية للوحة التحكم - محدثة لاستخدام الـ kernel المسترجع
 */

'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { StatsCards } from './StatsCards';
import { TaskList } from './TaskList';
import { EventTimeline } from './EventTimeline';
import { AlertPanel } from './AlertPanel';
import { QuickActions } from './QuickActions';
import { useAlerts } from '../../hooks/useAlerts';

// Dynamic import for MapView (client-side only, requires maplibre-gl)
const MapView = dynamic(() => import('./MapView'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <span className="text-4xl">🗺️</span>
        <p className="text-gray-500 mt-2">جاري تحميل الخريطة...</p>
      </div>
    </div>
  ),
});

interface CockpitProps {
  tenantId?: string;
}

export const Cockpit: React.FC<CockpitProps> = ({ tenantId = 'tenant_1' }) => {
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const { alerts, dismiss, dismissAll } = useAlerts();

  const handleFieldSelect = (fieldId: string | null) => {
    setSelectedField(fieldId);
    console.log('Field selected:', fieldId);
  };

  const handleAction = (actionId: string) => {
    console.log('Quick action:', actionId);
    // TODO: Implement quick actions
  };

  const handleAlertAction = (url: string) => {
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">لوحة التحكم</h1>
          <p className="text-sm text-gray-500 mt-1">
            {new Date().toLocaleDateString('ar-YE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-gray-600">متصل</span>
          </div>
          <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700 transition-colors">
            + مهمة جديدة
          </button>
        </div>
      </header>

      {/* Stats Section */}
      <div className="px-6 py-4">
        <StatsCards tenantId={tenantId} />
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 px-6 pb-6">
        {/* Map - 8 columns */}
        <div className="col-span-12 lg:col-span-8 bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <h3 className="font-bold text-gray-800">🗺️ خريطة الحقول</h3>
            <div className="flex gap-2">
              <button className="text-xs px-3 py-1 rounded-full bg-emerald-100 text-emerald-700">
                الحقول
              </button>
              <button className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200">
                NDVI
              </button>
              <button className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200">
                المهام
              </button>
            </div>
          </div>
          <div className="h-[400px] lg:h-[500px]">
            <MapView tenantId={tenantId} onFieldSelect={handleFieldSelect} />
          </div>
        </div>

        {/* Right Panel - 4 columns */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-4">
          {/* Quick Actions */}
          <QuickActions onAction={handleAction} />

          {/* Alerts */}
          <AlertPanel
            alerts={alerts}
            onDismiss={dismiss}
            onDismissAll={dismissAll}
            onAction={handleAlertAction}
          />
        </div>

        {/* Bottom Section */}
        <div className="col-span-12 grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Tasks */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-bold text-gray-800">📋 مهام اليوم</h3>
              <span className="text-xs bg-emerald-600 text-white px-2 py-1 rounded-full">
                {selectedField ? 'حقل محدد' : 'كل الحقول'}
              </span>
            </div>
            <div className="flex-1 overflow-auto p-4 max-h-[400px]">
              <TaskList tenantId={tenantId} fieldId={selectedField} />
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-bold text-gray-800">📊 الأحداث المباشرة</h3>
              <span className="flex items-center gap-1 text-xs text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                مباشر
              </span>
            </div>
            <div className="flex-1 overflow-auto p-4 max-h-[400px]">
              <EventTimeline tenantId={tenantId} />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="px-6 py-4 text-center text-sm text-gray-500 border-t bg-white">
        <p>SAHOOL v16.0 - منصة زراعية ذكية متكاملة مع خدمات Kernel المسترجعة</p>
      </footer>
    </div>
  );
};

export default Cockpit;
