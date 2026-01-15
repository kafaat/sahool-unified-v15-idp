// Type declaration for leaflet module
declare module "leaflet" {
  // ============================================================================
  // Core Types
  // ============================================================================

  export type LatLngTuple = [number, number];
  export type LatLngBoundsLiteral = [LatLngTuple, LatLngTuple];
  export type PointTuple = [number, number];

  export interface LatLng {
    lat: number;
    lng: number;
    alt?: number;
    equals(otherLatLng: LatLngExpression, maxMargin?: number): boolean;
    toString(): string;
    distanceTo(otherLatLng: LatLngExpression): number;
    wrap(): LatLng;
    toBounds(sizeInMeters: number): LatLngBounds;
  }

  export type LatLngExpression = LatLng | LatLngTuple | { lat: number; lng: number };

  export interface LatLngBounds {
    extend(latlng: LatLngExpression | LatLngBounds): this;
    getSouthWest(): LatLng;
    getNorthEast(): LatLng;
    getNorthWest(): LatLng;
    getSouthEast(): LatLng;
    getWest(): number;
    getSouth(): number;
    getEast(): number;
    getNorth(): number;
    getCenter(): LatLng;
    contains(otherBounds: LatLngBounds | LatLngExpression): boolean;
    intersects(otherBounds: LatLngBounds): boolean;
    overlaps(otherBounds: LatLngBounds): boolean;
    toBBoxString(): string;
    equals(otherBounds: LatLngBounds, maxMargin?: number): boolean;
    isValid(): boolean;
    pad(bufferRatio: number): LatLngBounds;
  }

  export interface Point {
    x: number;
    y: number;
    add(otherPoint: Point): Point;
    subtract(otherPoint: Point): Point;
    divideBy(num: number): Point;
    multiplyBy(num: number): Point;
    scaleBy(scale: Point): Point;
    unscaleBy(scale: Point): Point;
    round(): Point;
    floor(): Point;
    ceil(): Point;
    trunc(): Point;
    distanceTo(otherPoint: Point): number;
    equals(otherPoint: Point): boolean;
    contains(otherPoint: Point): boolean;
    toString(): string;
  }

  // ============================================================================
  // Event Types
  // ============================================================================

  export interface LeafletEvent {
    type: string;
    target: Layer | Map;
    sourceTarget: Layer | Map;
    propagatedFrom: Layer | Map;
  }

  export interface LeafletMouseEvent extends LeafletEvent {
    latlng: LatLng;
    layerPoint: Point;
    containerPoint: Point;
    originalEvent: MouseEvent;
  }

  export interface LeafletKeyboardEvent extends LeafletEvent {
    originalEvent: KeyboardEvent;
  }

  export interface LocationEvent extends LeafletEvent {
    latlng: LatLng;
    bounds: LatLngBounds;
    accuracy: number;
    altitude: number | null;
    altitudeAccuracy: number | null;
    heading: number | null;
    speed: number | null;
    timestamp: number;
  }

  export interface ErrorEvent extends LeafletEvent {
    message: string;
    code: number;
  }

  export interface LayerEvent extends LeafletEvent {
    layer: Layer;
  }

  export interface ZoomAnimEvent extends LeafletEvent {
    center: LatLng;
    zoom: number;
    noUpdate?: boolean;
  }

  export interface DragEndEvent extends LeafletEvent {
    distance: number;
  }

  export interface ResizeEvent extends LeafletEvent {
    oldSize: Point;
    newSize: Point;
  }

  export interface PopupEvent extends LeafletEvent {
    popup: Popup;
  }

  export interface TooltipEvent extends LeafletEvent {
    tooltip: Tooltip;
  }

  export type LeafletEventHandlerFn = (event: LeafletEvent) => void;
  export type LeafletMouseEventHandlerFn = (event: LeafletMouseEvent) => void;

  // ============================================================================
  // Base Classes
  // ============================================================================

  export interface Evented {
    on(type: string, fn: LeafletEventHandlerFn, context?: object): this;
    on(eventMap: { [type: string]: LeafletEventHandlerFn }): this;
    off(type?: string, fn?: LeafletEventHandlerFn, context?: object): this;
    fire(type: string, data?: object, propagate?: boolean): this;
    listens(type: string): boolean;
    once(type: string, fn: LeafletEventHandlerFn, context?: object): this;
    addEventParent(obj: Evented): this;
    removeEventParent(obj: Evented): this;
    addEventListener(type: string, fn: LeafletEventHandlerFn, context?: object): this;
    removeEventListener(type?: string, fn?: LeafletEventHandlerFn, context?: object): this;
    clearAllEventListeners(): this;
    addOneTimeEventListener(type: string, fn: LeafletEventHandlerFn, context?: object): this;
    fireEvent(type: string, data?: object, propagate?: boolean): this;
    hasEventListeners(type: string): boolean;
  }

  // ============================================================================
  // Layer Types
  // ============================================================================

  export interface LayerOptions {
    pane?: string;
    attribution?: string;
  }

  export interface Layer extends Evented {
    addTo(map: Map | LayerGroup): this;
    remove(): this;
    removeFrom(map: Map): this;
    getPane(name?: string): HTMLElement | undefined;
    getAttribution(): string | null;
    bindPopup(content: string | HTMLElement | Popup | ((layer: Layer) => string | HTMLElement), options?: PopupOptions): this;
    unbindPopup(): this;
    openPopup(latlng?: LatLngExpression): this;
    closePopup(): this;
    togglePopup(): this;
    isPopupOpen(): boolean;
    setPopupContent(content: string | HTMLElement | Popup): this;
    getPopup(): Popup | undefined;
    bindTooltip(content: string | HTMLElement | Tooltip | ((layer: Layer) => string | HTMLElement), options?: TooltipOptions): this;
    unbindTooltip(): this;
    openTooltip(latlng?: LatLngExpression): this;
    closeTooltip(): this;
    toggleTooltip(): this;
    isTooltipOpen(): boolean;
    setTooltipContent(content: string | HTMLElement | Tooltip): this;
    getTooltip(): Tooltip | undefined;
  }

  // ============================================================================
  // Interactive Layer
  // ============================================================================

  export interface InteractiveLayerOptions extends LayerOptions {
    interactive?: boolean;
    bubblingMouseEvents?: boolean;
  }

  // ============================================================================
  // Marker Types
  // ============================================================================

  export interface IconOptions {
    iconUrl?: string;
    iconRetinaUrl?: string;
    iconSize?: PointTuple;
    iconAnchor?: PointTuple;
    popupAnchor?: PointTuple;
    tooltipAnchor?: PointTuple;
    shadowUrl?: string;
    shadowRetinaUrl?: string;
    shadowSize?: PointTuple;
    shadowAnchor?: PointTuple;
    className?: string;
    crossOrigin?: boolean | string;
  }

  export interface Icon<T extends IconOptions = IconOptions> {
    options: T;
    createIcon(oldIcon?: HTMLElement): HTMLElement;
    createShadow(oldIcon?: HTMLElement): HTMLElement;
  }

  export interface DivIconOptions extends IconOptions {
    html?: string | HTMLElement | false;
    bgPos?: PointTuple;
  }

  export interface DivIcon extends Icon<DivIconOptions> {}

  export interface MarkerOptions extends InteractiveLayerOptions {
    icon?: Icon;
    keyboard?: boolean;
    title?: string;
    alt?: string;
    zIndexOffset?: number;
    opacity?: number;
    riseOnHover?: boolean;
    riseOffset?: number;
    draggable?: boolean;
    autoPan?: boolean;
    autoPanPadding?: PointTuple;
    autoPanSpeed?: number;
  }

  export interface Marker<P = object> extends Layer {
    toGeoJSON(precision?: number): GeoJSON.Feature<GeoJSON.Point, P>;
    getLatLng(): LatLng;
    setLatLng(latlng: LatLngExpression): this;
    setZIndexOffset(offset: number): this;
    getIcon(): Icon;
    setIcon(icon: Icon): this;
    setOpacity(opacity: number): this;
    getElement(): HTMLElement | undefined;
  }

  // ============================================================================
  // Path Types (for shapes)
  // ============================================================================

  export interface PathOptions extends InteractiveLayerOptions {
    stroke?: boolean;
    color?: string;
    weight?: number;
    opacity?: number;
    lineCap?: "butt" | "round" | "square";
    lineJoin?: "arcs" | "bevel" | "miter" | "miter-clip" | "round";
    dashArray?: string | number[];
    dashOffset?: string;
    fill?: boolean;
    fillColor?: string;
    fillOpacity?: number;
    fillRule?: "nonzero" | "evenodd";
    className?: string;
  }

  export interface Path extends Layer {
    redraw(): this;
    setStyle(style: PathOptions): this;
    bringToFront(): this;
    bringToBack(): this;
  }

  // ============================================================================
  // Polyline Types
  // ============================================================================

  export interface PolylineOptions extends PathOptions {
    smoothFactor?: number;
    noClip?: boolean;
  }

  export interface Polyline<T extends GeoJSON.GeometryObject = GeoJSON.LineString | GeoJSON.MultiLineString, P = object> extends Path {
    toGeoJSON(precision?: number): GeoJSON.Feature<T, P>;
    getLatLngs(): LatLng[] | LatLng[][] | LatLng[][][];
    setLatLngs(latlngs: LatLngExpression[] | LatLngExpression[][] | LatLngExpression[][][]): this;
    isEmpty(): boolean;
    closestLayerPoint(p: Point): Point;
    getCenter(): LatLng;
    getBounds(): LatLngBounds;
    addLatLng(latlng: LatLngExpression | LatLngExpression[], latlngs?: LatLng[]): this;
  }

  // ============================================================================
  // Polygon Types
  // ============================================================================

  export interface Polygon<P = object> extends Polyline<GeoJSON.Polygon | GeoJSON.MultiPolygon, P> {}

  // ============================================================================
  // Circle Types
  // ============================================================================

  export interface CircleMarkerOptions extends PathOptions {
    radius?: number;
  }

  export interface CircleMarker<P = object> extends Path {
    toGeoJSON(precision?: number): GeoJSON.Feature<GeoJSON.Point, P>;
    setLatLng(latlng: LatLngExpression): this;
    getLatLng(): LatLng;
    setRadius(radius: number): this;
    getRadius(): number;
  }

  export interface CircleOptions extends CircleMarkerOptions {}

  export interface Circle<P = object> extends CircleMarker<P> {
    setRadius(radius: number): this;
    getRadius(): number;
    getBounds(): LatLngBounds;
  }

  // ============================================================================
  // Rectangle Types
  // ============================================================================

  export interface Rectangle<P = object> extends Polygon<P> {
    setBounds(latLngBounds: LatLngBounds | LatLngBoundsLiteral): this;
  }

  // ============================================================================
  // Popup and Tooltip Types
  // ============================================================================

  export interface PopupOptions extends DivOverlayOptions {
    maxWidth?: number;
    minWidth?: number;
    maxHeight?: number;
    autoPan?: boolean;
    autoPanPaddingTopLeft?: PointTuple;
    autoPanPaddingBottomRight?: PointTuple;
    autoPanPadding?: PointTuple;
    keepInView?: boolean;
    closeButton?: boolean;
    autoClose?: boolean;
    closeOnEscapeKey?: boolean;
    closeOnClick?: boolean;
  }

  export interface DivOverlayOptions {
    offset?: PointTuple;
    className?: string;
    pane?: string;
    content?: string | HTMLElement | ((layer: Layer) => string | HTMLElement);
  }

  export interface Popup extends Layer {
    getLatLng(): LatLng | undefined;
    setLatLng(latlng: LatLngExpression): this;
    getContent(): string | HTMLElement | ((layer: Layer) => string | HTMLElement) | undefined;
    setContent(htmlContent: string | HTMLElement | ((layer: Layer) => string | HTMLElement)): this;
    getElement(): HTMLElement | undefined;
    update(): void;
    isOpen(): boolean;
    bringToFront(): this;
    bringToBack(): this;
    openOn(map: Map): this;
  }

  export interface TooltipOptions extends DivOverlayOptions {
    direction?: "right" | "left" | "top" | "bottom" | "center" | "auto";
    permanent?: boolean;
    sticky?: boolean;
    opacity?: number;
  }

  export interface Tooltip extends Layer {
    getLatLng(): LatLng | undefined;
    setLatLng(latlng: LatLngExpression): this;
    getContent(): string | HTMLElement | ((layer: Layer) => string | HTMLElement) | undefined;
    setContent(htmlContent: string | HTMLElement | ((layer: Layer) => string | HTMLElement)): this;
    getElement(): HTMLElement | undefined;
    update(): void;
    isOpen(): boolean;
    bringToFront(): this;
    bringToBack(): this;
  }

  // ============================================================================
  // Layer Groups
  // ============================================================================

  export interface LayerGroup<P = object> extends Layer {
    toGeoJSON(precision?: number): GeoJSON.FeatureCollection<GeoJSON.GeometryObject, P> | GeoJSON.Feature<GeoJSON.MultiPoint, P> | GeoJSON.GeometryCollection;
    addLayer(layer: Layer): this;
    removeLayer(layer: Layer | number): this;
    hasLayer(layer: Layer | number): boolean;
    clearLayers(): this;
    invoke(methodName: string, ...params: unknown[]): this;
    eachLayer(fn: (layer: Layer) => void, context?: object): this;
    getLayer(id: number): Layer | undefined;
    getLayers(): Layer[];
    setZIndex(zIndex: number): this;
    getLayerId(layer: Layer): number;
  }

  export interface FeatureGroup<P = object> extends LayerGroup<P> {
    setStyle(style: PathOptions): this;
    bringToFront(): this;
    bringToBack(): this;
    getBounds(): LatLngBounds;
  }

  export interface GeoJSONOptions<P = object, G extends GeoJSON.GeometryObject = GeoJSON.GeometryObject> extends InteractiveLayerOptions {
    pointToLayer?: (geoJsonPoint: GeoJSON.Feature<GeoJSON.Point, P>, latlng: LatLng) => Layer;
    style?: PathOptions | ((geoJsonFeature: GeoJSON.Feature<G, P>) => PathOptions);
    onEachFeature?: (feature: GeoJSON.Feature<G, P>, layer: Layer) => void;
    filter?: (geoJsonFeature: GeoJSON.Feature<G, P>) => boolean;
    coordsToLatLng?: (coords: [number, number] | [number, number, number]) => LatLng;
    markersInheritOptions?: boolean;
  }

  export interface GeoJSON<P = object, G extends GeoJSON.GeometryObject = GeoJSON.GeometryObject> extends FeatureGroup<P> {
    addData(data: GeoJSON.GeoJsonObject): this;
    resetStyle(layer?: Layer): this;
    setStyle(style: PathOptions | ((feature: GeoJSON.Feature<G, P>) => PathOptions)): this;
  }

  // ============================================================================
  // Tile Layer Types
  // ============================================================================

  export interface TileLayerOptions extends LayerOptions {
    minZoom?: number;
    maxZoom?: number;
    subdomains?: string | string[];
    errorTileUrl?: string;
    zoomOffset?: number;
    tms?: boolean;
    zoomReverse?: boolean;
    detectRetina?: boolean;
    crossOrigin?: boolean | string;
    referrerPolicy?: boolean | string;
    tileSize?: number | Point;
    opacity?: number;
    updateWhenIdle?: boolean;
    updateWhenZooming?: boolean;
    updateInterval?: number;
    bounds?: LatLngBounds | LatLngBoundsLiteral;
    maxNativeZoom?: number;
    minNativeZoom?: number;
    noWrap?: boolean;
    className?: string;
    keepBuffer?: number;
  }

  export interface TileLayer extends Layer {
    setUrl(url: string, noRedraw?: boolean): this;
    createTile(coords: { x: number; y: number; z: number }, done: (error: Error | null, tile: HTMLElement) => void): HTMLElement;
    getTileUrl(coords: { x: number; y: number; z: number }): string;
    getTileSize(): Point;
    bringToFront(): this;
    bringToBack(): this;
    getContainer(): HTMLElement | null;
    setOpacity(opacity: number): this;
    setZIndex(zIndex: number): this;
    isLoading(): boolean;
    redraw(): this;
  }

  export interface WMSOptions extends TileLayerOptions {
    layers?: string;
    styles?: string;
    format?: string;
    transparent?: boolean;
    version?: string;
    crs?: CRS;
    uppercase?: boolean;
  }

  export interface WMS extends TileLayer {
    setParams(params: WMSOptions, noRedraw?: boolean): this;
  }

  // ============================================================================
  // Map Types
  // ============================================================================

  export interface MapOptions {
    preferCanvas?: boolean;
    attributionControl?: boolean;
    zoomControl?: boolean;
    closePopupOnClick?: boolean;
    zoomSnap?: number;
    zoomDelta?: number;
    trackResize?: boolean;
    boxZoom?: boolean;
    doubleClickZoom?: boolean | "center";
    dragging?: boolean;
    crs?: CRS;
    center?: LatLngExpression;
    zoom?: number;
    minZoom?: number;
    maxZoom?: number;
    layers?: Layer[];
    maxBounds?: LatLngBounds | LatLngBoundsLiteral;
    renderer?: Renderer;
    fadeAnimation?: boolean;
    markerZoomAnimation?: boolean;
    transform3DLimit?: number;
    zoomAnimation?: boolean;
    zoomAnimationThreshold?: number;
    inertia?: boolean;
    inertiaDeceleration?: number;
    inertiaMaxSpeed?: number;
    easeLinearity?: number;
    worldCopyJump?: boolean;
    maxBoundsViscosity?: number;
    keyboard?: boolean;
    keyboardPanDelta?: number;
    scrollWheelZoom?: boolean | "center";
    wheelDebounceTime?: number;
    wheelPxPerZoomLevel?: number;
    tapHold?: boolean;
    tapTolerance?: number;
    touchZoom?: boolean | "center";
    bounceAtZoomLimits?: boolean;
  }

  export interface FitBoundsOptions extends ZoomPanOptions {
    paddingTopLeft?: PointTuple;
    paddingBottomRight?: PointTuple;
    padding?: PointTuple;
    maxZoom?: number;
  }

  export interface ZoomPanOptions {
    animate?: boolean;
    duration?: number;
    easeLinearity?: number;
    noMoveStart?: boolean;
  }

  export interface PanOptions extends ZoomPanOptions {}

  export interface ZoomOptions extends ZoomPanOptions {}

  export interface LocateOptions {
    watch?: boolean;
    setView?: boolean;
    maxZoom?: number;
    timeout?: number;
    maximumAge?: number;
    enableHighAccuracy?: boolean;
  }

  export interface Map extends Evented {
    // Methods for Layers and Controls
    addControl(control: Control): this;
    removeControl(control: Control): this;
    addLayer(layer: Layer): this;
    removeLayer(layer: Layer): this;
    hasLayer(layer: Layer): boolean;
    eachLayer(fn: (layer: Layer) => void, context?: object): this;
    openPopup(popup: Popup): this;
    openPopup(content: string | HTMLElement, latlng: LatLngExpression, options?: PopupOptions): this;
    closePopup(popup?: Popup): this;
    openTooltip(tooltip: Tooltip): this;
    openTooltip(content: string | HTMLElement, latlng: LatLngExpression, options?: TooltipOptions): this;
    closeTooltip(tooltip?: Tooltip): this;

    // Methods for modifying map state
    setView(center: LatLngExpression, zoom?: number, options?: ZoomPanOptions): this;
    setZoom(zoom: number, options?: ZoomPanOptions): this;
    zoomIn(delta?: number, options?: ZoomOptions): this;
    zoomOut(delta?: number, options?: ZoomOptions): this;
    setZoomAround(position: LatLngExpression | Point, zoom: number, options?: ZoomOptions): this;
    fitBounds(bounds: LatLngBounds | LatLngBoundsLiteral, options?: FitBoundsOptions): this;
    fitWorld(options?: FitBoundsOptions): this;
    panTo(latlng: LatLngExpression, options?: PanOptions): this;
    panBy(offset: PointTuple, options?: PanOptions): this;
    flyTo(latlng: LatLngExpression, zoom?: number, options?: ZoomPanOptions): this;
    flyToBounds(bounds: LatLngBounds | LatLngBoundsLiteral, options?: FitBoundsOptions): this;
    setMaxBounds(bounds: LatLngBounds | LatLngBoundsLiteral | null): this;
    setMinZoom(zoom: number): this;
    setMaxZoom(zoom: number): this;
    panInsideBounds(bounds: LatLngBounds | LatLngBoundsLiteral, options?: PanOptions): this;
    panInside(latlng: LatLngExpression, options?: { paddingTopLeft?: PointTuple; paddingBottomRight?: PointTuple; padding?: PointTuple }): this;
    invalidateSize(options?: boolean | { animate?: boolean; pan?: boolean; debounceMoveend?: boolean }): this;
    stop(): this;
    locate(options?: LocateOptions): this;
    stopLocate(): this;

    // Methods for getting map state
    getCenter(): LatLng;
    getZoom(): number;
    getBounds(): LatLngBounds;
    getMinZoom(): number;
    getMaxZoom(): number;
    getBoundsZoom(bounds: LatLngBounds | LatLngBoundsLiteral, inside?: boolean, padding?: PointTuple): number;
    getSize(): Point;
    getPixelBounds(): { min: Point; max: Point };
    getPixelOrigin(): Point;
    getPixelWorldBounds(zoom?: number): { min: Point; max: Point };

    // Conversion methods
    getContainer(): HTMLElement;
    getPane(name: string): HTMLElement | undefined;
    getPanes(): { [name: string]: HTMLElement };
    createPane(name: string, container?: HTMLElement): HTMLElement;
    project(latlng: LatLngExpression, zoom?: number): Point;
    unproject(point: Point | PointTuple, zoom?: number): LatLng;
    layerPointToLatLng(point: Point | PointTuple): LatLng;
    latLngToLayerPoint(latlng: LatLngExpression): Point;
    wrapLatLng(latlng: LatLngExpression): LatLng;
    wrapLatLngBounds(bounds: LatLngBounds): LatLngBounds;
    distance(latlng1: LatLngExpression, latlng2: LatLngExpression): number;
    containerPointToLayerPoint(point: Point | PointTuple): Point;
    layerPointToContainerPoint(point: Point | PointTuple): Point;
    containerPointToLatLng(point: Point | PointTuple): LatLng;
    latLngToContainerPoint(latlng: LatLngExpression): Point;
    mouseEventToContainerPoint(event: MouseEvent): Point;
    mouseEventToLayerPoint(event: MouseEvent): Point;
    mouseEventToLatLng(event: MouseEvent): LatLng;

    // Other methods
    remove(): this;
    whenReady(fn: () => void, context?: object): this;

    // Properties
    options: MapOptions;
    dragging: Handler;
    touchZoom: Handler;
    doubleClickZoom: Handler;
    scrollWheelZoom: Handler;
    boxZoom: Handler;
    keyboard: Handler;
    tap?: Handler;
    zoomControl?: Control.Zoom;
    attributionControl?: Control.Attribution;
  }

  // ============================================================================
  // Control Types
  // ============================================================================

  export interface ControlOptions {
    position?: "topleft" | "topright" | "bottomleft" | "bottomright";
  }

  export interface Control extends Evented {
    getPosition(): string;
    setPosition(position: "topleft" | "topright" | "bottomleft" | "bottomright"): this;
    getContainer(): HTMLElement | undefined;
    addTo(map: Map): this;
    remove(): this;
  }

  export namespace Control {
    interface ZoomOptions extends ControlOptions {
      zoomInText?: string;
      zoomInTitle?: string;
      zoomOutText?: string;
      zoomOutTitle?: string;
    }

    interface Zoom extends Control {}

    interface AttributionOptions extends ControlOptions {
      prefix?: string | false;
    }

    interface Attribution extends Control {
      setPrefix(prefix: string | false): this;
      addAttribution(text: string): this;
      removeAttribution(text: string): this;
    }

    interface LayersOptions extends ControlOptions {
      collapsed?: boolean;
      autoZIndex?: boolean;
      hideSingleBase?: boolean;
      sortLayers?: boolean;
      sortFunction?: (layerA: Layer, layerB: Layer, nameA: string, nameB: string) => number;
    }

    interface Layers extends Control {
      addBaseLayer(layer: Layer, name: string): this;
      addOverlay(layer: Layer, name: string): this;
      removeLayer(layer: Layer): this;
      expand(): this;
      collapse(): this;
    }

    interface ScaleOptions extends ControlOptions {
      maxWidth?: number;
      metric?: boolean;
      imperial?: boolean;
      updateWhenIdle?: boolean;
    }

    interface Scale extends Control {}
  }

  export const control: {
    (options?: ControlOptions): Control;
    zoom(options?: Control.ZoomOptions): Control.Zoom;
    attribution(options?: Control.AttributionOptions): Control.Attribution;
    layers(baseLayers?: { [name: string]: Layer }, overlays?: { [name: string]: Layer }, options?: Control.LayersOptions): Control.Layers;
    scale(options?: Control.ScaleOptions): Control.Scale;
  };

  // ============================================================================
  // CRS Types
  // ============================================================================

  export interface CRS {
    latLngToPoint(latlng: LatLngExpression, zoom: number): Point;
    pointToLatLng(point: Point | PointTuple, zoom: number): LatLng;
    project(latlng: LatLngExpression): Point;
    unproject(point: Point | PointTuple): LatLng;
    scale(zoom: number): number;
    zoom(scale: number): number;
    getProjectedBounds(zoom: number): { min: Point; max: Point };
    distance(latlng1: LatLngExpression, latlng2: LatLngExpression): number;
    wrapLatLng(latlng: LatLngExpression): LatLng;
    wrapLatLngBounds(bounds: LatLngBounds): LatLngBounds;
    code?: string;
    wrapLng?: [number, number];
    wrapLat?: [number, number];
    infinite: boolean;
  }

  export namespace CRS {
    const EPSG3395: CRS;
    const EPSG3857: CRS;
    const EPSG4326: CRS;
    const Earth: CRS;
    const Simple: CRS;
    const Base: CRS;
  }

  // ============================================================================
  // Renderer Types
  // ============================================================================

  export interface RendererOptions extends LayerOptions {
    padding?: number;
    tolerance?: number;
  }

  export interface Renderer extends Layer {}

  export interface Canvas extends Renderer {}
  export interface SVG extends Renderer {}

  // ============================================================================
  // Handler Types
  // ============================================================================

  export interface Handler {
    enable(): this;
    disable(): this;
    enabled(): boolean;
  }

  // ============================================================================
  // ImageOverlay Types
  // ============================================================================

  export interface ImageOverlayOptions extends InteractiveLayerOptions {
    opacity?: number;
    alt?: string;
    crossOrigin?: boolean | string;
    errorOverlayUrl?: string;
    zIndex?: number;
    className?: string;
  }

  export interface ImageOverlay extends Layer {
    setOpacity(opacity: number): this;
    bringToFront(): this;
    bringToBack(): this;
    setUrl(url: string): this;
    setBounds(bounds: LatLngBounds | LatLngBoundsLiteral): this;
    setZIndex(value: number): this;
    getBounds(): LatLngBounds;
    getElement(): HTMLImageElement | undefined;
    getCenter(): LatLng;
  }

  export interface VideoOverlayOptions extends ImageOverlayOptions {
    autoplay?: boolean;
    loop?: boolean;
    keepAspectRatio?: boolean;
    muted?: boolean;
    playsInline?: boolean;
  }

  export interface VideoOverlay extends ImageOverlay {
    getElement(): HTMLVideoElement | undefined;
  }

  // ============================================================================
  // Factory Functions
  // ============================================================================

  export function latLng(latitude: number, longitude: number, altitude?: number): LatLng;
  export function latLng(coords: LatLngTuple | [number, number, number] | { lat: number; lng: number; alt?: number }): LatLng;

  export function latLngBounds(corner1: LatLngExpression, corner2: LatLngExpression): LatLngBounds;
  export function latLngBounds(latlngs: LatLngExpression[]): LatLngBounds;

  export function point(x: number, y: number, round?: boolean): Point;
  export function point(coords: PointTuple): Point;

  export function icon(options: IconOptions): Icon;
  export function divIcon(options?: DivIconOptions): DivIcon;

  export function map(element: HTMLElement | string, options?: MapOptions): Map;

  export function tileLayer(urlTemplate: string, options?: TileLayerOptions): TileLayer;

  export namespace tileLayer {
    function wms(baseUrl: string, options?: WMSOptions): WMS;
  }

  export function marker(latlng: LatLngExpression, options?: MarkerOptions): Marker;

  export function popup(options?: PopupOptions, source?: Layer): Popup;
  export function popup(latlng: LatLngExpression, options?: PopupOptions): Popup;

  export function tooltip(options?: TooltipOptions, source?: Layer): Tooltip;
  export function tooltip(latlng: LatLngExpression, options?: TooltipOptions): Tooltip;

  export function circleMarker(latlng: LatLngExpression, options?: CircleMarkerOptions): CircleMarker;

  export function circle(latlng: LatLngExpression, options?: CircleOptions): Circle;
  export function circle(latlng: LatLngExpression, radius: number, options?: CircleOptions): Circle;

  export function polyline(latlngs: LatLngExpression[] | LatLngExpression[][], options?: PolylineOptions): Polyline;

  export function polygon(latlngs: LatLngExpression[] | LatLngExpression[][] | LatLngExpression[][][], options?: PolylineOptions): Polygon;

  export function rectangle(bounds: LatLngBounds | LatLngBoundsLiteral, options?: PolylineOptions): Rectangle;

  export function layerGroup(layers?: Layer[], options?: LayerOptions): LayerGroup;

  export function featureGroup(layers?: Layer[], options?: LayerOptions): FeatureGroup;

  export function geoJSON<P = object, G extends GeoJSON.GeometryObject = GeoJSON.GeometryObject>(
    geojson?: GeoJSON.GeoJsonObject | GeoJSON.GeoJsonObject[] | null,
    options?: GeoJSONOptions<P, G>
  ): GeoJSON<P, G>;

  export function imageOverlay(imageUrl: string, bounds: LatLngBounds | LatLngBoundsLiteral, options?: ImageOverlayOptions): ImageOverlay;

  export function videoOverlay(video: string | string[] | HTMLVideoElement, bounds: LatLngBounds | LatLngBoundsLiteral, options?: VideoOverlayOptions): VideoOverlay;

  export function canvas(options?: RendererOptions): Canvas;

  export function svg(options?: RendererOptions): SVG;

  // ============================================================================
  // GeoJSON namespace (from @types/geojson)
  // ============================================================================

  namespace GeoJSON {
    type GeoJsonTypes = "Point" | "MultiPoint" | "LineString" | "MultiLineString" | "Polygon" | "MultiPolygon" | "GeometryCollection" | "Feature" | "FeatureCollection";

    interface GeoJsonObject {
      type: GeoJsonTypes;
      bbox?: [number, number, number, number] | [number, number, number, number, number, number];
    }

    type Position = [number, number] | [number, number, number];

    interface Point extends GeoJsonObject {
      type: "Point";
      coordinates: Position;
    }

    interface MultiPoint extends GeoJsonObject {
      type: "MultiPoint";
      coordinates: Position[];
    }

    interface LineString extends GeoJsonObject {
      type: "LineString";
      coordinates: Position[];
    }

    interface MultiLineString extends GeoJsonObject {
      type: "MultiLineString";
      coordinates: Position[][];
    }

    interface Polygon extends GeoJsonObject {
      type: "Polygon";
      coordinates: Position[][];
    }

    interface MultiPolygon extends GeoJsonObject {
      type: "MultiPolygon";
      coordinates: Position[][][];
    }

    type GeometryObject = Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon | GeometryCollection;

    interface GeometryCollection extends GeoJsonObject {
      type: "GeometryCollection";
      geometries: GeometryObject[];
    }

    interface Feature<G extends GeometryObject = GeometryObject, P = object> extends GeoJsonObject {
      type: "Feature";
      geometry: G;
      id?: string | number;
      properties: P;
    }

    interface FeatureCollection<G extends GeometryObject = GeometryObject, P = object> extends GeoJsonObject {
      type: "FeatureCollection";
      features: Feature<G, P>[];
    }
  }

  // ============================================================================
  // Utility Types
  // ============================================================================

  export const version: string;

  export function noConflict(): typeof L;

  // ============================================================================
  // Default Export
  // ============================================================================

  const L: {
    version: string;
    noConflict: typeof noConflict;
    latLng: typeof latLng;
    latLngBounds: typeof latLngBounds;
    point: typeof point;
    icon: typeof icon;
    divIcon: typeof divIcon;
    map: typeof map;
    tileLayer: typeof tileLayer;
    marker: typeof marker;
    popup: typeof popup;
    tooltip: typeof tooltip;
    circleMarker: typeof circleMarker;
    circle: typeof circle;
    polyline: typeof polyline;
    polygon: typeof polygon;
    rectangle: typeof rectangle;
    layerGroup: typeof layerGroup;
    featureGroup: typeof featureGroup;
    geoJSON: typeof geoJSON;
    imageOverlay: typeof imageOverlay;
    videoOverlay: typeof videoOverlay;
    canvas: typeof canvas;
    svg: typeof svg;
    control: typeof control;
    Control: typeof Control;
    CRS: typeof CRS;
    LatLng: typeof LatLng;
    LatLngBounds: typeof LatLngBounds;
    Point: typeof Point;
    Icon: typeof Icon;
    DivIcon: typeof DivIcon;
    Marker: typeof Marker;
    TileLayer: typeof TileLayer;
    Popup: typeof Popup;
    Tooltip: typeof Tooltip;
    CircleMarker: typeof CircleMarker;
    Circle: typeof Circle;
    Polyline: typeof Polyline;
    Polygon: typeof Polygon;
    Rectangle: typeof Rectangle;
    Path: typeof Path;
    LayerGroup: typeof LayerGroup;
    FeatureGroup: typeof FeatureGroup;
    GeoJSON: typeof GeoJSON;
    ImageOverlay: typeof ImageOverlay;
    VideoOverlay: typeof VideoOverlay;
    Canvas: typeof Canvas;
    SVG: typeof SVG;
    Renderer: typeof Renderer;
    Handler: typeof Handler;
    Evented: typeof Evented;
    Layer: typeof Layer;
    Map: typeof Map;
  };
  export default L;
}
