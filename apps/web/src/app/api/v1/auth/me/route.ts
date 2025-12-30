import { NextRequest, NextResponse } from 'next/server';

/**
 * Mock Get Current User API Route
 * Returns the current authenticated user's information
 */

// Mock user data (same as in login route)
const MOCK_USERS: Record<string, {
  id: string;
  email: string;
  name: string;
  name_ar: string;
  role: string;
  tenantId: string;
}> = {
  'user-001': {
    id: 'user-001',
    email: 'test@sahool.com',
    name: 'Test User',
    name_ar: 'مستخدم اختبار',
    role: 'admin',
    tenantId: 'tenant-001',
  },
  'user-002': {
    id: 'user-002',
    email: 'farmer@sahool.com',
    name: 'Ahmed Farmer',
    name_ar: 'أحمد المزارع',
    role: 'farmer',
    tenantId: 'tenant-002',
  },
  'user-e2e-001': {
    id: 'user-e2e-001',
    email: 'test@example.com',
    name: 'E2E Test User',
    name_ar: 'مستخدم اختبار E2E',
    role: 'admin',
    tenantId: 'tenant-e2e',
  },
  'user-e2e-002': {
    id: 'user-e2e-002',
    email: 'user@test.com',
    name: 'Test User',
    name_ar: 'مستخدم اختبار',
    role: 'user',
    tenantId: 'tenant-e2e',
  },
};

function extractUserIdFromToken(token: string): string | null {
  try {
    const parts = token.replace('Bearer ', '').split('.');
    if (parts.length !== 3) return null;

    const payload = JSON.parse(Buffer.from(parts[1] ?? '', 'base64').toString());
    return payload.sub || null;
  } catch {
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization');

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        {
          success: false,
          error: 'Unauthorized - No token provided',
          error_ar: 'غير مصرح - لم يتم توفير رمز',
        },
        { status: 401 }
      );
    }

    const userId = extractUserIdFromToken(authHeader);

    if (!userId) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid token',
          error_ar: 'رمز غير صالح',
        },
        { status: 401 }
      );
    }

    const user = MOCK_USERS[userId];

    if (!user) {
      return NextResponse.json(
        {
          success: false,
          error: 'User not found',
          error_ar: 'المستخدم غير موجود',
        },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: user,
    });
  } catch (error) {
    console.error('Get user error:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Internal server error',
        error_ar: 'خطأ في الخادم',
      },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
