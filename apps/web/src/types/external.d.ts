/**
 * Type declarations for external modules
 */

// maplibre-gl types
declare module 'maplibre-gl' {
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
    on(event: string, layer: string, callback: (e: MapMouseEvent) => void): this;
    off(event: string, callback?: (e: MapMouseEvent) => void): this;
    remove(): void;
    addControl(control: NavigationControl | GeolocateControl, position?: string): this;
    addSource(id: string, source: any): this;
    addLayer(layer: any): this;
    getSource(id: string): any;
    removeSource(id: string): this;
    getLayer(id: string): any;
    removeLayer(id: string): this;
    setStyle(style: string | object): this;
    flyTo(options: any): this;
    fitBounds(bounds: LngLatBounds | [[number, number], [number, number]], options?: any): this;
    getCanvas(): HTMLCanvasElement;
    getBounds(): LngLatBounds;
    project(lngLat: any): { x: number; y: number };
    unproject(point: any): LngLat;
  }

  export class NavigationControl {
    constructor(options?: { showCompass?: boolean; showZoom?: boolean; visualizePitch?: boolean });
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
    constructor(options?: { closeButton?: boolean; closeOnClick?: boolean; offset?: number | [number, number] });
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

// SWR types
declare module 'swr' {
  export interface SWRConfiguration<Data = any, Error = any> {
    revalidateOnFocus?: boolean;
    revalidateOnReconnect?: boolean;
    refreshInterval?: number;
    refreshWhenHidden?: boolean;
    refreshWhenOffline?: boolean;
    dedupingInterval?: number;
    focusThrottleInterval?: number;
    loadingTimeout?: number;
    errorRetryInterval?: number;
    errorRetryCount?: number;
    fallbackData?: Data;
    suspense?: boolean;
    onSuccess?: (data: Data, key: string, config: SWRConfiguration<Data, Error>) => void;
    onError?: (err: Error, key: string, config: SWRConfiguration<Data, Error>) => void;
    [key: string]: any;
  }

  export interface SWRResponse<Data = any, Error = any> {
    data?: Data;
    error?: Error;
    isLoading: boolean;
    isValidating: boolean;
    mutate: (data?: Data | Promise<Data>, shouldRevalidate?: boolean) => Promise<Data | undefined>;
  }

  export default function useSWR<Data = any, Error = any>(
    key: string | (string | number)[] | null | undefined,
    fetcher?: ((...args: any[]) => Promise<Data>) | null,
    options?: SWRConfiguration<Data, Error>
  ): SWRResponse<Data, Error>;

  export { SWRConfiguration, SWRResponse };
}
