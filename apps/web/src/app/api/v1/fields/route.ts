/**
 * Fields API Proxy - /api/v1/fields
 *
 * Server-side proxy that forwards field requests directly to the
 * field-management-service (port 3000), bypassing Kong.
 *
 * This resolves the "name resolution failed" error that occurs when
 * Kong cannot resolve the upstream Docker service name in local dev.
 *
 * GET  /api/v1/fields  – list fields
 * POST /api/v1/fields  – create field
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';

const FIELD_SERVICE_URL =
  process.env.FIELD_SERVICE_URL ||
  process.env.FIELD_MANAGEMENT_SERVICE_URL ||
  'http://localhost:3000';

const UPSTREAM = `${FIELD_SERVICE_URL}/api/v1/fields`;

// ─── helpers ─────────────────────────────────────────────────────────────────

async function getAuthToken(): Promise<string | null> {
  const jar = await cookies();
  return jar.get('access_token')?.value ?? null;
}

function buildHeaders(token: string | null, body?: boolean): Record<string, string> {
  const h: Record<string, string> = {
    Accept: 'application/json',
  };
  if (body) h['Content-Type'] = 'application/json';
  if (token) h['Authorization'] = `Bearer ${token}`;
  return h;
}

function serviceError(message: string, status = 503): NextResponse {
  return NextResponse.json({ error: message, message }, { status });
}

// ─── GET /api/v1/fields ───────────────────────────────────────────────────────

export async function GET(req: NextRequest): Promise<NextResponse> {
  try {
    const token = await getAuthToken();
    const search = req.nextUrl.search; // forward query params as-is

    const res = await fetch(`${UPSTREAM}${search}`, {
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
    logger.error('Fields proxy GET failed:', msg);
    return serviceError(`Field service unavailable: ${msg}`);
  }
}

// ─── POST /api/v1/fields ──────────────────────────────────────────────────────

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const token = await getAuthToken();
    const body = await req.text();

    const res = await fetch(UPSTREAM, {
      method: 'POST',
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
    logger.error('Fields proxy POST failed:', msg);
    return serviceError(`Field service unavailable: ${msg}`);
  }
}
