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

/**
 * Red-Edge False Color: B8A(R) B05(G) B03(B)
 * Uses the red-edge bands (705–783 nm) that are highly sensitive to
 * chlorophyll content, canopy structure, and early stress signals.
 * Best for chlorophyll, pigment, and red-edge position indices.
 */
const RED_EDGE_FC = rgbScript('B8A', 'B05', 'B03');

// ---------------------------------------------------------------------------
// Index → evalscript routing
// Each entry maps a layer/index ID to the most informative real-imagery composite.
// No synthetic colour ramps — every response is actual Sentinel-2 reflectance data.
// ---------------------------------------------------------------------------

export const EVALSCRIPTS: Record<string, string> = {
  // ── RGB composites — direct band imagery ───────────────────────────────────
  TRUE_COLOR,
  TRUE_COLOR_L1C,
  TRUE_COLOR_L2A,
  FALSE_COLOR:       FALSE_COLOR_IR,
  SWIR,
  FALSE_COLOR_URBAN,

  // ── Vegetation indices → False Color IR ────────────────────────────────────
  // NIR reflectance is the primary driver for all these indices.
  // Healthy dense vegetation appears vivid red/magenta; stressed → pale; bare → dark.
  NDVI:   FALSE_COLOR_IR,
  EVI:    FALSE_COLOR_IR,
  EVI2:   FALSE_COLOR_IR,
  GNDVI:  FALSE_COLOR_IR,
  KNDVI:  FALSE_COLOR_IR,
  SAVI:   FALSE_COLOR_IR,
  MSAVI:  FALSE_COLOR_IR,
  OSAVI:  FALSE_COLOR_IR,
  ARVI:   FALSE_COLOR_IR,
  LAI:    FALSE_COLOR_IR,
  FAPAR:  FALSE_COLOR_IR,
  FCOVER: FALSE_COLOR_IR,

  // Red-edge indices → Red-Edge False Color (more sensitive to early stress)
  NDRE:              RED_EDGE_FC,
  REDEDGE_POSITION:  RED_EDGE_FC,

  // Yellowing / senescence — visible naturally in True Color
  NDYI: TRUE_COLOR,
  PSRI: TRUE_COLOR,

  // ── Water / Moisture indices → SWIR ────────────────────────────────────────
  // Water absorbs strongly in SWIR; wet features appear dark vs. dry bright.
  NDWI:        SWIR,
  MNDWI:       SWIR,
  NDMI:        SWIR,
  NDMI_STRESS: SWIR,
  MSI:         SWIR,
  NDII:        SWIR,

  // ── Soil / Bare-soil indices → False Color Urban ────────────────────────────
  // B11/B12 differentiate soil moisture and mineral composition well.
  BSI:  FALSE_COLOR_URBAN,
  NBSI: FALSE_COLOR_URBAN,

  // ── Snow / Ice indices → True Color ────────────────────────────────────────
  // Snow appears naturally white; ice/snow boundaries clearly visible.
  NDSI: TRUE_COLOR,
  NDGI: TRUE_COLOR,

  // ── Fire / Burn indices → SWIR ─────────────────────────────────────────────
  // Burn scars appear red/pink in B12; active fires glow orange.
  NBR:   SWIR,
  NBR2:  SWIR,
  BAIS2: SWIR,

  // ── Urban indices → False Color Urban ──────────────────────────────────────
  NDBI: FALSE_COLOR_URBAN,
  IBI:  FALSE_COLOR_URBAN,

  // ── Chlorophyll / Pigment indices → Red-Edge False Color ───────────────────
  // Red-edge bands (B05 705nm, B8A 783nm) are chlorophyll-diagnostic wavelengths.
  NDCI:             RED_EDGE_FC,
  CHL_REDEDGE:      RED_EDGE_FC,
  MCARI:            RED_EDGE_FC,
  ARI:              RED_EDGE_FC,
  MARI:             RED_EDGE_FC,
  SIPI1:            FALSE_COLOR_IR,
  PSSRB1:           FALSE_COLOR_IR,
};

// ---------------------------------------------------------------------------
// Human-readable label for each composite (shown in the status badge)
// ---------------------------------------------------------------------------
const COMPOSITE_LABEL: Record<string, string> = {
  [TRUE_COLOR]:         'True Color',
  [TRUE_COLOR_L1C]:     'True Color L1C',
  [TRUE_COLOR_L2A]:     'True Color L2A',
  [FALSE_COLOR_IR]:     'False Color IR',
  [SWIR]:               'SWIR',
  [FALSE_COLOR_URBAN]:  'False Color Urban',
  [RED_EDGE_FC]:        'Red-Edge False Color',
};

export function getCompositeLabel(index: string): string {
  const script = EVALSCRIPTS[index];
  return script ? (COMPOSITE_LABEL[script] ?? 'Sentinel-2') : 'Sentinel-2';
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

  // Cache key — includes all request dimensions.
  // Use composite label (not index) so NDVI and EVI share the same cached False Color IR tile.
  const compositeKey = getCompositeLabel(index);
  const cacheKey = [
    compositeKey, west, south, east, north,
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
