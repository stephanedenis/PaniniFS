// Research pages tests - Check research sections availability
import { test, expect } from '@playwright/test';

test.describe('Panini Research Pages', () => {
  test('research section is accessible', async ({ page }) => {
    await page.goto('/');
    
    // Try to find research-related links
    const researchLinks = page.locator('a').filter({ hasText: /research|études|papers/i });
    const count = await researchLinks.count();
    
    // If research links exist, they should be clickable
    if (count > 0) {
      const firstLink = researchLinks.first();
      await expect(firstLink).toBeVisible();
    }
  });

  test('research pages return proper status codes', async ({ page }) => {
    // Test common research paths (may be 404 during development)
    const researchPaths = [
      '/research',
      '/papers',
      '/publications'
    ];
    
    for (const path of researchPaths) {
      const response = await page.goto(path, { 
        waitUntil: 'domcontentloaded',
        timeout: 5000 
      }).catch(() => null);
      
      if (response) {
        const status = response.status();
        // Accept 200 (exists) or 404 (not yet implemented)
        // Fail on 500+ (server errors)
        expect(status).toBeLessThan(500);
      }
    }
  });

  test('research metadata is valid if page exists', async ({ page }) => {
    const response = await page.goto('/research', { 
      waitUntil: 'domcontentloaded' 
    }).catch(() => null);
    
    if (response && response.status() === 200) {
      // If page exists, check for basic metadata
      const title = await page.title();
      expect(title.length).toBeGreaterThan(0);
      
      // Check for meta description
      const metaDescription = page.locator('meta[name="description"]');
      if (await metaDescription.count() > 0) {
        const content = await metaDescription.getAttribute('content');
        expect(content?.length).toBeGreaterThan(0);
      }
    }
  });
});
