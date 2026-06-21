/**
 * Field AI Analysis Proxy
 * Proxies POST to field-intelligence POST /api/v1/analyze/field/comprehensive
 * Runs AgriGuard scoring + CropSeek-LLM advisory + NLLB Arabic translation.
 * Results are Redis-cached for 6 hours on the backend.
 */

import { NextRequest, NextResponse } from 'next/server';

const FIELD_INTELLIGENCE_URL =
  process.env.FIELD_INTELLIGENCE_URL || 'http://field-intelligence:8120';

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  try {
    // eslint-disable-next-line no-restricted-syntax
    const res = await fetch(`${FIELD_INTELLIGENCE_URL}/api/v1/analyze/field/comprehensive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(180000), // comprehensive analysis: 2 parallel LLM calls + buffer
    });

    const data = await res.json().catch(() => ({ error: 'Upstream parse error' }));
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Upstream error';
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
