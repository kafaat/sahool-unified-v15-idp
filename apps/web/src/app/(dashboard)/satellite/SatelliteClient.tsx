'use client';

import React, { useState, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { AlertTriangle, Search } from 'lucide-react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import {
  useSatelliteFields,
  useSatelliteStats,
} from '@/features/satellite';
import type { SatelliteField, IndexType } from '@/features/satellite';

/* ─── Index Buttons ─────────────────────────────────────────── */
const INDICES = [
  { id: 'ndvi',  label: 'NDVI',  key: 'ndvi'  as IndexType },
  { id: 'evi',   label: 'EVI',   key: 'evi'   as IndexType },
  { id: 'sar',   label: 'SAR',   key: 'ndvi'  as IndexType },
  { id: 'ndre',  label: 'NDRE',  key: 'ndre'  as IndexType },
  { id: 'ndwi',  label: 'NDWI',  key: 'ndwi'  as IndexType },
  { id: 'lai',   label: 'LAI',   key: 'lai'   as IndexType },
];

/* ─── NDVI color helper ─────────────────────────────────────── */
function ndviColor(v: number): string {
  if (v >= 0.6) return '#16a34a';
  if (v >= 0.45) return '#65a30d';
  if (v >= 0.3) return '#f59e0b';
  if (v >= 0.15) return '#ea580c';
  return '#dc2626';
}

function ndviLabel(v: number): string {
  if (v >= 0.6) return 'ممتاز';
  if (v >= 0.45) return 'جيد';
  if (v >= 0.3) return 'متوسط';
  if (v >= 0.15) return 'ضعيف';
  return 'حرج';
}

function ndviLabelColor(v: number): string {
  if (v >= 0.6) return 'text-green-700 bg-green-50';
  if (v >= 0.45) return 'text-lime-700 bg-lime-50';
  if (v >= 0.3) return 'text-amber-700 bg-amber-50';
  return 'text-red-700 bg-red-50';
}

/* ─── Field card in right panel ─────────────────────────────── */
function FieldCard({
  field,
  selected,
  onClick,
}: {
  field: SatelliteField;
  selected: boolean;
  onClick: () => void;
}) {
  const ndvi = field.indices.ndvi ?? 0;
  const ndviChange = field.indices.ndviChange ?? 0;
  const barPct = Math.max(0, Math.min(100, ndvi * 100));
  const changeSign = ndviChange >= 0 ? '+' : '';
  const color = ndviColor(ndvi);

  return (
    <div
      onClick={onClick}
      className={`rounded-xl border p-3 cursor-pointer transition-all hover:shadow-md ${
        selected
          ? 'border-green-500 bg-green-50/60 shadow-sm'
          : 'border-gray-200 bg-white hover:border-green-300'
      }`}
    >
      {/* Name + badge */}
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-bold text-gray-800 truncate">{field.fieldName}</div>
          <div className="text-xs text-gray-400 truncate">{field.fieldNameAr}</div>
        </div>
        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap ${ndviLabelColor(ndvi)}`}>
          {ndviLabel(ndvi)}
        </span>
      </div>

      {/* NDVI value + change */}
      <div className="flex items-center gap-1.5 mb-1">
        <span className="text-xs font-bold" style={{ color }}>
          NDVI: {ndvi.toFixed(2)}
        </span>
        <span
          className="text-[10px] font-semibold"
          style={{ color: ndviChange >= 0 ? '#16a34a' : '#dc2626' }}
        >
          ({changeSign}{ndviChange.toFixed(2)})
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden mb-2">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${barPct}%`, background: color }}
        />
      </div>

      {/* Footer: date + area + link */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[10px] text-gray-400">
          <span>{field.lastCapture}</span>
          <span>·</span>
          <span>{field.area.toFixed(2)} هـ</span>
        </div>
        <Link
          href={`/satellite-monitor/field/${field.id}`}
          onClick={e => e.stopPropagation()}
          className="text-[10px] font-semibold text-green-600 hover:text-green-700 hover:underline"
        >
          تفاصيل
        </Link>
      </div>
    </div>
  );
}

/* ─── Stats card ─────────────────────────────────────────────── */
function StatCard({ icon, label, value, color }: { icon: string; label: string; value: string; color: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
        style={{ background: `${color}15`, color }}
      >
        {icon}
      </div>
      <div>
        <div className="text-[10px] text-gray-400">{label}</div>
        <div className="text-lg font-black tabular-nums" style={{ color }}>{value}</div>
      </div>
    </div>
  );
}

/* ─── Map container style ────────────────────────────────────── */
const MAP_CONTAINER = { width: '100%', height: '100%' };
const YEMEN_CENTER = { lat: 15.55, lng: 48.52 };

/* ═══ MAIN COMPONENT ═════════════════════════════════════════ */
export default function SatelliteClient() {
  const [selIdx, setSelIdx] = useState('ndvi');
  const [selectedField, setSelectedField] = useState<SatelliteField | null>(null);
  const [search, setSearch] = useState('');
  const [mapRef, setMapRef] = useState<google.maps.Map | null>(null);

  const { data: fields = [], isLoading, error } = useSatelliteFields();
  const { data: stats } = useSatelliteStats();

  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '';
  const { isLoaded: mapsLoaded } = useJsApiLoader({
    googleMapsApiKey: apiKey,
    language: 'ar',
  });

  /* Compute map center from real field coordinates */
  const mapCenter = useMemo(() => {
    const fieldsWithCoords = fields.filter(
      f => f.coordinates?.lat && f.coordinates?.lng,
    );
    if (fieldsWithCoords.length === 0) return YEMEN_CENTER;
    const avgLat = fieldsWithCoords.reduce((s, f) => s + f.coordinates.lat, 0) / fieldsWithCoords.length;
    const avgLng = fieldsWithCoords.reduce((s, f) => s + f.coordinates.lng, 0) / fieldsWithCoords.length;
    return { lat: avgLat, lng: avgLng };
  }, [fields]);

  const filteredFields = useMemo(
    () =>
      fields.filter(
        f =>
          !search ||
          f.fieldName.toLowerCase().includes(search.toLowerCase()) ||
          f.fieldNameAr.includes(search),
      ),
    [fields, search],
  );

  const onMapLoad = useCallback((map: google.maps.Map) => {
    setMapRef(map);
  }, []);

  /* Fit map to field bounds when fields load */
  React.useEffect(() => {
    if (!mapRef || fields.length === 0) return;
    const fieldsWithCoords = fields.filter(f => f.coordinates?.lat && f.coordinates?.lng);
    if (fieldsWithCoords.length === 0) return;
    const bounds = new window.google.maps.LatLngBounds();
    fieldsWithCoords.forEach(f => bounds.extend({ lat: f.coordinates.lat, lng: f.coordinates.lng }));
    mapRef.fitBounds(bounds, 80);
  }, [mapRef, fields]);

  /* Loading */
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] rounded-xl bg-white border border-gray-200">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto mb-3" />
          <p className="text-sm text-gray-500">جاري تحميل بيانات الأقمار الصناعية…</p>
        </div>
      </div>
    );
  }

  /* Error */
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px] rounded-xl bg-white border border-red-200">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <p className="font-medium text-red-600">فشل في تحميل بيانات الأقمار الصناعية</p>
          <p className="text-sm text-gray-400 mt-1">Failed to load satellite data</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 rounded bg-green-600 text-white text-sm font-bold hover:bg-green-700"
          >
            إعادة المحاولة / Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4" dir="rtl">

      {/* ── Page title ── */}
      <div>
        <h1 className="text-lg font-bold text-gray-800">صور الأقمار الصناعية وتحليل الغطاء النباتي</h1>
        <p className="text-xs text-gray-400">Satellite Imagery &amp; Vegetation Analysis</p>
      </div>

      {/* ── Stats row ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon="🛰" label="آخر التقاط" value={stats?.lastCapture ?? '—'} color="#3b82f6" />
        <StatCard icon="📈" label="متوسط NDVI" value={stats?.averageNdvi?.toFixed(2) ?? '—'} color="#16a34a" />
        <StatCard icon="📍" label="الحقول المراقبة" value={String(stats?.totalFields ?? fields.length)} color="#8b5cf6" />
        <StatCard icon="◫" label="المساحة الكلية (هـ)" value={stats?.totalArea?.toFixed(1) ?? '—'} color="#f59e0b" />
      </div>

      {/* ── Index filter bar ── */}
      <div className="bg-white border border-gray-200 rounded-xl p-2 flex items-center gap-2 flex-wrap">
        <div className="flex gap-1 flex-wrap">
          {INDICES.map(idx => (
            <button
              key={idx.id}
              onClick={() => setSelIdx(idx.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                selIdx === idx.id
                  ? 'bg-green-600 text-white border-green-600 shadow-sm'
                  : 'text-gray-500 border-gray-200 hover:border-green-400 hover:text-green-600'
              }`}
            >
              {idx.label}
            </button>
          ))}
        </div>
        <div className="mr-auto">
          <Link
            href="/satellite-monitor/add-field"
            className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition-colors"
          >
            <span>+</span>
            <span>إضافة حقل</span>
          </Link>
        </div>
      </div>

      {/* ── Main content: map + field list ── */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-4" style={{ minHeight: 520 }}>

        {/* Map */}
        <div className="rounded-xl overflow-hidden border border-gray-200 bg-gray-100" style={{ minHeight: 480 }}>
          {mapsLoaded ? (
            <GoogleMap
              mapContainerStyle={MAP_CONTAINER}
              center={mapCenter}
              zoom={13}
              mapTypeId="satellite"
              onLoad={onMapLoad}
              options={{
                mapTypeControl: true,
                streetViewControl: false,
                fullscreenControl: true,
                zoomControl: true,
              }}
            >
              {fields.map(field => {
                const lat = field.coordinates?.lat;
                const lng = field.coordinates?.lng;
                if (!lat || !lng) return null;
                const isSelected = selectedField?.id === field.id;
                return (
                  <Marker
                    key={field.id}
                    position={{ lat, lng }}
                    onClick={() => setSelectedField(isSelected ? null : field)}
                    icon={{
                      path: window.google.maps.SymbolPath.CIRCLE,
                      scale: isSelected ? 14 : 10,
                      fillColor: ndviColor(field.indices.ndvi ?? 0),
                      fillOpacity: 0.9,
                      strokeColor: isSelected ? '#ffffff' : ndviColor(field.indices.ndvi ?? 0),
                      strokeWeight: isSelected ? 3 : 1.5,
                    }}
                    title={field.fieldNameAr}
                  />
                );
              })}

              {selectedField && selectedField.coordinates?.lat && selectedField.coordinates?.lng && (
                <InfoWindow
                  position={{ lat: selectedField.coordinates.lat, lng: selectedField.coordinates.lng }}
                  onCloseClick={() => setSelectedField(null)}
                >
                  <div className="text-sm p-1 min-w-[140px]" style={{ direction: 'rtl' }}>
                    <div className="font-bold text-gray-800 mb-1">{selectedField.fieldNameAr}</div>
                    <div className="text-xs text-gray-500 mb-0.5">
                      NDVI: <span className="font-semibold" style={{ color: ndviColor(selectedField.indices.ndvi ?? 0) }}>
                        {(selectedField.indices.ndvi ?? 0).toFixed(2)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">{selectedField.area.toFixed(1)} هكتار</div>
                    <Link
                      href={`/satellite-monitor/field/${selectedField.id}`}
                      className="inline-block mt-1.5 text-xs text-green-600 font-semibold hover:underline"
                    >
                      عرض التفاصيل ←
                    </Link>
                  </div>
                </InfoWindow>
              )}
            </GoogleMap>
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-100">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
            </div>
          )}
        </div>

        {/* Right: fields panel */}
        <div className="flex flex-col gap-3">

          {/* Panel header */}
          <div className="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center justify-between">
            <span className="font-bold text-gray-800 text-sm">الحقول</span>
            <span className="text-xs text-gray-400">{fields.length} حقل</span>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute top-1/2 -translate-y-1/2 right-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="بحث في الحقول..."
              className="w-full bg-white border border-gray-200 rounded-xl pr-9 pl-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:border-green-400"
            />
          </div>

          {/* Field cards */}
          <div className="flex flex-col gap-2 overflow-y-auto" style={{ maxHeight: 400 }}>
            {filteredFields.length === 0 ? (
              <div className="text-center text-sm text-gray-400 py-8">لا توجد حقول</div>
            ) : (
              filteredFields.map(field => (
                <FieldCard
                  key={field.id}
                  field={field}
                  selected={selectedField?.id === field.id}
                  onClick={() => setSelectedField(prev => prev?.id === field.id ? null : field)}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
