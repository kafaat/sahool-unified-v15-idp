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
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { useDroneFlights, useDroneDevices } from '../hooks/useDrone';

const statusColors: Record<string, string> = {
  'available': 'bg-gray-100 text-gray-700',
  'idle': 'bg-gray-100 text-gray-700',
  'in_flight': 'bg-green-100 text-green-700',
  'in-flight': 'bg-green-100 text-green-700',
  'charging': 'bg-blue-100 text-blue-700',
  'maintenance': 'bg-orange-100 text-orange-700',
  'offline': 'bg-red-100 text-red-700',
};

const statusLabels: Record<string, string> = {
  'available': 'جاهز',
  'idle': 'جاهز',
  'in_flight': 'في الطيران',
  'in-flight': 'في الطيران',
  'charging': 'قيد الشحن',
  'maintenance': 'صيانة',
  'offline': 'غير متصل',
};

const missionStatusColors: Record<string, string> = {
  'planned': 'bg-blue-100 text-blue-700',
  'in_progress': 'bg-green-100 text-green-700',
  'active': 'bg-green-100 text-green-700',
  'completed': 'bg-gray-100 text-gray-700',
  'failed': 'bg-red-100 text-red-700',
  'cancelled': 'bg-red-100 text-red-700',
  'aborted': 'bg-red-100 text-red-700',
};

const missionStatusLabels: Record<string, string> = {
  'planned': 'مخطط',
  'in_progress': 'نشط',
  'active': 'نشط',
  'completed': 'مكتمل',
  'failed': 'فشل',
  'cancelled': 'ملغى',
  'aborted': 'ملغى',
};

const missionTypeLabels: Record<string, string> = {
  'survey': 'مسح جوي',
  'spray': 'رش مبيدات',
  'mapping': 'خرائط تضاريس',
  'inspection': 'فحص',
  'vra': 'رش متغير المعدل',
};

export default function DroneClient() {
  const [activeTab, setActiveTab] = useState<'fleet' | 'missions'>('fleet');

  const {
    data: flights = [],
    isLoading: isLoadingFlights,
    isError: isFlightsError,
    error: flightsError,
  } = useDroneFlights();

  const {
    data: devices = [],
    isLoading: isLoadingDevices,
    isError: isDevicesError,
    error: devicesError,
  } = useDroneDevices();

  const isLoading = isLoadingFlights || isLoadingDevices;
  const isError = isFlightsError || isDevicesError;
  const errorMsg = flightsError ?? devicesError;

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-600 font-medium">جاري تحميل بيانات الطائرات...</p>
          <p className="text-sm text-gray-400 mt-1">Loading drone data...</p>
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
            فشل في تحميل بيانات الطائرات
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            {errorMsg instanceof Error ? errorMsg.message : 'Failed to load drone data'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  const stats = {
    total: devices.length,
    inFlight: devices.filter((d) => d.status === 'in_flight').length,
    idle: devices.filter((d) => d.status === 'available').length,
    totalMissions: flights.length,
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
            devices.length === 0 ? (
              <div className="text-center py-12">
                <Plane className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد طائرات مسجلة</h3>
                <p className="text-gray-500 text-sm">No drones registered yet</p>
              </div>
            ) : (
              <table className="w-full text-right">
                <thead>
                  <tr className="border-b border-gray-200 text-sm text-gray-500">
                    <th className="pb-3 pr-4 font-medium">الطائرة</th>
                    <th className="pb-3 pr-4 font-medium">الموديل</th>
                    <th className="pb-3 pr-4 font-medium">الحالة</th>
                    <th className="pb-3 pr-4 font-medium">البطارية</th>
                    <th className="pb-3 pr-4 font-medium">ساعات الطيران</th>
                    <th className="pb-3 font-medium">إجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.map((drone) => (
                    <tr key={drone.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 pr-4">
                        <p className="font-semibold text-gray-900">{drone.nameAr}</p>
                        <p className="text-xs text-gray-500">{drone.id}</p>
                      </td>
                      <td className="py-4 pr-4 text-sm text-gray-700">
                        {drone.manufacturer} {drone.model}
                      </td>
                      <td className="py-4 pr-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[drone.status] ?? 'bg-gray-100 text-gray-700'}`}>
                          {statusLabels[drone.status] ?? drone.status}
                        </span>
                      </td>
                      <td className="py-4 pr-4">
                        <div className="flex items-center gap-2">
                          <Battery className={`w-4 h-4 ${drone.battery > 50 ? 'text-green-600' : drone.battery > 20 ? 'text-orange-500' : 'text-red-500'}`} />
                          <span className="text-sm">{drone.battery}%</span>
                        </div>
                      </td>
                      <td className="py-4 pr-4 text-sm text-gray-700">{drone.totalFlightHours} س</td>
                      <td className="py-4">
                        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">تفاصيل</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          ) : flights.length === 0 ? (
            <div className="text-center py-12">
              <Map className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد مهمات</h3>
              <p className="text-gray-500 text-sm">No missions recorded yet</p>
            </div>
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
                {flights.map((flight) => (
                  <tr key={flight.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4 text-sm font-semibold text-gray-900">{flight.id}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">
                      {missionTypeLabels[flight.missionType] ?? flight.missionType}
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{flight.droneName}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">
                      {flight.fieldNameAr ?? flight.fieldName}
                    </td>
                    <td className="py-4 pr-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${missionStatusColors[flight.status] ?? 'bg-gray-100 text-gray-700'}`}>
                        {missionStatusLabels[flight.status] ?? flight.status}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{flight.coverage ?? '-'}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{flight.duration ?? '-'}</td>
                    <td className="py-4 text-sm text-gray-700">
                      {flight.startedAt
                        ? new Date(flight.startedAt).toLocaleDateString('ar-SA')
                        : new Date(flight.createdAt).toLocaleDateString('ar-SA')}
                    </td>
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
