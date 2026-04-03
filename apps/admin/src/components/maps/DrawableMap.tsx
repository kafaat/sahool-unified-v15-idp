'use client';

// Drawable Map Component - Click-to-draw polygon/bbox selection
// خريطة الرسم التفاعلية - رسم المضلعات ومربعات الإحاطة بالنقر
// Supports: polygon drawing via click, bbox calculation, GeoJSON export

import { useEffect, useState, useRef, useCallback } from 'react';
import dynamic from 'next/dynamic';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DrawableMapProps {
  onBboxSelect: (bbox: [number, number, number, number]) => void;
  onBoundaryDraw: (coordinates: number[][][]) => void;
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
// Dynamic imports (Leaflet does not support SSR)
// ---------------------------------------------------------------------------

const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false, loading: () => null },
) as any;

const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false, loading: () => null },
) as any;

const LayersControl = dynamic(
  () => import('react-leaflet').then((mod) => mod.LayersControl),
  { ssr: false, loading: () => null },
) as any;

const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false, loading: () => null },
) as any;

const Polyline = dynamic(
  () => import('react-leaflet').then((mod) => mod.Polyline),
  { ssr: false, loading: () => null },
) as any;

const Polygon = dynamic(
  () => import('react-leaflet').then((mod) => mod.Polygon),
  { ssr: false, loading: () => null },
) as any;

// ---------------------------------------------------------------------------
// Helper: build a small circular icon for vertices
// ---------------------------------------------------------------------------

function createVertexIcon(L: any, color: string = '#2563eb') {
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
}: {
  mode: DrawingMode;
  vertices: Vertex[];
  onAddVertex: (v: Vertex) => void;
}) {
  // useMapEvents is loaded dynamically — we import it at render time on the
  // client so the import is safe (this component is only rendered inside
  // MapContainer which itself is dynamically loaded with ssr:false).
  const [mapEvents, setMapEvents] = useState<any>(null);

  useEffect(() => {
    import('react-leaflet').then((mod) => {
      setMapEvents(() => mod.useMapEvents);
    });
  }, []);

  if (!mapEvents) return null;
  return <DrawingLayerInner mode={mode} vertices={vertices} onAddVertex={onAddVertex} useMapEvents={mapEvents} />;
}

function DrawingLayerInner({
  mode,
  vertices: _vertices,
  onAddVertex,
  useMapEvents,
}: {
  mode: DrawingMode;
  vertices: Vertex[];
  onAddVertex: (v: Vertex) => void;
  useMapEvents: any;
}) {
  useMapEvents({
    click(e: any) {
      if (!mode) return;
      onAddVertex({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });
  return null;
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function computeBbox(vertices: Vertex[]): [number, number, number, number] {
  const lats = vertices.map((v) => v.lat);
  const lngs = vertices.map((v) => v.lng);
  return [Math.min(...lngs), Math.min(...lats), Math.max(...lngs), Math.max(...lats)];
}

function verticesToGeoJSON(vertices: Vertex[]): number[][][] {
  // GeoJSON Polygon: [[[lng, lat], ...]] — ring must be closed
  const ring = vertices.map((v) => [v.lng, v.lat]);
  if (ring.length > 0 && ring[0]) {
    ring.push([...ring[0]]); // close the ring
  }
  return [ring];
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function DrawableMap({
  onBboxSelect,
  onBoundaryDraw,
  initialCenter = [15.5527, 48.5164],
  initialZoom = 6,
  height = '500px',
}: DrawableMapProps) {
  const [isClient, setIsClient] = useState(false);
  const [leaflet, setLeaflet] = useState<any>(null);
  const [mode, setMode] = useState<DrawingMode>(null);
  const [vertices, setVertices] = useState<Vertex[]>([]);
  const [completed, setCompleted] = useState(false);

  // Rectangle-specific: first and second click
  const rectStage = useRef<'first' | 'second'>('first');

  // Load leaflet CSS and module on client
  useEffect(() => {
    setIsClient(true);

    // CSS
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

  const handleAddVertex = useCallback(
    (v: Vertex) => {
      if (completed) return;

      if (mode === 'rectangle') {
        if (rectStage.current === 'first') {
          setVertices([v]);
          rectStage.current = 'second';
        } else {
          // Build rectangle from two corners
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

          const bbox = computeBbox(rectVertices);
          onBboxSelect(bbox);
          onBoundaryDraw(verticesToGeoJSON(rectVertices));
        }
      } else if (mode === 'polygon') {
        setVertices((prev) => [...prev, v]);
      }
    },
    [mode, completed, vertices, onBboxSelect, onBoundaryDraw],
  );

  const handleComplete = useCallback(() => {
    if (vertices.length < 3) return;
    setCompleted(true);

    const bbox = computeBbox(vertices);
    onBboxSelect(bbox);
    onBoundaryDraw(verticesToGeoJSON(vertices));
  }, [vertices, onBboxSelect, onBoundaryDraw]);

  const handleClear = useCallback(() => {
    setVertices([]);
    setCompleted(false);
    rectStage.current = 'first';
  }, []);

  const handleCancel = useCallback(() => {
    setVertices([]);
    setCompleted(false);
    setMode(null);
    rectStage.current = 'first';
  }, []);

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

  const polylinePositions = vertices.map((v) => [v.lat, v.lng] as [number, number]);

  const modeLabel = mode === 'polygon'
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
    <div className="relative rounded-lg overflow-hidden border border-gray-200" dir="rtl">
      {/* Toolbar */}
      <div className="absolute top-3 right-3 z-[1000] flex flex-col gap-2">
        {/* Mode selection buttons */}
        {!mode && !completed && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={startPolygon}
              className="px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-blue-700 transition-colors"
            >
              رسم مضلع
            </button>
            <button
              type="button"
              onClick={startRectangle}
              className="px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-indigo-700 transition-colors"
            >
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
                className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md shadow-md hover:bg-green-700 transition-colors"
              >
                إكمال ✓
              </button>
            )}
            <button
              type="button"
              onClick={handleClear}
              className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors"
            >
              مسح
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="px-3 py-2 bg-red-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-red-600 transition-colors"
            >
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
              className="px-3 py-2 bg-yellow-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-yellow-600 transition-colors"
            >
              مسح
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="px-3 py-2 bg-red-500 text-white text-sm font-medium rounded-md shadow-md hover:bg-red-600 transition-colors"
            >
              إلغاء
            </button>
          </div>
        )}
      </div>

      {/* Status bar */}
      {modeLabel && !completed && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-[1000] bg-white/95 backdrop-blur px-4 py-2 rounded-md shadow-md text-sm font-medium text-gray-700 border border-gray-200">
          {modeLabel}
          {mode === 'polygon' && vertices.length > 0 && (
            <span className="mr-2 text-blue-600">({vertices.length} نقاط)</span>
          )}
        </div>
      )}

      {/* Completion info */}
      {completed && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-[1000] bg-green-50 border border-green-300 px-4 py-2 rounded-md shadow-md text-sm font-medium text-green-800">
          تم تحديد المنطقة — {vertices.length} نقاط
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
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
              maxZoom={19}
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="صور فضائية">
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution="&copy; Esri, Maxar, Earthstar Geographics"
              maxZoom={18}
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {/* Drawing event listener */}
        <DrawingLayer mode={mode} vertices={vertices} onAddVertex={handleAddVertex} />

        {/* Vertex markers */}
        {vertices.map((v, i) => (
          <Marker
            key={`vertex-${i}`}
            position={[v.lat, v.lng]}
            icon={i === 0 ? firstVertexIcon : vertexIcon}
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
