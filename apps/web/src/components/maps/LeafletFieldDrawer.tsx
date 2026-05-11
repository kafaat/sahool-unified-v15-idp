'use client';

/**
 * LeafletFieldDrawer — redesigned interaction model
 *
 * Polygon  : click = add vertex; click first vertex (≥3 pts) = close
 * Circle   : click 1 = center; mousemove = radius grows; click 2 = done
 * Rectangle: click 1 = corner; mousemove = preview; click 2 = done
 * Resize   : polygon/rect = drag corner handles; circle = drag edge handle
 */

import { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import type * as L from 'leaflet';
import { Trash2, Search, Loader2 } from 'lucide-react';

// ─── Public props ─────────────────────────────────────────────────────────────

export interface GoogleMapsFieldDrawerProps {
  onBoundaryChange?: (geojson: GeoJSON.Polygon | null) => void;
  initialCenter?: [number, number];
  initialZoom?: number;
  height?: string;
  readOnly?: boolean;
  initialPolygon?: GeoJSON.Polygon | null;
  /** External flyTo target — when set the map animates to these coords. */
  externalFlyTo?: [number, number] | null;
  externalFlyZoom?: number;
  onZoomChange?: (zoom: number) => void;
}

// ─── Types ────────────────────────────────────────────────────────────────────

type DrawMode = 'polygon' | 'rectangle' | 'circle' | null;
type DrawPhase = 'idle' | 'first'; // first = first anchor placed

interface Vertex { lat: number; lng: number; }
interface CircleShape { center: Vertex; radius: number; }

// ─── Geometry helpers ─────────────────────────────────────────────────────────

function toRad(d: number) { return (d * Math.PI) / 180; }

function haversine(a: Vertex, b: Vertex): number {
  const R = 6_371_000;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const h = Math.sin(dLat / 2) ** 2 +
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

/** East-edge point of a circle — used for the resize drag handle. */
function circleEastEdge(center: Vertex, radius: number): Vertex {
  const R = 6_371_000;
  const lng = center.lng + (radius / (R * Math.cos(toRad(center.lat)))) * (180 / Math.PI);
  return { lat: center.lat, lng };
}

/** Rectangle vertices from two opposite corners. */
function rectFromCorners(a: Vertex, b: Vertex): Vertex[] {
  return [
    { lat: a.lat, lng: a.lng },
    { lat: a.lat, lng: b.lng },
    { lat: b.lat, lng: b.lng },
    { lat: b.lat, lng: a.lng },
  ];
}

/** Pixel distance from mouse to a lat/lng point on the map. */
function pixelDist(map: L.Map, mouseLatLng: L.LatLng, v: Vertex): number {
  try {
    const mp = map.latLngToContainerPoint(mouseLatLng);
    const vp = map.latLngToContainerPoint([v.lat, v.lng] as any);
    return Math.sqrt((mp.x - vp.x) ** 2 + (mp.y - vp.y) ** 2);
  } catch {
    return Infinity;
  }
}

// ─── SVG icons ────────────────────────────────────────────────────────────────

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
    <circle cx="12" cy="2"    r="1.5" fill="currentColor" stroke="none" />
    <circle cx="22" cy="8.5"  r="1.5" fill="currentColor" stroke="none" />
    <circle cx="22" cy="15.5" r="1.5" fill="currentColor" stroke="none" />
    <circle cx="12" cy="22"   r="1.5" fill="currentColor" stroke="none" />
    <circle cx="2"  cy="15.5" r="1.5" fill="currentColor" stroke="none" />
    <circle cx="2"  cy="8.5"  r="1.5" fill="currentColor" stroke="none" />
  </svg>
);

const IconRectangle = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="6" width="18" height="12" rx="1" />
    <circle cx="3"  cy="6"  r="1.5" fill="currentColor" stroke="none" />
    <circle cx="21" cy="6"  r="1.5" fill="currentColor" stroke="none" />
    <circle cx="21" cy="18" r="1.5" fill="currentColor" stroke="none" />
    <circle cx="3"  cy="18" r="1.5" fill="currentColor" stroke="none" />
  </svg>
);

const IconCircle = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="9" />
    <circle cx="12" cy="3"  r="1.5" fill="currentColor" stroke="none" />
    <circle cx="21" cy="12" r="1.5" fill="currentColor" stroke="none" />
    <circle cx="12" cy="21" r="1.5" fill="currentColor" stroke="none" />
    <circle cx="3"  cy="12" r="1.5" fill="currentColor" stroke="none" />
  </svg>
);

// ─── Skeleton ─────────────────────────────────────────────────────────────────

const MapSkeleton = ({ height }: { height: string }) => (
  <div className="bg-gray-100 animate-pulse flex items-center justify-center rounded-lg" style={{ height }}>
    <p className="text-gray-500 text-sm">جاري تحميل الخريطة...</p>
  </div>
);

// ─── Toolbar ──────────────────────────────────────────────────────────────────

const TOOLS: { mode: DrawMode; label: string; Icon: React.FC }[] = [
  { mode: null,        label: 'تحريك',  Icon: IconHand },
  { mode: 'polygon',   label: 'مضلع',   Icon: IconPolygon },
  { mode: 'rectangle', label: 'مستطيل', Icon: IconRectangle },
  { mode: 'circle',    label: 'دائرة',  Icon: IconCircle },
];

function DrawingToolbar({
  activeMode, onSetMode, completed, readOnly, onReset,
}: {
  activeMode: DrawMode; onSetMode: (m: DrawMode) => void;
  completed: boolean; readOnly: boolean; onReset: () => void;
}) {
  return (
    <div
      className="absolute top-3 left-1/2 -translate-x-1/2 z-[1000] flex items-center gap-1 bg-white rounded-xl shadow-lg border border-gray-200 p-1.5"
      style={{ direction: 'rtl' }}
    >
      {!completed && !readOnly && TOOLS.map(({ mode, label, Icon }) => {
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
      {completed && !readOnly && (
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <Trash2 size={15} />
          مسح وإعادة الرسم
        </button>
      )}
    </div>
  );
}

// ─── Leaflet icon factories ───────────────────────────────────────────────────

function makeIcon(L: typeof import('leaflet'), color: string, size: number, extra = '') {
  return L.divIcon({
    className: '',
    html: `<div style="width:${size}px;height:${size}px;background:${color};border:2px solid #fff;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,.3);${extra}"></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

// ─── Dynamic react-leaflet imports ────────────────────────────────────────────

const dynamicLeaflet = (loader: () => Promise<unknown>) =>
  dynamic(loader as any, { ssr: false }) as any;

const MapContainer = dynamicLeaflet(() => import('react-leaflet').then((m) => m.MapContainer));
const TileLayer    = dynamicLeaflet(() => import('react-leaflet').then((m) => m.TileLayer));
const Polyline     = dynamicLeaflet(() => import('react-leaflet').then((m) => m.Polyline));
const Polygon      = dynamicLeaflet(() => import('react-leaflet').then((m) => m.Polygon));
const Marker       = dynamicLeaflet(() => import('react-leaflet').then((m) => m.Marker));
const Circle       = dynamicLeaflet(() => import('react-leaflet').then((m) => m.Circle));

// ─── EventLayer ───────────────────────────────────────────────────────────────

interface EventLayerProps {
  mode: DrawMode;
  /** Whether the map should pan (disabled for rect/circle drawing). */
  disablePan: boolean;
  firstVertex: Vertex | null;
  vertexCount: number;
  onMapClick: (v: Vertex, nearFirst: boolean) => void;
  onMouseMove: (v: Vertex, nearFirst: boolean) => void;
}

function EventLayer(props: EventLayerProps) {
  const [hook, setHook] = useState<((h: any) => L.Map) | null>(null);
  useEffect(() => {
    import('react-leaflet').then((m) => setHook(() => m.useMapEvents));
  }, []);
  if (!hook) return null;
  return <EventLayerInner {...props} useMapEvents={hook} />;
}

function EventLayerInner({
  mode, disablePan, firstVertex, vertexCount,
  onMapClick, onMouseMove, useMapEvents,
}: EventLayerProps & { useMapEvents: (h: any) => L.Map }) {
  // Keep latest callbacks in refs so the useMapEvents handler never goes stale
  const clickRef = useRef(onMapClick);
  const moveRef  = useRef(onMouseMove);
  useEffect(() => { clickRef.current = onMapClick; }, [onMapClick]);
  useEffect(() => { moveRef.current  = onMouseMove; }, [onMouseMove]);

  const firstVertexRef = useRef(firstVertex);
  const vertexCountRef = useRef(vertexCount);
  useEffect(() => { firstVertexRef.current = firstVertex; }, [firstVertex]);
  useEffect(() => { vertexCountRef.current = vertexCount; }, [vertexCount]);

  const map = useMapEvents({
    click(e: L.LeafletMouseEvent) {
      if (!mode) return;
      const v = { lat: e.latlng.lat, lng: e.latlng.lng };
      const near = firstVertexRef.current !== null && vertexCountRef.current >= 3
        ? pixelDist(map, e.latlng, firstVertexRef.current) < 15
        : false;
      clickRef.current(v, near);
    },
    mousemove(e: L.LeafletMouseEvent) {
      const v = { lat: e.latlng.lat, lng: e.latlng.lng };
      const near = firstVertexRef.current !== null && vertexCountRef.current >= 3
        ? pixelDist(map, e.latlng, firstVertexRef.current) < 15
        : false;
      moveRef.current(v, near);
    },
  });

  // Always disable double-click zoom during drawing
  useEffect(() => {
    if (mode) {
      map.doubleClickZoom.disable();
    } else {
      map.doubleClickZoom.enable();
    }
  }, [mode, map]);

  // Disable panning for rect/circle so drag draws the shape
  useEffect(() => {
    if (disablePan) {
      map.dragging.disable();
    } else {
      map.dragging.enable();
    }
    return () => { map.dragging.enable(); };
  }, [disablePan, map]);

  // Cursor
  useEffect(() => {
    const c = map.getContainer();
    c.style.cursor = mode ? 'crosshair' : '';
    return () => { c.style.cursor = ''; };
  }, [mode, map]);

  return null;
}

// ─── MapFlyTo ─────────────────────────────────────────────────────────────────

function MapFlyTo({ target, zoom }: { target: [number, number] | null; zoom: number }) {
  const [hook, setHook] = useState<(() => L.Map) | null>(null);
  useEffect(() => { import('react-leaflet').then((m) => setHook(() => m.useMap)); }, []);
  if (!hook || !target) return null;
  return <MapFlyToInner target={target} zoom={zoom} useMap={hook} />;
}

function MapFlyToInner({ target, zoom, useMap }: { target: [number, number]; zoom: number; useMap: () => L.Map }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(target, zoom, { duration: 1 });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target[0], target[1], zoom]);
  return null;
}

// ─── MapZoomTracker ───────────────────────────────────────────────────────────

function MapZoomTracker({ onZoomChange }: { onZoomChange?: (zoom: number) => void }) {
  const [hook, setHook] = useState<(() => L.Map) | null>(null);
  useEffect(() => { import('react-leaflet').then((m) => setHook(() => m.useMap)); }, []);
  if (!hook || !onZoomChange) return null;
  return <MapZoomTrackerInner onZoomChange={onZoomChange} useMap={hook} />;
}

function MapZoomTrackerInner({ onZoomChange, useMap }: { onZoomChange: (zoom: number) => void; useMap: () => L.Map }) {
  const map = useMap();
  useEffect(() => {
    // Fire immediately so the parent gets the actual initial zoom, not the state default.
    onZoomChange(map.getZoom());
    const handler = () => onZoomChange(map.getZoom());
    map.on('zoomend', handler);
    return () => { map.off('zoomend', handler); };
  }, [map, onZoomChange]);
  return null;
}

// ─── Inner component ──────────────────────────────────────────────────────────

function Inner({
  onBoundaryChange,
  initialCenter = [15.5527, 48.5164],
  initialZoom = 7,
  height = '500px',
  readOnly = false,
  initialPolygon,
  externalFlyTo,
  externalFlyZoom = 11,
  onZoomChange,
}: GoogleMapsFieldDrawerProps) {
  const [leafletLib, setLeafletLib] = useState<typeof import('leaflet') | null>(null);
  useEffect(() => { import('leaflet').then((L) => setLeafletLib(L)); }, []);

  // ── Core drawing state ────────────────────────────────────────────────────
  const [activeMode, setActiveMode] = useState<DrawMode>(null);
  const [drawPhase, setDrawPhase]   = useState<DrawPhase>('idle');
  const [vertices, setVertices]     = useState<Vertex[]>(() =>
    initialPolygon ? fromGeoJSON(initialPolygon) : [],
  );
  const [completed, setCompleted] = useState(!!initialPolygon);
  const [nearFirst, setNearFirst] = useState(false);

  // Live mouse position (for preview line / hint)
  const [mousePos, setMousePos] = useState<Vertex | null>(null);

  // Anchors stored in refs (don't need to trigger re-renders themselves)
  const circleAnchorRef = useRef<Vertex | null>(null);
  const rectAnchorRef   = useRef<Vertex | null>(null);

  // Circle preview radius (state so it re-renders on mousemove)
  const [circlePreviewRadius, setCirclePreviewRadius] = useState(0);

  // Completed circle: center + radius kept separately for resize
  const [completedCircle, setCompletedCircle] = useState<CircleShape | null>(null);

  // ── Measurements ──────────────────────────────────────────────────────────
  const areaHa = useMemo(() => computeArea(vertices), [vertices]);
  const periM  = useMemo(() => computePerimeter(vertices), [vertices]);

  // ── Search ────────────────────────────────────────────────────────────────
  const [searchQ,   setSearchQ]   = useState('');
  const [searching, setSearching] = useState(false);
  const [searchErr, setSearchErr] = useState('');
  const [flyTarget, setFlyTarget] = useState<[number, number] | null>(null);
  const [flyZoom,   setFlyZoom]   = useState(14);

  // When the parent passes a new externalFlyTo, forward it to the map
  useEffect(() => {
    if (externalFlyTo) {
      setFlyTarget(externalFlyTo);
      setFlyZoom(externalFlyZoom);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [externalFlyTo?.[0], externalFlyTo?.[1], externalFlyZoom]);

  // ── Emit ──────────────────────────────────────────────────────────────────
  const emit = useCallback((vs: Vertex[]) => {
    onBoundaryChange?.(vs.length >= 3 ? toGeoJSON(vs) : null);
  }, [onBoundaryChange]);

  // ── Full reset ────────────────────────────────────────────────────────────
  const handleReset = useCallback(() => {
    setActiveMode(null);
    setDrawPhase('idle');
    setVertices([]);
    setCompleted(false);
    setNearFirst(false);
    setMousePos(null);
    setCirclePreviewRadius(0);
    setCompletedCircle(null);
    circleAnchorRef.current = null;
    rectAnchorRef.current   = null;
    onBoundaryChange?.(null);
  }, [onBoundaryChange]);

  // ── Mode switch ───────────────────────────────────────────────────────────
  const handleSetMode = useCallback((mode: DrawMode) => {
    setActiveMode(mode);
    setDrawPhase('idle');
    setVertices([]);
    setCompleted(false);
    setNearFirst(false);
    setMousePos(null);
    setCirclePreviewRadius(0);
    setCompletedCircle(null);
    circleAnchorRef.current = null;
    rectAnchorRef.current   = null;
    if (!mode) onBoundaryChange?.(null);
  }, [onBoundaryChange]);

  // ── Mouse move ────────────────────────────────────────────────────────────
  const handleMouseMove = useCallback((v: Vertex, isNearFirst: boolean) => {
    setMousePos(v);
    setNearFirst(isNearFirst);

    if (drawPhase !== 'first') return;

    if (activeMode === 'circle' && circleAnchorRef.current) {
      const r = haversine(circleAnchorRef.current, v);
      setCirclePreviewRadius(r);
    }

    if (activeMode === 'rectangle' && rectAnchorRef.current) {
      setVertices(rectFromCorners(rectAnchorRef.current, v));
    }
  }, [activeMode, drawPhase]);

  // ── Map click ─────────────────────────────────────────────────────────────
  const handleMapClick = useCallback((v: Vertex, isNearFirst: boolean) => {
    if (completed) return;

    // ── Polygon ──────────────────────────────────────────────────────────
    if (activeMode === 'polygon') {
      if (isNearFirst && vertices.length >= 3) {
        // Close the polygon by clicking the first vertex
        setCompleted(true);
        setActiveMode(null);
        setDrawPhase('idle');
        setMousePos(null);
        setNearFirst(false);
        emit(vertices);
        return;
      }
      setVertices((prev) => [...prev, v]);
      setDrawPhase('first');
      return;
    }

    // ── Circle ────────────────────────────────────────────────────────────
    if (activeMode === 'circle') {
      if (drawPhase === 'idle') {
        circleAnchorRef.current = v;
        setDrawPhase('first');
        setCirclePreviewRadius(0);
        return;
      }
      if (drawPhase === 'first' && circleAnchorRef.current) {
        const radius = haversine(circleAnchorRef.current, v);
        if (radius < 1) return; // ignore tap-in-place
        const center = circleAnchorRef.current;
        const finalVerts = circlePolygon(center, radius);
        circleAnchorRef.current = null;
        setCompletedCircle({ center, radius });
        setVertices(finalVerts);
        setCompleted(true);
        setActiveMode(null);
        setDrawPhase('idle');
        setMousePos(null);
        setCirclePreviewRadius(0);
        emit(finalVerts);
      }
      return;
    }

    // ── Rectangle ─────────────────────────────────────────────────────────
    if (activeMode === 'rectangle') {
      if (drawPhase === 'idle') {
        rectAnchorRef.current = v;
        setDrawPhase('first');
        setVertices([v]);
        return;
      }
      if (drawPhase === 'first' && rectAnchorRef.current) {
        const finalVerts = rectFromCorners(rectAnchorRef.current, v);
        rectAnchorRef.current = null;
        setVertices(finalVerts);
        setCompleted(true);
        setActiveMode(null);
        setDrawPhase('idle');
        setMousePos(null);
        emit(finalVerts);
      }
      return;
    }
  }, [activeMode, completed, drawPhase, vertices, emit]);

  // ── Polygon / rectangle: drag corner to resize ────────────────────────────
  const handleVertexDrag = useCallback((idx: number, pos: Vertex) => {
    setVertices((prev) => {
      const next = prev.map((v, i) => (i === idx ? pos : v));
      emit(next);
      return next;
    });
  }, [emit]);

  const handleVertexDblClick = useCallback((idx: number) => {
    setVertices((prev) => {
      if (prev.length <= 3) return prev;
      const next = prev.filter((_, i) => i !== idx);
      emit(next);
      return next;
    });
  }, [emit]);

  // ── Circle: drag east-edge handle to resize ───────────────────────────────
  const handleCircleEdgeDrag = useCallback((edgePos: Vertex) => {
    setCompletedCircle((prev) => {
      if (!prev) return null;
      const newRadius = haversine(prev.center, edgePos);
      if (newRadius < 1) return prev;
      const newVerts = circlePolygon(prev.center, newRadius);
      setVertices(newVerts);
      emit(newVerts);
      return { center: prev.center, radius: newRadius };
    });
  }, [emit]);

  // ── Search ────────────────────────────────────────────────────────────────
  const doSearch = useCallback(async () => {
    const q = searchQ.trim();
    if (!q) return;
    setSearching(true);
    setSearchErr('');
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1`,
        { headers: { 'Accept-Language': 'ar,en' } },
      );
      const data = await res.json();
      if (data[0]) {
        setFlyTarget([parseFloat(data[0].lat), parseFloat(data[0].lon)]);
        setFlyZoom(14);
      } else {
        setSearchErr('لم يتم العثور على الموقع');
      }
    } catch {
      setSearchErr('خطأ في البحث');
    } finally {
      setSearching(false);
    }
  }, [searchQ]);

  // ── Derived ───────────────────────────────────────────────────────────────
  const polyPositions = useMemo(
    () => vertices.map((v) => [v.lat, v.lng] as [number, number]),
    [vertices],
  );

  // Preview line: last placed vertex → mouse cursor (polygon only)
  const previewLine = useMemo(() => {
    if (activeMode !== 'polygon' || !mousePos || vertices.length === 0) return null;
    const last = vertices[vertices.length - 1]!;
    return [
      [last.lat, last.lng] as [number, number],
      [mousePos.lat, mousePos.lng] as [number, number],
    ];
  }, [activeMode, mousePos, vertices]);

  const disablePan = !!(activeMode === 'rectangle' || activeMode === 'circle');

  if (!leafletLib) return <MapSkeleton height={height} />;

  const blueIcon    = makeIcon(leafletLib, '#2563eb', 12, 'cursor:move;');
  const greenIcon   = makeIcon(leafletLib, '#16a34a', 16,
    nearFirst
      ? 'cursor:pointer;border:3px solid #fff;box-shadow:0 0 0 4px rgba(22,163,74,.35),0 1px 4px rgba(0,0,0,.3);'
      : 'cursor:pointer;border:3px solid #fff;',
  );
  const orangeIcon  = makeIcon(leafletLib, '#f59e0b', 14, 'cursor:ew-resize;');
  const centerIcon  = makeIcon(leafletLib, '#16a34a', 10);

  return (
    <div className="relative rounded-lg overflow-hidden shadow-sm" style={{ height, position: 'relative' }}>

      {/* ── Toolbar ────────────────────────────────────────────────────────── */}
      <DrawingToolbar
        activeMode={activeMode}
        onSetMode={handleSetMode}
        completed={completed}
        readOnly={readOnly}
        onReset={handleReset}
      />

      {/* ── Search ─────────────────────────────────────────────────────────── */}
      <div className="absolute top-3 right-3 z-[1000] flex items-center gap-1" dir="rtl">
        <input
          type="text"
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); doSearch(); } }}
          placeholder="ابحث عن موقع..."
          style={{ width: 175 }}
          className="px-3 py-1.5 text-sm rounded-md shadow border border-gray-300 bg-white/95 backdrop-blur focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
        />
        <button
          type="button"
          onClick={doSearch}
          disabled={searching}
          className="px-2 py-1.5 bg-white/95 border border-gray-300 rounded-md shadow hover:bg-gray-100 text-gray-700 disabled:opacity-60"
        >
          {searching ? <Loader2 size={13} className="animate-spin" /> : <Search size={13} />}
        </button>
      </div>

      {searchErr && (
        <div className="absolute top-12 right-3 z-[1000] bg-red-100 border border-red-300 text-red-700 text-xs px-3 py-1 rounded shadow">
          {searchErr}
        </div>
      )}

      {/* ── "Click to close" hint ──────────────────────────────────────────── */}
      {activeMode === 'polygon' && nearFirst && vertices.length >= 3 && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1000] bg-green-600 text-white text-xs px-3 py-1.5 rounded-full shadow pointer-events-none whitespace-nowrap">
          انقر لإغلاق الشكل
        </div>
      )}

      {/* ── "Click to set center" hint ─────────────────────────────────────── */}
      {activeMode === 'circle' && drawPhase === 'idle' && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1000] bg-blue-600 text-white text-xs px-3 py-1.5 rounded-full shadow pointer-events-none whitespace-nowrap">
          انقر لتحديد مركز الدائرة
        </div>
      )}

      {/* ── "Click to finalize" hint ───────────────────────────────────────── */}
      {activeMode === 'circle' && drawPhase === 'first' && circlePreviewRadius > 1 && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1000] bg-blue-600 text-white text-xs px-3 py-1.5 rounded-full shadow pointer-events-none whitespace-nowrap">
          انقر لتأكيد الدائرة
        </div>
      )}

      {activeMode === 'rectangle' && drawPhase === 'idle' && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1000] bg-blue-600 text-white text-xs px-3 py-1.5 rounded-full shadow pointer-events-none whitespace-nowrap">
          انقر لتحديد الزاوية الأولى
        </div>
      )}

      {activeMode === 'rectangle' && drawPhase === 'first' && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[1000] bg-blue-600 text-white text-xs px-3 py-1.5 rounded-full shadow pointer-events-none whitespace-nowrap">
          انقر لتأكيد المستطيل
        </div>
      )}

      {/* ── Info bar ───────────────────────────────────────────────────────── */}
      {completed && areaHa > 0 && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-[1000] bg-white/95 border border-gray-300 rounded-md shadow px-4 py-2 text-xs font-medium text-gray-700 pointer-events-none whitespace-nowrap flex items-center gap-4">
          <span className="text-green-600 font-semibold">✓ تم تحديد الحدود</span>
          <span>المساحة: <strong>{areaHa.toFixed(2)}</strong> هكتار</span>
          <span>المحيط: <strong>{periM.toFixed(0)}</strong> م</span>
        </div>
      )}

      {/* ── Map ────────────────────────────────────────────────────────────── */}
      <MapContainer
        key={`${initialCenter[0]},${initialCenter[1]}`}
        center={initialCenter}
        zoom={initialZoom}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
        doubleClickZoom={false}
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri &mdash; Source: Esri, USGS, AeroGRID, IGN"
          maxNativeZoom={19}
          maxZoom={21}
        />

        <MapFlyTo target={flyTarget} zoom={flyZoom} />
        <MapZoomTracker onZoomChange={onZoomChange} />

        {!readOnly && (
          <EventLayer
            mode={activeMode}
            disablePan={disablePan}
            firstVertex={vertices[0] ?? null}
            vertexCount={vertices.length}
            onMapClick={handleMapClick}
            onMouseMove={handleMouseMove}
          />
        )}

        {/* ── Polygon: placed vertices outline ─────────────────────────── */}
        {activeMode === 'polygon' && vertices.length >= 2 && (
          <Polyline
            positions={polyPositions}
            pathOptions={{ color: '#2563eb', weight: 2 }}
          />
        )}

        {/* ── Polygon: dashed preview line to cursor ────────────────────── */}
        {previewLine && (
          <Polyline
            positions={previewLine}
            pathOptions={{ color: '#2563eb', weight: 2, dashArray: '6 4' }}
          />
        )}

        {/* ── Circle: live preview while drawing ───────────────────────── */}
        {activeMode === 'circle' && drawPhase === 'first' && circleAnchorRef.current && circlePreviewRadius > 0 && (
          <Circle
            center={[circleAnchorRef.current.lat, circleAnchorRef.current.lng]}
            radius={circlePreviewRadius}
            pathOptions={{ color: '#2563eb', weight: 2, dashArray: '6 4', fillColor: '#3b82f6', fillOpacity: 0.15 }}
          />
        )}

        {/* ── Rectangle: live preview while drawing ────────────────────── */}
        {activeMode === 'rectangle' && drawPhase === 'first' && vertices.length === 4 && (
          <Polyline
            positions={[...polyPositions, polyPositions[0]]}
            pathOptions={{ color: '#2563eb', weight: 2, dashArray: '6 4' }}
          />
        )}

        {/* ── Completed shape fill ─────────────────────────────────────── */}
        {completed && vertices.length >= 3 && (
          <Polygon
            positions={polyPositions}
            pathOptions={{ color: '#1d4ed8', weight: 2, fillColor: '#3b82f6', fillOpacity: 0.22 }}
          />
        )}

        {/* ── Polygon vertex markers (during drawing + after for resize) ── */}
        {activeMode === 'polygon' && vertices.map((v, i) => (
          <Marker
            key={`pv-${i}`}
            position={[v.lat, v.lng]}
            icon={i === 0 ? greenIcon : blueIcon}
            draggable={false}
          />
        ))}

        {/* ── Completed polygon / rectangle: draggable corner handles ───── */}
        {completed && !completedCircle && vertices.map((v, i) => (
          <Marker
            key={`cv-${i}`}
            position={[v.lat, v.lng]}
            icon={i === 0 ? greenIcon : blueIcon}
            draggable={!readOnly}
            eventHandlers={{
              drag(e: any) {
                const ll = e.target.getLatLng();
                handleVertexDrag(i, { lat: ll.lat, lng: ll.lng });
              },
              dblclick() {
                if (!readOnly) handleVertexDblClick(i);
              },
            }}
          />
        ))}

        {/* ── Completed circle: center dot + east-edge resize handle ────── */}
        {completed && completedCircle && (
          <>
            <Marker
              position={[completedCircle.center.lat, completedCircle.center.lng]}
              icon={centerIcon}
              draggable={false}
            />
            {(() => {
              const edge = circleEastEdge(completedCircle.center, completedCircle.radius);
              return (
                <Marker
                  key="circle-edge"
                  position={[edge.lat, edge.lng]}
                  icon={orangeIcon}
                  draggable={!readOnly}
                  eventHandlers={{
                    drag(e: any) {
                      const ll = e.target.getLatLng();
                      handleCircleEdgeDrag({ lat: ll.lat, lng: ll.lng });
                    },
                  }}
                />
              );
            })()}
          </>
        )}
      </MapContainer>
    </div>
  );
}

// ─── SSR-safe export ──────────────────────────────────────────────────────────

export default dynamic(() => Promise.resolve(Inner), {
  ssr: false,
  loading: () => <MapSkeleton height="500px" />,
});
