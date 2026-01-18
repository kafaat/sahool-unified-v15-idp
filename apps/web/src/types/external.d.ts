/**
 * Type declarations for external modules
 */

// ═══════════════════════════════════════════════════════════════════════════
// react-leaflet types fix for React 19 compatibility
// إصلاح أنواع react-leaflet للتوافق مع React 19
// ═══════════════════════════════════════════════════════════════════════════
import type { ReactNode } from "react";

declare module "react-leaflet" {
  import type { LatLngExpression, MapOptions as LeafletMapOptions } from "leaflet";

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
// maplibre-gl types
// ═══════════════════════════════════════════════════════════════════════════
declare module "maplibre-gl" {
  export interface MapOptions {
    container: string | HTMLElement;
    style: string | object;
    center?: [number, number];
    zoom?: number;
    minZoom?: number;
    maxZoom?: number;
    bearing?: number;
    pitch?: number;
    attributionControl?: boolean;
    [key: string]: any;
  }

  export interface MapMouseEvent {
    lngLat: LngLat;
    point: { x: number; y: number };
    features?: any[];
    target: Map;
    originalEvent: MouseEvent;
  }

  export interface LngLat {
    lng: number;
    lat: number;
    wrap(): LngLat;
    toArray(): [number, number];
  }

  export class LngLatBounds {
    constructor(sw?: [number, number] | LngLat, ne?: [number, number] | LngLat);
    extend(point: [number, number] | LngLat): this;
    getCenter(): LngLat;
    getSouthWest(): LngLat;
    getNorthEast(): LngLat;
    toArray(): [[number, number], [number, number]];
  }

  export class Map {
    constructor(options: MapOptions);
    on(event: string, callback: (e: MapMouseEvent) => void): this;
    on(
      event: string,
      layer: string,
      callback: (e: MapMouseEvent) => void,
    ): this;
    off(event: string, callback?: (e: MapMouseEvent) => void): this;
    remove(): void;
    addControl(
      control: NavigationControl | GeolocateControl,
      position?: string,
    ): this;
    addSource(id: string, source: any): this;
    addLayer(layer: any): this;
    getSource(id: string): any;
    removeSource(id: string): this;
    getLayer(id: string): any;
    removeLayer(id: string): this;
    setStyle(style: string | object): this;
    flyTo(options: any): this;
    fitBounds(
      bounds: LngLatBounds | [[number, number], [number, number]],
      options?: any,
    ): this;
    getCanvas(): HTMLCanvasElement;
    getBounds(): LngLatBounds;
    project(lngLat: any): { x: number; y: number };
    unproject(point: any): LngLat;
  }

  export class NavigationControl {
    constructor(options?: {
      showCompass?: boolean;
      showZoom?: boolean;
      visualizePitch?: boolean;
    });
  }

  export class GeolocateControl {
    constructor(options?: any);
  }

  export class Marker {
    constructor(options?: { color?: string; element?: HTMLElement });
    setLngLat(lngLat: [number, number] | LngLat): this;
    addTo(map: Map): this;
    remove(): this;
    setPopup(popup: Popup): this;
    getElement(): HTMLElement;
  }

  export class Popup {
    constructor(options?: {
      closeButton?: boolean;
      closeOnClick?: boolean;
      offset?: number | [number, number];
    });
    setLngLat(lngLat: [number, number] | LngLat): this;
    setHTML(html: string): this;
    addTo(map: Map): this;
    remove(): this;
  }

  const maplibregl: {
    Map: typeof Map;
    Marker: typeof Marker;
    Popup: typeof Popup;
    NavigationControl: typeof NavigationControl;
    GeolocateControl: typeof GeolocateControl;
    LngLatBounds: typeof LngLatBounds;
  };

  export default maplibregl;
}
