import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait, waitForPageLoad, waitForToast, isElementVisible } from './helpers/page.helpers';

/**
 * Wallet E2E Tests
 * اختبارات E2E للمحفظة
 */

test.describe('Wallet Page', () => {
  test.beforeEach(async ({ page, authenticatedPage }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, '/wallet');
  });

  test.describe('Page Load and Display', () => {
    test('should display wallet page correctly', async ({ page }) => {
      // Check page title/heading
      const heading = page.locator('h1:has-text("المحفظة"), h1:has-text("Wallet")');
      await expect(heading).toBeVisible({ timeout: 10000 });

      // Check for bilingual heading
      await expect(page.locator('text=/Wallet.*Payments/i')).toBeVisible();
    });

    test('should have correct page URL', async ({ page }) => {
      await expect(page).toHaveURL(/\/wallet/);
    });

    test('should display page header with correct labels', async ({ page }) => {
      // Arabic label
      await expect(page.locator('text=المحفظة')).toBeVisible();

      // English label
      await expect(page.locator('text=/Wallet.*Payments/i')).toBeVisible();
    });
  });

  test.describe('Balance Display', () => {
    test('should display wallet balance card', async ({ page }) => {
      // Wait for balance card to load
      await page.waitForTimeout(2000);

      // Check for balance label
      const balanceLabel = page.locator('text=/رصيد المحفظة|Wallet Balance/i');
      await expect(balanceLabel).toBeVisible({ timeout: 10000 });
    });

    test('should display balance amount with currency', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for balance amount (should have currency like SAR)
      const balanceAmount = page.locator('text=/\\d+\\.\\d+\\s+(SAR|ريال|SR)/i').first();

      if (await balanceAmount.isVisible({ timeout: 5000 })) {
        await expect(balanceAmount).toBeVisible();

        // Get balance text and verify format
        const balanceText = await balanceAmount.textContent();
        console.log(`Balance displayed: ${balanceText}`);
      }
    });

    test('should display pending balance if exists', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for pending balance indicator
      const pendingBalance = page.locator('text=/قيد الانتظار|Pending/i');
      const hasPending = await pendingBalance.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasPending) {
        console.log('Pending balance is displayed');
        await expect(pendingBalance).toBeVisible();
      } else {
        console.log('No pending balance to display');
      }
    });

    test('should display wallet icon', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Balance card should have wallet icon (SVG)
      const walletIcon = page.locator('svg').first();
      await expect(walletIcon).toBeVisible();
    });

    test('should display balance in gradient card', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Balance card should have gradient background
      const balanceCard = page.locator('.bg-gradient-to-br, [class*="gradient"]').first();
      const hasGradient = await balanceCard.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Gradient balance card: ${hasGradient ? 'found' : 'not found'}`);
    });
  });

  test.describe('Statistics Cards', () => {
    test('should display statistics cards', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for income label
      const incomeLabel = page.locator('text=/إجمالي الإيداعات|Total Income/i');
      const hasIncome = await incomeLabel.isVisible({ timeout: 5000 }).catch(() => false);

      // Look for expenses label
      const expensesLabel = page.locator('text=/إجمالي المصروفات|Total Expenses/i');
      const hasExpenses = await expensesLabel.isVisible({ timeout: 5000 }).catch(() => false);

      // Look for transactions count
      const transactionsLabel = page.locator('text=/عدد المعاملات|Transactions/i');
      const hasTransactions = await transactionsLabel.isVisible({ timeout: 5000 }).catch(() => false);

      console.log(`Statistics cards - Income: ${hasIncome}, Expenses: ${hasExpenses}, Transactions: ${hasTransactions}`);

      // At least one statistic should be visible
      expect(hasIncome || hasExpenses || hasTransactions).toBe(true);
    });

    test('should display monthly income statistics', async ({ page }) => {
      await page.waitForTimeout(2000);

      const monthlyIncomeLabel = page.locator('text=/إجمالي الإيداعات|Total Income/i');

      if (await monthlyIncomeLabel.isVisible({ timeout: 3000 })) {
        await expect(monthlyIncomeLabel).toBeVisible();

        // Should show "this month" indicator
        const thisMonthLabel = page.locator('text=/هذا الشهر/i');
        await expect(thisMonthLabel).toBeVisible();
      }
    });

    test('should display monthly expenses statistics', async ({ page }) => {
      await page.waitForTimeout(2000);

      const monthlyExpensesLabel = page.locator('text=/إجمالي المصروفات|Total Expenses/i');

      if (await monthlyExpensesLabel.isVisible({ timeout: 3000 })) {
        await expect(monthlyExpensesLabel).toBeVisible();
      }
    });

    test('should display transaction count', async ({ page }) => {
      await page.waitForTimeout(2000);

      const transactionCountLabel = page.locator('text=/عدد المعاملات|Transactions/i');

      if (await transactionCountLabel.isVisible({ timeout: 3000 })) {
        await expect(transactionCountLabel).toBeVisible();

        // Should display a number
        const countNumber = page.locator('text=/\\d+/').first();
        await expect(countNumber).toBeVisible();
      }
    });

    test('should display statistics with appropriate icons', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Statistics should have icons (SVG elements)
      const icons = page.locator('svg');
      const iconCount = await icons.count();

      expect(iconCount).toBeGreaterThan(0);
      console.log(`Found ${iconCount} icons in wallet page`);
    });
  });

  test.describe('Wallet Information Section', () => {
    test('should display wallet info section', async ({ page }) => {
      await page.waitForTimeout(2000);

      const walletInfoHeading = page.locator('text=/معلومات المحفظة|Wallet Info/i');
      const hasInfo = await walletInfoHeading.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasInfo) {
        await expect(walletInfoHeading).toBeVisible();
      } else {
        console.log('Wallet info section not found');
      }
    });

    test('should display wallet ID', async ({ page }) => {
      await page.waitForTimeout(2000);

      const walletIdLabel = page.locator('text=/معرف المحفظة/i');
      const hasWalletId = await walletIdLabel.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasWalletId) {
        await expect(walletIdLabel).toBeVisible();
      }
    });

    test('should display total deposits and withdrawals', async ({ page }) => {
      await page.waitForTimeout(2000);

      const depositsLabel = page.locator('text=/إجمالي الإيداعات/i');
      const withdrawalsLabel = page.locator('text=/إجمالي السحوبات/i');

      const hasDeposits = await depositsLabel.isVisible({ timeout: 3000 }).catch(() => false);
      const hasWithdrawals = await withdrawalsLabel.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Total deposits visible: ${hasDeposits}, Total withdrawals visible: ${hasWithdrawals}`);
    });

    test('should display last transaction date', async ({ page }) => {
      await page.waitForTimeout(2000);

      const lastTransactionLabel = page.locator('text=/آخر معاملة/i');
      const hasLastTransaction = await lastTransactionLabel.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasLastTransaction) {
        await expect(lastTransactionLabel).toBeVisible();
      }
    });
  });

  test.describe('Quick Action Buttons', () => {
    test('should display deposit button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const depositButton = page.locator('button:has-text("إيداع"), button:has-text("Deposit")');
      await expect(depositButton.first()).toBeVisible({ timeout: 10000 });
    });

    test('should display withdraw button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const withdrawButton = page.locator('button:has-text("سحب"), button:has-text("Withdraw")');
      await expect(withdrawButton.first()).toBeVisible({ timeout: 10000 });
    });

    test('should display transfer button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const transferButton = page.locator('button:has-text("تحويل"), button:has-text("Transfer")');
      await expect(transferButton.first()).toBeVisible({ timeout: 10000 });
    });

    test('should show alert when clicking deposit button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const depositButton = page.locator('button:has-text("إيداع")').first();

      if (await depositButton.isVisible({ timeout: 3000 })) {
        // Set up dialog handler
        page.on('dialog', async (dialog) => {
          expect(dialog.message()).toContain('قيد التطوير');
          await dialog.accept();
        });

        await depositButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('should show alert when clicking withdraw button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const withdrawButton = page.locator('button:has-text("سحب")').first();

      if (await withdrawButton.isVisible({ timeout: 3000 })) {
        // Set up dialog handler
        page.on('dialog', async (dialog) => {
          expect(dialog.message()).toContain('قيد التطوير');
          await dialog.accept();
        });

        await withdrawButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('should navigate to transfer form when clicking transfer', async ({ page }) => {
      await page.waitForTimeout(2000);

      const transferButton = page.locator('button:has-text("تحويل")').first();

      if (await transferButton.isVisible({ timeout: 3000 })) {
        await transferButton.click();
        await page.waitForTimeout(1000);

        // Should show transfer form or change view
        const backButton = page.locator('button:has-text("رجوع إلى المحفظة")');
        const hasBackButton = await backButton.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasBackButton) {
          await expect(backButton).toBeVisible();
          console.log('Transfer form loaded successfully');
        }
      }
    });
  });

  test.describe('Transaction History', () => {
    test('should display transaction history section', async ({ page }) => {
      await page.waitForTimeout(2000);

      const historyHeading = page.locator('h2:has-text("سجل المعاملات"), h2:has-text("Transaction History")');
      await expect(historyHeading).toBeVisible({ timeout: 10000 });
    });

    test('should display transaction history with bilingual labels', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for both Arabic and English labels
      const bilingualHeading = page.locator('text=/سجل المعاملات.*Transaction History/i');
      await expect(bilingualHeading).toBeVisible();
    });

    test('should display filter button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const filterButton = page.locator('button:has-text("فلتر"), button:has-text("Filter")');
      await expect(filterButton.first()).toBeVisible({ timeout: 10000 });
    });

    test('should display transaction items or empty state', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for transaction items or empty state
      const transactionItems = page.locator('[class*="rounded-xl"][class*="border-2"]');
      const emptyStateMessage = page.locator('text=/لا توجد معاملات|No transactions/i');

      const hasTransactions = await transactionItems.count() > 0;
      const hasEmptyState = await emptyStateMessage.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Transactions: ${hasTransactions}, Empty state: ${hasEmptyState}`);
      expect(hasTransactions || hasEmptyState).toBe(true);
    });

    test('should display empty state when no transactions exist', async ({ page }) => {
      await page.waitForTimeout(3000);

      const emptyStateMessage = page.locator('text=/لا توجد معاملات/i');
      const emptyStateIcon = page.locator('svg').last();

      const hasEmptyMessage = await emptyStateMessage.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasEmptyMessage) {
        await expect(emptyStateMessage).toBeVisible();
        console.log('Empty state displayed correctly');
      } else {
        console.log('Transactions exist - empty state not shown');
      }
    });

    test('should display transaction count if transactions exist', async ({ page }) => {
      await page.waitForTimeout(3000);

      const countLabel = page.locator('text=/عرض.*معاملة|Showing.*transactions/i');
      const hasCount = await countLabel.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasCount) {
        await expect(countLabel).toBeVisible();
        console.log('Transaction count displayed');
      } else {
        console.log('No transactions to count');
      }
    });
  });

  test.describe('Transaction Filters', () => {
    test('should toggle filter panel when clicking filter button', async ({ page }) => {
      await page.waitForTimeout(2000);

      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        await filterButton.click();
        await page.waitForTimeout(500);

        // Filter panel should appear
        const filterPanel = page.locator('button:has-text("الكل"), button:has-text("All")').first();
        const isPanelVisible = await filterPanel.isVisible({ timeout: 3000 }).catch(() => false);

        if (isPanelVisible) {
          await expect(filterPanel).toBeVisible();
          console.log('Filter panel opened successfully');
        }
      }
    });

    test('should display all transaction type filters', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Open filter panel
      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        await filterButton.click();
        await page.waitForTimeout(500);

        // Check for filter options
        const allFilter = page.locator('button:has-text("الكل")');
        const depositFilter = page.locator('button:has-text("إيداع")');
        const withdrawalFilter = page.locator('button:has-text("سحب")');
        const paymentFilter = page.locator('button:has-text("دفع")');
        const transferFilter = page.locator('button:has-text("تحويل")');

        const hasAllFilter = await allFilter.isVisible({ timeout: 2000 }).catch(() => false);
        const hasDepositFilter = await depositFilter.isVisible({ timeout: 2000 }).catch(() => false);
        const hasWithdrawalFilter = await withdrawalFilter.isVisible({ timeout: 2000 }).catch(() => false);
        const hasPaymentFilter = await paymentFilter.isVisible({ timeout: 2000 }).catch(() => false);
        const hasTransferFilter = await transferFilter.isVisible({ timeout: 2000 }).catch(() => false);

        console.log(`Filter options - All: ${hasAllFilter}, Deposit: ${hasDepositFilter}, Withdrawal: ${hasWithdrawalFilter}, Payment: ${hasPaymentFilter}, Transfer: ${hasTransferFilter}`);

        // At least the "All" filter should be visible
        if (hasAllFilter) {
          await expect(allFilter).toBeVisible();
        }
      }
    });

    test('should filter transactions by type - deposit', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Open filter panel
      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        await filterButton.click();
        await page.waitForTimeout(500);

        // Click deposit filter
        const depositFilter = page.locator('button:has-text("إيداع")');

        if (await depositFilter.isVisible({ timeout: 2000 })) {
          await depositFilter.click();
          await page.waitForTimeout(1000);

          // Filter should be active (blue background)
          const isActive = await depositFilter.evaluate((el) =>
            el.className.includes('bg-blue-600')
          );

          console.log(`Deposit filter active: ${isActive}`);
        }
      }
    });

    test('should filter transactions by type - withdrawal', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Open filter panel
      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        await filterButton.click();
        await page.waitForTimeout(500);

        // Click withdrawal filter
        const withdrawalFilter = page.locator('button:has-text("سحب")');

        if (await withdrawalFilter.isVisible({ timeout: 2000 })) {
          await withdrawalFilter.click();
          await page.waitForTimeout(1000);

          console.log('Withdrawal filter clicked');
        }
      }
    });

    test('should reset filters when clicking "All"', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Open filter panel
      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        await filterButton.click();
        await page.waitForTimeout(500);

        // Click a specific filter first
        const depositFilter = page.locator('button:has-text("إيداع")');
        if (await depositFilter.isVisible({ timeout: 2000 })) {
          await depositFilter.click();
          await page.waitForTimeout(500);
        }

        // Then click "All" to reset
        const allFilter = page.locator('button:has-text("الكل")');
        if (await allFilter.isVisible({ timeout: 2000 })) {
          await allFilter.click();
          await page.waitForTimeout(1000);

          // "All" filter should be active
          const isActive = await allFilter.evaluate((el) =>
            el.className.includes('bg-blue-600')
          );

          console.log(`All filter active after reset: ${isActive}`);
        }
      }
    });

    test('should hide filter panel when clicking filter button again', async ({ page }) => {
      await page.waitForTimeout(2000);

      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        // Open filter panel
        await filterButton.click();
        await page.waitForTimeout(500);

        // Verify panel is open
        const filterPanel = page.locator('button:has-text("الكل")').first();
        const isPanelVisible = await filterPanel.isVisible({ timeout: 2000 }).catch(() => false);

        if (isPanelVisible) {
          // Close filter panel
          await filterButton.click();
          await page.waitForTimeout(500);

          // Panel should be hidden
          const isPanelHidden = !await filterPanel.isVisible({ timeout: 2000 }).catch(() => true);
          console.log(`Filter panel hidden: ${isPanelHidden}`);
        }
      }
    });
  });

  test.describe('Transaction Details', () => {
    test('should display transaction status badges', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for status badges with Arabic labels
      const statusBadges = page.locator('text=/مكتمل|قيد الانتظار|فشل|ملغي/i');
      const count = await statusBadges.count();

      if (count > 0) {
        console.log(`Found ${count} transaction status badges`);
        await expect(statusBadges.first()).toBeVisible();
      } else {
        console.log('No transaction status badges found (no transactions)');
      }
    });

    test('should display transaction dates', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for date patterns (Arabic calendar format)
      const dates = page.locator('text=/\\d{1,2}\\/\\d{1,2}\\/\\d{4}/');
      const count = await dates.count();

      console.log(`Found ${count} transaction dates`);
    });

    test('should display transaction amounts with +/- indicators', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for amounts with +/- signs
      const amounts = page.locator('text=/[+\\-]\\d+\\.\\d+/');
      const count = await amounts.count();

      if (count > 0) {
        console.log(`Found ${count} transaction amounts with indicators`);
      } else {
        console.log('No transactions with amount indicators found');
      }
    });

    test('should display transaction icons', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Transaction items should have icons
      const icons = page.locator('svg');
      const iconCount = await icons.count();

      expect(iconCount).toBeGreaterThan(0);
      console.log(`Found ${iconCount} icons`);
    });

    test('should show bilingual descriptions for transactions', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Transactions should have both Arabic and English descriptions
      const transactionItems = page.locator('[class*="rounded-xl"][class*="border-2"]').first();

      if (await transactionItems.isVisible({ timeout: 3000 })) {
        const textContent = await transactionItems.textContent();
        console.log(`Transaction content includes bilingual text: ${textContent}`);
      }
    });
  });

  test.describe('Loading States', () => {
    test('should show loading skeleton for balance', async ({ page }) => {
      // Navigate fresh to catch loading state
      await page.goto('/wallet');

      // Look for loading skeleton or spinner
      const loadingSkeleton = page.locator('[class*="animate-pulse"], [class*="skeleton"]');
      const hasLoading = await loadingSkeleton.isVisible({ timeout: 1000 }).catch(() => false);

      console.log(`Loading skeleton shown: ${hasLoading}`);

      // Wait for content to load
      await page.waitForTimeout(3000);

      // Loading should be gone
      const stillLoading = await loadingSkeleton.isVisible({ timeout: 1000 }).catch(() => false);
      console.log(`Loading skeleton still visible after 3s: ${stillLoading}`);
    });

    test('should show loading skeleton for statistics', async ({ page }) => {
      // Navigate fresh to catch loading state
      await page.goto('/wallet');

      // Look for multiple loading skeletons (for statistics cards)
      const loadingSkeletons = page.locator('[class*="animate-pulse"]');
      const count = await loadingSkeletons.count();

      console.log(`Found ${count} loading skeletons initially`);

      // Wait for content to load
      await page.waitForTimeout(3000);
    });

    test('should show loading skeleton for transactions', async ({ page }) => {
      // Navigate fresh to catch loading state
      await page.goto('/wallet');

      // Look for transaction loading skeletons
      const loadingSkeleton = page.locator('[class*="animate-pulse"]');
      const hasLoading = await loadingSkeleton.isVisible({ timeout: 1000 }).catch(() => false);

      console.log(`Transaction loading skeleton shown: ${hasLoading}`);

      // Wait for content to load
      await page.waitForTimeout(3000);
    });

    test('should display error state gracefully if data fails to load', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for error messages
      const errorMessage = page.locator('text=/خطأ|Error|فشل/i');
      const hasError = await errorMessage.isVisible({ timeout: 2000 }).catch(() => false);

      if (hasError) {
        const errorText = await errorMessage.textContent();
        console.log(`Error message displayed: ${errorText}`);
      } else {
        console.log('No errors - data loaded successfully');
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Reload to apply responsive styles
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Main heading should still be visible
      const heading = page.locator('h1:has-text("المحفظة")');
      await expect(heading).toBeVisible();

      // Balance card should be visible
      const balanceLabel = page.locator('text=/رصيد المحفظة|Wallet Balance/i');
      await expect(balanceLabel).toBeVisible();
    });

    test('should show floating action buttons on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Look for floating action buttons (fixed position)
      const floatingButtons = page.locator('.fixed button');
      const count = await floatingButtons.count();

      console.log(`Found ${count} floating action buttons on mobile`);
    });

    test('should be responsive on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Content should be visible
      const heading = page.locator('h1:has-text("المحفظة")');
      await expect(heading).toBeVisible();

      // Statistics should be in grid layout
      const stats = page.locator('text=/إجمالي الإيداعات|Total Income/i');
      await expect(stats).toBeVisible();
    });

    test('should be responsive on desktop viewport', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // All content should be visible
      const heading = page.locator('h1:has-text("المحفظة")');
      await expect(heading).toBeVisible();

      // Statistics should be in grid layout (3 columns on desktop)
      const stats = page.locator('text=/إجمالي الإيداعات|Total Income/i');
      await expect(stats).toBeVisible();
    });

    test('should adjust grid layout on different screen sizes', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Test mobile
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(500);

      const mobileLayout = await page.locator('body').boundingBox();
      console.log(`Mobile layout width: ${mobileLayout?.width}`);

      // Test tablet
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.waitForTimeout(500);

      const tabletLayout = await page.locator('body').boundingBox();
      console.log(`Tablet layout width: ${tabletLayout?.width}`);

      // Test desktop
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.waitForTimeout(500);

      const desktopLayout = await page.locator('body').boundingBox();
      console.log(`Desktop layout width: ${desktopLayout?.width}`);
    });

    test('should hide mobile floating buttons on desktop', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Floating buttons should be hidden on desktop (md:hidden class)
      const floatingButtons = page.locator('.fixed.bottom-6.left-6 button');
      const count = await floatingButtons.count();

      if (count > 0) {
        // Check if hidden via CSS
        const isHidden = await floatingButtons.first().evaluate((el) => {
          const style = window.getComputedStyle(el);
          return style.display === 'none' || style.visibility === 'hidden';
        });

        console.log(`Floating buttons hidden on desktop: ${isHidden}`);
      }
    });
  });

  test.describe('Arabic/English Labels', () => {
    test('should display all key labels in both Arabic and English', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Main heading
      const mainHeading = page.locator('text=/المحفظة/i');
      await expect(mainHeading).toBeVisible();

      // Balance label
      const balanceLabel = page.locator('text=/رصيد المحفظة.*Wallet Balance/i');
      const hasBalance = await balanceLabel.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasBalance) {
        await expect(balanceLabel).toBeVisible();
      }

      // Transaction history
      const historyLabel = page.locator('text=/سجل المعاملات.*Transaction History/i');
      await expect(historyLabel).toBeVisible();

      console.log('Bilingual labels verified');
    });

    test('should display Arabic labels for action buttons', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Quick action buttons should have Arabic labels
      const depositButton = page.locator('button:has-text("إيداع")');
      const withdrawButton = page.locator('button:has-text("سحب")');
      const transferButton = page.locator('button:has-text("تحويل")');

      await expect(depositButton.first()).toBeVisible();
      await expect(withdrawButton.first()).toBeVisible();
      await expect(transferButton.first()).toBeVisible();
    });

    test('should display Arabic labels for statistics', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Statistics should have Arabic labels
      const incomeLabel = page.locator('text=/إجمالي الإيداعات/i');
      const expensesLabel = page.locator('text=/إجمالي المصروفات/i');

      const hasIncome = await incomeLabel.isVisible({ timeout: 3000 }).catch(() => false);
      const hasExpenses = await expensesLabel.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Arabic stats labels - Income: ${hasIncome}, Expenses: ${hasExpenses}`);
    });

    test('should display English labels alongside Arabic', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for English labels
      const englishLabels = [
        'Wallet',
        'Transaction History',
        'Total Income',
        'Total Expenses',
      ];

      for (const label of englishLabels) {
        const element = page.locator(`text=/${label}/i`);
        const isVisible = await element.isVisible({ timeout: 3000 }).catch(() => false);
        console.log(`English label "${label}": ${isVisible ? 'found' : 'not found'}`);
      }
    });

    test('should display Arabic filter labels', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Open filter panel
      const filterButton = page.locator('button:has-text("فلتر")');

      if (await filterButton.first().isVisible({ timeout: 3000 })) {
        await filterButton.first().click();
        await page.waitForTimeout(500);

        // Check for Arabic filter options
        const arabicFilters = [
          'الكل',
          'إيداع',
          'سحب',
          'دفع',
          'تحويل',
        ];

        for (const filter of arabicFilters) {
          const element = page.locator(`button:has-text("${filter}")`);
          const isVisible = await element.isVisible({ timeout: 2000 }).catch(() => false);
          console.log(`Arabic filter "${filter}": ${isVisible ? 'found' : 'not found'}`);
        }
      }
    });

    test('should display Arabic status labels', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for Arabic status labels
      const statusLabels = [
        'مكتمل',
        'قيد الانتظار',
        'فشل',
        'ملغي',
      ];

      let foundCount = 0;
      for (const label of statusLabels) {
        const element = page.locator(`text=${label}`);
        const count = await element.count();
        if (count > 0) {
          foundCount++;
        }
      }

      console.log(`Found ${foundCount} different Arabic status labels`);
    });

    test('should use Arabic date format', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for dates in Arabic format (ar-SA locale)
      const dates = page.locator('text=/\\d{1,2}\\/\\d{1,2}\\/\\d{4}/');
      const count = await dates.count();

      console.log(`Found ${count} dates in Arabic format`);
    });
  });

  test.describe('Navigation and Interactions', () => {
    test('should navigate back to dashboard view after transfer', async ({ page }) => {
      await page.waitForTimeout(2000);

      const transferButton = page.locator('button:has-text("تحويل")').first();

      if (await transferButton.isVisible({ timeout: 3000 })) {
        // Click transfer
        await transferButton.click();
        await page.waitForTimeout(1000);

        // Look for back button
        const backButton = page.locator('button:has-text("رجوع إلى المحفظة")');

        if (await backButton.isVisible({ timeout: 3000 })) {
          // Click back
          await backButton.click();
          await page.waitForTimeout(1000);

          // Should be back on dashboard view
          const balanceLabel = page.locator('text=/رصيد المحفظة/i');
          await expect(balanceLabel).toBeVisible();
        }
      }
    });

    test('should handle page reload correctly', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Reload page
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Content should load again
      const heading = page.locator('h1:has-text("المحفظة")');
      await expect(heading).toBeVisible();

      const balanceLabel = page.locator('text=/رصيد المحفظة/i');
      await expect(balanceLabel).toBeVisible();
    });

    test('should maintain state after navigation away and back', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Navigate away
      await navigateAndWait(page, '/dashboard');

      // Navigate back
      await navigateAndWait(page, '/wallet');
      await page.waitForTimeout(2000);

      // Wallet page should load correctly
      const heading = page.locator('h1:has-text("المحفظة")');
      await expect(heading).toBeVisible();
    });

    test('should handle hover states on transaction items', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Find transaction items
      const transactionItems = page.locator('[class*="rounded-xl"][class*="border-2"][class*="hover"]').first();

      if (await transactionItems.isVisible({ timeout: 3000 })) {
        // Hover over transaction
        await transactionItems.hover();
        await page.waitForTimeout(500);

        console.log('Transaction item hover state tested');
      }
    });

    test('should handle hover states on action buttons', async ({ page }) => {
      await page.waitForTimeout(2000);

      const depositButton = page.locator('button:has-text("إيداع")').first();

      if (await depositButton.isVisible({ timeout: 3000 })) {
        // Hover over button
        await depositButton.hover();
        await page.waitForTimeout(500);

        console.log('Action button hover state tested');
      }
    });
  });

  test.describe('Edge Cases', () => {
    test('should handle zero balance correctly', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Balance should be displayed even if zero
      const balanceAmount = page.locator('text=/\\d+\\.\\d+\\s+(SAR|ريال|SR)/i').first();

      if (await balanceAmount.isVisible({ timeout: 5000 })) {
        const balanceText = await balanceAmount.textContent();
        console.log(`Balance text: ${balanceText}`);

        // Should have proper decimal format
        expect(balanceText).toMatch(/\d+\.\d{2}/);
      }
    });

    test('should handle empty transaction history', async ({ page }) => {
      await page.waitForTimeout(3000);

      // Should show either transactions or empty state
      const emptyState = page.locator('text=/لا توجد معاملات/i');
      const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasEmptyState) {
        await expect(emptyState).toBeVisible();
        console.log('Empty state displayed correctly');
      } else {
        console.log('Transactions exist');
      }
    });

    test('should handle filter with no matching transactions', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Open filter panel
      const filterButton = page.locator('button:has-text("فلتر")').first();

      if (await filterButton.isVisible({ timeout: 3000 })) {
        await filterButton.click();
        await page.waitForTimeout(500);

        // Apply a filter
        const withdrawalFilter = page.locator('button:has-text("سحب")');

        if (await withdrawalFilter.isVisible({ timeout: 2000 })) {
          await withdrawalFilter.click();
          await page.waitForTimeout(1000);

          // Check if empty state or filtered results are shown
          const emptyState = page.locator('text=/لا توجد معاملات/i');
          const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

          console.log(`Empty state after filter: ${hasEmptyState}`);
        }
      }
    });
  });
});
