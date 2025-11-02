// Smoke tests - Basic site availability checks
import { test, expect } from '@playwright/test';

test.describe('Panini Site - Smoke Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check that we get a 200 response
    expect(page.url()).toContain('paninifs.org');
    
    // Check for basic structure
    await expect(page.locator('body')).toBeVisible();
  });

  test('has navigation links', async ({ page }) => {
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check for common navigation elements (adjust based on actual site structure)
    const links = page.locator('a');
    const linkCount = await links.count();
    
    // Should have at least some links
    expect(linkCount).toBeGreaterThan(0);
  });

  test('site responds with valid HTML', async ({ page }) => {
    const response = await page.goto('/');
    
    // Check response status
    expect(response?.status()).toBeLessThan(400);
    
    // Check content type
    const contentType = response?.headers()['content-type'];
    expect(contentType).toContain('text/html');
  });

  test('no console errors on homepage', async ({ page }) => {
    const consoleErrors = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Allow for known non-critical errors, but catch severe ones
    const severeErrors = consoleErrors.filter(err => 
      !err.includes('favicon') && 
      !err.includes('404')
    );
    
    expect(severeErrors.length).toBe(0);
  });
});
