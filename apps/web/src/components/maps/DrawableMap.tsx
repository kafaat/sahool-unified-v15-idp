'use client';

// Drawable Map Component - Click-to-draw polygon/rectangle on Leaflet
// خريطة الرسم التفاعلية - رسم المضلعات والمستطيلات بالنقر على الخريطة
// Exports GeoJSON via onBoundaryChange callback

import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import type * as L from 'leaflet';
import { MapContainer, TileLayer, LayersControl, Marker, Polyline, Polygon } from 'react-leaflet';
import { Undo2, Pentagon, Square, Trash2, X, Check } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DrawableMapProps {
  /** Called whenever a completed boundary changes; receives GeoJSON coordinates */
  onBoundaryChange?: (geojson: GeoJSON.Polygon | null) => void;
  initialCenter?: [number, number];
  initialZoom?: number;
  height?: string;
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
// Helper: build a small circular icon for vertices
// ---------------------------------------------------------------------------

function createVertexIcon(L: typeof import('leaflet'), color: string = '#2563eb') {
  return L.divIcon({
    className: '',
    html: `<div style="
      width: 12px;
      height: 12px;
      background: ${color};
      border: 2px solid #fff;
      border-radius: 50%;
      box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });
}

// ---------------------------------------------------------------------------
// Inner map component that has access to Leaflet via useMapEvents
// ---------------------------------------------------------------------------

function DrawingLayer({
  mode,
  vertices,
  onAddVertex,
  onMouseMove,
}: {
  mode: DrawingMode;
  vertices: Vertex[];
  onAddVertex: (v: Vertex) => void;
  onMouseMove?: (coords: { lat: number; lng: number }) => void;
}) {
  const [mapEvents, setMapEvents] = useState<((handlers: Record<string, (e: L.LeafletMouseEvent) => void>) => void) | null>(null);

  useEffect(() => {
    import('react-leaflet').then((mod) => {
      setMapEvents(() => mod.useMapEvents);
    });
  }, []);

  if (!mapEvents) return null;
  return (
    <DrawingLayerInner
      mode={mode}
      vertices={vertices}
      onAddVertex={onAddVertex}
      onMouseMove={onMouseMove}
      useMapEvents={mapEvents}
    />
  );
}

function DrawingLayerInner({
  mode,
  vertices: _vertices,
  onAddVertex,
  onMouseMove,
  useMapEvents,
}: {
  mode: DrawingMode;
  vertices: Vertex[];
  onAddVertex: (v: Vertex) => void;
  onMouseMove?: (coords: { lat: number; lng: number }) => void;
  useMapEvents: (handlers: Record<string, (e: L.LeafletMouseEvent) => void>) => void;
}) {
  useMapEvents({
    click(e: L.LeafletMouseEvent) {
      if (!mode) return;
      onAddVertex({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
    mousemove(e: L.LeafletMouseEvent) {
      onMouseMove?.({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });
  return null;
}

// ---------------------------------------------------------------------------
// Measurement utilities
// ---------------------------------------------------------------------------

/** Haversine distance between two points in meters */
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

/** Perimeter of the polygon in meters */
function computePerimeter(vertices: Vertex[]): number {
  if (vertices.length < 2) return 0;
  let total = 0;
  for (let i = 0; i < vertices.length; i++) {
    const next = (i + 1) % vertices.length;
    total += haversineDistance(vertices[i]!, vertices[next]!);
  }
  return total;
}

/** Area of a polygon in hectares using Shoelace formula on projected coordinates */
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

/** Convert vertices to GeoJSON Polygon */
function verticesToGeoJSON(vertices: Vertex[]): GeoJSON.Polygon {
  const ring = vertices.map((v) => [v.lng, v.lat] as [number, number]);
  if (ring.length > 0 && ring[0]) {
    ring.push([...ring[0]]);
  }
  return {
    type: 'Polygon',
    coordinates: [ring],
  };
}

function formatMeasurement(value: number, decimals: number = 2): string {
  return value.toFixed(decimals);
}

// ---------------------------------------------------------------------------
// Tile layer URL
// ---------------------------------------------------------------------------

const TILE_URL =
  process.env.NEXT_PUBLIC_TILE_URL ??
  'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

const SATELLITE_TILE_URL =
  process.env.NEXT_PUBLIC_SATELLITE_TILE_URL ??
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function DrawableMap({
  onBoundaryChange,
  initialCenter = [15.5527, 48.5164],
  initialZoom = 6,
  height = '500px',
}: DrawableMapProps) {
  const [isClient, setIsClient] = useState(false);
  const [leaflet, setLeaflet] = useState<typeof import('leaflet') | null>(null);
  const [mode, setMode] = useState<DrawingMode>(null);
  const [vertices, setVertices] = useState<Vertex[]>([]);
  const [completed, setCompleted] = useState(false);
  const [mouseCoords, setMouseCoords] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  const rectStage = useRef<'first' | 'second'>('first');

  // Load leaflet CSS and module on client
  useEffect(() => {
    setIsClient(true);
    if (!document.querySelector('link[href*="leaflet.css"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }
    import('leaflet').then((L) => setLeaflet(L));
  }, []);

  // -----------------------------------------------------------------------
  // Drawing handlers
  // -----------------------------------------------------------------------

  const emitBoundary = useCallback(
    (verts: Vertex[]) => {
      onBoundaryChange?.(verticesToGeoJSON(verts));
    },
    [onBoundaryChange],
  );

  const handleAddVertex = useCallback(
    (v: Vertex) => {
      if (completed) return;

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
      } else if (mode === 'polygon') {
        setVertices((prev) => [...prev, v]);
      }
    },
    [mode, completed, vertices, emitBoundary],
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

  const handleMouseMove = useCallback(
    (coords: { lat: number; lng: number }) => {
      setMouseCoords(coords);
    },
    [],
  );

  // Computed measurements
  const perimeter = useMemo(() => computePerimeter(vertices), [vertices]);
  const areaHectares = useMemo(
    () => computeAreaHectares(vertices),
    [vertices],
  );

  const startPolygon = useCallback(() => {
    handleClear();
    setMode('polygon');
  }, [handleClear]);

  const startRectangle = useCallback(() => {
    handleClear();
    setMode('rectangle');
  }, [handleClear]);

  // -----------------------------------------------------------------------
  // Render helpers
  // -----------------------------------------------------------------------

  const polylinePositions = vertices.map(
    (v) => [v.lat, v.lng] as [number, number],
  );

  const modeLabel =
    mode === 'polygon'
      ? 'رسم مضلع — انقر لإضافة نقاط'
      : mode === 'rectangle'
        ? rectStage.current === 'first' || vertices.length === 0
          ? 'رسم مستطيل — انقر لتحديد الزاوية الأولى'
          : 'انقر لتحديد الزاوية الثانية'
        : null;

  // -----------------------------------------------------------------------
  // SSR guard
  // -----------------------------------------------------------------------

  if (!isClient || !leaflet) {
    return <MapLoadingFallback height={height} />;
  }

  const vertexIcon = createVertexIcon(leaflet, '#2563eb');
  const firstVertexIcon = createVertexIcon(leaflet, '#16a34a');

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
      <div className="absolute top-3 right-3 z-[1000] flex flex-col gap-2">
        {/* Mode selection buttons */}
        {!mode && !completed && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={startPolygon}
              className="px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-blue-700 transition-colors inline-flex items-center gap-1.5"
            >
              <Pentagon size={14} />
              رسم مضلع
            </button>
            <button
              type="button"
              onClick={startRectangle}
              className="px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-indigo-700 transition-colors inline-flex items-center gap-1.5"
            >
              <Square size={14} />
              رسم مستطيل
            </button>
          </div>
        )}

        {/* Drawing controls */}
        {mode && !completed && (
          <div className="flex gap-2">
            {mode === 'polygon' && vertices.length >= 3 && (
              <button
                type="button"
                onClick={handleComplete}
                className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-green-700 transition-colors inline-flex items-center gap-1"
              >
                <Check size={14} />
                إكمال
              </button>
            )}
            {mode === 'polygon' && vertices.length > 0 && (
              <button
                type="button"
                onClick={handleUndo}
                className="px-3 py-2 bg-gray-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-gray-700 transition-colors inline-flex items-center gap-1"
              >
                <Undo2 size={14} />
                تراجع
              </button>
            )}
            <button
              type="button"
              onClick={handleClear}
              className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors inline-flex items-center gap-1"
            >
              <Trash2 size={14} />
              مسح
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="px-3 py-2 bg-red-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-red-600 transition-colors inline-flex items-center gap-1"
            >
              <X size={14} />
              إلغاء
            </button>
          </div>
        )}

        {/* Post-completion controls */}
        {completed && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleClear}
              className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors inline-flex items-center gap-1"
            >
              <Trash2 size={14} />
              مسح
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="px-3 py-2 bg-red-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-red-600 transition-colors inline-flex items-center gap-1"
            >
              <X size={14} />
              إلغاء
            </button>
          </div>
        )}
      </div>

      {/* Status bar */}
      {modeLabel && !completed && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-[1000] bg-white/95 backdrop-blur px-4 py-2 rounded-md shadow-md text-sm font-medium text-gray-700 border border-gray-200 flex flex-col items-center gap-1">
          <div>
            {modeLabel}
            {mode === 'polygon' && vertices.length > 0 && (
              <span className="mr-2 text-blue-600">
                النقاط: {vertices.length}
              </span>
            )}
          </div>
          {vertices.length >= 2 && (
            <div className="text-xs text-gray-500">
              المساحة: {formatMeasurement(areaHectares)} هكتار | المحيط:{' '}
              {formatMeasurement(perimeter)} م
            </div>
          )}
        </div>
      )}

      {/* Completion info */}
      {completed && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-[1000] bg-green-50 border border-green-300 px-4 py-2 rounded-md shadow-md text-sm font-medium text-green-800 flex flex-col items-center gap-1">
          <div>تم تحديد المنطقة — النقاط: {vertices.length}</div>
          <div className="text-xs">
            المساحة: {formatMeasurement(areaHectares)} هكتار | المحيط:{' '}
            {formatMeasurement(perimeter)} م
          </div>
        </div>
      )}

      {/* Mouse coordinates display */}
      {mouseCoords && (
        <div
          className="absolute bottom-3 right-3 z-[1000] bg-black/70 text-white px-3 py-1 rounded text-xs font-mono"
          dir="ltr"
        >
          خ.ع: {mouseCoords.lat.toFixed(4)}&deg; | خ.ط:{' '}
          {mouseCoords.lng.toFixed(4)}&deg;
        </div>
      )}

      {/* Map */}
      <MapContainer
        center={initialCenter}
        zoom={initialZoom}
        style={{ height, width: '100%' }}
        className="z-0"
      >
        <LayersControl position="topleft">
          <LayersControl.BaseLayer checked name="خريطة الشوارع">
            <TileLayer
              url={TILE_URL}
              attribution="&copy; OpenStreetMap contributors"
              maxZoom={19}
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="صور فضائية">
            <TileLayer
              url={SATELLITE_TILE_URL}
              attribution="&copy; Esri, Maxar, Earthstar Geographics"
              maxZoom={18}
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {/* Drawing event listener */}
        <DrawingLayer
          mode={mode}
          vertices={vertices}
          onAddVertex={handleAddVertex}
          onMouseMove={handleMouseMove}
        />

        {/* Vertex markers */}
        {vertices.map((v, i) => (
          <Marker
            key={`vertex-${i}`}
            position={[v.lat, v.lng]}
            icon={(i === 0 ? firstVertexIcon : vertexIcon) as unknown as L.Icon}
            interactive={false}
          />
        ))}

        {/* Polyline while drawing (not yet completed) */}
        {!completed && vertices.length >= 2 && (
          <Polyline
            positions={polylinePositions}
            pathOptions={{ color: '#2563eb', weight: 2, dashArray: '6 4' }}
          />
        )}

        {/* Completed polygon */}
        {completed && vertices.length >= 3 && (
          <Polygon
            positions={polylinePositions}
            pathOptions={{
              color: '#2563eb',
              weight: 2,
              fillColor: '#3b82f6',
              fillOpacity: 0.15,
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
