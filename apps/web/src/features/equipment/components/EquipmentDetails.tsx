/**
 * Equipment Details Component
 * مكون تفاصيل المعدات
 */

'use client';

import { useEquipmentDetails } from '../hooks/useEquipment';
import { Loader2, Wrench, Calendar, MapPin, DollarSign, Edit, Trash2 } from 'lucide-react';
import Link from 'next/link';

interface EquipmentDetailsProps {
  equipmentId: string;
}

const statusColors = {
  active: 'bg-green-100 text-green-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  repair: 'bg-orange-100 text-orange-800',
  idle: 'bg-gray-100 text-gray-800',
  retired: 'bg-red-100 text-red-800',
};

const statusLabels = {
  active: 'نشط',
  maintenance: 'صيانة',
  repair: 'إصلاح',
  idle: 'خامل',
  retired: 'متوقف',
};

const typeLabels = {
  tractor: 'جرار',
  harvester: 'حصادة',
  irrigation_system: 'نظام ري',
  sprayer: 'رشاش',
  planter: 'آلة زراعة',
  other: 'أخرى',
};

export function EquipmentDetails({ equipmentId }: EquipmentDetailsProps) {
  const { data: equipment, isLoading, error } = useEquipmentDetails(equipmentId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="mr-3 text-gray-600">جاري التحميل...</span>
      </div>
    );
  }

  if (error || !equipment) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        حدث خطأ أثناء تحميل تفاصيل المعدات
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{equipment.nameAr}</h1>
            <p className="text-gray-600">{equipment.name}</p>
          </div>
          <div className="flex gap-2">
            <Link
              href={`/equipment/${equipment.id}/edit`}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Edit className="w-5 h-5" />
            </Link>
            <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusColors[equipment.status]
            }`}
          >
            {statusLabels[equipment.status]}
          </span>
          <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
            {typeLabels[equipment.type]}
          </span>
        </div>
      </div>

      {/* Image */}
      {equipment.imageUrl && (
        <div className="bg-white rounded-lg shadow p-6">
          <img
            src={equipment.imageUrl}
            alt={equipment.nameAr}
            className="w-full h-96 object-cover rounded-lg"
          />
        </div>
      )}

      {/* Main Info */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Wrench className="w-5 h-5 ml-2 text-green-600" />
            المعلومات الأساسية
          </h2>

          <div className="space-y-3">
            <div>
              <label className="text-sm text-gray-500">الرقم التسلسلي</label>
              <p className="text-gray-900">{equipment.serialNumber}</p>
            </div>

            {equipment.manufacturer && (
              <div>
                <label className="text-sm text-gray-500">الشركة المصنعة</label>
                <p className="text-gray-900">{equipment.manufacturer}</p>
              </div>
            )}

            {equipment.model && (
              <div>
                <label className="text-sm text-gray-500">الموديل</label>
                <p className="text-gray-900">{equipment.model}</p>
              </div>
            )}

            {equipment.fuelType && (
              <div>
                <label className="text-sm text-gray-500">نوع الوقود</label>
                <p className="text-gray-900">{equipment.fuelType}</p>
              </div>
            )}

            {equipment.totalOperatingHours && (
              <div>
                <label className="text-sm text-gray-500">ساعات التشغيل</label>
                <p className="text-gray-900">
                  {equipment.totalOperatingHours.toLocaleString('ar-YE')} ساعة
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Financial Info */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <DollarSign className="w-5 h-5 ml-2 text-green-600" />
            المعلومات المالية
          </h2>

          <div className="space-y-3">
            <div>
              <label className="text-sm text-gray-500">تاريخ الشراء</label>
              <p className="text-gray-900">
                {new Date(equipment.purchaseDate).toLocaleDateString('ar-YE')}
              </p>
            </div>

            {equipment.purchasePrice && (
              <div>
                <label className="text-sm text-gray-500">سعر الشراء</label>
                <p className="text-gray-900">
                  {equipment.purchasePrice.toLocaleString('ar-YE')} ريال
                </p>
              </div>
            )}

            {equipment.currentValue && (
              <div>
                <label className="text-sm text-gray-500">القيمة الحالية</label>
                <p className="text-gray-900">
                  {equipment.currentValue.toLocaleString('ar-YE')} ريال
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Location and Assignment */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Location */}
        {equipment.location && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <MapPin className="w-5 h-5 ml-2 text-green-600" />
              الموقع
            </h2>

            <div className="space-y-2">
              {equipment.location.fieldName && (
                <p className="text-gray-900">{equipment.location.fieldName}</p>
              )}
              <p className="text-sm text-gray-500">
                خط العرض: {equipment.location.latitude.toFixed(6)}
              </p>
              <p className="text-sm text-gray-500">
                خط الطول: {equipment.location.longitude.toFixed(6)}
              </p>
            </div>
          </div>
        )}

        {/* Maintenance Info */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Calendar className="w-5 h-5 ml-2 text-green-600" />
            معلومات الصيانة
          </h2>

          <div className="space-y-3">
            {equipment.lastMaintenanceDate && (
              <div>
                <label className="text-sm text-gray-500">آخر صيانة</label>
                <p className="text-gray-900">
                  {new Date(equipment.lastMaintenanceDate).toLocaleDateString('ar-YE')}
                </p>
              </div>
            )}

            {equipment.nextMaintenanceDate && (
              <div>
                <label className="text-sm text-gray-500">الصيانة القادمة</label>
                <p
                  className={
                    new Date(equipment.nextMaintenanceDate) < new Date()
                      ? 'text-red-600 font-semibold'
                      : 'text-gray-900'
                  }
                >
                  {new Date(equipment.nextMaintenanceDate).toLocaleDateString('ar-YE')}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Assignment */}
      {equipment.assignedTo && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">الإسناد</h2>
          <p className="text-gray-900">
            مُسند إلى: <span className="font-medium">{equipment.assignedTo.userName}</span>
          </p>
        </div>
      )}
    </div>
  );
}
