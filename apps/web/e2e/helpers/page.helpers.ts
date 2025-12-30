import { Page, expect } from '@playwright/test';

/**
 * Page Helper Functions
 * دوال مساعدة للصفحات
 */

/**
 * Default timeout constants aligned with Playwright config
 * ثوابت المهلة الزمنية الافتراضية متوافقة مع إعدادات Playwright
 */
export const DEFAULT_TIMEOUT = 10000; // 10 seconds for actions
export const NAVIGATION_TIMEOUT = 20000; // 20 seconds for navigation
export const ELEMENT_TIMEOUT = 5000; // 5 seconds for element visibility

/**
 * Retry configuration
 * إعداد إعادة المحاولة
 */
export interface RetryOptions {
  maxRetries?: number;
  retryDelay?: number;
}

/**
 * Wait for page to be fully loaded
 * الانتظار حتى يتم تحميل الصفحة بالكامل
 */
export async function waitForPageLoad(
  page: Page,
  timeout: number = NAVIGATION_TIMEOUT
): Promise<void> {
  try {
    // Wait for DOM content to be loaded first
    await page.waitForLoadState('domcontentloaded', { timeout });

    // Then wait for network to be idle
    await page.waitForLoadState('networkidle', { timeout });
  } catch (error) {
    const currentUrl = page.url();
    throw new Error(
      `Page failed to load within ${timeout}ms. Current URL: ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Navigate and wait for page
 * التنقل والانتظار للصفحة
 */
export async function navigateAndWait(
  page: Page,
  url: string,
  timeout: number = NAVIGATION_TIMEOUT
): Promise<void> {
  try {
    await page.goto(url, { timeout, waitUntil: 'domcontentloaded' });
    await waitForPageLoad(page, timeout);
  } catch (error) {
    const currentUrl = page.url();
    throw new Error(
      `Failed to navigate to ${url}. Current URL: ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Check if element is visible on page
 * التحقق من ظهور عنصر في الصفحة
 */
export async function isElementVisible(
  page: Page,
  selector: string,
  timeout: number = ELEMENT_TIMEOUT
): Promise<boolean> {
  try {
    const element = page.locator(selector);
    return await element.isVisible({ timeout });
  } catch (error) {
    // Element not visible or timeout - this is expected behavior
    return false;
  }
}

/**
 * Wait for element to be visible with better error handling
 * الانتظار حتى يظهر العنصر مع معالجة أفضل للأخطاء
 */
export async function waitForElement(
  page: Page,
  selector: string,
  timeout: number = DEFAULT_TIMEOUT
): Promise<void> {
  try {
    await page.locator(selector).waitFor({ state: 'visible', timeout });
  } catch (error) {
    const currentUrl = page.url();
    throw new Error(
      `Element "${selector}" not found or not visible within ${timeout}ms on ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Wait for toast/notification message
 * الانتظار لرسالة التنبيه
 */
export async function waitForToast(
  page: Page,
  expectedText?: string,
  timeout: number = ELEMENT_TIMEOUT
): Promise<boolean> {
  const toastSelector = '[role="alert"], [data-testid="toast"], .toast, [class*="toast"]';

  try {
    await page.waitForSelector(toastSelector, { timeout, state: 'visible' });

    if (expectedText) {
      const toast = page.locator(toastSelector);
      await expect(toast).toContainText(expectedText, { timeout });
    }

    return true;
  } catch (error) {
    // Toast not found - log for debugging but don't throw
    console.warn(`Toast notification not found within ${timeout}ms${expectedText ? ` with text: "${expectedText}"` : ''}`);
    return false;
  }
}

/**
 * Fill form field with label
 * ملء حقل نموذج باستخدام التسمية
 */
export async function fillFieldByLabel(
  page: Page,
  label: string,
  value: string,
  timeout: number = DEFAULT_TIMEOUT
): Promise<void> {
  try {
    // Try to find input by label
    const labelElement = page.locator(`label:has-text("${label}")`).first();
    const inputId = await labelElement.getAttribute('for', { timeout: ELEMENT_TIMEOUT });

    if (inputId) {
      await page.fill(`#${inputId}`, value, { timeout });
    } else {
      // Try to find input within label or nearby
      const inputSelector = `label:has-text("${label}") ~ input, label:has-text("${label}") input`;
      await page.locator(inputSelector).first().fill(value, { timeout });
    }
  } catch (error) {
    const currentUrl = page.url();
    throw new Error(
      `Failed to fill field with label "${label}" on ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Click button by text (Arabic or English)
 * النقر على زر بالنص (عربي أو إنجليزي)
 */
export async function clickButtonByText(
  page: Page,
  textsOrFirstText: string | string[],
  timeoutOrSecondText?: number | string,
  ...restTexts: (string | number)[]
): Promise<void> {
  // Support both signatures:
  // 1. New: clickButtonByText(page, ['text1', 'text2'], timeout?)
  // 2. Old: clickButtonByText(page, 'text1', 'text2', ...)
  let texts: string[];
  let timeout: number = DEFAULT_TIMEOUT;

  if (Array.isArray(textsOrFirstText)) {
    // New signature: array of texts
    texts = textsOrFirstText;
    if (typeof timeoutOrSecondText === 'number') {
      timeout = timeoutOrSecondText;
    }
  } else {
    // Old variadic signature: individual text parameters
    texts = [textsOrFirstText];
    if (typeof timeoutOrSecondText === 'string') {
      texts.push(timeoutOrSecondText);
    } else if (typeof timeoutOrSecondText === 'number') {
      timeout = timeoutOrSecondText;
    }
    // Add remaining texts
    for (const item of restTexts) {
      if (typeof item === 'string') {
        texts.push(item);
      } else if (typeof item === 'number' && texts.length === restTexts.indexOf(item) + 1) {
        // Last parameter is timeout
        timeout = item;
      }
    }
  }

  const errors: string[] = [];

  for (const text of texts) {
    try {
      const button = page.locator(`button:has-text("${text}")`).first();
      // Check if button is visible with a shorter timeout per attempt
      const isVisible = await button.isVisible({ timeout: timeout / texts.length });

      if (isVisible) {
        await button.click({ timeout: DEFAULT_TIMEOUT });
        return;
      }
    } catch (error) {
      errors.push(`"${text}": ${error instanceof Error ? error.message : 'Not found'}`);
    }
  }

  const currentUrl = page.url();
  throw new Error(
    `Could not find visible button with any of these texts on ${currentUrl}: ${texts.join(', ')}. Errors: ${errors.join('; ')}`
  );
}

/**
 * Take screenshot with timestamp
 * أخذ لقطة شاشة مع الطابع الزمني
 */
export async function takeTimestampedScreenshot(
  page: Page,
  name: string
): Promise<string> {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const path = `test-results/screenshots/${name}-${timestamp}.png`;
    await page.screenshot({
      path,
      fullPage: true,
      timeout: DEFAULT_TIMEOUT
    });
    return path;
  } catch (error) {
    console.error(`Failed to take screenshot "${name}":`, error);
    throw new Error(
      `Screenshot failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Wait for API response
 * الانتظار لاستجابة API
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = DEFAULT_TIMEOUT
) {
  try {
    return await page.waitForResponse(
      (response) => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout }
    );
  } catch (error) {
    const pattern = typeof urlPattern === 'string' ? urlPattern : urlPattern.toString();
    throw new Error(
      `API response matching "${pattern}" not received within ${timeout}ms. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Check if page has error message
 * التحقق من وجود رسالة خطأ في الصفحة
 */
export async function hasErrorMessage(page: Page): Promise<boolean> {
  const errorSelectors = [
    '[role="alert"]',
    '.error',
    '[class*="error"]',
    'text=/error|خطأ|فشل/i'
  ];

  for (const selector of errorSelectors) {
    if (await isElementVisible(page, selector)) {
      return true;
    }
  }

  return false;
}

/**
 * Scroll element into view
 * التمرير للعنصر لإظهاره
 */
export async function scrollIntoView(page: Page, selector: string) {
  await page.locator(selector).scrollIntoViewIfNeeded();
}

/**
 * Get table row count
 * الحصول على عدد صفوف الجدول
 */
export async function getTableRowCount(page: Page, tableSelector = 'table'): Promise<number> {
  const rows = await page.locator(`${tableSelector} tbody tr`).count();
  return rows;
}

/**
 * Select dropdown option
 * اختيار خيار من القائمة المنسدلة
 */
export async function selectDropdownOption(
  page: Page,
  selector: string,
  optionText: string,
  timeout: number = DEFAULT_TIMEOUT
): Promise<void> {
  try {
    // Click to open dropdown
    await page.click(selector, { timeout });

    // Wait for dropdown options to appear
    const optionSelector = `[role="option"]:has-text("${optionText}"), option:has-text("${optionText}")`;
    await page.waitForSelector(optionSelector, { state: 'visible', timeout: ELEMENT_TIMEOUT });

    // Click the option
    await page.click(optionSelector, { timeout });
  } catch (error) {
    const currentUrl = page.url();
    throw new Error(
      `Failed to select dropdown option "${optionText}" from "${selector}" on ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Wait for navigation to complete
 * الانتظار حتى يكتمل التنقل
 */
export async function waitForNavigation(
  page: Page,
  expectedUrl?: string | RegExp,
  timeout: number = NAVIGATION_TIMEOUT
): Promise<void> {
  try {
    if (expectedUrl) {
      await page.waitForURL(expectedUrl, { timeout });
    } else {
      await page.waitForLoadState('networkidle', { timeout });
    }
  } catch (error) {
    const currentUrl = page.url();
    const expected = expectedUrl
      ? typeof expectedUrl === 'string'
        ? expectedUrl
        : expectedUrl.toString()
      : 'networkidle';
    throw new Error(
      `Navigation failed. Expected: ${expected}, Current URL: ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Retry a function with exponential backoff
 * إعادة محاولة دالة مع تأخير متزايد
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const { maxRetries = 3, retryDelay = 1000 } = options;
  let lastError: Error | unknown;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      console.warn(`Attempt ${attempt}/${maxRetries} failed:`, error);

      if (attempt < maxRetries) {
        // Exponential backoff: delay * 2^(attempt-1)
        const delay = retryDelay * Math.pow(2, attempt - 1);
        console.log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw new Error(
    `Failed after ${maxRetries} attempts. Last error: ${lastError instanceof Error ? lastError.message : 'Unknown error'}`
  );
}

/**
 * Safe click with retry logic for flaky elements
 * نقر آمن مع إعادة محاولة للعناصر غير المستقرة
 */
export async function safeClick(
  page: Page,
  selector: string,
  options: RetryOptions & { timeout?: number } = {}
): Promise<void> {
  const { timeout = DEFAULT_TIMEOUT, ...retryOptions } = options;

  await retryWithBackoff(async () => {
    try {
      const element = page.locator(selector).first();
      await element.waitFor({ state: 'visible', timeout: ELEMENT_TIMEOUT });
      await element.click({ timeout });
    } catch (error) {
      const currentUrl = page.url();
      throw new Error(
        `Failed to click "${selector}" on ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }, retryOptions);
}
