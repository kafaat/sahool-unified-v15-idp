/**
 * Field AI Data Proxy
 * Proxies requests to field-management-service GET /api/v1/fields/:id/ai-data
 * Returns CDSE index stats + OpenWeather + OpenMeteo for a field.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const FIELD_SERVICE_URL =
  process.env.FIELD_SERVICE_URL || 'http://field-management-service:3000';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const SAFE_INDICE = /^[A-Z0-9_]{2,20}$/;

export async function GET(req: NextRequest): Promise<NextResponse> {
  const { searchParams } = req.nextUrl;
  const fieldId = searchParams.get('fieldId');
  const indice = searchParams.get('indice') ?? 'NDVI';

  if (!fieldId || !UUID_RE.test(fieldId)) {
    return NextResponse.json({ error: 'Invalid fieldId' }, { status: 400 });
  }
  if (!SAFE_INDICE.test(indice.toUpperCase())) {
    return NextResponse.json({ error: 'Invalid indice' }, { status: 400 });
  }

  // Forward auth cookie as Authorization header
  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;

  // eslint-disable-next-line no-restricted-syntax
  const upstream = new URL(`${FIELD_SERVICE_URL}/api/v1/fields/${fieldId}/ai-data`);
  upstream.searchParams.set('indice', indice.toUpperCase());

  try {
    const res = await fetch(upstream.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      signal: AbortSignal.timeout(45000),
    });

    const body = await res.json().catch(() => ({ error: 'Upstream parse error' }));

    return NextResponse.json(body, { status: res.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Upstream error';
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
