/**
 * Sentinel Hub integration — server-side only.
 * Keeps OAuth token in module-level cache to avoid re-fetching on every request.
 */

export type SentinelIndex = "NDVI" | "EVI" | "NDWI" | "TRUE_COLOR" | "FALSE_COLOR";

// ── Token cache ─────────────────────────────────────────────────────────────

let cachedToken: { value: string; expiresAt: number } | null = null;

export async function getSentinelToken(): Promise<string> {
  if (cachedToken && Date.now() < cachedToken.expiresAt - 60_000) {
    return cachedToken.value;
  }

  const res = await fetch(
    process.env.SENTINEL_HUB_AUTH_URL!,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: process.env.SENTINEL_HUB_CLIENT_ID!,
        client_secret: process.env.SENTINEL_HUB_CLIENT_SECRET!,
      }),
    }
  );

  if (!res.ok) throw new Error(`SH token fetch failed: ${res.status}`);

  const data = await res.json();
  cachedToken = {
    value: data.access_token,
    expiresAt: Date.now() + data.expires_in * 1000,
  };
  return cachedToken.value;
}

// ── Evalscripts ─────────────────────────────────────────────────────────────

const EVALSCRIPTS: Record<SentinelIndex, string> = {
  NDVI: `//VERSION=3
function setup() { return { input: ["B04","B08","dataMask"], output: { bands: 4 } }; }
function evaluatePixel(s) {
  const ndvi = (s.B08 - s.B04) / (s.B08 + s.B04);
  const c = colorBlend(ndvi,[-0.2,0,0.2,0.4,0.6,0.8,1.0],
    [[0.75,0.75,0.75],[0.86,0.08,0.23],[1,0.65,0],[1,1,0.6],[0.56,0.93,0.56],[0.13,0.55,0.13],[0,0.27,0]]);
  return [c[0],c[1],c[2],s.dataMask];
}`,
  EVI: `//VERSION=3
function setup() { return { input: ["B02","B04","B08","dataMask"], output: { bands: 4 } }; }
function evaluatePixel(s) {
  const evi = 2.5 * (s.B08 - s.B04) / ((s.B08 + 6 * s.B04 - 7.5 * s.B02) + 1);
  const c = colorBlend(evi,[0,0.2,0.4,0.6,0.8,1.0],
    [[0.86,0.08,0.23],[1,0.65,0],[1,1,0],[0.56,0.93,0.56],[0.13,0.55,0.13],[0,0.27,0]]);
  return [c[0],c[1],c[2],s.dataMask];
}`,
  NDWI: `//VERSION=3
function setup() { return { input: ["B03","B08","dataMask"], output: { bands: 4 } }; }
function evaluatePixel(s) {
  const ndwi = (s.B03 - s.B08) / (s.B03 + s.B08);
  const c = colorBlend(ndwi,[-0.8,-0.4,0,0.4,0.8],
    [[0.6,0.4,0],[1,1,0.8],[0.8,0.9,1],[0.2,0.6,0.9],[0,0.3,0.7]]);
  return [c[0],c[1],c[2],s.dataMask];
}`,
  TRUE_COLOR: `//VERSION=3
function setup() { return { input: ["B04","B03","B02","dataMask"], output: { bands: 4 } }; }
function evaluatePixel(s) {
  return [3.5*s.B04, 3.5*s.B03, 3.5*s.B02, s.dataMask];
}`,
  FALSE_COLOR: `//VERSION=3
function setup() { return { input: ["B08","B04","B03","dataMask"], output: { bands: 4 } }; }
function evaluatePixel(s) {
  return [3.5*s.B08, 3.5*s.B04, 3.5*s.B03, s.dataMask];
}`,
};

// ── Process API call ─────────────────────────────────────────────────────────

export async function fetchSentinelImage(
  index: SentinelIndex,
  bbox: [number, number, number, number], // [minLng, minLat, maxLng, maxLat]
  dateFrom: string,
  dateTo: string,
  width = 512,
  height = 512
): Promise<Response> {
  const token = await getSentinelToken();

  const payload = {
    input: {
      bounds: {
        bbox,
        properties: { crs: "http://www.opengis.net/def/crs/EPSG/0/4326" },
      },
      data: [
        {
          type: "sentinel-2-l2a",
          dataFilter: {
            timeRange: { from: `${dateFrom}T00:00:00Z`, to: `${dateTo}T23:59:59Z` },
            maxCloudCoverage: 30,
            mosaickingOrder: "leastCC",
          },
        },
      ],
    },
    output: {
      width,
      height,
      responses: [{ identifier: "default", format: { type: "image/png" } }],
    },
    evalscript: EVALSCRIPTS[index],
  };

  return fetch(`${process.env.SENTINEL_HUB_API_URL}/process`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "image/png",
    },
    body: JSON.stringify(payload),
  });
}
