'use client';

/**
 * SAHOOL Equipment Management Page
 * صفحة إدارة المعدات
 */

import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import {
  EquipmentList,
  EquipmentDetails,
  EquipmentForm,
  MaintenanceSchedule,
  useEquipmentStats,
  useEquipmentDetails,
} from '@/features/equipment';

export default function EquipmentClient() {
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const { data: stats, isLoading: statsLoading } = useEquipmentStats();
  const { data: selectedEquipment } = useEquipmentDetails(selectedEquipmentId || '');

  // const handleEquipmentClick = (equipmentId: string) => {
  //   setSelectedEquipmentId(equipmentId);
  //   setShowForm(false);
  // };

  const handleCreateClick = () => {
    setShowForm(true);
    setSelectedEquipmentId(null);
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setSelectedEquipmentId(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">إدارة المعدات</h1>
            <p className="text-gray-600 mt-1">Equipment Management</p>
          </div>
          <button
            onClick={handleCreateClick}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            <Plus className="w-5 h-5" />
            <span>إضافة معدة</span>
          </button>
        </div>
      </div>

      {/* Equipment Statistics */}
      {!statsLoading && stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">إجمالي المعدات</p>
            <p className="text-3xl font-bold text-gray-900">{stats.total || 0}</p>
          </div>
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">قيد التشغيل</p>
            <p className="text-3xl font-bold text-green-600">{stats.byStatus?.['active'] || 0}</p>
          </div>
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">قيد الصيانة</p>
            <p className="text-3xl font-bold text-orange-600">{stats.byStatus?.['maintenance'] || 0}</p>
          </div>
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">بحاجة لصيانة</p>
            <p className="text-3xl font-bold text-red-600">{stats.maintenanceDue || 0}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Equipment List - 2/3 width */}
        <div className="lg:col-span-2">
          {showForm ? (
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                {selectedEquipmentId ? 'تعديل معدة' : 'إضافة معدة جديدة'}
              </h2>
              <EquipmentForm
                equipment={selectedEquipment}
                onSuccess={handleFormSuccess}
                onCancel={() => setShowForm(false)}
              />
            </div>
          ) : selectedEquipmentId ? (
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="mb-4">
                <button
                  onClick={() => setSelectedEquipmentId(null)}
                  className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  ← العودة للقائمة
                </button>
              </div>
              <EquipmentDetails
                equipmentId={selectedEquipmentId}
              />
            </div>
          ) : (
            <EquipmentList />
          )}
        </div>

        {/* Maintenance Schedule - 1/3 width */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">جدول الصيانة</h2>
          <p className="text-sm text-gray-600 mb-6">Maintenance Schedule</p>
          <MaintenanceSchedule />
        </div>
      </div>
    </div>
  );
}
