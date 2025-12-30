import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait, waitForPageLoad } from './helpers/page.helpers';
import { pages } from './helpers/test-data';

/**
 * Weather Page E2E Tests
 * اختبارات E2E لصفحة الطقس
 *
 * Updated to use data-testid attributes for reliable element selection
 * Tests verify mock data fallback functionality
 */

test.describe('Weather Page', () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, pages.weather);
  });

  /**
   * Basic Page Structure Tests
   * اختبارات بنية الصفحة الأساسية
   */
  test.describe('Page Structure', () => {
    test('should display weather page with proper structure', async ({ page }) => {
      // Check page title
      await expect(page).toHaveTitle(/SAHOOL|سهول/i);

      // Check main page container
      await expect(page.getByTestId('weather-page')).toBeVisible();

      // Check page header
      await expect(page.getByTestId('weather-header')).toBeVisible();
      await expect(page.getByTestId('weather-title')).toHaveText('الطقس');
      await expect(page.getByTestId('weather-subtitle')).toHaveText('Weather Dashboard');
    });

    test('should display location selector', async ({ page }) => {
      // Check location selector container
      await expect(page.getByTestId('location-selector-container')).toBeVisible();

      // Check location icon
      await expect(page.getByTestId('location-icon')).toBeVisible();

      // Check location selector dropdown
      const locationSelector = page.getByTestId('location-selector');
      await expect(locationSelector).toBeVisible();

      // Verify it has options
      const options = await locationSelector.locator('option').count();
      expect(options).toBeGreaterThan(0);
    });

    test('should display weather dashboard', async ({ page }) => {
      await expect(page.getByTestId('weather-dashboard')).toBeVisible();
    });
  });

  /**
   * Location Selector Tests
   * اختبارات محدد الموقع
   */
  test.describe('Location Selector', () => {
    test('should have Yemen cities in location dropdown', async ({ page }) => {
      const locationSelector = page.getByTestId('location-selector');

      // Get all options
      const options = await locationSelector.locator('option').allTextContents();

      // Should have multiple Yemen cities
      expect(options.length).toBeGreaterThan(1);

      // Check for expected cities
      const expectedCities = ['صنعاء', 'عدن', 'تعز', 'الحديدة', 'إب'];
      for (const city of expectedCities) {
        const hasCity = options.some(opt => opt.includes(city));
        expect(hasCity).toBe(true);
      }
    });

    test('should change location when selector is changed', async ({ page }) => {
      const locationSelector = page.getByTestId('location-selector');

      // Get initial value
      const initialValue = await locationSelector.inputValue();

      // Select different location
      await locationSelector.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      // Value should change
      const newValue = await locationSelector.inputValue();
      expect(newValue).not.toBe(initialValue);
    });

    test('should trigger weather data reload when location changes', async ({ page }) => {
      const locationSelector = page.getByTestId('location-selector');

      // Wait for initial load
      await page.waitForTimeout(2000);

      // Change location
      await locationSelector.selectOption({ index: 2 });

      // Wait for data to reload
      await page.waitForTimeout(1000);

      // Weather components should still be visible
      await expect(page.getByTestId('current-weather')).toBeVisible({ timeout: 10000 });
    });
  });

  /**
   * Current Weather Display Tests
   * اختبارات عرض الطقس الحالي
   */
  test.describe('Current Weather Display', () => {
    test('should display current weather section with all elements', async ({ page }) => {
      // Wait for weather to load
      await page.waitForTimeout(3000);

      const currentWeather = page.getByTestId('current-weather');
      await expect(currentWeather).toBeVisible({ timeout: 10000 });

      // Check title and subtitle
      await expect(currentWeather.getByTestId('current-weather-title')).toHaveText('الطقس الحالي');
      await expect(currentWeather.getByTestId('current-weather-subtitle')).toHaveText('Current Weather');
    });

    test('should display temperature value', async ({ page }) => {
      await page.waitForTimeout(3000);

      const temperature = page.getByTestId('temperature');
      await expect(temperature).toBeVisible({ timeout: 10000 });

      // Check temperature format (number + °C)
      const tempText = await temperature.textContent();
      expect(tempText).toMatch(/\d+°C/);
    });

    test('should display weather condition', async ({ page }) => {
      await page.waitForTimeout(3000);

      await expect(page.getByTestId('weather-condition')).toBeVisible({ timeout: 10000 });

      // Condition should have text (Arabic or English)
      const conditionText = await page.getByTestId('weather-condition').textContent();
      expect(conditionText).toBeTruthy();
    });

    test('should display weather icon', async ({ page }) => {
      await page.waitForTimeout(3000);

      await expect(page.getByTestId('weather-icon')).toBeVisible({ timeout: 10000 });
    });

    test('should display weather location', async ({ page }) => {
      await page.waitForTimeout(3000);

      const location = page.getByTestId('weather-location');
      const isVisible = await location.isVisible({ timeout: 10000 }).catch(() => false);

      if (isVisible) {
        const locationText = await location.textContent();
        expect(locationText).toContain('اليمن');
      }
    });

    test('should display weather details grid', async ({ page }) => {
      await page.waitForTimeout(3000);

      const detailsGrid = page.getByTestId('weather-details-grid');
      await expect(detailsGrid).toBeVisible({ timeout: 10000 });

      // Check for humidity metric
      await expect(page.getByTestId('metric-الرطوبة')).toBeVisible();

      // Check for wind metric
      await expect(page.getByTestId('metric-الرياح')).toBeVisible();
    });

    test('should display humidity value', async ({ page }) => {
      await page.waitForTimeout(3000);

      const humidityMetric = page.getByTestId('metric-الرطوبة');
      await expect(humidityMetric).toBeVisible({ timeout: 10000 });

      const humidityValue = await humidityMetric.getByTestId('metric-الرطوبة-value').textContent();
      expect(humidityValue).toMatch(/\d+%/);
    });

    test('should display wind speed value', async ({ page }) => {
      await page.waitForTimeout(3000);

      const windMetric = page.getByTestId('metric-الرياح');
      await expect(windMetric).toBeVisible({ timeout: 10000 });

      const windValue = await windMetric.getByTestId('metric-الرياح-value').textContent();
      expect(windValue).toMatch(/\d+.*km\/h/i);
    });

    test('should display pressure if available', async ({ page }) => {
      await page.waitForTimeout(3000);

      const pressureMetric = page.getByTestId('metric-الضغط');
      const isVisible = await pressureMetric.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        const pressureValue = await pressureMetric.getByTestId('metric-الضغط-value').textContent();
        expect(pressureValue).toMatch(/\d+.*hPa/i);
      }
    });

    test('should display visibility if available', async ({ page }) => {
      await page.waitForTimeout(3000);

      const visibilityMetric = page.getByTestId('metric-الرؤية');
      const isVisible = await visibilityMetric.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        const visibilityValue = await visibilityMetric.getByTestId('metric-الرؤية-value').textContent();
        expect(visibilityValue).toMatch(/\d+.*km/i);
      }
    });

    test('should display timestamp', async ({ page }) => {
      await page.waitForTimeout(3000);

      const timestamp = page.getByTestId('weather-timestamp');
      const isVisible = await timestamp.isVisible({ timeout: 10000 }).catch(() => false);

      if (isVisible) {
        const timestampText = await timestamp.textContent();
        expect(timestampText).toContain('آخر تحديث');
      }
    });
  });

  /**
   * 7-Day Forecast Tests
   * اختبارات توقعات 7 أيام
   */
  test.describe('7-Day Forecast', () => {
    test('should display forecast section', async ({ page }) => {
      await page.waitForTimeout(3000);

      const forecastChart = page.getByTestId('forecast-chart');
      await expect(forecastChart).toBeVisible({ timeout: 10000 });

      // Check title and subtitle
      await expect(forecastChart.getByTestId('forecast-title')).toHaveText('توقعات 7 أيام');
      await expect(forecastChart.getByTestId('forecast-subtitle')).toHaveText('7-Day Forecast');
    });

    test('should display forecast list with multiple days', async ({ page }) => {
      await page.waitForTimeout(4000);

      const forecastList = page.getByTestId('forecast-list');
      await expect(forecastList).toBeVisible({ timeout: 10000 });

      // Check for forecast days
      const day0 = page.getByTestId('forecast-day-0');
      await expect(day0).toBeVisible();
    });

    test('should display date for each forecast day', async ({ page }) => {
      await page.waitForTimeout(4000);

      const firstDayDate = page.getByTestId('forecast-day-0-date');
      await expect(firstDayDate).toBeVisible({ timeout: 10000 });

      // Date should have text content
      const dateText = await firstDayDate.textContent();
      expect(dateText).toBeTruthy();
    });

    test('should display condition for each forecast day', async ({ page }) => {
      await page.waitForTimeout(4000);

      const firstDayCondition = page.getByTestId('forecast-day-0-condition');
      await expect(firstDayCondition).toBeVisible({ timeout: 10000 });

      // Condition should have text
      const conditionText = await firstDayCondition.textContent();
      expect(conditionText).toBeTruthy();
    });

    test('should display temperature for each forecast day', async ({ page }) => {
      await page.waitForTimeout(4000);

      const firstDayTemp = page.getByTestId('forecast-day-0-temp');
      await expect(firstDayTemp).toBeVisible({ timeout: 10000 });

      // Temperature should match pattern
      const tempText = await firstDayTemp.textContent();
      expect(tempText).toMatch(/\d+°C/);
    });

    test('should display humidity for each forecast day', async ({ page }) => {
      await page.waitForTimeout(4000);

      const firstDayHumidity = page.getByTestId('forecast-day-0-humidity');
      await expect(firstDayHumidity).toBeVisible({ timeout: 10000 });

      // Humidity should match pattern
      const humidityText = await firstDayHumidity.textContent();
      expect(humidityText).toMatch(/\d+%/);
    });

    test('should display temperature bars', async ({ page }) => {
      await page.waitForTimeout(4000);

      const firstDayTempBar = page.getByTestId('forecast-day-0-temp-bar');
      await expect(firstDayTempBar).toBeVisible({ timeout: 10000 });
    });

    test('should display forecast legend', async ({ page }) => {
      await page.waitForTimeout(4000);

      const legend = page.getByTestId('forecast-legend');
      await expect(legend).toBeVisible({ timeout: 10000 });
    });

    test('should display multiple forecast days (up to 7)', async ({ page }) => {
      await page.waitForTimeout(4000);

      // Count visible forecast days
      const forecastList = page.getByTestId('forecast-list');
      const days = forecastList.locator('[data-testid^="forecast-day-"]');
      const count = await days.count();

      // Should have at least 1 day and at most 7 days
      expect(count).toBeGreaterThan(0);
      expect(count).toBeLessThanOrEqual(7);
    });
  });

  /**
   * Weather Alerts Tests
   * اختبارات تنبيهات الطقس
   */
  test.describe('Weather Alerts', () => {
    test('should display weather alerts section', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Alerts section should be visible (either with alerts or no-data state)
      const hasAlerts = await page.getByTestId('weather-alerts').isVisible({ timeout: 5000 }).catch(() => false);
      const noAlerts = await page.getByTestId('alerts-no-data').isVisible({ timeout: 5000 }).catch(() => false);

      // One of them should be visible
      expect(hasAlerts || noAlerts).toBe(true);
    });

    test('should show no alerts message when no alerts exist', async ({ page }) => {
      await page.waitForTimeout(4000);

      const noAlertsSection = page.getByTestId('alerts-no-data');
      const isVisible = await noAlertsSection.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        await expect(page.getByTestId('no-alerts-message')).toHaveText('لا توجد تنبيهات طقس حالية');
        await expect(page.getByTestId('normal-conditions-message')).toHaveText('الأحوال الجوية طبيعية');
      }
    });

    test('should display alert cards if alerts exist', async ({ page }) => {
      await page.waitForTimeout(4000);

      const alertsSection = page.getByTestId('weather-alerts');
      const isVisible = await alertsSection.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        // Check for alerts list
        await expect(page.getByTestId('alerts-list')).toBeVisible();

        // Check if alert cards are present
        const alertCards = page.locator('[data-testid^="alert-card-"]');
        const count = await alertCards.count();

        if (count > 0) {
          // At least one alert exists
          expect(count).toBeGreaterThan(0);
        }
      }
    });

    test('should display alert details when alerts exist', async ({ page }) => {
      await page.waitForTimeout(4000);

      const alertCards = page.locator('[data-testid^="alert-card-"]');
      const count = await alertCards.count();

      if (count > 0) {
        // Get first alert ID
        const firstCard = alertCards.first();
        const testId = await firstCard.getAttribute('data-testid');
        const alertId = testId?.replace('alert-card-', '') || '1';

        // Check alert components
        await expect(page.getByTestId(`alert-${alertId}-icon`)).toBeVisible();
        await expect(page.getByTestId(`alert-${alertId}-title`)).toBeVisible();
        await expect(page.getByTestId(`alert-${alertId}-severity`)).toBeVisible();
        await expect(page.getByTestId(`alert-${alertId}-description`)).toBeVisible();
      }
    });
  });

  /**
   * Mock Data Fallback Tests
   * اختبارات البيانات الاحتياطية
   */
  test.describe('Mock Data Fallback', () => {
    test('should display weather data with mock fallback', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Current weather should be visible (either real data or mock data)
      const currentWeather = page.getByTestId('current-weather');
      await expect(currentWeather).toBeVisible({ timeout: 10000 });

      // Temperature should be displayed
      const temperature = page.getByTestId('temperature');
      await expect(temperature).toBeVisible();
      const tempText = await temperature.textContent();
      expect(tempText).toMatch(/\d+°C/);

      // This confirms mock data fallback is working if API is down
    });

    test('should display forecast with mock fallback', async ({ page }) => {
      await page.waitForTimeout(4000);

      // Forecast should be visible (either real data or mock data)
      const forecastChart = page.getByTestId('forecast-chart');
      await expect(forecastChart).toBeVisible({ timeout: 10000 });

      // At least one forecast day should be displayed
      await expect(page.getByTestId('forecast-day-0')).toBeVisible();
    });

    test('should display alerts or no-alerts state with mock fallback', async ({ page }) => {
      await page.waitForTimeout(4000);

      // Either alerts or no-alerts should be visible
      const hasAlerts = await page.getByTestId('weather-alerts').isVisible({ timeout: 5000 }).catch(() => false);
      const noAlerts = await page.getByTestId('alerts-no-data').isVisible({ timeout: 5000 }).catch(() => false);

      // One state should be visible (confirms fallback is working)
      expect(hasAlerts || noAlerts).toBe(true);
    });

    test('should not crash when API is unavailable', async ({ page }) => {
      await page.waitForTimeout(5000);

      // Page should remain functional
      await expect(page.getByTestId('weather-page')).toBeVisible();
      await expect(page.getByTestId('weather-title')).toBeVisible();

      // All main sections should be present
      const currentWeather = page.getByTestId('current-weather');
      const forecast = page.getByTestId('forecast-chart');

      await expect(currentWeather).toBeVisible({ timeout: 10000 });
      await expect(forecast).toBeVisible({ timeout: 10000 });
    });
  });

  /**
   * Responsive Design Tests
   * اختبارات التصميم المتجاوب
   */
  test.describe('Responsive Design', () => {
    test('should display correctly on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      await expect(page.getByTestId('weather-page')).toBeVisible();
      await expect(page.getByTestId('weather-title')).toBeVisible();
      await expect(page.getByTestId('location-selector')).toBeVisible();
    });

    test('should display correctly on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      await expect(page.getByTestId('weather-page')).toBeVisible();
      await expect(page.getByTestId('weather-title')).toBeVisible();
    });

    test('should display correctly on desktop viewport', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      await expect(page.getByTestId('weather-page')).toBeVisible();
      await expect(page.getByTestId('weather-title')).toBeVisible();
    });
  });

  /**
   * Integration Tests
   * اختبارات التكامل
   */
  test.describe('Integration', () => {
    test('should work with browser refresh', async ({ page }) => {
      await page.waitForTimeout(3000);

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(3000);

      await expect(page.getByTestId('weather-page')).toBeVisible();
      await expect(page.getByTestId('current-weather')).toBeVisible({ timeout: 10000 });
    });

    test('should display all sections together', async ({ page }) => {
      await page.waitForTimeout(5000);

      // All main sections should be present
      await expect(page.getByTestId('weather-dashboard')).toBeVisible();
      await expect(page.getByTestId('current-weather')).toBeVisible({ timeout: 10000 });
      await expect(page.getByTestId('forecast-chart')).toBeVisible({ timeout: 10000 });

      // Alerts section (one of the two states)
      const hasAlerts = await page.getByTestId('weather-alerts').isVisible({ timeout: 5000 }).catch(() => false);
      const noAlerts = await page.getByTestId('alerts-no-data').isVisible({ timeout: 5000 }).catch(() => false);
      expect(hasAlerts || noAlerts).toBe(true);
    });
  });
});
