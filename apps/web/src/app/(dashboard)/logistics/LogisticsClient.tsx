"use client";

import React, { useState, useEffect } from "react";
import { Truck, Package, MapPin, Clock, CheckCircle, AlertCircle, Calendar } from "lucide-react";

interface Shipment {
  id: string;
  orderNumber: string;
  origin: string;
  originAr: string;
  destination: string;
  destinationAr: string;
  status: "pending" | "in_transit" | "delivered" | "delayed";
  estimatedDelivery: string;
  cargo: string;
  cargoAr: string;
  weight: number;
  driver?: string;
}

const mockShipments: Shipment[] = [
  {
    id: "1",
    orderNumber: "SHP-2026-001",
    origin: "Riyadh Warehouse",
    originAr: "مستودع الرياض",
    destination: "Al-Kharj Farm",
    destinationAr: "مزرعة الخرج",
    status: "in_transit",
    estimatedDelivery: "2026-01-25",
    cargo: "Fertilizers",
    cargoAr: "أسمدة",
    weight: 2500,
    driver: "محمد العلي",
  },
  {
    id: "2",
    orderNumber: "SHP-2026-002",
    origin: "Dammam Port",
    originAr: "ميناء الدمام",
    destination: "Qassim Distribution",
    destinationAr: "توزيع القصيم",
    status: "pending",
    estimatedDelivery: "2026-01-27",
    cargo: "Agricultural Equipment",
    cargoAr: "معدات زراعية",
    weight: 5000,
  },
  {
    id: "3",
    orderNumber: "SHP-2026-003",
    origin: "Jeddah Hub",
    originAr: "مركز جدة",
    destination: "Taif Farms",
    destinationAr: "مزارع الطائف",
    status: "delivered",
    estimatedDelivery: "2026-01-24",
    cargo: "Seeds",
    cargoAr: "بذور",
    weight: 800,
    driver: "خالد السعيد",
  },
  {
    id: "4",
    orderNumber: "SHP-2026-004",
    origin: "Al-Ahsa Center",
    originAr: "مركز الأحساء",
    destination: "Hofuf Market",
    destinationAr: "سوق الهفوف",
    status: "delayed",
    estimatedDelivery: "2026-01-24",
    cargo: "Fresh Produce",
    cargoAr: "منتجات طازجة",
    weight: 1200,
    driver: "أحمد الفهد",
  },
];

export default function LogisticsClient() {
  const [shipments, setShipments] = useState<Shipment[]>(mockShipments);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setIsLoading(false), 500);
  }, []);

  const getStatusColor = (status: Shipment["status"]) => {
    const colors = {
      pending: "text-yellow-600 bg-yellow-100",
      in_transit: "text-blue-600 bg-blue-100",
      delivered: "text-green-600 bg-green-100",
      delayed: "text-red-600 bg-red-100",
    };
    return colors[status];
  };

  const getStatusLabel = (status: Shipment["status"]) => {
    const labels = {
      pending: "قيد الانتظار",
      in_transit: "في الطريق",
      delivered: "تم التسليم",
      delayed: "متأخر",
    };
    return labels[status];
  };

  const getStatusIcon = (status: Shipment["status"]) => {
    const icons = {
      pending: <Clock className="w-4 h-4" />,
      in_transit: <Truck className="w-4 h-4" />,
      delivered: <CheckCircle className="w-4 h-4" />,
      delayed: <AlertCircle className="w-4 h-4" />,
    };
    return icons[status];
  };

  const filteredShipments = filterStatus === "all"
    ? shipments
    : shipments.filter(s => s.status === filterStatus);

  const stats = {
    total: shipments.length,
    inTransit: shipments.filter(s => s.status === "in_transit").length,
    delivered: shipments.filter(s => s.status === "delivered").length,
    delayed: shipments.filter(s => s.status === "delayed").length,
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
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
            onChange={(e) => setFilterStatus(e.target.value)}
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
              <div className="text-lg font-bold text-purple-600">{stats.total}</div>
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
              <div className="text-lg font-bold text-blue-600">{stats.inTransit}</div>
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
              <div className="text-lg font-bold text-green-600">{stats.delivered}</div>
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
              <div className="text-lg font-bold text-red-600">{stats.delayed}</div>
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
          {filteredShipments.map((shipment) => (
            <div key={shipment.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-medium text-gray-900">{shipment.orderNumber}</span>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(shipment.status)}`}>
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
                      <div className="font-medium">{shipment.driver}</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
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
