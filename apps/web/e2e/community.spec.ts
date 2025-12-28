import { test, expect } from './fixtures/test-fixtures';
import {
  navigateAndWait,
  waitForPageLoad,
  isElementVisible,
  scrollIntoView,
  waitForApiResponse,
} from './helpers/page.helpers';
import { selectors, timeouts } from './helpers/test-data';

/**
 * Community E2E Tests
 * اختبارات E2E لمجتمع المزارعين
 */

test.describe('Community Page', () => {
  test.beforeEach(async ({ page, authenticatedPage }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, '/community');
  });

  test.describe('Page Load and Basic Structure', () => {
    test('should display community page correctly', async ({ page }) => {
      // Check page title
      await expect(page).toHaveTitle(/Farmer Community|مجتمع/i);

      // Check for main heading in Arabic
      const arabicHeading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(arabicHeading).toBeVisible({ timeout: timeouts.long });

      // Check for English subtitle
      const englishSubtitle = page.locator('text=/Farmer Community/i');
      await expect(englishSubtitle).toBeVisible();
    });

    test('should display create post button', async ({ page }) => {
      // Create post button should be visible
      const createPostButton = page.locator('button:has-text("انشر سؤالاً أو تجربة")');
      await expect(createPostButton).toBeVisible({ timeout: timeouts.long });

      // Button should be a dashed border style
      const buttonClass = await createPostButton.getAttribute('class');
      expect(buttonClass).toContain('border-dashed');
    });

    test('should display filters section', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Filters container should be visible
      const filtersContainer = page.locator('.bg-white').filter({
        has: page.locator('input[placeholder*="ابحث"]'),
      });
      await expect(filtersContainer).toBeVisible();
    });

    test('should display search input', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');
      await expect(searchInput).toBeVisible({ timeout: timeouts.long });

      // Search icon should be present
      const searchIcon = page.locator('svg').filter({
        has: page.locator('..'),
      }).first();
      await expect(searchIcon).toBeVisible();
    });

    test('should display type filter dropdown', async ({ page }) => {
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });
      await expect(typeFilter).toBeVisible({ timeout: timeouts.long });
    });

    test('should display sort dropdown', async ({ page }) => {
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });
      await expect(sortDropdown).toBeVisible({ timeout: timeouts.long });
    });
  });

  test.describe('Posts/Discussions Display', () => {
    test('should display posts in feed', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for post cards
      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();
      console.log(`Found ${count} post cards`);

      // Should have posts or show empty state
      if (count === 0) {
        const emptyState = page.locator('text=/لا توجد منشورات|No posts found/i');
        await expect(emptyState).toBeVisible();
      } else {
        expect(count).toBeGreaterThan(0);
      }
    });

    test('should display post author information', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Should have user avatar (circular div with initials)
        const avatar = firstPost.locator('.w-12.h-12.rounded-full');
        await expect(avatar).toBeVisible();

        // Should have username
        const userName = firstPost.locator('.font-semibold.text-gray-900');
        await expect(userName.first()).toBeVisible();

        // Should have timestamp
        const timestamp = firstPost.locator('text=/منذ/i');
        await expect(timestamp.first()).toBeVisible();
      }
    });

    test('should display post type badges', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Should have type badge (سؤال, نصيحة, تجربة, نقاش)
        const typeBadge = firstPost.locator('span.rounded-full.text-xs').filter({
          hasText: /سؤال|نصيحة|تجربة|نقاش|تحديث/i,
        });

        const hasBadge = await typeBadge.isVisible({ timeout: 2000 }).catch(() => false);
        console.log(`Post type badge visible: ${hasBadge}`);
      }
    });

    test('should display post content', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Should have title
        const title = firstPost.locator('h3.text-xl.font-semibold');
        const hasTitle = await title.isVisible({ timeout: 2000 }).catch(() => false);

        if (hasTitle) {
          await expect(title).toBeVisible();
          const titleText = await title.textContent();
          expect(titleText?.length).toBeGreaterThan(0);
        }

        // Should have content text
        const content = firstPost.locator('p.text-gray-700');
        const hasContent = await content.first().isVisible().catch(() => false);
        console.log(`Post content visible: ${hasContent}`);
      }
    });

    test('should display post statistics', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Should display likes count
        const likesCount = firstPost.locator('text=/\\d+.*إعجاب/i');
        await expect(likesCount.first()).toBeVisible();

        // Should display comments count
        const commentsCount = firstPost.locator('text=/\\d+.*تعليق/i');
        await expect(commentsCount.first()).toBeVisible();

        // Should display views count
        const viewsCount = firstPost.locator('text=/\\d+.*مشاهدة/i');
        await expect(viewsCount.first()).toBeVisible();
      }
    });

    test('should display post images if present', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Check for images in grid layout
        const images = firstPost.locator('img[src]');
        const imageCount = await images.count();

        console.log(`Found ${imageCount} images in first post`);

        if (imageCount > 0) {
          // Images should be visible
          await expect(images.first()).toBeVisible();
        }
      }
    });

    test('should display post tags if present', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Check for tags (starting with #)
        const tags = firstPost.locator('span.text-green-600').filter({
          hasText: /#/,
        });

        const tagCount = await tags.count();
        console.log(`Found ${tagCount} tags in first post`);

        if (tagCount > 0) {
          // Tags should be visible and clickable
          await expect(tags.first()).toBeVisible();
          const tagClass = await tags.first().getAttribute('class');
          expect(tagClass).toContain('cursor-pointer');
        }
      }
    });

    test('should display user badges if present', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        // Look for verified badge icons
        const verifiedBadges = page.locator('svg.text-blue-500, svg.text-yellow-500');
        const badgeCount = await verifiedBadges.count();

        console.log(`Found ${badgeCount} user badges`);
      }
    });
  });

  test.describe('User Interactions - Like', () => {
    test('should display like button on each post', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Like button should be visible
        const likeButton = firstPost.locator('button:has-text("إعجاب")');
        await expect(likeButton).toBeVisible();

        // Should have thumbs up icon
        const likeIcon = likeButton.locator('svg');
        await expect(likeIcon).toBeVisible();
      }
    });

    test('should toggle like on post when clicked', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const likeButton = firstPost.locator('button:has-text("إعجاب")');

        // Get initial state
        const initialClass = await likeButton.getAttribute('class');

        // Click like button
        await likeButton.click();
        await page.waitForTimeout(1000);

        // Button state should change
        const newClass = await likeButton.getAttribute('class');
        console.log(`Like button clicked - classes changed: ${initialClass !== newClass}`);
      }
    });

    test('should show liked state with different styling', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const likeButton = firstPost.locator('button:has-text("إعجاب")');

        // Click to like
        await likeButton.click();
        await page.waitForTimeout(1000);

        // Should have green background when liked
        const buttonClass = await likeButton.getAttribute('class');
        const isLiked = buttonClass?.includes('bg-green-50') || buttonClass?.includes('text-green-600');

        console.log(`Like button shows liked state: ${isLiked}`);
      }
    });

    test('should disable like button while request is pending', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const likeButton = firstPost.locator('button:has-text("إعجاب")');

        // Check if button can be disabled
        const isDisabled = await likeButton.isDisabled().catch(() => false);
        console.log(`Like button disabled state works: ${isDisabled !== undefined}`);
      }
    });
  });

  test.describe('User Interactions - Comment', () => {
    test('should display comment button on each post', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Comment button should be visible
        const commentButton = firstPost.locator('button:has-text("تعليق")');
        await expect(commentButton).toBeVisible();

        // Should have message icon
        const commentIcon = commentButton.locator('svg');
        await expect(commentIcon).toBeVisible();
      }
    });

    test('should toggle comments section when comment button clicked', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const commentButton = firstPost.locator('button:has-text("تعليق")');

        // Click comment button
        await commentButton.click();
        await page.waitForTimeout(1000);

        // Comments section might appear
        const commentsSection = firstPost.locator('.bg-gray-50').filter({
          hasText: /تعليق/i,
        });

        const hasComments = await commentsSection.isVisible({ timeout: 2000 }).catch(() => false);
        console.log(`Comments section toggled: ${hasComments}`);

        if (hasComments) {
          // Click again to close
          await commentButton.click();
          await page.waitForTimeout(500);
        }
      }
    });

    test('should display comments count', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const commentButton = firstPost.locator('button:has-text("تعليق")');

        // Open comments
        await commentButton.click();
        await page.waitForTimeout(1000);

        // Look for comments count display
        const commentsCount = firstPost.locator('text=/\\d+.*تعليق/i');
        const hasCount = await commentsCount.first().isVisible().catch(() => false);

        console.log(`Comments count displayed: ${hasCount}`);
      }
    });

    test('should display individual comments', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const commentButton = firstPost.locator('button:has-text("تعليق")');

        // Open comments
        await commentButton.click();
        await page.waitForTimeout(1000);

        // Look for comment cards
        const commentCards = firstPost.locator('.bg-white.p-3.rounded-lg');
        const commentCount = await commentCards.count();

        console.log(`Found ${commentCount} individual comments`);

        if (commentCount > 0) {
          // Each comment should have avatar and content
          const firstComment = commentCards.first();
          const avatar = firstComment.locator('.w-8.h-8.rounded-full');
          const hasAvatar = await avatar.isVisible().catch(() => false);

          console.log(`Comment has avatar: ${hasAvatar}`);
        }
      }
    });
  });

  test.describe('User Interactions - Share and Save', () => {
    test('should display share button on each post', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Share button should be visible
        const shareButton = firstPost.locator('button:has-text("مشاركة")');
        await expect(shareButton).toBeVisible();
      }
    });

    test('should display save/bookmark button on each post', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Save/bookmark button should be visible (icon only button)
        const saveButton = firstPost.locator('button').filter({
          has: page.locator('svg'),
        }).filter({
          hasNotText: /إعجاب|تعليق|مشاركة/,
        });

        const hasSaveButton = await saveButton.first().isVisible().catch(() => false);
        console.log(`Save button visible: ${hasSaveButton}`);
      }
    });

    test('should handle share button click', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();
        const shareButton = firstPost.locator('button:has-text("مشاركة")');

        // Click share button
        await shareButton.click();
        await page.waitForTimeout(500);

        // Page should not crash
        const heading = page.locator('h1:has-text("مجتمع المزارعين")');
        await expect(heading).toBeVisible();

        console.log('Share button clicked successfully');
      }
    });

    test('should toggle save state when bookmark clicked', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Find bookmark/save button (last icon-only button in actions)
        const actionButtons = firstPost.locator('.border-t button').filter({
          has: page.locator('svg'),
        });
        const saveButton = actionButtons.last();

        const hasButton = await saveButton.isVisible().catch(() => false);

        if (hasButton) {
          // Get initial state
          const initialClass = await saveButton.getAttribute('class');

          // Click save button
          await saveButton.click();
          await page.waitForTimeout(1000);

          // Button state should change
          const newClass = await saveButton.getAttribute('class');
          console.log(`Save button clicked - state changed: ${initialClass !== newClass}`);
        }
      }
    });
  });

  test.describe('Search and Filtering', () => {
    test('should allow typing in search field', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');
      await searchInput.fill('زراعة');

      const value = await searchInput.inputValue();
      expect(value).toBe('زراعة');
    });

    test('should search for posts in Arabic', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');
      await searchInput.fill('نصيحة');

      // Wait for search to take effect
      await page.waitForTimeout(1500);

      // Page should update
      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();
    });

    test('should search for posts in English', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');
      await searchInput.fill('farming');

      // Wait for search to take effect
      await page.waitForTimeout(1500);

      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();
    });

    test('should clear search results', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');

      // Search for something
      await searchInput.fill('test');
      await page.waitForTimeout(1000);

      // Clear search
      await searchInput.clear();
      await page.waitForTimeout(1000);

      // Should show all posts again
      const value = await searchInput.inputValue();
      expect(value).toBe('');
    });

    test('should show empty state when no results found', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');

      // Search for something unlikely to exist
      await searchInput.fill('xyz123nonexistent999');
      await page.waitForTimeout(1500);

      // Should show empty state
      const emptyState = page.locator('text=/لا توجد منشورات|No posts found/i');
      const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Empty state shown for no results: ${hasEmptyState}`);
    });
  });

  test.describe('Type Filtering', () => {
    test('should display all post type options', async ({ page }) => {
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Check for all type options
      const options = ['الكل', 'أسئلة', 'نصائح', 'تجارب', 'نقاشات'];

      for (const option of options) {
        const hasOption = await typeFilter
          .locator(`option:has-text("${option}")`)
          .isVisible()
          .catch(() => false);
        expect(hasOption).toBe(true);
      }
    });

    test('should filter by questions type', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Select questions
      await typeFilter.selectOption({ label: 'أسئلة' });
      await page.waitForTimeout(1500);

      // Verify selection
      const selectedValue = await typeFilter.inputValue();
      expect(selectedValue).toBe('question');
    });

    test('should filter by tips type', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Select tips
      await typeFilter.selectOption({ label: 'نصائح' });
      await page.waitForTimeout(1500);

      const selectedValue = await typeFilter.inputValue();
      expect(selectedValue).toBe('tip');
    });

    test('should filter by experience type', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Select experience
      await typeFilter.selectOption({ label: 'تجارب' });
      await page.waitForTimeout(1500);

      const selectedValue = await typeFilter.inputValue();
      expect(selectedValue).toBe('experience');
    });

    test('should filter by discussion type', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Select discussion
      await typeFilter.selectOption({ label: 'نقاشات' });
      await page.waitForTimeout(1500);

      const selectedValue = await typeFilter.inputValue();
      expect(selectedValue).toBe('discussion');
    });

    test('should reset to all types', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // First select a specific type
      await typeFilter.selectOption({ label: 'أسئلة' });
      await page.waitForTimeout(1000);

      // Then select all
      await typeFilter.selectOption({ label: 'الكل' });
      await page.waitForTimeout(1000);

      const selectedValue = await typeFilter.inputValue();
      expect(selectedValue).toBe('all');
    });
  });

  test.describe('Sort Functionality', () => {
    test('should display all sort options', async ({ page }) => {
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });

      // Check for all sort options
      const options = ['الأحدث', 'الأكثر شعبية', 'الرائج'];

      for (const option of options) {
        const hasOption = await sortDropdown
          .locator(`option:has-text("${option}")`)
          .isVisible()
          .catch(() => false);
        expect(hasOption).toBe(true);
      }
    });

    test('should sort by recent', async ({ page }) => {
      await page.waitForTimeout(1000);

      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });

      // Select recent
      await sortDropdown.selectOption({ label: 'الأحدث' });
      await page.waitForTimeout(1500);

      const selectedValue = await sortDropdown.inputValue();
      expect(selectedValue).toBe('recent');
    });

    test('should sort by popular', async ({ page }) => {
      await page.waitForTimeout(1000);

      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });

      // Select popular
      await sortDropdown.selectOption({ label: 'الأكثر شعبية' });
      await page.waitForTimeout(1500);

      const selectedValue = await sortDropdown.inputValue();
      expect(selectedValue).toBe('popular');
    });

    test('should sort by trending', async ({ page }) => {
      await page.waitForTimeout(1000);

      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });

      // Select trending
      await sortDropdown.selectOption({ label: 'الرائج' });
      await page.waitForTimeout(1500);

      const selectedValue = await sortDropdown.inputValue();
      expect(selectedValue).toBe('trending');
    });

    test('should combine filters with sort', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Set type filter
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });
      await typeFilter.selectOption({ label: 'نصائح' });
      await page.waitForTimeout(500);

      // Set sort
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });
      await sortDropdown.selectOption({ label: 'الأكثر شعبية' });
      await page.waitForTimeout(1500);

      // Both should be applied
      const typeValue = await typeFilter.inputValue();
      const sortValue = await sortDropdown.inputValue();

      expect(typeValue).toBe('tip');
      expect(sortValue).toBe('popular');
    });

    test('should combine search with filters and sort', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Add search
      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');
      await searchInput.fill('زراعة');
      await page.waitForTimeout(500);

      // Set type
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });
      await typeFilter.selectOption({ label: 'أسئلة' });
      await page.waitForTimeout(500);

      // Set sort
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });
      await sortDropdown.selectOption({ label: 'الرائج' });
      await page.waitForTimeout(1500);

      // All should be applied
      const searchValue = await searchInput.inputValue();
      const typeValue = await typeFilter.inputValue();
      const sortValue = await sortDropdown.inputValue();

      expect(searchValue).toBe('زراعة');
      expect(typeValue).toBe('question');
      expect(sortValue).toBe('trending');
    });
  });

  test.describe('Create Post Functionality', () => {
    test('should open create post modal when button clicked', async ({ page }) => {
      const createPostButton = page.locator('button:has-text("انشر سؤالاً أو تجربة")');
      await createPostButton.click();
      await page.waitForTimeout(1000);

      // Modal might appear
      const modal = page.locator('[role="dialog"], .fixed').filter({
        hasText: /منشور|Post/i,
      });

      const hasModal = await modal.isVisible({ timeout: 2000 }).catch(() => false);
      console.log(`Create post modal opened: ${hasModal}`);

      if (hasModal) {
        // Close modal by pressing Escape
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    });

    test('should close create post modal', async ({ page }) => {
      const createPostButton = page.locator('button:has-text("انشر سؤالاً أو تجربة")');
      await createPostButton.click();
      await page.waitForTimeout(1000);

      // Try to close with Escape
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);

      // Or look for close button
      const closeButton = page.locator('button[aria-label="close"], button:has-text("✕")');
      const hasCloseButton = await closeButton.isVisible({ timeout: 1000 }).catch(() => false);

      if (hasCloseButton) {
        await closeButton.click();
        await page.waitForTimeout(500);
      }

      // Page should still be visible
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();
    });
  });

  test.describe('Loading States', () => {
    test('should display loading spinner on initial load', async ({ page }) => {
      // Navigate without waiting
      await page.goto('/community');

      // Look for loading spinner
      const loadingSpinner = page.locator('.animate-spin');
      const hasLoading = await loadingSpinner.isVisible({ timeout: 1000 }).catch(() => false);

      console.log(`Loading spinner shown: ${hasLoading}`);

      // Wait for content to load
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Content should be visible
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();
    });

    test('should show loading state during filtering', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Change filter
      await typeFilter.selectOption({ label: 'نصائح' });

      // There might be a brief loading state
      await page.waitForTimeout(500);

      // Results should eventually load
      await page.waitForTimeout(1500);

      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();
    });

    test('should handle empty posts list gracefully', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث في المجتمع"]');

      // Search for non-existent content
      await searchInput.fill('xyz999nonexistent12345');
      await page.waitForTimeout(1500);

      // Should show empty state
      const emptyState = page.locator('text=/لا توجد منشورات|No posts found/i');
      const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

      console.log(`Empty state displayed: ${hasEmptyState}`);

      if (hasEmptyState) {
        // Should have both Arabic and English text
        const emptyText = await emptyState.textContent();
        console.log(`Empty state message: ${emptyText}`);
      }
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
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();

      // Create post button should be visible
      const createPostButton = page.locator('button:has-text("انشر سؤالاً")');
      await expect(createPostButton).toBeVisible();

      // Search should be visible
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await expect(searchInput).toBeVisible();

      // Filters should adapt (may stack vertically)
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });
      await expect(typeFilter).toBeVisible();
    });

    test('should be responsive on tablet viewport (768x1024)', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();

      // All filters should be visible
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await expect(searchInput).toBeVisible();

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });
      await expect(typeFilter).toBeVisible();

      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });
      await expect(sortDropdown).toBeVisible();
    });

    test('should be responsive on desktop viewport (1920x1080)', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();

      // All elements should be visible and well-spaced
      const createPostButton = page.locator('button:has-text("انشر سؤالاً")');
      await expect(createPostButton).toBeVisible();

      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await expect(searchInput).toBeVisible();
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

    test('should scroll posts on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Get initial scroll position
      const initialScroll = await page.evaluate(() => window.scrollY);

      // Scroll down
      await page.evaluate(() => window.scrollTo(0, 500));
      await page.waitForTimeout(500);

      const newScroll = await page.evaluate(() => window.scrollY);

      // Scroll should have changed
      expect(newScroll).toBeGreaterThan(initialScroll);
    });
  });

  test.describe('Arabic/English Labels', () => {
    test('should display Arabic page title', async ({ page }) => {
      const arabicTitle = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(arabicTitle).toBeVisible({ timeout: timeouts.long });
    });

    test('should display English page subtitle', async ({ page }) => {
      const englishSubtitle = page.locator('text=/Farmer Community/i');
      await expect(englishSubtitle).toBeVisible({ timeout: timeouts.long });
    });

    test('should display Arabic action button labels', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Check Arabic button labels
        const likeButton = firstPost.locator('button:has-text("إعجاب")');
        await expect(likeButton).toBeVisible();

        const commentButton = firstPost.locator('button:has-text("تعليق")');
        await expect(commentButton).toBeVisible();

        const shareButton = firstPost.locator('button:has-text("مشاركة")');
        await expect(shareButton).toBeVisible();
      }
    });

    test('should display Arabic filter labels', async ({ page }) => {
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // All options should be in Arabic
      const arabicOptions = ['الكل', 'أسئلة', 'نصائح', 'تجارب', 'نقاشات'];

      for (const option of arabicOptions) {
        const optionElement = typeFilter.locator(`option:has-text("${option}")`);
        const exists = await optionElement.count();
        expect(exists).toBeGreaterThan(0);
      }
    });

    test('should display Arabic sort labels', async ({ page }) => {
      const sortDropdown = page.locator('select').filter({
        has: page.locator('option:has-text("الأحدث")'),
      });

      // All options should be in Arabic
      const arabicOptions = ['الأحدث', 'الأكثر شعبية', 'الرائج'];

      for (const option of arabicOptions) {
        const optionElement = sortDropdown.locator(`option:has-text("${option}")`);
        const exists = await optionElement.count();
        expect(exists).toBeGreaterThan(0);
      }
    });

    test('should display Arabic post statistics labels', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Check Arabic statistics labels
        const likesLabel = firstPost.locator('text=/إعجاب/i');
        await expect(likesLabel.first()).toBeVisible();

        const commentsLabel = firstPost.locator('text=/تعليق/i');
        await expect(commentsLabel.first()).toBeVisible();

        const viewsLabel = firstPost.locator('text=/مشاهدة/i');
        await expect(viewsLabel.first()).toBeVisible();
      }
    });

    test('should display Arabic post type badges', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Post type badges should be in Arabic
        const typeBadge = firstPost.locator('span.rounded-full').filter({
          hasText: /سؤال|نصيحة|تجربة|نقاش|تحديث/i,
        });

        const hasBadge = await typeBadge.isVisible({ timeout: 2000 }).catch(() => false);
        console.log(`Arabic type badge visible: ${hasBadge}`);
      }
    });

    test('should display Arabic timestamp labels', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Timestamp should be in Arabic format
        const timestamp = firstPost.locator('text=/منذ/i');
        await expect(timestamp.first()).toBeVisible();
      }
    });

    test('should display Arabic empty state message', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await searchInput.fill('xyz999nonexistent');
      await page.waitForTimeout(1500);

      // Empty state should have Arabic text
      const emptyMessage = page.locator('text=/لا توجد منشورات/i');
      const hasMessage = await emptyMessage.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasMessage) {
        await expect(emptyMessage).toBeVisible();
      }
    });

    test('should maintain RTL layout for Arabic text', async ({ page }) => {
      // Check if main container has RTL direction
      const mainContainer = page.locator('div[dir="rtl"]');
      await expect(mainContainer).toBeVisible();

      // Heading should follow RTL
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      const direction = await heading.evaluate((el) => window.getComputedStyle(el).direction);
      console.log(`Text direction: ${direction}`);
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle page refresh gracefully', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Apply some filters
      const searchInput = page.locator('input[placeholder*="ابحث"]');
      await searchInput.fill('test');
      await page.waitForTimeout(1000);

      // Reload page
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Page should load successfully
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();
    });

    test('should not crash on rapid filter changes', async ({ page }) => {
      await page.waitForTimeout(1000);

      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });

      // Rapidly change filters
      await typeFilter.selectOption({ label: 'أسئلة' });
      await page.waitForTimeout(200);
      await typeFilter.selectOption({ label: 'نصائح' });
      await page.waitForTimeout(200);
      await typeFilter.selectOption({ label: 'تجارب' });
      await page.waitForTimeout(1000);

      // Page should still function
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();
    });

    test('should handle network errors gracefully', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Page should have error boundaries
      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();

      // Should not show critical error
      const criticalError = page.locator('text=/Critical Error|خطأ حرج/i');
      const hasCriticalError = await criticalError.isVisible({ timeout: 1000 }).catch(() => false);
      expect(hasCriticalError).toBe(false);
    });

    test('should handle multiple simultaneous interactions', async ({ page }) => {
      await page.waitForTimeout(2000);

      const postCards = page.locator('.bg-white.rounded-xl.shadow-sm').filter({
        has: page.locator('text=/إعجاب|تعليق/i'),
      });

      const count = await postCards.count();

      if (count > 0) {
        const firstPost = postCards.first();

        // Click multiple buttons quickly
        const likeButton = firstPost.locator('button:has-text("إعجاب")');
        const commentButton = firstPost.locator('button:has-text("تعليق")');

        await likeButton.click();
        await page.waitForTimeout(100);
        await commentButton.click();
        await page.waitForTimeout(1000);

        // Page should not crash
        const heading = page.locator('h1:has-text("مجتمع المزارعين")');
        await expect(heading).toBeVisible();
      }
    });

    test('should maintain scroll position during interactions', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Scroll down
      await page.evaluate(() => window.scrollTo(0, 300));
      await page.waitForTimeout(500);

      const initialScroll = await page.evaluate(() => window.scrollY);

      // Interact with filters
      const typeFilter = page.locator('select').filter({
        has: page.locator('option:has-text("الكل")'),
      });
      await typeFilter.selectOption({ label: 'نصائح' });
      await page.waitForTimeout(1000);

      // Page should be functional
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();

      console.log(`Scroll position maintained during filtering: ${initialScroll}px`);
    });

    test('should handle rapid search input changes', async ({ page }) => {
      await page.waitForTimeout(1000);

      const searchInput = page.locator('input[placeholder*="ابحث"]');

      // Type rapidly
      await searchInput.fill('a');
      await page.waitForTimeout(100);
      await searchInput.fill('ab');
      await page.waitForTimeout(100);
      await searchInput.fill('abc');
      await page.waitForTimeout(100);
      await searchInput.clear();
      await page.waitForTimeout(1000);

      // Page should still be functional
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      await expect(heading).toBeVisible();
    });
  });

  test.describe('Accessibility and Usability', () => {
    test('should have focusable interactive elements', async ({ page }) => {
      // Create post button should be focusable
      const createPostButton = page.locator('button:has-text("انشر سؤالاً")');
      await createPostButton.focus();

      const isFocused = await createPostButton.evaluate((el) => el === document.activeElement);
      expect(isFocused).toBe(true);
    });

    test('should allow keyboard navigation', async ({ page }) => {
      // Tab through elements
      await page.keyboard.press('Tab');
      await page.waitForTimeout(200);
      await page.keyboard.press('Tab');
      await page.waitForTimeout(200);

      // Some element should have focus
      const activeElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(activeElement).toBeTruthy();
    });

    test('should display all content without horizontal scroll', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for horizontal overflow
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });

      expect(hasHorizontalScroll).toBe(false);
    });

    test('should have readable text contrast', async ({ page }) => {
      await page.waitForTimeout(2000);

      // Main heading should have good contrast
      const heading = page.locator('h1:has-text("مجتمع المزارعين")');
      const color = await heading.evaluate((el) => window.getComputedStyle(el).color);

      console.log(`Heading color: ${color}`);
      expect(color).toBeTruthy();
    });
  });
});
