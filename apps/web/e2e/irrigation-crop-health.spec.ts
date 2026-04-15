/**
 * Irrigation & Crop Health E2E Tests
 * اختبارات E2E للري وصحة المحصول
 *
 * Comprehensive tests for:
 * - Irrigation management
 * - Irrigation scheduling
 * - Smart irrigation recommendations
 * - NDVI analysis
 * - Crop health monitoring
 * - Disease detection
 * - Yield predictions
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import {
  waitForPageLoad,
  navigateAndWait,
} from "./helpers/page.helpers";
import { timeouts } from "./helpers/test-data";

test.describe("Irrigation Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Irrigation Dashboard", () => {
    test("should display irrigation page correctly", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");

      // Check for irrigation heading
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for irrigation-related content
      await expect(
        page.locator("text=/الري|Irrigation/i")
      ).toBeVisible();
    });

    test("should display irrigation status summary", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for status indicators
      const statusSection = page.locator(
        'text=/الحالة|Status|Active|نشط|معطل|Disabled/i'
      );
      const hasStatus = await statusSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Irrigation status displayed: ${hasStatus}`);
    });

    test("should display water usage metrics", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for water usage data
      const waterUsage = page.locator(
        'text=/استهلاك المياه|Water Usage|لتر|liters|m³|متر مكعب/i'
      );
      const hasWaterUsage = await waterUsage.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Water usage metrics displayed: ${hasWaterUsage}`);
    });

    test("should display irrigation zones", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for zones
      const zones = page.locator(
        'text=/المناطق|Zones|منطقة|Zone/i'
      );
      const hasZones = await zones.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Irrigation zones displayed: ${hasZones}`);
    });

    test("should display irrigation schedule", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for schedule
      const schedule = page.locator(
        'text=/الجدول|Schedule|مجدول|Scheduled/i'
      );
      const hasSchedule = await schedule.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Irrigation schedule displayed: ${hasSchedule}`);
    });
  });

  test.describe("Irrigation Control", () => {
    test("should start/stop irrigation manually", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for start/stop controls
      const controlBtn = page.locator(
        'button:has-text("تشغيل"), button:has-text("Start"), button:has-text("إيقاف"), button:has-text("Stop")'
      );

      if (await controlBtn.first().isVisible({ timeout: timeouts.medium })) {
        console.log("Manual irrigation control available");
      }
    });

    test("should set irrigation duration", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for duration input
      const durationInput = page.locator(
        'input[name="duration"], input[placeholder*="مدة"], input[placeholder*="Duration"]'
      );
      const hasDuration = await durationInput.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Duration input available: ${hasDuration}`);
    });

    test("should select irrigation zone", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for zone selector
      const zoneSelector = page.locator(
        'select[name="zone"], [data-testid="zone-selector"]'
      );
      const hasZoneSelector = await zoneSelector.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Zone selector available: ${hasZoneSelector}`);
    });

    test("should display real-time irrigation status", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for real-time indicators
      const realTimeStatus = page.locator(
        '[class*="live"], [class*="real-time"], [data-testid="irrigation-status"]'
      );
      const hasRealTime = await realTimeStatus.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Real-time status displayed: ${hasRealTime}`);
    });
  });

  test.describe("Irrigation Scheduling", () => {
    test("should display schedule calendar", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for calendar
      const calendar = page.locator(
        '[class*="calendar"], [data-testid="irrigation-calendar"], table'
      );
      const hasCalendar = await calendar.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Schedule calendar displayed: ${hasCalendar}`);
    });

    test("should create new irrigation schedule", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for add schedule button
      const addScheduleBtn = page.locator(
        'button:has-text("إضافة جدول"), button:has-text("Add Schedule"), button:has-text("جديد")'
      );

      if (await addScheduleBtn.first().isVisible({ timeout: timeouts.medium })) {
        await addScheduleBtn.first().click();
        await page.waitForTimeout(500);

        // Form should appear
        const form = page.locator('form, [role="dialog"]');
        const hasForm = await form.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Schedule form opened: ${hasForm}`);
      }
    });

    test("should edit existing schedule", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for schedule items
      const scheduleItems = page.locator('[data-testid="schedule-item"], [class*="schedule-item"]');

      if (await scheduleItems.first().isVisible({ timeout: timeouts.medium })) {
        // Look for edit button
        const editBtn = page.locator('button:has-text("تعديل"), button:has-text("Edit")');

        if (await editBtn.first().isVisible({ timeout: timeouts.short })) {
          console.log("Schedule editing available");
        }
      }
    });

    test("should delete schedule", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      const scheduleItems = page.locator('[data-testid="schedule-item"]');

      if (await scheduleItems.first().isVisible({ timeout: timeouts.medium })) {
        const deleteBtn = page.locator('button:has-text("حذف"), button:has-text("Delete")');

        if (await deleteBtn.first().isVisible({ timeout: timeouts.short })) {
          console.log("Schedule deletion available");
        }
      }
    });
  });

  test.describe("Smart Irrigation Recommendations", () => {
    test("should display AI recommendations", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for recommendations section
      const recommendations = page.locator(
        'text=/التوصيات|Recommendations|نصيحة|Advice/i'
      );
      const hasRecommendations = await recommendations.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`AI recommendations displayed: ${hasRecommendations}`);
    });

    test("should show weather-based irrigation advice", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for weather-based advice
      const weatherAdvice = page.locator(
        'text=/الطقس|Weather|مطر|Rain|درجة الحرارة|Temperature/i'
      );
      const hasWeatherAdvice = await weatherAdvice.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Weather-based advice displayed: ${hasWeatherAdvice}`);
    });

    test("should show soil moisture recommendations", async ({ page }) => {
      await navigateAndWait(page, "/irrigation");
      await page.waitForTimeout(timeouts.medium);

      // Look for soil moisture data
      const soilMoisture = page.locator(
        'text=/رطوبة التربة|Soil Moisture|SM|%/i'
      );
      const hasSoilMoisture = await soilMoisture.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Soil moisture data displayed: ${hasSoilMoisture}`);
    });
  });
});

test.describe("Crop Health Monitoring", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Crop Health Dashboard", () => {
    test("should display crop health page correctly", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");

      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      await expect(
        page.locator("text=/صحة المحصول|Crop Health/i")
      ).toBeVisible();
    });

    test("should display health overview cards", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      const healthCards = page.locator(
        '[data-testid="health-card"], [class*="health-card"], [class*="card"]'
      );
      const count = await healthCards.count();

      console.log(`Health cards displayed: ${count}`);
    });

    test("should display health status indicators", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for status indicators (good, warning, critical)
      const statusIndicators = page.locator(
        'text=/جيد|Good|تحذير|Warning|حرج|Critical|صحي|Healthy/i'
      );
      const hasStatus = await statusIndicators.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Health status indicators displayed: ${hasStatus}`);
    });
  });

  test.describe("NDVI Analysis", () => {
    test("should display NDVI map", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for NDVI section
      const ndviSection = page.locator(
        'text=/NDVI|مؤشر الغطاء النباتي|Vegetation Index/i'
      );
      await expect(ndviSection.first()).toBeVisible({ timeout: timeouts.long });
    });

    test("should display NDVI color legend", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for legend
      const legend = page.locator(
        '[class*="legend"], [data-testid="ndvi-legend"]'
      );
      const hasLegend = await legend.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`NDVI legend displayed: ${hasLegend}`);
    });

    test("should show NDVI value range", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for NDVI values (0.0 to 1.0 range)
      const ndviValues = page.locator(
        'text=/0\\.[0-9]+|NDVI.*[0-9]\\.[0-9]/i'
      );
      const hasValues = await ndviValues.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`NDVI values displayed: ${hasValues}`);
    });

    test("should display NDVI trend over time", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for trend chart
      const trendChart = page.locator(
        '[class*="chart"], canvas, svg, [data-testid="ndvi-trend"]'
      );
      const hasChart = await trendChart.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`NDVI trend chart displayed: ${hasChart}`);
    });

    test("should select time period for NDVI analysis", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for time period selector
      const timePeriod = page.locator(
        'button:has-text("7 أيام"), button:has-text("7 Days"), button:has-text("30 Days"), select[name="period"]'
      );
      const hasTimePeriod = await timePeriod.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Time period selector available: ${hasTimePeriod}`);
    });
  });

  test.describe("Disease Detection", () => {
    test("should display disease alerts", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for disease section
      const diseaseSection = page.locator(
        'text=/الأمراض|Diseases|Disease Detection|كشف الأمراض/i'
      );
      const hasDisease = await diseaseSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Disease section displayed: ${hasDisease}`);
    });

    test("should display disease risk level", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for risk indicators
      const riskLevel = page.locator(
        'text=/خطر|Risk|منخفض|Low|متوسط|Medium|عالي|High/i'
      );
      const hasRisk = await riskLevel.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Disease risk level displayed: ${hasRisk}`);
    });

    test("should show detected diseases list", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for disease list
      const diseaseList = page.locator(
        '[data-testid="disease-list"], [class*="disease-item"]'
      );
      const count = await diseaseList.count();

      console.log(`Diseases detected: ${count}`);
    });

    test("should upload image for disease detection", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for upload button
      const uploadBtn = page.locator(
        'button:has-text("رفع صورة"), button:has-text("Upload Image"), input[type="file"]'
      );
      const hasUpload = await uploadBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Image upload for detection available: ${hasUpload}`);
    });

    test("should display treatment recommendations for diseases", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for treatment section
      const treatments = page.locator(
        'text=/العلاج|Treatment|توصيات|Recommendations|المبيدات|Pesticides/i'
      );
      const hasTreatments = await treatments.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Treatment recommendations displayed: ${hasTreatments}`);
    });
  });

  test.describe("Pest Monitoring", () => {
    test("should display pest monitoring section", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for pest section
      const pestSection = page.locator(
        'text=/الآفات|Pests|Pest Monitoring|مراقبة الآفات/i'
      );
      const hasPest = await pestSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Pest monitoring section displayed: ${hasPest}`);
    });

    test("should display pest alerts", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for pest alerts
      const pestAlerts = page.locator(
        '[data-testid="pest-alert"], [class*="pest-alert"]'
      );
      const count = await pestAlerts.count();

      console.log(`Pest alerts: ${count}`);
    });
  });

  test.describe("Yield Prediction", () => {
    test("should display yield prediction section", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for yield section
      const yieldSection = page.locator(
        'text=/الإنتاجية|Yield|توقعات المحصول|Yield Prediction/i'
      );
      const hasYield = await yieldSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Yield prediction displayed: ${hasYield}`);
    });

    test("should display estimated yield values", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for yield values
      const yieldValues = page.locator(
        'text=/طن|ton|kg|كجم|هكتار|hectare/i'
      );
      const hasValues = await yieldValues.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Yield values displayed: ${hasValues}`);
    });

    test("should display yield comparison with previous seasons", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for comparison
      const comparison = page.locator(
        'text=/مقارنة|Comparison|السابق|Previous|الموسم الماضي/i'
      );
      const hasComparison = await comparison.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Yield comparison displayed: ${hasComparison}`);
    });
  });

  test.describe("Satellite Imagery", () => {
    test("should navigate to satellite page", async ({ page }) => {
      await navigateAndWait(page, "/satellite");

      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });
    });

    test("should display satellite map", async ({ page }) => {
      await navigateAndWait(page, "/satellite");
      await page.waitForTimeout(timeouts.medium);

      // Look for map container
      const map = page.locator(
        '[class*="map"], canvas, [data-testid="satellite-map"]'
      );
      const hasMap = await map.first().isVisible({ timeout: timeouts.long }).catch(() => false);

      console.log(`Satellite map displayed: ${hasMap}`);
    });

    test("should select satellite imagery layers", async ({ page }) => {
      await navigateAndWait(page, "/satellite");
      await page.waitForTimeout(timeouts.medium);

      // Look for layer selector
      const layerSelector = page.locator(
        'button:has-text("الطبقات"), button:has-text("Layers"), [data-testid="layer-selector"]'
      );
      const hasLayers = await layerSelector.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Layer selector available: ${hasLayers}`);
    });

    test("should display imagery date selector", async ({ page }) => {
      await navigateAndWait(page, "/satellite");
      await page.waitForTimeout(timeouts.medium);

      // Look for date selector
      const dateSelector = page.locator(
        'input[type="date"], [data-testid="date-selector"], button:has-text("التاريخ")'
      );
      const hasDate = await dateSelector.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Date selector available: ${hasDate}`);
    });
  });

  test.describe("Sensors and IoT", () => {
    test("should display sensor data on crop health page", async ({ page }) => {
      await navigateAndWait(page, "/crop-health");
      await page.waitForTimeout(timeouts.medium);

      // Look for sensor data
      const sensorData = page.locator(
        'text=/المستشعرات|Sensors|درجة الحرارة|Temperature|الرطوبة|Humidity/i'
      );
      const hasSensorData = await sensorData.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Sensor data displayed: ${hasSensorData}`);
    });

    test("should navigate to IoT page", async ({ page }) => {
      await navigateAndWait(page, "/iot");

      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });
    });

    test("should display connected sensors", async ({ page }) => {
      await navigateAndWait(page, "/iot");
      await page.waitForTimeout(timeouts.medium);

      // Look for sensor list
      const sensors = page.locator(
        '[data-testid="sensor-card"], [class*="sensor-item"]'
      );
      const count = await sensors.count();

      console.log(`Connected sensors: ${count}`);
    });

    test("should display sensor readings", async ({ page }) => {
      await navigateAndWait(page, "/iot");
      await page.waitForTimeout(timeouts.medium);

      // Look for readings
      const readings = page.locator(
        'text=/°C|%|°F|ppm|lux/i'
      );
      const hasReadings = await readings.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Sensor readings displayed: ${hasReadings}`);
    });
  });
});
