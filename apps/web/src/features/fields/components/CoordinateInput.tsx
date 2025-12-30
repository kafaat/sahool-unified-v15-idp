'use client';

/**
 * SAHOOL Coordinate Input Component
 * مكون إدخال الإحداثيات
 *
 * Similar to: John Deere Operations Center, Farmonaut
 *
 * Features:
 * - Manual coordinate entry (lat/lng)
 * - Multiple format support (DD, DMS, UTM)
 * - Coordinate validation
 * - Copy/Paste support
 * - GPS coordinate capture
 */

import React, { useState, useCallback } from 'react';
import {
  MapPin,
  Navigation,
  Copy,
  Check,
  AlertCircle,
  Plus,
  Trash2,
  Download,
  Upload,
} from 'lucide-react';
import type { GeoPolygon, GeoPoint } from '../types';

// Coordinate format types
type CoordinateFormat = 'DD' | 'DMS' | 'UTM';

interface Coordinate {
  id: string;
  lat: number;
  lng: number;
}

interface CoordinateInputProps {
  initialCoordinates?: Coordinate[];
  onCoordinatesChange?: (coordinates: Coordinate[]) => void;
  onPolygonCreate?: (polygon: GeoPolygon) => void;
  onCentroidCreate?: (centroid: GeoPoint) => void;
  maxPoints?: number;
  minPoints?: number;
  mode?: 'polygon' | 'point' | 'both';
}

// Validate latitude (-90 to 90)
const isValidLat = (lat: number): boolean => lat >= -90 && lat <= 90;

// Validate longitude (-180 to 180)
const isValidLng = (lng: number): boolean => lng >= -180 && lng <= 180;

// Convert DMS to DD (reserved for future DMS input support)
const _dmsToDD = (degrees: number, minutes: number, seconds: number, direction: string): number => {
  let dd = degrees + minutes / 60 + seconds / 3600;
  if (direction === 'S' || direction === 'W') {
    dd = dd * -1;
  }
  return dd;
};
void _dmsToDD; // Suppress unused warning - will be used for DMS input parsing

// Convert DD to DMS
const ddToDMS = (dd: number, isLat: boolean): string => {
  const direction = isLat ? (dd >= 0 ? 'N' : 'S') : (dd >= 0 ? 'E' : 'W');
  const absDD = Math.abs(dd);
  const degrees = Math.floor(absDD);
  const minutesDecimal = (absDD - degrees) * 60;
  const minutes = Math.floor(minutesDecimal);
  const seconds = ((minutesDecimal - minutes) * 60).toFixed(2);
  return `${degrees}° ${minutes}' ${seconds}" ${direction}`;
};

// Generate unique ID
const generateId = (): string => Math.random().toString(36).substring(2, 9);

export const CoordinateInput: React.FC<CoordinateInputProps> = ({
  initialCoordinates = [],
  onCoordinatesChange,
  onPolygonCreate,
  onCentroidCreate,
  maxPoints = 100,
  minPoints = 3,
  mode = 'polygon',
}) => {
  const [coordinates, setCoordinates] = useState<Coordinate[]>(
    initialCoordinates.length > 0 ? initialCoordinates : [{ id: generateId(), lat: 0, lng: 0 }]
  );
  const [format, setFormat] = useState<CoordinateFormat>('DD');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [copied, setCopied] = useState(false);
  const [isCapturingGPS, setIsCapturingGPS] = useState(false);

  // Add new coordinate
  const addCoordinate = useCallback(() => {
    if (coordinates.length >= maxPoints) return;

    const newCoord: Coordinate = { id: generateId(), lat: 0, lng: 0 };
    const updated = [...coordinates, newCoord];
    setCoordinates(updated);
    onCoordinatesChange?.(updated);
  }, [coordinates, maxPoints, onCoordinatesChange]);

  // Remove coordinate
  const removeCoordinate = useCallback((id: string) => {
    if (coordinates.length <= 1) return;

    const updated = coordinates.filter((c) => c.id !== id);
    setCoordinates(updated);
    onCoordinatesChange?.(updated);

    // Clear error for removed coordinate
    const newErrors = { ...errors };
    delete newErrors[id];
    setErrors(newErrors);
  }, [coordinates, errors, onCoordinatesChange]);

  // Update coordinate
  const updateCoordinate = useCallback((id: string, field: 'lat' | 'lng', value: string) => {
    const numValue = parseFloat(value);
    const newErrors = { ...errors };

    // Validate
    if (isNaN(numValue)) {
      newErrors[`${id}-${field}`] = 'قيمة غير صالحة';
    } else if (field === 'lat' && !isValidLat(numValue)) {
      newErrors[`${id}-${field}`] = 'خط العرض يجب أن يكون بين -90 و 90';
    } else if (field === 'lng' && !isValidLng(numValue)) {
      newErrors[`${id}-${field}`] = 'خط الطول يجب أن يكون بين -180 و 180';
    } else {
      delete newErrors[`${id}-${field}`];
    }

    setErrors(newErrors);

    const updated = coordinates.map((c) =>
      c.id === id ? { ...c, [field]: isNaN(numValue) ? 0 : numValue } : c
    );
    setCoordinates(updated);
    onCoordinatesChange?.(updated);
  }, [coordinates, errors, onCoordinatesChange]);

  // Capture GPS location
  const captureGPSLocation = useCallback(() => {
    if (!('geolocation' in navigator)) {
      alert('المتصفح لا يدعم تحديد الموقع');
      return;
    }

    setIsCapturingGPS(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const newCoord: Coordinate = {
          id: generateId(),
          lat: parseFloat(latitude.toFixed(6)),
          lng: parseFloat(longitude.toFixed(6)),
        };

        const updated = [...coordinates, newCoord];
        setCoordinates(updated);
        onCoordinatesChange?.(updated);
        setIsCapturingGPS(false);
      },
      (error) => {
        console.error('GPS error:', error);
        alert('تعذر الحصول على الموقع الحالي');
        setIsCapturingGPS(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [coordinates, onCoordinatesChange]);

  // Create polygon from coordinates
  const createPolygon = useCallback(() => {
    const validCoords = coordinates.filter(
      (c) => isValidLat(c.lat) && isValidLng(c.lng) && (c.lat !== 0 || c.lng !== 0)
    );

    if (validCoords.length < minPoints) {
      alert(`يجب إدخال ${minPoints} نقاط على الأقل`);
      return;
    }

    // Close the polygon
    const polygonCoords = validCoords.map((c) => [c.lng, c.lat]);
    const firstCoord = polygonCoords[0];
    if (firstCoord) {
      polygonCoords.push(firstCoord);
    }

    const polygon: GeoPolygon = {
      type: 'Polygon',
      coordinates: [polygonCoords],
    };

    onPolygonCreate?.(polygon);
  }, [coordinates, minPoints, onPolygonCreate]);

  // Create centroid from first coordinate
  const createCentroid = useCallback(() => {
    const firstCoord = coordinates[0];
    if (!firstCoord || !isValidLat(firstCoord.lat) || !isValidLng(firstCoord.lng)) {
      alert('يرجى إدخال إحداثيات صحيحة');
      return;
    }

    const centroid: GeoPoint = {
      type: 'Point',
      coordinates: [firstCoord.lng, firstCoord.lat],
    };

    onCentroidCreate?.(centroid);
  }, [coordinates, onCentroidCreate]);

  // Copy coordinates to clipboard
  const copyToClipboard = useCallback(() => {
    const text = coordinates
      .map((c) => `${c.lat.toFixed(6)}, ${c.lng.toFixed(6)}`)
      .join('\n');

    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [coordinates]);

  // Export as GeoJSON
  const exportGeoJSON = useCallback(() => {
    const validCoords = coordinates.filter(
      (c) => isValidLat(c.lat) && isValidLng(c.lng)
    );

    const geojson = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'Polygon',
            coordinates: [validCoords.map((c) => [c.lng, c.lat])],
          },
        },
      ],
    };

    const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'field-coordinates.geojson';
    a.click();
    URL.revokeObjectURL(url);
  }, [coordinates]);

  // Import from GeoJSON
  const importGeoJSON = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const geojson = JSON.parse(e.target?.result as string);
        const feature = geojson.features?.[0];
        const coords = feature?.geometry?.coordinates?.[0];

        if (coords && Array.isArray(coords)) {
          const imported: Coordinate[] = coords.slice(0, -1).map((c: number[]) => ({
            id: generateId(),
            lat: c[1] ?? 0,
            lng: c[0] ?? 0,
          }));

          setCoordinates(imported);
          onCoordinatesChange?.(imported);
        }
      } catch {
        alert('تعذر قراءة الملف');
      }
    };
    reader.readAsText(file);
  }, [onCoordinatesChange]);

  const hasErrors = Object.keys(errors).length > 0;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-green-600" />
            <h3 className="font-bold text-gray-900">إدخال الإحداثيات</h3>
          </div>

          {/* Format selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">التنسيق:</span>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value as CoordinateFormat)}
              className="text-sm border border-gray-300 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="DD">درجات عشرية (DD)</option>
              <option value="DMS">درجات/دقائق/ثواني (DMS)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Coordinate list */}
      <div className="p-4 space-y-3 max-h-80 overflow-y-auto">
        {coordinates.map((coord, index) => (
          <div key={coord.id} className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-sm font-medium">
              {index + 1}
            </div>

            <div className="flex-1 grid grid-cols-2 gap-3">
              {/* Latitude */}
              <div>
                <label className="block text-xs text-gray-500 mb-1">خط العرض (Lat)</label>
                <input
                  type="number"
                  step="0.000001"
                  value={coord.lat || ''}
                  onChange={(e) => updateCoordinate(coord.id, 'lat', e.target.value)}
                  placeholder="15.552700"
                  className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 ${
                    errors[`${coord.id}-lat`]
                      ? 'border-red-300 focus:ring-red-500'
                      : 'border-gray-300 focus:ring-green-500'
                  }`}
                />
                {errors[`${coord.id}-lat`] && (
                  <p className="text-xs text-red-500 mt-1">{errors[`${coord.id}-lat`]}</p>
                )}
                {format === 'DMS' && coord.lat !== 0 && (
                  <p className="text-xs text-gray-400 mt-1">{ddToDMS(coord.lat, true)}</p>
                )}
              </div>

              {/* Longitude */}
              <div>
                <label className="block text-xs text-gray-500 mb-1">خط الطول (Lng)</label>
                <input
                  type="number"
                  step="0.000001"
                  value={coord.lng || ''}
                  onChange={(e) => updateCoordinate(coord.id, 'lng', e.target.value)}
                  placeholder="48.516400"
                  className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 ${
                    errors[`${coord.id}-lng`]
                      ? 'border-red-300 focus:ring-red-500'
                      : 'border-gray-300 focus:ring-green-500'
                  }`}
                />
                {errors[`${coord.id}-lng`] && (
                  <p className="text-xs text-red-500 mt-1">{errors[`${coord.id}-lng`]}</p>
                )}
                {format === 'DMS' && coord.lng !== 0 && (
                  <p className="text-xs text-gray-400 mt-1">{ddToDMS(coord.lng, false)}</p>
                )}
              </div>
            </div>

            {/* Remove button */}
            {coordinates.length > 1 && (
              <button
                onClick={() => removeCoordinate(coord.id)}
                className="flex-shrink-0 p-2 text-gray-400 hover:text-red-500 transition-colors"
                title="حذف النقطة"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-3">
        {/* Add point buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={addCoordinate}
            disabled={coordinates.length >= maxPoints}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-4 h-4" />
            إضافة نقطة
          </button>

          <button
            onClick={captureGPSLocation}
            disabled={isCapturingGPS}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <Navigation className={`w-4 h-4 ${isCapturingGPS ? 'animate-pulse' : ''}`} />
            {isCapturingGPS ? 'جاري التحديد...' : 'موقعي GPS'}
          </button>

          <button
            onClick={copyToClipboard}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
            {copied ? 'تم النسخ' : 'نسخ'}
          </button>
        </div>

        {/* Import/Export */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={exportGeoJSON}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="w-4 h-4" />
            تصدير GeoJSON
          </button>

          <label className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
            <Upload className="w-4 h-4" />
            استيراد GeoJSON
            <input
              type="file"
              accept=".geojson,.json"
              onChange={importGeoJSON}
              className="hidden"
            />
          </label>
        </div>

        {/* Create buttons */}
        <div className="flex gap-2 pt-2">
          {(mode === 'polygon' || mode === 'both') && (
            <button
              onClick={createPolygon}
              disabled={hasErrors || coordinates.length < minPoints}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <MapPin className="w-4 h-4" />
              إنشاء حدود الحقل
            </button>
          )}

          {(mode === 'point' || mode === 'both') && (
            <button
              onClick={createCentroid}
              disabled={hasErrors || coordinates.length < 1}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Navigation className="w-4 h-4" />
              تحديد المركز
            </button>
          )}
        </div>

        {/* Status */}
        {hasErrors && (
          <div className="flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span>يرجى تصحيح الأخطاء أعلاه</span>
          </div>
        )}

        <div className="text-xs text-gray-500 text-center">
          {coordinates.length} نقطة من {maxPoints} كحد أقصى
        </div>
      </div>
    </div>
  );
};

export default CoordinateInput;
