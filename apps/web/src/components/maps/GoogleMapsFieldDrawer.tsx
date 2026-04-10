'use client';

/**
 * GoogleMapsFieldDrawer
 *
 * Uses the native Google Maps DrawingManager but replaces its tiny toolbar
 * with a custom large toolbar (≈2× the native size) so it is clearly readable.
 * The DrawingManager still provides all rubber-band preview and shape editing.
 *
 * Custom toolbar is positioned at TOP_CENTER of the map.
 * Native Map/Satellite toggle is at TOP_LEFT.
 * Search box is at TOP_RIGHT.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Trash2, Search, Loader2 } from 'lucide-react';

// ─── Public props ─────────────────────────────────────────────────────────────

export interface GoogleMapsFieldDrawerProps {
  onBoundaryChange?: (geojson: GeoJSON.Polygon | null) => void;
  initialCenter?: [number, number]; // [lat, lng]
  initialZoom?: number;
  height?: string;
  readOnly?: boolean;
  initialPolygon?: GeoJSON.Polygon | null;
}

// Stable reference — avoids @react-google-maps/api "libraries changed" warning
const DRAWING_LIBS: ['drawing'] = ['drawing'];

// Drawing modes (matching google.maps.drawing.OverlayType string values)
type DrawMode = 'polygon' | 'rectangle' | 'circle' | null;

// ─── Geometry helpers ─────────────────────────────────────────────────────────

interface Vertex { lat: number; lng: number; }

function toRad(d: number) { return (d * Math.PI) / 180; }

function haversine(a: Vertex, b: Vertex): number {
  const R = 6_371_000;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function computePerimeter(vs: Vertex[]): number {
  let t = 0;
  for (let i = 0; i < vs.length; i++) t += haversine(vs[i]!, vs[(i + 1) % vs.length]!);
  return t;
}

function computeArea(vs: Vertex[]): number {
  if (vs.length < 3) return 0;
  const avgLat = vs.reduce((s, v) => s + v.lat, 0) / vs.length;
  const cosLat = Math.cos(toRad(avgLat));
  const R = 6_371_000;
  const p = vs.map((v) => ({ x: toRad(v.lng) * cosLat * R, y: toRad(v.lat) * R }));
  let a = 0;
  for (let i = 0; i < p.length; i++) {
    const j = (i + 1) % p.length;
    a += p[i]!.x * p[j]!.y - p[j]!.x * p[i]!.y;
  }
  return Math.abs(a) / 2 / 10_000;
}

function toGeoJSON(vs: Vertex[]): GeoJSON.Polygon {
  const ring = vs.map((v) => [v.lng, v.lat] as [number, number]);
  if (ring[0]) ring.push([...ring[0]]);
  return { type: 'Polygon', coordinates: [ring] };
}

function fromGeoJSON(p: GeoJSON.Polygon): Vertex[] {
  const ring = p.coordinates[0];
  if (!ring || ring.length < 2) return [];
  return ring.slice(0, -1).map(([lng, lat]) => ({ lat: lat!, lng: lng! }));
}

function circlePolygon(c: Vertex, r: number, n = 72): Vertex[] {
  const R = 6_371_000;
  return Array.from({ length: n }, (_, i) => {
    const ang = (2 * Math.PI * i) / n;
    const lat =
      (Math.asin(
        Math.sin(toRad(c.lat)) * Math.cos(r / R) +
          Math.cos(toRad(c.lat)) * Math.sin(r / R) * Math.cos(ang),
      ) * 180) / Math.PI;
    const lng =
      c.lng +
      (Math.atan2(
        Math.sin(ang) * Math.sin(r / R) * Math.cos(toRad(c.lat)),
        Math.cos(r / R) - Math.sin(toRad(c.lat)) * Math.sin(toRad(lat)),
      ) * 180) / Math.PI;
    return { lat, lng };
  });
}

// ─── SVG shape icons (inline – no dependency) ────────────────────────────────

const IconHand = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 11V6a2 2 0 0 0-2-2 2 2 0 0 0-2 2" />
    <path d="M14 10V4a2 2 0 0 0-2-2 2 2 0 0 0-2 2v2" />
    <path d="M10 10.5V6a2 2 0 0 0-2-2 2 2 0 0 0-2 2v8" />
    <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />
  </svg>
);

const IconPolygon = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5" />
    <circle cx="12" cy="2"    r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="22" cy="8.5"  r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="22" cy="15.5" r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="12" cy="22"   r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="2"  cy="15.5" r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="2"  cy="8.5"  r="1.5" fill="currentColor" stroke="none"/>
  </svg>
);

const IconRectangle = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="6" width="18" height="12" rx="1" />
    <circle cx="3"  cy="6"  r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="21" cy="6"  r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="21" cy="18" r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="3"  cy="18" r="1.5" fill="currentColor" stroke="none"/>
  </svg>
);

const IconCircle = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="9" />
    <circle cx="12" cy="3"  r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="21" cy="12" r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="12" cy="21" r="1.5" fill="currentColor" stroke="none"/>
    <circle cx="3"  cy="12" r="1.5" fill="currentColor" stroke="none"/>
  </svg>
);

// ─── Loading skeleton ─────────────────────────────────────────────────────────

const MapSkeleton = ({ height }: { height: string }) => (
  <div
    className="bg-gray-100 animate-pulse flex items-center justify-center rounded-lg"
    style={{ height }}
  >
    <p className="text-gray-500 text-sm">جاري تحميل الخريطة...</p>
  </div>
);

// ─── Custom large toolbar ─────────────────────────────────────────────────────

interface ToolbarProps {
  activeMode: DrawMode;
  onSetMode: (m: DrawMode) => void;
  completed: boolean;
  readOnly: boolean;
}

const TOOLS: { mode: DrawMode; label: string; Icon: React.FC }[] = [
  { mode: null,        label: 'تحريك',   Icon: IconHand },
  { mode: 'polygon',   label: 'مضلع',    Icon: IconPolygon },
  { mode: 'rectangle', label: 'مستطيل',  Icon: IconRectangle },
  { mode: 'circle',    label: 'دائرة',   Icon: IconCircle },
];

function DrawingToolbar({ activeMode, onSetMode, completed, readOnly }: ToolbarProps) {
  if (readOnly || completed) return null;
  return (
    <div
      className="absolute top-3 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1 bg-white rounded-xl shadow-lg border border-gray-200 p-1.5"
      style={{ direction: 'rtl' }}
    >
      {TOOLS.map(({ mode, label, Icon }) => {
        const isActive = activeMode === mode;
        return (
          <button
            key={String(mode)}
            type="button"
            title={label}
            onClick={() => onSetMode(mode)}
            className={`
              flex flex-col items-center justify-center gap-1
              w-16 h-16 rounded-lg text-xs font-medium transition-all select-none
              ${isActive
                ? 'bg-blue-600 text-white shadow-inner'
                : 'text-gray-700 hover:bg-gray-100 hover:text-blue-600'}
            `}
          >
            <Icon />
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}

// ─── Inner component (browser only) ──────────────────────────────────────────

function Inner({
  onBoundaryChange,
  initialCenter = [15.5527, 48.5164],
  initialZoom = 7,
  height = '500px',
  readOnly = false,
  initialPolygon,
}: GoogleMapsFieldDrawerProps) {
  // Dynamically import @react-google-maps/api to avoid SSR issues
  const [lib, setLib] = useState<{
    GoogleMap: React.ComponentType<any>;
    DrawingManager: React.ComponentType<any>;
    useJsApiLoader: (o: any) => { isLoaded: boolean; loadError?: Error };
  } | null>(null);

  useEffect(() => {
    import('@react-google-maps/api').then((m) =>
      setLib({
        GoogleMap: m.GoogleMap,
        DrawingManager: (m as any).DrawingManager,
        useJsApiLoader: m.useJsApiLoader,
      }),
    );
  }, []);

  // ── Shape state ───────────────────────────────────────────────────────────
  const [completed, setCompleted] = useState(!!initialPolygon);
  const [areaHa, setAreaHa]       = useState(0);
  const [periM, setPeriM]         = useState(0);

  // ── Drawing mode (for custom toolbar) ────────────────────────────────────
  const [activeMode, setActiveMode] = useState<DrawMode>(null);
  const dmRef = useRef<any>(null);

  const handleDmLoad = useCallback((dm: any) => { dmRef.current = dm; }, []);

  const handleSetMode = useCallback((mode: DrawMode) => {
    setActiveMode(mode);
    if (dmRef.current) {
      dmRef.current.setDrawingMode(mode);  // null = stop drawing
    }
  }, []);

  // ── Refs ──────────────────────────────────────────────────────────────────
  const mapRef        = useRef<any>(null);
  const shapeRef      = useRef<any>(null);
  const listenersRef  = useRef<any[]>([]);

  // ── Search ────────────────────────────────────────────────────────────────
  const [searchQ,   setSearchQ]   = useState('');
  const [searching, setSearching] = useState(false);
  const [searchErr, setSearchErr] = useState('');

  // ── Emit helper ───────────────────────────────────────────────────────────
  const emit = useCallback(
    (vs: Vertex[]) => {
      setAreaHa(computeArea(vs));
      setPeriM(computePerimeter(vs));
      onBoundaryChange?.(vs.length >= 3 ? toGeoJSON(vs) : null);
    },
    [onBoundaryChange],
  );

  // ── Remove current overlay + listeners ────────────────────────────────────
  const clearOverlay = useCallback(() => {
    listenersRef.current.forEach((l) => {
      try { window.google?.maps.event.removeListener(l); } catch { /* ignore */ }
    });
    listenersRef.current = [];
    if (shapeRef.current) {
      try { shapeRef.current.setMap(null); } catch { /* ignore */ }
      shapeRef.current = null;
    }
  }, []);

  // ── Reset everything ──────────────────────────────────────────────────────
  const handleReset = useCallback(() => {
    clearOverlay();
    setCompleted(false);
    setAreaHa(0);
    setPeriM(0);
    setActiveMode(null);
    onBoundaryChange?.(null);
    // Re-enable drawing toolbar
    if (dmRef.current) dmRef.current.setDrawingMode(null);
  }, [clearOverlay, onBoundaryChange]);

  // ── Polygon complete ──────────────────────────────────────────────────────
  const onPolygonComplete = useCallback(
    (polygon: any) => {
      shapeRef.current = polygon;
      polygon.setEditable(true);
      polygon.setDraggable(true);
      setActiveMode(null);
      setCompleted(true);

      const extract = () => {
        const vs: Vertex[] = polygon.getPath().getArray()
          .map((ll: any) => ({ lat: ll.lat(), lng: ll.lng() }));
        emit(vs);
      };
      extract();

      const path = polygon.getPath();
      listenersRef.current = [
        path.addListener('set_at',    extract),
        path.addListener('insert_at', extract),
        path.addListener('remove_at', extract),
        polygon.addListener('dragend', extract),
      ];
    },
    [emit],
  );

  // ── Rectangle complete ────────────────────────────────────────────────────
  const onRectangleComplete = useCallback(
    (rect: any) => {
      shapeRef.current = rect;
      rect.setEditable(true);
      rect.setDraggable(true);
      setActiveMode(null);
      setCompleted(true);

      const extract = () => {
        const bounds = rect.getBounds();
        const ne = bounds.getNorthEast();
        const sw = bounds.getSouthWest();
        emit([
          { lat: ne.lat(), lng: sw.lng() },
          { lat: ne.lat(), lng: ne.lng() },
          { lat: sw.lat(), lng: ne.lng() },
          { lat: sw.lat(), lng: sw.lng() },
        ]);
      };
      extract();
      listenersRef.current = [rect.addListener('bounds_changed', extract)];
    },
    [emit],
  );

  // ── Circle complete ───────────────────────────────────────────────────────
  const onCircleComplete = useCallback(
    (circle: any) => {
      shapeRef.current = circle;
      circle.setEditable(true);
      circle.setDraggable(true);
      setActiveMode(null);
      setCompleted(true);

      const extract = () => {
        const c = { lat: circle.getCenter().lat(), lng: circle.getCenter().lng() };
        emit(circlePolygon(c, circle.getRadius()));
      };
      extract();
      listenersRef.current = [
        circle.addListener('radius_changed', extract),
        circle.addListener('center_changed', extract),
      ];
    },
    [emit],
  );

  // ── Map load ──────────────────────────────────────────────────────────────
  const onMapLoad = useCallback(
    (map: any) => {
      map.setCenter({ lat: initialCenter[0], lng: initialCenter[1] });
      map.setZoom(initialZoom);
      mapRef.current = map;

      if (initialPolygon && !shapeRef.current) {
        const vs = fromGeoJSON(initialPolygon);
        const polygon = new window.google.maps.Polygon({
          paths: vs.map((v) => ({ lat: v.lat, lng: v.lng })),
          map,
          editable: !readOnly,
          draggable: !readOnly,
          fillColor: '#3b82f6',
          fillOpacity: 0.22,
          strokeColor: '#1d4ed8',
          strokeWeight: 5,
          strokeOpacity: 1,
        });
        shapeRef.current = polygon;
        emit(vs);

        if (!readOnly) {
          const ex = () => {
            const v: Vertex[] = polygon.getPath().getArray()
              .map((ll: any) => ({ lat: ll.lat(), lng: ll.lng() }));
            emit(v);
          };
          const path = polygon.getPath();
          listenersRef.current = [
            path.addListener('set_at',    ex),
            path.addListener('insert_at', ex),
            path.addListener('remove_at', ex),
            polygon.addListener('dragend', ex),
          ];
        }
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [initialCenter, initialZoom, initialPolygon, readOnly],
  );

  // ── Search ────────────────────────────────────────────────────────────────
  const doSearch = useCallback(async () => {
    const q = searchQ.trim();
    if (!q || !window.google) return;
    setSearching(true);
    setSearchErr('');
    try {
      const gc = new window.google.maps.Geocoder();
      const res = await gc.geocode({ address: q });
      if (res.results[0]) {
        const loc = res.results[0].geometry.location;
        mapRef.current?.panTo({ lat: loc.lat(), lng: loc.lng() });
        mapRef.current?.setZoom(14);
      } else {
        setSearchErr('لم يتم العثور على الموقع');
      }
    } catch {
      setSearchErr('خطأ في البحث');
    } finally {
      setSearching(false);
    }
  }, [searchQ]);

  if (!lib) return <MapSkeleton height={height} />;

  return (
    <Loader
      lib={lib}
      completed={completed}
      areaHa={areaHa}
      periM={periM}
      readOnly={readOnly}
      height={height}
      activeMode={activeMode}
      onSetMode={handleSetMode}
      searchQ={searchQ}
      searching={searching}
      searchErr={searchErr}
      onMapLoad={onMapLoad}
      onDmLoad={handleDmLoad}
      onPolygonComplete={onPolygonComplete}
      onRectangleComplete={onRectangleComplete}
      onCircleComplete={onCircleComplete}
      onReset={handleReset}
      onSearchChange={setSearchQ}
      onSearch={doSearch}
      onSearchKey={(e) => { if (e.key === 'Enter') { e.preventDefault(); doSearch(); } }}
    />
  );
}

// ─── Loader wrapper ───────────────────────────────────────────────────────────

interface LoaderProps {
  lib: {
    GoogleMap: React.ComponentType<any>;
    DrawingManager: React.ComponentType<any>;
    useJsApiLoader: (o: any) => { isLoaded: boolean; loadError?: Error };
  };
  completed: boolean;
  areaHa: number;
  periM: number;
  readOnly: boolean;
  height: string;
  activeMode: DrawMode;
  onSetMode: (m: DrawMode) => void;
  searchQ: string;
  searching: boolean;
  searchErr: string;
  onMapLoad: (m: any) => void;
  onDmLoad: (dm: any) => void;
  onPolygonComplete: (p: any) => void;
  onRectangleComplete: (r: any) => void;
  onCircleComplete: (c: any) => void;
  onReset: () => void;
  onSearchChange: (v: string) => void;
  onSearch: () => void;
  onSearchKey: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

function Loader({
  lib,
  completed, areaHa, periM,
  readOnly, height,
  activeMode, onSetMode,
  searchQ, searching, searchErr,
  onMapLoad, onDmLoad,
  onPolygonComplete, onRectangleComplete, onCircleComplete,
  onReset,
  onSearchChange, onSearch, onSearchKey,
}: LoaderProps) {
  const { isLoaded, loadError } = lib.useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '',
    libraries: DRAWING_LIBS,
  });

  if (loadError) {
    return (
      <div
        className="bg-red-50 border border-red-200 flex flex-col items-center justify-center gap-2 rounded-lg"
        style={{ height }}
      >
        <p className="text-red-600 text-sm font-medium">فشل تحميل خرائط جوجل</p>
        <p className="text-red-400 text-xs">تحقق من مفتاح API والاتصال بالإنترنت</p>
      </div>
    );
  }

  if (!isLoaded) return <MapSkeleton height={height} />;

  const { GoogleMap, DrawingManager } = lib;

  // DrawingManager options — toolbar hidden (we use our custom one above)
  const dmOptions: any = {
    drawingControl: false,   // ← hide native tiny toolbar
    drawingMode: activeMode, // controlled externally
    polygonOptions: {
      fillColor: '#3b82f6',
      fillOpacity: 0.22,
      strokeColor: '#1d4ed8',
      strokeWeight: 5,
      strokeOpacity: 1,
      clickable: true,
      editable: true,
      draggable: true,
      zIndex: 1,
    },
    rectangleOptions: {
      fillColor: '#3b82f6',
      fillOpacity: 0.15,
      strokeColor: '#1d4ed8',
      strokeWeight: 5,
      strokeOpacity: 1,
      clickable: true,
      editable: true,
      draggable: true,
      zIndex: 1,
    },
    circleOptions: {
      fillColor: '#3b82f6',
      fillOpacity: 0.15,
      strokeColor: '#1d4ed8',
      strokeWeight: 5,
      strokeOpacity: 1,
      clickable: true,
      editable: true,
      draggable: true,
      zIndex: 1,
    },
  };

  const mapOptions: any = {
    mapTypeControl: true,
    mapTypeControlOptions: {
      position: window.google.maps.ControlPosition.TOP_LEFT,
      style: window.google.maps.MapTypeControlStyle.DEFAULT,
    },
    zoomControl: true,
    zoomControlOptions: {
      position: window.google.maps.ControlPosition.RIGHT_CENTER,
    },
    streetViewControl: false,
    fullscreenControl: true,
    fullscreenControlOptions: {
      position: window.google.maps.ControlPosition.RIGHT_TOP,
    },
    rotateControl: false,
    mapTypeId: 'satellite',
  };

  return (
    <div className="relative rounded-lg overflow-hidden shadow-sm" style={{ height }}>

      {/* ── Custom drawing toolbar (2× native size, centered) ────────── */}
      <DrawingToolbar
        activeMode={activeMode}
        onSetMode={onSetMode}
        completed={completed}
        readOnly={readOnly}
      />

      {/* ── Search box (top-right) ───────────────────────────────────── */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-1" dir="rtl">
        <input
          type="text"
          value={searchQ}
          onChange={(e) => onSearchChange(e.target.value)}
          onKeyDown={onSearchKey}
          placeholder="ابحث عن موقع..."
          style={{ width: 175 }}
          className="px-3 py-1.5 text-sm rounded-md shadow border border-gray-300 bg-white/95 backdrop-blur focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
        />
        <button
          type="button"
          onClick={onSearch}
          disabled={searching}
          className="px-2 py-1.5 bg-white/95 border border-gray-300 rounded-md shadow hover:bg-gray-100 text-gray-700 disabled:opacity-60"
        >
          {searching
            ? <Loader2 size={13} className="animate-spin" />
            : <Search size={13} />}
        </button>
      </div>

      {searchErr && (
        <div className="absolute top-12 right-3 z-20 bg-red-100 border border-red-300 text-red-700 text-xs px-3 py-1 rounded shadow">
          {searchErr}
        </div>
      )}

      {/* ── Clear button — appears after shape is drawn ──────────────── */}
      {!readOnly && completed && (
        <button
          type="button"
          onClick={onReset}
          className="absolute top-3 left-1/2 -translate-x-1/2 z-20 inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-300 rounded-xl shadow-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
        >
          <Trash2 size={15} />
          مسح وإعادة الرسم
        </button>
      )}

      {/* ── Area / perimeter info — bottom-centre ───────────────────── */}
      {completed && areaHa > 0 && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 bg-white/95 border border-gray-300 rounded-md shadow px-4 py-2 text-xs font-medium text-gray-700 pointer-events-none whitespace-nowrap flex items-center gap-4">
          <span className="text-green-600 font-semibold">✓ تم تحديد الحدود</span>
          <span>المساحة: <strong>{areaHa.toFixed(2)}</strong> هكتار</span>
          <span>المحيط: <strong>{periM.toFixed(0)}</strong> م</span>
        </div>
      )}

      {/* ── Google Map ────────────────────────────────────────────────── */}
      <GoogleMap
        mapContainerStyle={{ width: '100%', height: '100%' }}
        onLoad={onMapLoad}
        options={mapOptions}
      >
        {!readOnly && (
          <DrawingManager
            options={dmOptions}
            onLoad={onDmLoad}
            onPolygonComplete={onPolygonComplete}
            onRectangleComplete={onRectangleComplete}
            onCircleComplete={onCircleComplete}
          />
        )}
      </GoogleMap>
    </div>
  );
}

// ─── SSR-safe export ──────────────────────────────────────────────────────────

export default dynamic(() => Promise.resolve(Inner), {
  ssr: false,
  loading: () => <MapSkeleton height="500px" />,
});
