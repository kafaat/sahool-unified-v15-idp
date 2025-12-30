/**
 * Equipment Card Component
 * مكون بطاقة المعدات
 */

'use client';

import Link from 'next/link';
import type { Equipment } from '../types';
import { Wrench, Calendar, MapPin, TrendingUp } from 'lucide-react';

interface EquipmentCardProps {
  equipment: Equipment;
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

export function EquipmentCard({ equipment }: EquipmentCardProps) {
  const maintenanceDue = equipment.nextMaintenanceDate
    ? new Date(equipment.nextMaintenanceDate) < new Date()
    : false;

  return (
    <Link href={`/equipment/${equipment.id}`}>
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 space-y-4 cursor-pointer">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{equipment.nameAr}</h3>
            <p className="text-sm text-gray-500">{equipment.name}</p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              statusColors[equipment.status]
            }`}
          >
            {statusLabels[equipment.status]}
          </span>
        </div>

        {/* Image or Placeholder */}
        {equipment.imageUrl ? (
          <img
            src={equipment.imageUrl}
            alt={equipment.nameAr}
            className="w-full h-48 object-cover rounded-lg"
          />
        ) : (
          <div className="w-full h-48 bg-gradient-to-br from-green-100 to-green-200 rounded-lg flex items-center justify-center">
            <Wrench className="w-16 h-16 text-green-600 opacity-50" />
          </div>
        )}

        {/* Details */}
        <div className="space-y-2">
          <div className="flex items-center text-sm text-gray-600">
            <TrendingUp className="w-4 h-4 ml-2" />
            <span>{typeLabels[equipment.type]}</span>
          </div>

          {equipment.location && (
            <div className="flex items-center text-sm text-gray-600">
              <MapPin className="w-4 h-4 ml-2" />
              <span>{equipment.location.fieldName || 'موقع المعدة'}</span>
            </div>
          )}

          {equipment.nextMaintenanceDate && (
            <div
              className={`flex items-center text-sm ${
                maintenanceDue ? 'text-red-600' : 'text-gray-600'
              }`}
            >
              <Calendar className="w-4 h-4 ml-2" />
              <span>
                الصيانة القادمة:{' '}
                {new Date(equipment.nextMaintenanceDate).toLocaleDateString('ar-YE')}
              </span>
            </div>
          )}

          {equipment.totalOperatingHours && (
            <div className="text-sm text-gray-600">
              ساعات التشغيل: {equipment.totalOperatingHours.toLocaleString('ar-YE')} ساعة
            </div>
          )}
        </div>

        {/* Footer */}
        {equipment.assignedTo && (
          <div className="pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500">
              مُسند إلى: <span className="text-gray-700">{equipment.assignedTo.userName}</span>
            </p>
          </div>
        )}

        {maintenanceDue && (
          <div className="bg-red-50 border border-red-200 rounded p-2 text-xs text-red-800">
            تنبيه: الصيانة متأخرة!
          </div>
        )}
      </div>
    </Link>
  );
}
