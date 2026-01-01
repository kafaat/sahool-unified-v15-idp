// Type declaration for leaflet module
declare module 'leaflet' {
  export interface MapOptions {
    center?: [number, number];
    zoom?: number;
    scrollWheelZoom?: boolean;
    [key: string]: any;
  }

  export interface Icon {
    iconUrl?: string;
    iconSize?: [number, number];
    iconAnchor?: [number, number];
    popupAnchor?: [number, number];
    [key: string]: any;
  }

  export interface LatLngExpression {
    lat: number;
    lng: number;
  }

  export function icon(options: Icon): any;
  export function map(element: HTMLElement | string, options?: MapOptions): any;
  export function tileLayer(urlTemplate: string, options?: any): any;
  export function marker(latlng: LatLngExpression | [number, number], options?: any): any;
  export function popup(options?: any): any;
  export function circleMarker(latlng: LatLngExpression | [number, number], options?: any): any;
  export function polyline(latlngs: Array<LatLngExpression | [number, number]>, options?: any): any;
  export function polygon(latlngs: Array<LatLngExpression | [number, number]>, options?: any): any;
  export const control: any;

  const L: any;
  export default L;
}
