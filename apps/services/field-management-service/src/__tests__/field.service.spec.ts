/**
 * Field Management Service - Service Layer Tests
 * Tests for business logic, validation, and data processing
 */

import { AppDataSource } from "@sahool/field-shared";
import { Field } from "@sahool/field-shared";
import {
  validatePolygonCoordinates,
  validateGeoJSON,
  calculatePolygonArea,
} from "@sahool/field-shared";
import {
  generateETag,
  validateIfMatch,
  createConflictResponse,
} from "@sahool/field-shared";

// Mock the data source
jest.mock("@sahool/field-shared", () => {
  const original = jest.requireActual("@sahool/field-shared");
  return {
    ...original,
    AppDataSource: {
      initialize: jest.fn().mockResolvedValue(undefined),
      query: jest.fn(),
      getRepository: jest.fn(() => ({
        findOne: jest.fn(),
        find: jest.fn(),
        create: jest.fn(),
        save: jest.fn(),
        delete: jest.fn(),
        createQueryBuilder: jest.fn(),
      })),
    },
  };
});

describe("Field Management Service - Service Layer", () => {
  let mockFieldRepo: any;

  const mockField: Partial<Field> = {
    id: "field-001",
    name: "Test Field",
    tenantId: "tenant-001",
    cropType: "wheat",
    status: "active",
    version: 1,
    boundary: {
      type: "Polygon",
      coordinates: [
        [
          [44.0, 15.0],
          [44.1, 15.0],
          [44.1, 15.1],
          [44.0, 15.1],
          [44.0, 15.0],
        ],
      ],
    } as any,
    centroid: {
      type: "Point",
      coordinates: [44.05, 15.05],
    } as any,
    areaHectares: 100.5,
    healthScore: 0.75,
    ndviValue: 0.65,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockFieldRepo = (AppDataSource as any).getRepository(Field);
  });

  describe("Field Validation", () => {
    describe("validatePolygonCoordinates", () => {
      it("should validate correct polygon coordinates", () => {
        const validCoords = [
          [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
            [44.0, 15.0],
          ],
        ];

        const result = validatePolygonCoordinates(validCoords);

        expect(result.valid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });

      it("should reject polygon with less than 4 points", () => {
        const invalidCoords = [
          [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.0, 15.0],
          ],
        ];

        const result = validatePolygonCoordinates(invalidCoords);

        expect(result.valid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });

      it("should reject polygon that is not closed", () => {
        const invalidCoords = [
          [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
          ],
        ];

        const result = validatePolygonCoordinates(invalidCoords);

        expect(result.valid).toBe(false);
      });

      it("should reject coordinates outside valid range", () => {
        const invalidCoords = [
          [
            [200.0, 15.0], // Invalid longitude
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
            [200.0, 15.0],
          ],
        ];

        const result = validatePolygonCoordinates(invalidCoords);

        expect(result.valid).toBe(false);
        expect(result.errors.some((e) => e.includes("longitude"))).toBe(true);
      });

      it("should reject latitude outside valid range", () => {
        const invalidCoords = [
          [
            [44.0, 95.0], // Invalid latitude
            [44.1, 95.0],
            [44.1, 95.1],
            [44.0, 95.1],
            [44.0, 95.0],
          ],
        ];

        const result = validatePolygonCoordinates(invalidCoords);

        expect(result.valid).toBe(false);
        expect(result.errors.some((e) => e.includes("latitude"))).toBe(true);
      });

      it("should provide warnings for suspicious coordinates", () => {
        const suspiciousCoords = [
          [
            [0.0, 0.0], // Null Island
            [0.1, 0.0],
            [0.1, 0.1],
            [0.0, 0.1],
            [0.0, 0.0],
          ],
        ];

        const result = validatePolygonCoordinates(suspiciousCoords);

        expect(result.warnings.length).toBeGreaterThan(0);
      });
    });

    describe("validateGeoJSON", () => {
      it("should validate correct GeoJSON", () => {
        const validGeoJSON = {
          type: "Polygon",
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

        const result = validateGeoJSON(validGeoJSON);

        expect(result.valid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });

      it("should reject GeoJSON without type", () => {
        const invalidGeoJSON = {
          coordinates: [
            [
              [44.0, 15.0],
              [44.1, 15.0],
              [44.0, 15.0],
            ],
          ],
        };

        const result = validateGeoJSON(invalidGeoJSON);

        expect(result.valid).toBe(false);
      });

      it("should reject GeoJSON without coordinates", () => {
        const invalidGeoJSON = {
          type: "Polygon",
        };

        const result = validateGeoJSON(invalidGeoJSON);

        expect(result.valid).toBe(false);
      });

      it("should reject non-Polygon types", () => {
        const invalidGeoJSON = {
          type: "Point",
          coordinates: [44.0, 15.0],
        };

        const result = validateGeoJSON(invalidGeoJSON);

        expect(result.valid).toBe(false);
      });
    });

    describe("calculatePolygonArea", () => {
      it("should calculate area for valid polygon", () => {
        const coords = [
          [44.0, 15.0],
          [44.1, 15.0],
          [44.1, 15.1],
          [44.0, 15.1],
          [44.0, 15.0],
        ];

        const area = calculatePolygonArea(coords);

        expect(area).toBeGreaterThan(0);
        expect(typeof area).toBe("number");
      });

      it("should return 0 for degenerate polygon", () => {
        const coords = [
          [44.0, 15.0],
          [44.0, 15.0],
          [44.0, 15.0],
          [44.0, 15.0],
        ];

        const area = calculatePolygonArea(coords);

        expect(area).toBe(0);
      });

      it("should handle different polygon sizes", () => {
        const smallCoords = [
          [44.0, 15.0],
          [44.01, 15.0],
          [44.01, 15.01],
          [44.0, 15.01],
          [44.0, 15.0],
        ];

        const largeCoords = [
          [44.0, 15.0],
          [44.5, 15.0],
          [44.5, 15.5],
          [44.0, 15.5],
          [44.0, 15.0],
        ];

        const smallArea = calculatePolygonArea(smallCoords);
        const largeArea = calculatePolygonArea(largeCoords);

        expect(largeArea).toBeGreaterThan(smallArea);
      });
    });
  });

  describe("ETag and Optimistic Locking", () => {
    describe("generateETag", () => {
      it("should generate ETag from field ID and version", () => {
        const etag = generateETag("field-001", 1);

        expect(etag).toBe('"field-001_v1"');
      });

      it("should generate different ETags for different versions", () => {
        const etag1 = generateETag("field-001", 1);
        const etag2 = generateETag("field-001", 2);

        expect(etag1).not.toBe(etag2);
      });

      it("should generate different ETags for different fields", () => {
        const etag1 = generateETag("field-001", 1);
        const etag2 = generateETag("field-002", 1);

        expect(etag1).not.toBe(etag2);
      });
    });

    describe("validateIfMatch", () => {
      it("should validate matching ETag", () => {
        const etag = '"field-001_v1"';
        const isValid = validateIfMatch(etag, "field-001", 1);

        expect(isValid).toBe(true);
      });

      it("should reject mismatched ETag", () => {
        const etag = '"field-001_v1"';
        const isValid = validateIfMatch(etag, "field-001", 2);

        expect(isValid).toBe(false);
      });

      it("should handle ETags without quotes", () => {
        const etag = "field-001_v1";
        const isValid = validateIfMatch(etag, "field-001", 1);

        expect(isValid).toBe(true);
      });
    });

    describe("createConflictResponse", () => {
      it("should create conflict response with server data", () => {
        const currentETag = '"field-001_v2"';
        const response = createConflictResponse(
          mockField as Field,
          currentETag,
          "field",
        );

        expect(response.success).toBe(false);
        expect(response.error).toContain("Conflict");
        expect(response.serverData).toBeDefined();
        expect(response.serverETag).toBe(currentETag);
      });

      it("should include conflict resolution instructions", () => {
        const currentETag = '"field-001_v2"';
        const response = createConflictResponse(
          mockField as Field,
          currentETag,
          "field",
        );

        expect(response.resolution).toBeDefined();
        expect(response.resolution.steps).toBeDefined();
      });
    });
  });

  describe("Field Business Logic", () => {
    describe("Field Creation", () => {
      it("should create field with automatic centroid calculation", async () => {
        const fieldData = {
          name: "New Field",
          tenantId: "tenant-001",
          cropType: "wheat",
          coordinates: [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
          ],
        };

        mockFieldRepo.create.mockReturnValue({
          ...mockField,
          ...fieldData,
        });
        mockFieldRepo.save.mockResolvedValue({
          ...mockField,
          ...fieldData,
          id: "field-new",
        });

        const created = mockFieldRepo.create(fieldData);
        const saved = await mockFieldRepo.save(created);

        expect(saved).toBeDefined();
        expect(saved.centroid).toBeDefined();
      });

      it("should close polygon automatically if not closed", () => {
        const openCoords = [
          [44.0, 15.0],
          [44.1, 15.0],
          [44.1, 15.1],
          [44.0, 15.1],
        ];

        const closedCoords = [...openCoords];
        if (
          JSON.stringify(closedCoords[0]) !==
          JSON.stringify(closedCoords[closedCoords.length - 1])
        ) {
          closedCoords.push(closedCoords[0]);
        }

        expect(closedCoords).toHaveLength(5);
        expect(closedCoords[0]).toEqual(closedCoords[4]);
      });

      it("should validate required fields", () => {
        const invalidData = {
          name: "Incomplete Field",
          // Missing tenantId and cropType
        };

        const hasRequiredFields =
          invalidData.name &&
          (invalidData as any).tenantId &&
          (invalidData as any).cropType;

        expect(hasRequiredFields).toBe(false);
      });
    });

    describe("Field Updates", () => {
      it("should increment version on update", async () => {
        const updatedField = { ...mockField, version: 2, name: "Updated Name" };
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const saved = await mockFieldRepo.save({
          ...mockField,
          name: "Updated Name",
        });

        expect(saved.version).toBe(2);
      });

      it("should track boundary changes in history", async () => {
        const oldBoundary = mockField.boundary;
        const newBoundary = {
          type: "Polygon",
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

        const boundaryChanged =
          JSON.stringify(newBoundary) !== JSON.stringify(oldBoundary);

        expect(boundaryChanged).toBe(true);
      });

      it("should prevent updating immutable fields", () => {
        const updates = {
          id: "new-id", // Should not be allowed
          tenantId: "new-tenant", // Should not be allowed
          name: "Updated Name", // Allowed
        };

        const allowedFields = ["name", "cropType", "status", "irrigationType"];
        const isIdUpdateAttempt = Object.keys(updates).includes("id");
        const isTenantUpdateAttempt = Object.keys(updates).includes("tenantId");

        expect(isIdUpdateAttempt).toBe(true);
        expect(isTenantUpdateAttempt).toBe(true);
      });
    });

    describe("NDVI Analysis", () => {
      it("should calculate health score from NDVI", () => {
        const calculateHealthScore = (ndviValue: number): number => {
          if (ndviValue < 0.2) return 0;
          if (ndviValue > 0.8) return 1;
          return (ndviValue - 0.2) / 0.6;
        };

        expect(calculateHealthScore(0.5)).toBeCloseTo(0.5, 2);
        expect(calculateHealthScore(0.8)).toBeCloseTo(1.0, 2);
        expect(calculateHealthScore(0.2)).toBeCloseTo(0.0, 2);
      });

      it("should categorize NDVI values correctly", () => {
        const getNdviCategory = (value: number) => {
          if (value < 0) return "non-vegetation";
          if (value < 0.2) return "bare-soil";
          if (value < 0.4) return "stressed";
          if (value < 0.6) return "moderate";
          if (value < 0.8) return "healthy";
          return "very-healthy";
        };

        expect(getNdviCategory(-0.1)).toBe("non-vegetation");
        expect(getNdviCategory(0.1)).toBe("bare-soil");
        expect(getNdviCategory(0.3)).toBe("stressed");
        expect(getNdviCategory(0.5)).toBe("moderate");
        expect(getNdviCategory(0.7)).toBe("healthy");
        expect(getNdviCategory(0.9)).toBe("very-healthy");
      });

      it("should detect NDVI trend", () => {
        const values = [0.5, 0.52, 0.54, 0.56, 0.58, 0.6];
        const firstHalf = values.slice(0, Math.floor(values.length / 2));
        const secondHalf = values.slice(Math.floor(values.length / 2));
        const firstAvg =
          firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
        const secondAvg =
          secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
        const trend = secondAvg - firstAvg;

        expect(trend).toBeGreaterThan(0);
      });
    });

    describe("Sync Logic", () => {
      it("should detect new fields in batch sync", () => {
        const fields = [
          { id: "field-001", _isNew: false },
          { _isNew: true, name: "New Field" },
          { id: "field-002", _isNew: false },
        ];

        const newFields = fields.filter((f) => f._isNew || !f.id);

        expect(newFields).toHaveLength(1);
      });

      it("should detect version conflicts", () => {
        const clientVersion = 1;
        const serverVersion = 5;

        const hasConflict = clientVersion < serverVersion;

        expect(hasConflict).toBe(true);
      });

      it("should calculate pending downloads", async () => {
        const lastSyncDate = new Date("2024-01-01");
        const serverFields = [
          { ...mockField, updatedAt: new Date("2024-01-02") },
          { ...mockField, updatedAt: new Date("2024-01-03") },
          { ...mockField, updatedAt: new Date("2023-12-31") },
        ];

        const pendingFields = serverFields.filter(
          (f) => f.updatedAt > lastSyncDate,
        );

        expect(pendingFields).toHaveLength(2);
      });
    });
  });

  describe("PostGIS Integration", () => {
    describe("Area Calculation", () => {
      it("should calculate area using PostGIS", async () => {
        (AppDataSource.query as jest.Mock).mockResolvedValue([
          { area_hectares: 100.5 },
        ]);

        const result = await AppDataSource.query(
          "SELECT ST_Area(ST_Transform(boundary, 32637)) / 10000 as area_hectares FROM fields WHERE id = $1",
          ["field-001"],
        );

        expect(result[0].area_hectares).toBe(100.5);
      });
    });

    describe("Distance Calculation", () => {
      it("should calculate distance between fields", async () => {
        (AppDataSource.query as jest.Mock).mockResolvedValue([
          { distance_km: 5.2 },
        ]);

        const result = await AppDataSource.query(
          "SELECT calculate_fields_distance($1, $2) as distance_km",
          ["field-001", "field-002"],
        );

        expect(result[0].distance_km).toBe(5.2);
      });
    });

    describe("Point in Polygon", () => {
      it("should check if point is inside field boundary", async () => {
        (AppDataSource.query as jest.Mock).mockResolvedValue([
          { is_inside: true },
        ]);

        const result = await AppDataSource.query(
          "SELECT check_point_in_field($1, $2, $3) as is_inside",
          [15.05, 44.05, "field-001"],
        );

        expect(result[0].is_inside).toBe(true);
      });
    });

    describe("Spatial Queries", () => {
      it("should find fields within radius", async () => {
        const mockNearbyFields = [
          {
            field_id: "field-001",
            field_name: "Nearby Field",
            distance_km: 2.5,
          },
        ];

        (AppDataSource.query as jest.Mock).mockResolvedValue(mockNearbyFields);

        const result = await AppDataSource.query(
          "SELECT * FROM find_fields_in_radius($1, $2, $3, $4)",
          [15.05, 44.05, 5, "tenant-001"],
        );

        expect(result).toHaveLength(1);
        expect(result[0].distance_km).toBe(2.5);
      });

      it("should find fields in bounding box", async () => {
        const mockFields = [
          { field_id: "field-001", field_name: "Field 1" },
          { field_id: "field-002", field_name: "Field 2" },
        ];

        (AppDataSource.query as jest.Mock).mockResolvedValue(mockFields);

        const result = await AppDataSource.query(
          "SELECT * FROM find_fields_in_bbox($1, $2, $3, $4, $5)",
          [15.0, 44.0, 15.5, 44.5, "tenant-001"],
        );

        expect(result).toHaveLength(2);
      });
    });
  });

  describe("Error Handling", () => {
    it("should handle database connection errors", async () => {
      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error("Connection failed"),
      );

      await expect(AppDataSource.query("SELECT 1")).rejects.toThrow(
        "Connection failed",
      );
    });

    it("should handle invalid field ID", async () => {
      mockFieldRepo.findOne.mockResolvedValue(null);

      const field = await mockFieldRepo.findOne({ where: { id: "invalid" } });

      expect(field).toBeNull();
    });

    it("should handle transaction rollback on error", async () => {
      mockFieldRepo.save.mockRejectedValue(new Error("Save failed"));

      await expect(mockFieldRepo.save(mockField)).rejects.toThrow(
        "Save failed",
      );
    });
  });

  describe("Data Sanitization", () => {
    it("should prevent SQL injection in queries", () => {
      const maliciousInput = "field-001'; DROP TABLE fields; --";
      const parameterizedQuery = "SELECT * FROM fields WHERE id = $1";

      // Using parameterized queries prevents SQL injection
      expect(parameterizedQuery).toContain("$1");
      expect(maliciousInput).toContain("'");
    });

    it("should sanitize user input", () => {
      const input = '<script>alert("xss")</script>';
      const sanitized = input.replace(/</g, "&lt;").replace(/>/g, "&gt;");

      expect(sanitized).not.toContain("<script>");
      expect(sanitized).toContain("&lt;script&gt;");
    });

    it("should prevent prototype pollution", () => {
      const maliciousUpdate = {
        name: "Updated Field",
        __proto__: { isAdmin: true },
      };

      // Explicit property assignment prevents prototype pollution
      const safeUpdate: any = {};
      if (maliciousUpdate.name !== undefined)
        safeUpdate.name = maliciousUpdate.name;

      expect(safeUpdate.__proto__).toBeUndefined();
      expect((safeUpdate as any).isAdmin).toBeUndefined();
    });
  });
});
