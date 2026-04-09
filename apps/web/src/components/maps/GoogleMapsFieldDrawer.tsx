'use client';

// Google Maps Field Drawer Component
// مكون رسم حدود الحقل على خرائط جوجل
// Supports: polygon (multipoint), rectangle (bbox), circle, freehand
// Exports GeoJSON polygon via onBoundaryChange callback

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import {
  Undo2, Pentagon, Square, Trash2, X, Check, Map,
  Circle as CircleIcon, Pen, Search, Loader2,
} from 'lucide-react';

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

type DrawingMode = 'polygon' | 'rectangle' | 'circle' | 'freehand' | null;

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
// Measurement utilities
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
  return ring.slice(0, -1).map(([lng, lat]) => ({ lat: lat!, lng: lng! }));
}

/** Convert a circle (center + radius in meters) to an approximate polygon */
function circleToPolygon(center: Vertex, radiusM: number, numPoints = 48): Vertex[] {
  const toRad = (d: number) => (d * Math.PI) / 180;
  const toDeg = (r: number) => (r * 180) / Math.PI;
  const R = 6371000;
  const vertices: Vertex[] = [];
  for (let i = 0; i < numPoints; i++) {
    const angle = (2 * Math.PI * i) / numPoints;
    const lat = toDeg(
      Math.asin(
        Math.sin(toRad(center.lat)) * Math.cos(radiusM / R) +
        Math.cos(toRad(center.lat)) * Math.sin(radiusM / R) * Math.cos(angle)
      )
    );
    const lng =
      center.lng +
      toDeg(
        Math.atan2(
          Math.sin(angle) * Math.sin(radiusM / R) * Math.cos(toRad(center.lat)),
          Math.cos(radiusM / R) - Math.sin(toRad(center.lat)) * Math.sin(toRad(lat))
        )
      );
    vertices.push({ lat, lng });
  }
  return vertices;
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
  // Always start in satellite view
  const [mapType, setMapType] = useState<'roadmap' | 'satellite'>('satellite');

  // Rectangle stage
  const rectStage = useRef<'first' | 'second'>('first');

  // Circle state
  const [circleCenter, setCircleCenter] = useState<Vertex | null>(null);
  const [circleRadiusM, setCircleRadiusM] = useState<number>(0);

  // Freehand state
  const isMouseDown = useRef(false);
  const lastFreehandPoint = useRef<Vertex | null>(null);

  // Map instance ref (for programmatic pan/zoom)
  const mapInstanceRef = useRef<google.maps.Map | null>(null);

  // Location search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

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

  // ------------------------------------------------------------------
  // Map click handler
  // ------------------------------------------------------------------
  const handleMapClick = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (readOnly || !mode || completed || !e.latLng) return;
      // Freehand uses mousemove/mousedown instead of click
      if (mode === 'freehand') return;

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
      } else if (mode === 'circle') {
        if (!circleCenter) {
          setCircleCenter(v);
        } else {
          const radius = haversineDistance(circleCenter, v);
          const poly = circleToPolygon(circleCenter, radius);
          setVertices(poly);
          setCompleted(true);
          setMode(null);
          setCircleCenter(null);
          setCircleRadiusM(0);
          emitBoundary(poly);
        }
      } else {
        // polygon — multipoint
        setVertices((prev) => [...prev, v]);
      }
    },
    [readOnly, mode, completed, vertices, circleCenter, emitBoundary]
  );

  // ------------------------------------------------------------------
  // Mouse move — freehand drawing + circle radius preview
  // ------------------------------------------------------------------
  const handleMouseMove = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (!e.latLng) return;
      const v: Vertex = { lat: e.latLng.lat(), lng: e.latLng.lng() };

      if (mode === 'circle' && circleCenter) {
        setCircleRadiusM(haversineDistance(circleCenter, v));
      }

      if (mode === 'freehand' && isMouseDown.current && !completed) {
        const last = lastFreehandPoint.current;
        // Minimum 30 m between consecutive freehand points to avoid oversampling
        if (last && haversineDistance(last, v) < 30) return;
        lastFreehandPoint.current = v;
        setVertices((prev) => [...prev, v]);
      }
    },
    [mode, circleCenter, completed]
  );

  const handleMouseDown = useCallback(() => {
    if (mode === 'freehand' && !completed) {
      isMouseDown.current = true;
    }
  }, [mode, completed]);

  const handleMouseUp = useCallback(() => {
    if (mode === 'freehand' && isMouseDown.current) {
      isMouseDown.current = false;
      lastFreehandPoint.current = null;
      setVertices((prev) => {
        if (prev.length >= 3) {
          setCompleted(true);
          emitBoundary(prev);
        }
        return prev;
      });
    }
  }, [mode, emitBoundary]);

  // ------------------------------------------------------------------
  // Drawing actions
  // ------------------------------------------------------------------
  const handleComplete = useCallback(() => {
    if (vertices.length < 3) return;
    setCompleted(true);
    emitBoundary(vertices);
  }, [vertices, emitBoundary]);

  const handleUndo = useCallback(() => {
    if (completed) return;
    if (mode === 'circle' && circleCenter) {
      setCircleCenter(null);
      setCircleRadiusM(0);
      return;
    }
    setVertices((prev) => prev.slice(0, -1));
  }, [completed, mode, circleCenter]);

  const handleClear = useCallback(() => {
    setVertices([]);
    setCompleted(false);
    setCircleCenter(null);
    setCircleRadiusM(0);
    rectStage.current = 'first';
    isMouseDown.current = false;
    lastFreehandPoint.current = null;
    onBoundaryChange?.(null);
  }, [onBoundaryChange]);

  const handleCancel = useCallback(() => {
    handleClear();
    setMode(null);
  }, [handleClear]);

  const startMode = useCallback(
    (newMode: DrawingMode) => {
      handleClear();
      setMode(newMode);
    },
    [handleClear]
  );

  // ------------------------------------------------------------------
  // Location search
  // ------------------------------------------------------------------
  const handleSearch = useCallback(async () => {
    const q = searchQuery.trim();
    if (!q || typeof window === 'undefined' || !window.google) return;
    setSearching(true);
    setSearchError('');
    try {
      const geocoder = new window.google.maps.Geocoder();
      const result = await geocoder.geocode({ address: q });
      if (result.results[0]) {
        const loc = result.results[0].geometry.location;
        mapInstanceRef.current?.panTo({ lat: loc.lat(), lng: loc.lng() });
        mapInstanceRef.current?.setZoom(14);
      } else {
        setSearchError('لم يتم العثور على الموقع');
      }
    } catch {
      setSearchError('خطأ في البحث');
    } finally {
      setSearching(false);
    }
  }, [searchQuery]);

  const handleSearchKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSearch();
      }
    },
    [handleSearch]
  );

  // ------------------------------------------------------------------
  // Derived values
  // ------------------------------------------------------------------
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
      circleCenter={circleCenter}
      circleRadiusM={circleRadiusM}
      searchQuery={searchQuery}
      searching={searching}
      searchError={searchError}
      mapInstanceRef={mapInstanceRef}
      onMapClick={handleMapClick}
      onMouseMove={handleMouseMove}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onComplete={handleComplete}
      onUndo={handleUndo}
      onClear={handleClear}
      onCancel={handleCancel}
      onStartMode={startMode}
      onToggleMapType={() => setMapType((t) => (t === 'roadmap' ? 'satellite' : 'roadmap'))}
      onSearchQueryChange={setSearchQuery}
      onSearch={handleSearch}
      onSearchKeyDown={handleSearchKeyDown}
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
  circleCenter: Vertex | null;
  circleRadiusM: number;
  searchQuery: string;
  searching: boolean;
  searchError: string;
  mapInstanceRef: React.MutableRefObject<google.maps.Map | null>;
  onMapClick: (e: google.maps.MapMouseEvent) => void;
  onMouseMove: (e: google.maps.MapMouseEvent) => void;
  onMouseDown: () => void;
  onMouseUp: () => void;
  onComplete: () => void;
  onUndo: () => void;
  onClear: () => void;
  onCancel: () => void;
  onStartMode: (mode: DrawingMode) => void;
  onToggleMapType: () => void;
  onSearchQueryChange: (q: string) => void;
  onSearch: () => void;
  onSearchKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

function GoogleMapLoaderWrapper({
  GoogleMap, Polygon, Polyline, Circle, useJsApiLoader,
  mode, vertices, completed, mapType, readOnly,
  areaHectares, perimeter, initialCenter, initialZoom, height,
  circleCenter, circleRadiusM,
  searchQuery, searching, searchError,
  mapInstanceRef,
  onMapClick, onMouseMove, onMouseDown, onMouseUp,
  onComplete, onUndo, onClear, onCancel, onStartMode, onToggleMapType,
  onSearchQueryChange, onSearch, onSearchKeyDown,
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

  // Can undo when: in an active mode, not completed, and either have vertices or a circle center
  const canUndo = !completed && (vertices.length > 0 || circleCenter !== null);
  // Can complete polygon when drawing polygon and have ≥ 3 points
  const canComplete = mode === 'polygon' && !completed && vertices.length >= 3;

  const modeLabel =
    mode === 'polygon' ? 'رسم مضلع متعدد النقاط — انقر لإضافة نقاط'
    : mode === 'rectangle' ? vertices.length === 0 ? 'رسم مستطيل — انقر الزاوية الأولى' : 'انقر الزاوية المقابلة'
    : mode === 'circle' ? !circleCenter ? 'رسم دائرة — انقر مركز الدائرة' : `انقر لتحديد نصف القطر (${(circleRadiusM / 1000).toFixed(2)} كم)`
    : mode === 'freehand' ? 'رسم حر — اضغط مع السحب لرسم الحدود'
    : null;

  const borderColor =
    mode === 'polygon' ? 'border-green-500'
    : mode === 'rectangle' ? 'border-blue-500'
    : mode === 'circle' ? 'border-purple-500'
    : mode === 'freehand' ? 'border-orange-500'
    : 'border-gray-200';

  const mapOptions: any = {
    disableDefaultUI: false,
    zoomControl: true,
    streetViewControl: false,
    mapTypeControl: false,
    fullscreenControl: false,
    // Disable drag while freehand drawing so mouse-drag draws, not pans
    draggable: mode !== 'freehand',
    gestureHandling: mode === 'freehand' ? 'none' : 'auto',
  };

  return (
    <div
      className={`relative rounded-lg overflow-hidden border-2 ${borderColor}`}
      dir="rtl"
      style={{ height }}
    >
      {/* ── Location Search Bar ─────────────────────────────────────── */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-1" style={{ maxWidth: 280 }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchQueryChange(e.target.value)}
          onKeyDown={onSearchKeyDown}
          placeholder="ابحث عن موقع..."
          className="flex-1 px-3 py-2 text-sm rounded-md shadow-md border border-gray-300 bg-white/95 backdrop-blur focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 placeholder-gray-400 min-w-0"
          style={{ width: 180 }}
        />
        <button
          type="button"
          onClick={onSearch}
          disabled={searching}
          className="px-2.5 py-2 bg-white/95 backdrop-blur border border-gray-300 rounded-md shadow-md hover:bg-gray-100 transition-colors text-gray-700 disabled:opacity-60"
          title="بحث"
        >
          {searching ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
        </button>
      </div>

      {/* ── Mode Toolbar (top-left) ─────────────────────────────────── */}
      {!readOnly && (
        <div className="absolute top-3 left-3 z-20 flex flex-col gap-2">
          {/* Mode selection — show when idle or when switching */}
          {(!mode || completed) && (
            <div className="flex flex-col gap-1.5">
              {[
                { id: 'polygon' as DrawingMode, icon: <Pentagon size={14} />, label: 'مضلع', color: 'bg-green-600 hover:bg-green-700' },
                { id: 'rectangle' as DrawingMode, icon: <Square size={14} />, label: 'مستطيل', color: 'bg-blue-600 hover:bg-blue-700' },
                { id: 'circle' as DrawingMode, icon: <CircleIcon size={14} />, label: 'دائرة', color: 'bg-purple-600 hover:bg-purple-700' },
                { id: 'freehand' as DrawingMode, icon: <Pen size={14} />, label: 'رسم حر', color: 'bg-orange-500 hover:bg-orange-600' },
              ].map(({ id, icon, label, color }) => (
                <button
                  key={id as string}
                  type="button"
                  onClick={() => onStartMode(id)}
                  className={`px-3 py-2 text-white text-sm font-medium rounded-md shadow-md transition-colors inline-flex items-center gap-1.5 ${color}`}
                >
                  {icon}
                  {label}
                </button>
              ))}
            </div>
          )}

          {/* Active-mode controls */}
          {mode && !completed && (
            <div className="flex flex-col gap-1.5">
              {canComplete && (
                <button
                  type="button"
                  onClick={onComplete}
                  className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-green-700 transition-colors inline-flex items-center gap-1"
                >
                  <Check size={14} />
                  إكمال
                </button>
              )}
              {canUndo && (
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

          {/* Completed state controls */}
          {completed && (
            <div className="flex flex-col gap-1.5">
              <button
                type="button"
                onClick={onClear}
                className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors inline-flex items-center gap-1"
              >
                <Trash2 size={14} />
                مسح وإعادة الرسم
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── Map type toggle (bottom-left corner) ────────────────────── */}
      <div className="absolute bottom-16 left-3 z-20">
        <button
          type="button"
          onClick={onToggleMapType}
          className="px-3 py-2 bg-white/95 backdrop-blur text-gray-700 text-sm font-medium rounded-md shadow-md hover:bg-gray-100 transition-colors inline-flex items-center gap-1.5 border border-gray-300"
        >
          <Map size={14} />
          {mapType === 'satellite' ? 'خريطة الشوارع' : 'صور فضائية'}
        </button>
      </div>

      {/* ── Status bar ──────────────────────────────────────────────── */}
      {!readOnly && modeLabel && !completed && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 bg-white/95 backdrop-blur px-4 py-2 rounded-md shadow-md text-sm font-medium text-gray-700 border border-gray-200 flex flex-col items-center gap-1 pointer-events-none">
          <div>
            {modeLabel}
            {mode === 'polygon' && vertices.length > 0 && (
              <span className="mr-2 text-blue-600">النقاط: {vertices.length}</span>
            )}
            {mode === 'freehand' && vertices.length > 0 && (
              <span className="mr-2 text-orange-600">النقاط: {vertices.length}</span>
            )}
          </div>
          {vertices.length >= 2 && (
            <div className="text-xs text-gray-500">
              المساحة: {areaHectares.toFixed(2)} هكتار | المحيط: {perimeter.toFixed(0)} م
            </div>
          )}
        </div>
      )}

      {/* ── Search error ─────────────────────────────────────────────── */}
      {searchError && (
        <div className="absolute top-12 right-3 z-20 bg-red-100 border border-red-300 text-red-700 text-xs px-3 py-1 rounded-md shadow">
          {searchError}
        </div>
      )}

      {/* ── Completion badge ─────────────────────────────────────────── */}
      {completed && vertices.length >= 3 && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 bg-green-50 border border-green-300 px-4 py-2 rounded-md shadow-md text-sm font-medium text-green-800 flex flex-col items-center gap-1 pointer-events-none">
          <div>تم تحديد المنطقة — النقاط: {vertices.length}</div>
          <div className="text-xs">
            المساحة: {areaHectares.toFixed(2)} هكتار | المحيط: {perimeter.toFixed(0)} م
          </div>
        </div>
      )}

      {/* ── Google Map ───────────────────────────────────────────────── */}
      <GoogleMap
        mapContainerStyle={{ height: '100%', width: '100%' }}
        center={center}
        zoom={initialZoom}
        mapTypeId={mapType}
        onClick={readOnly ? undefined : onMapClick}
        onMouseMove={onMouseMove}
        onMouseDown={onMouseDown}
        onMouseUp={onMouseUp}
        onLoad={(map: google.maps.Map) => { mapInstanceRef.current = map; }}
        options={mapOptions}
      >
        {/* Vertex markers */}
        {vertices.map((v, i) => (
          <Circle
            key={`vertex-${i}`}
            center={{ lat: v.lat, lng: v.lng }}
            radius={mode === 'freehand' ? 8 : 15}
            options={{
              fillColor: i === 0 ? '#16a34a' : '#2563eb',
              fillOpacity: 1,
              strokeColor: '#ffffff',
              strokeWeight: 2,
              clickable: false,
            }}
          />
        ))}

        {/* Circle center marker */}
        {mode === 'circle' && circleCenter && (
          <Circle
            center={{ lat: circleCenter.lat, lng: circleCenter.lng }}
            radius={20}
            options={{
              fillColor: '#9333ea',
              fillOpacity: 1,
              strokeColor: '#ffffff',
              strokeWeight: 2,
              clickable: false,
            }}
          />
        )}

        {/* Circle preview */}
        {mode === 'circle' && circleCenter && circleRadiusM > 0 && (
          <Circle
            center={{ lat: circleCenter.lat, lng: circleCenter.lng }}
            radius={circleRadiusM}
            options={{
              fillColor: '#9333ea',
              fillOpacity: 0.15,
              strokeColor: '#9333ea',
              strokeWeight: 2,
              strokeOpacity: 0.8,
              clickable: false,
            }}
          />
        )}

        {/* Polyline preview while drawing polygon/freehand */}
        {!completed && vertices.length >= 2 && (mode === 'polygon' || mode === 'freehand') && (
          <Polyline
            path={paths}
            options={{
              strokeColor: mode === 'freehand' ? '#f97316' : '#2563eb',
              strokeWeight: 2,
              strokeOpacity: 0.8,
              clickable: false,
            }}
          />
        )}

        {/* Completed or read-only polygon */}
        {(completed || readOnly) && vertices.length >= 3 && (
          <Polygon
            paths={paths}
            options={{
              fillColor: '#3b82f6',
              fillOpacity: 0.2,
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
