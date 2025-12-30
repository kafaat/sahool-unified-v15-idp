'use client';

/**
 * SAHOOL Field Drawing Map Component
 * مكون خريطة رسم الحقول التفاعلية
 *
 * Features:
 * - Draw polygon boundaries for fields
 * - Edit existing field boundaries
 * - Measure area in hectares
 * - Undo/Redo support
 * - GPS location support
 * - Satellite/Map view toggle
 *
 * Similar to: FarmLogs, Climate FieldView, Ag Leader
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  MapPin,
  Loader2,
  Edit2,
  Trash2,
  RefreshCw,
  ArrowLeft,
  Navigation,
  Globe,
  Layers,
  Check,
  X,
  Plus,
  Minus,
} from 'lucide-react';
import type { GeoPolygon } from '../types';

// Leaflet type definition
declare global {
  interface Window {
    L?: typeof import('leaflet');
  }
}

interface FieldDrawingMapProps {
  initialPolygon?: GeoPolygon;
  onPolygonChange?: (polygon: GeoPolygon | null) => void;
  onAreaChange?: (areaHectares: number) => void;
  height?: string;
  editable?: boolean;
  showAreaCalculation?: boolean;
}

// Drawing modes
type DrawingMode = 'none' | 'draw' | 'edit' | 'delete';

// Map tile layers
const TILE_LAYERS = {
  standard: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors',
  },
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '© Esri, Maxar, Earthstar Geographics',
  },
  terrain: {
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '© OpenTopoMap contributors',
  },
};

// Yemen center coordinates
const YEMEN_CENTER: [number, number] = [15.5527, 48.5164];
const DEFAULT_ZOOM = 8;

// Calculate area from coordinates (in hectares)
function calculateArea(coordinates: number[][]): number {
  if (!coordinates || coordinates.length < 3) return 0;

  // Shoelace formula for polygon area
  let area = 0;
  const n = coordinates.length;

  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const coordI = coordinates[i] as number[] | undefined;
    const coordJ = coordinates[j] as number[] | undefined;

    // Skip if coordinates are invalid
    if (!coordI || !coordJ || coordI.length < 2 || coordJ.length < 2) continue;

    const lng1 = coordI[0] ?? 0;
    const lat1 = coordI[1] ?? 0;
    const lng2 = coordJ[0] ?? 0;
    const lat2 = coordJ[1] ?? 0;

    // Convert to approximate meters (rough approximation for Yemen latitude)
    const x1 = lng1 * 111320 * Math.cos((lat1 * Math.PI) / 180);
    const y1 = lat1 * 110540;
    const x2 = lng2 * 111320 * Math.cos((lat2 * Math.PI) / 180);
    const y2 = lat2 * 110540;

    area += x1 * y2;
    area -= x2 * y1;
  }

  area = Math.abs(area) / 2;
  // Convert square meters to hectares
  return area / 10000;
}

export const FieldDrawingMap: React.FC<FieldDrawingMapProps> = ({
  initialPolygon,
  onPolygonChange,
  onAreaChange,
  height = '500px',
  editable = true,
  showAreaCalculation = true,
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const polygonLayerRef = useRef<any>(null);
  const drawingPointsRef = useRef<[number, number][]>([]);
  const markersRef = useRef<any[]>([]);
  const polylineRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [mapError, setMapError] = useState<string | null>(null);
  const [drawingMode, setDrawingMode] = useState<DrawingMode>('none');
  const [currentTileLayer, setCurrentTileLayer] = useState<'standard' | 'satellite' | 'terrain'>('standard');
  const [areaHectares, setAreaHectares] = useState(0);
  const [undoStack, setUndoStack] = useState<[number, number][][]>([]);
  const [redoStack, setRedoStack] = useState<[number, number][][]>([]);
  const [isDrawing, setIsDrawing] = useState(false);

  // Update area when polygon changes
  const updateArea = useCallback((coords: [number, number][]) => {
    if (coords.length >= 3) {
      const geoJsonCoords = coords.map((c) => [c[1], c[0]]); // Convert to [lng, lat]
      const area = calculateArea(geoJsonCoords);
      setAreaHectares(area);
      onAreaChange?.(area);
    } else {
      setAreaHectares(0);
      onAreaChange?.(0);
    }
  }, [onAreaChange]);

  // Convert drawing points to GeoJSON polygon
  const createPolygonGeoJSON = useCallback((points: [number, number][]): GeoPolygon | null => {
    if (!points || points.length < 3) return null;

    const firstPoint = points[0];
    if (!firstPoint) return null;

    // Close the polygon by adding first point at end
    const closedPoints: [number, number][] = [...points, firstPoint];
    const coordinates: number[][] = closedPoints
      .filter((p): p is [number, number] => p !== undefined && p.length === 2)
      .map((p) => [p[1], p[0]]); // Convert [lat, lng] to [lng, lat]

    return {
      type: 'Polygon',
      coordinates: [coordinates],
    };
  }, []);

  // Initialize map
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    const initMap = async () => {
      try {
        if (!window.L) {
          await loadLeaflet();
        }

        if (!window.L) {
          setMapError('فشل في تحميل مكتبة الخرائط');
          setIsLoading(false);
          return;
        }

        const L = window.L;

        if (!mapInstanceRef.current && mapRef.current) {
          const map = L.map(mapRef.current, {
            zoomControl: true,
            doubleClickZoom: false, // Disable to prevent conflicts with drawing
          }).setView(YEMEN_CENTER, DEFAULT_ZOOM);

          // Add initial tile layer
          const tileLayer = L.tileLayer(TILE_LAYERS.standard.url, {
            attribution: TILE_LAYERS.standard.attribution,
            maxZoom: 19,
          }).addTo(map);

          tileLayerRef.current = tileLayer;
          mapInstanceRef.current = map;

          // Load initial polygon if provided
          if (initialPolygon && initialPolygon.coordinates && initialPolygon.coordinates[0]) {
            const coords = initialPolygon.coordinates[0];
            const latLngs = coords.slice(0, -1).map((c: number[]) => [c[1], c[0]] as [number, number]);
            drawingPointsRef.current = latLngs;

            const polygon = L.polygon(latLngs, {
              color: '#2563eb',
              weight: 3,
              fillColor: '#3b82f6',
              fillOpacity: 0.3,
            }).addTo(map);

            polygonLayerRef.current = polygon;
            updateArea(latLngs);

            // Fit map to polygon
            map.fitBounds(polygon.getBounds(), { padding: [50, 50] });
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing map:', error);
        setMapError('حدث خطأ في تحميل الخريطة');
        setIsLoading(false);
      }
    };

    initMap();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [initialPolygon, updateArea]);

  // Handle tile layer change
  useEffect(() => {
    if (!mapInstanceRef.current || !window.L) return;

    const L = window.L;
    const layer = TILE_LAYERS[currentTileLayer];

    if (tileLayerRef.current) {
      mapInstanceRef.current.removeLayer(tileLayerRef.current);
    }

    tileLayerRef.current = L.tileLayer(layer.url, {
      attribution: layer.attribution,
      maxZoom: 19,
    }).addTo(mapInstanceRef.current);
  }, [currentTileLayer]);

  // Handle drawing mode
  useEffect(() => {
    if (!mapInstanceRef.current || !window.L || !editable) return;

    const L = window.L;
    const map = mapInstanceRef.current;

    // Clear existing event listeners
    map.off('click');

    if (drawingMode === 'draw') {
      setIsDrawing(true);
      map.getContainer().style.cursor = 'crosshair';

      map.on('click', (e: any) => {
        const { lat, lng } = e.lngLat ?? e.latlng;
        const point: [number, number] = [lat, lng];

        // Save current state to undo stack
        setUndoStack((prev) => [...prev, [...drawingPointsRef.current]]);
        setRedoStack([]);

        // Add point
        drawingPointsRef.current.push(point);

        // Add marker
        const marker = L.circleMarker([lat, lng], {
          radius: 8,
          fillColor: '#2563eb',
          color: '#1e40af',
          weight: 2,
          fillOpacity: 1,
        }).addTo(map);
        markersRef.current.push(marker);

        // Update polyline
        if (polylineRef.current) {
          map.removeLayer(polylineRef.current);
        }
        if (drawingPointsRef.current.length > 1) {
          polylineRef.current = L.polyline(drawingPointsRef.current, {
            color: '#2563eb',
            weight: 2,
            dashArray: '5, 10',
          }).addTo(map);
        }

        // Update area preview
        updateArea(drawingPointsRef.current);
      });
    } else {
      setIsDrawing(false);
      map.getContainer().style.cursor = '';
    }

    return () => {
      map.off('click');
      map.getContainer().style.cursor = '';
    };
  }, [drawingMode, editable, updateArea]);

  // Complete drawing
  const completeDrawing = useCallback(() => {
    if (!mapInstanceRef.current || !window.L) return;
    if (drawingPointsRef.current.length < 3) {
      alert('يجب رسم 3 نقاط على الأقل');
      return;
    }

    const L = window.L;
    const map = mapInstanceRef.current;

    // Clear temporary drawing elements
    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];
    if (polylineRef.current) {
      map.removeLayer(polylineRef.current);
      polylineRef.current = null;
    }

    // Remove old polygon
    if (polygonLayerRef.current) {
      map.removeLayer(polygonLayerRef.current);
    }

    // Create final polygon
    const polygon = L.polygon(drawingPointsRef.current, {
      color: '#16a34a',
      weight: 3,
      fillColor: '#22c55e',
      fillOpacity: 0.3,
    }).addTo(map);

    polygonLayerRef.current = polygon;

    // Create GeoJSON and notify parent
    const geoJson = createPolygonGeoJSON(drawingPointsRef.current);
    onPolygonChange?.(geoJson);

    // Update area
    updateArea(drawingPointsRef.current);

    setDrawingMode('none');
    setIsDrawing(false);
  }, [createPolygonGeoJSON, onPolygonChange, updateArea]);

  // Cancel drawing
  const cancelDrawing = useCallback(() => {
    if (!mapInstanceRef.current) return;

    const map = mapInstanceRef.current;

    // Clear temporary elements
    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];
    if (polylineRef.current) {
      map.removeLayer(polylineRef.current);
      polylineRef.current = null;
    }

    // Restore previous polygon if exists
    if (undoStack.length > 0) {
      drawingPointsRef.current = undoStack[undoStack.length - 1] || [];
    } else {
      drawingPointsRef.current = [];
    }

    setDrawingMode('none');
    setIsDrawing(false);
    setUndoStack([]);
    setRedoStack([]);
  }, [undoStack]);

  // Clear all
  const clearAll = useCallback(() => {
    if (!mapInstanceRef.current) return;

    const map = mapInstanceRef.current;

    // Save to undo
    setUndoStack((prev) => [...prev, [...drawingPointsRef.current]]);
    setRedoStack([]);

    // Clear everything
    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];
    if (polylineRef.current) {
      map.removeLayer(polylineRef.current);
      polylineRef.current = null;
    }
    if (polygonLayerRef.current) {
      map.removeLayer(polygonLayerRef.current);
      polygonLayerRef.current = null;
    }

    drawingPointsRef.current = [];
    setAreaHectares(0);
    onPolygonChange?.(null);
    onAreaChange?.(0);
  }, [onPolygonChange, onAreaChange]);

  // Undo
  const handleUndo = useCallback(() => {
    if (undoStack.length === 0) return;

    const previousState = undoStack[undoStack.length - 1];
    setRedoStack((prev) => [...prev, [...drawingPointsRef.current]]);
    setUndoStack((prev) => prev.slice(0, -1));
    drawingPointsRef.current = previousState || [];

    // Redraw
    if (mapInstanceRef.current && window.L) {
      const L = window.L;
      const map = mapInstanceRef.current;

      markersRef.current.forEach((m) => map.removeLayer(m));
      markersRef.current = [];

      drawingPointsRef.current.forEach(([lat, lng]) => {
        const marker = L.circleMarker([lat, lng], {
          radius: 8,
          fillColor: '#2563eb',
          color: '#1e40af',
          weight: 2,
          fillOpacity: 1,
        }).addTo(map);
        markersRef.current.push(marker);
      });

      if (polylineRef.current) {
        map.removeLayer(polylineRef.current);
      }
      if (drawingPointsRef.current.length > 1) {
        polylineRef.current = L.polyline(drawingPointsRef.current, {
          color: '#2563eb',
          weight: 2,
          dashArray: '5, 10',
        }).addTo(map);
      }

      updateArea(drawingPointsRef.current);
    }
  }, [undoStack, updateArea]);

  // Redo
  const handleRedo = useCallback(() => {
    if (redoStack.length === 0) return;

    const nextState = redoStack[redoStack.length - 1];
    setUndoStack((prev) => [...prev, [...drawingPointsRef.current]]);
    setRedoStack((prev) => prev.slice(0, -1));
    drawingPointsRef.current = nextState || [];

    updateArea(drawingPointsRef.current);
  }, [redoStack, updateArea]);

  // Get current location
  const goToCurrentLocation = useCallback(() => {
    if (!mapInstanceRef.current) return;

    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          mapInstanceRef.current?.setView([latitude, longitude], 15);
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('تعذر الحصول على الموقع الحالي');
        }
      );
    } else {
      alert('المتصفح لا يدعم تحديد الموقع');
    }
  }, []);

  // Zoom in
  const handleZoomIn = useCallback(() => {
    if (!mapInstanceRef.current) return;
    mapInstanceRef.current.zoomIn();
  }, []);

  // Zoom out
  const handleZoomOut = useCallback(() => {
    if (!mapInstanceRef.current) return;
    mapInstanceRef.current.zoomOut();
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center">
          <Loader2 className="w-10 h-10 animate-spin text-green-600 mb-3" />
          <p className="text-gray-600">جاري تحميل الخريطة...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (mapError) {
    return (
      <div
        className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative flex items-center justify-center"
        style={{ height }}
      >
        <div className="flex flex-col items-center text-center p-4">
          <MapPin className="w-12 h-12 text-gray-400 mb-3" />
          <p className="text-gray-600 font-medium">{mapError}</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="bg-white rounded-xl border border-gray-200 overflow-hidden relative shadow-sm"
      style={{ height }}
    >
      {/* Map Container */}
      <div ref={mapRef} className="w-full h-full" />

      {/* Drawing Toolbar */}
      {editable && (
        <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
          {/* Main drawing tools */}
          <div className="bg-white rounded-lg shadow-lg p-1 flex flex-col gap-1">
            <button
              onClick={() => setDrawingMode(drawingMode === 'draw' ? 'none' : 'draw')}
              className={`p-2 rounded-lg transition-colors ${
                drawingMode === 'draw'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              title="رسم حقل جديد"
            >
              <Edit2 className="w-5 h-5" />
            </button>

            <button
              onClick={clearAll}
              className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-red-100 hover:text-red-600 transition-colors"
              title="مسح الكل"
            >
              <Trash2 className="w-5 h-5" />
            </button>

            <div className="h-px bg-gray-200 my-1" />

            <button
              onClick={handleUndo}
              disabled={undoStack.length === 0}
              className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="تراجع"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>

            <button
              onClick={handleRedo}
              disabled={redoStack.length === 0}
              className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="إعادة"
            >
              <RefreshCw className="w-5 h-5" />
            </button>

            <div className="h-px bg-gray-200 my-1" />

            <button
              onClick={goToCurrentLocation}
              className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              title="موقعي الحالي"
            >
              <Navigation className="w-5 h-5" />
            </button>
          </div>

          {/* Map type selector */}
          <div className="bg-white rounded-lg shadow-lg p-1 flex flex-col gap-1">
            <button
              onClick={() => setCurrentTileLayer('standard')}
              className={`p-2 rounded-lg transition-colors ${
                currentTileLayer === 'standard'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              title="خريطة عادية"
            >
              <Globe className="w-5 h-5" />
            </button>

            <button
              onClick={() => setCurrentTileLayer('satellite')}
              className={`p-2 rounded-lg transition-colors ${
                currentTileLayer === 'satellite'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              title="صور الأقمار الصناعية"
            >
              <Layers className="w-5 h-5" />
            </button>
          </div>

          {/* Zoom controls */}
          <div className="bg-white rounded-lg shadow-lg p-1 flex flex-col gap-1">
            <button
              onClick={handleZoomIn}
              className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              title="تكبير"
            >
              <Plus className="w-5 h-5" />
            </button>

            <button
              onClick={handleZoomOut}
              className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              title="تصغير"
            >
              <Minus className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Drawing mode indicator and controls */}
      {isDrawing && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000]">
          <div className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-3">
            <span className="text-sm font-medium">وضع الرسم - انقر لإضافة نقاط</span>
            <div className="h-4 w-px bg-blue-400" />
            <button
              onClick={completeDrawing}
              className="p-1 hover:bg-blue-500 rounded transition-colors"
              title="إنهاء الرسم"
            >
              <Check className="w-5 h-5" />
            </button>
            <button
              onClick={cancelDrawing}
              className="p-1 hover:bg-blue-500 rounded transition-colors"
              title="إلغاء"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Area display */}
      {showAreaCalculation && (
        <div className="absolute bottom-4 right-4 z-[1000]">
          <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3">
            <div className="text-xs text-gray-500 mb-1">المساحة المحسوبة</div>
            <div className="text-lg font-bold text-gray-900">
              {areaHectares.toFixed(2)} <span className="text-sm font-normal text-gray-600">هكتار</span>
            </div>
            {areaHectares > 0 && (
              <div className="text-xs text-gray-500 mt-1">
                ≈ {(areaHectares * 10000).toFixed(0)} م²
              </div>
            )}
          </div>
        </div>
      )}

      {/* Instructions */}
      {editable && drawingPointsRef.current.length === 0 && !isDrawing && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-[1000]">
          <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg px-4 py-2 text-sm text-gray-600">
            انقر على زر القلم ✏️ لبدء رسم حدود الحقل
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to load Leaflet dynamically
async function loadLeaflet(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.L) {
      resolve();
      return;
    }

    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    cssLink.crossOrigin = '';
    document.head.appendChild(cssLink);

    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Leaflet'));
    document.head.appendChild(script);
  });
}

export default FieldDrawingMap;
