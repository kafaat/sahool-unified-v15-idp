import { NextRequest, NextResponse } from 'next/server';

/**
 * Mock Login API Route
 * This provides a mock authentication endpoint for E2E testing
 * In production, this would be handled by the actual auth service
 */

// Mock user data for testing
const MOCK_USERS = [
  {
    id: 'user-001',
    email: 'test@sahool.com',
    password: 'Test@123456',
    name: 'Test User',
    name_ar: 'مستخدم اختبار',
    role: 'admin',
    tenantId: 'tenant-001',
  },
  {
    id: 'user-002',
    email: 'farmer@sahool.com',
    password: 'Farmer@123',
    name: 'Ahmed Farmer',
    name_ar: 'أحمد المزارع',
    role: 'farmer',
    tenantId: 'tenant-002',
  },
  // E2E test users
  {
    id: 'user-e2e-001',
    email: 'test@example.com',
    password: 'Test@123456',
    name: 'E2E Test User',
    name_ar: 'مستخدم اختبار E2E',
    role: 'admin',
    tenantId: 'tenant-e2e',
  },
  {
    id: 'user-e2e-002',
    email: 'user@test.com',
    password: 'Password123!',
    name: 'Test User',
    name_ar: 'مستخدم اختبار',
    role: 'user',
    tenantId: 'tenant-e2e',
  },
];

// Generate a mock JWT token
function generateMockToken(userId: string): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64');
  const payload = Buffer.from(JSON.stringify({
    sub: userId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 86400, // 24 hours
  })).toString('base64');
  const signature = Buffer.from('mock-signature').toString('base64');
  return `${header}.${payload}.${signature}`;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // Validate input
    if (!email || !password) {
      return NextResponse.json(
        {
          success: false,
          error: 'Email and password are required',
          error_ar: 'البريد الإلكتروني وكلمة المرور مطلوبان',
        },
        { status: 400 }
      );
    }

    // Find user
    const user = MOCK_USERS.find(
      (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password
    );

    if (!user) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid email or password',
          error_ar: 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
        },
        { status: 401 }
      );
    }

    // Generate token and return user data
    const token = generateMockToken(user.id);

    return NextResponse.json({
      success: true,
      data: {
        access_token: token,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          name_ar: user.name_ar,
          role: user.role,
          tenantId: user.tenantId,
        },
      },
    });
  } catch (error) {
    console.error('Login error:', error);
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
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
