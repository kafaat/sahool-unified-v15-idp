/**
 * Field AI Data Aggregator
 * Aggregates all data needed for comprehensive field analysis:
 *  - All 37 CDSE spectral indices from vegetation-analysis-service
 *  - 4 satellite imagery thumbnails (True Color, NDVI, NDMI, NDRE)
 *  - Full field metadata (crop, prev crop, soil, dates, bbox) from field-management-service
 *  - Farm admin hierarchy (governorate, district) from field-management-service
 *  - Current weather from OpenWeather API
 *  - Maximum agro data from Open-Meteo API (soil moisture 5 depths, soil temp 4 depths, ET0, VPD, solar, 7-day forecast)
 *
 * Returns a ComprehensiveAnalysisRequest shape ready to POST to field-intelligence.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { FIELD_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

const FIELD_SERVICE_URL =
  process.env.FIELD_SERVICE_URL || process.env.FIELD_MANAGEMENT_URL || 'http://field-management-service:3000';
const VEGETATION_URL =
  process.env.VEGETATION_ANALYSIS_URL || 'http://vegetation-analysis-service:8090';
const OPENWEATHER_API_KEY = process.env.OPENWEATHER_API_KEY || process.env.OPENWEATHERMAP_API_KEY || '';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const SAFE_INDICE = /^[A-Z0-9_]{2,20}$/;

function authHeaders(token?: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function extractTenantId(token?: string): string | null {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const decoded = JSON.parse(Buffer.from(parts[1] as string, 'base64').toString());
    return (decoded.tid ?? decoded.tenant_id ?? null) as string | null;
  } catch {
    return null;
  }
}


async function fetchWithTimeout(url: string, opts: RequestInit = {}, timeoutMs = 20000): Promise<Response> {
  return fetch(url, { ...opts, signal: AbortSignal.timeout(timeoutMs) });
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const { searchParams } = req.nextUrl;
  const fieldId = searchParams.get('fieldId');
  const indice = (searchParams.get('indice') ?? 'NDVI').toUpperCase();

  if (!fieldId || !UUID_RE.test(fieldId)) {
    return NextResponse.json({ error: 'Invalid fieldId' }, { status: 400 });
  }
  if (!SAFE_INDICE.test(indice)) {
    return NextResponse.json({ error: 'Invalid indice' }, { status: 400 });
  }

  // Accept lat/lng from query params (frontend knows the field coordinates from the map)
  const qLat = searchParams.get('lat');
  const qLng = searchParams.get('lng');

  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;
  const auth = authHeaders(token);
  const tenantId = extractTenantId(token);
  const today = new Date().toISOString().slice(0, 10);

  // Build common headers including tenant context
  const commonHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...auth,
    ...(tenantId ? { 'X-Tenant-Id': tenantId } : {}),
  };

  // ── Step 1: Fetch field details FIRST (need metadata for AI analysis) ───────
  let fieldData: Record<string, unknown> = {};
  try {
    const fieldRes = await fetchWithTimeout(
      `${FIELD_SERVICE_URL}${buildUrl(FIELD_ENDPOINTS.GET, { fieldId })}?include=farm`,
      { headers: commonHeaders },
    );
    if (fieldRes.ok) {
      const raw = await fieldRes.json().catch(() => ({}));
      // Unwrap { success: true, data: {...} } envelope if present
      fieldData = (raw?.data && typeof raw.data === 'object') ? raw.data : raw;
    }
  } catch {
    // Field service unavailable — continue with empty field data
  }

  // Extract lat/lng: prefer query params (from frontend), then try field data (multiple formats)
  const centroid = fieldData?.centroid as Record<string, unknown> | undefined;
  const centroidCoords = centroid?.coordinates as number[] | undefined; // GeoJSON [lng, lat]
  const location = fieldData?.location as Record<string, number> | undefined;

  const lat: number = qLat ? parseFloat(qLat) :
    (fieldData?.centroidLat as number | undefined) ??  // field-management-service format
    centroidCoords?.[1] ??   // GeoJSON format: coordinates = [lng, lat]
    location?.lat ??
    (centroid as Record<string, number> | undefined)?.lat ??
    (fieldData as Record<string, number>)?.lat ??
    0;
  const lng: number = qLng ? parseFloat(qLng) :
    (fieldData?.centroidLng as number | undefined) ??  // field-management-service format
    centroidCoords?.[0] ??   // GeoJSON format: coordinates = [lng, lat]
    location?.lng ?? location?.lon ??
    (centroid as Record<string, number> | undefined)?.lng ??
    (fieldData as Record<string, number>)?.lng ??
    (fieldData as Record<string, number>)?.lon ??
    0;

  // ── Step 2: Parallel fetches for indices, imagery, and weather (all use lat/lng) ─
  const [allIndicesRes, imageryRes, weatherRes, meteoRes] = await Promise.allSettled([
    // 1. All 37 spectral indices (with lat/lng for simulated data)
    fetchWithTimeout(
      `${VEGETATION_URL}/v1/fields/${fieldId}/all-indices?date=${today}&lat=${lat}&lon=${lng}`,
      { headers: commonHeaders },
    ),
    // 2. Satellite imagery thumbnails (True Color, NDVI, NDMI, NDRE)
    fetchWithTimeout(
      `${VEGETATION_URL}/v1/fields/${fieldId}/imagery?date=${today}&lat=${lat}&lon=${lng}`,
      { headers: commonHeaders },
    ),
    // 3. OpenWeather current weather
    (lat !== 0 || lng !== 0) && OPENWEATHER_API_KEY
      ? fetchWithTimeout(
          `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${OPENWEATHER_API_KEY}&units=metric`,
          {},
          10000,
        )
      : Promise.resolve(null),
    // 4. Open-Meteo (maximum agriculture data)
    (lat !== 0 || lng !== 0)
      ? fetchWithTimeout(
          `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}` +
          `&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain` +
          `,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,pressure_msl` +
          `,vapour_pressure_deficit,et0_fao_evapotranspiration` +
          `,soil_temperature_0cm,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm` +
          `,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_moisture_27_to_81cm` +
          `,shortwave_radiation,direct_radiation,diffuse_radiation,sunshine_duration` +
          `,is_day` +
          `&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum` +
          `,et0_fao_evapotranspiration,shortwave_radiation_sum,sunshine_duration` +
          `,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant` +
          `,uv_index_max,precipitation_probability_max,weather_code` +
          `&forecast_days=7&timezone=auto`,
          {},
          15000,
        )
      : Promise.resolve(null),
  ]);

  // Parse indices
  let indicesData: Record<string, unknown> = {};
  if (allIndicesRes.status === 'fulfilled' && allIndicesRes.value.ok) {
    indicesData = await allIndicesRes.value.json().catch(() => ({}));
  }

  // Parse imagery
  let imageryData: Record<string, unknown> = {};
  if (imageryRes.status === 'fulfilled' && imageryRes.value.ok) {
    imageryData = await imageryRes.value.json().catch(() => ({}));
  }

  // Parse weather
  let weather: Record<string, unknown> | null = null;
  if (weatherRes.status === 'fulfilled' && weatherRes.value?.ok) {
    const w = await weatherRes.value.json().catch(() => null);
    if (w) {
      weather = {
        temperature: w.main?.temp,
        feels_like: w.main?.feels_like,
        humidity: w.main?.humidity,
        wind_speed: w.wind?.speed != null ? Math.round(w.wind.speed * 3.6) : null, // m/s → km/h
        precipitation: w.rain?.['1h'] ?? 0,
        cloud_cover: w.clouds?.all,
        description: w.weather?.[0]?.description ?? '',
        pressure: w.main?.pressure,
      };
    }
  }

  // Parse meteo (maximum agriculture data)
  let meteo: Record<string, unknown> | null = null;
  if (meteoRes.status === 'fulfilled' && meteoRes.value?.ok) {
    const m = await meteoRes.value.json().catch(() => null);
    if (m) {
      meteo = {
        // Current conditions
        temperature_2m: m.current?.temperature_2m,
        relative_humidity_2m: m.current?.relative_humidity_2m,
        apparent_temperature: m.current?.apparent_temperature,
        precipitation: m.current?.precipitation,
        wind_speed_10m: m.current?.wind_speed_10m,
        wind_direction_10m: m.current?.wind_direction_10m,
        wind_gusts_10m: m.current?.wind_gusts_10m,
        cloud_cover: m.current?.cloud_cover,
        pressure_msl: m.current?.pressure_msl,
        is_day: m.current?.is_day,
        // Agriculture-specific current
        vapour_pressure_deficit: m.current?.vapour_pressure_deficit,
        et0_fao_evapotranspiration: m.current?.et0_fao_evapotranspiration,
        shortwave_radiation: m.current?.shortwave_radiation,
        direct_radiation: m.current?.direct_radiation,
        diffuse_radiation: m.current?.diffuse_radiation,
        sunshine_duration: m.current?.sunshine_duration,
        // Soil moisture (5 depths)
        soil_moisture: {
          depth_0_1cm: m.current?.soil_moisture_0_to_1cm,
          depth_1_3cm: m.current?.soil_moisture_1_to_3cm,
          depth_3_9cm: m.current?.soil_moisture_3_to_9cm,
          depth_9_27cm: m.current?.soil_moisture_9_to_27cm,
          depth_27_81cm: m.current?.soil_moisture_27_to_81cm,
        },
        // Soil temperature (4 depths)
        soil_temperature: {
          surface: m.current?.soil_temperature_0cm,
          depth_6cm: m.current?.soil_temperature_6cm,
          depth_18cm: m.current?.soil_temperature_18cm,
          depth_54cm: m.current?.soil_temperature_54cm,
        },
        // 7-day daily forecast
        forecast_7day: (m.daily?.time as string[] | undefined)?.map((date: string, i: number) => ({
          date,
          temp_max: m.daily?.temperature_2m_max?.[i],
          temp_min: m.daily?.temperature_2m_min?.[i],
          precipitation_sum: m.daily?.precipitation_sum?.[i],
          rain_sum: m.daily?.rain_sum?.[i],
          et0: m.daily?.et0_fao_evapotranspiration?.[i],
          radiation_sum: m.daily?.shortwave_radiation_sum?.[i],
          sunshine_duration: m.daily?.sunshine_duration?.[i],
          wind_speed_max: m.daily?.wind_speed_10m_max?.[i],
          wind_gusts_max: m.daily?.wind_gusts_10m_max?.[i],
          wind_direction_dominant: m.daily?.wind_direction_10m_dominant?.[i],
          uv_index_max: m.daily?.uv_index_max?.[i],
          precipitation_probability_max: m.daily?.precipitation_probability_max?.[i],
          weather_code: m.daily?.weather_code?.[i],
        })) ?? [],
      };
    }
  }

  // ── Build farm hierarchy ─────────────────────────────────────────────────────
  const farm = (fieldData?.farm ?? fieldData?.Farm) as Record<string, unknown> | undefined;
  const farmHierarchy = {
    governorate: farm?.governorate ?? farm?.region ?? null,
    district: farm?.district ?? null,
    sub_district: farm?.subDistrict ?? farm?.sub_district ?? null,
  };

  // ── Build field info ─────────────────────────────────────────────────────────
  const bbox = (fieldData?.bbox ?? fieldData?.boundingBox) as number[] | undefined;
  const fieldName = (fieldData?.name as string | undefined) ?? fieldId;
  const fieldInfo = {
    id: fieldId,
    name: fieldName,
    name_ar: (fieldData?.nameAr ?? fieldData?.name_ar ?? fieldName) as string | null | undefined,
    lat,
    lng,
    area_ha: (fieldData?.area ?? fieldData?.areaHectares ?? fieldData?.area_ha) as number | null | undefined,
    crop_type: (fieldData?.crop ?? fieldData?.cropType ?? fieldData?.crop_type) as string | null | undefined,
    previous_crop: (fieldData?.previousCrop ?? fieldData?.previous_crop) as string | null | undefined,
    soil_type: (fieldData?.soilType ?? fieldData?.soil_type) as string | null | undefined,
    irrigation_type: (fieldData?.irrigationType ?? fieldData?.irrigation_type) as string | null | undefined,
    seeding_date: (fieldData?.plantingDate ?? fieldData?.seedingDate ?? fieldData?.seeding_date) as string | null | undefined,
    harvest_date: (fieldData?.expectedHarvest ?? fieldData?.harvestDate ?? fieldData?.harvest_date) as string | null | undefined,
    bbox: bbox ?? null,
    farm_hierarchy: farmHierarchy,
  };

  // ── Build indices payload (pass through all 37 indices) ──────────────────────
  const rawIndices = (indicesData?.indices ?? {}) as Record<string, Record<string, number | null>>;
  const nullStats = { value: null, min: null, max: null, std_dev: null, cloud_cover: null };
  const ALL_INDEX_KEYS = [
    // Vegetation Vigor (10)
    'NDVI', 'EVI', 'EVI2', 'GNDVI', 'WDRVI', 'ARVI', 'DVI', 'RVI', 'RDVI', 'NIRv',
    // Red Edge / Chlorophyll (8)
    'NDRE', 'NDRE1', 'NDRE2', 'S2REP', 'IRECI', 'CIre', 'CIgreen', 'MCARI',
    // Soil-Adjusted (4)
    'SAVI', 'OSAVI', 'MSAVI', 'TSAVI',
    // Water / Moisture (6)
    'NDWI', 'NDMI', 'MNDWI', 'MSI', 'LSWI', 'DSWI',
    // Canopy Structure (3)
    'LAI', 'FAPAR', 'SeLI',
    // Pigment / Senescence (3)
    'PSRI', 'SIPI', 'ARI',
    // Soil (2)
    'BSI', 'BI',
    // Phenology (1)
    'NDPI',
  ];
  const indices: Record<string, Record<string, number | null>> = {};
  for (const key of ALL_INDEX_KEYS) {
    indices[key] = rawIndices[key] ?? nullStats;
  }

  // ── Build imagery payload ───────────────────────────────────────────────────
  const imagery = (imageryData?.thumbnails ?? {
    true_color: null,
    ndvi_heatmap: null,
    ndmi_heatmap: null,
    ndre_heatmap: null,
  }) as Record<string, string | null>;

  return NextResponse.json({
    field: fieldInfo,
    indices,
    imagery,
    primary_indice: indice,
    weather,
    meteo,
    index_count: (indicesData as Record<string, unknown>)?.index_count ?? ALL_INDEX_KEYS.length,
    satellite_date: (indicesData as Record<string, unknown>)?.acquisition_date ?? today,
    cloud_cover_pct: (indicesData as Record<string, unknown>)?.cloud_cover_percent ?? null,
    data_source: (indicesData as Record<string, unknown>)?.data_source ?? 'unknown',
    fetched_at: new Date().toISOString(),
  });
}
