export const runtime = 'nodejs';

import { NextRequest, NextResponse } from 'next/server';

// ---------------------------------------------------------------------------
// In-process LRU image cache — avoids re-fetching identical Sentinel images
// within the same worker process (survives hot-reload in dev, TTL in prod).
// Key: "${index}::${west}::${south}::${east}::${north}::${from}::${to}::${w}x${h}"
// ---------------------------------------------------------------------------
const IMAGE_CACHE_MAX = 200;
const IMAGE_CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours — historical scenes are immutable

interface CacheEntry { buf: ArrayBuffer; expiresAt: number }
const _imageCache = new Map<string, CacheEntry>();

function imageCacheGet(key: string): ArrayBuffer | null {
  const entry = _imageCache.get(key);
  if (!entry) return null;
  if (entry.expiresAt <= Date.now()) { _imageCache.delete(key); return null; }
  return entry.buf;
}

function imageCacheSet(key: string, buf: ArrayBuffer): void {
  // Evict oldest entry when at capacity
  if (_imageCache.size >= IMAGE_CACHE_MAX) {
    const oldest = _imageCache.keys().next().value;
    if (oldest) _imageCache.delete(oldest);
  }
  _imageCache.set(key, { buf, expiresAt: Date.now() + IMAGE_CACHE_TTL_MS });
}

// ---------------------------------------------------------------------------
// OAuth2 token cache (module-level, shared across requests in the same worker)
// ---------------------------------------------------------------------------
let _token: { value: string; expiresAt: number } | null = null;

async function getToken(): Promise<string | null> {
  // CDSE (Copernicus Data Space Ecosystem) credentials take priority.
  // Fall back to legacy SENTINEL_HUB_* vars for backward compatibility.
  const clientId     = process.env.CDSE_CLIENT_ID     || process.env.SENTINEL_HUB_CLIENT_ID;
  const clientSecret = process.env.CDSE_CLIENT_SECRET || process.env.SENTINEL_HUB_CLIENT_SECRET;
  const authUrl =
    process.env.SH_TOKEN_URL ||
    process.env.SENTINEL_HUB_AUTH_URL ||
    'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token';

  if (!clientId || !clientSecret) return null;

  const now = Date.now();
  if (_token && _token.expiresAt > now) return _token.value;

  try {
    const res = await fetch(authUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: clientId,
        client_secret: clientSecret,
        // CDSE requires scope=openid; harmless for commercial Sentinel Hub
        scope: 'openid',
      }),
      signal: AbortSignal.timeout(15000),
    });

    if (!res.ok) return null;

    const data = (await res.json()) as { access_token: string; expires_in: number };
    const BUFFER_S = 120;
    _token = {
      value: data.access_token,
      expiresAt: now + (data.expires_in - BUFFER_S) * 1000,
    };
    return _token.value;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Actual Sentinel-2 band composite evalscripts
// Each renders real satellite reflectance data — no synthetic colour coding.
// Source: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Process/Examples/S2L2A.html
// ---------------------------------------------------------------------------

/** Gamma-compress a surface reflectance value to display range. */
const ADJ_FN = 'function adj(v){return Math.pow(Math.min(1,Math.max(0,3.5*v)),1/2.2);}';

/**
 * Build a 4-band (RGBA, alpha=1) evalscript for a band triplet.
 * Bands are listed in RGB order: [red_band, green_band, blue_band].
 */
function rgbScript(rBand: string, gBand: string, bBand: string): string {
  const allBands = [...new Set([rBand, gBand, bBand])];
  const inputList = allBands.map((b) => `"${b}"`).join(',');
  return (
    `//VERSION=3\n` +
    `function setup(){return{input:[{bands:[${inputList}]}],output:{bands:4}}}\n` +
    `function evaluatePixel(s){${ADJ_FN}` +
    `return[adj(s.${rBand}),adj(s.${gBand}),adj(s.${bBand}),1];}`
  );
}

// ── Base composites ─────────────────────────────────────────────────────────

/** True Color L2A: B04(R) B03(G) B02(B) — natural appearance, surface reflectance */
const TRUE_COLOR = rgbScript('B04', 'B03', 'B02');

/**
 * True Color L1C — slight warm/cool tint to compensate TOA vs surface difference.
 * Uses highlight-compression tone curve instead of simple gamma.
 */
const TRUE_COLOR_L1C =
  '//VERSION=3\n' +
  'function setup(){return{input:[{bands:["B02","B03","B04"]}],output:{bands:4}}}\n' +
  'function evaluatePixel(s){\n' +
  '  function adj(v){return Math.pow(Math.min(1,Math.max(0,3.0*v)),1/2.2);}\n' +
  '  var r=adj(s.B04),g=adj(s.B03),b=adj(s.B02);\n' +
  '  return[r*1.05,g,b*0.95,1];\n' +
  '}';

/**
 * True Color L2A — highlight-compressed tone curve.
 * Reduces blown-out bright areas while keeping shadows visible.
 */
const TRUE_COLOR_L2A =
  '//VERSION=3\n' +
  'function setup(){return{input:[{bands:["B02","B03","B04"]}],output:{bands:4}}}\n' +
  'function evaluatePixel(s){\n' +
  '  function adj(v){var x=3.5*v;return x/(x+0.3);}\n' +
  '  function gam(v){return Math.pow(Math.min(1,Math.max(0,v)),1/2.2);}\n' +
  '  return[gam(adj(s.B04)),gam(adj(s.B03)),gam(adj(s.B02)),1];\n' +
  '}';

/**
 * False Color IR: B08(R) B04(G) B03(B)
 * Healthy dense vegetation → vivid red/magenta (strong NIR reflectance).
 * Best composite for all vegetation-health indices (NDVI, EVI, SAVI, LAI …).
 */
const FALSE_COLOR_IR = rgbScript('B08', 'B04', 'B03');

/**
 * SWIR composite: B12(R) B8A(G) B04(B)
 * Water bodies → near-black; moist soil/vegetation → dark green/blue;
 * burn scars → red/pink; bare soil → orange-brown.
 * Best for water, moisture, fire, and burn indices.
 */
const SWIR = rgbScript('B12', 'B8A', 'B04');

/**
 * False Color Urban: B12(R) B11(G) B04(B)
 * Built-up areas → purple/lilac; vegetation → green; bare soil → orange.
 * Best for soil/bare-soil indices and urban indices.
 */
const FALSE_COLOR_URBAN = rgbScript('B12', 'B11', 'B04');

// ---------------------------------------------------------------------------
// Computed index evalscript factory
// Generates evalscript strings that compute the actual index formula and
// apply a colour ramp via colorBlend() — standard CDSE/SentinelHub JS utility.
// colorBlend(value, domain, colorStops) where stops are [R,G,B,A] in 0–1.
// ---------------------------------------------------------------------------

function mkIndexScript(
  bands: string[],
  formula: string,
  domain: number[],
  stops: [number, number, number, number][],
): string {
  const bl = bands.map((b) => `"${b}"`).join(',');
  return (
    `//VERSION=3\n` +
    `function setup(){return{input:[{bands:[${bl}]}],output:{bands:4}}}\n` +
    `function evaluatePixel(s){var v=${formula};return colorBlend(v,${JSON.stringify(domain)},${JSON.stringify(stops)});}`
  );
}

// ── Shared colour stop arrays ────────────────────────────────────────────────

/** Standard vegetation ramp: dark-red → orange → yellow → light-green → dark-green
 *  Matches the classic NDVI palette used in the reference mobile app (images 11–13). */
const VEG_DOM  = [-0.5, 0, 0.1, 0.25, 0.45, 0.65, 1.0];
const VEG_STOPS: [number,number,number,number][] = [
  [0.40,0.00,0.00,1],   // -0.5  deep maroon (water/urban)
  [0.90,0.00,0.00,1],   //  0.0  bright blood red (bare/stressed)
  [0.95,0.15,0.05,1],   //  0.1  deep red-orange (still clearly "problem")
  [0.93,0.82,0.08,1],   //  0.25 yellow (sparse/transitional vegetation)
  [0.38,0.80,0.18,1],   //  0.45 yellow-green (moderate vegetation)
  [0.08,0.52,0.08,1],   //  0.65 medium green (good vegetation)
  [0.02,0.25,0.02,1],   //  1.0  dark forest green
];

/** Moisture ramp: brown/orange → pale → dark-blue
 *  Matches NDMI reference image (image 18). */
const MOIST_DOM  = [-1, -0.5, -0.2, 0, 0.2, 0.5, 1];
const MOIST_STOPS: [number,number,number,number][] = [
  [0.55,0.36,0.15,1],[0.80,0.60,0.35,1],[0.95,0.85,0.65,1],
  [0.90,0.95,0.99,1],[0.60,0.80,0.95,1],[0.20,0.55,0.90,1],[0.00,0.25,0.65,1],
];

/** Diverging pink → white → blue for NDWI/water indices
 *  Matches NDWI reference image (image 19). */
const NDWI_DOM  = [-1, -0.3, 0, 0.3, 1];
const NDWI_STOPS: [number,number,number,number][] = [
  [0.85,0.10,0.55,1],[0.95,0.60,0.80,1],[0.98,0.98,0.98,1],
  [0.40,0.70,0.95,1],[0.05,0.30,0.75,1],
];

// ── Vegetation indices ────────────────────────────────────────────────────────
const NDVI_COMPUTED   = mkIndexScript(['B08','B04'],
  '(s.B08-s.B04)/(s.B08+s.B04+1e-9)', VEG_DOM, VEG_STOPS);
const EVI_COMPUTED    = mkIndexScript(['B08','B04','B02'],
  '2.5*(s.B08-s.B04)/(s.B08+6*s.B04-7.5*s.B02+1+1e-9)', VEG_DOM, VEG_STOPS);
const EVI2_COMPUTED   = mkIndexScript(['B08','B04'],
  '2.5*(s.B08-s.B04)/(s.B08+2.4*s.B04+1+1e-9)', VEG_DOM, VEG_STOPS);
const GNDVI_COMPUTED  = mkIndexScript(['B08','B03'],
  '(s.B08-s.B03)/(s.B08+s.B03+1e-9)', VEG_DOM, VEG_STOPS);
const KNDVI_COMPUTED  = mkIndexScript(['B08','B04'],
  'Math.tanh(Math.pow((s.B08-s.B04)/(s.B08+s.B04+1e-9),2))', VEG_DOM, VEG_STOPS);
const SAVI_COMPUTED   = mkIndexScript(['B08','B04'],
  '1.5*(s.B08-s.B04)/(s.B08+s.B04+0.5+1e-9)', VEG_DOM, VEG_STOPS);
const MSAVI_COMPUTED  = mkIndexScript(['B08','B04'],
  '(2*s.B08+1-Math.sqrt(Math.max(0,(2*s.B08+1)*(2*s.B08+1)-8*(s.B08-s.B04))))/2',
  VEG_DOM, VEG_STOPS);
const OSAVI_COMPUTED  = mkIndexScript(['B08','B04'],
  '(s.B08-s.B04)/(s.B08+s.B04+0.16+1e-9)', VEG_DOM, VEG_STOPS);
const ARVI_COMPUTED   = mkIndexScript(['B08','B04','B02'],
  '(s.B08-(2*s.B04-s.B02))/(s.B08+(2*s.B04-s.B02)+1e-9)', VEG_DOM, VEG_STOPS);
const NDRE_COMPUTED   = mkIndexScript(['B8A','B05'],
  '(s.B8A-s.B05)/(s.B8A+s.B05+1e-9)', VEG_DOM, VEG_STOPS);
const LAI_COMPUTED    = mkIndexScript(['B08','B04'],
  'Math.max(0,Math.min(1,(3.618*(s.B08-s.B04)/(s.B08+s.B04+1e-9)-0.118)/6))',
  [0,0.1,0.2,0.4,0.6,0.8,1], VEG_STOPS);
const FAPAR_COMPUTED  = mkIndexScript(['B08','B04'],
  'Math.max(0,Math.min(1,0.95*(s.B08-s.B04)/(s.B08+s.B04+1e-9)+0.026))',
  [0,0.1,0.2,0.4,0.6,0.8,1], VEG_STOPS);
const FCOVER_COMPUTED = mkIndexScript(['B08','B04'],
  'Math.max(0,Math.min(1,1.0457*(s.B08-s.B04)/(s.B08+s.B04+1e-9)-0.1))',
  [0,0.1,0.2,0.4,0.6,0.8,1], VEG_STOPS);
const NDYI_COMPUTED   = mkIndexScript(['B11','B08'],
  '(s.B11-s.B08)/(s.B11+s.B08+1e-9)',
  [-0.5,-0.2,0,0.2,0.5],
  [[0.10,0.55,0.10,1],[0.60,0.85,0.30,1],[0.95,0.95,0.20,1],
   [0.95,0.65,0.10,1],[0.70,0.10,0.05,1]]);
const PSRI_COMPUTED   = mkIndexScript(['B04','B02','B06'],
  '(s.B04-s.B02)/(s.B06+1e-9)',
  [-0.3,0,0.1,0.2,0.5],
  [[0.15,0.60,0.15,1],[0.85,0.90,0.25,1],[0.95,0.75,0.15,1],
   [0.85,0.40,0.10,1],[0.55,0.10,0.05,1]]);

// ── Red-edge chlorophyll index (RECI) ─────────────────────────────────────────
// RECI = B07/B05 − 1  (range 0–12; high = high chlorophyll)
// Matches reference images 16–17: vivid red → orange → yellow → dark green.
const RECI_COMPUTED = mkIndexScript(['B07','B05'],
  'Math.max(0,s.B07/(s.B05+1e-9)-1)',
  [0,1,2,4,8,12],
  [[0.75,0.05,0.05,1],[0.90,0.50,0.05,1],[0.90,0.85,0.20,1],
   [0.40,0.75,0.15,1],[0.10,0.55,0.10,1],[0.00,0.35,0.05,1]]);

// ── Water / Moisture indices ──────────────────────────────────────────────────
const NDWI_COMPUTED        = mkIndexScript(['B03','B08'],
  '(s.B03-s.B08)/(s.B03+s.B08+1e-9)', NDWI_DOM, NDWI_STOPS);
const MNDWI_COMPUTED       = mkIndexScript(['B03','B11'],
  '(s.B03-s.B11)/(s.B03+s.B11+1e-9)', NDWI_DOM, NDWI_STOPS);
const NDMI_COMPUTED        = mkIndexScript(['B08','B11'],
  '(s.B08-s.B11)/(s.B08+s.B11+1e-9)', MOIST_DOM, MOIST_STOPS);
const NDMI_STRESS_COMPUTED = mkIndexScript(['B08','B11'],
  '-(s.B08-s.B11)/(s.B08+s.B11+1e-9)',
  [-1,-0.5,0,0.5,1],
  [[0.10,0.55,0.10,1],[0.70,0.90,0.40,1],[0.98,0.95,0.65,1],
   [0.95,0.50,0.15,1],[0.70,0.05,0.05,1]]);
const MSI_COMPUTED         = mkIndexScript(['B11','B08'],
  's.B11/(s.B08+1e-9)',
  [0,0.4,0.8,1.2,2.0,3.0],
  [[0.00,0.40,0.80,1],[0.40,0.75,0.95,1],[0.90,0.95,0.85,1],
   [0.95,0.85,0.45,1],[0.90,0.45,0.10,1],[0.60,0.05,0.05,1]]);
const NDII_COMPUTED        = mkIndexScript(['B08','B11'],
  '(s.B08-s.B11)/(s.B08+s.B11+1e-9)', MOIST_DOM, MOIST_STOPS);

// ── Soil / Urban indices ──────────────────────────────────────────────────────
const BSI_COMPUTED  = mkIndexScript(['B11','B04','B08','B02'],
  '((s.B11+s.B04)-(s.B08+s.B02))/((s.B11+s.B04)+(s.B08+s.B02)+1e-9)',
  [-0.5,-0.2,0,0.1,0.3,0.5],
  [[0.10,0.45,0.10,1],[0.55,0.80,0.35,1],[0.90,0.95,0.65,1],
   [0.95,0.85,0.50,1],[0.80,0.55,0.25,1],[0.60,0.30,0.10,1]]);
const NDBI_COMPUTED = mkIndexScript(['B11','B08'],
  '(s.B11-s.B08)/(s.B11+s.B08+1e-9)',
  [-0.5,-0.2,0,0.2,0.4,0.6],
  [[0.10,0.45,0.10,1],[0.70,0.90,0.55,1],[0.95,0.95,0.75,1],
   [0.85,0.75,0.65,1],[0.65,0.50,0.50,1],[0.45,0.35,0.55,1]]);

// ── Fire / Burn indices ───────────────────────────────────────────────────────
const NBR_COMPUTED   = mkIndexScript(['B08','B12'],
  '(s.B08-s.B12)/(s.B08+s.B12+1e-9)', VEG_DOM, VEG_STOPS);
const NBR2_COMPUTED  = mkIndexScript(['B8A','B12'],
  '(s.B8A-s.B12)/(s.B8A+s.B12+1e-9)', VEG_DOM, VEG_STOPS);
const BAIS2_COMPUTED = mkIndexScript(['B06','B07','B8A','B04','B12'],
  '(1-Math.sqrt((s.B06*s.B07*s.B8A)/(s.B04+1e-9)))*((s.B12-s.B8A)/(Math.sqrt(s.B12+s.B8A+1e-9))+1)',
  [0,0.5,1.0,1.5,2.0,3.0],
  [[0.10,0.45,0.10,1],[0.65,0.90,0.40,1],[0.95,0.95,0.65,1],
   [0.95,0.70,0.20,1],[0.85,0.20,0.05,1],[0.50,0.05,0.05,1]]);
const NDSI_COMPUTED  = mkIndexScript(['B03','B11'],
  '(s.B03-s.B11)/(s.B03+s.B11+1e-9)',
  [-0.5,-0.2,0,0.3,0.6,1.0],
  [[0.40,0.30,0.20,1],[0.65,0.65,0.55,1],[0.80,0.85,0.90,1],
   [0.90,0.95,0.98,1],[0.95,0.98,1.00,1],[1.00,1.00,1.00,1]]);

// ── Chlorophyll / Pigment indices ─────────────────────────────────────────────
const NDCI_COMPUTED    = mkIndexScript(['B07','B05'],
  '(s.B07-s.B05)/(s.B07+s.B05+1e-9)', VEG_DOM, VEG_STOPS);
const MCARI_COMPUTED   = mkIndexScript(['B05','B04','B03'],
  '((s.B05-s.B04)-0.2*(s.B05-s.B03))*(s.B05/(s.B04+1e-9))',
  [0,0.05,0.1,0.2,0.4,0.6],
  [[0.80,0.10,0.10,1],[0.90,0.55,0.15,1],[0.90,0.85,0.20,1],
   [0.45,0.80,0.20,1],[0.10,0.55,0.10,1],[0.00,0.35,0.05,1]]);
const ARI_COMPUTED     = mkIndexScript(['B03','B05'],
  'Math.max(0,Math.min(1,(1/(s.B03+1e-9)-1/(s.B05+1e-9))/20))',
  [0,0.2,0.4,0.6,0.8,1],
  [[0.10,0.55,0.10,1],[0.55,0.80,0.30,1],[0.90,0.95,0.20,1],
   [0.95,0.65,0.15,1],[0.85,0.25,0.25,1],[0.60,0.05,0.15,1]]);
const SIPI1_COMPUTED   = mkIndexScript(['B08','B02','B04'],
  '(s.B08-s.B02)/(s.B08+s.B04+1e-9)', VEG_DOM, VEG_STOPS);
const PSSRB1_COMPUTED  = mkIndexScript(['B08','B05'],
  'Math.max(0,Math.min(1,s.B08/(s.B05+1e-9)/10))',
  [0,0.1,0.2,0.4,0.6,0.8,1], VEG_STOPS);

// ---------------------------------------------------------------------------
// Index → evalscript routing
// Vegetation/water/fire/chlorophyll indices now compute the actual formula
// and apply a colour ramp (colorBlend). RGB composites remain unchanged.
// ---------------------------------------------------------------------------

const EVALSCRIPTS: Record<string, string> = {
  // ── RGB composites — direct band imagery (unchanged) ────────────────────────
  TRUE_COLOR,
  TRUE_COLOR_L1C,
  TRUE_COLOR_L2A,
  FALSE_COLOR:       FALSE_COLOR_IR,
  SWIR,
  FALSE_COLOR_URBAN,

  // ── Vegetation indices — computed colourmap ─────────────────────────────────
  NDVI:              NDVI_COMPUTED,
  EVI:               EVI_COMPUTED,
  EVI2:              EVI2_COMPUTED,
  GNDVI:             GNDVI_COMPUTED,
  KNDVI:             KNDVI_COMPUTED,
  SAVI:              SAVI_COMPUTED,
  MSAVI:             MSAVI_COMPUTED,
  OSAVI:             OSAVI_COMPUTED,
  ARVI:              ARVI_COMPUTED,
  NDRE:              NDRE_COMPUTED,
  RECI:              RECI_COMPUTED,
  LAI:               LAI_COMPUTED,
  FAPAR:             FAPAR_COMPUTED,
  FCOVER:            FCOVER_COMPUTED,
  NDYI:              NDYI_COMPUTED,
  PSRI:              PSRI_COMPUTED,
  REDEDGE_POSITION:  NDRE_COMPUTED,

  // ── Water / Moisture indices — computed colourmap ───────────────────────────
  NDWI:        NDWI_COMPUTED,
  MNDWI:       MNDWI_COMPUTED,
  NDMI:        NDMI_COMPUTED,
  NDMI_STRESS: NDMI_STRESS_COMPUTED,
  MSI:         MSI_COMPUTED,
  NDII:        NDII_COMPUTED,

  // ── Soil / Urban indices — computed ────────────────────────────────────────
  BSI:  BSI_COMPUTED,
  NBSI: BSI_COMPUTED,
  NDBI: NDBI_COMPUTED,
  IBI:  NDBI_COMPUTED,

  // ── Fire / Burn / Snow indices — computed ──────────────────────────────────
  NBR:   NBR_COMPUTED,
  NBR2:  NBR2_COMPUTED,
  BAIS2: BAIS2_COMPUTED,
  NDSI:  NDSI_COMPUTED,
  NDGI:  NDSI_COMPUTED,

  // ── Chlorophyll / Pigment indices — computed ────────────────────────────────
  NDCI:             NDCI_COMPUTED,
  CHL_REDEDGE:      RECI_COMPUTED,
  MCARI:            MCARI_COMPUTED,
  ARI:              ARI_COMPUTED,
  MARI:             ARI_COMPUTED,
  SIPI1:            SIPI1_COMPUTED,
  PSSRB1:           PSSRB1_COMPUTED,
};

// ---------------------------------------------------------------------------
// Human-readable label shown in the status badge and response headers
// ---------------------------------------------------------------------------
const BASE_COMPOSITE_LABELS: Record<string, string> = {
  TRUE_COLOR: 'True Color', TRUE_COLOR_L1C: 'True Color L1C', TRUE_COLOR_L2A: 'True Color L2A',
  FALSE_COLOR: 'False Color IR', SWIR: 'SWIR', FALSE_COLOR_URBAN: 'False Color Urban',
};

function getCompositeLabel(index: string): string {
  return BASE_COMPOSITE_LABELS[index.toUpperCase()] ?? index.toUpperCase();
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);

  const index = (searchParams.get('index') ?? '').toUpperCase();
  const westStr  = searchParams.get('west');
  const southStr = searchParams.get('south');
  const eastStr  = searchParams.get('east');
  const northStr = searchParams.get('north');
  const widthStr  = searchParams.get('width')  ?? '512';
  const heightStr = searchParams.get('height') ?? '512';
  // Optional date range — if provided, fetch imagery for that specific window
  // (used by the timeline slider). Format: ISO 8601 strings.
  const fromStr = searchParams.get('from');
  const toStr   = searchParams.get('to');

  if (!index || !westStr || !southStr || !eastStr || !northStr) {
    return NextResponse.json(
      { error: 'Missing required params: index, west, south, east, north' },
      { status: 400 },
    );
  }

  const evalscript = EVALSCRIPTS[index];
  if (!evalscript) {
    return NextResponse.json(
      { error: `Unknown index "${index}". Supported: ${Object.keys(EVALSCRIPTS).join(', ')}` },
      { status: 400 },
    );
  }

  const west  = parseFloat(westStr);
  const south = parseFloat(southStr);
  const east  = parseFloat(eastStr);
  const north = parseFloat(northStr);
  const width  = Math.min(2048, Math.max(1, parseInt(widthStr,  10) || 512));
  const height = Math.min(2048, Math.max(1, parseInt(heightStr, 10) || 512));

  if ([west, south, east, north].some(isNaN)) {
    return NextResponse.json({ error: 'west, south, east, north must be numbers' }, { status: 400 });
  }

  // Determine time range and mosaicking strategy:
  //   Specific date  → tight ±5-day window around the selected acquisition date,
  //                     mostRecent ordering (caller verified the date via STAC catalog).
  //   Latest mode    → 18-month rolling window, leastCC ordering (picks clearest scene).
  const now = new Date();
  let fromDate: Date;
  let toDate: Date;
  let mosaickingOrder: string;

  if (fromStr && toStr) {
    fromDate = new Date(fromStr);
    toDate   = new Date(toStr);
    if (isNaN(fromDate.getTime()) || isNaN(toDate.getTime())) {
      return NextResponse.json({ error: 'Invalid from/to date format' }, { status: 400 });
    }
    // Specific date: use a tight window — caller sends ±5 days around the acquisition
    // date returned by the STAC catalog. We keep that window as-is so we match the
    // correct scene rather than drifting to a different (potentially clearer) date.
    mosaickingOrder = 'mostRecent';
  } else {
    // Latest mode — 18-month window; leastCC picks the least-cloudy pixel composite
    // across the entire window, delivering the best available scene for the area.
    toDate = now;
    fromDate = new Date(now);
    fromDate.setMonth(fromDate.getMonth() - 18);
    mosaickingOrder = 'leastCC';
  }

  // Cache key — unique per index (computed scripts differ per formula).
  const compositeKey = getCompositeLabel(index);
  const cacheKey = [
    index, west, south, east, north,
    fromDate.toISOString().split('T')[0],
    toDate.toISOString().split('T')[0],
    `${width}x${height}`,
  ].join('::');

  const cached = imageCacheGet(cacheKey);
  if (cached) {
    return new NextResponse(cached, {
      status: 200,
      headers: {
        'Content-Type': 'image/png',
        'Cache-Control': 'public, max-age=3600',
        'X-Cache': 'HIT',
        'X-Composite': compositeKey,
        'Content-Length': String(cached.byteLength),
      },
    });
  }

  const token = await getToken();
  if (!token) {
    return NextResponse.json({ error: 'sentinel_hub_unavailable' }, { status: 503 });
  }

  // Derive process URL:
  //   1. Explicit SH_BASE_URL (operator override, highest priority)
  //   2. CDSE credentials present → always force sh.dataspace.copernicus.eu
  //      CDSE tokens (from identity.dataspace.copernicus.eu) are rejected by
  //      services.sentinel-hub.com (commercial), so we must not fall through to it.
  //   3. Legacy SENTINEL_HUB_PROCESS_URL (commercial SH with its own credentials)
  //   4. CDSE default
  const processUrl =
    (process.env.SH_BASE_URL ? `${process.env.SH_BASE_URL}/api/v1/process` : null) ||
    (process.env.CDSE_CLIENT_ID ? 'https://sh.dataspace.copernicus.eu/api/v1/process' : null) ||
    process.env.SENTINEL_HUB_PROCESS_URL ||
    'https://sh.dataspace.copernicus.eu/api/v1/process';

  const requestBody = {
    input: {
      bounds: {
        bbox: [west, south, east, north],
        properties: { crs: 'http://www.opengis.net/def/crs/EPSG/0/4326' },
      },
      data: [
        {
          type: 'sentinel-2-l2a',
          dataFilter: {
            timeRange: {
              from: fromDate.toISOString(),
              to:   toDate.toISOString(),
            },
            maxCloudCoverage: 100,
            mosaickingOrder,
          },
          processing: { upsampling: 'BILINEAR', downsampling: 'BILINEAR' },
        },
      ],
    },
    output: {
      width,
      height,
      responses: [{ identifier: 'default', format: { type: 'image/png' } }],
    },
    evalscript,
  };

  try {
    const res = await fetch(processUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        Accept: 'image/png',
      },
      body: JSON.stringify(requestBody),
      signal: AbortSignal.timeout(30000),
    });

    if (!res.ok) {
      return NextResponse.json({ error: 'sentinel_hub_unavailable' }, { status: 503 });
    }

    const imageBuffer = await res.arrayBuffer();
    imageCacheSet(cacheKey, imageBuffer);

    return new NextResponse(imageBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'image/png',
        'Cache-Control': 'public, max-age=3600',
        'X-Cache': 'MISS',
        'X-Composite': compositeKey,
        'Content-Length': String(imageBuffer.byteLength),
      },
    });
  } catch {
    return NextResponse.json({ error: 'sentinel_hub_unavailable' }, { status: 503 });
  }
}
