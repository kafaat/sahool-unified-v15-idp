import { Controller, Get, Post, Body, Param, Query, HttpException, HttpStatus } from '@nestjs/common';
import { GISIntegrationService, GeoJSONFeatureCollection, GeoJSONGeometry, BoundingBox, SpatialQuery, RouteRequest } from './gis-integration.service';

// Request DTOs
interface GetMapDto {
  layers: string[];
  bbox: { minX: number; minY: number; maxX: number; maxY: number };
  width: number;
  height: number;
  format?: string;
  srs?: string;
  transparent?: boolean;
}

interface GetFeatureInfoDto {
  layers: string[];
  point: { x: number; y: number };
  bbox: { minX: number; minY: number; maxX: number; maxY: number };
  width: number;
  height: number;
  srs?: string;
}

interface GetFeaturesDto {
  typeName: string;
  bbox?: { minX: number; minY: number; maxX: number; maxY: number };
  filter?: string;
  maxFeatures?: number;
  startIndex?: number;
  propertyName?: string[];
  sortBy?: string;
  outputFormat?: string;
}

interface SpatialQueryDto {
  operation: 'intersects' | 'contains' | 'within' | 'overlaps' | 'touches' | 'buffer' | 'union';
  geometry?: GeoJSONGeometry;
  distance?: number;
  unit?: 'meters' | 'kilometers' | 'miles';
  targetLayer?: string;
  properties?: string[];
}

interface CreateFieldDto {
  farmId: string;
  name: string;
  nameAr: string;
  geometry: GeoJSONGeometry;
  soilType?: string;
  irrigationType?: string;
  currentCrop?: string;
}

interface ZonalStatsDto {
  zones: GeoJSONFeatureCollection;
  rasterLayer: string;
  statistics: ('count' | 'sum' | 'mean' | 'min' | 'max' | 'std')[];
}

interface RouteRequestDto {
  origin: { lat: number; lng: number };
  destination: { lat: number; lng: number };
  waypoints?: { lat: number; lng: number }[];
  avoid?: string[];
  optimize?: boolean;
}

interface CreateProjectDto {
  name: string;
  nameAr: string;
  description: string;
  layers: string[];
  basemap?: string;
  center?: { lat: number; lng: number };
  zoom?: number;
  owner: string;
}

interface TransformDto {
  coordinates: number[];
  fromSRS: string;
  toSRS: string;
}

interface ValidateGeoJSONDto {
  geojson: any;
}

@Controller('gis')
export class GISIntegrationController {
  constructor(private readonly gisService: GISIntegrationService) {}

  /**
   * GET /gis
   * Service information and capabilities
   */
  @Get()
  getServiceInfo() {
    const info = this.gisService.getServiceInfo();
    return {
      ...info,
      endpoints: {
        // Service Info
        info: 'GET /gis - Service information',

        // Layer Management
        layers: 'GET /gis/layers - List all layers',
        layerById: 'GET /gis/layers/:layerId - Get layer details',
        catalog: 'GET /gis/layers/catalog - Get layer catalog',

        // OGC WMS
        wmsCapabilities: 'GET /gis/wms/capabilities - WMS GetCapabilities',
        wmsGetMap: 'POST /gis/wms/map - WMS GetMap URL',
        wmsFeatureInfo: 'POST /gis/wms/feature-info - WMS GetFeatureInfo',

        // OGC WFS
        wfsCapabilities: 'GET /gis/wfs/capabilities - WFS GetCapabilities',
        wfsGetFeature: 'POST /gis/wfs/features - WFS GetFeature',

        // Spatial Queries
        spatialQuery: 'POST /gis/spatial/query - Execute spatial query',
        buffer: 'POST /gis/spatial/buffer - Create buffer',

        // Field Management
        createField: 'POST /gis/fields - Create field boundary',
        calculateArea: 'POST /gis/fields/area - Calculate area',
        calculateCentroid: 'POST /gis/fields/centroid - Calculate centroid',

        // Analysis
        zonalStats: 'POST /gis/analysis/zonal-stats - Zonal statistics',

        // Routing
        route: 'POST /gis/routing/route - Calculate route',

        // Map Projects
        createProject: 'POST /gis/projects - Create map project',
        basemaps: 'GET /gis/basemaps - List basemaps',

        // Utilities
        validate: 'POST /gis/utils/validate - Validate GeoJSON',
        transform: 'POST /gis/utils/transform - Transform coordinates',
        demo: 'GET /gis/demo/fields - Generate demo fields',
      },
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Layer Management
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * GET /gis/layers
   * List all available layers
   */
  @Get('layers')
  getLayers() {
    const layers = this.gisService.getLayers();
    return {
      success: true,
      count: layers.length,
      layers: layers.map(l => ({
        id: l.id,
        name: l.name,
        nameAr: l.nameAr,
        type: l.type,
        visible: l.visible,
        opacity: l.opacity,
      })),
    };
  }

  /**
   * GET /gis/layers/catalog
   * Get layer catalog grouped by type
   */
  @Get('layers/catalog')
  getLayerCatalog() {
    const catalog = this.gisService.getLayerCatalog();
    return {
      success: true,
      catalog: {
        vector: catalog.vector.map(l => ({ id: l.id, name: l.name, nameAr: l.nameAr })),
        raster: catalog.raster.map(l => ({ id: l.id, name: l.name, nameAr: l.nameAr })),
        services: catalog.services.map(l => ({ id: l.id, name: l.name, nameAr: l.nameAr })),
      },
    };
  }

  /**
   * GET /gis/layers/:layerId
   * Get layer details
   */
  @Get('layers/:layerId')
  getLayer(@Param('layerId') layerId: string) {
    const layer = this.gisService.getLayer(layerId);
    if (!layer) {
      throw new HttpException('Layer not found', HttpStatus.NOT_FOUND);
    }
    return {
      success: true,
      layer,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // OGC WMS Endpoints
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * GET /gis/wms/capabilities
   * WMS GetCapabilities
   */
  @Get('wms/capabilities')
  getWMSCapabilities() {
    const capabilities = this.gisService.getWMSCapabilities();
    return {
      success: true,
      service: 'WMS',
      ...capabilities,
    };
  }

  /**
   * POST /gis/wms/map
   * Generate WMS GetMap URL
   */
  @Post('wms/map')
  getMapUrl(@Body() dto: GetMapDto) {
    if (!dto.layers || !dto.bbox || !dto.width || !dto.height) {
      throw new HttpException(
        'Required: layers, bbox, width, height',
        HttpStatus.BAD_REQUEST
      );
    }

    const bbox: BoundingBox = {
      ...dto.bbox,
      srs: dto.srs || 'EPSG:4326',
    };

    const url = this.gisService.getWMSMapUrl({
      layers: dto.layers,
      bbox,
      width: dto.width,
      height: dto.height,
      format: dto.format,
      srs: dto.srs,
      transparent: dto.transparent,
    });

    return {
      success: true,
      url,
      request: {
        service: 'WMS',
        version: '1.3.0',
        request: 'GetMap',
        ...dto,
      },
    };
  }

  /**
   * POST /gis/wms/feature-info
   * WMS GetFeatureInfo
   */
  @Post('wms/feature-info')
  getFeatureInfo(@Body() dto: GetFeatureInfoDto) {
    if (!dto.layers || !dto.point || !dto.bbox || !dto.width || !dto.height) {
      throw new HttpException(
        'Required: layers, point, bbox, width, height',
        HttpStatus.BAD_REQUEST
      );
    }

    const bbox: BoundingBox = {
      ...dto.bbox,
      srs: dto.srs || 'EPSG:4326',
    };

    const result = this.gisService.getFeatureInfo({
      layers: dto.layers,
      point: dto.point,
      bbox,
      width: dto.width,
      height: dto.height,
      srs: dto.srs,
    });

    return {
      success: true,
      ...result,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // OGC WFS Endpoints
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * GET /gis/wfs/capabilities
   * WFS GetCapabilities
   */
  @Get('wfs/capabilities')
  getWFSCapabilities() {
    const capabilities = this.gisService.getWFSCapabilities();
    return {
      success: true,
      service: 'WFS',
      ...capabilities,
    };
  }

  /**
   * POST /gis/wfs/features
   * WFS GetFeature
   */
  @Post('wfs/features')
  getFeatures(@Body() dto: GetFeaturesDto) {
    if (!dto.typeName) {
      throw new HttpException('Required: typeName', HttpStatus.BAD_REQUEST);
    }

    const bbox = dto.bbox ? {
      ...dto.bbox,
      srs: 'EPSG:4326',
    } : undefined;

    const result = this.gisService.getFeatures({
      typeName: dto.typeName,
      bbox,
      filter: dto.filter,
      maxFeatures: dto.maxFeatures,
      startIndex: dto.startIndex,
      propertyName: dto.propertyName,
      sortBy: dto.sortBy,
      outputFormat: dto.outputFormat,
    });

    return {
      success: true,
      ...result,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Spatial Queries
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * POST /gis/spatial/query
   * Execute spatial query
   */
  @Post('spatial/query')
  executeSpatialQuery(@Body() dto: SpatialQueryDto) {
    if (!dto.operation) {
      throw new HttpException('Required: operation', HttpStatus.BAD_REQUEST);
    }

    const query: SpatialQuery = {
      operation: dto.operation,
      geometry: dto.geometry,
      distance: dto.distance,
      unit: dto.unit,
      targetLayer: dto.targetLayer,
      properties: dto.properties,
    };

    const result = this.gisService.executeSpatialQuery(query);

    return {
      success: true,
      operation: dto.operation,
      ...result,
    };
  }

  /**
   * POST /gis/spatial/buffer
   * Create buffer around geometry
   */
  @Post('spatial/buffer')
  createBuffer(@Body() dto: { geometry: GeoJSONGeometry; distance: number; unit?: string }) {
    if (!dto.geometry || !dto.distance) {
      throw new HttpException('Required: geometry, distance', HttpStatus.BAD_REQUEST);
    }

    const result = this.gisService.executeSpatialQuery({
      operation: 'buffer',
      geometry: dto.geometry,
      distance: dto.distance,
      unit: (dto.unit as 'meters' | 'kilometers' | 'miles') || 'meters',
    });

    return {
      success: true,
      buffer: result.features[0],
      originalGeometry: dto.geometry.type,
      distance: dto.distance,
      unit: dto.unit || 'meters',
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Field Management
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * POST /gis/fields
   * Create field boundary
   */
  @Post('fields')
  createField(@Body() dto: CreateFieldDto) {
    if (!dto.farmId || !dto.name || !dto.geometry) {
      throw new HttpException(
        'Required: farmId, name, geometry',
        HttpStatus.BAD_REQUEST
      );
    }

    const field = this.gisService.createFieldBoundary(dto);

    return {
      success: true,
      message: 'Field boundary created',
      messageAr: 'تم إنشاء حدود الحقل',
      field,
    };
  }

  /**
   * POST /gis/fields/area
   * Calculate area of geometry
   */
  @Post('fields/area')
  calculateArea(@Body() dto: { geometry: GeoJSONGeometry }) {
    if (!dto.geometry) {
      throw new HttpException('Required: geometry', HttpStatus.BAD_REQUEST);
    }

    const areaHectares = this.gisService.calculateArea(dto.geometry);

    return {
      success: true,
      area: {
        hectares: areaHectares,
        dunum: areaHectares * 10,
        squareMeters: areaHectares * 10000,
        acres: areaHectares * 2.471,
      },
    };
  }

  /**
   * POST /gis/fields/centroid
   * Calculate centroid of geometry
   */
  @Post('fields/centroid')
  calculateCentroid(@Body() dto: { geometry: GeoJSONGeometry }) {
    if (!dto.geometry) {
      throw new HttpException('Required: geometry', HttpStatus.BAD_REQUEST);
    }

    const centroid = this.gisService.calculateCentroid(dto.geometry);

    return {
      success: true,
      centroid,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Analysis
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * POST /gis/analysis/zonal-stats
   * Calculate zonal statistics
   */
  @Post('analysis/zonal-stats')
  calculateZonalStats(@Body() dto: ZonalStatsDto) {
    if (!dto.zones || !dto.rasterLayer || !dto.statistics) {
      throw new HttpException(
        'Required: zones, rasterLayer, statistics',
        HttpStatus.BAD_REQUEST
      );
    }

    const results = this.gisService.calculateZonalStatistics(dto);

    return {
      success: true,
      rasterLayer: dto.rasterLayer,
      requestedStatistics: dto.statistics,
      zoneCount: results.length,
      results,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Routing
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * POST /gis/routing/route
   * Calculate route
   */
  @Post('routing/route')
  calculateRoute(@Body() dto: RouteRequestDto) {
    if (!dto.origin || !dto.destination) {
      throw new HttpException('Required: origin, destination', HttpStatus.BAD_REQUEST);
    }

    const result = this.gisService.calculateRoute(dto);

    return {
      success: true,
      route: {
        ...result,
        distanceUnit: 'km',
        durationUnit: 'minutes',
      },
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Map Projects
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * POST /gis/projects
   * Create map project
   */
  @Post('projects')
  createProject(@Body() dto: CreateProjectDto) {
    if (!dto.name || !dto.layers || !dto.owner) {
      throw new HttpException('Required: name, layers, owner', HttpStatus.BAD_REQUEST);
    }

    const project = this.gisService.createMapProject(dto);

    return {
      success: true,
      message: 'Map project created',
      messageAr: 'تم إنشاء مشروع الخريطة',
      project,
    };
  }

  /**
   * GET /gis/basemaps
   * List available basemaps
   */
  @Get('basemaps')
  getBasemaps() {
    const basemaps = this.gisService.getBasemaps();
    return {
      success: true,
      count: basemaps.length,
      basemaps,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Utilities
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * POST /gis/utils/validate
   * Validate GeoJSON
   */
  @Post('utils/validate')
  validateGeoJSON(@Body() dto: ValidateGeoJSONDto) {
    const result = this.gisService.validateGeoJSON(dto.geojson);
    return {
      success: true,
      ...result,
    };
  }

  /**
   * POST /gis/utils/transform
   * Transform coordinates between SRS
   */
  @Post('utils/transform')
  transformCoordinates(@Body() dto: TransformDto) {
    if (!dto.coordinates || !dto.fromSRS || !dto.toSRS) {
      throw new HttpException(
        'Required: coordinates, fromSRS, toSRS',
        HttpStatus.BAD_REQUEST
      );
    }

    const transformed = this.gisService.transformCoordinates(
      dto.coordinates,
      dto.fromSRS,
      dto.toSRS
    );

    return {
      success: true,
      original: {
        coordinates: dto.coordinates,
        srs: dto.fromSRS,
      },
      transformed: {
        coordinates: transformed,
        srs: dto.toSRS,
      },
    };
  }

  /**
   * GET /gis/demo/fields
   * Generate demo agricultural fields
   */
  @Get('demo/fields')
  getDemoFields(@Query('count') count?: string) {
    const fieldCount = count ? parseInt(count, 10) : 10;
    const fields = this.gisService.generateDemoFields(
      Math.min(Math.max(1, fieldCount), 50)
    );

    return {
      success: true,
      message: 'Demo agricultural fields generated',
      messageAr: 'تم إنشاء حقول زراعية تجريبية',
      ...fields,
    };
  }

  /**
   * GET /gis/demo/wms
   * Demo WMS request
   */
  @Get('demo/wms')
  demoWMS() {
    const capabilities = this.gisService.getWMSCapabilities();
    const mapUrl = this.gisService.getWMSMapUrl({
      layers: ['fields', 'ndvi'],
      bbox: { minX: 46.5, minY: 24.5, maxX: 47.0, maxY: 25.0, srs: 'EPSG:4326' },
      width: 800,
      height: 600,
      format: 'image/png',
      transparent: true,
    });

    return {
      success: true,
      demo: 'WMS Service Demo',
      demoAr: 'عرض خدمة WMS',
      capabilities: {
        version: capabilities.version,
        title: capabilities.title,
        layerCount: capabilities.layers.length,
      },
      sampleRequest: {
        url: mapUrl,
        layers: ['fields', 'ndvi'],
        bbox: 'Saudi Arabia (Riyadh Region)',
        dimensions: '800x600',
      },
    };
  }

  /**
   * GET /gis/demo/routing
   * Demo routing request
   */
  @Get('demo/routing')
  demoRouting() {
    const route = this.gisService.calculateRoute({
      origin: { lat: 24.7136, lng: 46.6753 }, // Riyadh
      destination: { lat: 24.4539, lng: 39.6142 }, // Medina
      waypoints: [
        { lat: 24.5, lng: 43.0 }, // Midpoint
      ],
    });

    return {
      success: true,
      demo: 'Routing Service Demo',
      demoAr: 'عرض خدمة التوجيه',
      route: {
        origin: 'Riyadh',
        destination: 'Medina',
        distance: `${route.distance} km`,
        duration: `${route.duration} minutes`,
        instructionCount: route.instructions.length,
      },
    };
  }
}
