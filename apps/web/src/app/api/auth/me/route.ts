/**
 * Current User API Route
 * نقطة نهاية بيانات المستخدم الحالي
 *
 * Reads the httpOnly access_token cookie and decodes the JWT payload
 * to return user identity without an extra round-trip to the backend.
 * The middleware has already validated the token signature, so we only
 * need to decode (not verify) the payload here.
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET() {
  try {
    const cookieStore = await cookies();
    const tokenCookie = cookieStore.get('access_token');

    if (!tokenCookie?.value) {
      return NextResponse.json({ success: false, error: 'No session' }, { status: 401 });
    }

    // Decode JWT payload (base64url) — no signature verification needed here
    // because Next.js middleware already validates the signature on every request.
    const parts = tokenCookie.value.split('.');
    if (parts.length !== 3 || !parts[1]) {
      return NextResponse.json({ success: false, error: 'Invalid token format' }, { status: 401 });
    }

    const payloadB64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const payloadJson = Buffer.from(payloadB64, 'base64').toString('utf-8');
    const payload = JSON.parse(payloadJson);

    // Check expiry
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
      return NextResponse.json({ success: false, error: 'Token expired' }, { status: 401 });
    }

    return NextResponse.json({
      success: true,
      data: {
        id: payload.sub,
        email: payload.email,
        name: payload.name || payload.email,
        role: Array.isArray(payload.roles) ? payload.roles[0] : payload.role,
        tenant_id: payload.tid,
      },
    });
  } catch {
    return NextResponse.json({ success: false, error: 'Failed to decode session' }, { status: 500 });
  }
}
