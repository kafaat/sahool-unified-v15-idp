/**
 * Unit Tests for Agricultural Utilities
 * اختبارات وحدة للأدوات الزراعية
 */

import { describe, it, expect } from "vitest";
import {
  // Coordinates
  isValidCoordinate,
  isMiddleEastCoordinate,
  isYemenCoordinate,
  calculateDistance,
  // Area
  convertArea,
  calculatePolygonArea,
  // NDVI
  classifyNDVI,
  ndviToHealthScore,
  // Soil moisture
  classifySoilMoisture,
  // Weather
  calculateET0,
  calculateGDD,
  assessFrostRisk,
  // Crop stages
  getWheatGrowthStage,
  // Validation
  isValidMiddleEastPhone,
  isValidFieldId,
  isValidFarmId,
} from "../agricultural";

describe("Agricultural Utilities", () => {
  describe("Coordinate Utilities", () => {
    it("should validate coordinates", () => {
      expect(isValidCoordinate(15.5, 44.2)).toBe(true);
      expect(isValidCoordinate(-90, -180)).toBe(true);
      expect(isValidCoordinate(90, 180)).toBe(true);
      expect(isValidCoordinate(91, 0)).toBe(false);
      expect(isValidCoordinate(0, 181)).toBe(false);
      expect(isValidCoordinate(NaN, 0)).toBe(false);
    });

    it("should check Middle East coordinates", () => {
      // Riyadh, Saudi Arabia
      expect(isMiddleEastCoordinate(24.7136, 46.6753)).toBe(true);
      // Sanaa, Yemen
      expect(isMiddleEastCoordinate(15.3694, 44.191)).toBe(true);
      // New York (outside Middle East)
      expect(isMiddleEastCoordinate(40.7128, -74.006)).toBe(false);
    });

    it("should check Yemen coordinates", () => {
      // Sanaa
      expect(isYemenCoordinate(15.3694, 44.191)).toBe(true);
      // Aden
      expect(isYemenCoordinate(12.7855, 45.0187)).toBe(true);
      // Dubai (outside Yemen)
      expect(isYemenCoordinate(25.2048, 55.2708)).toBe(false);
    });

    it("should calculate distance between coordinates", () => {
      // Sanaa to Aden (approximately 350 km)
      const distance = calculateDistance(
        { latitude: 15.3694, longitude: 44.191 },
        { latitude: 12.7855, longitude: 45.0187 },
      );
      expect(distance).toBeGreaterThan(300);
      expect(distance).toBeLessThan(400);
    });
  });

  describe("Area Utilities", () => {
    it("should convert area units", () => {
      // 1 hectare = 10 dunum
      expect(convertArea(1, "hectare", "dunum")).toBeCloseTo(10);
      // 1 dunum = 0.1 hectare
      expect(convertArea(10, "dunum", "hectare")).toBeCloseTo(1);
      // 1 hectare = 10000 sqm
      expect(convertArea(1, "hectare", "sqm")).toBeCloseTo(10000);
      // 1 acre ≈ 0.4047 hectare
      expect(convertArea(1, "acre", "hectare")).toBeCloseTo(0.4047);
    });

    it("should calculate polygon area", () => {
      // Small square field (approximately 1 hectare)
      const square = [
        { latitude: 15.0, longitude: 44.0 },
        { latitude: 15.0, longitude: 44.001 },
        { latitude: 15.001, longitude: 44.001 },
        { latitude: 15.001, longitude: 44.0 },
      ];
      const area = calculatePolygonArea(square);
      // Should be approximately 1 hectare (1.2 ha ± tolerance)
      expect(area).toBeGreaterThan(0.5);
      expect(area).toBeLessThan(2);
    });

    it("should return 0 for invalid polygons", () => {
      expect(calculatePolygonArea([])).toBe(0);
      expect(
        calculatePolygonArea([
          { latitude: 0, longitude: 0 },
          { latitude: 1, longitude: 1 },
        ]),
      ).toBe(0);
    });
  });

  describe("NDVI Utilities", () => {
    it("should classify NDVI values", () => {
      expect(classifyNDVI(-0.5).label).toBe("Water/No Data");
      expect(classifyNDVI(0.05).label).toBe("Bare Soil");
      expect(classifyNDVI(0.15).label).toBe("Sparse Vegetation");
      expect(classifyNDVI(0.3).label).toBe("Moderate Vegetation");
      expect(classifyNDVI(0.5).label).toBe("Dense Vegetation");
      expect(classifyNDVI(0.8).label).toBe("Very Dense Vegetation");
    });

    it("should have Arabic labels", () => {
      expect(classifyNDVI(0.5).labelAr).toBe("غطاء نباتي كثيف");
    });

    it("should convert NDVI to health score", () => {
      expect(ndviToHealthScore(-0.1)).toBe(0);
      expect(ndviToHealthScore(0)).toBe(0);
      expect(ndviToHealthScore(0.4)).toBe(50);
      expect(ndviToHealthScore(0.8)).toBe(100);
      expect(ndviToHealthScore(1.0)).toBe(100);
    });
  });

  describe("Soil Moisture Utilities", () => {
    it("should classify soil moisture", () => {
      expect(classifySoilMoisture(10).status).toBe("very_dry");
      expect(classifySoilMoisture(10).needsIrrigation).toBe(true);

      expect(classifySoilMoisture(30).status).toBe("dry");
      expect(classifySoilMoisture(30).needsIrrigation).toBe(true);

      expect(classifySoilMoisture(50).status).toBe("optimal");
      expect(classifySoilMoisture(50).needsIrrigation).toBe(false);

      expect(classifySoilMoisture(70).status).toBe("wet");
      expect(classifySoilMoisture(85).status).toBe("very_wet");
    });

    it("should adjust thresholds for crop types", () => {
      // Rice needs more water
      expect(classifySoilMoisture(50, "rice").status).toBe("dry");
      expect(classifySoilMoisture(70, "rice").status).toBe("optimal");

      // Date palms are drought tolerant
      expect(classifySoilMoisture(30, "date palm").status).toBe("optimal");
    });

    it("should have Arabic status labels", () => {
      expect(classifySoilMoisture(50).statusAr).toBe("مثالي");
    });
  });

  describe("Weather Utilities", () => {
    it("should calculate ET0", () => {
      // Summer day at latitude 15°N
      const et0 = calculateET0(25, 40, 15, 180);
      expect(et0).toBeGreaterThan(0);
      expect(et0).toBeLessThan(15);
    });

    it("should calculate GDD", () => {
      expect(calculateGDD(10, 30, 10)).toBe(10); // Mean 20, base 10 = GDD 10
      expect(calculateGDD(5, 15, 10)).toBe(0); // Mean 10, base 10 = GDD 0
      expect(calculateGDD(15, 25, 10)).toBe(10); // Mean 20, base 10 = GDD 10
    });

    it("should assess frost risk", () => {
      expect(assessFrostRisk(10).risk).toBe("none");
      expect(assessFrostRisk(3).risk).toBe("low");
      expect(assessFrostRisk(1).risk).toBe("moderate");
      expect(assessFrostRisk(-1).risk).toBe("high");
      expect(assessFrostRisk(-5).risk).toBe("severe");
    });

    it("should have Arabic risk labels", () => {
      expect(assessFrostRisk(-1).riskAr).toBe("مرتفع");
    });
  });

  describe("Crop Stage Utilities", () => {
    it("should identify wheat growth stages", () => {
      expect(getWheatGrowthStage(5).stage).toBe("germination");
      expect(getWheatGrowthStage(15).stage).toBe("seedling");
      expect(getWheatGrowthStage(35).stage).toBe("tillering");
      expect(getWheatGrowthStage(60).stage).toBe("stem_elongation");
      expect(getWheatGrowthStage(85).stage).toBe("booting");
      expect(getWheatGrowthStage(95).stage).toBe("heading");
      expect(getWheatGrowthStage(105).stage).toBe("flowering");
      expect(getWheatGrowthStage(120).stage).toBe("grain_filling");
      expect(getWheatGrowthStage(145).stage).toBe("ripening");
    });

    it("should have Arabic stage labels", () => {
      expect(getWheatGrowthStage(35).stageAr).toBe("التفريع");
    });

    it("should calculate days remaining to next stage", () => {
      const stage = getWheatGrowthStage(35);
      expect(stage.daysRemaining).toBeGreaterThan(0);
    });

    it("should adjust for variety", () => {
      const earlyVariety = getWheatGrowthStage(45, "early");
      const lateVariety = getWheatGrowthStage(45, "late");

      // Early variety should be further along
      expect(earlyVariety.daysRemaining).toBeLessThanOrEqual(lateVariety.daysRemaining);
    });
  });

  describe("Validation Utilities", () => {
    it("should validate Middle East phone numbers", () => {
      // Yemen
      expect(isValidMiddleEastPhone("+967712345678")).toBe(true);
      expect(isValidMiddleEastPhone("00967712345678")).toBe(true);
      expect(isValidMiddleEastPhone("967712345678")).toBe(true);

      // Saudi Arabia
      expect(isValidMiddleEastPhone("+966512345678", "SA")).toBe(true);

      // Invalid
      expect(isValidMiddleEastPhone("123456")).toBe(false);
    });

    it("should validate field IDs", () => {
      expect(isValidFieldId("FIELD-001")).toBe(true);
      expect(isValidFieldId("FLD-ABC123")).toBe(true);
      expect(isValidFieldId("field-001")).toBe(true);
      expect(isValidFieldId("invalid")).toBe(false);
      expect(isValidFieldId("FIELD-")).toBe(false);
    });

    it("should validate farm IDs", () => {
      expect(isValidFarmId("FARM-001")).toBe(true);
      expect(isValidFarmId("FARM-ABC123")).toBe(true);
      expect(isValidFarmId("invalid")).toBe(false);
    });
  });
});
