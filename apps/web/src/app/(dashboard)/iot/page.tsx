'use client';

/**
 * SAHOOL IoT & Sensors Page
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

export default function IoTPage() {
  const [selectedSensorId, setSelectedSensorId] = useState<string | null>(null);
  const { data: sensors, isLoading: sensorsLoading } = useSensors();
  const { data: actuators, isLoading: actuatorsLoading } = useActuators();
  const { data: alertRules, isLoading: alertRulesLoading } = useAlertRules();

  const activeSensors = sensors?.filter((s) => s.status === 'online').length || 0;
  const activeActuators = actuators?.filter((a) => a.status === 'online').length || 0;
  const activeAlerts = alertRules?.filter((r) => r.enabled).length || 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h1 className="text-3xl font-bold text-gray-900">إنترنت الأشياء والمستشعرات</h1>
        <p className="text-gray-600 mt-1">IoT & Sensors Management</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-xs text-gray-500">متصل</span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{activeSensors}</h3>
          <p className="text-sm text-gray-600">مستشعرات نشطة | Active Sensors</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Zap className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-xs text-gray-500">متصل</span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{activeActuators}</h3>
          <p className="text-sm text-gray-600">مشغلات نشطة | Active Actuators</p>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
            <span className="text-xs text-gray-500">مفعّل</span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{activeAlerts}</h3>
          <p className="text-sm text-gray-600">قواعد التنبيه | Alert Rules</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sensors Dashboard - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Sensors Dashboard */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">لوحة المستشعرات</h2>
            <p className="text-sm text-gray-600 mb-6">Sensors Dashboard</p>
            <SensorsDashboard onSensorClick={setSelectedSensorId} />
          </div>

          {/* Sensor Readings & Chart */}
          {selectedSensorId && (
            <SensorReadingsSection sensorId={selectedSensorId} />
          )}

          {/* Actuator Controls */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">التحكم بالمشغلات</h2>
            <p className="text-sm text-gray-600 mb-6">Actuator Controls</p>
            <ActuatorControls />
          </div>
        </div>

        {/* Alert Rules - 1/3 width */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">قواعد التنبيه</h2>
          <p className="text-sm text-gray-600 mb-6">Alert Rules</p>
          <AlertRules />
        </div>
      </div>
    </div>
  );
}

/**
 * Sensor Readings Section with Chart
 */
function SensorReadingsSection({ sensorId }: { sensorId: string }) {
  const { data: readings } = useSensorReadings({
    sensorId,
    limit: 50,
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
        sensorUnit={sensor.unit}
        sensorUnitAr={sensor.unitAr}
        showStats={true}
      />

      {/* Readings Table */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">قراءات {sensor.nameAr}</h2>
        <p className="text-sm text-gray-600 mb-6">Recent Readings - {sensor.name}</p>
        <SensorReadings sensorId={sensorId} limit={20} />
      </div>
    </>
  );
}
