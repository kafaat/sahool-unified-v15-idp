/**
 * SAHOOL Dashboard Cockpit Component
 * الشاشة الرئيسية للوحة التحكم
 */

import React from 'react';
import { KPIGrid } from './KPIGrid';
import { AlertPanel } from './AlertPanel';
import { QuickActions } from './QuickActions';
import { useKPIs } from '../../hooks/useKPIs';
import { useAlerts } from '../../hooks/useAlerts';

export const Cockpit: React.FC = () => {
  const { kpis, isLoading: kpisLoading } = useKPIs();
  const { alerts, dismiss, dismissAll, isLoading: alertsLoading } = useAlerts();

  const handleKPIClick = (kpi: any) => {
    console.log('KPI clicked:', kpi);
  };

  const handleAction = (actionId: string) => {
    console.log('Action:', actionId);
  };

  const handleAlertAction = (url: string) => {
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6" dir="rtl">
      {/* Header */}
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">لوحة التحكم</h1>
        <p className="text-gray-500 mt-1">مرحباً، هذا ملخص اليوم</p>
      </header>

      {/* KPI Section */}
      <section className="mb-6">
        <KPIGrid
          kpis={kpis}
          isLoading={kpisLoading}
          onKPIClick={handleKPIClick}
        />
      </section>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Area - 2 columns */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-[500px] flex items-center justify-center">
            <div className="text-center text-gray-400">
              <span className="text-6xl">🗺️</span>
              <p className="mt-4">خريطة الحقول</p>
              <p className="text-sm mt-2">تحتاج إلى Mapbox/Leaflet</p>
            </div>
          </div>
        </div>

        {/* Sidebar - 1 column */}
        <div className="space-y-6">
          <QuickActions onAction={handleAction} />

          <AlertPanel
            alerts={alerts}
            onDismiss={dismiss}
            onDismissAll={dismissAll}
            onAction={handleAlertAction}
          />
        </div>
      </div>

      {/* Footer Stats */}
      <footer className="mt-8 text-center text-sm text-gray-500">
        <p>SAHOOL v16.0 - منصة زراعية ذكية</p>
      </footer>
    </div>
  );
};

export default Cockpit;
