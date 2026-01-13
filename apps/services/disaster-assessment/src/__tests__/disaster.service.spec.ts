/**
 * اختبارات خدمة تقييم الكوارث
 * Disaster Assessment Service Tests
 *
 * Comprehensive tests for the SAHOOL Disaster Assessment Service.
 */

import { Test, TestingModule } from "@nestjs/testing";
import { DisasterService } from "../disaster/disaster.service";
import {
  DisasterType,
  Severity,
  DisasterStatus,
} from "../disaster/disaster.dto";

// ─────────────────────────────────────────────────────────────────────────────
// Test Suite
// ─────────────────────────────────────────────────────────────────────────────

describe("DisasterService", () => {
  let service: DisasterService;
  let module: TestingModule;

  beforeEach(async () => {
    module = await Test.createTestingModule({
      providers: [DisasterService],
    }).compile();

    service = module.get<DisasterService>(DisasterService);
  });

  afterEach(async () => {
    await module?.close();
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Initialization Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Initialization", () => {
    it("should be defined", () => {
      expect(service).toBeDefined();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Get Active Disasters Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("getActiveDisasters", () => {
    it("should return all disasters when no filters", async () => {
      const result = await service.getActiveDisasters({});

      expect(result.total).toBeGreaterThan(0);
      expect(result.disasters).toBeDefined();
      expect(Array.isArray(result.disasters)).toBe(true);
    });

    it("should filter by disaster type", async () => {
      const result = await service.getActiveDisasters({
        type: DisasterType.FLOOD,
      });

      expect(result.disasters.every((d) => d.type === DisasterType.FLOOD)).toBe(
        true,
      );
    });

    it("should filter by governorate", async () => {
      const result = await service.getActiveDisasters({
        governorate: "hadramaut",
      });

      expect(result.disasters.every((d) => d.governorate === "hadramaut")).toBe(
        true,
      );
    });

    it("should filter by severity", async () => {
      const result = await service.getActiveDisasters({
        severity: Severity.HIGH,
      });

      expect(result.disasters.every((d) => d.severity === Severity.HIGH)).toBe(
        true,
      );
    });

    it("should include Arabic translations", async () => {
      const result = await service.getActiveDisasters({});

      expect(result.disasters[0].governorateAr).toBeDefined();
      expect(result.disasters[0].typeAr).toBeDefined();
    });

    it("should return empty array when no matches", async () => {
      const result = await service.getActiveDisasters({
        governorate: "nonexistent",
      });

      expect(result.total).toBe(0);
      expect(result.disasters).toEqual([]);
    });

    it("should apply multiple filters", async () => {
      const result = await service.getActiveDisasters({
        type: DisasterType.LOCUST,
        severity: Severity.CRITICAL,
      });

      result.disasters.forEach((d) => {
        expect(d.type).toBe(DisasterType.LOCUST);
        expect(d.severity).toBe(Severity.CRITICAL);
      });
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Get Disaster by ID Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("getDisasterById", () => {
    it("should return disaster when found", async () => {
      const result = await service.getDisasterById("disaster-001");

      expect(result.id).toBe("disaster-001");
      expect(result.type).toBe(DisasterType.FLOOD);
      expect(result.governorateAr).toBeDefined();
      expect(result.typeAr).toBeDefined();
    });

    it("should include affected fields list", async () => {
      const result = await service.getDisasterById("disaster-001");

      expect(result.affectedFields).toBeDefined();
      expect(Array.isArray(result.affectedFields)).toBe(true);
    });

    it("should return error for non-existent disaster", async () => {
      const result = await service.getDisasterById("nonexistent");

      expect(result.error).toBe("Disaster not found");
      expect(result.errorAr).toBe("الكارثة غير موجودة");
    });

    it("should include localized governorate name", async () => {
      const result = await service.getDisasterById("disaster-001");

      expect(result.governorateAr).toBe("حضرموت");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Report Disaster Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("reportDisaster", () => {
    it("should create new disaster successfully", async () => {
      const dto = {
        type: DisasterType.STORM,
        title: "Test Storm",
        description: "Test storm description",
        governorate: "sanaa",
        location: { lat: 15.3, lng: 44.2 },
        affectedRadiusKm: 10,
        severity: Severity.MEDIUM,
        startDate: "2024-12-20T00:00:00Z",
      };

      const result = await service.reportDisaster(dto);

      expect(result.success).toBe(true);
      expect(result.message).toBe("Disaster reported successfully");
      expect(result.messageAr).toBe("تم الإبلاغ عن الكارثة بنجاح");
      expect(result.disaster.id).toBeDefined();
      expect(result.disaster.type).toBe(DisasterType.STORM);
    });

    it("should set status to ACTIVE", async () => {
      const dto = {
        type: DisasterType.DROUGHT,
        title: "Test Drought",
        description: "Test drought description",
        governorate: "marib",
        location: { lat: 15.4, lng: 45.3 },
        affectedRadiusKm: 20,
        severity: Severity.HIGH,
        startDate: "2024-12-20T00:00:00Z",
      };

      const result = await service.reportDisaster(dto);

      expect(result.disaster.status).toBe(DisasterStatus.ACTIVE);
    });

    it("should initialize counts to zero", async () => {
      const dto = {
        type: DisasterType.PEST,
        title: "Test Pest",
        description: "Test pest description",
        governorate: "ibb",
        location: { lat: 13.9, lng: 44.2 },
        affectedRadiusKm: 5,
        severity: Severity.LOW,
        startDate: "2024-12-20T00:00:00Z",
      };

      const result = await service.reportDisaster(dto);

      expect(result.disaster.affectedFieldsCount).toBe(0);
      expect(result.disaster.totalAffectedAreaHectares).toBe(0);
      expect(result.disaster.totalEstimatedLossYER).toBe(0);
    });

    it("should include Arabic translations in response", async () => {
      const dto = {
        type: DisasterType.HAIL,
        title: "Test Hail",
        description: "Test hail description",
        governorate: "taiz",
        location: { lat: 13.6, lng: 44.0 },
        affectedRadiusKm: 8,
        severity: Severity.MEDIUM,
        startDate: "2024-12-20T00:00:00Z",
      };

      const result = await service.reportDisaster(dto);

      expect(result.disaster.governorateAr).toBe("تعز");
      expect(result.disaster.typeAr).toBe("بَرَد");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Assess Field Damage Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("assessFieldDamage", () => {
    it("should assess field damage with provided values", async () => {
      const dto = {
        disasterId: "disaster-001",
        damagePercentage: 45,
        affectedAreaHectares: 10,
        estimatedLossYER: 2000000,
        affectedCropType: "wheat",
        assessmentNotes: "Significant flood damage",
      };

      const result = await service.assessFieldDamage("field-123", dto);

      expect(result.fieldId).toBe("field-123");
      expect(result.disasterId).toBe("disaster-001");
      expect(result.damagePercentage).toBe(45);
      expect(result.affectedAreaHectares).toBe(10);
      expect(result.estimatedLossYER).toBe(2000000);
    });

    it("should determine correct damage level", async () => {
      const testCases = [
        { percentage: 5, expectedLevel: "minimal" },
        { percentage: 15, expectedLevel: "light" },
        { percentage: 35, expectedLevel: "moderate" },
        { percentage: 60, expectedLevel: "severe" },
        { percentage: 90, expectedLevel: "catastrophic" },
      ];

      for (const { percentage, expectedLevel } of testCases) {
        const result = await service.assessFieldDamage("field-123", {
          disasterId: "disaster-001",
          damagePercentage: percentage,
        });

        expect(result.damageLevel).toBe(expectedLevel);
      }
    });

    it("should include Arabic damage level", async () => {
      const result = await service.assessFieldDamage("field-123", {
        disasterId: "disaster-001",
        damagePercentage: 50,
      });

      expect(result.damageLevelAr).toBeDefined();
      expect(typeof result.damageLevelAr).toBe("string");
    });

    it("should determine insurance eligibility", async () => {
      // Below 30% - not eligible
      const result1 = await service.assessFieldDamage("field-123", {
        disasterId: "disaster-001",
        damagePercentage: 25,
      });
      expect(result1.insuranceEligible).toBe(false);
      expect(result1.insuranceClaimAmount).toBe(0);

      // Above 30% - eligible
      const result2 = await service.assessFieldDamage("field-123", {
        disasterId: "disaster-001",
        damagePercentage: 50,
        estimatedLossYER: 1000000,
      });
      expect(result2.insuranceEligible).toBe(true);
      expect(result2.insuranceClaimAmount).toBe(700000); // 70% of loss
    });

    it("should include recommendations", async () => {
      const result = await service.assessFieldDamage("field-123", {
        disasterId: "disaster-001",
        damagePercentage: 40,
      });

      expect(result.recommendations).toBeDefined();
      expect(Array.isArray(result.recommendations)).toBe(true);
      expect(result.recommendationsAr).toBeDefined();
      expect(Array.isArray(result.recommendationsAr)).toBe(true);
    });

    it("should include timestamp", async () => {
      const result = await service.assessFieldDamage("field-123", {
        disasterId: "disaster-001",
      });

      expect(result.assessedAt).toBeDefined();
      // Should be valid ISO date
      expect(() => new Date(result.assessedAt)).not.toThrow();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Flood Risk Map Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("getFloodRiskMap", () => {
    it("should return flood risk data for governorate", async () => {
      const result = await service.getFloodRiskMap("hadramaut");

      expect(result.governorate).toBe("hadramaut");
      expect(result.governorateAr).toBe("حضرموت");
      expect(result.riskZones).toBeDefined();
      expect(Array.isArray(result.riskZones)).toBe(true);
    });

    it("should include risk zone breakdown", async () => {
      const result = await service.getFloodRiskMap("hadramaut");

      const zones = result.riskZones;
      expect(zones.some((z) => z.zone === "high")).toBe(true);
      expect(zones.some((z) => z.zone === "medium")).toBe(true);
      expect(zones.some((z) => z.zone === "low")).toBe(true);
    });

    it("should include Arabic zone names", async () => {
      const result = await service.getFloodRiskMap("hadramaut");

      result.riskZones.forEach((zone) => {
        expect(zone.zoneAr).toBeDefined();
        expect(zone.color).toBeDefined();
        expect(zone.percentage).toBeDefined();
      });
    });

    it("should include area calculations", async () => {
      const result = await service.getFloodRiskMap("hadramaut");

      expect(result.totalAreaHectares).toBeGreaterThan(0);
      expect(result.highRiskAreaHectares).toBeGreaterThan(0);
    });

    it("should include recommendations", async () => {
      const result = await service.getFloodRiskMap("hadramaut");

      expect(result.recommendations).toBeDefined();
      expect(result.recommendations.length).toBeGreaterThan(0);
      expect(result.recommendationsAr).toBeDefined();
      expect(result.recommendationsAr.length).toBeGreaterThan(0);
    });

    it("should include data source information", async () => {
      const result = await service.getFloodRiskMap("hadramaut");

      expect(result.dataSource).toBeDefined();
      expect(result.dataSourceAr).toBeDefined();
      expect(result.lastUpdated).toBeDefined();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Drought Index Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("getDroughtIndex", () => {
    it("should return drought index for governorate", async () => {
      const result = await service.getDroughtIndex("marib");

      expect(result.governorate).toBe("marib");
      expect(result.governorateAr).toBe("مأرب");
      expect(result.indexType).toBe("SPI");
      expect(typeof result.indexValue).toBe("number");
    });

    it("should include status and color", async () => {
      const result = await service.getDroughtIndex("marib");

      expect(result.status).toBeDefined();
      expect(result.statusAr).toBeDefined();
      expect(result.color).toBeDefined();
      expect(result.color).toMatch(/^#[0-9a-fA-F]{6}$/);
    });

    it("should include historical comparison", async () => {
      const result = await service.getDroughtIndex("marib");

      expect(result.historicalComparison).toBeDefined();
      expect(result.historicalComparison.lastMonth).toBeDefined();
      expect(result.historicalComparison.lastYear).toBeDefined();
      expect(result.historicalComparison.fiveYearAvg).toBeDefined();
    });

    it("should include forecast", async () => {
      const result = await service.getDroughtIndex("marib");

      expect(result.forecast).toBeDefined();
      expect(result.forecast.nextMonth).toBeDefined();
      expect(result.forecast.nextMonthAr).toBeDefined();
    });

    it("should include data source", async () => {
      const result = await service.getDroughtIndex("marib");

      expect(result.dataSource).toBeDefined();
      expect(result.dataSourceAr).toBeDefined();
      expect(result.lastUpdated).toBeDefined();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Statistics Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("getStatistics", () => {
    it("should return statistics for current year by default", async () => {
      const currentYear = new Date().getFullYear();
      const result = await service.getStatistics({});

      expect(result.year).toBe(currentYear);
      expect(result.governorate).toBe("all");
      expect(result.governorateAr).toBe("جميع المحافظات");
    });

    it("should filter by year", async () => {
      const result = await service.getStatistics({ year: 2023 });

      expect(result.year).toBe(2023);
    });

    it("should filter by governorate", async () => {
      const result = await service.getStatistics({ governorate: "sanaa" });

      expect(result.governorate).toBe("sanaa");
      expect(result.governorateAr).toBe("صنعاء");
    });

    it("should include summary statistics", async () => {
      const result = await service.getStatistics({});

      expect(result.summary).toBeDefined();
      expect(result.summary.totalDisasters).toBeDefined();
      expect(result.summary.activeDisasters).toBeDefined();
      expect(result.summary.resolvedDisasters).toBeDefined();
      expect(result.summary.totalAffectedAreaHectares).toBeDefined();
      expect(result.summary.totalEstimatedLossYER).toBeDefined();
      expect(result.summary.totalFieldsAffected).toBeDefined();
      expect(result.summary.farmersAffected).toBeDefined();
    });

    it("should include breakdown by type", async () => {
      const result = await service.getStatistics({});

      expect(result.byType).toBeDefined();
      expect(Array.isArray(result.byType)).toBe(true);
      result.byType.forEach((item) => {
        expect(item.type).toBeDefined();
        expect(item.typeAr).toBeDefined();
        expect(item.count).toBeDefined();
        expect(item.lossYER).toBeDefined();
      });
    });

    it("should include breakdown by month", async () => {
      const result = await service.getStatistics({});

      expect(result.byMonth).toBeDefined();
      expect(result.byMonth.length).toBe(12);
      result.byMonth.forEach((item) => {
        expect(item.month).toBeGreaterThanOrEqual(1);
        expect(item.month).toBeLessThanOrEqual(12);
        expect(item.count).toBeDefined();
        expect(item.lossYER).toBeDefined();
      });
    });

    it("should include trend information", async () => {
      const result = await service.getStatistics({});

      expect(result.trend).toBeDefined();
      expect(result.trendAr).toBeDefined();
      expect(result.comparedToLastYear).toBeDefined();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Disaster Type Translations Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Disaster Type Translations", () => {
    it("should have Arabic translations for all disaster types", async () => {
      const types = [
        DisasterType.FLOOD,
        DisasterType.DROUGHT,
        DisasterType.FROST,
        DisasterType.HAIL,
        DisasterType.STORM,
        DisasterType.PEST,
        DisasterType.DISEASE,
        DisasterType.LOCUST,
        DisasterType.WILDFIRE,
      ];

      for (const type of types) {
        const dto = {
          type,
          title: "Test",
          description: "Test",
          governorate: "sanaa",
          location: { lat: 15.3, lng: 44.2 },
          affectedRadiusKm: 10,
          severity: Severity.LOW,
          startDate: "2024-12-20T00:00:00Z",
        };

        const result = await service.reportDisaster(dto);
        expect(result.disaster.typeAr).toBeDefined();
        expect(result.disaster.typeAr.length).toBeGreaterThan(0);
      }
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Governorate Translations Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Governorate Translations", () => {
    it("should have Arabic translations for major governorates", async () => {
      const governorates = [
        { en: "sanaa", ar: "صنعاء" },
        { en: "aden", ar: "عدن" },
        { en: "taiz", ar: "تعز" },
        { en: "hodeidah", ar: "الحديدة" },
        { en: "hadramaut", ar: "حضرموت" },
        { en: "marib", ar: "مأرب" },
      ];

      for (const { en, ar } of governorates) {
        const result = await service.getFloodRiskMap(en);
        expect(result.governorateAr).toBe(ar);
      }
    });
  });
});
