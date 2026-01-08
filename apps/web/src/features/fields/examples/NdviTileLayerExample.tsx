// @ts-nocheck - Example file with maplibre type complexities
'use client';

/**
 * NDVI Tile Layer Usage Example
 * مثال على استخدام طبقة NDVI
 *
 * This example demonstrates how to use the NdviTileLayer component
 * with MapLibre GL to display NDVI data on a map.
 */

import React, { useRef, useEffect, useState, type RefObject } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import {
  NdviTileLayer,
  NdviColorLegend,
  NdviLoadingOverlay,
} from '../components/NdviTileLayer';
import { Calendar, Eye, EyeOff } from 'lucide-react';

/**
 * مثال تطبيقي كامل لعرض NDVI على الخريطة
 * Complete example of displaying NDVI on a map
 */
export const NdviMapExample: React.FC<{ fieldId: string }> = ({ fieldId }) => {
  // مرجع حاوية الخريطة - Map container reference
  const mapContainer = useRef<HTMLDivElement>(null);

  // مرجع كائن الخريطة - Map instance reference
  const map = useRef<maplibregl.Map | null>(null);

  // حالات التحكم - Control states
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [opacity, setOpacity] = useState(0.7);
  const [visible, setVisible] = useState(true);
  const [isNdviLoading, setIsNdviLoading] = useState(false);

  /**
   * تهيئة الخريطة - Initialize map
   */
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // إنشاء خريطة MapLibre - Create MapLibre map
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors',
          },
        },
        layers: [
          {
            id: 'osm',
            type: 'raster',
            source: 'osm',
          },
        ],
      },
      center: [44.2, 15.0], // مركز اليمن - Yemen center
      zoom: 10,
    }) as maplibregl.Map;

    // إضافة أدوات التحكم - Add navigation controls
    if (map.current) {
      map.current.addControl(new maplibregl.NavigationControl(), 'top-left');
    }

    // تعيين حالة التحميل - Set loading state
    if (map.current) {
      map.current.on('load', () => {
        setMapLoaded(true);
      });
    }

    // التنظيف - Cleanup
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  /**
   * معالج تحميل طبقة NDVI
   * NDVI layer load handler
   */
  const handleNdviLoad = () => {
    console.log('NDVI layer loaded successfully');
    setIsNdviLoading(false);
  };

  /**
   * معالج أخطاء NDVI
   * NDVI error handler
   */
  const handleNdviError = (error: Error) => {
    console.error('NDVI layer error:', error);
    setIsNdviLoading(false);
    // يمكن إضافة إشعار للمستخدم هنا
    // Can add user notification here
  };

  /**
   * تبديل ظهور الطبقة
   * Toggle layer visibility
   */
  const toggleVisibility = () => {
    setVisible((prev) => !prev);
  };

  return (
    <div className="relative w-full h-screen">
      {/* حاوية الخريطة - Map container */}
      <div ref={mapContainer} className="w-full h-full" />

      {/* طبقة NDVI - NDVI Layer */}
      {mapLoaded && (
        <NdviTileLayer
          fieldId={fieldId}
          date={selectedDate}
          opacity={opacity}
          visible={visible}
          map={map as RefObject<maplibregl.Map | null>}
          onLoad={handleNdviLoad}
          onError={handleNdviError}
        />
      )}

      {/* لوحة التحكم - Control Panel */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 space-y-4 w-80">
        {/* عنوان - Title */}
        <h3 className="text-lg font-bold text-gray-800 text-right">
          طبقة NDVI
        </h3>

        {/* اختيار التاريخ - Date Selection */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 text-right">
            <Calendar className="inline-block w-4 h-4 ml-2" />
            التاريخ
          </label>
          <input
            type="date"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-right"
            value={selectedDate?.toISOString().split('T')[0] || ''}
            onChange={(e) => {
              setSelectedDate(e.target.value ? new Date(e.target.value) : undefined);
              setIsNdviLoading(true);
            }}
            max={new Date().toISOString().split('T')[0]}
          />
          <p className="text-xs text-gray-500 text-right">
            اتركه فارغاً لآخر البيانات المتاحة
          </p>
        </div>

        {/* التحكم في الشفافية - Opacity Control */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 text-right">
            الشفافية: {Math.round(opacity * 100)}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={opacity * 100}
            onChange={(e) => setOpacity(Number(e.target.value) / 100)}
            className="w-full"
          />
        </div>

        {/* التحكم في الظهور - Visibility Toggle */}
        <button
          onClick={toggleVisibility}
          className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${
            visible
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          {visible ? (
            <>
              <Eye className="w-4 h-4" />
              إخفاء الطبقة
            </>
          ) : (
            <>
              <EyeOff className="w-4 h-4" />
              إظهار الطبقة
            </>
          )}
        </button>
      </div>

      {/* مفتاح الألوان - Color Legend */}
      <NdviColorLegend className="absolute bottom-4 right-4" />

      {/* مؤشر التحميل - Loading Overlay */}
      <NdviLoadingOverlay isLoading={isNdviLoading} />

      {/* حالة التحميل الأولية - Initial loading state */}
      {!mapLoaded && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-gray-500">جاري تحميل الخريطة...</div>
        </div>
      )}
    </div>
  );
};

/**
 * مثال بسيط - Simple Example
 */
export const SimpleNdviExample: React.FC = () => {
  const map = useRef<maplibregl.Map | null>(null);
  const mapContainer = useRef<HTMLDivElement>(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
          },
        },
        layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
      },
      center: [44.2, 15.0],
      zoom: 10,
    }) as maplibregl.Map;

    if (map.current) {
      map.current.on('load', () => setMapReady(true));
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  return (
    <div className="relative w-full h-96">
      <div ref={mapContainer} className="w-full h-full" />

      {mapReady && (
        <>
          {/* استخدام أبسط مع الإعدادات الافتراضية - Simplest usage with defaults */}
          <NdviTileLayer
            fieldId="field-123"
            map={map as RefObject<maplibregl.Map | null>}
          />

          {/* إضافة مفتاح الألوان - Add color legend */}
          <NdviColorLegend className="absolute bottom-4 right-4" />
        </>
      )}
    </div>
  );
};

/**
 * مثال مع عدة حقول - Example with Multiple Fields
 */
export const MultipleFieldsNdviExample: React.FC<{
  fields: Array<{ id: string; name: string }>;
}> = ({ fields }) => {
  const map = useRef<maplibregl.Map | null>(null);
  const mapContainer = useRef<HTMLDivElement>(null);
  const [mapReady, setMapReady] = useState(false);
  const [selectedField, setSelectedField] = useState(fields[0]?.id);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
          },
        },
        layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
      },
      center: [44.2, 15.0],
      zoom: 8,
    }) as maplibregl.Map;

    if (map.current) {
      map.current.on('load', () => setMapReady(true));
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  return (
    <div className="relative w-full h-screen">
      <div ref={mapContainer} className="w-full h-full" />

      {/* قائمة اختيار الحقل - Field selection */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
          اختر الحقل
        </label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-right"
          value={selectedField}
          onChange={(e) => setSelectedField(e.target.value)}
        >
          {fields.map((field) => (
            <option key={field.id} value={field.id}>
              {field.name}
            </option>
          ))}
        </select>
      </div>

      {/* عرض NDVI للحقل المحدد فقط - Show NDVI for selected field only */}
      {mapReady && selectedField && (
        <>
          <NdviTileLayer
            fieldId={selectedField}
            map={map as RefObject<maplibregl.Map | null>}
            opacity={0.8}
          />
          <NdviColorLegend className="absolute bottom-4 right-4" />
        </>
      )}
    </div>
  );
};

/**
 * مثال مع المقارنة الزمنية - Temporal Comparison Example
 */
export const TemporalComparisonExample: React.FC<{ fieldId: string }> = ({
  fieldId,
}) => {
  const map = useRef<maplibregl.Map | null>(null);
  const mapContainer = useRef<HTMLDivElement>(null);
  const [mapReady, setMapReady] = useState(false);
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [compareDate, setCompareDate] = useState<Date | undefined>(undefined);
  const [showComparison, setShowComparison] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
          },
        },
        layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
      },
      center: [44.2, 15.0],
      zoom: 12,
    }) as maplibregl.Map;

    if (map.current) {
      map.current.on('load', () => setMapReady(true));
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  return (
    <div className="relative w-full h-screen">
      <div ref={mapContainer} className="w-full h-full" />

      {/* لوحة المقارنة - Comparison panel */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 space-y-4 w-80">
        <h3 className="text-lg font-bold text-gray-800 text-right">
          مقارنة NDVI الزمنية
        </h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 text-right">
            التاريخ الحالي
          </label>
          <input
            type="date"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-right"
            value={currentDate.toISOString().split('T')[0]}
            onChange={(e) => setCurrentDate(new Date(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 text-right">
            تاريخ المقارنة
          </label>
          <input
            type="date"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-right"
            value={compareDate?.toISOString().split('T')[0] || ''}
            onChange={(e) =>
              setCompareDate(e.target.value ? new Date(e.target.value) : undefined)
            }
          />
        </div>

        <button
          onClick={() => setShowComparison(!showComparison)}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          disabled={!compareDate}
        >
          {showComparison ? 'إخفاء المقارنة' : 'عرض المقارنة'}
        </button>
      </div>

      {mapReady && (
        <>
          {/* التاريخ الحالي - Current date */}
          <NdviTileLayer
            fieldId={fieldId}
            date={currentDate}
            map={map as React.RefObject<maplibregl.Map | null>}
            opacity={showComparison ? 0.5 : 0.7}
          />

          {/* تاريخ المقارنة - Comparison date (if enabled) */}
          {showComparison && compareDate && (
            <NdviTileLayer
              fieldId={fieldId}
              date={compareDate}
              map={map as React.RefObject<maplibregl.Map | null>}
              opacity={0.5}
            />
          )}

          <NdviColorLegend className="absolute bottom-4 right-4" />
        </>
      )}
    </div>
  );
};

export default NdviMapExample;
