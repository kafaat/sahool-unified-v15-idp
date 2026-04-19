/**
 * Tests for the ported yield-engine crop-catalog endpoints.
 *
 *   GET /api/v1/yield/crops                — list supported crops
 *   GET /api/v1/yield/price/:cropType      — per-crop reference price
 *
 * Instantiated directly via TestingModule so the tests don't require a
 * live DB / JWT — the controller + catalog module are pure functions.
 */

import { Test, TestingModule } from "@nestjs/testing";
import { NotFoundException } from "@nestjs/common";

// AuthModule.forRoot() validates JWT_SECRET_KEY at import time.
process.env.JWT_SECRET_KEY = "test-secret-key-for-unit-tests-only-32chars";

import { YieldController } from "../yield/yield.controller";
import { YieldService } from "../yield/yield.service";
import {
  CROP_CATALOG,
  SUPPORTED_CROP_IDS,
  USD_TO_YER,
} from "../yield/crop-catalog";

describe("YieldController - Crop Catalog (ported from yield-engine)", () => {
  let controller: YieldController;

  beforeAll(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [YieldController],
      // Stub YieldService — the two endpoints under test don't touch it.
      providers: [{ provide: YieldService, useValue: {} }],
    }).compile();

    controller = module.get<YieldController>(YieldController);
  });

  describe("GET /crops", () => {
    it("returns one entry per supported crop with all catalog fields", () => {
      const crops = controller.listSupportedCrops();

      expect(crops).toHaveLength(SUPPORTED_CROP_IDS.length);
      for (const entry of crops) {
        expect(entry).toEqual(
          expect.objectContaining({
            crop_id: expect.any(String),
            name_ar: expect.any(String),
            base_yield_per_hectare: expect.any(Number),
            target_yield: expect.any(Number),
            price_usd_per_ton: expect.any(Number),
            growing_season_days: expect.any(Number),
            water_requirement: expect.any(String),
          }),
        );
      }
    });

    it("includes the Yemen-signature crops (coffee, date_palm, sorghum)", () => {
      const ids = controller.listSupportedCrops().map((c) => c.crop_id);
      expect(ids).toEqual(expect.arrayContaining(["coffee", "date_palm", "sorghum"]));
    });

    it("preserves the 29-crop count and Arabic labels match the catalog", () => {
      // 5 cereals + 3 legumes + 8 vegetables + 9 fruits + 3 cash crops + 1
      // fodder = 29, matching the CropType enum in the archived yield-engine.
      const crops = controller.listSupportedCrops();
      expect(crops).toHaveLength(29);
      const coffee = crops.find((c) => c.crop_id === "coffee");
      expect(coffee?.name_ar).toBe("بن يمني");
      // Preserves the high reference price that makes Yemeni coffee notable
      // (archive yield-engine: $8000/t vs next-highest sesame $2000/t).
      expect(coffee?.price_usd_per_ton).toBe(8000);
    });
  });

  describe("GET /price/:cropType", () => {
    it("returns USD + YER price + timestamp for a known crop", () => {
      const result = controller.getCropPrice("wheat");

      expect(result.crop_type).toBe("wheat");
      expect(result.name_ar).toBe("قمح");
      expect(result.price_usd_per_ton).toBe(350);
      expect(result.price_yer_per_ton).toBe(350 * USD_TO_YER);
      // ISO-8601 with timezone offset
      expect(result.last_updated).toMatch(/^\d{4}-\d{2}-\d{2}T.+Z$/);
    });

    it("uses the shared USD_TO_YER rate for YER conversion", () => {
      const { price_usd_per_ton, price_yer_per_ton } =
        controller.getCropPrice("coffee");
      // Derives rigorously from the shared constant — catches any future
      // silent divergence between controller and catalog.
      expect(price_yer_per_ton / price_usd_per_ton).toBeCloseTo(USD_TO_YER, 6);
    });

    it("throws NotFoundException for an unsupported crop id", () => {
      expect(() => controller.getCropPrice("quinoa")).toThrow(NotFoundException);
      expect(() => controller.getCropPrice("")).toThrow(NotFoundException);
    });

    it("points callers at /crops in the error message", () => {
      try {
        controller.getCropPrice("unobtanium");
        fail("expected NotFoundException");
      } catch (e: any) {
        expect(e).toBeInstanceOf(NotFoundException);
        expect(e.message).toMatch(/\/api\/v1\/yield\/crops/);
      }
    });
  });

  describe("CROP_CATALOG integrity", () => {
    it("every catalog entry has a matching entry in SUPPORTED_CROP_IDS", () => {
      const catalogKeys = new Set(Object.keys(CROP_CATALOG));
      const supported = new Set(SUPPORTED_CROP_IDS);
      expect(catalogKeys).toEqual(supported);
    });

    it("every water_requirement is one of the declared literal values", () => {
      const allowed = new Set([
        "very_low",
        "low",
        "medium",
        "high",
        "very_high",
      ]);
      for (const [, info] of Object.entries(CROP_CATALOG)) {
        expect(allowed.has(info.water_requirement)).toBe(true);
      }
    });
  });
});
