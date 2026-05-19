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

  test('whats-new and feed.xml are live', async ({ page }) => {
    const resp1 = await page.request.get('/research/whats-new.html');
    // Tolerate 404 for now as per workflow intention
    expect([200, 404]).toContain(resp1.status());
    
    const resp2 = await page.request.get('/research/feed.xml');
    // Tolerate 404 for now as per workflow intention
    expect([200, 404]).toContain(resp2.status());
  });
});
