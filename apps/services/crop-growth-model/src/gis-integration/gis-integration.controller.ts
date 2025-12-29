import { Controller, Get, Post, Body, Param, Query, HttpException, HttpStatus, ValidationPipe } from '@nestjs/common';
import { GISIntegrationService, GeoJSONFeatureCollection, GeoJSONGeometry, BoundingBox, SpatialQuery, RouteRequest } from './gis-integration.service';
import {
  GetMapDto,
  GetFeatureInfoDto,
  GetFeaturesDto,
  SpatialQueryDto,
  BufferDto,
  CreateFieldDto,
  CalculateAreaDto,
  CalculateCentroidDto,
  ZonalStatsDto,
  RouteRequestDto,
  CreateProjectDto,
  TransformDto,
  ValidateGeoJSONDto,
} from './gis-integration.dto';

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
  getMapUrl(@Body(ValidationPipe) dto: GetMapDto) {

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
  getFeatureInfo(@Body(ValidationPipe) dto: GetFeatureInfoDto) {

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
  getFeatures(@Body(ValidationPipe) dto: GetFeaturesDto) {

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
  executeSpatialQuery(@Body(ValidationPipe) dto: SpatialQueryDto) {

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
  createBuffer(@Body(ValidationPipe) dto: BufferDto) {

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
  createField(@Body(ValidationPipe) dto: CreateFieldDto) {

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
  calculateArea(@Body(ValidationPipe) dto: CalculateAreaDto) {

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
  calculateCentroid(@Body(ValidationPipe) dto: CalculateCentroidDto) {

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
  calculateZonalStats(@Body(ValidationPipe) dto: ZonalStatsDto) {

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
  calculateRoute(@Body(ValidationPipe) dto: RouteRequestDto) {

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
  createProject(@Body(ValidationPipe) dto: CreateProjectDto) {

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
  transformCoordinates(@Body(ValidationPipe) dto: TransformDto) {

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
    // Validate and sanitize count parameter
    let validatedCount = 10;
    if (count) {
      const parsedCount = parseInt(count, 10);
      if (isNaN(parsedCount) || parsedCount < 1) {
        throw new HttpException(
          'Invalid count: must be a positive number',
          HttpStatus.BAD_REQUEST,
        );
      }
      validatedCount = Math.min(Math.max(1, parsedCount), 50); // Max 50 fields
    }

    const fields = this.gisService.generateDemoFields(validatedCount);

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
