'use client';

/**
 * SAHOOL IoT & Sensors Page Client Component
 * صفحة إنترنت الأشياء والمستشعرات
 */

import React, { useState } from 'react';
import { Activity, Zap, AlertTriangle } from 'lucide-react';
import {
  SensorsDashboard,
  SensorReadings,
  SensorChart,
  ActuatorControls,
  AlertRules,
  useSensors,
  useSensorReadings,
  useActuators,
  useAlertRules,
} from '@/features/iot';

/**
 * Sensor Readings Section with Chart
 */
function SensorReadingsSection({ sensorId }: { sensorId: string }) {
  const { data: readings } = useSensorReadings({
    sensorId,
  });
  const { data: sensors } = useSensors();
  const sensor = sensors?.find((s) => s.id === sensorId);

  if (!sensor || !readings) return null;

  return (
    <>
      {/* Chart */}
      <SensorChart
        readings={readings}
        sensorType={sensor.type}
        sensorUnit={sensor.lastReading?.unit || ''}
        sensorUnitAr={sensor.lastReading?.unit || ''}
        showStats={true}
      />

      {/* Readings Table */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">قراءات {sensor.nameAr}</h2>
        <p className="text-sm text-gray-600 mb-6">Recent Readings - {sensor.name}</p>
        <SensorReadings sensorId={sensorId} sensorName={sensor.name} unit={sensor.lastReading?.unit || ''} />
      </div>
    </>
  );
}

export default function IoTClient() {
  const [selectedSensorId, setSelectedSensorId] = useState<string | null>(null);
  const { data: sensors } = useSensors();
  const { data: actuators } = useActuators();
  const { data: alertRules } = useAlertRules();

  const activeSensors = sensors?.filter((s) => s.status === 'active').length || 0;
  const activeActuators = actuators?.filter((a) => a.status === 'on').length || 0;
  const activeAlerts = alertRules?.filter((r) => r.enabled).length || 0;

  return (
    <div className="space-y-6" data-testid="iot-page">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="page-header">
        <h1 className="text-3xl font-bold text-gray-900" data-testid="page-title">إنترنت الأشياء والمستشعرات</h1>
        <p className="text-gray-600 mt-1" data-testid="page-subtitle">IoT & Sensors Management</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="statistics-grid">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="stat-card-sensors">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg" data-testid="sensor-icon">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-xs text-gray-500" data-testid="sensor-status">متصل</span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1" data-testid="active-sensors-count">{activeSensors}</h3>
          <p className="text-sm text-gray-600" data-testid="sensor-label">مستشعرات نشطة | Active Sensors</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="stat-card-actuators">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg" data-testid="actuator-icon">
              <Zap className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-xs text-gray-500" data-testid="actuator-status">متصل</span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1" data-testid="active-actuators-count">{activeActuators}</h3>
          <p className="text-sm text-gray-600" data-testid="actuator-label">مشغلات نشطة | Active Actuators</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="stat-card-alerts">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg" data-testid="alert-icon">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
            <span className="text-xs text-gray-500" data-testid="alert-status">مفعّل</span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1" data-testid="active-alerts-count">{activeAlerts}</h3>
          <p className="text-sm text-gray-600" data-testid="alert-label">قواعد التنبيه | Alert Rules</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" data-testid="main-content-grid">
        {/* Sensors Dashboard - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Sensors Dashboard */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="sensors-dashboard-section">
            <h2 className="text-xl font-bold text-gray-900 mb-4" data-testid="sensors-dashboard-title">لوحة المستشعرات</h2>
            <p className="text-sm text-gray-600 mb-6" data-testid="sensors-dashboard-subtitle">Sensors Dashboard</p>
            <SensorsDashboard onSensorClick={setSelectedSensorId} />
          </div>

          {/* Sensor Readings & Chart */}
          {selectedSensorId && (
            <SensorReadingsSection sensorId={selectedSensorId} />
          )}

          {/* Actuator Controls */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="actuator-controls-section">
            <h2 className="text-xl font-bold text-gray-900 mb-4" data-testid="actuator-controls-title">التحكم بالمشغلات</h2>
            <p className="text-sm text-gray-600 mb-6" data-testid="actuator-controls-subtitle">Actuator Controls</p>
            <ActuatorControls />
          </div>
        </div>

        {/* Alert Rules - 1/3 width */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="alert-rules-section">
          <h2 className="text-xl font-bold text-gray-900 mb-4" data-testid="alert-rules-title">قواعد التنبيه</h2>
          <p className="text-sm text-gray-600 mb-6" data-testid="alert-rules-subtitle">Alert Rules</p>
          <AlertRules />
        </div>
      </div>
    </div>
  );
}
