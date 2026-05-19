/**
 * Field AI Data Service
 * Fetches CDSE (Sentinel Hub) index statistics + OpenWeather + OpenMeteo
 * for a given field — used by the AI analysis pipeline in field-intelligence.
 */

import { Injectable, NotFoundException, Logger } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";

interface BBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface CdseIndexStats {
  indice: string;
  value: number | null;
  minValue: number | null;
  maxValue: number | null;
  stdDev: number | null;
  date: string;
  cloudCover: number | null;
}

export interface OpenWeatherData {
  temperature: number;
  feelsLike: number;
  humidity: number;
  windSpeed: number;
  windDirection: number;
  precipitation: number;
  description: string;
  pressure: number;
  cloudCover: number;
  visibility: number;
}

export interface OpenMeteoData {
  temperature2m: number | null;
  relativeHumidity2m: number | null;
  precipitation: number | null;
  windSpeed10m: number | null;
  soilMoisture0to1cm: number | null;
  et0FaoEvapotranspiration: number | null;
  surfacePressure: number | null;
  cloudCover: number | null;
  shortwaveRadiation: number | null;
}

export interface FieldAiData {
  field: {
    id: string;
    name: string;
    nameAr: string | null;
    lat: number;
    lng: number;
    areaHa: number | null;
    cropType: string | null;
    soilType: string | null;
  };
  cdse: CdseIndexStats;
  weather: OpenWeatherData | null;
  meteo: OpenMeteoData | null;
  indice: string;
  fetchedAt: string;
}

// Evalscripts for common CDSE indices (Sentinel-2 L2A)
const EVALSCRIPTS: Record<string, string> = {
  NDVI: `//VERSION=3
function setup(){return{input:["B04","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[(s.B08-s.B04)/(s.B08+s.B04+1e-10)];}`,

  EVI: `//VERSION=3
function setup(){return{input:["B02","B04","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[2.5*(s.B08-s.B04)/(s.B08+6*s.B04-7.5*s.B02+1)];}`,

  NDWI: `//VERSION=3
function setup(){return{input:["B03","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[(s.B03-s.B08)/(s.B03+s.B08+1e-10)];}`,

  NDMI: `//VERSION=3
function setup(){return{input:["B08","B11","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[(s.B08-s.B11)/(s.B08+s.B11+1e-10)];}`,

  SAVI: `//VERSION=3
function setup(){return{input:["B04","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[1.5*(s.B08-s.B04)/(s.B08+s.B04+0.5)];}`,

  NDRE: `//VERSION=3
function setup(){return{input:["B05","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[(s.B08-s.B05)/(s.B08+s.B05+1e-10)];}`,

  NBR: `//VERSION=3
function setup(){return{input:["B08","B12","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[(s.B08-s.B12)/(s.B08+s.B12+1e-10)];}`,

  BSI: `//VERSION=3
function setup(){return{input:["B02","B04","B08","B11","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];let a=s.B11+s.B04,b=s.B08+s.B02;return[(a-b)/(a+b+1e-10)];}`,

  MSAVI: `//VERSION=3
function setup(){return{input:["B04","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];let n=s.B08,r=s.B04;return[(2*n+1-Math.sqrt(Math.pow(2*n+1,2)-8*(n-r)))/2];}`,

  GNDVI: `//VERSION=3
function setup(){return{input:["B03","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];return[(s.B08-s.B03)/(s.B08+s.B03+1e-10)];}`,

  LAI: `//VERSION=3
function setup(){return{input:["B04","B08","dataMask"],output:{bands:1,sampleType:"FLOAT32"}};}
function evaluatePixel(s){if(s.dataMask===0)return[NaN];let ndvi=(s.B08-s.B04)/(s.B08+s.B04+1e-10);return[Math.max(0,3.618*ndvi-0.118)];}`,
};

function getEvalscript(indice: string): string {
  return EVALSCRIPTS[indice.toUpperCase()] ?? EVALSCRIPTS["NDVI"];
}

@Injectable()
export class FieldAiDataService {
  private readonly logger = new Logger(FieldAiDataService.name);

  constructor(private readonly prisma: PrismaService) {}

  async getFieldAiData(
    fieldId: string,
    tenantId: string,
    indice: string,
  ): Promise<FieldAiData> {
    // Verify field exists and belongs to tenant
    const field = await this.prisma.field.findFirst({
      where: { id: fieldId, tenantId, isDeleted: false },
      select: {
        id: true,
        name: true,
        cropType: true,
        soilType: true,
        areaHectares: true,
        metadata: true,
        ndviValue: true,
      },
    });

    if (!field) throw new NotFoundException(`Field ${fieldId} not found`);

    // Fetch nameAr from metadata if present
    const meta = field.metadata as Record<string, unknown> | null;
    const nameAr = (meta?.nameAr as string | undefined) ?? null;

    // Get centroid + bbox from PostGIS via raw SQL
    const geomRows = await this.prisma.$queryRawUnsafe<
      Array<{
        centroid_lng: number | null;
        centroid_lat: number | null;
        min_lng: number | null;
        min_lat: number | null;
        max_lng: number | null;
        max_lat: number | null;
      }>
    >(
      `SELECT
         ST_X(centroid::geometry) AS centroid_lng,
         ST_Y(centroid::geometry) AS centroid_lat,
         ST_XMin(boundary::geometry) AS min_lng,
         ST_YMin(boundary::geometry) AS min_lat,
         ST_XMax(boundary::geometry) AS max_lng,
         ST_YMax(boundary::geometry) AS max_lat
       FROM fields
       WHERE id = $1::uuid AND boundary IS NOT NULL`,
      fieldId,
    );

    const geom = geomRows[0];
    const lat = geom?.centroid_lat != null ? Number(geom.centroid_lat) : null;
    const lng = geom?.centroid_lng != null ? Number(geom.centroid_lng) : null;

    if (lat == null || lng == null) {
      throw new Error(`Field ${fieldId} has no geometry / centroid`);
    }

    const bbox: BBox = geom?.min_lng != null
      ? {
          west: Number(geom.min_lng),
          south: Number(geom.min_lat),
          east: Number(geom.max_lng),
          north: Number(geom.max_lat),
        }
      : { west: lng - 0.005, south: lat - 0.005, east: lng + 0.005, north: lat + 0.005 };

    const upperIndice = indice.toUpperCase();

    const [cdseResult, weatherResult, meteoResult] = await Promise.allSettled([
      this.fetchCdseStats(upperIndice, bbox),
      this.fetchOpenWeather(lat, lng),
      this.fetchOpenMeteo(lat, lng),
    ]);

    let cdse: CdseIndexStats =
      cdseResult.status === "fulfilled"
        ? cdseResult.value
        : { indice: upperIndice, value: null, minValue: null, maxValue: null, stdDev: null, date: new Date().toISOString(), cloudCover: null };

    // ── KPI snapshot fallback: if live CDSE value is null, use the most recent
    // stored snapshot value for this index so the AI always has a number to work with.
    if (cdse.value === null) {
      try {
        const snapshot = await this.prisma.fieldKpiSnapshot.findFirst({
          where: { fieldId, tenantId },
          orderBy: { fetchedAt: "desc" },
        });

        if (snapshot) {
          const snapshotValue = this.extractSnapshotValue(snapshot, upperIndice);
          if (snapshotValue !== null) {
            this.logger.log(
              `Using KPI snapshot fallback for ${upperIndice} on field ${fieldId}: ${snapshotValue}`,
            );
            cdse = {
              indice: upperIndice,
              value: snapshotValue,
              minValue: null,
              maxValue: null,
              stdDev: null,
              date: snapshot.fetchedAt?.toISOString() ?? new Date().toISOString(),
              cloudCover: snapshot.cloudProbability != null
                ? parseFloat(String(snapshot.cloudProbability))
                : null,
            };
          }
        }
      } catch (err) {
        this.logger.warn(`KPI snapshot fallback failed for field ${fieldId}: ${String(err)}`);
      }
    }

    // ── NdviReading fallback: query the historical timeseries table (same data
    // that powers the satellite map timeline). Pick the most recent reading
    // regardless of cloud cover — the date is shown to the AI so it knows the
    // imagery age (e.g. "last captured in May").
    if (cdse.value === null) {
      try {
        const reading = await this.prisma.ndviReading.findFirst({
          where: { fieldId, tenantId, isDeleted: false },
          orderBy: { capturedAt: "desc" },
          select: { value: true, capturedAt: true, cloudCover: true },
        });

        if (reading?.value != null) {
          const val = parseFloat(Number(reading.value).toFixed(4));
          if (Number.isFinite(val)) {
            this.logger.log(
              `Using NdviReading fallback for field ${fieldId}: NDVI=${val} captured at ${reading.capturedAt.toISOString()}`,
            );
            cdse = {
              // NdviReading only stores NDVI. For other indices we keep value null
              // but record the capture date so the AI has temporal context.
              indice: upperIndice,
              value: upperIndice === "NDVI" ? val : null,
              minValue: null,
              maxValue: null,
              stdDev: null,
              date: reading.capturedAt.toISOString(),
              cloudCover: reading.cloudCover != null
                ? parseFloat(String(reading.cloudCover))
                : null,
            };
          }
        }
      } catch (err) {
        this.logger.warn(`NdviReading fallback failed for field ${fieldId}: ${String(err)}`);
      }
    }

    // ── field.ndviValue fallback: the cached NDVI value stored on the field row
    // itself (written by updateFieldNdvi). Absolute last resort for NDVI.
    if (cdse.value === null && upperIndice === "NDVI" && field.ndviValue != null) {
      const val = parseFloat(Number(field.ndviValue).toFixed(4));
      if (Number.isFinite(val)) {
        this.logger.log(`Using field.ndviValue for field ${fieldId}: ${val}`);
        cdse = {
          indice: "NDVI",
          value: val,
          minValue: null,
          maxValue: null,
          stdDev: null,
          date: cdse.date,
          cloudCover: cdse.cloudCover,
        };
      }
    }

    return {
      field: {
        id: field.id,
        name: field.name,
        nameAr,
        lat,
        lng,
        areaHa: field.areaHectares != null ? parseFloat(String(field.areaHectares)) : null,
        cropType: field.cropType ?? null,
        soilType: field.soilType ?? null,
      },
      cdse,
      weather: weatherResult.status === "fulfilled" ? weatherResult.value : null,
      meteo: meteoResult.status === "fulfilled" ? meteoResult.value : null,
      indice: upperIndice,
      fetchedAt: new Date().toISOString(),
    };
  }

  /** Maps an index name (e.g. "NDVI") to its numeric value in a KPI snapshot row */
  private extractSnapshotValue(
    snapshot: Record<string, unknown>,
    indice: string,
  ): number | null {
    const map: Record<string, string> = {
      NDVI: "ndvi", EVI: "evi", EVI2: "evi2",
      NDWI: "ndwi", NDMI: "ndmi", NDMI_STRESS: "ndmi",
      SAVI: "savi", LAI: "lai", NDRE: "ndre",
      NBR: "nbr", NBR2: "nbr2", BSI: "bsi",
      MSAVI: "msavi", GNDVI: "gndvi", ARVI: "arvi",
      BAIS2: "bais2", NDBI: "ndbi", NDSI: "ndsi",
      NDGI: "ndgi", LST: "lst",
    };
    const key = map[indice];
    if (!key) return null;
    const raw = snapshot[key];
    if (raw == null) return null;
    const n = parseFloat(String(raw));
    return Number.isFinite(n) ? parseFloat(n.toFixed(4)) : null;
  }

  private async fetchCdseStats(indice: string, bbox: BBox): Promise<CdseIndexStats> {
    const clientId = process.env.SENTINEL_HUB_CLIENT_ID;
    const clientSecret = process.env.SENTINEL_HUB_CLIENT_SECRET;

    if (!clientId || !clientSecret) {
      this.logger.warn("Sentinel Hub credentials not configured — skipping CDSE fetch");
      return { indice, value: null, minValue: null, maxValue: null, stdDev: null, date: new Date().toISOString(), cloudCover: null };
    }

    try {
      const authUrl =
        process.env.SENTINEL_HUB_AUTH_URL ??
        "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token";

      const tokenRes = await fetch(
        authUrl,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            grant_type: "client_credentials",
            client_id: clientId,
            client_secret: clientSecret,
          }).toString(),
          signal: AbortSignal.timeout(15000),
        },
      );

      if (!tokenRes.ok) throw new Error(`Token request failed: ${tokenRes.status}`);

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const tokenBody = (await tokenRes.json()) as any;
      const access_token: string = tokenBody.access_token;

      const today = new Date();

      // Helper: build a statistics payload for a given lookback window and cloud threshold
      const buildPayload = (lookbackDays: number, maxCloud: number) => {
        const from = new Date(today);
        from.setDate(from.getDate() - lookbackDays);
        return {
          payload: {
            input: {
              bounds: {
                bbox: [bbox.west, bbox.south, bbox.east, bbox.north],
                properties: { crs: "http://www.opengis.net/def/crs/OGC/1.3/CRS84" },
              },
              data: [
                {
                  type: "sentinel-2-l2a",
                  dataFilter: { mosaickingOrder: "leastCC", maxCloudCoverage: maxCloud },
                },
              ],
            },
            aggregation: {
              timeRange: {
                from: from.toISOString().split("T")[0] + "T00:00:00Z",
                to: today.toISOString().split("T")[0] + "T23:59:59Z",
              },
              aggregationInterval: { of: `P${lookbackDays}D` },
              resx: 10,
              resy: 10,
              evalscript: getEvalscript(indice),
            },
            calculations: {
              default: {
                statistics: { default: { percentiles: { k: [25, 50, 75] } } },
              },
            },
          },
          fromStr: from.toISOString().split("T")[0] + "T00:00:00Z",
        };
      };

      // Try progressively wider windows to always find the latest available imagery
      const attempts = [
        buildPayload(30, 50),
        buildPayload(90, 80),
        buildPayload(180, 90),
        buildPayload(365, 100),
      ];

      let stats: Record<string, number> | null = null;
      let usedFromStr = attempts[0].fromStr;
      let intervalFrom: string | undefined;

      const statsApiBase =
        process.env.SENTINEL_HUB_API_URL ??
        "https://services.sentinel-hub.com/api/v1";

      for (const attempt of attempts) {
        if (stats != null) break;
        const { payload, fromStr } = attempt;
        usedFromStr = fromStr;

        const statsRes = await fetch(
          `${statsApiBase}/statistics`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${access_token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
            signal: AbortSignal.timeout(30000),
          },
        );

        if (!statsRes.ok) {
          const errText = await statsRes.text().catch(() => "");
          this.logger.warn(`Statistics API ${statsRes.status} (window=${fromStr}): ${errText.slice(0, 200)}`);
          continue;
        }

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const statsData = (await statsRes.json()) as any;
        const interval = statsData?.data?.[0];
        const candidate = interval?.outputs?.default?.bands?.B0?.stats;

        // Accept only if mean is a finite number (not NaN / null)
        const mean = candidate?.mean != null ? Number(candidate.mean) : NaN;
        if (Number.isFinite(mean)) {
          stats = candidate;
          intervalFrom = interval?.interval?.from;
        }
      }

      return {
        indice,
        value: stats?.mean != null && Number.isFinite(Number(stats.mean))
          ? parseFloat(Number(stats.mean).toFixed(4))
          : null,
        minValue: stats?.min != null && Number.isFinite(Number(stats.min))
          ? parseFloat(Number(stats.min).toFixed(4))
          : null,
        maxValue: stats?.max != null && Number.isFinite(Number(stats.max))
          ? parseFloat(Number(stats.max).toFixed(4))
          : null,
        stdDev: stats?.stDev != null && Number.isFinite(Number(stats.stDev))
          ? parseFloat(Number(stats.stDev).toFixed(4))
          : null,
        date: intervalFrom ?? usedFromStr,
        cloudCover: null,
      };
    } catch (err) {
      this.logger.error(`CDSE stats fetch failed for ${indice}: ${String(err)}`);
      return { indice, value: null, minValue: null, maxValue: null, stdDev: null, date: new Date().toISOString(), cloudCover: null };
    }
  }

  private async fetchOpenWeather(lat: number, lng: number): Promise<OpenWeatherData | null> {
    const apiKey = process.env.OPENWEATHERMAP_API_KEY ?? process.env.OPENWEATHER_API_KEY;
    if (!apiKey) {
      this.logger.warn("OpenWeatherMap API key not configured");
      return null;
    }

    try {
      const res = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${apiKey}&units=metric`,
        { signal: AbortSignal.timeout(10000) },
      );
      if (!res.ok) throw new Error(`OpenWeather ${res.status}`);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const d = (await res.json()) as any;
      return {
        temperature: d.main?.temp ?? 0,
        feelsLike: d.main?.feels_like ?? 0,
        humidity: d.main?.humidity ?? 0,
        windSpeed: d.wind?.speed ?? 0,
        windDirection: d.wind?.deg ?? 0,
        precipitation: d.rain?.["1h"] ?? d.snow?.["1h"] ?? 0,
        description: d.weather?.[0]?.description ?? "",
        pressure: d.main?.pressure ?? 0,
        cloudCover: d.clouds?.all ?? 0,
        visibility: Math.round((d.visibility ?? 10000) / 1000),
      };
    } catch (err) {
      this.logger.error(`OpenWeather fetch failed: ${String(err)}`);
      return null;
    }
  }

  private async fetchOpenMeteo(lat: number, lng: number): Promise<OpenMeteoData | null> {
    const vars = [
      "temperature_2m",
      "relative_humidity_2m",
      "precipitation",
      "wind_speed_10m",
      "soil_moisture_0_to_1cm",
      "et0_fao_evapotranspiration",
      "surface_pressure",
      "cloud_cover",
      "shortwave_radiation",
    ].join(",");

    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=${vars}&wind_speed_unit=ms`,
        { signal: AbortSignal.timeout(10000) },
      );
      if (!res.ok) throw new Error(`OpenMeteo ${res.status}`);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const d = (await res.json()) as any;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const c: any = d.current ?? {};
      return {
        temperature2m: c.temperature_2m ?? null,
        relativeHumidity2m: c.relative_humidity_2m ?? null,
        precipitation: c.precipitation ?? null,
        windSpeed10m: c.wind_speed_10m ?? null,
        soilMoisture0to1cm: c.soil_moisture_0_to_1cm ?? null,
        et0FaoEvapotranspiration: c.et0_fao_evapotranspiration ?? null,
        surfacePressure: c.surface_pressure ?? null,
        cloudCover: c.cloud_cover ?? null,
        shortwaveRadiation: c.shortwave_radiation ?? null,
      };
    } catch (err) {
      this.logger.error(`OpenMeteo fetch failed: ${String(err)}`);
      return null;
    }
  }
}
