/**
 * SAHOOL Web GUI Browser Test — Full Flow
 */
const { chromium } = require('playwright');
const http  = require('http');
const path  = require('path');
const fs    = require('fs');

const BASE_URL = 'http://localhost:3002';
const API_URL  = 'http://localhost:8000';
const SS_DIR   = path.join(__dirname, 'screenshots');
if (!fs.existsSync(SS_DIR)) fs.mkdirSync(SS_DIR, { recursive: true });

const TS       = Date.now();
const EMAIL    = `guibrowser${TS}@sahool.com`;
const PASSWORD = 'TestPass123!';

const ok   = m => console.log(`  ✅ ${m}`);
const warn = m => console.log(`  ⚠️  ${m}`);
const fail = m => console.log(`  ❌ ${m}`);

async function ss(page, name) {
  const f = path.join(SS_DIR, `${name}.png`);
  await page.screenshot({ path: f, fullPage: false });
  console.log(`  📸 ${name}.png`);
}

// API helper using Node http (no browser)
function apiPost(url, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const u = new URL(url);
    const opts = { hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } };
    const req = http.request(opts, res => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => { try { resolve(JSON.parse(raw)); } catch { resolve({}); } });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  // Track console errors
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });

  // Track network requests for debugging
  const apiResponses = [];
  page.on('response', async resp => {
    if (resp.url().includes('/api/v1/') || resp.url().includes('/api/auth/')) {
      try {
        const body = await resp.json().catch(() => null);
        apiResponses.push({ url: resp.url(), status: resp.status(), body });
      } catch {
        // response body parse failure is non-fatal — keep watching the next one
      }
    }
  });

  try {
    // ── 1. HOME → LOGIN REDIRECT ──────────────────────────────────
    console.log('\n=== 1. Home → Login Redirect ===');
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(1000);
    await ss(page, '01-home');
    page.url().includes('/login') ? ok('Unauthenticated → /login ✓') : warn(`URL: ${page.url()}`);

    // ── 2. REGISTER PAGE ──────────────────────────────────────────
    console.log('\n=== 2. Register Page ===');
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);
    await ss(page, '02-register-page');
    ok(`Register page loaded: ${page.url()}`);

    // Count inputs to understand form structure
    const allInputs = await page.locator('input').all();
    for (const inp of allInputs) {
      const type = await inp.getAttribute('type').catch(() => '?');
      const ph   = await inp.getAttribute('placeholder').catch(() => '');
      const id   = await inp.getAttribute('id').catch(() => '');
      console.log(`  input[type="${type}"] id="${id}" placeholder="${ph}"`);
    }

    // ── 3. REGISTER FORM SUBMIT ───────────────────────────────────
    console.log('\n=== 3. Register Form ===');
    // Default is phone method - fill firstName, lastName, phone, password, confirmPassword
    await page.locator('input[placeholder="محمد"]').fill('Browser').catch(() => warn('No firstName placeholder "محمد"'));
    await page.locator('input[placeholder="الأحمد"]').fill('Test').catch(() => warn('No lastName placeholder "الأحمد"'));
    await page.locator('input[type="tel"]').first().fill('+967712345678').catch(() => warn('No tel input'));
    await page.locator('input[type="email"]').first().fill(EMAIL).catch(() => warn('No email input'));
    const pws = page.locator('input[type="password"]');
    const pwCount = await pws.count();
    for (let i = 0; i < pwCount; i++) await pws.nth(i).fill(PASSWORD);
    console.log(`  Filled ${pwCount} password fields`);
    await ss(page, '03-register-filled');

    // Listen for the register API response
    const registerResponsePromise = page.waitForResponse(
      r => r.url().includes('/api/v1/auth/register'), { timeout: 10000 }
    ).catch(() => null);

    await page.locator('button[type="submit"]').first().click();
    const regResp = await registerResponsePromise;

    if (regResp) {
      const regBody = await regResp.json().catch(() => null);
      console.log(`  Register API status: ${regResp.status()}`);
      if (regBody?.access_token) {
        ok('Registration API call succeeded');
      } else {
        const errMsg = regBody?.error?.message || regBody?.message || JSON.stringify(regBody).substring(0, 100);
        warn(`Register API response: ${errMsg}`);
      }
    }

    await page.waitForTimeout(3000);
    await ss(page, '04-register-result');
    const afterReg = page.url();
    console.log(`  URL after register: ${afterReg}`);
    if (afterReg.includes('/login')) ok('→ Redirected to /login after register');
    else warn(`Stayed at: ${afterReg}`);

    // ── 4. LOGIN (phone method — default) ─────────────────────────
    console.log('\n=== 4. Login (Phone Method) ===');
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(1500);
    await ss(page, '05-login-page');

    // Log what inputs exist
    const loginInputs = await page.locator('input').all();
    for (const inp of loginInputs) {
      const type = await inp.getAttribute('type').catch(() => '?');
      const ph   = await inp.getAttribute('placeholder').catch(() => '');
      console.log(`  input[type="${type}"] placeholder="${ph}"`);
    }

    // Login defaults to phone mode — fill phone + password
    await page.locator('input[type="tel"], input[placeholder*="+967"]').first().fill('+967712345678');
    await page.locator('input[type="password"]').first().fill(PASSWORD);
    await ss(page, '06-login-phone-filled');

    // Intercept login API response
    const loginRespPromise = page.waitForResponse(
      r => r.url().includes('/api/v1/auth/login'), { timeout: 10000 }
    ).catch(() => null);
    await page.locator('button[type="submit"]').first().click();
    const loginApiResp = await loginRespPromise;

    if (loginApiResp) {
      const loginBody = await loginApiResp.json().catch(() => null);
      console.log(`  Login API status: ${loginApiResp.status()}`);
      if (loginBody?.access_token) ok('Login API response has access_token');
      else warn(`Login response: ${JSON.stringify(loginBody).substring(0, 100)}`);
    }

    await page.waitForTimeout(3000);
    await ss(page, '07-after-phone-login');
    const afterPhoneLogin = page.url();
    console.log(`  URL after phone login: ${afterPhoneLogin}`);

    if (!afterPhoneLogin.includes('/login')) {
      ok(`Phone login succeeded → ${afterPhoneLogin}`);
    } else {
      warn('Phone login did not redirect — trying email method');

      // Switch to email tab and try
      await page.locator('button[aria-label*="email" i], button:has-text("البريد الإلكتروني")').first().click().catch(() => {});
      await page.waitForTimeout(500);
      await page.locator('input[type="email"]').first().fill(EMAIL).catch(() => {});
      await page.locator('input[type="password"]').first().fill(PASSWORD);
      await ss(page, '07b-login-email-filled');

      const loginRespPromise2 = page.waitForResponse(
        r => r.url().includes('/api/v1/auth/login'), { timeout: 8000 }
      ).catch(() => null);
      await page.locator('button[type="submit"]').first().click();
      const lr2 = await loginRespPromise2;
      if (lr2) console.log(`  Email login API status: ${lr2.status()}`);
      await page.waitForTimeout(3000);
      await ss(page, '07c-after-email-login');
      console.log(`  URL after email login: ${page.url()}`);
      if (!page.url().includes('/login')) ok(`Email login succeeded → ${page.url()}`);
      else {
        warn('UI login failed — using API auth directly');
        // Last resort: inject token via API registration
        const freshReg = await apiPost(`${API_URL}/api/v1/auth/register`, {
          email: `apidirect${TS}@sahool.com`, password: PASSWORD,
          name: 'API Direct', phone: '+967712345678'
        });
        if (freshReg.access_token) {
          const sessionSet = await page.evaluate(async ({ token, refresh }) => {
            const r = await fetch('/api/auth/session', {
              method: 'POST', credentials: 'include',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ access_token: token, refresh_token: refresh }),
            });
            return r.ok;
          }, { token: freshReg.access_token, refresh: freshReg.refresh_token || '' });
          sessionSet ? ok('API direct auth session set') : fail('API direct auth failed');
        }
      }
    }

    // ── 5. FIELDS LIST ──────────────────────────────────────────────
    console.log('\n=== 5. Fields List Page ===');
    await page.goto(`${BASE_URL}/fields`, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    await ss(page, '08-fields-list');

    const fieldsUrl = page.url();
    console.log(`  URL: ${fieldsUrl}`);
    if (fieldsUrl.includes('/fields') && !fieldsUrl.includes('/login')) {
      ok('Fields list loaded (authenticated) ✓');
      // Check content
      const pageText = await page.locator('body').textContent();
      const hasContent = pageText.includes('حقل') || pageText.includes('Field') || pageText.includes('wheat') || pageText.includes('إنشاء');
      hasContent ? ok('Fields content visible') : warn('No field content detected');

      // Screenshot shows create button
      const createBtnText = await page.locator('button:has-text("إنشاء"), button:has-text("Create"), button:has-text("جديد")').first().textContent().catch(() => '');
      createBtnText ? ok(`Create button visible: "${createBtnText.trim()}"`) : warn('Create button not found');
    } else {
      fail(`Not authenticated, at: ${fieldsUrl}`);
    }

    // ── 6. CREATE FIELD FLOW ────────────────────────────────────────
    console.log('\n=== 6. Create Field Modal ===');
    // Find and click create button
    const createBtns = await page.locator('button').all();
    let createClicked = false;
    for (const btn of createBtns.slice(0, 20)) {
      const text = await btn.textContent().catch(() => '');
      if (/إنشاء|Create|جديد|New|Add|\+/.test(text)) {
        await btn.click();
        createClicked = true;
        ok(`Clicked: "${text.trim().substring(0, 40)}"`);
        break;
      }
    }
    if (!createClicked) warn('Create button not found');

    await page.waitForTimeout(2500);
    await ss(page, '09-create-modal');

    // ── 7. FILL FORM ────────────────────────────────────────────────
    console.log('\n=== 7. Field Form — Info Tab ===');
    const formInputs = await page.locator('[role="dialog"] input, [role="dialog"] select, form input').all();
    console.log(`  Form inputs found: ${formInputs.length}`);

    for (const inp of formInputs.slice(0, 8)) {
      const type = await inp.getAttribute('type').catch(() => '?');
      const ph   = await inp.getAttribute('placeholder').catch(() => '');
      console.log(`  [${type}] "${ph}"`);
    }

    // Fill field name
    const nameInput = page.locator('[role="dialog"] input[type="text"], form input[type="text"]').first();
    if (await nameInput.isVisible().catch(() => false)) {
      await nameInput.fill(`Browser Test ${TS}`);
      ok('Field name entered');
    }

    await ss(page, '10-form-filled');

    // Click boundary tab
    console.log('\n=== 8. Boundary Tab ===');
    const boundaryBtns = await page.locator('button').all();
    let boundaryClicked = false;
    for (const btn of boundaryBtns.slice(0, 30)) {
      const text = await btn.textContent().catch(() => '');
      if (/حدود|Boundary/.test(text)) {
        await btn.click();
        boundaryClicked = true;
        ok(`Boundary tab: "${text.trim()}"`);
        break;
      }
    }
    if (!boundaryClicked) warn('Boundary tab not found');

    await page.waitForTimeout(5000); // Google Maps takes time
    await ss(page, '11-boundary-tab');

    // Check Google Maps
    const gmStyle = await page.locator('.gm-style').count();
    const canvas  = await page.locator('canvas').count();
    console.log(`  .gm-style: ${gmStyle} | canvas elements: ${canvas}`);
    if (gmStyle > 0)   ok('Google Maps rendered (.gm-style)!');
    else if (canvas > 0) warn('Canvas present (maps may be loading)');
    else                 warn('Google Maps not detected — checking for error...');

    // Check for any map error message
    const mapErr = await page.locator('[class*="gm-err"], [class*="map-error"]').textContent().catch(() => '');
    if (mapErr) warn(`Map error: ${mapErr.substring(0, 100)}`);

    // Close modal
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);

    // ── 9. FIELD DETAIL PAGE ────────────────────────────────────────
    console.log('\n=== 9. Field Detail + KPI Tiles ===');
    const FIELD_ID = 'c5fec430-f388-46b9-bd24-6f7fc59d7f1b';
    await page.goto(`${BASE_URL}/fields/${FIELD_ID}`, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(6000); // KPI tiles + map load async
    await ss(page, '12-field-detail');

    const detailUrl = page.url();
    console.log(`  URL: ${detailUrl}`);

    if (detailUrl.includes('/fields/') && !detailUrl.includes('/login') && !detailUrl.endsWith('/fields')) {
      ok('Field detail page loaded ✓');

      const body = await page.locator('body').textContent();

      // KPI tile content checks
      const checks = [
        ['NDVI / مؤشر الغطاء النباتي',   /NDVI|مؤشر الغطاء/],
        ['EVI / مؤشر النباتات المحسّن',    /EVI|مؤشر النبات/],
        ['NDWI / مؤشر الماء',             /NDWI|مؤشر.*ماء/],
        ['Temperature / درجة الحرارة',    /Temperature|درجة الحرارة|°/],
        ['Humidity / الرطوبة',            /Humidity|الرطوبة|%/],
        ['Wind Speed / سرعة الرياح',       /Wind|الرياح|km\/h/],
        ['Precipitation / الأمطار',        /Precipitation|الأمطار|mm/],
        ['UV Index / مؤشر الأشعة',        /UV|الأشعة/],
        ['Sentinel source',               /Sentinel/],
        ['OpenWeather source',             /OpenWeather|weather/i],
      ];
      for (const [label, pattern] of checks) {
        pattern.test(body) ? ok(`${label}`) : warn(`Not found: ${label}`);
      }

      // Map element
      const gmCount = await page.locator('.gm-style').count();
      const leaflet = await page.locator('.leaflet-container').count();
      console.log(`  Maps: gm-style=${gmCount} leaflet=${leaflet}`);
      gmCount > 0 ? ok('Google Maps on field detail') :
        leaflet > 0 ? ok('Map visible (Leaflet)') : warn('No map element found');

      // Final screenshot
      await ss(page, '13-field-kpi-final');
    } else {
      fail(`Wrong URL: ${detailUrl}`);
    }

    // ── 10. CONSOLE ERRORS ─────────────────────────────────────────
    console.log('\n=== 10. Console Errors ===');
    const skip = ['favicon', 'manifest', 'ERR_BLOCKED', 'analytics', 'sentry', '_next/static'];
    const crit = errors.filter(e => !skip.some(s => e.includes(s)));
    if (crit.length === 0) ok('No critical console errors');
    else {
      warn(`${crit.length} error(s):`);
      crit.slice(0, 5).forEach(e => console.log(`    • ${e.substring(0, 130)}`));
    }

    // API calls summary
    console.log('\n=== Network Calls Summary ===');
    apiResponses.slice(-10).forEach(r => {
      const statusIcon = r.status < 300 ? '✅' : r.status < 400 ? '↩️ ' : '❌';
      console.log(`  ${statusIcon} ${r.status} ${r.url.replace('http://localhost:3002', '').replace('http://localhost:8000', '[Kong]').substring(0, 80)}`);
    });

    console.log(`\n📁 Screenshots: ${SS_DIR}`);
    console.log('\n═══════════════════════════════════════');
    console.log('      BROWSER GUI TEST COMPLETE');
    console.log('═══════════════════════════════════════\n');

  } catch (err) {
    fail(`Fatal: ${err.message}`);
    await ss(page, 'XX-fatal').catch(() => {});
    console.error(err.stack);
  } finally {
    await browser.close();
  }
})();
