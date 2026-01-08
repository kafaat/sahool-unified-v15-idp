/**
 * Field Core Service - Geospatial Service Tests
 * Tests for PostGIS-powered geospatial operations
 */

import { AppDataSource } from '@sahool/field-shared';
import { GeoService } from '@sahool/field-shared';

// Mock the data source
jest.mock('@sahool/field-shared', () => {
  const original = jest.requireActual('@sahool/field-shared');
  return {
    ...original,
    AppDataSource: {
      initialize: jest.fn().mockResolvedValue(undefined),
      query: jest.fn(),
      isInitialized: true,
    },
  };
});

describe('Geospatial Service - PostGIS Operations', () => {
  let geoService: GeoService;

  beforeAll(() => {
    geoService = new GeoService();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('findFieldsInRadius - Proximity search', () => {
    it('should find fields within specified radius', async () => {
      const mockResults = [
        {
          field_id: 'field-001',
          field_name: 'North Field',
          distance_km: 1.5,
          area_hectares: 100.5,
          crop_type: 'wheat',
          centroid_lat: 15.05,
          centroid_lng: 44.05,
        },
        {
          field_id: 'field-002',
          field_name: 'South Field',
          distance_km: 3.2,
          area_hectares: 75.2,
          crop_type: 'rice',
          centroid_lat: 15.03,
          centroid_lng: 44.03,
        },
      ];

      (AppDataSource.query as jest.Mock).mockResolvedValue(mockResults);

      const result = await geoService.findFieldsInRadius(15.05, 44.05, 5);

      expect(result).toHaveLength(2);
      expect(result[0].field_id).toBe('field-001');
      expect(result[0].distance_km).toBe(1.5);
      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.stringContaining('find_fields_in_radius'),
        [15.05, 44.05, 5, null]
      );
    });

    it('should filter by tenant when tenantId provided', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await geoService.findFieldsInRadius(15.05, 44.05, 5, 'tenant-001');

      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.any(String),
        [15.05, 44.05, 5, 'tenant-001']
      );
    });

    it('should handle empty results', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      const result = await geoService.findFieldsInRadius(0, 0, 5);

      expect(result).toEqual([]);
    });

    it('should work with different radius values', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await geoService.findFieldsInRadius(15.05, 44.05, 10);

      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.any(String),
        [15.05, 44.05, 10, null]
      );
    });
  });

  describe('findNearbyFarms - Farm proximity search', () => {
    it('should find nearby farms sorted by distance', async () => {
      const mockFarms = [
        {
          farm_id: 'farm-001',
          farm_name: 'Green Valley Farm',
          distance_km: 2.1,
          total_area_hectares: 500.0,
          location_lat: 15.05,
          location_lng: 44.05,
          phone: '+967-1234567',
          email: 'farm@example.com',
        },
        {
          farm_id: 'farm-002',
          farm_name: 'Sunset Farm',
          distance_km: 4.5,
          total_area_hectares: 300.0,
          location_lat: 15.08,
          location_lng: 44.08,
          phone: null,
          email: null,
        },
      ];

      (AppDataSource.query as jest.Mock).mockResolvedValue(mockFarms);

      const result = await geoService.findNearbyFarms(15.05, 44.05, 10);

      expect(result).toHaveLength(2);
      expect(result[0].farm_name).toBe('Green Valley Farm');
      expect(result[0].distance_km).toBe(2.1);
      expect(result[1].distance_km).toBeGreaterThan(result[0].distance_km);
    });

    it('should use default limit when not provided', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await geoService.findNearbyFarms(15.05, 44.05);

      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.any(String),
        [15.05, 44.05, 10, null]
      );
    });

    it('should respect custom limit parameter', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await geoService.findNearbyFarms(15.05, 44.05, 5, 'tenant-001');

      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.any(String),
        [15.05, 44.05, 5, 'tenant-001']
      );
    });
  });

  describe('calculateFieldArea - Area calculation', () => {
    it('should calculate field area in hectares', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { area_hectares: '150.5' },
      ]);

      const result = await geoService.calculateFieldArea('field-001');

      expect(result.field_id).toBe('field-001');
      expect(result.area_hectares).toBe(150.5);
      expect(result.calculated_at).toBeDefined();
      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.stringContaining('get_field_area'),
        ['field-001']
      );
    });

    it('should throw error for non-existent field', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await expect(
        geoService.calculateFieldArea('nonexistent')
      ).rejects.toThrow('Field with ID nonexistent not found');
    });

    it('should throw error when field has no boundary', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { area_hectares: null },
      ]);

      await expect(
        geoService.calculateFieldArea('field-no-boundary')
      ).rejects.toThrow('not found or has no boundary');
    });

    it('should handle decimal precision correctly', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { area_hectares: '100.123456' },
      ]);

      const result = await geoService.calculateFieldArea('field-001');

      expect(result.area_hectares).toBeCloseTo(100.123456, 6);
    });
  });

  describe('checkPointInField - Point containment test', () => {
    it('should return true when point is inside field', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { is_inside: true },
      ]);

      const result = await geoService.checkPointInField(15.05, 44.05, 'field-001');

      expect(result.field_id).toBe('field-001');
      expect(result.is_inside).toBe(true);
      expect(result.checked_at).toBeDefined();
      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.stringContaining('check_point_in_field'),
        [15.05, 44.05, 'field-001']
      );
    });

    it('should return false when point is outside field', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { is_inside: false },
      ]);

      const result = await geoService.checkPointInField(99.0, 99.0, 'field-001');

      expect(result.is_inside).toBe(false);
    });

    it('should handle boundary edge cases', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { is_inside: true },
      ]);

      const result = await geoService.checkPointInField(44.0, 15.0, 'field-001');

      expect(result.is_inside).toBeDefined();
    });

    it('should handle empty query result', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      const result = await geoService.checkPointInField(15.05, 44.05, 'field-001');

      expect(result.is_inside).toBe(false);
    });
  });

  describe('findFieldsInBBox - Bounding box query', () => {
    it('should find fields within bounding box', async () => {
      const mockFields = [
        {
          field_id: 'field-001',
          field_name: 'Field 1',
          area_hectares: 100.0,
          crop_type: 'wheat',
          boundary_geojson: {
            type: 'Polygon',
            coordinates: [
              [
                [44.0, 15.0],
                [44.1, 15.0],
                [44.1, 15.1],
                [44.0, 15.1],
                [44.0, 15.0],
              ],
            ],
          },
        },
        {
          field_id: 'field-002',
          field_name: 'Field 2',
          area_hectares: 75.0,
          crop_type: 'rice',
          boundary_geojson: {
            type: 'Polygon',
            coordinates: [
              [
                [44.2, 15.2],
                [44.3, 15.2],
                [44.3, 15.3],
                [44.2, 15.3],
                [44.2, 15.2],
              ],
            ],
          },
        },
      ];

      (AppDataSource.query as jest.Mock).mockResolvedValue(mockFields);

      const result = await geoService.findFieldsInBBox(15.0, 44.0, 15.5, 44.5);

      expect(result).toHaveLength(2);
      expect(result[0].boundary_geojson).toBeDefined();
      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.stringContaining('find_fields_in_bbox'),
        [15.0, 44.0, 15.5, 44.5, null]
      );
    });

    it('should filter by tenant in bounding box query', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await geoService.findFieldsInBBox(
        15.0,
        44.0,
        15.5,
        44.5,
        'tenant-001'
      );

      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.any(String),
        [15.0, 44.0, 15.5, 44.5, 'tenant-001']
      );
    });

    it('should validate bounding box coordinates', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      // South-West to North-East
      await geoService.findFieldsInBBox(15.0, 44.0, 15.5, 44.5);

      expect(AppDataSource.query).toHaveBeenCalled();
    });

    it('should handle empty results for bbox', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      const result = await geoService.findFieldsInBBox(0, 0, 1, 1);

      expect(result).toEqual([]);
    });
  });

  describe('calculateFieldsDistance - Distance between fields', () => {
    it('should calculate distance between two fields', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { distance_km: '5.25' },
      ]);

      const result = await geoService.calculateFieldsDistance(
        'field-001',
        'field-002'
      );

      expect(result.field_id_1).toBe('field-001');
      expect(result.field_id_2).toBe('field-002');
      expect(result.distance_km).toBe(5.25);
      expect(result.calculated_at).toBeDefined();
    });

    it('should throw error when distance calculation fails', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await expect(
        geoService.calculateFieldsDistance('field-001', 'field-002')
      ).rejects.toThrow('Could not calculate distance between fields');
    });

    it('should handle zero distance for same field', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { distance_km: '0' },
      ]);

      const result = await geoService.calculateFieldsDistance(
        'field-001',
        'field-001'
      );

      expect(result.distance_km).toBe(0);
    });

    it('should handle large distances', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { distance_km: '1234.567' },
      ]);

      const result = await geoService.calculateFieldsDistance(
        'field-far-1',
        'field-far-2'
      );

      expect(result.distance_km).toBeCloseTo(1234.567, 3);
    });
  });

  describe('getRegionFieldStats - Regional statistics', () => {
    it('should return statistics for region', async () => {
      const mockStats = {
        total_fields: '25',
        total_area_ha: 1250.5,
        avg_field_size_ha: 50.02,
        crop_distribution: {
          wheat: 10,
          rice: 8,
          corn: 5,
          barley: 2,
        },
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([mockStats]);

      const result = await geoService.getRegionFieldStats(
        15.0,
        44.0,
        15.5,
        44.5
      );

      expect(result.total_fields).toBe('25');
      expect(result.total_area_ha).toBe(1250.5);
      expect(result.avg_field_size_ha).toBe(50.02);
      expect(result.crop_distribution.wheat).toBe(10);
    });

    it('should return zero stats for empty region', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      const result = await geoService.getRegionFieldStats(0, 0, 1, 1);

      expect(result).toEqual({
        total_fields: '0',
        total_area_ha: 0,
        avg_field_size_ha: 0,
        crop_distribution: {},
      });
    });

    it('should filter region stats by tenant', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        {
          total_fields: '10',
          total_area_ha: 500.0,
          avg_field_size_ha: 50.0,
          crop_distribution: { wheat: 10 },
        },
      ]);

      await geoService.getRegionFieldStats(
        15.0,
        44.0,
        15.5,
        44.5,
        'tenant-001'
      );

      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.any(String),
        [15.0, 44.0, 15.5, 44.5, 'tenant-001']
      );
    });
  });

  describe('getFieldGeoJSON - Field GeoJSON retrieval', () => {
    it('should return field with GeoJSON geometries', async () => {
      const mockGeoJSON = {
        id: 'field-001',
        name: 'Test Field',
        boundary_geojson: {
          type: 'Polygon',
          coordinates: [
            [
              [44.0, 15.0],
              [44.1, 15.0],
              [44.1, 15.1],
              [44.0, 15.1],
              [44.0, 15.0],
            ],
          ],
        },
        centroid_geojson: {
          type: 'Point',
          coordinates: [44.05, 15.05],
        },
        area_hectares: 100.5,
        crop_type: 'wheat',
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([mockGeoJSON]);

      const result = await geoService.getFieldGeoJSON('field-001');

      expect(result.id).toBe('field-001');
      expect(result.boundary_geojson.type).toBe('Polygon');
      expect(result.centroid_geojson.type).toBe('Point');
    });

    it('should throw error for non-existent field', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await expect(
        geoService.getFieldGeoJSON('nonexistent')
      ).rejects.toThrow('Field with ID nonexistent not found');
    });
  });

  describe('getFarmGeoJSON - Farm GeoJSON retrieval', () => {
    it('should return farm with GeoJSON geometries', async () => {
      const mockFarmGeoJSON = {
        id: 'farm-001',
        name: 'Green Valley Farm',
        location_geojson: {
          type: 'Point',
          coordinates: [44.05, 15.05],
        },
        boundary_geojson: {
          type: 'Polygon',
          coordinates: [
            [
              [44.0, 15.0],
              [44.2, 15.0],
              [44.2, 15.2],
              [44.0, 15.2],
              [44.0, 15.0],
            ],
          ],
        },
        total_area_hectares: 500.0,
        address: 'Rural Area, Yemen',
        phone: '+967-1234567',
        email: 'farm@example.com',
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([mockFarmGeoJSON]);

      const result = await geoService.getFarmGeoJSON('farm-001');

      expect(result.id).toBe('farm-001');
      expect(result.location_geojson.type).toBe('Point');
      expect(result.boundary_geojson).toBeDefined();
    });

    it('should throw error for non-existent farm', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await expect(
        geoService.getFarmGeoJSON('nonexistent')
      ).rejects.toThrow('Farm with ID nonexistent not found');
    });
  });

  describe('getFarmFields - Get all fields for a farm', () => {
    it('should return all fields belonging to a farm', async () => {
      const mockFields = [
        {
          id: 'field-001',
          name: 'North Field',
          crop_type: 'wheat',
          boundary_geojson: { type: 'Polygon', coordinates: [] },
          centroid_geojson: { type: 'Point', coordinates: [44.05, 15.05] },
          area_hectares: 100.5,
          status: 'active',
          health_score: 0.75,
          ndvi_value: 0.65,
        },
        {
          id: 'field-002',
          name: 'South Field',
          crop_type: 'rice',
          boundary_geojson: { type: 'Polygon', coordinates: [] },
          centroid_geojson: { type: 'Point', coordinates: [44.03, 15.03] },
          area_hectares: 75.0,
          status: 'active',
          health_score: 0.82,
          ndvi_value: 0.71,
        },
      ];

      (AppDataSource.query as jest.Mock).mockResolvedValue(mockFields);

      const result = await geoService.getFarmFields('farm-001');

      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('North Field');
      expect(result[1].name).toBe('South Field');
    });

    it('should return empty array for farm with no fields', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      const result = await geoService.getFarmFields('farm-no-fields');

      expect(result).toEqual([]);
    });
  });

  describe('createFieldWithBoundary - Create field with GeoJSON', () => {
    it('should create field with valid GeoJSON boundary', async () => {
      const fieldData = {
        name: 'New Geo Field',
        tenant_id: 'tenant-001',
        crop_type: 'wheat',
        owner_id: 'owner-001',
        boundary_geojson: {
          type: 'Polygon',
          coordinates: [
            [
              [44.0, 15.0],
              [44.1, 15.0],
              [44.1, 15.1],
              [44.0, 15.1],
              [44.0, 15.0],
            ],
          ],
        },
      };

      const mockCreated = {
        id: 'field-new',
        name: 'New Geo Field',
        area_hectares: 100.5,
        boundary_geojson: fieldData.boundary_geojson,
        centroid_geojson: { type: 'Point', coordinates: [44.05, 15.05] },
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([mockCreated]);

      const result = await geoService.createFieldWithBoundary(fieldData);

      expect(result.id).toBe('field-new');
      expect(result.area_hectares).toBe(100.5);
      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO fields'),
        expect.arrayContaining([
          'New Geo Field',
          'tenant-001',
          'wheat',
          'owner-001',
          null,
          expect.any(String),
        ])
      );
    });

    it('should create field without optional owner_id and farm_id', async () => {
      const fieldData = {
        name: 'Simple Field',
        tenant_id: 'tenant-001',
        crop_type: 'rice',
        boundary_geojson: {
          type: 'Polygon',
          coordinates: [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.0]]],
        },
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { id: 'field-simple', name: 'Simple Field' },
      ]);

      const result = await geoService.createFieldWithBoundary(fieldData);

      expect(result.id).toBe('field-simple');
    });
  });

  describe('updateFieldBoundary - Update field geometry', () => {
    it('should update field boundary with new GeoJSON', async () => {
      const newBoundary = {
        type: 'Polygon',
        coordinates: [
          [
            [44.0, 15.0],
            [44.2, 15.0],
            [44.2, 15.2],
            [44.0, 15.2],
            [44.0, 15.0],
          ],
        ],
      };

      const mockUpdated = {
        id: 'field-001',
        name: 'Updated Field',
        area_hectares: 200.5,
        boundary_geojson: newBoundary,
        centroid_geojson: { type: 'Point', coordinates: [44.1, 15.1] },
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([mockUpdated]);

      const result = await geoService.updateFieldBoundary('field-001', newBoundary);

      expect(result.id).toBe('field-001');
      expect(result.area_hectares).toBe(200.5);
      expect(AppDataSource.query).toHaveBeenCalledWith(
        expect.stringContaining('UPDATE fields'),
        [expect.any(String), 'field-001']
      );
    });

    it('should throw error when updating non-existent field', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      const newBoundary = {
        type: 'Polygon',
        coordinates: [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.0]]],
      };

      await expect(
        geoService.updateFieldBoundary('nonexistent', newBoundary)
      ).rejects.toThrow('Field with ID nonexistent not found');
    });
  });

  describe('createFarmWithLocation - Create farm with coordinates', () => {
    it('should create farm with location and boundary', async () => {
      const farmData = {
        name: 'New Farm',
        tenant_id: 'tenant-001',
        owner_id: 'owner-001',
        location_lat: 15.05,
        location_lng: 44.05,
        boundary_geojson: {
          type: 'Polygon',
          coordinates: [
            [
              [44.0, 15.0],
              [44.2, 15.0],
              [44.2, 15.2],
              [44.0, 15.2],
              [44.0, 15.0],
            ],
          ],
        },
        address: 'Rural Yemen',
        phone: '+967-1234567',
        email: 'farm@example.com',
      };

      const mockCreated = {
        id: 'farm-new',
        name: 'New Farm',
        location_geojson: { type: 'Point', coordinates: [44.05, 15.05] },
        boundary_geojson: farmData.boundary_geojson,
        total_area_hectares: 500.0,
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([mockCreated]);

      const result = await geoService.createFarmWithLocation(farmData);

      expect(result.id).toBe('farm-new');
      expect(result.location_geojson.type).toBe('Point');
    });

    it('should create farm with location only (no boundary)', async () => {
      const farmData = {
        name: 'Simple Farm',
        tenant_id: 'tenant-001',
        owner_id: 'owner-001',
        location_lat: 15.05,
        location_lng: 44.05,
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([
        {
          id: 'farm-simple',
          name: 'Simple Farm',
          location_geojson: { type: 'Point', coordinates: [44.05, 15.05] },
          total_area_hectares: 0,
        },
      ]);

      const result = await geoService.createFarmWithLocation(farmData);

      expect(result.id).toBe('farm-simple');
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle PostGIS query failures', async () => {
      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error('PostGIS function not found')
      );

      await expect(
        geoService.findFieldsInRadius(15.05, 44.05, 5)
      ).rejects.toThrow('PostGIS function not found');
    });

    it('should handle database connection errors', async () => {
      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error('Connection lost')
      );

      await expect(
        geoService.calculateFieldArea('field-001')
      ).rejects.toThrow('Connection lost');
    });

    it('should handle invalid coordinates gracefully', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      // Invalid coordinates should be handled by PostGIS
      const result = await geoService.findFieldsInRadius(999, 999, 5);

      expect(result).toEqual([]);
    });

    it('should handle null geometries', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { area_hectares: null },
      ]);

      await expect(
        geoService.calculateFieldArea('field-null-geometry')
      ).rejects.toThrow();
    });

    it('should handle malformed GeoJSON', async () => {
      const invalidGeoJSON = {
        type: 'InvalidType',
        coordinates: 'not-an-array',
      };

      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error('Invalid GeoJSON')
      );

      await expect(
        geoService.createFieldWithBoundary({
          name: 'Invalid Field',
          tenant_id: 'tenant-001',
          crop_type: 'wheat',
          boundary_geojson: invalidGeoJSON,
        })
      ).rejects.toThrow('Invalid GeoJSON');
    });
  });

  describe('Performance and Optimization', () => {
    it('should use spatial indexes for proximity queries', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([]);

      await geoService.findFieldsInRadius(15.05, 44.05, 5);

      // Verify the query uses PostGIS spatial functions
      const query = (AppDataSource.query as jest.Mock).mock.calls[0][0];
      expect(query).toContain('find_fields_in_radius');
    });

    it('should batch process large datasets efficiently', async () => {
      const largeDataset = Array(1000)
        .fill(null)
        .map((_, i) => ({
          field_id: `field-${i}`,
          field_name: `Field ${i}`,
          distance_km: i * 0.1,
          area_hectares: 100.0,
          crop_type: 'wheat',
          centroid_lat: 15.0,
          centroid_lng: 44.0,
        }));

      (AppDataSource.query as jest.Mock).mockResolvedValue(largeDataset);

      const result = await geoService.findFieldsInRadius(15.0, 44.0, 100);

      expect(result).toHaveLength(1000);
    });

    it('should minimize database round trips', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        {
          id: 'field-001',
          boundary_geojson: { type: 'Polygon', coordinates: [] },
          centroid_geojson: { type: 'Point', coordinates: [44.05, 15.05] },
        },
      ]);

      await geoService.getFieldGeoJSON('field-001');

      // Should be a single query
      expect(AppDataSource.query).toHaveBeenCalledTimes(1);
    });
  });

  describe('Data Integrity and Validation', () => {
    it('should preserve SRID in spatial operations', async () => {
      const geoJSON = {
        type: 'Polygon',
        coordinates: [
          [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
            [44.0, 15.0],
          ],
        ],
      };

      (AppDataSource.query as jest.Mock).mockResolvedValue([{ id: 'field-001' }]);

      await geoService.createFieldWithBoundary({
        name: 'SRID Test',
        tenant_id: 'tenant-001',
        crop_type: 'wheat',
        boundary_geojson: geoJSON,
      });

      const query = (AppDataSource.query as jest.Mock).mock.calls[0][0];
      // Verify SRID 4326 (WGS84) is used
      expect(query).toContain('4326');
    });

    it('should handle coordinate precision correctly', async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([
        { distance_km: '5.123456789' },
      ]);

      const result = await geoService.calculateFieldsDistance(
        'field-001',
        'field-002'
      );

      expect(result.distance_km).toBeCloseTo(5.123456789, 9);
    });

    it('should validate polygon closure', async () => {
      const openPolygon = {
        type: 'Polygon',
        coordinates: [
          [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
            // Missing closing point
          ],
        ],
      };

      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error('Polygon is not closed')
      );

      await expect(
        geoService.createFieldWithBoundary({
          name: 'Open Polygon',
          tenant_id: 'tenant-001',
          crop_type: 'wheat',
          boundary_geojson: openPolygon,
        })
      ).rejects.toThrow();
    });
  });
});
