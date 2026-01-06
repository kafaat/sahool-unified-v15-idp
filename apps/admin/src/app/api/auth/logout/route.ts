/**
 * Server-side logout API route
 * Clears httpOnly cookies
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST() {
  try {
    const cookieStore = await cookies();

    // Clear all auth-related cookies
    cookieStore.delete('sahool_admin_token');
    cookieStore.delete('sahool_admin_refresh_token');
    cookieStore.delete('sahool_admin_last_activity');

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
