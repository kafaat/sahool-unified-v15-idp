/**
 * Equipment Details Component
 * مكون تفاصيل المعدات
 */

'use client';

import Image from 'next/image';
import { useEquipmentDetails } from '../hooks/useEquipment';
import { Loader2, Wrench, Calendar, MapPin, DollarSign, Edit, Trash2 } from 'lucide-react';
import Link from 'next/link';

interface EquipmentDetailsProps {
  equipmentId: string;
}

// Include backend-side statuses (operational, inactive) as aliases — see
// equipment-service EquipmentStatus enum for the full set.
const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  operational: 'bg-green-100 text-green-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  repair: 'bg-orange-100 text-orange-800',
  idle: 'bg-gray-100 text-gray-800',
  inactive: 'bg-gray-100 text-gray-800',
  retired: 'bg-red-100 text-red-800',
};

const statusLabels: Record<string, string> = {
  active: 'نشط',
  operational: 'نشط',
  maintenance: 'صيانة',
  repair: 'إصلاح',
  idle: 'خامل',
  inactive: 'خامل',
  retired: 'متوقف',
};

const typeLabels: Record<string, string> = {
  tractor: 'جرار',
  harvester: 'حصادة',
  irrigation_system: 'نظام ري',
  sprayer: 'رشاش',
  planter: 'آلة زراعة',
  pump: 'مضخة',
  drone: 'طائرة بدون طيار',
  pivot: 'محور ري',
  sensor: 'مستشعر',
  vehicle: 'مركبة',
  other: 'أخرى',
};

const UNKNOWN_STATUS_CLASS = 'bg-gray-100 text-gray-700';
const UNKNOWN_LABEL = 'غير محدد';

/** Safe date formatter — guards against Invalid Date / NaN / null. */
function formatDateAr(value: string | number | Date | null | undefined): string {
  if (value === null || value === undefined || value === '') return UNKNOWN_LABEL;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return UNKNOWN_LABEL;
  return d.toLocaleDateString('ar-YE');
}

/** Safe number formatter — guards against non-numeric values. */
function formatNumberAr(value: unknown): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return UNKNOWN_LABEL;
  return value.toLocaleString('ar-YE');
}

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
            <button
              aria-label="حذف المعدة"
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusColors[equipment.status] ?? UNKNOWN_STATUS_CLASS
            }`}
          >
            {statusLabels[equipment.status] ?? UNKNOWN_LABEL}
          </span>
          <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
            {typeLabels[equipment.type] ?? UNKNOWN_LABEL}
          </span>
        </div>
      </div>

      {/* Image */}
      {equipment.imageUrl && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="relative w-full h-96">
            <Image
              src={equipment.imageUrl}
              alt={equipment.nameAr}
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 60vw"
              className="object-cover rounded-lg"
              priority
            />
          </div>
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

            {typeof equipment.totalOperatingHours === 'number' &&
              Number.isFinite(equipment.totalOperatingHours) && (
                <div>
                  <label className="text-sm text-gray-500">ساعات التشغيل</label>
                  <p className="text-gray-900">
                    {formatNumberAr(equipment.totalOperatingHours)} ساعة
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
              <p className="text-gray-900">{formatDateAr(equipment.purchaseDate)}</p>
            </div>

            {typeof equipment.purchasePrice === 'number' &&
              Number.isFinite(equipment.purchasePrice) && (
                <div>
                  <label className="text-sm text-gray-500">سعر الشراء</label>
                  <p className="text-gray-900">
                    {formatNumberAr(equipment.purchasePrice)} ريال
                  </p>
                </div>
              )}

            {typeof equipment.currentValue === 'number' &&
              Number.isFinite(equipment.currentValue) && (
                <div>
                  <label className="text-sm text-gray-500">القيمة الحالية</label>
                  <p className="text-gray-900">
                    {formatNumberAr(equipment.currentValue)} ريال
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
                خط العرض:{' '}
                {typeof equipment.location.latitude === 'number' &&
                Number.isFinite(equipment.location.latitude)
                  ? equipment.location.latitude.toFixed(6)
                  : UNKNOWN_LABEL}
              </p>
              <p className="text-sm text-gray-500">
                خط الطول:{' '}
                {typeof equipment.location.longitude === 'number' &&
                Number.isFinite(equipment.location.longitude)
                  ? equipment.location.longitude.toFixed(6)
                  : UNKNOWN_LABEL}
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
                <p className="text-gray-900">{formatDateAr(equipment.lastMaintenanceDate)}</p>
              </div>
            )}

            {equipment.nextMaintenanceDate && (() => {
              const nextDate = new Date(equipment.nextMaintenanceDate);
              const isValid = !Number.isNaN(nextDate.getTime());
              const isOverdue = isValid && nextDate < new Date();
              return (
                <div>
                  <label className="text-sm text-gray-500">الصيانة القادمة</label>
                  <p className={isOverdue ? 'text-red-600 font-semibold' : 'text-gray-900'}>
                    {formatDateAr(equipment.nextMaintenanceDate)}
                  </p>
                </div>
              );
            })()}
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
