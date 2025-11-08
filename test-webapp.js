const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Collect console messages
  const consoleMessages = [];
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    consoleMessages.push({ type, text });
    console.log(`[CONSOLE ${type.toUpperCase()}] ${text}`);
  });
  
  // Collect errors
  const pageErrors = [];
  page.on('pageerror', error => {
    pageErrors.push(error.message);
    console.log(`[PAGE ERROR] ${error.message}`);
  });
  
  // Collect network errors
  page.on('requestfailed', request => {
    console.log(`[NETWORK FAILED] ${request.url()} - ${request.failure().errorText}`);
  });
  
  try {
    console.log('🚀 Navigating to http://localhost:5173/');
    await page.goto('http://localhost:5173/', { 
      waitUntil: 'networkidle',
      timeout: 10000 
    });
    
    console.log('✅ Page loaded successfully');
    
    // Wait a bit for any async errors
    await page.waitForTimeout(3000);
    
    // Get page title
    const title = await page.title();
    console.log(`\n📄 Page title: ${title}`);
    
    // Check for React root
    const hasReactRoot = await page.locator('#root').count() > 0;
    console.log(`\n⚛️  React root present: ${hasReactRoot}`);
    
    // Check for main content
    const bodyText = await page.textContent('body');
    console.log(`\n📝 Body has content: ${bodyText.length > 100}`);
    
    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`Console messages: ${consoleMessages.length}`);
    console.log(`  - log: ${consoleMessages.filter(m => m.type === 'log').length}`);
    console.log(`  - warn: ${consoleMessages.filter(m => m.type === 'warning').length}`);
    console.log(`  - error: ${consoleMessages.filter(m => m.type === 'error').length}`);
    console.log(`Page errors: ${pageErrors.length}`);
    
    if (pageErrors.length > 0) {
      console.log('\n❌ ERRORS FOUND:');
      pageErrors.forEach((err, i) => console.log(`  ${i+1}. ${err}`));
    }
    
    if (consoleMessages.filter(m => m.type === 'error').length === 0 && pageErrors.length === 0) {
      console.log('\n✅ NO ERRORS DETECTED');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
})();
