/**
 * Fields API Proxy - /api/v1/fields/[fieldId]
 *
 * GET    /api/v1/fields/:id  – get field by id
 * PUT    /api/v1/fields/:id  – update field
 * DELETE /api/v1/fields/:id  – delete field
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';

const FIELD_SERVICE_URL =
  process.env.FIELD_SERVICE_URL ||
  process.env.FIELD_MANAGEMENT_SERVICE_URL ||
  'http://localhost:3000';

async function getAuthToken(): Promise<string | null> {
  const jar = await cookies();
  return jar.get('access_token')?.value ?? null;
}

function buildHeaders(token: string | null, body?: boolean): Record<string, string> {
  const h: Record<string, string> = { Accept: 'application/json' };
  if (body) h['Content-Type'] = 'application/json';
  if (token) h['Authorization'] = `Bearer ${token}`;
  return h;
}

function serviceError(message: string, status = 503): NextResponse {
  return NextResponse.json({ error: message, message }, { status });
}

type Params = { params: Promise<{ fieldId: string }> };

// ─── GET /api/v1/fields/:id ───────────────────────────────────────────────────

export async function GET(_req: NextRequest, { params }: Params): Promise<NextResponse> {
  const { fieldId } = await params;
  try {
    const token = await getAuthToken();
    // eslint-disable-next-line no-restricted-syntax
    const res = await fetch(`${FIELD_SERVICE_URL}/api/v1/fields/${fieldId}`, {
      method: 'GET',
      headers: buildHeaders(token),
      cache: 'no-store',
    });
    const body = await res.text();
    return new NextResponse(body, {
      status: res.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Unknown error';
    logger.error('Fields proxy GET/:id failed:', msg);
    return serviceError(`Field service unavailable: ${msg}`);
  }
}

// ─── PUT /api/v1/fields/:id ───────────────────────────────────────────────────

export async function PUT(req: NextRequest, { params }: Params): Promise<NextResponse> {
  const { fieldId } = await params;
  try {
    const token = await getAuthToken();
    const body = await req.text();
    // eslint-disable-next-line no-restricted-syntax
    const res = await fetch(`${FIELD_SERVICE_URL}/api/v1/fields/${fieldId}`, {
      method: 'PUT',
      headers: buildHeaders(token, true),
      body,
    });
    const responseBody = await res.text();
    return new NextResponse(responseBody, {
      status: res.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Unknown error';
    logger.error('Fields proxy PUT/:id failed:', msg);
    return serviceError(`Field service unavailable: ${msg}`);
  }
}

// ─── DELETE /api/v1/fields/:id ───────────────────────────────────────────────

export async function DELETE(_req: NextRequest, { params }: Params): Promise<NextResponse> {
  const { fieldId } = await params;
  try {
    const token = await getAuthToken();
    // eslint-disable-next-line no-restricted-syntax
    const res = await fetch(`${FIELD_SERVICE_URL}/api/v1/fields/${fieldId}`, {
      method: 'DELETE',
      headers: buildHeaders(token),
    });
    if (res.status === 204) return new NextResponse(null, { status: 204 });
    const responseBody = await res.text();
    return new NextResponse(responseBody, {
      status: res.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Unknown error';
    logger.error('Fields proxy DELETE/:id failed:', msg);
    return serviceError(`Field service unavailable: ${msg}`);
  }
}
