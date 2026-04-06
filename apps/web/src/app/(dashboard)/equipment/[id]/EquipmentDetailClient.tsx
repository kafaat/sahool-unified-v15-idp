'use client';

/**
 * SAHOOL Equipment Detail Client Component
 * مكون تفاصيل المعدات
 */

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Loader2, AlertTriangle } from 'lucide-react';
import { EquipmentDetails, MaintenanceSchedule } from '@/features/equipment';

interface EquipmentDetailClientProps {
  equipmentId: string;
}

export default function EquipmentDetailClient({ equipmentId }: EquipmentDetailClientProps) {
  if (!equipmentId) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">معرف المعدة غير صالح</h2>
            <p className="text-gray-600 mb-6">Invalid equipment ID</p>
            <Link
              href="/equipment"
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              <ArrowRight className="w-5 h-5" />
              <span>العودة لقائمة المعدات</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">تفاصيل المعدات</h1>
            <p className="text-gray-600 mt-1">Equipment Details</p>
          </div>
          <Link
            href="/equipment"
            className="flex items-center gap-2 px-6 py-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
          >
            <ArrowRight className="w-5 h-5" />
            <span>العودة لقائمة المعدات</span>
          </Link>
        </div>
      </div>

      {/* Equipment Details */}
      <EquipmentDetails equipmentId={equipmentId} />

      {/* Maintenance History */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">سجل الصيانة</h2>
        <p className="text-sm text-gray-600 mb-6">Maintenance History</p>
        <MaintenanceSchedule equipmentId={equipmentId} />
      </div>
    </div>
  );
}
