import { Injectable } from '@nestjs/common';

// ═══════════════════════════════════════════════════════════════════════════════
// GIS Integration Service - خدمة تكامل نظم المعلومات الجغرافية
// Based on GeoSuite/QCarta patterns - GeoServer, PostGIS, OGC Services
// ═══════════════════════════════════════════════════════════════════════════════

// GeoJSON Feature types
export interface GeoJSONGeometry {
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon';
  coordinates: number[] | number[][] | number[][][] | number[][][][];
}

export interface GeoJSONFeature {
  type: 'Feature';
  id?: string | number;
  geometry: GeoJSONGeometry;
  properties: Record<string, any>;
  bbox?: number[];
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
  bbox?: number[];
  crs?: { type: string; properties: { name: string } };
}

// Layer configuration
export interface LayerConfig {
  id: string;
  name: string;
  nameAr: string;
  type: 'vector' | 'raster' | 'wms' | 'wmts';
  source: string;
  workspace?: string;
  style?: string;
  visible: boolean;
  opacity: number;
  minZoom?: number;
  maxZoom?: number;
  attribution?: string;
  metadata?: LayerMetadata;
}

export interface LayerMetadata {
  title: string;
  abstract: string;
  keywords: string[];
  contactInfo?: string;
  accessConstraints?: string;
  updateFrequency?: string;
  spatialExtent: BoundingBox;
  temporalExtent?: { start: string; end: string };
  dataQuality?: string;
}

export interface BoundingBox {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  srs: string;
}

// Field boundary management
export interface FieldBoundary {
  id: string;
  farmId: string;
  name: string;
  nameAr: string;
  geometry: GeoJSONGeometry;
  areaHectares: number;
  areaDunum: number;
  perimeter: number;
  centroid: { lat: number; lng: number };
  soilType?: string;
  irrigationType?: string;
  currentCrop?: string;
  plantingDate?: string;
  harvestDate?: string;
  ndviHistory?: { date: string; value: number }[];
  metadata?: Record<string, any>;
}

// Spatial query types
export interface SpatialQuery {
  operation: 'intersects' | 'contains' | 'within' | 'overlaps' | 'touches' | 'buffer' | 'union';
  geometry?: GeoJSONGeometry;
  distance?: number;
  unit?: 'meters' | 'kilometers' | 'miles';
  targetLayer?: string;
  properties?: string[];
}

export interface SpatialQueryResult {
  features: GeoJSONFeature[];
  count: number;
  bbox: BoundingBox;
  queryTime: number;
}

// OGC Service configurations
export interface WMSCapabilities {
  version: string;
  title: string;
  abstract: string;
  layers: WMSLayer[];
  formats: string[];
  srs: string[];
}

export interface WMSLayer {
  name: string;
  title: string;
  abstract: string;
  srs: string[];
  boundingBox: BoundingBox;
  styles: { name: string; title: string }[];
  queryable: boolean;
}

export interface WFSCapabilities {
  version: string;
  title: string;
  featureTypes: WFSFeatureType[];
  outputFormats: string[];
}

export interface WFSFeatureType {
  name: string;
  title: string;
  abstract: string;
  srs: string;
  boundingBox: BoundingBox;
  keywords: string[];
}

// Map project configuration
export interface MapProject {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  layers: LayerConfig[];
  basemap: string;
  center: { lat: number; lng: number };
  zoom: number;
  extent: BoundingBox;
  createdAt: Date;
  updatedAt: Date;
  owner: string;
  shared: boolean;
}

// Spatial statistics
export interface ZonalStatistics {
  zone: string;
  count: number;
  sum: number;
  mean: number;
  min: number;
  max: number;
  std: number;
  area: number;
}

// Routing (based on PgRouting)
export interface RouteRequest {
  origin: { lat: number; lng: number };
  destination: { lat: number; lng: number };
  waypoints?: { lat: number; lng: number }[];
  avoid?: string[];
  optimize?: boolean;
}

export interface RouteResult {
  geometry: GeoJSONGeometry;
  distance: number;
  duration: number;
  instructions: RouteInstruction[];
}

export interface RouteInstruction {
  type: string;
  text: string;
  distance: number;
  duration: number;
  geometry?: GeoJSONGeometry;
}

@Injectable()
export class GISIntegrationService {
  // Saudi Arabia and Gulf region boundaries
  private readonly regionExtent: BoundingBox = {
    minX: 34.0,
    minY: 16.0,
    maxX: 56.0,
    maxY: 32.0,
    srs: 'EPSG:4326',
  };

  // Agricultural layers catalog
  private readonly agriculturalLayers: LayerConfig[] = [
    {
      id: 'fields',
      name: 'Agricultural Fields',
      nameAr: 'الحقول الزراعية',
      type: 'vector',
      source: 'postgis://sahool/agricultural_fields',
      workspace: 'sahool',
      style: 'agricultural_fields_style',
      visible: true,
      opacity: 0.8,
      metadata: {
        title: 'Agricultural Field Boundaries',
        abstract: 'Boundaries of registered agricultural fields',
        keywords: ['agriculture', 'fields', 'boundaries', 'crops'],
        spatialExtent: this.regionExtent,
        updateFrequency: 'daily',
      },
    },
    {
      id: 'ndvi',
      name: 'NDVI Index',
      nameAr: 'مؤشر الغطاء النباتي',
      type: 'raster',
      source: 'sentinel-2-ndvi',
      visible: true,
      opacity: 0.7,
      metadata: {
        title: 'Normalized Difference Vegetation Index',
        abstract: 'NDVI derived from Sentinel-2 imagery',
        keywords: ['ndvi', 'vegetation', 'sentinel-2', 'remote sensing'],
        spatialExtent: this.regionExtent,
        updateFrequency: 'weekly',
      },
    },
    {
      id: 'soil',
      name: 'Soil Types',
      nameAr: 'أنواع التربة',
      type: 'vector',
      source: 'postgis://sahool/soil_types',
      visible: false,
      opacity: 0.6,
      metadata: {
        title: 'Soil Classification Map',
        abstract: 'Soil types and characteristics',
        keywords: ['soil', 'classification', 'agriculture'],
        spatialExtent: this.regionExtent,
        updateFrequency: 'yearly',
      },
    },
    {
      id: 'irrigation',
      name: 'Irrigation Networks',
      nameAr: 'شبكات الري',
      type: 'vector',
      source: 'postgis://sahool/irrigation_networks',
      visible: false,
      opacity: 0.8,
      metadata: {
        title: 'Irrigation Infrastructure',
        abstract: 'Irrigation canals, wells, and distribution networks',
        keywords: ['irrigation', 'water', 'infrastructure'],
        spatialExtent: this.regionExtent,
        updateFrequency: 'monthly',
      },
    },
    {
      id: 'weather_stations',
      name: 'Weather Stations',
      nameAr: 'محطات الطقس',
      type: 'vector',
      source: 'postgis://sahool/weather_stations',
      visible: true,
      opacity: 1.0,
      metadata: {
        title: 'Weather Monitoring Stations',
        abstract: 'Location and data from weather stations',
        keywords: ['weather', 'stations', 'monitoring', 'climate'],
        spatialExtent: this.regionExtent,
        updateFrequency: 'hourly',
      },
    },
  ];

  // Basemap options
  private readonly basemaps: Map<string, { url: string; attribution: string }> = new Map([
    ['osm', {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors',
    }],
    ['satellite', {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attribution: '© Esri',
    }],
    ['terrain', {
      url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: '© OpenTopoMap',
    }],
    ['arabic', {
      url: 'https://mt1.google.com/vt/lyrs=m@224&hl=ar&x={x}&y={y}&z={z}',
      attribution: '© Google',
    }],
  ]);

  // Coordinate systems
  private readonly supportedSRS: string[] = [
    'EPSG:4326',   // WGS 84
    'EPSG:3857',   // Web Mercator
    'EPSG:32637',  // UTM Zone 37N (Saudi Arabia East)
    'EPSG:32638',  // UTM Zone 38N (Saudi Arabia East)
    'EPSG:32639',  // UTM Zone 39N (Gulf Region)
  ];

  /**
   * Get service information
   */
  getServiceInfo(): {
    name: string;
    nameAr: string;
    version: string;
    capabilities: string[];
    basedOn: string[];
    supportedFormats: string[];
    supportedSRS: string[];
  } {
    return {
      name: 'GIS Integration Service',
      nameAr: 'خدمة تكامل نظم المعلومات الجغرافية',
      version: '1.0.0',
      capabilities: [
        'OGC WMS - Web Map Service',
        'OGC WFS - Web Feature Service',
        'OGC WMTS - Web Map Tile Service',
        'GeoJSON import/export',
        'Spatial queries (PostGIS)',
        'Field boundary management',
        'Zonal statistics',
        'Route planning (PgRouting)',
        'Multi-CRS support',
        'Agricultural layer catalog',
      ],
      basedOn: ['GeoSuite', 'QCarta', 'GeoServer', 'PostGIS', 'PgRouting'],
      supportedFormats: ['GeoJSON', 'GML', 'KML', 'Shapefile', 'GeoTIFF', 'WKT', 'WKB'],
      supportedSRS: this.supportedSRS,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Layer Management - إدارة الطبقات
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Get all available layers
   */
  getLayers(): LayerConfig[] {
    return this.agriculturalLayers;
  }

  /**
   * Get layer by ID
   */
  getLayer(layerId: string): LayerConfig | undefined {
    return this.agriculturalLayers.find(l => l.id === layerId);
  }

  /**
   * Get layer catalog grouped by type
   */
  getLayerCatalog(): {
    vector: LayerConfig[];
    raster: LayerConfig[];
    services: LayerConfig[];
  } {
    return {
      vector: this.agriculturalLayers.filter(l => l.type === 'vector'),
      raster: this.agriculturalLayers.filter(l => l.type === 'raster'),
      services: this.agriculturalLayers.filter(l => l.type === 'wms' || l.type === 'wmts'),
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // OGC WMS Service - خدمة خرائط الويب
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Get WMS Capabilities (GetCapabilities)
   */
  getWMSCapabilities(): WMSCapabilities {
    return {
      version: '1.3.0',
      title: 'SAHOOL Agricultural WMS',
      abstract: 'Web Map Service for SAHOOL Agricultural Platform',
      layers: this.agriculturalLayers.map(layer => ({
        name: layer.id,
        title: layer.name,
        abstract: layer.metadata?.abstract || '',
        srs: this.supportedSRS,
        boundingBox: layer.metadata?.spatialExtent || this.regionExtent,
        styles: [{ name: 'default', title: 'Default Style' }],
        queryable: layer.type === 'vector',
      })),
      formats: ['image/png', 'image/jpeg', 'image/gif', 'image/svg+xml'],
      srs: this.supportedSRS,
    };
  }

  /**
   * Generate WMS GetMap URL
   */
  getWMSMapUrl(params: {
    layers: string[];
    bbox: BoundingBox;
    width: number;
    height: number;
    format?: string;
    srs?: string;
    styles?: string[];
    transparent?: boolean;
  }): string {
    const baseUrl = '/gis/wms';
    const queryParams = new URLSearchParams({
      SERVICE: 'WMS',
      VERSION: '1.3.0',
      REQUEST: 'GetMap',
      LAYERS: params.layers.join(','),
      BBOX: `${params.bbox.minX},${params.bbox.minY},${params.bbox.maxX},${params.bbox.maxY}`,
      WIDTH: params.width.toString(),
      HEIGHT: params.height.toString(),
      FORMAT: params.format || 'image/png',
      CRS: params.srs || 'EPSG:4326',
      STYLES: params.styles?.join(',') || '',
      TRANSPARENT: (params.transparent !== false).toString(),
    });

    return `${baseUrl}?${queryParams.toString()}`;
  }

  /**
   * WMS GetFeatureInfo - query features at a point
   */
  getFeatureInfo(params: {
    layers: string[];
    point: { x: number; y: number };
    bbox: BoundingBox;
    width: number;
    height: number;
    srs?: string;
  }): GeoJSONFeatureCollection {
    // Simulate feature info response
    const features: GeoJSONFeature[] = [];

    for (const layerId of params.layers) {
      const layer = this.getLayer(layerId);
      if (layer && layer.type === 'vector') {
        features.push({
          type: 'Feature',
          id: `${layerId}_sample`,
          geometry: {
            type: 'Point',
            coordinates: [params.point.x, params.point.y],
          },
          properties: {
            layer: layerId,
            layerName: layer.name,
            layerNameAr: layer.nameAr,
            queryPoint: params.point,
            // Sample data
            fieldId: 'F001',
            cropType: 'wheat',
            area: 45.5,
            ndvi: 0.72,
          },
        });
      }
    }

    return {
      type: 'FeatureCollection',
      features,
      crs: {
        type: 'name',
        properties: { name: params.srs || 'EPSG:4326' },
      },
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // OGC WFS Service - خدمة المعالم
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Get WFS Capabilities
   */
  getWFSCapabilities(): WFSCapabilities {
    return {
      version: '2.0.0',
      title: 'SAHOOL Agricultural WFS',
      featureTypes: this.agriculturalLayers
        .filter(l => l.type === 'vector')
        .map(layer => ({
          name: layer.id,
          title: layer.name,
          abstract: layer.metadata?.abstract || '',
          srs: 'EPSG:4326',
          boundingBox: layer.metadata?.spatialExtent || this.regionExtent,
          keywords: layer.metadata?.keywords || [],
        })),
      outputFormats: ['application/json', 'application/gml+xml', 'text/xml'],
    };
  }

  /**
   * WFS GetFeature - retrieve features
   */
  getFeatures(params: {
    typeName: string;
    bbox?: BoundingBox;
    filter?: string;
    maxFeatures?: number;
    startIndex?: number;
    propertyName?: string[];
    sortBy?: string;
    outputFormat?: string;
  }): GeoJSONFeatureCollection {
    // Generate sample features based on layer type
    const features: GeoJSONFeature[] = [];
    const maxFeatures = params.maxFeatures || 100;

    // Sample agricultural fields
    if (params.typeName === 'fields') {
      for (let i = 0; i < Math.min(5, maxFeatures); i++) {
        features.push(this.generateSampleField(i));
      }
    }

    return {
      type: 'FeatureCollection',
      features,
      bbox: params.bbox ? [params.bbox.minX, params.bbox.minY, params.bbox.maxX, params.bbox.maxY] : undefined,
    };
  }

  /**
   * Generate sample field feature
   */
  private generateSampleField(index: number): GeoJSONFeature {
    const baseLat = 24.7 + (index * 0.1);
    const baseLng = 46.7 + (index * 0.1);
    const size = 0.02 + (Math.random() * 0.03);

    return {
      type: 'Feature',
      id: `field_${index + 1}`,
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [baseLng, baseLat],
          [baseLng + size, baseLat],
          [baseLng + size, baseLat + size],
          [baseLng, baseLat + size],
          [baseLng, baseLat],
        ]],
      },
      properties: {
        id: `F${String(index + 1).padStart(3, '0')}`,
        name: `Field ${index + 1}`,
        nameAr: `حقل ${index + 1}`,
        farmId: `FARM${Math.floor(index / 3) + 1}`,
        cropType: ['wheat', 'barley', 'date_palm', 'alfalfa'][index % 4],
        areaHectares: Math.round((size * size * 111 * 111) * 100) / 100,
        soilType: ['loamy', 'sandy', 'clay'][index % 3],
        irrigationType: ['drip', 'sprinkler', 'flood'][index % 3],
        ndviCurrent: Math.round((0.4 + Math.random() * 0.4) * 100) / 100,
        plantingDate: '2024-11-15',
        status: 'active',
      },
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Spatial Queries - الاستعلامات المكانية
  // Based on PostGIS patterns
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Execute spatial query
   */
  executeSpatialQuery(query: SpatialQuery): SpatialQueryResult {
    const startTime = Date.now();
    const features: GeoJSONFeature[] = [];

    switch (query.operation) {
      case 'buffer':
        if (query.geometry && query.distance) {
          features.push(this.createBuffer(query.geometry, query.distance, query.unit || 'meters'));
        }
        break;

      case 'intersects':
      case 'contains':
      case 'within':
        // Simulate spatial query results
        for (let i = 0; i < 3; i++) {
          features.push(this.generateSampleField(i));
        }
        break;
    }

    return {
      features,
      count: features.length,
      bbox: this.calculateBBox(features),
      queryTime: Date.now() - startTime,
    };
  }

  /**
   * Create buffer around geometry
   */
  private createBuffer(geometry: GeoJSONGeometry, distance: number, unit: string): GeoJSONFeature {
    // Convert distance to degrees (approximate)
    const distanceDegrees = unit === 'kilometers' ? distance / 111 :
                           unit === 'miles' ? distance / 69 :
                           distance / 111000; // meters

    // Simplified buffer for point
    if (geometry.type === 'Point') {
      const [lng, lat] = geometry.coordinates as number[];
      const bufferCoords: number[][] = [];

      for (let i = 0; i <= 36; i++) {
        const angle = (i * 10) * Math.PI / 180;
        bufferCoords.push([
          lng + distanceDegrees * Math.cos(angle),
          lat + distanceDegrees * Math.sin(angle),
        ]);
      }

      return {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [bufferCoords],
        },
        properties: {
          operation: 'buffer',
          distance,
          unit,
          originalGeometry: geometry.type,
        },
      };
    }

    // Return original geometry with buffer flag for complex geometries
    return {
      type: 'Feature',
      geometry,
      properties: {
        operation: 'buffer',
        distance,
        unit,
        note: 'Complex buffer requires PostGIS',
      },
    };
  }

  /**
   * Calculate bounding box for features
   */
  private calculateBBox(features: GeoJSONFeature[]): BoundingBox {
    if (features.length === 0) {
      return this.regionExtent;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    for (const feature of features) {
      const coords = this.flattenCoordinates(feature.geometry.coordinates);
      for (const coord of coords) {
        minX = Math.min(minX, coord[0]);
        minY = Math.min(minY, coord[1]);
        maxX = Math.max(maxX, coord[0]);
        maxY = Math.max(maxY, coord[1]);
      }
    }

    return { minX, minY, maxX, maxY, srs: 'EPSG:4326' };
  }

  /**
   * Flatten nested coordinates
   */
  private flattenCoordinates(coords: any): number[][] {
    if (typeof coords[0] === 'number') {
      return [coords as number[]];
    }
    if (typeof coords[0][0] === 'number') {
      return coords as number[][];
    }
    return coords.flat(10).filter((c: any) => typeof c[0] === 'number');
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Field Boundary Management - إدارة حدود الحقول
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Create field boundary from GeoJSON
   */
  createFieldBoundary(input: {
    farmId: string;
    name: string;
    nameAr: string;
    geometry: GeoJSONGeometry;
    soilType?: string;
    irrigationType?: string;
    currentCrop?: string;
  }): FieldBoundary {
    const area = this.calculateArea(input.geometry);
    const perimeter = this.calculatePerimeter(input.geometry);
    const centroid = this.calculateCentroid(input.geometry);

    return {
      id: `field_${Date.now()}`,
      farmId: input.farmId,
      name: input.name,
      nameAr: input.nameAr,
      geometry: input.geometry,
      areaHectares: area,
      areaDunum: area * 10, // 1 hectare = 10 dunum
      perimeter,
      centroid,
      soilType: input.soilType,
      irrigationType: input.irrigationType,
      currentCrop: input.currentCrop,
      metadata: {
        createdAt: new Date().toISOString(),
        source: 'user_input',
      },
    };
  }

  /**
   * Calculate area in hectares
   */
  calculateArea(geometry: GeoJSONGeometry): number {
    if (geometry.type !== 'Polygon' && geometry.type !== 'MultiPolygon') {
      return 0;
    }

    // Simplified shoelace formula for polygon area
    const coords = geometry.type === 'Polygon'
      ? geometry.coordinates[0] as number[][]
      : (geometry.coordinates[0] as number[][][])[0];

    let area = 0;
    for (let i = 0; i < coords.length - 1; i++) {
      area += coords[i][0] * coords[i + 1][1];
      area -= coords[i + 1][0] * coords[i][1];
    }
    area = Math.abs(area) / 2;

    // Convert to hectares (approximate, assuming degrees near equator)
    // 1 degree ≈ 111 km, so 1 degree² ≈ 12321 km² = 1232100 ha
    const hectares = area * 12321;
    return Math.round(hectares * 100) / 100;
  }

  /**
   * Calculate perimeter in kilometers
   */
  calculatePerimeter(geometry: GeoJSONGeometry): number {
    if (geometry.type !== 'Polygon' && geometry.type !== 'MultiPolygon') {
      return 0;
    }

    const coords = geometry.type === 'Polygon'
      ? geometry.coordinates[0] as number[][]
      : (geometry.coordinates[0] as number[][][])[0];

    let perimeter = 0;
    for (let i = 0; i < coords.length - 1; i++) {
      perimeter += this.haversineDistance(
        coords[i][1], coords[i][0],
        coords[i + 1][1], coords[i + 1][0]
      );
    }

    return Math.round(perimeter * 100) / 100;
  }

  /**
   * Calculate centroid
   */
  calculateCentroid(geometry: GeoJSONGeometry): { lat: number; lng: number } {
    const coords = this.flattenCoordinates(geometry.coordinates);
    const sumLat = coords.reduce((sum, c) => sum + c[1], 0);
    const sumLng = coords.reduce((sum, c) => sum + c[0], 0);

    return {
      lat: sumLat / coords.length,
      lng: sumLng / coords.length,
    };
  }

  /**
   * Haversine distance in kilometers
   */
  private haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Zonal Statistics - الإحصائيات المكانية
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Calculate zonal statistics for raster within polygons
   */
  calculateZonalStatistics(params: {
    zones: GeoJSONFeatureCollection;
    rasterLayer: string;
    statistics: ('count' | 'sum' | 'mean' | 'min' | 'max' | 'std')[];
  }): ZonalStatistics[] {
    const results: ZonalStatistics[] = [];

    for (const zone of params.zones.features) {
      const zoneId = zone.id?.toString() || 'unknown';
      const area = this.calculateArea(zone.geometry);

      // Simulate statistics based on zone area
      const baseValue = area * 10;

      results.push({
        zone: zoneId,
        count: Math.floor(area * 100),
        sum: Math.round(baseValue * 100),
        mean: Math.round((0.3 + Math.random() * 0.5) * 100) / 100, // NDVI-like values
        min: Math.round((0.1 + Math.random() * 0.2) * 100) / 100,
        max: Math.round((0.6 + Math.random() * 0.3) * 100) / 100,
        std: Math.round((0.05 + Math.random() * 0.1) * 100) / 100,
        area,
      });
    }

    return results;
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Routing Service - خدمة التوجيه
  // Based on PgRouting patterns
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Calculate route between points
   */
  calculateRoute(request: RouteRequest): RouteResult {
    const { origin, destination, waypoints = [] } = request;

    // Create route geometry
    const coordinates: number[][] = [
      [origin.lng, origin.lat],
      ...waypoints.map(wp => [wp.lng, wp.lat]),
      [destination.lng, destination.lat],
    ];

    // Calculate distance
    let totalDistance = 0;
    for (let i = 0; i < coordinates.length - 1; i++) {
      totalDistance += this.haversineDistance(
        coordinates[i][1], coordinates[i][0],
        coordinates[i + 1][1], coordinates[i + 1][0]
      );
    }

    // Estimate duration (assuming average speed of 60 km/h for agricultural roads)
    const durationMinutes = (totalDistance / 60) * 60;

    return {
      geometry: {
        type: 'LineString',
        coordinates,
      },
      distance: Math.round(totalDistance * 100) / 100,
      duration: Math.round(durationMinutes),
      instructions: this.generateRouteInstructions(coordinates),
    };
  }

  /**
   * Generate route instructions
   */
  private generateRouteInstructions(coordinates: number[][]): RouteInstruction[] {
    const instructions: RouteInstruction[] = [];

    instructions.push({
      type: 'start',
      text: 'ابدأ من نقطة الانطلاق',
      distance: 0,
      duration: 0,
    });

    for (let i = 0; i < coordinates.length - 1; i++) {
      const distance = this.haversineDistance(
        coordinates[i][1], coordinates[i][0],
        coordinates[i + 1][1], coordinates[i + 1][0]
      );

      instructions.push({
        type: i === coordinates.length - 2 ? 'arrive' : 'continue',
        text: i === coordinates.length - 2
          ? 'وصلت إلى الوجهة'
          : `استمر ${Math.round(distance * 10) / 10} كم`,
        distance: Math.round(distance * 100) / 100,
        duration: Math.round((distance / 60) * 60),
        geometry: {
          type: 'LineString',
          coordinates: [coordinates[i], coordinates[i + 1]],
        },
      });
    }

    return instructions;
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Map Project Management - إدارة مشاريع الخرائط
  // Based on QCarta patterns
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Create map project
   */
  createMapProject(input: {
    name: string;
    nameAr: string;
    description: string;
    layers: string[];
    basemap?: string;
    center?: { lat: number; lng: number };
    zoom?: number;
    owner: string;
  }): MapProject {
    const selectedLayers = input.layers
      .map(id => this.getLayer(id))
      .filter((l): l is LayerConfig => l !== undefined);

    return {
      id: `project_${Date.now()}`,
      name: input.name,
      nameAr: input.nameAr,
      description: input.description,
      layers: selectedLayers,
      basemap: input.basemap || 'satellite',
      center: input.center || { lat: 24.7, lng: 46.7 },
      zoom: input.zoom || 10,
      extent: this.regionExtent,
      createdAt: new Date(),
      updatedAt: new Date(),
      owner: input.owner,
      shared: false,
    };
  }

  /**
   * Get available basemaps
   */
  getBasemaps(): { id: string; name: string; url: string; attribution: string }[] {
    return Array.from(this.basemaps.entries()).map(([id, config]) => ({
      id,
      name: id.charAt(0).toUpperCase() + id.slice(1),
      ...config,
    }));
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // GeoJSON Utilities - أدوات GeoJSON
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Validate GeoJSON
   */
  validateGeoJSON(geojson: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!geojson) {
      errors.push('GeoJSON object is null or undefined');
      return { valid: false, errors };
    }

    if (!geojson.type) {
      errors.push('Missing type property');
    }

    if (geojson.type === 'Feature') {
      if (!geojson.geometry) {
        errors.push('Feature missing geometry');
      }
      if (!geojson.properties) {
        errors.push('Feature missing properties');
      }
    }

    if (geojson.type === 'FeatureCollection') {
      if (!Array.isArray(geojson.features)) {
        errors.push('FeatureCollection features must be an array');
      }
    }

    const validGeometryTypes = [
      'Point', 'LineString', 'Polygon',
      'MultiPoint', 'MultiLineString', 'MultiPolygon',
    ];

    if (geojson.geometry && !validGeometryTypes.includes(geojson.geometry.type)) {
      errors.push(`Invalid geometry type: ${geojson.geometry.type}`);
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Convert between coordinate systems (simplified)
   */
  transformCoordinates(
    coordinates: number[],
    fromSRS: string,
    toSRS: string
  ): number[] {
    // For EPSG:4326 to EPSG:3857 (Web Mercator)
    if (fromSRS === 'EPSG:4326' && toSRS === 'EPSG:3857') {
      const [lng, lat] = coordinates;
      const x = lng * 20037508.34 / 180;
      const y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
      return [x, y * 20037508.34 / 180];
    }

    // For EPSG:3857 to EPSG:4326
    if (fromSRS === 'EPSG:3857' && toSRS === 'EPSG:4326') {
      const [x, y] = coordinates;
      const lng = x * 180 / 20037508.34;
      const lat = Math.atan(Math.exp(y * Math.PI / 20037508.34)) * 360 / Math.PI - 90;
      return [lng, lat];
    }

    // Return original if transformation not supported
    return coordinates;
  }

  /**
   * Generate demo data for agricultural fields
   */
  generateDemoFields(count: number = 10): GeoJSONFeatureCollection {
    const features: GeoJSONFeature[] = [];

    for (let i = 0; i < count; i++) {
      features.push(this.generateSampleField(i));
    }

    return {
      type: 'FeatureCollection',
      features,
      bbox: [46.5, 24.5, 47.0, 25.0],
    };
  }
}
