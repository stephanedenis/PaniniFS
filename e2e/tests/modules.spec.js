// Modules aggregation tests - Check module listings and structure
import { test, expect } from '@playwright/test';

test.describe('Modules documentation (aggregated)', () => {
  test('modules index is reachable and titled', async ({ page }) => {
    await page.goto('/modules/');
    await expect(page).toHaveTitle(/Documentation des modules|Module documentation|Modules docs/i);
    await expect(page.locator('h1')).toContainText(/Documentation des modules|Module documentation|Modules docs/i);
  });

  test('module listings have valid structure', async ({ page }) => {
    const response = await page.goto('/modules', {
      waitUntil: 'domcontentloaded'
    }).catch(() => null);
    
    if (response && response.status() === 200) {
      // Check for module list elements
      const moduleElements = page.locator('[data-module], .module, article');
      const count = await moduleElements.count();
      
      // If we have modules, verify they have content
      if (count > 0) {
        const firstModule = moduleElements.first();
        await expect(firstModule).toBeVisible();
        
        // Each module should have some text content
        const text = await firstModule.textContent();
        expect(text?.length).toBeGreaterThan(0);
      }
    } else {
      // Fallback mode: ensure at least one GitHub link is present
      const ghLinks = await page
        .locator('a[href*="github.com"][href*="Panini-FS"], a[href*="github.com"][href*="PaniniFS"]')
        .count();
      expect(ghLinks).toBeGreaterThan(0);
    }
  });
});
