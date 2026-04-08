'use client';

// Google Maps Field Drawer Component
// مكون رسم حدود الحقل على خرائط جوجل
// Replaces DrawableMap.tsx (Leaflet) with Google Maps API
// Exports GeoJSON polygon via onBoundaryChange callback

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { Undo2, Pentagon, Square, Trash2, X, Check, Map } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface GoogleMapsFieldDrawerProps {
  onBoundaryChange?: (geojson: GeoJSON.Polygon | null) => void;
  initialCenter?: [number, number]; // [lat, lng]
  initialZoom?: number;
  height?: string;
  readOnly?: boolean;
  initialPolygon?: GeoJSON.Polygon | null;
}

type DrawingMode = 'polygon' | 'rectangle' | null;

interface Vertex {
  lat: number;
  lng: number;
}

// ---------------------------------------------------------------------------
// Loading fallback
// ---------------------------------------------------------------------------

const MapLoadingFallback = ({ height }: { height: string }) => (
  <div
    className="bg-gray-100 animate-pulse flex items-center justify-center rounded-lg"
    style={{ height }}
  >
    <p className="text-gray-500 text-sm">جاري تحميل الخريطة...</p>
  </div>
);

// ---------------------------------------------------------------------------
// Measurement utilities (copied from DrawableMap.tsx)
// ---------------------------------------------------------------------------

function haversineDistance(a: Vertex, b: Vertex): number {
  const R = 6371000;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const sinLat = Math.sin(dLat / 2);
  const sinLng = Math.sin(dLng / 2);
  const h =
    sinLat * sinLat +
    Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * sinLng * sinLng;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function computePerimeter(vertices: Vertex[]): number {
  if (vertices.length < 2) return 0;
  let total = 0;
  for (let i = 0; i < vertices.length; i++) {
    const next = (i + 1) % vertices.length;
    total += haversineDistance(vertices[i]!, vertices[next]!);
  }
  return total;
}

function computeAreaHectares(vertices: Vertex[]): number {
  if (vertices.length < 3) return 0;
  const avgLat = vertices.reduce((s, v) => s + v.lat, 0) / vertices.length;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const cosLat = Math.cos(toRad(avgLat));
  const R = 6371000;
  const projected = vertices.map((v) => ({
    x: toRad(v.lng) * cosLat * R,
    y: toRad(v.lat) * R,
  }));
  let area = 0;
  for (let i = 0; i < projected.length; i++) {
    const j = (i + 1) % projected.length;
    area += projected[i]!.x * projected[j]!.y;
    area -= projected[j]!.x * projected[i]!.y;
  }
  area = Math.abs(area) / 2;
  return area / 10000;
}

function verticesToGeoJSON(vertices: Vertex[]): GeoJSON.Polygon {
  const ring = vertices.map((v) => [v.lng, v.lat] as [number, number]);
  if (ring.length > 0 && ring[0]) {
    ring.push([...ring[0]]);
  }
  return { type: 'Polygon', coordinates: [ring] };
}

function geoJSONToVertices(polygon: GeoJSON.Polygon): Vertex[] {
  const ring = polygon.coordinates[0];
  if (!ring || ring.length < 2) return [];
  // GeoJSON is [lng, lat]; remove closing point (last == first)
  return ring.slice(0, -1).map(([lng, lat]) => ({ lat: lat!, lng: lng! }));
}

// ---------------------------------------------------------------------------
// Inner component (runs only in browser)
// ---------------------------------------------------------------------------

function GoogleMapsFieldDrawerInner({
  onBoundaryChange,
  initialCenter = [15.5527, 48.5164],
  initialZoom = 7,
  height = '500px',
  readOnly = false,
  initialPolygon,
}: GoogleMapsFieldDrawerProps) {
  const [GoogleMapComponents, setGoogleMapComponents] = useState<{
    GoogleMap: React.ComponentType<any>;
    Polygon: React.ComponentType<any>;
    Polyline: React.ComponentType<any>;
    Circle: React.ComponentType<any>;
    useJsApiLoader: (opts: any) => { isLoaded: boolean; loadError?: Error };
  } | null>(null);

  const [mode, setMode] = useState<DrawingMode>(null);
  const [vertices, setVertices] = useState<Vertex[]>(() =>
    initialPolygon ? geoJSONToVertices(initialPolygon) : []
  );
  const [completed, setCompleted] = useState<boolean>(() => !!initialPolygon);
  const [mapType, setMapType] = useState<'roadmap' | 'satellite'>('roadmap');
  const rectStage = useRef<'first' | 'second'>('first');

  // Load @react-google-maps/api dynamically
  useEffect(() => {
    import('@react-google-maps/api').then((mod) => {
      setGoogleMapComponents({
        GoogleMap: mod.GoogleMap,
        Polygon: mod.Polygon,
        Polyline: mod.Polyline,
        Circle: mod.Circle,
        useJsApiLoader: mod.useJsApiLoader,
      });
    });
  }, []);

  const emitBoundary = useCallback(
    (verts: Vertex[]) => {
      onBoundaryChange?.(verticesToGeoJSON(verts));
    },
    [onBoundaryChange]
  );

  const handleMapClick = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (readOnly || !mode || completed || !e.latLng) return;
      const v: Vertex = { lat: e.latLng.lat(), lng: e.latLng.lng() };

      if (mode === 'rectangle') {
        if (rectStage.current === 'first') {
          setVertices([v]);
          rectStage.current = 'second';
        } else {
          const first = vertices[0] ?? v;
          const rectVertices: Vertex[] = [
            { lat: first.lat, lng: first.lng },
            { lat: first.lat, lng: v.lng },
            { lat: v.lat, lng: v.lng },
            { lat: v.lat, lng: first.lng },
          ];
          setVertices(rectVertices);
          setCompleted(true);
          rectStage.current = 'first';
          emitBoundary(rectVertices);
        }
      } else {
        setVertices((prev) => [...prev, v]);
      }
    },
    [readOnly, mode, completed, vertices, emitBoundary]
  );

  const handleComplete = useCallback(() => {
    if (vertices.length < 3) return;
    setCompleted(true);
    emitBoundary(vertices);
  }, [vertices, emitBoundary]);

  const handleClear = useCallback(() => {
    setVertices([]);
    setCompleted(false);
    rectStage.current = 'first';
    onBoundaryChange?.(null);
  }, [onBoundaryChange]);

  const handleCancel = useCallback(() => {
    setVertices([]);
    setCompleted(false);
    setMode(null);
    rectStage.current = 'first';
    onBoundaryChange?.(null);
  }, [onBoundaryChange]);

  const handleUndo = useCallback(() => {
    if (completed || vertices.length === 0) return;
    setVertices((prev) => prev.slice(0, -1));
  }, [completed, vertices.length]);

  const startPolygon = useCallback(() => {
    handleClear();
    setMode('polygon');
  }, [handleClear]);

  const startRectangle = useCallback(() => {
    handleClear();
    setMode('rectangle');
  }, [handleClear]);

  const areaHectares = useMemo(() => computeAreaHectares(vertices), [vertices]);
  const perimeter = useMemo(() => computePerimeter(vertices), [vertices]);

  if (!GoogleMapComponents) {
    return <MapLoadingFallback height={height} />;
  }

  const { GoogleMap, Polygon, Polyline, Circle, useJsApiLoader } = GoogleMapComponents;

  return (
    <GoogleMapLoaderWrapper
      GoogleMap={GoogleMap}
      Polygon={Polygon}
      Polyline={Polyline}
      Circle={Circle}
      useJsApiLoader={useJsApiLoader}
      mode={mode}
      vertices={vertices}
      completed={completed}
      mapType={mapType}
      readOnly={readOnly}
      areaHectares={areaHectares}
      perimeter={perimeter}
      initialCenter={initialCenter}
      initialZoom={initialZoom}
      height={height}
      onMapClick={handleMapClick}
      onComplete={handleComplete}
      onClear={handleClear}
      onCancel={handleCancel}
      onUndo={handleUndo}
      onStartPolygon={startPolygon}
      onStartRectangle={startRectangle}
      onToggleMapType={() => setMapType((t) => (t === 'roadmap' ? 'satellite' : 'roadmap'))}
    />
  );
}

// ---------------------------------------------------------------------------
// Loader wrapper — separated to allow calling useJsApiLoader hook
// ---------------------------------------------------------------------------

interface LoaderProps {
  GoogleMap: React.ComponentType<any>;
  Polygon: React.ComponentType<any>;
  Polyline: React.ComponentType<any>;
  Circle: React.ComponentType<any>;
  useJsApiLoader: (opts: any) => { isLoaded: boolean; loadError?: Error };
  mode: DrawingMode;
  vertices: Vertex[];
  completed: boolean;
  mapType: 'roadmap' | 'satellite';
  readOnly: boolean;
  areaHectares: number;
  perimeter: number;
  initialCenter: [number, number];
  initialZoom: number;
  height: string;
  onMapClick: (e: google.maps.MapMouseEvent) => void;
  onComplete: () => void;
  onClear: () => void;
  onCancel: () => void;
  onUndo: () => void;
  onStartPolygon: () => void;
  onStartRectangle: () => void;
  onToggleMapType: () => void;
}

function GoogleMapLoaderWrapper({
  GoogleMap,
  Polygon,
  Polyline,
  Circle,
  useJsApiLoader,
  mode,
  vertices,
  completed,
  mapType,
  readOnly,
  areaHectares,
  perimeter,
  initialCenter,
  initialZoom,
  height,
  onMapClick,
  onComplete,
  onClear,
  onCancel,
  onUndo,
  onStartPolygon,
  onStartRectangle,
  onToggleMapType,
}: LoaderProps) {
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '',
  });

  if (loadError) {
    return (
      <div
        className="bg-red-50 border border-red-200 flex items-center justify-center rounded-lg"
        style={{ height }}
      >
        <p className="text-red-600 text-sm">فشل تحميل خرائط جوجل. تحقق من مفتاح API.</p>
      </div>
    );
  }

  if (!isLoaded) {
    return <MapLoadingFallback height={height} />;
  }

  const center = { lat: initialCenter[0], lng: initialCenter[1] };
  const paths = vertices.map((v) => ({ lat: v.lat, lng: v.lng }));

  const modeLabel =
    mode === 'polygon'
      ? 'رسم مضلع — انقر لإضافة نقاط'
      : mode === 'rectangle'
        ? vertices.length === 0
          ? 'رسم مستطيل — انقر لتحديد الزاوية الأولى'
          : 'انقر لتحديد الزاوية الثانية'
        : null;

  return (
    <div
      className={`relative rounded-lg overflow-hidden border-2 ${
        mode === 'polygon'
          ? 'border-green-500'
          : mode === 'rectangle'
            ? 'border-blue-500'
            : 'border-gray-200'
      }`}
      dir="rtl"
    >
      {/* Toolbar */}
      {!readOnly && (
        <div className="absolute top-3 right-3 z-10 flex flex-col gap-2">
          {!mode && !completed && (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={onStartPolygon}
                className="px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-blue-700 transition-colors inline-flex items-center gap-1.5"
              >
                <Pentagon size={14} />
                رسم مضلع
              </button>
              <button
                type="button"
                onClick={onStartRectangle}
                className="px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-indigo-700 transition-colors inline-flex items-center gap-1.5"
              >
                <Square size={14} />
                رسم مستطيل
              </button>
            </div>
          )}

          {mode && !completed && (
            <div className="flex gap-2">
              {mode === 'polygon' && vertices.length >= 3 && (
                <button
                  type="button"
                  onClick={onComplete}
                  className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-green-700 transition-colors inline-flex items-center gap-1"
                >
                  <Check size={14} />
                  إكمال
                </button>
              )}
              {mode === 'polygon' && vertices.length > 0 && (
                <button
                  type="button"
                  onClick={onUndo}
                  className="px-3 py-2 bg-gray-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-gray-700 transition-colors inline-flex items-center gap-1"
                >
                  <Undo2 size={14} />
                  تراجع
                </button>
              )}
              <button
                type="button"
                onClick={onClear}
                className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors inline-flex items-center gap-1"
              >
                <Trash2 size={14} />
                مسح
              </button>
              <button
                type="button"
                onClick={onCancel}
                className="px-3 py-2 bg-red-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-red-600 transition-colors inline-flex items-center gap-1"
              >
                <X size={14} />
                إلغاء
              </button>
            </div>
          )}

          {completed && (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClear}
                className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors inline-flex items-center gap-1"
              >
                <Trash2 size={14} />
                مسح
              </button>
              <button
                type="button"
                onClick={onCancel}
                className="px-3 py-2 bg-red-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-red-600 transition-colors inline-flex items-center gap-1"
              >
                <X size={14} />
                إلغاء
              </button>
            </div>
          )}
        </div>
      )}

      {/* Map type toggle */}
      <div className="absolute top-3 left-3 z-10">
        <button
          type="button"
          onClick={onToggleMapType}
          className="px-3 py-2 bg-white text-gray-700 text-sm font-medium rounded-md shadow-md hover:bg-gray-100 transition-colors inline-flex items-center gap-1.5 border border-gray-300"
        >
          <Map size={14} />
          {mapType === 'roadmap' ? 'صور فضائية' : 'خريطة الشوارع'}
        </button>
      </div>

      {/* Status bar */}
      {!readOnly && modeLabel && !completed && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10 bg-white/95 backdrop-blur px-4 py-2 rounded-md shadow-md text-sm font-medium text-gray-700 border border-gray-200 flex flex-col items-center gap-1">
          <div>
            {modeLabel}
            {mode === 'polygon' && vertices.length > 0 && (
              <span className="mr-2 text-blue-600">النقاط: {vertices.length}</span>
            )}
          </div>
          {vertices.length >= 2 && (
            <div className="text-xs text-gray-500">
              المساحة: {areaHectares.toFixed(2)} هكتار | المحيط: {perimeter.toFixed(0)} م
            </div>
          )}
        </div>
      )}

      {/* Completion badge */}
      {completed && vertices.length >= 3 && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10 bg-green-50 border border-green-300 px-4 py-2 rounded-md shadow-md text-sm font-medium text-green-800 flex flex-col items-center gap-1">
          <div>تم تحديد المنطقة — النقاط: {vertices.length}</div>
          <div className="text-xs">
            المساحة: {areaHectares.toFixed(2)} هكتار | المحيط: {perimeter.toFixed(0)} م
          </div>
        </div>
      )}

      {/* Google Map */}
      <GoogleMap
        mapContainerStyle={{ height, width: '100%' }}
        center={center}
        zoom={initialZoom}
        mapTypeId={mapType}
        onClick={readOnly ? undefined : onMapClick}
        options={{
          disableDefaultUI: false,
          zoomControl: true,
          streetViewControl: false,
          mapTypeControl: false,
          fullscreenControl: true,
        }}
      >
        {/* Vertex markers */}
        {vertices.map((v, i) => (
          <Circle
            key={`vertex-${i}`}
            center={{ lat: v.lat, lng: v.lng }}
            radius={15}
            options={{
              fillColor: i === 0 ? '#16a34a' : '#2563eb',
              fillOpacity: 1,
              strokeColor: '#ffffff',
              strokeWeight: 2,
              clickable: false,
            }}
          />
        ))}

        {/* Polyline preview while drawing */}
        {!completed && vertices.length >= 2 && (
          <Polyline
            path={paths}
            options={{
              strokeColor: '#2563eb',
              strokeWeight: 2,
              strokeOpacity: 0.8,
              icons: [{ icon: { path: 'M 0,-1 0,1', strokeOpacity: 1, scale: 4 }, offset: '0', repeat: '20px' }],
            }}
          />
        )}

        {/* Completed polygon */}
        {(completed || readOnly) && vertices.length >= 3 && (
          <Polygon
            paths={paths}
            options={{
              fillColor: '#3b82f6',
              fillOpacity: 0.15,
              strokeColor: '#2563eb',
              strokeWeight: 2,
            }}
          />
        )}
      </GoogleMap>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Export — SSR-safe dynamic wrapper
// ---------------------------------------------------------------------------

const GoogleMapsFieldDrawerDynamic = dynamic(
  () => Promise.resolve(GoogleMapsFieldDrawerInner),
  {
    ssr: false,
    loading: () => <MapLoadingFallback height="500px" />,
  }
);

export default GoogleMapsFieldDrawerDynamic;
