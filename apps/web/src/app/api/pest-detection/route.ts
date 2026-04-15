/**
 * Pest Detection API Proxy Routes
 * وكيل واجهة برمجة تطبيقات كشف الآفات
 *
 * Proxies pest detection requests to pest-detection-service.
 * All endpoints require authentication via httpOnly access_token cookie.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { PEST_ENDPOINTS } from '@sahool/shared-types/contracts';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const PEST_DETECTION_URL =
  process.env.PEST_DETECTION_URL || 'http://pest-detection-service:8125';

const REQUEST_TIMEOUT_MS = 15_000;

/** Validate IDs to prevent path traversal */
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

/** Validate free-form filter enum values (region, season, severity) */
const SAFE_ENUM_PATTERN = /^[a-zA-Z0-9_-]{1,64}$/;

/**
 * Maximum raw JSON body size for POST requests (bytes).
 * Base64 images can be large, so we allow up to 10 MB raw → ~7.5 MB decoded.
 */
const MAX_JSON_BODY_BYTES = 10 * 1024 * 1024;

/** Maximum allowed base64 image payload length (characters). */
const MAX_BASE64_IMAGE_LENGTH = 10 * 1024 * 1024; // ~7.5 MB decoded

/**
 * Validate an outbound image_url to block SSRF against internal targets.
 * Only https URLs to non-loopback/non-private addresses are permitted.
 */
function isSafeImageUrl(raw: unknown): raw is string {
  if (typeof raw !== 'string' || raw.length === 0 || raw.length > 2048) return false;
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    return false;
  }
  if (url.protocol !== 'https:' && url.protocol !== 'http:') return false;
  // Reject userinfo (no credentials in URLs)
  if (url.username || url.password) return false;
  const host = url.hostname.toLowerCase();
  // Block loopback, private, link-local, and metadata endpoints
  if (
    host === 'localhost' ||
    host === '0.0.0.0' ||
    host === '::1' ||
    host.endsWith('.localhost') ||
    host.endsWith('.local') ||
    host.endsWith('.internal') ||
    /^127\./.test(host) ||
    /^10\./.test(host) ||
    /^192\.168\./.test(host) ||
    /^172\.(1[6-9]|2\d|3[01])\./.test(host) ||
    /^169\.254\./.test(host) || // AWS/GCP metadata link-local
    /^fc00:/.test(host) ||
    /^fe80:/.test(host)
  ) {
    return false;
  }
  return true;
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Extract and validate the access token from httpOnly cookie.
 * Returns the token string or null if absent/invalid.
 */
async function getAccessToken(): Promise<string | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;
  if (!token || token.length < 20 || token.length > 2048) {
    return null;
  }
  return token;
}

/**
 * Extract tenant ID from the access token JWT payload (unverified decode).
 * The backend performs full verification; this is for forwarding only.
 */
function extractTenantId(token: string): string | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) return null;
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf-8'));
    return payload.tid || payload.tenant_id || null;
  } catch {
    return null;
  }
}

/**
 * Build standard authorization headers for upstream requests.
 */
function buildHeaders(token: string, tenantId: string | null): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
  if (tenantId) {
    headers['X-Tenant-ID'] = tenantId;
  }
  return headers;
}

// ═══════════════════════════════════════════════════════════════════════════
// GET /api/pest-detection
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/pest-detection?action=list&region=xxx
 * GET /api/pest-detection?action=by-crop&cropType=wheat
 */
export async function GET(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse params ---
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    let path: string;

    switch (action) {
      case 'list': {
        const params = new URLSearchParams();
        const region = searchParams.get('region');
        const season = searchParams.get('season');
        const severity = searchParams.get('severity');
        if (region) {
          if (!SAFE_ENUM_PATTERN.test(region)) {
            return NextResponse.json({ error: 'Invalid region format' }, { status: 400 });
          }
          params.set('region', region);
        }
        if (season) {
          if (!SAFE_ENUM_PATTERN.test(season)) {
            return NextResponse.json({ error: 'Invalid season format' }, { status: 400 });
          }
          params.set('season', season);
        }
        if (severity) {
          if (!SAFE_ENUM_PATTERN.test(severity)) {
            return NextResponse.json({ error: 'Invalid severity format' }, { status: 400 });
          }
          params.set('severity', severity);
        }
        const qs = params.toString();
        path = `${PEST_ENDPOINTS.LIST}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'by-crop': {
        const cropType = searchParams.get('cropType');
        if (!cropType || !SAFE_ID_PATTERN.test(cropType)) {
          return NextResponse.json(
            { error: 'Valid cropType is required' },
            { status: 400 }
          );
        }
        const params = new URLSearchParams();
        const region = searchParams.get('region');
        if (region) {
          if (!SAFE_ENUM_PATTERN.test(region)) {
            return NextResponse.json({ error: 'Invalid region format' }, { status: 400 });
          }
          params.set('region', region);
        }
        const qs = params.toString();
        path = `${PEST_ENDPOINTS.BY_CROP.replace('{cropType}', encodeURIComponent(cropType))}${qs ? `?${qs}` : ''}`;
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: list, by-crop' },
          { status: 400 }
        );
    }

    const response = await fetch(`${PEST_DETECTION_URL}${path}`, {
      method: 'GET',
      headers: buildHeaders(token, tenantId),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Pest detection service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Pest detection service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Pest detection GET proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch pest detection data' },
      { status: 502 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST /api/pest-detection
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/pest-detection
 * Body: { action: 'identify' | 'treatment', ... }
 *
 * action=identify   -> Identify pest from image (base64)
 * action=treatment  -> Recommend treatment for a detected pest
 */
export async function POST(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    const tenantId = extractTenantId(token);

    // --- Body size guard (defense against huge base64 payloads) ---
    const contentLengthHeader = request.headers.get('content-length');
    if (contentLengthHeader) {
      const contentLength = Number(contentLengthHeader);
      if (Number.isFinite(contentLength) && contentLength > MAX_JSON_BODY_BYTES) {
        return NextResponse.json(
          { error: `Request body too large (max ${MAX_JSON_BODY_BYTES} bytes)` },
          { status: 413 }
        );
      }
    }

    // --- Parse body ---
    let body: Record<string, unknown>;
    try {
      body = (await request.json()) as Record<string, unknown>;
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }
    if (!body || typeof body !== 'object') {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }
    const { action } = body as { action?: unknown };

    if (!action || typeof action !== 'string') {
      return NextResponse.json({ error: 'action is required' }, { status: 400 });
    }

    let path: string;
    let payload: Record<string, unknown>;

    switch (action) {
      case 'identify': {
        const { fieldId, image, image_url, crop_type, confidence_threshold } =
          body as {
            fieldId?: unknown;
            image?: unknown;
            image_url?: unknown;
            crop_type?: unknown;
            confidence_threshold?: unknown;
          };

        if (fieldId !== undefined && (typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId))) {
          return NextResponse.json({ error: 'Invalid fieldId format' }, { status: 400 });
        }

        if (image == null && image_url == null) {
          return NextResponse.json(
            { error: 'Either image (base64) or image_url is required' },
            { status: 400 }
          );
        }

        if (image !== undefined) {
          if (typeof image !== 'string') {
            return NextResponse.json({ error: 'image must be a base64 string' }, { status: 400 });
          }
          if (image.length > MAX_BASE64_IMAGE_LENGTH) {
            return NextResponse.json(
              { error: `image too large (max ${MAX_BASE64_IMAGE_LENGTH} chars)` },
              { status: 413 }
            );
          }
          // Sanity-check base64 (allow data URLs and raw base64)
          const base64Body = image.startsWith('data:')
            ? image.slice(image.indexOf(',') + 1)
            : image;
          if (!/^[A-Za-z0-9+/=\s]*$/.test(base64Body)) {
            return NextResponse.json({ error: 'image is not valid base64' }, { status: 400 });
          }
        }

        if (image_url !== undefined && !isSafeImageUrl(image_url)) {
          return NextResponse.json(
            { error: 'image_url must be a public https/http URL' },
            { status: 400 }
          );
        }

        if (crop_type !== undefined && (typeof crop_type !== 'string' || !SAFE_ID_PATTERN.test(crop_type))) {
          return NextResponse.json({ error: 'Invalid crop_type format' }, { status: 400 });
        }

        if (
          confidence_threshold !== undefined &&
          (typeof confidence_threshold !== 'number' ||
            !Number.isFinite(confidence_threshold) ||
            confidence_threshold < 0 ||
            confidence_threshold > 1)
        ) {
          return NextResponse.json(
            { error: 'confidence_threshold must be a number between 0 and 1' },
            { status: 400 }
          );
        }

        path = PEST_ENDPOINTS.IDENTIFY;
        payload = {
          ...(fieldId != null && { field_id: fieldId }),
          ...(image != null && { image }),
          ...(image_url != null && { image_url }),
          ...(crop_type != null && { crop_type }),
          ...(confidence_threshold != null && { confidence_threshold }),
        };
        break;
      }
      case 'treatment': {
        const { pestId, fieldId, crop_type: cropType, severity: sev } = body as {
          pestId?: unknown;
          fieldId?: unknown;
          crop_type?: unknown;
          severity?: unknown;
        };

        if (!pestId || typeof pestId !== 'string' || !SAFE_ID_PATTERN.test(pestId)) {
          return NextResponse.json({ error: 'Valid pestId is required' }, { status: 400 });
        }

        if (fieldId !== undefined && (typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId))) {
          return NextResponse.json({ error: 'Invalid fieldId format' }, { status: 400 });
        }

        if (cropType !== undefined && (typeof cropType !== 'string' || !SAFE_ID_PATTERN.test(cropType))) {
          return NextResponse.json({ error: 'Invalid crop_type format' }, { status: 400 });
        }

        if (sev !== undefined && (typeof sev !== 'string' || !SAFE_ENUM_PATTERN.test(sev))) {
          return NextResponse.json({ error: 'Invalid severity format' }, { status: 400 });
        }

        // Contract template: PEST_ENDPOINTS.TREATMENT_RECOMMEND.
        // pest-detection-service exposes POST /api/v1/treatments/recommend —
        // it does NOT expose /api/v1/pests/treatment.
        path = PEST_ENDPOINTS.TREATMENT_RECOMMEND;
        payload = {
          pest_id: pestId,
          ...(fieldId != null && { field_id: fieldId }),
          ...(cropType != null && { crop_type: cropType }),
          ...(sev != null && { severity: sev }),
        };
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: identify, treatment' },
          { status: 400 }
        );
    }

    const response = await fetch(`${PEST_DETECTION_URL}${path}`, {
      method: 'POST',
      headers: buildHeaders(token, tenantId),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Pest detection service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Pest detection service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Pest detection POST proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process pest detection request' },
      { status: 502 }
    );
  }
}
