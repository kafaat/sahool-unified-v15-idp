'use client';

/**
 * SAHOOL Field Form Component
 * مكون نموذج الحقل
 *
 * Includes interactive boundary drawing (FieldBoundaryMap) and a live
 * weather KPI preview (Open-Meteo, no API key required) that loads as
 * soon as the user finishes drawing the bbox / polygon.
 */

import React, { useState, useCallback } from 'react';
import { Save, X, MapPin, Thermometer, Droplets, Wind, CloudRain, Loader2 } from 'lucide-react';
import type { Field, FieldFormData, GeoPolygon } from '../types';
import { FieldBoundaryMap } from './FieldBoundaryMap.dynamic';

interface FieldFormProps {
  field?: Field;
  onSubmit: (data: FieldFormData) => void | Promise<void>;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

const MAX_NAME_LENGTH = 255;
const MIN_NAME_LENGTH = 2;
const MAX_AREA_HECTARES = 10000;
const MIN_AREA_HECTARES = 0.01;

// ---------------------------------------------------------------------------
// Shoelace formula: area in hectares from a GeoJSON ring [[lng,lat],...]
// ---------------------------------------------------------------------------
function ringAreaHectares(ring: number[][]): number {
  if (ring.length < 3) return 0;
  const lats = ring.map((p) => p[1]!);
  const avgLat = lats.reduce((s, v) => s + v, 0) / lats.length;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const cosLat = Math.cos(toRad(avgLat));
  const R = 6371000;
  const proj = ring.map((p) => ({ x: toRad(p[0]!) * cosLat * R, y: toRad(p[1]!) * R }));
  let area = 0;
  for (let i = 0; i < proj.length; i++) {
    const j = (i + 1) % proj.length;
    area += proj[i]!.x * proj[j]!.y;
    area -= proj[j]!.x * proj[i]!.y;
  }
  return Math.abs(area) / 2 / 10_000;
}

// ---------------------------------------------------------------------------
// Minimal weather preview — calls Open-Meteo directly (free, no API key)
// ---------------------------------------------------------------------------
interface WeatherPreview {
  temp: number;
  humidity: number;
  wind: number;
  precip: number;
  cloudCover: number;
  uvIndex?: number;
}

async function fetchOpenMeteoPreview(lat: number, lng: number): Promise<WeatherPreview> {
  const params = new URLSearchParams({
    latitude: lat.toFixed(6),
    longitude: lng.toFixed(6),
    current:
      'temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,cloud_cover,uv_index',
    wind_speed_unit: 'kmh',
    timezone: 'auto',
  });
  const res = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`, {
    signal: AbortSignal.timeout(10_000),
  });
  if (!res.ok) throw new Error(`Open-Meteo ${res.status}`);
  const data = await res.json();
  const c = data.current ?? {};
  return {
    temp: c.temperature_2m ?? 0,
    humidity: c.relative_humidity_2m ?? 0,
    wind: c.wind_speed_10m ?? 0,
    precip: c.precipitation ?? 0,
    cloudCover: c.cloud_cover ?? 0,
    uvIndex: c.uv_index,
  };
}

// ---------------------------------------------------------------------------
// KPI strip shown after the bbox is drawn
// ---------------------------------------------------------------------------
function WeatherKpiStrip({
  preview,
  loading,
  error,
}: {
  preview: WeatherPreview | null;
  loading: boolean;
  error: boolean;
}) {
  if (loading) {
    return (
      <div className="mt-3 flex items-center gap-2 text-sm text-gray-500 px-1">
        <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
        <span>جاري تحميل بيانات الطقس... | Fetching weather…</span>
      </div>
    );
  }
  if (error || !preview) {
    return (
      <p className="mt-3 text-xs text-gray-400 px-1">
        بيانات الطقس غير متاحة | Weather data unavailable
      </p>
    );
  }
  const kpis = [
    {
      icon: Thermometer,
      color: 'text-orange-500',
      bg: 'bg-orange-50',
      label: 'درجة الحرارة',
      value: `${preview.temp.toFixed(1)}°C`,
    },
    {
      icon: Droplets,
      color: 'text-blue-500',
      bg: 'bg-blue-50',
      label: 'الرطوبة',
      value: `${preview.humidity}%`,
    },
    {
      icon: Wind,
      color: 'text-cyan-500',
      bg: 'bg-cyan-50',
      label: 'الرياح',
      value: `${preview.wind} كم/س`,
    },
    {
      icon: CloudRain,
      color: 'text-indigo-500',
      bg: 'bg-indigo-50',
      label: 'التساقط',
      value: `${preview.precip} مم`,
    },
  ];
  return (
    <div className="mt-3 grid grid-cols-4 gap-2">
      {kpis.map(({ icon: Icon, color, bg, label, value }) => (
        <div key={label} className={`${bg} rounded-lg p-2 text-center`}>
          <Icon className={`${color} w-4 h-4 mx-auto mb-1`} />
          <p className="text-xs text-gray-500 mb-0.5">{label}</p>
          <p className={`text-sm font-bold ${color}`}>{value}</p>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export const FieldForm: React.FC<FieldFormProps> = ({
  field,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [formData, setFormData] = useState<FieldFormData>({
    name: field?.name || '',
    nameAr: field?.nameAr || '',
    area: field?.area || 0,
    crop: field?.crop || '',
    cropAr: field?.cropAr || '',
    description: field?.description || '',
    descriptionAr: field?.descriptionAr || '',
    farmId: field?.farmId || '',
    polygon: field?.polygon,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [weatherPreview, setWeatherPreview] = useState<WeatherPreview | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState(false);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    const trimmedNameAr = formData.nameAr.trim();
    if (!trimmedNameAr) {
      newErrors.nameAr = 'اسم الحقل بالعربية مطلوب';
    } else if (trimmedNameAr.length < MIN_NAME_LENGTH) {
      newErrors.nameAr = `الاسم قصير جداً (الحد الأدنى ${MIN_NAME_LENGTH} أحرف)`;
    } else if (trimmedNameAr.length > MAX_NAME_LENGTH) {
      newErrors.nameAr = `الاسم طويل جداً (الحد الأقصى ${MAX_NAME_LENGTH} حرف)`;
    }
    const trimmedName = formData.name.trim();
    if (!trimmedName) {
      newErrors.name = 'Field name in English is required';
    } else if (trimmedName.length < MIN_NAME_LENGTH) {
      newErrors.name = `Name too short (minimum ${MIN_NAME_LENGTH} characters)`;
    } else if (trimmedName.length > MAX_NAME_LENGTH) {
      newErrors.name = `Name too long (maximum ${MAX_NAME_LENGTH} characters)`;
    }
    if (!formData.area || formData.area <= 0) {
      newErrors.area = 'المساحة مطلوبة وأكبر من صفر';
    } else if (formData.area < MIN_AREA_HECTARES) {
      newErrors.area = `الحد الأدنى للمساحة ${MIN_AREA_HECTARES} هكتار`;
    } else if (formData.area > MAX_AREA_HECTARES) {
      newErrors.area = `الحد الأقصى للمساحة ${MAX_AREA_HECTARES} هكتار`;
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await onSubmit({
      ...formData,
      name: formData.name.trim(),
      nameAr: formData.nameAr.trim(),
    });
  };

  const handleChange = <K extends keyof FieldFormData>(key: K, value: FieldFormData[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  // Called by FieldBoundaryMap whenever the user finishes a polygon / rectangle
  const handleBoundaryChange = useCallback(
    (polygon: GeoPolygon | null, bbox: [number, number, number, number] | null) => {
      handleChange('polygon', polygon ?? undefined);

      if (!polygon || !bbox) {
        setWeatherPreview(null);
        setWeatherError(false);
        return;
      }

      // Auto-compute area from the drawn polygon (overrides manual input)
      const ring = polygon.coordinates[0];
      if (ring && ring.length >= 3) {
        const ha = ringAreaHectares(ring);
        if (ha > 0) {
          handleChange('area', parseFloat(ha.toFixed(2)));
        }
      }

      // Fetch Open-Meteo weather using bbox centroid (free, no API key)
      const [minLng, minLat, maxLng, maxLat] = bbox;
      const lat = (minLat + maxLat) / 2;
      const lng = (minLng + maxLng) / 2;

      setWeatherLoading(true);
      setWeatherError(false);
      setWeatherPreview(null);

      fetchOpenMeteoPreview(lat, lng)
        .then((w) => {
          setWeatherPreview(w);
          setWeatherLoading(false);
        })
        .catch(() => {
          setWeatherError(true);
          setWeatherLoading(false);
        });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const hasBoundary = !!formData.polygon;

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {field ? 'تعديل الحقل | Edit Field' : 'إضافة حقل جديد | Add New Field'}
      </h2>

      <div className="space-y-6">
        {/* ── Map boundary section ─────────────────────────────────────── */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-4 h-4 text-green-600" />
            <label className="text-sm font-medium text-gray-700">
              حدود الحقل على الخريطة | Field Boundary on Map
            </label>
            {hasBoundary && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
                ✓ تم تحديد الحدود
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mb-3">
            ارسم مضلعاً أو مستطيلاً على الخريطة لتحديد حدود الحقل. ستُحسب المساحة تلقائياً.
            <br />
            Draw a polygon or rectangle to define the field boundary. Area is computed automatically.
          </p>
          <FieldBoundaryMap
            onBoundaryChange={handleBoundaryChange}
            height="380px"
          />

          {/* Weather KPI preview — loads after bbox is set */}
          {(hasBoundary || weatherLoading) && (
            <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-100">
              <p className="text-xs font-medium text-gray-600 mb-1">
                بيانات الطقس الحالية للموقع | Current Location Weather
              </p>
              <WeatherKpiStrip
                preview={weatherPreview}
                loading={weatherLoading}
                error={weatherError}
              />
              {hasBoundary && !weatherLoading && (
                <p className="mt-2 text-xs text-gray-400">
                  مؤشرات الأقمار الصناعية (NDVI، EVI، LAI) ستُحمَّل بعد حفظ الحقل.
                  <br />
                  Satellite indices (NDVI, EVI, LAI) will load after the field is saved.
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── Name (Arabic) ─────────────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الاسم (بالعربية) *
          </label>
          <input
            type="text"
            required
            maxLength={MAX_NAME_LENGTH}
            value={formData.nameAr}
            onChange={(e) => handleChange('nameAr', e.target.value)}
            className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none focus:border-blue-500 ${errors.nameAr ? 'border-red-400' : 'border-gray-200'}`}
            placeholder="أدخل اسم الحقل"
          />
          {errors.nameAr && <p className="mt-1 text-sm text-red-600">{errors.nameAr}</p>}
        </div>

        {/* ── Name (English) ────────────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Name (English) *</label>
          <input
            type="text"
            required
            maxLength={MAX_NAME_LENGTH}
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none focus:border-blue-500 ${errors.name ? 'border-red-400' : 'border-gray-200'}`}
            placeholder="Enter field name"
            dir="ltr"
          />
          {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
        </div>

        {/* ── Area ─────────────────────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            المساحة (هكتار) *
            {hasBoundary && (
              <span className="mr-2 text-xs text-green-600 font-normal">
                — محسوبة من الخريطة تلقائياً
              </span>
            )}
          </label>
          <input
            type="number"
            required
            min={MIN_AREA_HECTARES}
            max={MAX_AREA_HECTARES}
            step="0.01"
            value={formData.area || ''}
            onChange={(e) => handleChange('area', parseFloat(e.target.value) || 0)}
            className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none focus:border-blue-500 ${errors.area ? 'border-red-400' : 'border-gray-200'}`}
            placeholder="0.00"
          />
          {errors.area && <p className="mt-1 text-sm text-red-600">{errors.area}</p>}
        </div>

        {/* ── Crop (Arabic) ─────────────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            المحصول (بالعربية)
          </label>
          <input
            type="text"
            value={formData.cropAr || ''}
            onChange={(e) => handleChange('cropAr', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="نوع المحصول"
          />
        </div>

        {/* ── Crop (English) ────────────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Crop (English)</label>
          <input
            type="text"
            value={formData.crop || ''}
            onChange={(e) => handleChange('crop', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Crop type"
            dir="ltr"
          />
        </div>

        {/* ── Description (Arabic) ──────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الوصف (بالعربية)
          </label>
          <textarea
            value={formData.descriptionAr || ''}
            onChange={(e) => handleChange('descriptionAr', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="وصف الحقل"
          />
        </div>

        {/* ── Description (English) ─────────────────────────────────────── */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description (English)
          </label>
          <textarea
            value={formData.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Field description"
            dir="ltr"
          />
        </div>
      </div>

      {/* ── Actions ───────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-end gap-3 mt-8 pt-6 border-t-2 border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center gap-2 px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            <X className="w-4 h-4" />
            <span>إلغاء | Cancel</span>
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          <span>{isSubmitting ? 'جاري الحفظ...' : 'حفظ | Save'}</span>
        </button>
      </div>
    </form>
  );
};

export default FieldForm;
