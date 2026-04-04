'use client';

/**
 * SAHOOL Drone Fleet Management Client
 * إدارة أسطول الطائرات بدون طيار
 */

import React, { useState } from 'react';
import {
  Plane,
  Battery,
  Plus,
  Play,
  Pause,
  RotateCcw,
  Map,
} from 'lucide-react';

interface Drone {
  id: string;
  name: string;
  nameAr: string;
  model: string;
  status: 'idle' | 'in-flight' | 'charging' | 'maintenance';
  battery: number;
  lastMission: string;
  fieldId: string;
  fieldName: string;
  totalFlightHours: number;
}

interface Mission {
  id: string;
  droneId: string;
  droneName: string;
  type: 'survey' | 'spray' | 'vra' | 'mapping';
  typeAr: string;
  fieldName: string;
  status: 'planned' | 'active' | 'completed' | 'aborted';
  date: string;
  areaCovered: number;
  duration: number;
}

const MOCK_DRONES: Drone[] = [
  { id: 'DR-001', name: 'Falcon-1', nameAr: 'الصقر-1', model: 'DJI Agras T40', status: 'idle', battery: 92, lastMission: '2026-04-03', fieldId: 'F-003', fieldName: 'حقل القمح الشمالي', totalFlightHours: 245 },
  { id: 'DR-002', name: 'Falcon-2', nameAr: 'الصقر-2', model: 'DJI Matrice 350', status: 'in-flight', battery: 67, lastMission: '2026-04-04', fieldId: 'F-007', fieldName: 'حقل النخيل', totalFlightHours: 189 },
  { id: 'DR-003', name: 'Eagle-1', nameAr: 'النسر-1', model: 'DJI Agras T20P', status: 'charging', battery: 35, lastMission: '2026-04-02', fieldId: 'F-012', fieldName: 'حقل الطماطم', totalFlightHours: 312 },
  { id: 'DR-004', name: 'Hawk-1', nameAr: 'الباز-1', model: 'DJI Phantom 4 RTK', status: 'maintenance', battery: 0, lastMission: '2026-03-28', fieldId: 'F-001', fieldName: 'حقل الشعير', totalFlightHours: 410 },
];

const MOCK_MISSIONS: Mission[] = [
  { id: 'MS-101', droneId: 'DR-002', droneName: 'الصقر-2', type: 'survey', typeAr: 'مسح جوي', fieldName: 'حقل النخيل', status: 'active', date: '2026-04-04', areaCovered: 12.5, duration: 35 },
  { id: 'MS-100', droneId: 'DR-001', droneName: 'الصقر-1', type: 'vra', typeAr: 'رش متغير المعدل', fieldName: 'حقل القمح الشمالي', status: 'completed', date: '2026-04-03', areaCovered: 8.2, duration: 45 },
  { id: 'MS-099', droneId: 'DR-003', droneName: 'النسر-1', type: 'spray', typeAr: 'رش مبيدات', fieldName: 'حقل الطماطم', status: 'completed', date: '2026-04-02', areaCovered: 5.0, duration: 28 },
  { id: 'MS-098', droneId: 'DR-001', droneName: 'الصقر-1', type: 'mapping', typeAr: 'خرائط تضاريس', fieldName: 'حقل الشعير', status: 'completed', date: '2026-04-01', areaCovered: 15.0, duration: 55 },
  { id: 'MS-097', droneId: 'DR-004', droneName: 'الباز-1', type: 'survey', typeAr: 'مسح جوي', fieldName: 'حقل القمح الجنوبي', status: 'aborted', date: '2026-03-28', areaCovered: 3.1, duration: 12 },
];

const statusColors: Record<string, string> = {
  'idle': 'bg-gray-100 text-gray-700',
  'in-flight': 'bg-green-100 text-green-700',
  'charging': 'bg-blue-100 text-blue-700',
  'maintenance': 'bg-orange-100 text-orange-700',
};

const statusLabels: Record<string, string> = {
  'idle': 'جاهز',
  'in-flight': 'في الطيران',
  'charging': 'قيد الشحن',
  'maintenance': 'صيانة',
};

const missionStatusColors: Record<string, string> = {
  'planned': 'bg-blue-100 text-blue-700',
  'active': 'bg-green-100 text-green-700',
  'completed': 'bg-gray-100 text-gray-700',
  'aborted': 'bg-red-100 text-red-700',
};

const missionStatusLabels: Record<string, string> = {
  'planned': 'مخطط',
  'active': 'نشط',
  'completed': 'مكتمل',
  'aborted': 'ملغى',
};

export default function DroneClient() {
  const [activeTab, setActiveTab] = useState<'fleet' | 'missions'>('fleet');

  const stats = {
    total: MOCK_DRONES.length,
    inFlight: MOCK_DRONES.filter(d => d.status === 'in-flight').length,
    idle: MOCK_DRONES.filter(d => d.status === 'idle').length,
    totalMissions: MOCK_MISSIONS.length,
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الطائرات بدون طيار</h1>
            <p className="text-gray-600 mt-1">Drone Fleet Management</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-5 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-semibold">
              <Map className="w-5 h-5" />
              <span>خريطة VRA</span>
            </button>
            <button className="flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
              <Plus className="w-5 h-5" />
              <span>مهمة جديدة</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Plane className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">إجمالي الطائرات</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Play className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">في الطيران</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{stats.inFlight}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Pause className="w-5 h-5 text-gray-600" />
            <p className="text-sm text-gray-600">جاهزة للطيران</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.idle}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <RotateCcw className="w-5 h-5 text-purple-600" />
            <p className="text-sm text-gray-600">إجمالي المهمات</p>
          </div>
          <p className="text-3xl font-bold text-purple-600">{stats.totalMissions}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl border-2 border-gray-200">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('fleet')}
            className={`px-6 py-4 font-semibold text-sm transition-colors ${activeTab === 'fleet' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            الأسطول
          </button>
          <button
            onClick={() => setActiveTab('missions')}
            className={`px-6 py-4 font-semibold text-sm transition-colors ${activeTab === 'missions' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            المهمات
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'fleet' ? (
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">الطائرة</th>
                  <th className="pb-3 pr-4 font-medium">الموديل</th>
                  <th className="pb-3 pr-4 font-medium">الحالة</th>
                  <th className="pb-3 pr-4 font-medium">البطارية</th>
                  <th className="pb-3 pr-4 font-medium">الحقل</th>
                  <th className="pb-3 pr-4 font-medium">ساعات الطيران</th>
                  <th className="pb-3 font-medium">إجراءات</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_DRONES.map(drone => (
                  <tr key={drone.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4">
                      <p className="font-semibold text-gray-900">{drone.nameAr}</p>
                      <p className="text-xs text-gray-500">{drone.id}</p>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{drone.model}</td>
                    <td className="py-4 pr-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[drone.status]}`}>
                        {statusLabels[drone.status]}
                      </span>
                    </td>
                    <td className="py-4 pr-4">
                      <div className="flex items-center gap-2">
                        <Battery className={`w-4 h-4 ${drone.battery > 50 ? 'text-green-600' : drone.battery > 20 ? 'text-orange-500' : 'text-red-500'}`} />
                        <span className="text-sm">{drone.battery}%</span>
                      </div>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{drone.fieldName}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{drone.totalFlightHours} س</td>
                    <td className="py-4">
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">تفاصيل</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">المهمة</th>
                  <th className="pb-3 pr-4 font-medium">النوع</th>
                  <th className="pb-3 pr-4 font-medium">الطائرة</th>
                  <th className="pb-3 pr-4 font-medium">الحقل</th>
                  <th className="pb-3 pr-4 font-medium">الحالة</th>
                  <th className="pb-3 pr-4 font-medium">المساحة (هـ)</th>
                  <th className="pb-3 pr-4 font-medium">المدة (د)</th>
                  <th className="pb-3 font-medium">التاريخ</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_MISSIONS.map(mission => (
                  <tr key={mission.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4 text-sm font-semibold text-gray-900">{mission.id}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{mission.typeAr}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{mission.droneName}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{mission.fieldName}</td>
                    <td className="py-4 pr-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${missionStatusColors[mission.status]}`}>
                        {missionStatusLabels[mission.status]}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{mission.areaCovered}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{mission.duration}</td>
                    <td className="py-4 text-sm text-gray-700">{mission.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
