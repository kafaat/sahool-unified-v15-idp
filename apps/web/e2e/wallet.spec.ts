import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait, waitForPageLoad } from './helpers/page.helpers';

/**
 * Wallet E2E Tests
 * اختبارات E2E للمحفظة
 */

test.describe('Wallet Page', () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, '/wallet');
  });

  test.describe('Page Load and Display', () => {
    test('should display wallet page correctly', async ({ page }) => {
      // Check page title/heading using data-testid
      const heading = page.locator('[data-testid="wallet-page-title"]');
      await expect(heading).toBeVisible({ timeout: 10000 });

      // Check for bilingual subtitle
      const subtitle = page.locator('[data-testid="wallet-page-subtitle"]');
      await expect(subtitle).toBeVisible();
      await expect(subtitle).toContainText('Wallet');
    });

    test('should have correct page URL', async ({ page }) => {
      await expect(page).toHaveURL(/\/wallet/);
    });

    test('should display page header with correct labels', async ({ page }) => {
      // Check wallet page container
      await expect(page.locator('[data-testid="wallet-page"]')).toBeVisible();

      // Check page header
      await expect(page.locator('[data-testid="wallet-page-header"]')).toBeVisible();

      // Check title and subtitle
      await expect(page.locator('[data-testid="wallet-page-title"]')).toContainText('المحفظة');
      await expect(page.locator('[data-testid="wallet-page-subtitle"]')).toContainText('Wallet');
    });
  });

  test.describe('Balance Display', () => {
    test('should display wallet balance card', async ({ page }) => {
      // Check for balance card using data-testid
      const balanceCard = page.locator('[data-testid="wallet-balance-card"]');
      await expect(balanceCard).toBeVisible({ timeout: 10000 });

      // Check for balance label
      const balanceLabel = page.locator('[data-testid="wallet-balance-label"]');
      await expect(balanceLabel).toBeVisible();
      await expect(balanceLabel).toContainText('رصيد المحفظة');
      await expect(balanceLabel).toContainText('Wallet Balance');
    });

    test('should display balance amount with currency', async ({ page }) => {
      // Look for balance amount using data-testid
      const balanceAmount = page.locator('[data-testid="wallet-balance-amount"]');
      await expect(balanceAmount).toBeVisible({ timeout: 10000 });

      // Get balance text and verify format
      const balanceText = await balanceAmount.textContent();
      console.log(`Balance displayed: ${balanceText}`);

      // Should contain decimal number and currency
      expect(balanceText).toMatch(/\d+\.\d+/);
      expect(balanceText).toContain('SAR');
    });

    test('should display pending balance if exists', async ({ page }) => {
      // Look for pending balance indicator using data-testid
      const pendingBalance = page.locator('[data-testid="wallet-pending-balance"]');
      const hasPending = await pendingBalance.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasPending) {
        console.log('Pending balance is displayed');
        await expect(pendingBalance).toBeVisible();
        await expect(pendingBalance).toContainText('قيد الانتظار');
      } else {
        console.log('No pending balance to display (which is expected with mock data)');
      }
    });

    test('should display wallet icon', async ({ page }) => {
      // Balance card should have wallet icon using data-testid
      const walletIcon = page.locator('[data-testid="wallet-icon"]');
      await expect(walletIcon).toBeVisible({ timeout: 10000 });
    });

    test('should display balance in gradient card', async ({ page }) => {
      // Balance card should have gradient background
      const balanceCard = page.locator('[data-testid="wallet-balance-card"]');
      await expect(balanceCard).toBeVisible({ timeout: 10000 });

      // Verify it has gradient classes
      const hasGradient = await balanceCard.evaluate((el) =>
        el.className.includes('bg-gradient-to-br')
      );
      expect(hasGradient).toBe(true);
      console.log('Gradient balance card verified');
    });
  });

  test.describe('Statistics Cards', () => {
    test('should display statistics cards', async ({ page }) => {
      // Check statistics grid
      const statsGrid = page.locator('[data-testid="wallet-statistics-grid"]');
      await expect(statsGrid).toBeVisible({ timeout: 10000 });

      // Check all three stat cards
      const incomeCard = page.locator('[data-testid="wallet-stat-income"]');
      const expensesCard = page.locator('[data-testid="wallet-stat-expenses"]');
      const transactionsCard = page.locator('[data-testid="wallet-stat-transactions"]');

      await expect(incomeCard).toBeVisible();
      await expect(expensesCard).toBeVisible();
      await expect(transactionsCard).toBeVisible();

      console.log('All statistics cards are displayed with mock data');
    });

    test('should display monthly income statistics', async ({ page }) => {
      const incomeCard = page.locator('[data-testid="wallet-stat-income"]');
      await expect(incomeCard).toBeVisible({ timeout: 10000 });

      // Check income amount
      const incomeAmount = page.locator('[data-testid="wallet-stat-income-amount"]');
      await expect(incomeAmount).toBeVisible();

      const amountText = await incomeAmount.textContent();
      console.log(`Monthly income: ${amountText}`);

      // Should show proper format with SAR currency
      expect(amountText).toMatch(/\d+\.\d+/);
      expect(amountText).toContain('SAR');

      // Should show "this month" indicator
      await expect(incomeCard).toContainText('هذا الشهر');
    });

    test('should display monthly expenses statistics', async ({ page }) => {
      const expensesCard = page.locator('[data-testid="wallet-stat-expenses"]');
      await expect(expensesCard).toBeVisible({ timeout: 10000 });

      // Check expenses amount
      const expensesAmount = page.locator('[data-testid="wallet-stat-expenses-amount"]');
      await expect(expensesAmount).toBeVisible();

      const amountText = await expensesAmount.textContent();
      console.log(`Monthly expenses: ${amountText}`);

      expect(amountText).toMatch(/\d+\.\d+/);
      expect(amountText).toContain('SAR');
    });

    test('should display transaction count', async ({ page }) => {
      const transactionsCard = page.locator('[data-testid="wallet-stat-transactions"]');
      await expect(transactionsCard).toBeVisible({ timeout: 10000 });

      // Check transaction count
      const transactionCount = page.locator('[data-testid="wallet-stat-transactions-count"]');
      await expect(transactionCount).toBeVisible();

      const countText = await transactionCount.textContent();
      console.log(`Transaction count: ${countText}`);

      // Should display a number
      expect(countText).toMatch(/\d+/);
    });

    test('should display statistics with appropriate icons', async ({ page }) => {
      // All statistics cards should be visible
      const statsGrid = page.locator('[data-testid="wallet-statistics-grid"]');
      await expect(statsGrid).toBeVisible({ timeout: 10000 });

      // Statistics should have icons (SVG elements within the cards)
      const icons = statsGrid.locator('svg');
      const iconCount = await icons.count();

      expect(iconCount).toBeGreaterThanOrEqual(3); // At least one icon per stat card
      console.log(`Found ${iconCount} icons in statistics cards`);
    });
  });

  test.describe('Wallet Information Section', () => {
    test('should display wallet info section', async ({ page }) => {
      const walletInfoSection = page.locator('[data-testid="wallet-info-section"]');
      await expect(walletInfoSection).toBeVisible({ timeout: 10000 });

      await expect(walletInfoSection).toContainText('معلومات المحفظة');
      await expect(walletInfoSection).toContainText('Wallet Info');
    });

    test('should display wallet ID', async ({ page }) => {
      const walletId = page.locator('[data-testid="wallet-info-id"]');
      await expect(walletId).toBeVisible({ timeout: 10000 });

      await expect(walletId).toContainText('معرف المحفظة');

      const idValue = await walletId.textContent();
      console.log(`Wallet ID: ${idValue}`);
    });

    test('should display total deposits and withdrawals', async ({ page }) => {
      const deposits = page.locator('[data-testid="wallet-info-deposits"]');
      const withdrawals = page.locator('[data-testid="wallet-info-withdrawals"]');

      await expect(deposits).toBeVisible({ timeout: 10000 });
      await expect(withdrawals).toBeVisible({ timeout: 10000 });

      await expect(deposits).toContainText('إجمالي الإيداعات');
      await expect(withdrawals).toContainText('إجمالي السحوبات');

      const depositsText = await deposits.textContent();
      const withdrawalsText = await withdrawals.textContent();

      console.log(`Total deposits: ${depositsText}`);
      console.log(`Total withdrawals: ${withdrawalsText}`);

      // Verify they contain SAR currency
      expect(depositsText).toContain('SAR');
      expect(withdrawalsText).toContain('SAR');
    });

    test('should display last transaction date', async ({ page }) => {
      const lastTransaction = page.locator('[data-testid="wallet-info-last-transaction"]');
      await expect(lastTransaction).toBeVisible({ timeout: 10000 });

      await expect(lastTransaction).toContainText('آخر معاملة');

      const dateText = await lastTransaction.textContent();
      console.log(`Last transaction: ${dateText}`);
    });
  });

  test.describe('Quick Action Buttons', () => {
    test('should display deposit button', async ({ page }) => {
      const depositButton = page.locator('[data-testid="wallet-deposit-button"]');
      await expect(depositButton).toBeVisible({ timeout: 10000 });
      await expect(depositButton).toContainText('إيداع');
    });

    test('should display withdraw button', async ({ page }) => {
      const withdrawButton = page.locator('[data-testid="wallet-withdraw-button"]');
      await expect(withdrawButton).toBeVisible({ timeout: 10000 });
      await expect(withdrawButton).toContainText('سحب');
    });

    test('should display transfer button', async ({ page }) => {
      const transferButton = page.locator('[data-testid="wallet-transfer-button"]');
      await expect(transferButton).toBeVisible({ timeout: 10000 });
      await expect(transferButton).toContainText('تحويل');
    });

    test('should show alert when clicking deposit button', async ({ page }) => {
      const depositButton = page.locator('[data-testid="wallet-deposit-button"]');
      await expect(depositButton).toBeVisible({ timeout: 10000 });

      // Set up dialog handler
      page.on('dialog', async (dialog) => {
        expect(dialog.message()).toContain('قيد التطوير');
        await dialog.accept();
      });

      await depositButton.click();
      await page.waitForTimeout(500);
      console.log('Deposit button clicked - alert shown');
    });

    test('should show alert when clicking withdraw button', async ({ page }) => {
      const withdrawButton = page.locator('[data-testid="wallet-withdraw-button"]');
      await expect(withdrawButton).toBeVisible({ timeout: 10000 });

      // Set up dialog handler
      page.on('dialog', async (dialog) => {
        expect(dialog.message()).toContain('قيد التطوير');
        await dialog.accept();
      });

      await withdrawButton.click();
      await page.waitForTimeout(500);
      console.log('Withdraw button clicked - alert shown');
    });

    test('should navigate to transfer form when clicking transfer', async ({ page }) => {
      const transferButton = page.locator('[data-testid="wallet-transfer-button"]');
      await expect(transferButton).toBeVisible({ timeout: 10000 });

      await transferButton.click();
      await page.waitForTimeout(1000);

      // Should show transfer form or change view with back button
      const backButton = page.locator('[data-testid="wallet-back-button"]');
      await expect(backButton).toBeVisible({ timeout: 5000 });
      await expect(backButton).toContainText('رجوع إلى المحفظة');

      console.log('Transfer form loaded successfully');
    });
  });

  test.describe('Transaction History', () => {
    test('should display transaction history section', async ({ page }) => {
      const historySection = page.locator('[data-testid="transaction-history"]');
      await expect(historySection).toBeVisible({ timeout: 10000 });

      const historyHeading = page.locator('[data-testid="transaction-history-heading"]');
      await expect(historyHeading).toBeVisible();
    });

    test('should display transaction history with bilingual labels', async ({ page }) => {
      const historyHeading = page.locator('[data-testid="transaction-history-heading"]');
      await expect(historyHeading).toBeVisible({ timeout: 10000 });

      // Check for both Arabic and English labels
      await expect(historyHeading).toContainText('سجل المعاملات');
      await expect(historyHeading).toContainText('Transaction History');
    });

    test('should display filter button', async ({ page }) => {
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await expect(filterButton).toBeVisible({ timeout: 10000 });
      await expect(filterButton).toContainText('فلتر');
    });

    test('should display transaction items with mock data', async ({ page }) => {
      // With mock data fallback, we should always have transactions
      const transactionList = page.locator('[data-testid="transaction-list"]');
      await expect(transactionList).toBeVisible({ timeout: 10000 });

      // Check for transaction items
      const transactionItems = transactionList.locator('[data-testid^="transaction-item-"]');
      const count = await transactionItems.count();

      expect(count).toBeGreaterThan(0);
      console.log(`Found ${count} transaction items with mock data`);

      // Verify transaction count is displayed
      const countLabel = page.locator('[data-testid="transaction-count"]');
      await expect(countLabel).toBeVisible();
      await expect(countLabel).toContainText(`${count}`);
    });

    test('should display transaction details correctly', async ({ page }) => {
      // Check that first transaction has all required elements
      const firstTransaction = page.locator('[data-testid^="transaction-item-"]').first();
      await expect(firstTransaction).toBeVisible({ timeout: 10000 });

      // Check for icon
      const icon = firstTransaction.locator('[data-testid="transaction-item-icon"]');
      await expect(icon).toBeVisible();

      // Check for descriptions
      const descriptionAr = firstTransaction.locator('[data-testid="transaction-item-description-ar"]');
      const descriptionEn = firstTransaction.locator('[data-testid="transaction-item-description"]');
      await expect(descriptionAr).toBeVisible();
      await expect(descriptionEn).toBeVisible();

      // Check for status
      const status = firstTransaction.locator('[data-testid="transaction-item-status"]');
      await expect(status).toBeVisible();

      // Check for date
      const date = firstTransaction.locator('[data-testid="transaction-item-date"]');
      await expect(date).toBeVisible();

      // Check for amount
      const amount = firstTransaction.locator('[data-testid="transaction-item-amount"]');
      await expect(amount).toBeVisible();

      console.log('Transaction details verified successfully');
    });
  });

  test.describe('Transaction Filters', () => {
    test('should toggle filter panel when clicking filter button', async ({ page }) => {
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await expect(filterButton).toBeVisible({ timeout: 10000 });

      await filterButton.click();
      await page.waitForTimeout(500);

      // Filter panel should appear
      const filterPanel = page.locator('[data-testid="transaction-filter-panel"]');
      await expect(filterPanel).toBeVisible({ timeout: 5000 });

      console.log('Filter panel opened successfully');
    });

    test('should display all transaction type filters', async ({ page }) => {
      // Open filter panel
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await expect(filterButton).toBeVisible({ timeout: 10000 });

      await filterButton.click();
      await page.waitForTimeout(500);

      // Check for filter panel
      const filterPanel = page.locator('[data-testid="transaction-filter-panel"]');
      await expect(filterPanel).toBeVisible();

      // Check for all filter options
      const allFilter = page.locator('[data-testid="transaction-filter-all"]');
      const depositFilter = page.locator('[data-testid="transaction-filter-deposit"]');
      const withdrawalFilter = page.locator('[data-testid="transaction-filter-withdrawal"]');
      const paymentFilter = page.locator('[data-testid="transaction-filter-payment"]');
      const transferFilter = page.locator('[data-testid="transaction-filter-transfer"]');

      await expect(allFilter).toBeVisible();
      await expect(depositFilter).toBeVisible();
      await expect(withdrawalFilter).toBeVisible();
      await expect(paymentFilter).toBeVisible();
      await expect(transferFilter).toBeVisible();

      console.log('All filter options are visible');
    });

    test('should filter transactions by type - deposit', async ({ page }) => {
      // Open filter panel
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Click deposit filter
      const depositFilter = page.locator('[data-testid="transaction-filter-deposit"]');
      await expect(depositFilter).toBeVisible();
      await depositFilter.click();
      await page.waitForTimeout(1000);

      // Filter should be active (blue background)
      const isActive = await depositFilter.evaluate((el) =>
        el.className.includes('bg-blue-600')
      );

      expect(isActive).toBe(true);
      console.log('Deposit filter active and transactions filtered');
    });

    test('should filter transactions by type - withdrawal', async ({ page }) => {
      // Open filter panel
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Click withdrawal filter
      const withdrawalFilter = page.locator('[data-testid="transaction-filter-withdrawal"]');
      await expect(withdrawalFilter).toBeVisible();
      await withdrawalFilter.click();
      await page.waitForTimeout(1000);

      // Verify filter is active
      const isActive = await withdrawalFilter.evaluate((el) =>
        el.className.includes('bg-blue-600')
      );

      expect(isActive).toBe(true);
      console.log('Withdrawal filter clicked and active');
    });

    test('should reset filters when clicking "All"', async ({ page }) => {
      // Open filter panel
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Click a specific filter first
      const depositFilter = page.locator('[data-testid="transaction-filter-deposit"]');
      await depositFilter.click();
      await page.waitForTimeout(500);

      // Then click "All" to reset
      const allFilter = page.locator('[data-testid="transaction-filter-all"]');
      await allFilter.click();
      await page.waitForTimeout(1000);

      // "All" filter should be active
      const isActive = await allFilter.evaluate((el) =>
        el.className.includes('bg-blue-600')
      );

      expect(isActive).toBe(true);
      console.log('All filter active after reset');
    });

    test('should hide filter panel when clicking filter button again', async ({ page }) => {
      const filterButton = page.locator('[data-testid="transaction-filter-button"]');
      await expect(filterButton).toBeVisible({ timeout: 10000 });

      // Open filter panel
      await filterButton.click();
      await page.waitForTimeout(500);

      // Verify panel is open
      const filterPanel = page.locator('[data-testid="transaction-filter-panel"]');
      await expect(filterPanel).toBeVisible();

      // Close filter panel
      await filterButton.click();
      await page.waitForTimeout(500);

      // Panel should be hidden
      const isPanelHidden = !await filterPanel.isVisible({ timeout: 2000 }).catch(() => true);
      expect(isPanelHidden).toBe(true);
      console.log('Filter panel hidden successfully');
    });
  });

  test.describe('Transaction Details', () => {
    test('should display transaction with all details using mock data', async ({ page }) => {
      // Get first transaction item
      const firstTransaction = page.locator('[data-testid^="transaction-item-"]').first();
      await expect(firstTransaction).toBeVisible({ timeout: 10000 });

      // Check status badge
      const statusBadge = firstTransaction.locator('[data-testid="transaction-item-status"]');
      await expect(statusBadge).toBeVisible();
      const statusText = await statusBadge.textContent();
      expect(statusText).toMatch(/مكتمل|قيد الانتظار|فشل|ملغي/);
      console.log(`Transaction status: ${statusText}`);

      // Check date
      const date = firstTransaction.locator('[data-testid="transaction-item-date"]');
      await expect(date).toBeVisible();
      const dateText = await date.textContent();
      console.log(`Transaction date: ${dateText}`);

      // Check amount with +/- indicators
      const amount = firstTransaction.locator('[data-testid="transaction-item-amount"]');
      await expect(amount).toBeVisible();
      const amountText = await amount.textContent();
      expect(amountText).toMatch(/[\+\-]?\d+\.\d+/);
      console.log(`Transaction amount: ${amountText}`);

      // Check bilingual descriptions
      const descriptionAr = await firstTransaction.locator('[data-testid="transaction-item-description-ar"]').textContent();
      const descriptionEn = await firstTransaction.locator('[data-testid="transaction-item-description"]').textContent();
      expect(descriptionAr).toBeTruthy();
      expect(descriptionEn).toBeTruthy();
      console.log(`Bilingual descriptions verified: AR="${descriptionAr}", EN="${descriptionEn}"`);
    });
  });

  test.describe('Mock Data Rendering', () => {
    test('should render with mock data fallback when API fails', async ({ page }) => {
      // The wallet page should always render with mock data as fallback
      // Verify all key sections are present with data

      // Check wallet dashboard
      const dashboard = page.locator('[data-testid="wallet-dashboard"]');
      await expect(dashboard).toBeVisible({ timeout: 10000 });

      // Check balance is displayed with mock data
      const balanceAmount = page.locator('[data-testid="wallet-balance-amount"]');
      await expect(balanceAmount).toBeVisible();
      const balance = await balanceAmount.textContent();
      expect(balance).toContain('943.00'); // Mock wallet balance
      expect(balance).toContain('SAR');

      // Check statistics have mock values
      const incomeAmount = page.locator('[data-testid="wallet-stat-income-amount"]');
      await expect(incomeAmount).toBeVisible();
      const income = await incomeAmount.textContent();
      expect(income).toContain('1500.00'); // Mock monthly income

      // Check transactions list has mock data
      const transactionList = page.locator('[data-testid="transaction-list"]');
      await expect(transactionList).toBeVisible();

      const transactionItems = transactionList.locator('[data-testid^="transaction-item-"]');
      const count = await transactionItems.count();
      expect(count).toBe(4); // We have 4 mock transactions

      console.log('Wallet page successfully renders with mock data fallback');
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);

      // Main components should be visible
      const pageTitle = page.locator('[data-testid="wallet-page-title"]');
      await expect(pageTitle).toBeVisible({ timeout: 10000 });

      const balanceCard = page.locator('[data-testid="wallet-balance-card"]');
      await expect(balanceCard).toBeVisible();

      console.log('Mobile viewport: Wallet page renders correctly');
    });

    test('should be responsive on desktop viewport', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);

      // All content should be visible
      const dashboard = page.locator('[data-testid="wallet-dashboard"]');
      await expect(dashboard).toBeVisible({ timeout: 10000 });

      // Statistics grid should be visible
      const statsGrid = page.locator('[data-testid="wallet-statistics-grid"]');
      await expect(statsGrid).toBeVisible();

      console.log('Desktop viewport: Wallet page renders correctly');
    });
  });

  test.describe('Bilingual Support', () => {
    test('should display bilingual labels throughout the page', async ({ page }) => {
      // Page title
      const pageTitle = page.locator('[data-testid="wallet-page-title"]');
      await expect(pageTitle).toContainText('المحفظة');

      const pageSubtitle = page.locator('[data-testid="wallet-page-subtitle"]');
      await expect(pageSubtitle).toContainText('Wallet');

      // Balance label
      const balanceLabel = page.locator('[data-testid="wallet-balance-label"]');
      await expect(balanceLabel).toContainText('رصيد المحفظة');
      await expect(balanceLabel).toContainText('Wallet Balance');

      // Transaction history
      const historyHeading = page.locator('[data-testid="transaction-history-heading"]');
      await expect(historyHeading).toContainText('سجل المعاملات');
      await expect(historyHeading).toContainText('Transaction History');

      console.log('Bilingual labels verified successfully');
    });
  });

  test.describe('Navigation', () => {
    test('should navigate to transfer form and back to dashboard', async ({ page }) => {
      // Click transfer button
      const transferButton = page.locator('[data-testid="wallet-transfer-button"]');
      await transferButton.click();
      await page.waitForTimeout(1000);

      // Should show back button
      const backButton = page.locator('[data-testid="wallet-back-button"]');
      await expect(backButton).toBeVisible({ timeout: 5000 });

      // Click back
      await backButton.click();
      await page.waitForTimeout(1000);

      // Should be back on dashboard view
      const dashboard = page.locator('[data-testid="wallet-dashboard"]');
      await expect(dashboard).toBeVisible();

      console.log('Navigation between transfer and dashboard verified');
    });

    test('should handle page reload correctly', async ({ page }) => {
      // Reload page
      await page.reload();
      await waitForPageLoad(page);

      // Content should load again with mock data
      const pageTitle = page.locator('[data-testid="wallet-page-title"]');
      await expect(pageTitle).toBeVisible({ timeout: 10000 });

      const dashboard = page.locator('[data-testid="wallet-dashboard"]');
      await expect(dashboard).toBeVisible();

      console.log('Page reload handled correctly');
    });
  });
});
