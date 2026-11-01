import { expect, test } from '@playwright/test';

const tile = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACXBIWXMAAAPoAAAD6AG1e1JrAAAADUlEQVQImWM4c+bMfwAIMANkpuW1DwAAAABJRU5ErkJggg==', 'base64');

test.beforeEach(async ({ page }) => {
  // Keep actual raster loading deterministic and independent of third-party availability.
  await page.route('https://tile.openstreetmap.org/**', (route) => route.fulfill({ contentType: 'image/png', body: tile }));
  await page.route('https://server.arcgisonline.com/**', (route) => route.fulfill({ contentType: 'image/png', body: tile }));
});

test('real attribution controls strip consecutive executable attributes and preserve safe credit links', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/?mode=attribution');
  await page.waitForFunction(() => window.fixtureMap?.loaded());
  await expect(page.locator('.maplibregl-ctrl-attrib-inner a')).toHaveAttribute('href', 'https://example.org/credit');
  const result = await page.evaluate(() => ({
    unsafe: [...document.querySelectorAll('.maplibregl-ctrl-attrib-inner *')]
      .flatMap((element) => [...element.attributes].filter((attribute) => /^on/i.test(attribute.name)).map((attribute) => attribute.name)),
    executed: window.attributionExecuted,
    webgl2: window.fixtureMap.getCanvas().getContext('webgl2') instanceof WebGL2RenderingContext,
    errors: window.fixtureErrors,
  }));
  expect(result.unsafe).toEqual([]);
  expect(result.executed).toBeUndefined();
  expect(result.webgl2).toBe(true);
  expect(result.errors).toEqual([]);
  expect(errors).toEqual([]);
});

test('the actual dashboard renders NDVI fields, supports layer selection and keeps popup names as text', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await page.waitForFunction(() => window.fixtureMap?.isStyleLoaded() && !window.fixtureMap.isMoving());
  const rendered = await page.evaluate(() => ({
    layers: ['fields-fill', 'fields-outline', 'fields-label'].map((id) => Boolean(window.fixtureMap.getLayer(id))),
    fields: window.fixtureMap.queryRenderedFeatures({ layers: ['fields-fill'] }).map((feature) => ({ id: feature.properties.id, ndvi: feature.properties.ndvi })),
  }));
  expect(rendered.layers).toEqual([true, true, true]);
  expect(rendered.fields).toEqual(expect.arrayContaining([{ id: 'bare-soil', ndvi: 0 }, { id: 'healthy', ndvi: 0.7 }]));
  await page.getByRole('button', { name: 'عرض صور القمر الصناعي' }).click();
  expect(await page.evaluate(() => window.fixtureMap.getLayoutProperty('satellite', 'visibility'))).toBe('visible');
  expect(await page.evaluate(() => window.fixtureMap.getLayoutProperty('osm', 'visibility'))).toBe('none');
  await page.getByRole('button', { name: 'عرض خريطة الشوارع' }).click();
  const point = await page.evaluate(() => {
    const point = window.fixtureMap.project([44.19, 15]);
    const bounds = window.fixtureMap.getCanvas().getBoundingClientRect();
    return { x: point.x + bounds.left, y: point.y + bounds.top };
  });
  await page.mouse.click(point.x, point.y);
  await expect(page.locator('.sahool-popup-content')).toContainText('<img src=x onerror="window.popupExecuted=1">');
  await expect(page.locator('.sahool-popup-content img')).toHaveCount(0);
  await expect(page.locator('.sahool-popup-content')).toContainText('0.00');
  expect(await page.evaluate(() => window.selectedField)).toBe('bare-soil');
  expect(await page.evaluate(() => window.popupExecuted)).toBeUndefined();
  expect(await page.evaluate(() => window.fixtureErrors)).toEqual([]);
  expect(errors).toEqual([]);
});
