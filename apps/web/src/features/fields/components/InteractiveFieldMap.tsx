'use client';

/**
 * SAHOOL Interactive Field Map Component
 * مكون خريطة الحقول التفاعلية
 *
 * Features / المميزات:
 * - Field boundary polygon display / عرض حدود الحقول
 * - NDVI layer overlay with color coding / طبقة NDVI مع الترميز اللوني
 * - Health zones visualization / تصور مناطق الصحة
 * - Task markers / علامات المهام
 * - Weather overlay / طبقة الطقس
 * - Layer controls / التحكم في الطبقات
 * - Zoom and draw controls / أدوات التكبير والرسم
 * - Interactive click handlers / معالجات النقر التفاعلية
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  MapContainer,
  TileLayer,
  Polygon,
  Marker,
  Popup,
  LayersControl,
  ZoomControl,
  useMapEvents,
  Circle,
} from 'react-leaflet';
import type { LatLngExpression, LatLngTuple } from 'leaflet';
import L from 'leaflet';
import {
  Layers,
  Cloud,
  Droplets,
  Thermometer,
  Wind,
} from 'lucide-react';
import type { Field, GeoPolygon, GeoPoint } from '../types';
import type { Task, TaskStatus, Priority } from '../../tasks/types';
import type { WeatherData } from '@sahool/api-client';

// ═══════════════════════════════════════════════════════════════════════════
// Types & Interfaces / الأنواع والواجهات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Health Zone Interface / واجهة منطقة الصحة
 * Represents a zone with specific health status
 */
export interface HealthZone {
  id: string;
  fieldId: string;
  center: GeoPoint;
  radius: number; // in meters / بالأمتار
  healthScore: number; // 0-100
  ndviValue?: number;
  status: 'healthy' | 'moderate' | 'stressed' | 'critical';
  color: string;
}

/**
 * Map Task Interface / واجهة مهمة الخريطة
 * Extended task with location data for map display
 */
export interface MapTask extends Task {
  location?: GeoPoint;
}

/**
 * Map Layer Configuration / تكوين طبقات الخريطة
 */
export interface LayerConfig {
  fields: boolean;
  ndvi: boolean;
  healthZones: boolean;
  tasks: boolean;
  weather: boolean;
}

/**
 * Component Props Interface / واجهة خصائص المكون
 */
export interface InteractiveFieldMapProps {
  /** Fields to display / الحقول للعرض */
  fields?: Field[];
  /** Single field (alternative to fields array) / حقل واحد (بديل لمصفوفة الحقول) */
  field?: Field;
  /** Tasks to display as markers / المهام لعرضها كعلامات */
  tasks?: MapTask[];
  /** Health zones to visualize / مناطق الصحة للتصور */
  healthZones?: HealthZone[];
  /** Weather data overlay / بيانات الطقس للطبقة */
  weather?: WeatherData;
  /** Map height / ارتفاع الخريطة */
  height?: string;
  /** Initial center coordinates [lat, lng] / الإحداثيات المركزية الأولية */
  center?: LatLngTuple;
  /** Initial zoom level / مستوى التكبير الأولي */
  zoom?: number;
  /** Enable layer controls / تفعيل التحكم في الطبقات */
  enableLayerControl?: boolean;
  /** Callback when field is clicked / استدعاء عند النقر على الحقل */
  onFieldClick?: (field: Field) => void;
  /** Callback when task marker is clicked / استدعاء عند النقر على علامة المهمة */
  onTaskClick?: (task: MapTask) => void;
  /** Callback when health zone is clicked / استدعاء عند النقر على منطقة الصحة */
  onHealthZoneClick?: (zone: HealthZone) => void;
  /** Callback when map is clicked / استدعاء عند النقر على الخريطة */
  onMapClick?: (lat: number, lng: number) => void;
  /** Custom class name / اسم الفئة المخصص */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Functions / وظائف مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Convert GeoPolygon to Leaflet LatLng coordinates
 * تحويل GeoPolygon إلى إحداثيات Leaflet
 */
const geoPolygonToLatLng = (polygon: GeoPolygon): LatLngExpression[][] => {
  return polygon.coordinates.map((ring) =>
    ring.map(([lng, lat]) => [lat, lng] as LatLngTuple)
  );
};

/**
 * Convert GeoPoint to Leaflet LatLng
 * تحويل GeoPoint إلى إحداثيات Leaflet
 */
const geoPointToLatLng = (point: GeoPoint): LatLngTuple => {
  const [lng, lat] = point.coordinates;
  return [lat, lng];
};

/**
 * Get color based on NDVI value
 * الحصول على اللون بناءً على قيمة NDVI
 */
const getNDVIColor = (ndvi: number): string => {
  if (ndvi >= 0.6) return '#00ff00'; // Healthy green / أخضر صحي
  if (ndvi >= 0.4) return '#90ee90'; // Light green / أخضر فاتح
  if (ndvi >= 0.2) return '#ffff00'; // Yellow / أصفر
  if (ndvi >= 0.0) return '#ffa500'; // Orange / برتقالي
  return '#ff0000'; // Red / أحمر
};

/**
 * Get color based on health score
 * الحصول على اللون بناءً على درجة الصحة
 */
const getHealthColor = (score: number): string => {
  if (score >= 80) return '#22c55e'; // Green / أخضر
  if (score >= 60) return '#eab308'; // Yellow / أصفر
  if (score >= 40) return '#f97316'; // Orange / برتقالي
  return '#ef4444'; // Red / أحمر
};

/**
 * Get task marker color based on priority and status
 * الحصول على لون علامة المهمة بناءً على الأولوية والحالة
 */
const getTaskColor = (priority: Priority, status: TaskStatus): string => {
  if (status === 'completed') return '#22c55e'; // Green / أخضر
  if (status === 'cancelled') return '#6b7280'; // Gray / رمادي

  switch (priority) {
    case 'urgent':
      return '#dc2626'; // Red / أحمر
    case 'high':
      return '#f97316'; // Orange / برتقالي
    case 'medium':
      return '#eab308'; // Yellow / أصفر
    case 'low':
      return '#3b82f6'; // Blue / أزرق
    default:
      return '#6b7280'; // Gray / رمادي
  }
};

/**
 * Create custom task marker icon
 * إنشاء أيقونة علامة مهمة مخصصة
 */
const createTaskIcon = (priority: Priority, status: TaskStatus): L.DivIcon => {
  const color = getTaskColor(priority, status);
  return new L.DivIcon({
    className: 'custom-task-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
      ">
        ${status === 'completed' ? '✓' : '!'}
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15],
  });
};

// ═══════════════════════════════════════════════════════════════════════════
// Map Event Handler Component / مكون معالج أحداث الخريطة
// ═══════════════════════════════════════════════════════════════════════════

interface MapEventsHandlerProps {
  onMapClick?: (lat: number, lng: number) => void;
}

const MapEventsHandler: React.FC<MapEventsHandlerProps> = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
};

// ═══════════════════════════════════════════════════════════════════════════
// Weather Overlay Component / مكون طبقة الطقس
// ═══════════════════════════════════════════════════════════════════════════

interface WeatherOverlayProps {
  weather: WeatherData;
}

const WeatherOverlay: React.FC<WeatherOverlayProps> = ({ weather }) => {
  return (
    <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-4 z-[1000] min-w-[280px]">
      <div className="flex items-center gap-2 mb-3">
        <Cloud className="w-5 h-5 text-blue-500" />
        <h3 className="font-bold text-gray-900">
          {weather.condition_ar || weather.condition}
        </h3>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Thermometer className="w-4 h-4" />
            <span>درجة الحرارة</span>
          </div>
          <span className="font-semibold text-gray-900">
            {weather.temperature_c}°C
          </span>
        </div>

        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Droplets className="w-4 h-4" />
            <span>الرطوبة</span>
          </div>
          <span className="font-semibold text-gray-900">
            {weather.humidity_percent}%
          </span>
        </div>

        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Wind className="w-4 h-4" />
            <span>سرعة الرياح</span>
          </div>
          <span className="font-semibold text-gray-900">
            {weather.wind_speed_kmh} km/h
          </span>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Layer Control Panel Component / مكون لوحة التحكم في الطبقات
// ═══════════════════════════════════════════════════════════════════════════

interface LayerControlPanelProps {
  layers: LayerConfig;
  onLayerToggle: (layer: keyof LayerConfig) => void;
}

const LayerControlPanel: React.FC<LayerControlPanelProps> = ({
  layers,
  onLayerToggle,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="absolute top-4 left-4 z-[1000]">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-white rounded-lg shadow-lg p-2 hover:bg-gray-50 transition-colors"
        title="طبقات الخريطة"
      >
        <Layers className="w-6 h-6 text-gray-700" />
      </button>

      {isOpen && (
        <div className="mt-2 bg-white rounded-lg shadow-lg p-4 min-w-[200px]">
          <h3 className="font-bold text-gray-900 mb-3 text-sm">طبقات الخريطة</h3>

          <div className="space-y-2">
            {(Object.keys(layers) as Array<keyof LayerConfig>).map((layer) => (
              <label
                key={layer}
                className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors"
              >
                <input
                  type="checkbox"
                  checked={layers[layer]}
                  onChange={() => onLayerToggle(layer)}
                  className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  {layer === 'fields' && 'حدود الحقول'}
                  {layer === 'ndvi' && 'طبقة NDVI'}
                  {layer === 'healthZones' && 'مناطق الصحة'}
                  {layer === 'tasks' && 'المهام'}
                  {layer === 'weather' && 'الطقس'}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Main Component / المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

export const InteractiveFieldMap: React.FC<InteractiveFieldMapProps> = ({
  fields = [],
  field,
  tasks = [],
  healthZones = [],
  weather,
  height = '600px',
  center,
  zoom = 13,
  enableLayerControl = true,
  onFieldClick,
  onTaskClick,
  onHealthZoneClick,
  onMapClick,
  className = '',
}) => {
  // ─────────────────────────────────────────────────────────────────────────
  // State Management / إدارة الحالة
  // ─────────────────────────────────────────────────────────────────────────

  const [activeLayers, setActiveLayers] = useState<LayerConfig>({
    fields: true,
    ndvi: true,
    healthZones: true,
    tasks: true,
    weather: true,
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Data Processing / معالجة البيانات
  // ─────────────────────────────────────────────────────────────────────────

  // Combine single field with fields array / دمج حقل واحد مع مصفوفة الحقول
  const allFields = useMemo(() => {
    return field ? [field, ...fields] : fields;
  }, [field, fields]);

  // Calculate map center from fields / حساب مركز الخريطة من الحقول
  const mapCenter = useMemo((): LatLngTuple => {
    if (center) return center;

    if (allFields.length > 0) {
      const firstField = allFields[0];
      if (firstField?.centroid) {
        return geoPointToLatLng(firstField.centroid);
      }
      if (firstField?.polygon && firstField.polygon.coordinates.length > 0) {
        const firstRing = firstField.polygon.coordinates[0];
        if (firstRing && firstRing.length > 0) {
          const coords = firstRing[0];
          if (coords && coords.length >= 2) {
            const [lng, lat] = coords;
            return [lat, lng];
          }
        }
      }
    }

    // Default center (Yemen) / المركز الافتراضي (اليمن)
    return [15.5527, 48.5164];
  }, [center, allFields]);

  // ─────────────────────────────────────────────────────────────────────────
  // Event Handlers / معالجات الأحداث
  // ─────────────────────────────────────────────────────────────────────────

  const handleLayerToggle = useCallback((layer: keyof LayerConfig) => {
    setActiveLayers((prev) => ({
      ...prev,
      [layer]: !prev[layer],
    }));
  }, []);

  const handleFieldClick = useCallback(
    (clickedField: Field) => {
      if (onFieldClick) {
        onFieldClick(clickedField);
      }
    },
    [onFieldClick]
  );

  const handleTaskClick = useCallback(
    (clickedTask: MapTask) => {
      if (onTaskClick) {
        onTaskClick(clickedTask);
      }
    },
    [onTaskClick]
  );

  const handleHealthZoneClick = useCallback(
    (zone: HealthZone) => {
      if (onHealthZoneClick) {
        onHealthZoneClick(zone);
      }
    },
    [onHealthZoneClick]
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Render / العرض
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div
      className={`relative rounded-xl overflow-hidden border-2 border-gray-200 shadow-lg ${className}`}
      style={{ height }}
    >
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        zoomControl={false}
        className="w-full h-full"
        style={{ height: '100%', width: '100%' }}
      >
        {/* Base Map Tiles / خرائط الأساس */}
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="خريطة الشوارع">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="صور الأقمار الصناعية">
            <TileLayer
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {/* Zoom Controls / أدوات التكبير */}
        <ZoomControl position="bottomright" />

        {/* Map Click Events / أحداث النقر على الخريطة */}
        <MapEventsHandler onMapClick={onMapClick} />

        {/* Field Boundaries Layer / طبقة حدود الحقول */}
        {activeLayers.fields &&
          allFields.map((fieldItem) => {
            if (!fieldItem.polygon) return null;

            const positions = geoPolygonToLatLng(fieldItem.polygon);
            const color = activeLayers.ndvi && fieldItem.ndviValue
              ? getNDVIColor(fieldItem.ndviValue)
              : '#3b82f6';

            return (
              <Polygon
                key={fieldItem.id}
                positions={positions}
                pathOptions={{
                  color: color,
                  fillColor: color,
                  fillOpacity: 0.3,
                  weight: 2,
                }}
                eventHandlers={{
                  click: () => handleFieldClick(fieldItem),
                }}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <h3 className="font-bold text-gray-900 mb-2">
                      {fieldItem.nameAr || fieldItem.name}
                    </h3>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">المساحة:</span>
                        <span className="font-semibold">{fieldItem.area} هكتار</span>
                      </div>
                      {fieldItem.crop && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">المحصول:</span>
                          <span className="font-semibold">
                            {fieldItem.cropAr || fieldItem.crop}
                          </span>
                        </div>
                      )}
                      {activeLayers.ndvi && fieldItem.ndviValue !== undefined && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">NDVI:</span>
                          <span className="font-semibold">
                            {fieldItem.ndviValue.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {fieldItem.healthScore !== undefined && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">الصحة:</span>
                          <span className="font-semibold">
                            {fieldItem.healthScore}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </Polygon>
            );
          })}

        {/* Health Zones Layer / طبقة مناطق الصحة */}
        {activeLayers.healthZones &&
          healthZones.map((zone) => {
            const position = geoPointToLatLng(zone.center);

            return (
              <Circle
                key={zone.id}
                center={position}
                radius={zone.radius}
                pathOptions={{
                  color: zone.color || getHealthColor(zone.healthScore),
                  fillColor: zone.color || getHealthColor(zone.healthScore),
                  fillOpacity: 0.2,
                  weight: 2,
                }}
                eventHandlers={{
                  click: () => handleHealthZoneClick(zone),
                }}
              >
                <Popup>
                  <div className="p-2">
                    <h4 className="font-bold text-gray-900 mb-2">منطقة صحة</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">الحالة:</span>
                        <span className="font-semibold">{zone.status}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">درجة الصحة:</span>
                        <span className="font-semibold">{zone.healthScore}%</span>
                      </div>
                      {zone.ndviValue !== undefined && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">NDVI:</span>
                          <span className="font-semibold">
                            {zone.ndviValue.toFixed(2)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </Circle>
            );
          })}

        {/* Task Markers Layer / طبقة علامات المهام */}
        {activeLayers.tasks &&
          tasks.map((task) => {
            if (!task.location) return null;

            const position = geoPointToLatLng(task.location);
            const icon = createTaskIcon(task.priority, task.status);

            return (
              <Marker
                key={task.id}
                position={position}
                icon={icon}
                eventHandlers={{
                  click: () => handleTaskClick(task),
                }}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <h4 className="font-bold text-gray-900 mb-2">
                      {task.title_ar || task.title}
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-600">الحالة:</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            task.status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : task.status === 'in_progress'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {task.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-600">الأولوية:</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            task.priority === 'urgent'
                              ? 'bg-red-100 text-red-800'
                              : task.priority === 'high'
                              ? 'bg-orange-100 text-orange-800'
                              : task.priority === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {task.priority}
                        </span>
                      </div>
                      {task.due_date && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">موعد الاستحقاق:</span>
                          <span className="font-semibold">
                            {new Date(task.due_date).toLocaleDateString('ar-EG')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
      </MapContainer>

      {/* Weather Overlay / طبقة الطقس */}
      {activeLayers.weather && weather && <WeatherOverlay weather={weather} />}

      {/* Layer Control Panel / لوحة التحكم في الطبقات */}
      {enableLayerControl && (
        <LayerControlPanel
          layers={activeLayers}
          onLayerToggle={handleLayerToggle}
        />
      )}

      {/* Map Legend / مفتاح الخريطة */}
      {activeLayers.ndvi && (
        <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3 z-[1000]">
          <h4 className="font-bold text-xs text-gray-900 mb-2">مفتاح NDVI</h4>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#00ff00' }} />
              <span>صحي جداً (&gt; 0.6)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#90ee90' }} />
              <span>صحي (0.4-0.6)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ffff00' }} />
              <span>متوسط (0.2-0.4)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ffa500' }} />
              <span>ضعيف (0-0.2)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ff0000' }} />
              <span>حرج (&lt; 0)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveFieldMap;
