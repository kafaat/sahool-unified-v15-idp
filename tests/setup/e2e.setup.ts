/**
 * E2E Test Setup
 * إعداد الاختبارات الشاملة
 */
import { execSync } from 'child_process';

// Global setup
beforeAll(async () => {
  console.log('🧪 Starting E2E test setup...');

  // Ensure test database is ready
  try {
    // Check if DATABASE_URL is set for test environment
    if (!process.env.DATABASE_URL) {
      console.log('⚠️ DATABASE_URL not set, using default test database');
      process.env.DATABASE_URL =
        'postgresql://postgres:postgres@localhost:5432/sahool_test';
    }

    // Run migrations
    console.log('📦 Running database migrations...');
    execSync('npx prisma migrate deploy', {
      cwd: process.cwd() + '/services/research_core',
      stdio: 'pipe',
      env: { ...process.env },
    });

    console.log('✅ E2E setup complete');
  } catch (error) {
    console.error('❌ E2E setup failed:', error);
    // Don't throw - let individual tests handle database availability
  }
});

// Global teardown
afterAll(async () => {
  console.log('🧹 E2E test cleanup...');

  // Cleanup test data if needed
  // This is handled by individual test files

  console.log('✅ E2E cleanup complete');
});

// Increase default timeout for E2E tests
jest.setTimeout(30000);

// Custom matchers for API responses
expect.extend({
  toBeValidApiResponse(received) {
    const pass =
      received &&
      typeof received === 'object' &&
      (received.data !== undefined || received.id !== undefined);

    return {
      message: () =>
        pass
          ? `expected ${JSON.stringify(received)} not to be a valid API response`
          : `expected ${JSON.stringify(received)} to be a valid API response`,
      pass,
    };
  },

  toHavePagination(received) {
    const pass =
      received &&
      received.meta &&
      typeof received.meta.total === 'number' &&
      typeof received.meta.page === 'number' &&
      typeof received.meta.limit === 'number';

    return {
      message: () =>
        pass
          ? `expected response not to have pagination`
          : `expected response to have pagination with total, page, and limit`,
      pass,
    };
  },

  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;

    return {
      message: () =>
        pass
          ? `expected ${received} not to be within range ${floor} - ${ceiling}`
          : `expected ${received} to be within range ${floor} - ${ceiling}`,
      pass,
    };
  },
});

// Declare custom matchers
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidApiResponse(): R;
      toHavePagination(): R;
      toBeWithinRange(floor: number, ceiling: number): R;
    }
  }
}
