import { chromium } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dir = dirname(fileURLToPath(import.meta.url));

const loginRes = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@sahool.app', password: 'Admin123!' }),
});
const ACCESS_TOKEN = (await loginRes.json()).access_token;

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
await context.addCookies([{
  name: 'access_token', value: ACCESS_TOKEN,
  domain: 'localhost', path: '/', httpOnly: false, secure: false,
}]);

const page = await context.newPage();
await page.setViewportSize({ width: 1600, height: 950 });
await page.goto('http://localhost:3040/satellite', { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForTimeout(5000);

// Dismiss dev overlay: click the × on the "1 Issue" pill via shadow DOM
await page.evaluate(() => {
  // Try to remove shadow-dom portals
  document.querySelectorAll('nextjs-portal').forEach(portal => {
    const root = portal.shadowRoot;
    if (root) root.innerHTML = '';
    portal.remove();
  });
});
await page.waitForTimeout(1000);

// Also try pressing Escape
await page.keyboard.press('Escape');
await page.waitForTimeout(500);

// Click the × close button by coordinates (bottom-left "1 Issue ×" pill)
const pill = page.locator('text=1 Issue').first();
try {
  const bbox = await pill.boundingBox();
  if (bbox) {
    // Click the × which is to the right of the text
    await page.mouse.click(bbox.x + bbox.width + 5, bbox.y + bbox.height / 2);
    console.log('Clicked × on pill');
  }
} catch {}
await page.waitForTimeout(1000);

await page.screenshot({ path: join(__dir, 'sat-debug4.png') });

// Now wait for select
try {
  await page.waitForFunction(
    () => document.querySelector('select')?.options.length > 1,
    { timeout: 15000 }
  );
  console.log('Select loaded');
} catch {
  console.log('Select timeout — checking what is on page');
  const text = await page.evaluate(() => document.body.innerText.substring(0, 200));
  console.log('TEXT:', text);
  process.exit(1);
}

const options = await page.$$eval('select option', opts =>
  opts.map(o => ({ value: o.value, text: o.text.trim() }))
);
const field = options.find(o => o.text.includes('1111111')) || options.find(o => o.value);
console.log('Selecting:', field?.text);
if (!field) process.exit(1);

await page.selectOption('select', field.value);
await page.waitForTimeout(5000);
await page.locator('button', { hasText: 'NDVI' }).first().click();

try {
  await page.waitForResponse(
    res => res.url().includes('/api/sentinel') && res.status() === 200,
    { timeout: 25000 }
  );
  console.log('Sentinel loaded');
} catch { console.log('Sentinel timeout'); }
await page.waitForTimeout(7000);

const badge = await page.evaluate(() => {
  const el = document.querySelector('[class*="bg-green-7"]');
  return el ? el.textContent?.trim() : '(none)';
});
console.log('Badge:', badge);

const mapEl = await page.$('.flex-1.min-h-0.relative');
if (mapEl) await mapEl.screenshot({ path: join(__dir, 'sat-map-final.png') });
await page.screenshot({ path: join(__dir, 'sat-full-final.png') });
console.log('Done');

await browser.close();
