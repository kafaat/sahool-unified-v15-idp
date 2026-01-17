/**
 * SAHOOL Health Zones Layer - Usage Example
 * مثال على استخدام مكون طبقة مناطق الصحة
 *
 * This example demonstrates how to use the HealthZonesLayer component
 * to display field health zones on a map with NDVI-based color coding.
 *
 * يوضح هذا المثال كيفية استخدام مكون HealthZonesLayer
 * لعرض مناطق صحة الحقل على الخريطة مع ترميز الألوان بناءً على NDVI
 */

"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  HealthZonesLayer,
  type FieldZone,
} from "../components/HealthZonesLayer";

// Dynamic imports for react-leaflet to avoid SSR issues
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false },
) as any;

const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false },
) as any;

// ═══════════════════════════════════════════════════════════════════════════
// Sample Data - بيانات تجريبية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * بيانات مناطق تجريبية للحقل
 * Sample field zones data
 */
const sampleZones: FieldZone[] = [
  {
    id: "zone-1",
    name: "المنطقة الشمالية",
    boundary: [
      [15.5527, 48.5164],
      [15.5537, 48.5174],
      [15.5527, 48.5184],
      [15.5517, 48.5174],
    ],
    ndviValue: 0.75,
    healthStatus: "excellent",
    area: 2.5,
  },
  {
    id: "zone-2",
    name: "المنطقة الوسطى",
    boundary: [
      [15.5517, 48.5174],
      [15.5527, 48.5184],
      [15.5517, 48.5194],
      [15.5507, 48.5184],
    ],
    ndviValue: 0.52,
    healthStatus: "moderate",
    area: 3.2,
  },
  {
    id: "zone-3",
    name: "المنطقة الجنوبية",
    boundary: [
      [15.5507, 48.5184],
      [15.5517, 48.5194],
      [15.5507, 48.5204],
      [15.5497, 48.5194],
    ],
    ndviValue: 0.32,
    healthStatus: "poor",
    area: 1.8,
  },
  {
    id: "zone-4",
    name: "المنطقة الشرقية",
    boundary: [
      [15.5527, 48.5184],
      [15.5537, 48.5194],
      [15.5527, 48.5204],
      [15.5517, 48.5194],
    ],
    ndviValue: 0.68,
    healthStatus: "good",
    area: 2.1,
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// Example Component - مكون المثال
// ═══════════════════════════════════════════════════════════════════════════

export default function HealthZonesLayerExample() {
  const [isMounted, setIsMounted] = useState(false);
  const [selectedZoneId, setSelectedZoneId] = useState<string | undefined>();
  const [showLabels, setShowLabels] = useState(true);
  const [showTooltips, setShowTooltips] = useState(true);

  // Handle mount state for SSR
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Handle zone click
  const handleZoneClick = (zone: FieldZone) => {
    console.log("Zone clicked:", zone);
    setSelectedZoneId(zone.id);

    // يمكنك هنا فتح modal أو عرض تفاصيل إضافية
    // Here you can open a modal or display additional details
    alert(
      `تم النقر على: ${zone.name}\nNDVI: ${zone.ndviValue}\nالصحة: ${zone.healthStatus}`,
    );
  };

  if (!isMounted) {
    return (
      <div className="bg-gray-100 animate-pulse rounded-lg h-[600px] flex items-center justify-center">
        <p className="text-gray-500">جاري تحميل الخريطة...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4" dir="rtl">
      {/* العنوان والوصف - Header and Description */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          مثال على طبقة مناطق الصحة
        </h1>
        <p className="text-gray-600">
          هذا المثال يوضح كيفية استخدام مكون HealthZonesLayer لعرض مناطق الحقل
          بألوان مختلفة بناءً على قيم NDVI. انقر على أي منطقة لعرض تفاصيلها.
        </p>
      </div>

      {/* عناصر التحكم - Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          إعدادات العرض
        </h2>
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showLabels}
              onChange={(e) => setShowLabels(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <span className="text-sm text-gray-700">عرض التسميات</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showTooltips}
              onChange={(e) => setShowTooltips(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <span className="text-sm text-gray-700">عرض التلميحات</span>
          </label>

          <button
            onClick={() => setSelectedZoneId(undefined)}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300 transition-colors"
          >
            إلغاء التحديد
          </button>
        </div>
      </div>

      {/* المنطقة المحددة - Selected Zone Info */}
      {selectedZoneId && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-900 mb-2">
            المنطقة المحددة:
          </h3>
          <p className="text-green-800">
            {sampleZones.find((z) => z.id === selectedZoneId)?.name}
          </p>
        </div>
      )}

      {/* الخريطة - Map */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="h-[600px]">
          <MapContainer
            center={[15.5517, 48.5184]}
            zoom={14}
            style={{ height: "100%", width: "100%" }}
            scrollWheelZoom={true}
          >
            {/* طبقة الخريطة الأساسية - Base Tile Layer */}
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* طبقة مناطق الصحة - Health Zones Layer */}
            <HealthZonesLayer
              zones={sampleZones}
              selectedZoneId={selectedZoneId}
              onZoneClick={handleZoneClick}
              showLabels={showLabels}
              showTooltips={showTooltips}
            />
          </MapContainer>
        </div>
      </div>

      {/* دليل الألوان - Color Legend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          دليل الألوان - ترميز NDVI
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-green-500"></div>
            <div>
              <p className="font-semibold text-gray-900">أخضر - صحة ممتازة</p>
              <p className="text-sm text-gray-600">NDVI &gt; 0.6</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-yellow-500"></div>
            <div>
              <p className="font-semibold text-gray-900">أصفر - صحة متوسطة</p>
              <p className="text-sm text-gray-600">NDVI 0.4 - 0.6</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-red-500"></div>
            <div>
              <p className="font-semibold text-gray-900">أحمر - صحة ضعيفة</p>
              <p className="text-sm text-gray-600">NDVI &lt; 0.4</p>
            </div>
          </div>
        </div>
      </div>

      {/* ملاحظات الاستخدام - Usage Notes */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">
          ملاحظات الاستخدام
        </h2>
        <ul className="space-y-2 text-blue-800 text-sm">
          <li>• يجب أن تكون الإحداثيات بتنسيق [lat, lng]</li>
          <li>• قيم NDVI يجب أن تكون بين -1 و 1</li>
          <li>• كل منطقة يجب أن تحتوي على 3 نقاط على الأقل</li>
          <li>• استخدم dynamic imports لتجنب مشاكل SSR</li>
          <li>• يدعم المكون RTL للغة العربية</li>
        </ul>
      </div>

      {/* كود المثال - Example Code */}
      <div className="bg-gray-900 rounded-lg p-6 text-left" dir="ltr">
        <h2 className="text-lg font-semibold text-white mb-4">Usage Code</h2>
        <pre className="text-green-400 text-sm overflow-x-auto">
          <code>{`import { HealthZonesLayer, type FieldZone } from '@/features/fields';

const zones: FieldZone[] = [
  {
    id: 'zone-1',
    name: 'المنطقة الشمالية',
    boundary: [[15.5527, 48.5164], [15.5537, 48.5174], ...],
    ndviValue: 0.75,
    healthStatus: 'excellent',
    area: 2.5,
  },
  // ... more zones
];

<MapContainer center={[15.5517, 48.5184]} zoom={14}>
  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

  <HealthZonesLayer
    zones={zones}
    selectedZoneId={selectedZoneId}
    onZoneClick={(zone) => console.log('Clicked:', zone)}
    showLabels={true}
    showTooltips={true}
  />
</MapContainer>`}</code>
        </pre>
      </div>
    </div>
  );
}
