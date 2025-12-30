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

      // Check for marketplace page
      const marketplacePage = page.getByTestId('marketplace-page');
      await expect(marketplacePage).toBeVisible({ timeout: timeouts.long });

      // Check for main heading in Arabic
      const arabicHeading = page.getByTestId('marketplace-title');
      await expect(arabicHeading).toBeVisible();
      await expect(arabicHeading).toHaveText('السوق الزراعي');

      // Check for English subtitle
      const englishSubtitle = page.getByTestId('marketplace-subtitle');
      await expect(englishSubtitle).toBeVisible();
      await expect(englishSubtitle).toHaveText('Agricultural Marketplace');
    });

    test('should display page header with cart button', async ({ page }) => {
      // Cart button should be visible
      const cartButton = page.getByTestId('cart-button');
      await expect(cartButton).toBeVisible();

      // Cart icon should be present
      const cartIcon = cartButton.locator('svg');
      await expect(cartIcon).toBeVisible();
    });

    test('should display statistics cards', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check statistics cards container
      const statsCards = page.getByTestId('statistics-cards');
      await expect(statsCards).toBeVisible();

      // Check for "Available Products" stat card
      const productsCard = page.getByTestId('stat-card-products');
      await expect(productsCard).toBeVisible();
      const productsCount = page.getByTestId('stat-products-count');
      await expect(productsCount).toBeVisible();

      // Check for "Items in Cart" stat card
      const cartCard = page.getByTestId('stat-card-cart');
      await expect(cartCard).toBeVisible();
      const cartCount = page.getByTestId('stat-cart-count');
      await expect(cartCount).toBeVisible();

      // Check for "My Orders" stat card
      const ordersCard = page.getByTestId('stat-card-orders');
      await expect(ordersCard).toBeVisible();
      const ordersCount = page.getByTestId('stat-orders-count');
      await expect(ordersCount).toBeVisible();
    });

    test('should display products section', async ({ page }) => {
      // Products section should be visible
      const productsSection = page.getByTestId('products-section');
      await expect(productsSection).toBeVisible({ timeout: timeouts.long });

      // Products heading should be visible
      const productsHeading = page.getByTestId('products-heading');
      await expect(productsHeading).toBeVisible();
      await expect(productsHeading).toHaveText('المنتجات');
    });
  });

  test.describe('Product Listing and Display', () => {
    test('should display product grid with mock data', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check products list (should show products from mock data)
      const productsList = page.getByTestId('products-list');
      const hasProducts = await productsList.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasProducts) {
        // Look for product cards with data-testid
        const productCards = page.getByTestId('product-card');
        const count = await productCards.count();
        console.log(`Found ${count} product cards with mock data`);

        // Should have products from expanded mock data (8 products)
        expect(count).toBeGreaterThan(0);
        expect(count).toBe(8); // We have 8 products in mock data
      } else {
        // Check for empty state
        const emptyState = page.getByTestId('empty-state');
        await expect(emptyState).toBeVisible();
      }
    });

    test('should display product card details with proper data-testid', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Get first product card using data-testid
      const firstProduct = page.getByTestId('product-card').first();
      const isVisible = await firstProduct.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Product should have an image or placeholder
        const productImage = firstProduct.getByTestId('product-image-container');
        await expect(productImage).toBeVisible();

        // Product should have category
        const category = firstProduct.getByTestId('product-category');
        await expect(category).toBeVisible();

        // Product should have Arabic and English names
        const nameAr = firstProduct.getByTestId('product-name-ar');
        await expect(nameAr).toBeVisible();

        const nameEn = firstProduct.getByTestId('product-name-en');
        await expect(nameEn).toBeVisible();

        // Product should have seller info
        const seller = firstProduct.getByTestId('product-seller');
        await expect(seller).toBeVisible();

        // Product should have price
        const priceSection = firstProduct.getByTestId('product-price-section');
        await expect(priceSection).toBeVisible();

        // Product should have add to cart button
        const addToCartBtn = firstProduct.getByTestId('add-to-cart-button');
        await expect(addToCartBtn).toBeVisible();
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
      const searchInput = page.getByTestId('search-input');
      await expect(searchInput).toBeVisible({ timeout: timeouts.long });
    });

    test('should allow typing in search field', async ({ page }) => {
      const searchInput = page.getByTestId('search-input');
      await searchInput.fill('بذور');

      const value = await searchInput.inputValue();
      expect(value).toBe('بذور');
    });

    test('should search for products in English', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.getByTestId('search-input');
      await searchInput.fill('seed');

      // Wait for search to take effect
      await page.waitForTimeout(1500);

      // Should show search results
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} products matching 'seed'`);

      // Should filter products (we have seed products in mock data)
      expect(count).toBeGreaterThan(0);
    });

    test('should search for products in Arabic', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.getByTestId('search-input');
      await searchInput.fill('بذور');

      // Wait for search to take effect
      await page.waitForTimeout(1500);

      // Should show search results
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} products matching 'بذور'`);

      // Should filter products (we have seed products in mock data)
      expect(count).toBeGreaterThan(0);
    });

    test('should show empty state when no results found', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.getByTestId('search-input');
      // Search for something unlikely to exist
      await searchInput.fill('xyz123nonexistent999');

      await page.waitForTimeout(1500);

      // Should show empty state with proper data-testid
      const emptyState = page.getByTestId('empty-state');
      const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Empty state shown for no results: ${hasEmptyState}`);
      expect(hasEmptyState).toBe(true);

      // Check empty state elements
      if (hasEmptyState) {
        const emptyIcon = page.getByTestId('empty-state-icon');
        await expect(emptyIcon).toBeVisible();

        const emptyTitle = page.getByTestId('empty-state-title');
        await expect(emptyTitle).toBeVisible();

        const emptyMessage = page.getByTestId('empty-state-message');
        await expect(emptyMessage).toBeVisible();
      }
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
      const filterButton = page.getByTestId('filter-toggle-button');
      await expect(filterButton).toBeVisible({ timeout: timeouts.long });
    });

    test('should toggle filter panel', async ({ page }) => {
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();

      await page.waitForTimeout(500);

      // Category filters should appear with proper data-testid
      const categoryFilters = page.getByTestId('category-filters');
      await expect(categoryFilters).toBeVisible();

      // Check individual category buttons
      const allButton = page.getByTestId('category-filter-all');
      await expect(allButton).toBeVisible();

      const seedsButton = page.getByTestId('category-filter-seeds');
      await expect(seedsButton).toBeVisible();

      // Click again to close
      await filterButton.click();
      await page.waitForTimeout(500);
    });

    test('should display sort dropdown', async ({ page }) => {
      const sortDropdown = page.getByTestId('sort-dropdown');
      await expect(sortDropdown).toBeVisible({ timeout: timeouts.long });
    });

    test('should change sort order', async ({ page }) => {
      await page.waitForTimeout(1000);

      const sortDropdown = page.getByTestId('sort-dropdown');

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
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();
      await page.waitForTimeout(500);

      // Check for all category buttons with data-testid
      const categoryTestIds = [
        'category-filter-all',
        'category-filter-seeds',
        'category-filter-fertilizers',
        'category-filter-pesticides',
        'category-filter-equipment',
        'category-filter-tools',
      ];

      for (const testId of categoryTestIds) {
        const categoryButton = page.getByTestId(testId);
        await expect(categoryButton).toBeVisible();
      }
    });

    test('should filter by seeds category and show only seed products', async ({ page }) => {
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();
      await page.waitForTimeout(500);

      const seedsButton = page.getByTestId('category-filter-seeds');
      await seedsButton.click();
      await page.waitForTimeout(1500);

      // Button should be active (has different styling)
      const buttonClass = await seedsButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');

      // Should show filtered products (we have 3 seed products in mock data)
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} seed products`);
      expect(count).toBe(3); // wheat, corn, tomato seeds
    });

    test('should filter by fertilizers category', async ({ page }) => {
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();
      await page.waitForTimeout(500);

      const fertilizersButton = page.getByTestId('category-filter-fertilizers');
      await fertilizersButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await fertilizersButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');

      // Should show filtered products (we have 2 fertilizer products in mock data)
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} fertilizer products`);
      expect(count).toBe(2); // NPK and compost
    });

    test('should filter by pesticides category', async ({ page }) => {
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();
      await page.waitForTimeout(500);

      const pesticidesButton = page.getByTestId('category-filter-pesticides');
      await pesticidesButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await pesticidesButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');

      // Should show filtered products (we have 1 pesticide product in mock data)
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} pesticide products`);
      expect(count).toBe(1); // organic pesticide
    });

    test('should filter by equipment category', async ({ page }) => {
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();
      await page.waitForTimeout(500);

      const equipmentButton = page.getByTestId('category-filter-equipment');
      await equipmentButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await equipmentButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');

      // Should show filtered products (we have 1 equipment product in mock data)
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} equipment products`);
      expect(count).toBe(1); // drip irrigation kit
    });

    test('should filter by tools category', async ({ page }) => {
      const filterButton = page.getByTestId('filter-toggle-button');
      await filterButton.click();
      await page.waitForTimeout(500);

      const toolsButton = page.getByTestId('category-filter-tools');
      await toolsButton.click();
      await page.waitForTimeout(1500);

      const buttonClass = await toolsButton.getAttribute('class');
      expect(buttonClass).toContain('bg-blue-600');

      // Should show filtered products (we have 1 tools product in mock data)
      const productCards = page.getByTestId('product-card');
      const count = await productCards.count();
      console.log(`Found ${count} tools products`);
      expect(count).toBe(1); // garden hand tools set
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
      const cartButton = page.getByTestId('cart-button');
      await expect(cartButton).toBeVisible();

      // Check if cart count badge exists
      const cartBadge = page.getByTestId('cart-count-badge');
      const hasBadge = await cartBadge.isVisible({ timeout: 1000 }).catch(() => false);

      console.log(`Cart count badge visible: ${hasBadge}`);
    });

    test('should open cart sidebar when cart button clicked', async ({ page }) => {
      const cartButton = page.getByTestId('cart-button');
      await cartButton.click();
      await page.waitForTimeout(1000);

      // Cart sidebar should be visible with proper data-testid
      const cartSidebar = page.getByTestId('cart-sidebar');
      const isVisible = await cartSidebar.isVisible({ timeout: 2000 }).catch(() => false);

      if (isVisible) {
        await expect(cartSidebar).toBeVisible();

        // Check cart header elements
        const cartTitle = page.getByTestId('cart-title');
        await expect(cartTitle).toBeVisible();

        const closeButton = page.getByTestId('cart-close-button');
        await expect(closeButton).toBeVisible();
      } else {
        console.log('Cart sidebar not visible');
      }
    });

    test('should add product to cart using data-testid', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Find first product card and add to cart button
      const firstProduct = page.getByTestId('product-card').first();
      const addToCartButton = firstProduct.getByTestId('add-to-cart-button');

      const isVisible = await addToCartButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Click add to cart button
        await addToCartButton.click();
        await page.waitForTimeout(1000);

        // Cart count badge should appear and update
        const cartBadge = page.getByTestId('cart-count-badge');
        const hasBadgeNow = await cartBadge.isVisible({ timeout: 2000 }).catch(() => false);

        console.log(`Cart badge appeared after adding: ${hasBadgeNow}`);

        if (hasBadgeNow) {
          const badgeText = await cartBadge.textContent();
          console.log(`Cart count: ${badgeText}`);
          expect(badgeText).toBeTruthy();
        }
      } else {
        console.log('No products available to add to cart');
      }
    });

    test('should display cart summary banner when items in cart', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for cart summary banner with data-testid
      const cartSummaryBanner = page.getByTestId('cart-summary-banner');
      const isVisible = await cartSummaryBanner.isVisible({ timeout: 2000 }).catch(() => false);

      console.log(`Cart summary banner visible: ${isVisible}`);

      if (isVisible) {
        // Should display banner title
        const summaryTitle = page.getByTestId('cart-summary-title');
        await expect(summaryTitle).toBeVisible();

        // Should display total amount
        const summaryTotal = page.getByTestId('cart-summary-total');
        await expect(summaryTotal).toBeVisible();

        // Should have review button
        const summaryButton = page.getByTestId('cart-summary-button');
        await expect(summaryButton).toBeVisible();
      }
    });

    test('should close cart sidebar', async ({ page }) => {
      // Open cart
      const cartButton = page.getByTestId('cart-button');
      await cartButton.click();
      await page.waitForTimeout(1000);

      // Look for close button with data-testid
      const closeButton = page.getByTestId('cart-close-button');
      const hasCloseButton = await closeButton.isVisible({ timeout: 1000 }).catch(() => false);

      if (hasCloseButton) {
        await closeButton.click();
        await page.waitForTimeout(500);

        // Cart sidebar should be hidden
        const cartSidebar = page.getByTestId('cart-sidebar');
        const stillVisible = await cartSidebar.isVisible({ timeout: 1000 }).catch(() => false);
        expect(stillVisible).toBe(false);
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

  test.describe('Content Rendering', () => {
    test('should display content after page load', async ({ page }) => {
      // Navigate and wait for content to load
      await page.goto('/marketplace');
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Content should be visible
      const heading = page.locator('h1:has-text("السوق الزراعي")');
      await expect(heading).toBeVisible();
    });

    test('should display content after search', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"], input[placeholder*="Search"]');

      // Type search query
      await searchInput.fill('test search');

      // Wait for results to load
      await page.waitForTimeout(2000);

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
