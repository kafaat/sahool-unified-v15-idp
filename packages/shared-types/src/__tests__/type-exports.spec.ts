/**
 * Shared Types Export Tests for SAHOOL Platform
 *
 * Tests validate type definitions and exports.
 */

// Type definitions for testing
interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

interface TenantEntity extends BaseEntity {
  tenantId: string;
}

interface Field extends TenantEntity {
  name: string;
  nameAr?: string;
  farmId: string;
  areaHa: number;
  boundary: GeoJSONPolygon | null;
  cropType?: string;
  ndvi?: number;
  soilMoisture?: number;
  status: FieldStatus;
}

interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

interface GeoJSONPoint {
  type: 'Point';
  coordinates: [number, number];
}

type FieldStatus = 'active' | 'fallow' | 'harvested' | 'planned';

interface User extends TenantEntity {
  email: string;
  name: string;
  nameAr?: string;
  roles: UserRole[];
  isActive: boolean;
}

type UserRole = 'admin' | 'manager' | 'farmer' | 'viewer';

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

interface ApiError {
  code: string;
  message: string;
  messageAr?: string;
  details?: Record<string, unknown>;
}

type Result<T, E = ApiError> = { success: true; data: T } | { success: false; error: E };

// Type guard functions
function isField(obj: unknown): obj is Field {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    'areaHa' in obj &&
    'status' in obj
  );
}

function isGeoJSONPolygon(obj: unknown): obj is GeoJSONPolygon {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'type' in obj &&
    (obj as GeoJSONPolygon).type === 'Polygon' &&
    'coordinates' in obj
  );
}

function isApiError(obj: unknown): obj is ApiError {
  return typeof obj === 'object' && obj !== null && 'code' in obj && 'message' in obj;
}

describe('Type Definitions', () => {
  describe('BaseEntity', () => {
    it('should have required fields', () => {
      const entity: BaseEntity = {
        id: 'entity-123',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(entity.id).toBeDefined();
      expect(entity.createdAt).toBeInstanceOf(Date);
      expect(entity.updatedAt).toBeInstanceOf(Date);
    });
  });

  describe('TenantEntity', () => {
    it('should extend BaseEntity with tenantId', () => {
      const entity: TenantEntity = {
        id: 'entity-123',
        tenantId: 'tenant-456',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(entity.tenantId).toBe('tenant-456');
    });
  });

  describe('Field', () => {
    it('should have all required fields', () => {
      const field: Field = {
        id: 'field-123',
        tenantId: 'tenant-456',
        createdAt: new Date(),
        updatedAt: new Date(),
        name: 'North Field',
        farmId: 'farm-789',
        areaHa: 10.5,
        boundary: null,
        status: 'active',
      };

      expect(field.name).toBe('North Field');
      expect(field.areaHa).toBe(10.5);
      expect(field.status).toBe('active');
    });

    it('should allow optional fields', () => {
      const field: Field = {
        id: 'field-123',
        tenantId: 'tenant-456',
        createdAt: new Date(),
        updatedAt: new Date(),
        name: 'North Field',
        nameAr: 'الحقل الشمالي',
        farmId: 'farm-789',
        areaHa: 10.5,
        boundary: null,
        cropType: 'wheat',
        ndvi: 0.72,
        soilMoisture: 45,
        status: 'active',
      };

      expect(field.nameAr).toBe('الحقل الشمالي');
      expect(field.cropType).toBe('wheat');
      expect(field.ndvi).toBe(0.72);
    });

    it('should validate FieldStatus type', () => {
      const validStatuses: FieldStatus[] = ['active', 'fallow', 'harvested', 'planned'];

      validStatuses.forEach((status) => {
        const field: Field = {
          id: 'field-123',
          tenantId: 'tenant-456',
          createdAt: new Date(),
          updatedAt: new Date(),
          name: 'Test Field',
          farmId: 'farm-789',
          areaHa: 10,
          boundary: null,
          status,
        };

        expect(validStatuses).toContain(field.status);
      });
    });
  });

  describe('GeoJSON Types', () => {
    it('should define valid GeoJSON Polygon', () => {
      const polygon: GeoJSONPolygon = {
        type: 'Polygon',
        coordinates: [
          [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0, 0],
          ],
        ],
      };

      expect(polygon.type).toBe('Polygon');
      expect(polygon.coordinates).toHaveLength(1);
      expect(polygon.coordinates[0]).toHaveLength(5);
    });

    it('should define valid GeoJSON Point', () => {
      const point: GeoJSONPoint = {
        type: 'Point',
        coordinates: [46.75, 24.75],
      };

      expect(point.type).toBe('Point');
      expect(point.coordinates).toHaveLength(2);
    });
  });

  describe('User', () => {
    it('should have all required fields', () => {
      const user: User = {
        id: 'user-123',
        tenantId: 'tenant-456',
        createdAt: new Date(),
        updatedAt: new Date(),
        email: 'user@example.com',
        name: 'John Doe',
        roles: ['farmer'],
        isActive: true,
      };

      expect(user.email).toBe('user@example.com');
      expect(user.roles).toContain('farmer');
    });

    it('should validate UserRole type', () => {
      const validRoles: UserRole[] = ['admin', 'manager', 'farmer', 'viewer'];

      const user: User = {
        id: 'user-123',
        tenantId: 'tenant-456',
        createdAt: new Date(),
        updatedAt: new Date(),
        email: 'user@example.com',
        name: 'John Doe',
        roles: validRoles,
        isActive: true,
      };

      expect(user.roles).toEqual(validRoles);
    });
  });

  describe('PaginatedResponse', () => {
    it('should wrap array data with pagination info', () => {
      const response: PaginatedResponse<Field> = {
        data: [],
        total: 100,
        page: 1,
        pageSize: 10,
        hasNext: true,
        hasPrevious: false,
      };

      expect(response.total).toBe(100);
      expect(response.hasNext).toBe(true);
      expect(response.hasPrevious).toBe(false);
    });

    it('should work with different types', () => {
      const userResponse: PaginatedResponse<User> = {
        data: [],
        total: 50,
        page: 2,
        pageSize: 25,
        hasNext: false,
        hasPrevious: true,
      };

      expect(userResponse.page).toBe(2);
      expect(userResponse.hasPrevious).toBe(true);
    });
  });

  describe('ApiError', () => {
    it('should have required fields', () => {
      const error: ApiError = {
        code: 'FIELD_NOT_FOUND',
        message: 'Field not found',
      };

      expect(error.code).toBe('FIELD_NOT_FOUND');
      expect(error.message).toBe('Field not found');
    });

    it('should allow Arabic message', () => {
      const error: ApiError = {
        code: 'FIELD_NOT_FOUND',
        message: 'Field not found',
        messageAr: 'الحقل غير موجود',
      };

      expect(error.messageAr).toBe('الحقل غير موجود');
    });

    it('should allow details object', () => {
      const error: ApiError = {
        code: 'VALIDATION_ERROR',
        message: 'Validation failed',
        details: {
          field: 'areaHa',
          constraint: 'min',
          value: -5,
        },
      };

      expect(error.details?.field).toBe('areaHa');
    });
  });

  describe('Result Type', () => {
    it('should represent success result', () => {
      const result: Result<Field> = {
        success: true,
        data: {
          id: 'field-123',
          tenantId: 'tenant-456',
          createdAt: new Date(),
          updatedAt: new Date(),
          name: 'Test Field',
          farmId: 'farm-789',
          areaHa: 10,
          boundary: null,
          status: 'active',
        },
      };

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.name).toBe('Test Field');
      }
    });

    it('should represent error result', () => {
      const result: Result<Field> = {
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Field not found',
        },
      };

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.code).toBe('NOT_FOUND');
      }
    });
  });
});

describe('Type Guards', () => {
  describe('isField', () => {
    it('should return true for valid Field object', () => {
      const field = {
        id: 'field-123',
        name: 'Test Field',
        areaHa: 10,
        status: 'active',
      };

      expect(isField(field)).toBe(true);
    });

    it('should return false for invalid object', () => {
      expect(isField(null)).toBe(false);
      expect(isField(undefined)).toBe(false);
      expect(isField({ id: '123' })).toBe(false);
      expect(isField('string')).toBe(false);
    });
  });

  describe('isGeoJSONPolygon', () => {
    it('should return true for valid Polygon', () => {
      const polygon = {
        type: 'Polygon',
        coordinates: [
          [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0, 0],
          ],
        ],
      };

      expect(isGeoJSONPolygon(polygon)).toBe(true);
    });

    it('should return false for Point', () => {
      const point = {
        type: 'Point',
        coordinates: [0, 0],
      };

      expect(isGeoJSONPolygon(point)).toBe(false);
    });

    it('should return false for invalid object', () => {
      expect(isGeoJSONPolygon(null)).toBe(false);
      expect(isGeoJSONPolygon({})).toBe(false);
    });
  });

  describe('isApiError', () => {
    it('should return true for valid ApiError', () => {
      const error = {
        code: 'ERROR_CODE',
        message: 'Error message',
      };

      expect(isApiError(error)).toBe(true);
    });

    it('should return false for invalid object', () => {
      expect(isApiError(null)).toBe(false);
      expect(isApiError({ code: 'ERROR' })).toBe(false);
      expect(isApiError({ message: 'Error' })).toBe(false);
    });
  });
});
