/**
 * Prescription Map Component
 * مكون خريطة الوصفة
 *
 * Map visualization for VRA prescription zones with color-coded rates using Leaflet.
 */

'use client';

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Map as MapIcon, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PrescriptionResponse } from '../types/vra';

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false, loading: () => <MapLoadingFallback /> }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);
const GeoJSON = dynamic(
  () => import('react-leaflet').then((mod) => mod.GeoJSON),
  { ssr: false }
);

// ═══════════════════════════════════════════════════════════════════════════
// Component Props
// ═══════════════════════════════════════════════════════════════════════════

export interface PrescriptionMapProps {
  prescription: PrescriptionResponse;
  height?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Loading Fallback
// ═══════════════════════════════════════════════════════════════════════════

function MapLoadingFallback() {
  return (
    <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg">
      <div className="flex flex-col items-center gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <p className="text-sm text-gray-600">Loading map... | جاري تحميل الخريطة...</p>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const PrescriptionMap: React.FC<PrescriptionMapProps> = ({
  prescription,
  height = '500px',
}) => {
  // Convert zones to GeoJSON FeatureCollection
  const geoJsonData = useMemo(() => {
    const features = prescription.zones
      .filter((zone) => zone.polygon && zone.polygon.length > 0)
      .map((zone) => ({
        type: 'Feature' as const,
        id: zone.zoneId,
        properties: {
          zoneId: zone.zoneId,
          zoneName: zone.zoneName,
          zoneNameAr: zone.zoneNameAr,
          zoneLevel: zone.zoneLevel,
          ndviMin: zone.ndviMin,
          ndviMax: zone.ndviMax,
          areaHa: zone.areaHa,
          percentage: zone.percentage,
          recommendedRate: zone.recommendedRate,
          unit: zone.unit,
          totalProduct: zone.totalProduct,
          color: zone.color,
        },
        geometry: {
          type: 'Polygon' as const,
          coordinates: zone.polygon,
        },
      }));

    return {
      type: 'FeatureCollection' as const,
      features,
    };
  }, [prescription.zones]);

  // Calculate map center and bounds
  const mapConfig = useMemo(() => {
    if (!prescription.zones || prescription.zones.length === 0) {
      return { center: [15.5, 44.2] as [number, number], zoom: 12 };
    }

    // Calculate center from zone centroids
    const lats = prescription.zones.map((z) => z.centroid[1]);
    const lons = prescription.zones.map((z) => z.centroid[0]);

    const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
    const centerLon = (Math.min(...lons) + Math.max(...lons)) / 2;

    // Calculate appropriate zoom level based on bounds
    const latDiff = Math.max(...lats) - Math.min(...lats);
    const lonDiff = Math.max(...lons) - Math.min(...lons);
    const maxDiff = Math.max(latDiff, lonDiff);

    let zoom = 12;
    if (maxDiff > 0.1) zoom = 10;
    if (maxDiff > 0.2) zoom = 9;
    if (maxDiff > 0.5) zoom = 8;
    if (maxDiff < 0.05) zoom = 14;

    return {
      center: [centerLat, centerLon] as [number, number],
      zoom,
    };
  }, [prescription.zones]);

  // GeoJSON style function
  const getGeoJsonStyle = (feature: any) => {
    return {
      fillColor: feature.properties.color,
      fillOpacity: 0.6,
      color: feature.properties.color,
      weight: 3,
      opacity: 1,
    };
  };

  // GeoJSON hover/interaction handlers
  const onEachFeature = (feature: any, layer: any) => {
    const props = feature.properties;

    // Create popup content
    const popupContent = `
      <div class="p-2 min-w-[200px]">
        <h3 class="font-bold text-sm mb-2">${props.zoneName} | ${props.zoneNameAr}</h3>
        <div class="space-y-1 text-xs">
          <p><strong>NDVI Range:</strong> ${props.ndviMin.toFixed(2)} - ${props.ndviMax.toFixed(2)}</p>
          <p><strong>Area | المساحة:</strong> ${props.areaHa.toFixed(2)} ha (${props.percentage.toFixed(1)}%)</p>
          <p><strong>Rate | المعدل:</strong> <span class="text-green-700 font-semibold">${props.recommendedRate.toFixed(2)} ${props.unit}</span></p>
          <p><strong>Total Product | إجمالي المنتج:</strong> ${props.totalProduct.toFixed(2)} ${props.unit}</p>
        </div>
      </div>
    `;

    layer.bindPopup(popupContent);

    // Highlight on hover
    layer.on({
      mouseover: (e: any) => {
        const layer = e.target;
        layer.setStyle({
          weight: 5,
          fillOpacity: 0.8,
        });
      },
      mouseout: (e: any) => {
        const layer = e.target;
        layer.setStyle(getGeoJsonStyle(feature));
      },
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapIcon className="w-5 h-5" />
          <span>Prescription Map | خريطة الوصفة</span>
        </CardTitle>
        <p className="text-sm text-gray-600 mt-1">
          {prescription.vraType.toUpperCase()} Application - {prescription.numZones} Management Zones
        </p>
      </CardHeader>
      <CardContent>
        {/* Leaflet Map Container */}
        <div
          className="rounded-lg border-2 border-gray-200 overflow-hidden relative"
          style={{ height }}
        >
          <MapContainer
            center={mapConfig.center}
            zoom={mapConfig.zoom}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
          >
            {/* OpenStreetMap Tile Layer */}
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />

            {/* Prescription Zones GeoJSON Layer */}
            <GeoJSON
              key={prescription.id}
              data={geoJsonData}
              style={getGeoJsonStyle}
              onEachFeature={onEachFeature}
            />
          </MapContainer>

          {/* Map Info Overlay */}
          <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3 max-w-xs z-10">
            <div className="space-y-1 text-xs">
              <p className="font-bold text-gray-800">
                Total Area | إجمالي المساحة: {prescription.totalAreaHa.toFixed(2)} ha
              </p>
              <p className="text-gray-700">
                Target Rate | المعدل المستهدف: {prescription.targetRate} {prescription.unit}
              </p>
              <p className="text-green-700 font-semibold">
                Savings | التوفير: {prescription.savingsPercent.toFixed(1)}%
                ({prescription.savingsAmount.toFixed(2)} {prescription.unit})
              </p>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4">
          <h4 className="text-sm font-semibold mb-2">Legend | مفتاح الخريطة</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
            {prescription.zones.map((zone) => (
              <div key={zone.zoneId} className="flex items-center gap-2">
                <div
                  className="w-6 h-6 rounded border border-gray-300"
                  style={{ backgroundColor: zone.color }}
                />
                <div className="flex-1">
                  <p className="text-xs font-medium">
                    {zone.zoneName} | {zone.zoneNameAr}
                  </p>
                  <p className="text-xs text-gray-500">
                    {zone.percentage.toFixed(1)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Zone Details Tooltips */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {prescription.zones.map((zone) => (
            <div
              key={zone.zoneId}
              className="p-3 rounded-lg border-2"
              style={{ borderColor: zone.color }}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: zone.color }}
                />
                <h5 className="font-semibold text-sm">
                  {zone.zoneName} | {zone.zoneNameAr}
                </h5>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <p>NDVI: {zone.ndviMin.toFixed(2)} - {zone.ndviMax.toFixed(2)}</p>
                <p>Area: {zone.areaHa.toFixed(2)} ha ({zone.percentage.toFixed(1)}%)</p>
                <p className="font-medium text-green-700">
                  Rate: {zone.recommendedRate.toFixed(2)} {zone.unit}
                </p>
                <p>Total: {zone.totalProduct.toFixed(2)} {zone.unit}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default PrescriptionMap;
