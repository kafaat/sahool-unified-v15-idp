import { Page, expect } from '@playwright/test';

/**
 * Page Helper Functions
 * دوال مساعدة للصفحات
 */

/**
 * Wait for page to be fully loaded
 * الانتظار حتى يتم تحميل الصفحة بالكامل
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
}

/**
 * Navigate and wait for page
 * التنقل والانتظار للصفحة
 */
export async function navigateAndWait(page: Page, url: string) {
  await page.goto(url);
  await waitForPageLoad(page);
}

/**
 * Check if element is visible on page
 * التحقق من ظهور عنصر في الصفحة
 */
export async function isElementVisible(page: Page, selector: string): Promise<boolean> {
  try {
    const element = page.locator(selector);
    return await element.isVisible({ timeout: 5000 });
  } catch {
    return false;
  }
}

/**
 * Wait for toast/notification message
 * الانتظار لرسالة التنبيه
 */
export async function waitForToast(page: Page, expectedText?: string, timeout = 5000) {
  const toastSelector = '[role="alert"], [data-testid="toast"], .toast, [class*="toast"]';

  try {
    await page.waitForSelector(toastSelector, { timeout, state: 'visible' });

    if (expectedText) {
      const toast = page.locator(toastSelector);
      await expect(toast).toContainText(expectedText);
    }

    return true;
  } catch {
    return false;
  }
}

/**
 * Fill form field with label
 * ملء حقل نموذج باستخدام التسمية
 */
export async function fillFieldByLabel(page: Page, label: string, value: string) {
  // Try to find input by label
  const labelElement = page.locator(`label:has-text("${label}")`);
  const inputId = await labelElement.getAttribute('for');

  if (inputId) {
    await page.fill(`#${inputId}`, value);
  } else {
    // Try to find input within label or nearby
    await page.locator(`label:has-text("${label}") ~ input, label:has-text("${label}") input`).first().fill(value);
  }
}

/**
 * Click button by text (Arabic or English)
 * النقر على زر بالنص (عربي أو إنجليزي)
 */
export async function clickButtonByText(page: Page, ...texts: string[]) {
  for (const text of texts) {
    const button = page.locator(`button:has-text("${text}")`);
    if (await button.isVisible({ timeout: 1000 })) {
      await button.click();
      return;
    }
  }
  throw new Error(`Could not find button with any of these texts: ${texts.join(', ')}`);
}

/**
 * Take screenshot with timestamp
 * أخذ لقطة شاشة مع الطابع الزمني
 */
export async function takeTimestampedScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `test-results/screenshots/${name}-${timestamp}.png`,
    fullPage: true
  });
}

/**
 * Wait for API response
 * الانتظار لاستجابة API
 */
export async function waitForApiResponse(page: Page, urlPattern: string | RegExp, timeout = 10000) {
  return page.waitForResponse(
    (response) => {
      const url = response.url();
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern);
      }
      return urlPattern.test(url);
    },
    { timeout }
  );
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
export async function selectDropdownOption(page: Page, selector: string, optionText: string) {
  await page.click(selector);
  await page.waitForTimeout(300);
  await page.click(`[role="option"]:has-text("${optionText}"), option:has-text("${optionText}")`);
}

/**
 * Wait for navigation to complete
 * الانتظار حتى يكتمل التنقل
 */
export async function waitForNavigation(page: Page, expectedUrl?: string | RegExp) {
  if (expectedUrl) {
    await page.waitForURL(expectedUrl, { timeout: 10000 });
  } else {
    await page.waitForLoadState('networkidle');
  }
}
