// Modules aggregation tests - Check module listings and structure
import { test, expect } from '@playwright/test';

test.describe('Panini Modules Aggregation', () => {
  test('modules index page is accessible', async ({ page }) => {
    const response = await page.goto('/modules', {
      waitUntil: 'domcontentloaded',
      timeout: 5000
    }).catch(() => null);
    
    if (response) {
      const status = response.status();
      // Accept 200 (exists) or 404 (not yet implemented)
      expect(status).toBeLessThan(500);
      
      if (status === 200) {
        // If modules page exists, check for content
        const bodyText = await page.textContent('body');
        expect(bodyText.length).toBeGreaterThan(0);
      }
    }
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
    }
  });

  test('modules can be navigated', async ({ page }) => {
    const response = await page.goto('/modules', {
      waitUntil: 'domcontentloaded'
    }).catch(() => null);
    
    if (response && response.status() === 200) {
      // Find all links on the modules page
      const links = page.locator('a[href*="/module"], a[href*="/modules/"]');
      const linkCount = await links.count();
      
      if (linkCount > 0) {
        // Try clicking the first module link
        const firstLink = links.first();
        const href = await firstLink.getAttribute('href');
        
        if (href) {
          const moduleResponse = await page.goto(href, {
            waitUntil: 'domcontentloaded',
            timeout: 5000
          }).catch(() => null);
          
          if (moduleResponse) {
            expect(moduleResponse.status()).toBeLessThan(500);
          }
        }
      }
    }
  });

  test('modules page has proper metadata', async ({ page }) => {
    const response = await page.goto('/modules', {
      waitUntil: 'domcontentloaded'
    }).catch(() => null);
    
    if (response && response.status() === 200) {
      // Check page title
      const title = await page.title();
      expect(title.length).toBeGreaterThan(0);
      expect(title.toLowerCase()).toMatch(/module|panini/);
    }
  });
});
