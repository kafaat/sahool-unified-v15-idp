/**
 * Type declarations for external modules
 */

// ═══════════════════════════════════════════════════════════════════════════
// react-leaflet types fix for React 19 compatibility
// إصلاح أنواع react-leaflet للتوافق مع React 19
// ═══════════════════════════════════════════════════════════════════════════
import type { ReactNode } from "react";

declare module "react-leaflet" {
  import type {
    LatLngExpression,
    MapOptions as LeafletMapOptions,
  } from "leaflet";

  // Extend MapContainer props for React 19
  interface MapContainerProps extends Partial<LeafletMapOptions> {
    children?: ReactNode;
    center?: LatLngExpression;
    zoom?: number;
    zoomControl?: boolean;
    className?: string;
    style?: React.CSSProperties;
    whenReady?: () => void;
    whenCreated?: (map: L.Map) => void;
  }

  // Extend TileLayer props
  interface TileLayerProps {
    url: string;
    attribution?: string;
    children?: ReactNode;
  }

  // Extend LayersControl props
  interface LayersControlProps {
    position?: "topleft" | "topright" | "bottomleft" | "bottomright";
    children?: ReactNode;
  }

  // Extend BaseLayer props
  namespace LayersControl {
    interface BaseLayerProps {
      checked?: boolean;
      name: string;
      children?: ReactNode;
    }

    interface OverlayProps {
      checked?: boolean;
      name: string;
      children?: ReactNode;
    }
  }

  // Extend Marker props
  interface MarkerProps {
    position: LatLngExpression;
    icon?: L.Icon;
    children?: ReactNode;
    eventHandlers?: Record<string, (e: L.LeafletEvent) => void>;
  }

  // Extend Popup props
  interface PopupProps {
    children?: ReactNode;
  }

  // Extend Polygon props
  interface PolygonProps {
    positions: LatLngExpression[] | LatLngExpression[][];
    pathOptions?: L.PathOptions;
    children?: ReactNode;
    eventHandlers?: Record<string, (e: L.LeafletEvent) => void>;
  }

  // Extend Circle props
  interface CircleProps {
    center: LatLngExpression;
    radius: number;
    pathOptions?: L.PathOptions;
    children?: ReactNode;
  }

  // Extend GeoJSON props
  interface GeoJSONProps {
    data: GeoJSON.GeoJsonObject;
    style?: L.StyleFunction | L.PathOptions;
    onEachFeature?: (feature: GeoJSON.Feature, layer: L.Layer) => void;
    children?: ReactNode;
  }

  // Extend ZoomControl props
  interface ZoomControlProps {
    position?: "topleft" | "topright" | "bottomleft" | "bottomright";
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// maplibre-gl types - using library's own types
// Note: maplibre-gl has its own TypeScript definitions (@types/maplibre-gl)
// We only add minimal augmentations if needed, not full replacements
// ═══════════════════════════════════════════════════════════════════════════
