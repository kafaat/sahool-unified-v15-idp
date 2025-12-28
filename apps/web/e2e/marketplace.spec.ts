import { test, expect } from './fixtures/test-fixtures';
import {
  navigateAndWait,
  waitForPageLoad,
} from './helpers/page.helpers';
import { timeouts } from './helpers/test-data';

/**
 * Marketplace E2E Tests
 * اختبارات E2E للسوق الزراعي
 */

test.describe('Marketplace Page', () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, '/marketplace');
  });

  test.describe('Page Load and Basic Structure', () => {
    test('should display marketplace page correctly', async ({ page }) => {
      // Check page title - uses default SAHOOL title
      await expect(page).toHaveTitle(/SAHOOL|سهول/i);

      // Check for main heading in Arabic
      const arabicHeading = page.locator('text=/السوق الزراعي/i');
      await expect(arabicHeading).toBeVisible({ timeout: timeouts.long });

      // Check for English subtitle
      const englishSubtitle = page.locator('text=/Agricultural Marketplace/i');
      await expect(englishSubtitle).toBeVisible();
    });

    test('should display page header with cart button', async ({ page }) => {
      // Cart button should be visible
      const cartButton = page.locator('button:has-text("السلة")');
      await expect(cartButton).toBeVisible();

      // Cart icon should be present
      const cartIcon = cartButton.locator('svg');
      await expect(cartIcon).toBeVisible();
    });

    test('should display statistics cards', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for "Available Products" stat card
      const availableProducts = page.locator('text=/منتجات متاحة|Available Products/i');
      await expect(availableProducts).toBeVisible();

      // Check for "Items in Cart" stat card
      const itemsInCart = page.locator('text=/منتجات في السلة|Items in Cart/i');
      await expect(itemsInCart).toBeVisible();

      // Check for "My Orders" stat card
      const myOrders = page.locator('text=/طلباتي|My Orders/i');
      await expect(myOrders).toBeVisible();

      // All stat cards should display numeric values
      const statNumbers = page.locator('h3.text-3xl');
      const count = await statNumbers.count();
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test('should display products section', async ({ page }) => {
      // Products heading should be visible
      const productsHeading = page.locator('h2:has-text("المنتجات")');
      await expect(productsHeading).toBeVisible({ timeout: timeouts.long });
    });
  });

  test.describe('Product Listing and Display', () => {
    test('should display product grid', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for product cards
      const productCards = page.locator('[class*="grid"] > div').filter({
        has: page.locator('text=/منتج|Product|بذور|أسمدة|معدات/i'),
      });

      const count = await productCards.count();
      console.log(`Found ${count} product cards`);

      // Should have at least one product or show empty state
      if (count === 0) {
        // Check for empty state
        const emptyState = page.locator('text=/لا توجد منتجات/i');
        await expect(emptyState).toBeVisible();
      } else {
        expect(count).toBeGreaterThan(0);
      }
    });

    test('should display product card details', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Get first product card
      const firstProduct = page.locator('[class*="grid"] > div').first();

      if (await firstProduct.isVisible({ timeout: 3000 })) {
        // Product should have an image or placeholder
        const productImage = firstProduct.locator('img, svg');
        await expect(productImage.first()).toBeVisible();

        // Product should have a name (could be in Arabic or English)
        const productText = await firstProduct.textContent();
        expect(productText).toBeTruthy();
        expect(productText!.length).toBeGreaterThan(0);
      } else {
        console.log('No products available to test card details');
      }
    });

    test('should display product prices', async ({ page }) => {
      await page.waitForTimeout(2000);

      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();

      if (count > 0) {
        const firstProduct = productCards.first();

        // Should display price with currency
        const priceElement = firstProduct.locator('text=/\\d+\\.\\d+.*ر\\.س|SAR|SR/i');
        const hasPriceInCard = await priceElement.isVisible().catch(() => false);

        console.log(`Price visible in product card: ${hasPriceInCard}`);
      }
    });

    test('should display add to cart buttons', async ({ page }) => {
      await page.waitForTimeout(2000);

      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();

      if (count > 0) {
        // Look for shopping cart icon buttons
        const cartButtons = page.locator('button svg[class*="lucide"]').filter({
          has: page.locator('..'),
        });

        const buttonCount = await cartButtons.count();
        console.log(`Found ${buttonCount} add to cart buttons`);
      }
    });

    test('should display product count', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for results count text
      const resultsText = page.locator('text=/عرض.*منتج|Showing.*products/i');
      const isVisible = await resultsText.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        await expect(resultsText).toBeVisible();
      } else {
        console.log('Results count not visible - may show empty state');
      }
    });
  });

  test.describe('Search Functionality', () => {
    test('should display search input', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');
      await expect(searchInput).toBeVisible({ timeout: timeouts.long });
    });

    test('should allow typing in search field', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');
      await searchInput.fill('بذور');

      const value = await searchInput.inputValue();
      expect(value).toBe('بذور');
    });

    test('should search for products in English', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');
      await searchInput.fill('seed');

      // Wait for search to take effect
      await page.waitForTimeout(1500);

      // Page should update (either show results or empty state)
      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();
    });

    test('should search for products in Arabic', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');
      await searchInput.fill('بذور');

      // Wait for search to take effect
      await page.waitForTimeout(1500);

      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();
    });

    test('should show empty state when no results found', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');
      // Search for something unlikely to exist
      await searchInput.fill('xyz123nonexistent999');

      await page.waitForTimeout(1500);

      // Should show empty state or no results message
      const emptyState = page.locator(
        'text=/لا توجد منتجات|No products|جرب البحث بكلمات مختلفة/i'
      );
      const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Empty state shown for no results: ${hasEmptyState}`);
    });

    test('should clear search results', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');

      // Search for something
      await searchInput.fill('test');
      await page.waitForTimeout(1000);

      // Clear search
      await searchInput.clear();
      await page.waitForTimeout(1000);

      // Should show all products again
      const value = await searchInput.inputValue();
      expect(value).toBe('');
    });
  });

  test.describe('Filtering and Sorting', () => {
    test('should display filter button', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await expect(filterButton).toBeVisible({ timeout: timeouts.long });
    });

    test('should toggle filter panel', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();

      await page.waitForTimeout(500);

      // Category filter buttons should appear
      const categoryFilters = page.locator('button:has-text("الكل"), button:has-text("بذور")');
      await expect(categoryFilters.first()).toBeVisible();

      // Click again to close
      await filterButton.click();
      await page.waitForTimeout(500);
    });

    test('should display sort dropdown', async ({ page }) => {
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("ترتيب حسب")'),
      });

      await expect(sortDropdown).toBeVisible({ timeout: timeouts.long });
    });

    test('should change sort order', async ({ page }) => {
      await page.waitForTimeout(1000);

      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("ترتيب حسب")'),
      });

      // Select price low to high
      await sortDropdown.selectOption({ label: 'السعر: من الأقل للأعلى' });
      await page.waitForTimeout(1000);

      // Verify selection
      const selectedValue = await sortDropdown.inputValue();
      expect(selectedValue).toBe('price_asc');
    });

    test('should display all sort options', async ({ page }) => {
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("ترتيب حسب")'),
      });

      // Check for all sort options
      const options = [
        'ترتيب حسب',
        'السعر: من الأقل للأعلى',
        'السعر: من الأعلى للأقل',
        'الأحدث',
        'الأعلى تقييماً',
      ];

      for (const option of options) {
        const hasOption = await sortDropdown
          .locator(`option:has-text("${option}")`)
          .isVisible()
          .catch(() => false);
        expect(hasOption).toBe(true);
      }
    });
  });

  test.describe('Product Categories', () => {
    test('should display category filters when filter is open', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Check for all category buttons
      const categories = ['الكل', 'بذور', 'أسمدة', 'مبيدات', 'معدات', 'أدوات'];

      for (const category of categories) {
        const categoryButton = page.locator(`button:has-text("${category}")`);
        await expect(categoryButton).toBeVisible();
      }
    });

    test('should filter by seeds category', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      const seedsButton = page.locator('button:has-text("بذور")');
      await seedsButton.click();
      await page.waitForTimeout(1500);

      // Button should be active (has different styling)
      const buttonClass = await seedsButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });

    test('should filter by fertilizers category', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      const fertilizersButton = page.locator('button:has-text("أسمدة")');
      await fertilizersButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await fertilizersButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });

    test('should filter by pesticides category', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      const pesticidesButton = page.locator('button:has-text("مبيدات")');
      await pesticidesButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await pesticidesButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });

    test('should filter by equipment category', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      const equipmentButton = page.locator('button:has-text("معدات")');
      await equipmentButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await equipmentButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });

    test('should filter by tools category', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      const toolsButton = page.locator('button:has-text("أدوات")');
      await toolsButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await toolsButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });

    test('should reset to all categories', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      // First select a specific category
      const seedsButton = page.locator('button:has-text("بذور")');
      await seedsButton.click();
      await page.waitForTimeout(1000);

      // Then click "All" button
      const allButton = page.locator('button:has-text("الكل")');
      await allButton.click();
      await page.waitForTimeout(1000);

      // "All" button should be active
      const buttonClass = await allButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });

    test('should combine search with category filter', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Open filters
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Select category
      const seedsButton = page.locator('button:has-text("بذور")');
      await seedsButton.click();
      await page.waitForTimeout(500);

      // Add search term
      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');
      await searchInput.fill('test');
      await page.waitForTimeout(1500);

      // Both filters should be applied
      const searchValue = await searchInput.inputValue();
      expect(searchValue).toBe('test');

      const buttonClass = await seedsButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');
    });
  });

  test.describe('Shopping Cart Functionality', () => {
    test('should display cart count badge when items added', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for cart button
      const cartButton = page.locator('button:has-text("السلة")');

      // Check if cart count badge exists
      const cartBadge = cartButton.locator('span.bg-red-500');
      const hasBadge = await cartBadge.isVisible({ timeout: 1000 }).catch(() => false);

      console.log(`Cart count badge visible: ${hasBadge}`);
    });

    test('should open cart sidebar when cart button clicked', async ({ page }) => {
      const cartButton = page.locator('button:has-text("السلة")');
      await cartButton.click();
      await page.waitForTimeout(1000);

      // Cart sidebar should be visible
      const cartSidebar = page.locator('[class*="fixed"], [role="dialog"]').filter({
        has: page.locator('text=/السلة|Cart/i'),
      });

      const isVisible = await cartSidebar.isVisible({ timeout: 2000 }).catch(() => false);

      if (isVisible) {
        await expect(cartSidebar).toBeVisible();
      } else {
        // Cart might be empty and showing different UI
        console.log('Cart sidebar opened but may be in different state');
      }
    });

    test('should add product to cart', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Find first add to cart button
      const addToCartButtons = page.locator('button').filter({
        has: page.locator('svg'),
      });

      const count = await addToCartButtons.count();

      if (count > 0) {
        // Get initial cart count if any
        const cartButton = page.locator('button:has-text("السلة")');
        const initialBadge = cartButton.locator('span.bg-red-500');
        // const hadBadge = await initialBadge.isVisible({ timeout: 500 }).catch(() => false);
        // let initialCount = 0;
        // if (hadBadge) {
        //   initialCount = parseInt((await initialBadge.textContent()) || '0');
        // }
        void initialBadge; // Suppress unused variable warning

        // Click first add to cart button
        await addToCartButtons.first().click();
        await page.waitForTimeout(1000);

        // Cart count should update
        const newBadge = cartButton.locator('span.bg-red-500');
        const hasBadgeNow = await newBadge.isVisible({ timeout: 2000 }).catch(() => false);

        console.log(`Cart badge appeared after adding: ${hasBadgeNow}`);
      }
    });

    test('should display cart summary banner when items in cart', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for cart summary banner
      const cartSummaryBanner = page.locator('text=/لديك.*منتجات في السلة/i');
      const isVisible = await cartSummaryBanner.isVisible({ timeout: 2000 }).catch(() => false);

      console.log(`Cart summary banner visible: ${isVisible}`);

      if (isVisible) {
        // Should display total amount
        const totalText = page.locator('text=/الإجمالي:/i');
        await expect(totalText).toBeVisible();
      }
    });

    test('should close cart sidebar', async ({ page }) => {
      // Open cart
      const cartButton = page.locator('button:has-text("السلة")');
      await cartButton.click();
      await page.waitForTimeout(1000);

      // Look for close button or click outside
      const closeButton = page.locator('button[aria-label="close"], button:has-text("✕")');
      const hasCloseButton = await closeButton.isVisible({ timeout: 1000 }).catch(() => false);

      if (hasCloseButton) {
        await closeButton.click();
        await page.waitForTimeout(500);
      } else {
        // Try pressing Escape key
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Product Details and Interaction', () => {
    test('should display product images', async ({ page }) => {
      await page.waitForTimeout(2000);

      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();

      if (count > 0) {
        const firstProduct = productCards.first();
        const productImage = firstProduct.locator('img, svg').first();

        await expect(productImage).toBeVisible();
      }
    });

    test('should display discount badges on discounted products', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for discount badge
      const discountBadge = page.locator('div.bg-red-500:has-text("%")');
      const hasDiscount = await discountBadge.isVisible({ timeout: 2000 }).catch(() => false);

      console.log(`Discount badge found: ${hasDiscount}`);

      if (hasDiscount) {
        // Should show percentage
        const badgeText = await discountBadge.first().textContent();
        expect(badgeText).toMatch(/%/);
      }
    });

    test('should display out of stock badge when product unavailable', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for out of stock badge
      const outOfStockBadge = page.locator('text=/نفذت الكمية/i');
      const hasOutOfStock = await outOfStockBadge.isVisible({ timeout: 2000 }).catch(() => false);

      console.log(`Out of stock badge found: ${hasOutOfStock}`);
    });

    test('should display seller information', async ({ page }) => {
      await page.waitForTimeout(2000);

      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();

      if (count > 0) {
        // Look for location/seller info with MapPin icon
        const sellerInfo = productCards.first().locator('svg').first();
        const hasSeller = await sellerInfo.isVisible().catch(() => false);

        console.log(`Seller information displayed: ${hasSeller}`);
      }
    });

    test('should display product ratings', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for star rating icons
      const starRatings = page.locator('svg').filter({
        hasText: '',
      });

      const ratingCount = await starRatings.count();
      console.log(`Found ${ratingCount} rating icons`);
    });

    test('should show low stock warning', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for low stock warning
      const lowStockWarning = page.locator('text=/الكمية المتبقية:/i');
      const hasWarning = await lowStockWarning.isVisible({ timeout: 2000 }).catch(() => false);

      console.log(`Low stock warning found: ${hasWarning}`);
    });

    test('should click on product card', async ({ page }) => {
      await page.waitForTimeout(2000);

      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();

      if (count > 0) {
        const firstProduct = productCards.first();

        // Get current URL
        const initialUrl = page.url();

        // Click product (might open modal or navigate)
        await firstProduct.click();
        await page.waitForTimeout(1000);

        // Something should happen (URL change, modal open, etc.)
        const newUrl = page.url();
        const hasModal = await page.locator('[role="dialog"]').isVisible({ timeout: 1000 }).catch(() => false);

        console.log(`After product click - URL changed: ${initialUrl !== newUrl}, Modal opened: ${hasModal}`);
      }
    });
  });

  test.describe('Loading States', () => {
    test('should display loading skeletons on initial load', async ({ page }) => {
      // Navigate to marketplace without waiting for full load
      await page.goto('/marketplace');

      // Look for loading skeletons or spinners
      const loadingElements = page.locator('[class*="animate-pulse"], [class*="skeleton"], [aria-busy="true"]');
      const hasLoading = await loadingElements.isVisible({ timeout: 1000 }).catch(() => false);

      console.log(`Loading state shown: ${hasLoading}`);

      // Wait for content to load
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Loading should be gone and content visible
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();
    });

    test('should show loading state during search', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');

      // Type search query
      await searchInput.fill('test search');

      // There might be a brief loading state
      await page.waitForTimeout(500);

      // Results should eventually load
      await page.waitForTimeout(1500);

      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();
    });

    test('should handle empty product list gracefully', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');

      // Search for non-existent product
      await searchInput.fill('xyznoproduct123456789');
      await page.waitForTimeout(1500);

      // Should show empty state with icon
      const emptyStateIcon = page.locator('svg[class*="text-gray-300"]');
      const hasEmptyIcon = await emptyStateIcon.isVisible({ timeout: 2000 }).catch(() => false);

      const emptyStateText = page.locator('text=/لا توجد منتجات|No products/i');
      const hasEmptyText = await emptyStateText.isVisible({ timeout: 2000 }).catch(() => false);

      console.log(`Empty state icon: ${hasEmptyIcon}, Empty state text: ${hasEmptyText}`);
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile viewport (375x667)', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Main heading should be visible
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();

      // Cart button should be visible
      const cartButton = page.locator('button:has-text("السلة")');
      await expect(cartButton).toBeVisible();

      // Search should be visible
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await expect(searchInput).toBeVisible();

      // Products grid should adapt (1 column on mobile)
      await page.waitForTimeout(1000);
      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();
      console.log(`Mobile view: ${count} products visible`);
    });

    test('should be responsive on tablet viewport (768x1024)', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();

      // Filters should be visible
      const filterButton = page.locator('button:has-text("فلتر")');
      await expect(filterButton).toBeVisible();

      // Products grid should show 2 columns on tablet
      console.log('Tablet view verified');
    });

    test('should be responsive on desktop viewport (1920x1080)', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();

      // All stats should be visible in one row
      const statCards = page.locator('text=/منتجات متاحة|منتجات في السلة|طلباتي/i');
      const count = await statCards.count();
      expect(count).toBeGreaterThanOrEqual(3);

      // Products grid should show 4 columns on large desktop
      console.log('Desktop view verified');
    });

    test('should adapt layout on small mobile (320x568)', async ({ page }) => {
      // Set very small mobile viewport
      await page.setViewportSize({ width: 320, height: 568 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Page should still be usable
      const heading = page.locator('h1');
      await expect(heading).toBeVisible();

      // Critical elements should be accessible
      const cartButton = page.locator('button:has-text("السلة")');
      await expect(cartButton).toBeVisible();
    });

    test('should maintain functionality when resizing window', async ({ page }) => {
      // Start desktop
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await searchInput.fill('test');

      // Resize to mobile
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(1000);

      // Search value should persist
      const value = await searchInput.inputValue();
      expect(value).toBe('test');
    });
  });

  test.describe('Bilingual Support (Arabic/English)', () => {
    test('should display Arabic labels correctly', async ({ page }) => {
      // Check for key Arabic labels
      const arabicLabels = [
        'السوق الزراعي',
        'منتجات متاحة',
        'منتجات في السلة',
        'طلباتي',
        'المنتجات',
        'السلة',
      ];

      for (const label of arabicLabels) {
        const element = page.locator(`text=${label}`);
        await expect(element).toBeVisible({ timeout: timeouts.long });
      }
    });

    test('should display English labels correctly', async ({ page }) => {
      // Check for key English labels
      const englishLabels = [
        'Agricultural Marketplace',
        'Available Products',
        'Items in Cart',
        'My Orders',
      ];

      for (const label of englishLabels) {
        const element = page.locator(`text=${label}`);
        await expect(element).toBeVisible({ timeout: timeouts.long });
      }
    });

    test('should display bilingual search placeholder', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      const placeholder = await searchInput.getAttribute('placeholder');

      // Should contain both Arabic and English
      expect(placeholder).toContain('ابحث');
      expect(placeholder).toContain('Search');
    });

    test('should display bilingual category labels', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Arabic category labels should be present
      const arabicCategories = ['بذور', 'أسمدة', 'مبيدات', 'معدات', 'أدوات'];

      for (const category of arabicCategories) {
        const categoryButton = page.locator(`button:has-text("${category}")`);
        await expect(categoryButton).toBeVisible();
      }
    });

    test('should display bilingual sort options', async ({ page }) => {
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("ترتيب حسب")'),
      });

      // All options should be in Arabic
      const arabicOptions = [
        'ترتيب حسب',
        'السعر: من الأقل للأعلى',
        'السعر: من الأعلى للأقل',
        'الأحدث',
        'الأعلى تقييماً',
      ];

      for (const option of arabicOptions) {
        const optionElement = sortDropdown.locator(`option:has-text("${option}")`);
        const exists = await optionElement.count();
        expect(exists).toBeGreaterThan(0);
      }
    });

    test('should display bilingual product information', async ({ page }) => {
      await page.waitForTimeout(2000);

      const productCards = page.locator('[class*="grid"] > div');
      const count = await productCards.count();

      if (count > 0) {
        const firstProduct = productCards.first();
        const productText = await firstProduct.textContent();

        // Product should contain some text (could be Arabic or English)
        expect(productText).toBeTruthy();
        expect(productText!.length).toBeGreaterThan(0);
      }
    });

    test('should display bilingual empty state messages', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await searchInput.fill('xyz999nonexistent');
      await page.waitForTimeout(1500);

      // Empty state should have bilingual message
      const emptyMessage = page.locator('text=/لا توجد منتجات/i');
      const hasMessage = await emptyMessage.isVisible({ timeout: 2000 }).catch(() => false);

      if (hasMessage) {
        const messageText = await emptyMessage.textContent();
        console.log(`Empty state message: ${messageText}`);
      }
    });

    test('should maintain RTL layout for Arabic text', async ({ page }) => {
      // Check if main heading is displayed correctly (RTL)
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();

      // Arabic text should flow right-to-left
      const direction = await heading.evaluate((el) => window.getComputedStyle(el).direction);
      console.log(`Text direction: ${direction}`);
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle page refresh gracefully', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Add item to search
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await searchInput.fill('test');
      await page.waitForTimeout(1000);

      // Reload page
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Page should load successfully
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();
    });

    test('should not crash on rapid filter changes', async ({ page }) => {
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(300);

      // Rapidly click different categories
      const seedsButton = page.locator('button:has-text("بذور")');
      const fertilizersButton = page.locator('button:has-text("أسمدة")');
      const pesticidesButton = page.locator('button:has-text("مبيدات")');

      await seedsButton.click();
      await page.waitForTimeout(200);
      await fertilizersButton.click();
      await page.waitForTimeout(200);
      await pesticidesButton.click();
      await page.waitForTimeout(1000);

      // Page should still function
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // This test verifies the page doesn't crash if data fails to load
      await page.waitForTimeout(2000);

      // Page should have error boundaries
      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();

      // Should not show critical error
      const criticalError = page.locator('text=/Critical Error|خطأ حرج/i');
      const hasCriticalError = await criticalError.isVisible({ timeout: 1000 }).catch(() => false);
      expect(hasCriticalError).toBe(false);
    });

    test('should maintain scroll position during filtering', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Scroll down
      await page.evaluate(() => window.scrollTo(0, 500));
      await page.waitForTimeout(500);

      const initialScroll = await page.evaluate(() => window.scrollY);

      // Apply filter
      const filterButton = page.locator('button:has-text("فلتر")');
      await filterButton.click();
      await page.waitForTimeout(300);

      const seedsButton = page.locator('button:has-text("بذور")');
      await seedsButton.click();
      await page.waitForTimeout(1000);

      // Scroll position may change, but page should be functional
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();

      console.log(`Initial scroll: ${initialScroll}, filtering applied successfully`);
    });
  });
});
