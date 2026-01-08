/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck - Example file for demonstration purposes
/**
 * WeatherOverlay Usage Example
 * مثال استخدام تراكب الطقس
 *
 * This example demonstrates how to use the WeatherOverlay component
 * on a field map to display real-time weather information.
 */

import React from 'react';
import { MapContainer, TileLayer, Polygon } from 'react-leaflet';
import { WeatherOverlay } from './WeatherOverlay';
import type { Field } from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Basic Usage
// ═══════════════════════════════════════════════════════════════════════════

export function BasicWeatherOverlayExample() {
  const fieldId = 'field-123';

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.3694, 44.191]}
        zoom={13}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Weather overlay in top-right corner (default) */}
        <WeatherOverlay fieldId={fieldId} />
      </MapContainer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Different Positions
// ═══════════════════════════════════════════════════════════════════════════

export function PositionedWeatherOverlayExample() {
  const fieldId = 'field-123';

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.3694, 44.191]}
        zoom={13}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Top-left position */}
        <WeatherOverlay fieldId={fieldId} position="topleft" />

        {/* Or bottom-right */}
        {/* <WeatherOverlay fieldId={fieldId} position="bottomright" /> */}

        {/* Or bottom-left */}
        {/* <WeatherOverlay fieldId={fieldId} position="bottomleft" /> */}
      </MapContainer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Expanded by Default
// ═══════════════════════════════════════════════════════════════════════════

export function ExpandedWeatherOverlayExample() {
  const fieldId = 'field-123';

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={[15.3694, 44.191]}
        zoom={13}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Start with expanded view */}
        <WeatherOverlay fieldId={fieldId} expanded={true} />
      </MapContainer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Multiple Fields with Weather
// ═══════════════════════════════════════════════════════════════════════════

interface FieldWithWeatherProps {
  field: Field;
}

export function FieldWithWeather({ field }: FieldWithWeatherProps) {
  // Convert polygon coordinates for Leaflet (expects [lat, lng])
  const polygonPositions = field.polygon?.coordinates[0].map(
    ([lng, lat]) => [lat, lng] as [number, number]
  ) || [];

  const center = field.centroid?.coordinates
    ? [field.centroid.coordinates[1], field.centroid.coordinates[0]] as [number, number]
    : [15.3694, 44.191] as [number, number];

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={center}
        zoom={14}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Show field polygon */}
        {polygonPositions.length > 0 && (
          <Polygon
            positions={polygonPositions}
            pathOptions={{
              color: '#10b981',
              fillColor: '#10b981',
              fillOpacity: 0.2,
            }}
          />
        )}

        {/* Weather overlay for this field */}
        <WeatherOverlay
          fieldId={field.id}
          position="topright"
        />
      </MapContainer>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: With Field Details Panel
// ═══════════════════════════════════════════════════════════════════════════

export function FieldMapWithWeatherAndDetails({ field }: FieldWithWeatherProps) {
  const polygonPositions = field.polygon?.coordinates?.[0]?.map(
    ([lng, lat]: [number, number]) => [lat, lng] as [number, number]
  ) ?? [];

  const center = field.centroid?.coordinates
    ? [field.centroid.coordinates[1], field.centroid.coordinates[0]] as [number, number]
    : [15.3694, 44.191] as [number, number];

  return (
    <div className="relative h-[600px] w-full">
      <MapContainer
        center={center}
        zoom={14}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {polygonPositions.length > 0 && (
          <Polygon
            positions={polygonPositions}
            pathOptions={{
              color: '#10b981',
              fillColor: '#10b981',
              fillOpacity: 0.2,
            }}
          />
        )}

        {/* Weather in top-right */}
        <WeatherOverlay
          fieldId={field.id}
          position="topright"
        />
      </MapContainer>

      {/* Field details panel in bottom-left outside map */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 max-w-xs z-[1000]" dir="rtl">
        <h3 className="text-lg font-bold mb-2">{field.nameAr || field.name}</h3>
        <div className="space-y-1 text-sm text-gray-600">
          <p>المساحة: {field.area} هكتار</p>
          {field.cropAr && <p>المحصول: {field.cropAr}</p>}
          {field.soilType && <p>نوع التربة: {field.soilType}</p>}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Usage Notes / ملاحظات الاستخدام
// ═══════════════════════════════════════════════════════════════════════════

/*
USAGE NOTES:

1. The WeatherOverlay automatically fetches weather data based on the field's
   centroid coordinates.

2. Position options:
   - 'topright': Top right corner (default)
   - 'topleft': Top left corner
   - 'bottomright': Bottom right corner
   - 'bottomleft': Bottom left corner

3. The component is responsive and will:
   - Show compact view by default
   - Expand to show full details when clicked
   - Display weather alerts with badge notifications
   - Auto-refresh weather data periodically

4. Features included:
   ✓ Current temperature, humidity, wind speed & direction
   ✓ Weather condition icons (sun, cloud, rain, etc.)
   ✓ 24-hour rainfall forecast
   ✓ Severe weather alerts with color-coded badges
   ✓ Collapsible/expandable interface
   ✓ Arabic and English labels
   ✓ Loading and error states
   ✓ Accessibility features (ARIA labels)

5. The component uses the field's centroid for weather data. Make sure your
   field has a valid centroid defined.

6. Weather data is cached and auto-refreshed according to the useWeather hooks
   configuration (typically every 10-15 minutes).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ملاحظات الاستخدام:

1. يقوم تراكب الطقس تلقائياً بجلب بيانات الطقس بناءً على إحداثيات مركز الحقل.

2. خيارات الموقع:
   - 'topright': الزاوية العلوية اليمنى (افتراضي)
   - 'topleft': الزاوية العلوية اليسرى
   - 'bottomright': الزاوية السفلية اليمنى
   - 'bottomleft': الزاوية السفلية اليسرى

3. المكون متجاوب وسوف:
   - يعرض العرض المدمج افتراضياً
   - يتوسع لإظهار التفاصيل الكاملة عند النقر
   - يعرض تنبيهات الطقس مع إشعارات الشارات
   - يحدث بيانات الطقس تلقائياً بشكل دوري

4. الميزات المتضمنة:
   ✓ درجة الحرارة الحالية، الرطوبة، سرعة الرياح واتجاهها
   ✓ أيقونات حالة الطقس (شمس، غيوم، مطر، إلخ)
   ✓ توقعات الأمطار لمدة 24 ساعة
   ✓ تنبيهات الطقس الشديد مع شارات ملونة
   ✓ واجهة قابلة للطي/التوسيع
   ✓ تسميات عربية وإنجليزية
   ✓ حالات التحميل والخطأ
   ✓ ميزات إمكانية الوصول (تسميات ARIA)

5. يستخدم المكون مركز الحقل للحصول على بيانات الطقس. تأكد من أن الحقل
   الخاص بك لديه مركز صالح محدد.

6. يتم تخزين بيانات الطقس مؤقتاً وتحديثها تلقائياً وفقاً لإعدادات
   خطافات useWeather (عادةً كل 10-15 دقيقة).
*/
