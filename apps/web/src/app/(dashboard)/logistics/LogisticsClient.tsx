'use client';

import React, { useState, useMemo } from 'react';
import {
  Truck,
  Package,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle,
  Calendar,
  AlertTriangle,
} from 'lucide-react';
import { useShipments, useLogisticsStats } from '@/features/logistics';
import type { Shipment, ShipmentStatus } from '@/features/logistics';

export default function LogisticsClient() {
  const [filterStatus, setFilterStatus] = useState<ShipmentStatus | 'all'>('all');

  // Fetch data using React Query hooks
  const {
    data: shipments = [],
    isLoading,
    error,
  } = useShipments(filterStatus !== 'all' ? { status: filterStatus } : undefined);
  const { data: stats } = useLogisticsStats();

  const getStatusColor = (status: Shipment['status']) => {
    const colors: Record<Shipment['status'], string> = {
      pending: 'text-yellow-600 bg-yellow-100',
      in_transit: 'text-blue-600 bg-blue-100',
      delivered: 'text-green-600 bg-green-100',
      delayed: 'text-red-600 bg-red-100',
      cancelled: 'text-gray-600 bg-gray-100',
    };
    return colors[status];
  };

  const getStatusLabel = (status: Shipment['status']) => {
    const labels: Record<Shipment['status'], string> = {
      pending: 'قيد الانتظار',
      in_transit: 'في الطريق',
      delivered: 'تم التسليم',
      delayed: 'متأخر',
      cancelled: 'ملغي',
    };
    return labels[status];
  };

  const getStatusIcon = (status: Shipment['status']) => {
    const icons: Record<Shipment['status'], React.ReactNode> = {
      pending: <Clock className="w-4 h-4" />,
      in_transit: <Truck className="w-4 h-4" />,
      delivered: <CheckCircle className="w-4 h-4" />,
      delayed: <AlertCircle className="w-4 h-4" />,
      cancelled: <AlertCircle className="w-4 h-4" />,
    };
    return icons[status];
  };

  const localStats = useMemo(
    () => ({
      total: shipments.length,
      inTransit: shipments.filter((s) => s.status === 'in_transit').length,
      delivered: shipments.filter((s) => s.status === 'delivered').length,
      delayed: shipments.filter((s) => s.status === 'delayed').length,
    }),
    [shipments]
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات اللوجستيات</p>
          <p className="text-gray-500 text-sm">Failed to load logistics data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة اللوجستيات</h1>
          <p className="text-gray-500 mt-1">Logistics & Transportation Management</p>
        </div>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as ShipmentStatus | 'all')}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          >
            <option value="all">جميع الحالات</option>
            <option value="pending">قيد الانتظار</option>
            <option value="in_transit">في الطريق</option>
            <option value="delivered">تم التسليم</option>
            <option value="delayed">متأخر</option>
          </select>
          <button className="px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
            + شحنة جديدة
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الشحنات</div>
              <div className="text-lg font-bold text-purple-600">
                {stats?.totalShipments ?? localStats.total}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Truck className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">في الطريق</div>
              <div className="text-lg font-bold text-blue-600">
                {stats?.inTransitShipments ?? localStats.inTransit}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تم التسليم</div>
              <div className="text-lg font-bold text-green-600">
                {stats?.deliveredShipments ?? localStats.delivered}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متأخرة</div>
              <div className="text-lg font-bold text-red-600">
                {stats?.delayedShipments ?? localStats.delayed}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Shipments List */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">الشحنات</h2>
        </div>
        <div className="divide-y">
          {shipments.length === 0 ? (
            <div className="p-8 text-center text-gray-500">لا توجد شحنات</div>
          ) : (
            shipments.map((shipment) => (
              <div key={shipment.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-gray-900">{shipment.orderNumber}</span>
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(shipment.status)}`}
                      >
                        {getStatusIcon(shipment.status)}
                        {getStatusLabel(shipment.status)}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin className="w-4 h-4" />
                        <span>من: {shipment.originAr}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin className="w-4 h-4" />
                        <span>إلى: {shipment.destinationAr}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col md:flex-row gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">البضاعة</div>
                      <div className="font-medium">{shipment.cargoAr}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">الوزن</div>
                      <div className="font-medium">{shipment.weight.toLocaleString()} كجم</div>
                    </div>
                    <div>
                      <div className="text-gray-500">التسليم المتوقع</div>
                      <div className="font-medium flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {shipment.estimatedDelivery}
                      </div>
                    </div>
                    {shipment.driver && (
                      <div>
                        <div className="text-gray-500">السائق</div>
                        <div className="font-medium">{shipment.driver.name}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Map Placeholder */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">خريطة التتبع</h2>
        </div>
        <div className="aspect-video bg-gradient-to-br from-blue-100 via-blue-200 to-blue-300 flex items-center justify-center">
          <div className="text-center">
            <Truck className="w-16 h-16 text-blue-700 mx-auto mb-4" />
            <p className="text-blue-800 font-medium">خريطة تتبع الشحنات</p>
            <p className="text-blue-700 text-sm">Real-time Shipment Tracking</p>
          </div>
        </div>
      </div>
    </div>
  );
}
