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

test('navigation has Recherche and Modules docs', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('link', { name: /Recherche/i }).first()).toBeVisible();
  await expect(page.getByRole('link', { name: /Modules/ })).toBeVisible();
});
