# E2E Testing with Playwright

## Overview | نظرة عامة

This directory contains End-to-End (E2E) tests for the SAHOOL web application using Playwright.

هذا المجلد يحتوي على اختبارات E2E لتطبيق SAHOOL باستخدام Playwright.

## Structure | البنية

```
e2e/
├── fixtures/           # Custom test fixtures
│   └── test-fixtures.ts
├── helpers/            # Helper functions
│   ├── auth.helpers.ts      # Authentication helpers
│   └── page.helpers.ts      # Page interaction helpers
├── auth.spec.ts        # Authentication tests
├── navigation.spec.ts  # Navigation tests
├── forms.spec.ts       # Form interaction tests
├── dashboard.spec.ts   # Dashboard tests
├── settings.spec.ts    # Settings page tests
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Setup | الإعداد

### 1. Install Dependencies | تثبيت المتطلبات

```bash
cd apps/web
npm install
```

### 2. Install Playwright Browsers | تثبيت متصفحات Playwright

```bash
npx playwright install
```

### 3. Configure Environment | إعداد البيئة

Copy `.env.example` to `.env` and update the values:

```bash
cp e2e/.env.example e2e/.env
```

Update the following variables:
- `TEST_USER_EMAIL`: Test user email
- `TEST_USER_PASSWORD`: Test user password
- `PLAYWRIGHT_BASE_URL`: Application URL (default: http://localhost:3000)

## Running Tests | تشغيل الاختبارات

### Run all tests | تشغيل جميع الاختبارات

```bash
npm run test:e2e
```

### Run tests in UI mode | تشغيل الاختبارات في وضع UI

```bash
npm run test:e2e:ui
```

### Run tests in headed mode | تشغيل الاختبارات مع المتصفح المرئي

```bash
npm run test:e2e:headed
```

### Debug tests | تصحيح الاختبارات

```bash
npm run test:e2e:debug
```

### Run specific test file | تشغيل ملف اختبار محدد

```bash
npx playwright test e2e/auth.spec.ts
```

### Run tests in a specific browser | تشغيل الاختبارات في متصفح محدد

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### View test report | عرض تقرير الاختبارات

```bash
npm run test:e2e:report
```

## Test Categories | فئات الاختبارات

### 1. Authentication Tests (`auth.spec.ts`)
- Login functionality
- Logout functionality
- Session persistence
- Error handling
- Password reset flow

### 2. Navigation Tests (`navigation.spec.ts`)
- Page navigation
- Browser back/forward buttons
- Active navigation indicators
- Mobile navigation
- 404 handling

### 3. Form Tests (`forms.spec.ts`)
- Field management forms
- Task management forms
- Equipment management forms
- Search and filter functionality
- Form validation
- File uploads (if applicable)

### 4. Dashboard Tests (`dashboard.spec.ts`)
- Dashboard layout
- Statistics widgets
- Recent activity
- Weather widget
- Tasks summary
- Quick actions
- Charts and visualizations
- Responsive design

### 5. Settings Tests (`settings.spec.ts`)
- Profile settings
- Password change
- Notification preferences
- Language settings
- Theme settings
- Privacy settings
- Account management

## Helper Functions | الدوال المساعدة

### Authentication Helpers (`helpers/auth.helpers.ts`)

```typescript
import { login, logout, clearAuth } from './helpers/auth.helpers';

// Login
await login(page, { email: 'test@example.com', password: 'password' });

// Logout
await logout(page);

// Clear authentication
await clearAuth(page);
```

### Page Helpers (`helpers/page.helpers.ts`)

```typescript
import { navigateAndWait, waitForToast, fillFieldByLabel } from './helpers/page.helpers';

// Navigate and wait for page to load
await navigateAndWait(page, '/dashboard');

// Wait for toast message
await waitForToast(page, 'Success');

// Fill form field by label
await fillFieldByLabel(page, 'Email', 'test@example.com');
```

## Custom Fixtures | الإعدادات المخصصة

### Authenticated Page

Use the `authenticatedPage` fixture to automatically log in before tests:

```typescript
test('should access protected page', async ({ page, authenticatedPage }) => {
  // User is already logged in
  await page.goto('/dashboard');
  // Your test code
});
```

## Best Practices | أفضل الممارسات

1. **Use data-testid attributes**: Add `data-testid` to elements for reliable selection
2. **Wait for elements**: Use proper waiting strategies instead of fixed timeouts
3. **Clean up after tests**: Use `beforeEach` and `afterEach` hooks
4. **Independent tests**: Each test should be independent and not rely on others
5. **Mock external services**: Use mocking for external API calls when possible
6. **Page Object Pattern**: Consider using Page Object Pattern for complex pages

## Debugging | التصحيح

### Visual Debugging

```bash
npm run test:e2e:debug
```

### Screenshots on Failure

Screenshots are automatically captured on test failure and saved to `test-results/`.

### Videos

Videos are captured on failure and saved to `test-results/`.

### Trace Viewer

Traces are captured on first retry. View them with:

```bash
npx playwright show-trace test-results/.../trace.zip
```

## CI/CD Integration | التكامل مع CI/CD

The tests are configured to run in CI environments. Set the `CI` environment variable:

```bash
CI=true npm run test:e2e
```

This will:
- Run tests with 2 retries
- Run tests sequentially (workers=1)
- Generate HTML and JSON reports

## Troubleshooting | حل المشاكل

### Tests fail with "timeout" errors

Increase timeout in `playwright.config.ts`:

```typescript
timeout: 60 * 1000, // 60 seconds
```

### Browsers not installed

Run:

```bash
npx playwright install
```

### Authentication fails

Verify test credentials in `.env` file and ensure the test user exists in the database.

### Tests work locally but fail in CI

Ensure all required environment variables are set in CI and the application is running.

## Contributing | المساهمة

When adding new tests:

1. Follow existing test structure
2. Use descriptive test names
3. Add comments in both Arabic and English
4. Update this README if adding new test categories
5. Ensure tests pass before committing

## Resources | الموارد

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
