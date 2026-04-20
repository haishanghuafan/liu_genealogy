const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const consoleMessages = [];
  const networkErrors = [];

  page.on('console', msg => {
    consoleMessages.push({ type: msg.type(), text: msg.text() });
  });

  page.on('response', response => {
    if (!response.ok() && response.status() >= 400) {
      networkErrors.push({ url: response.url(), status: response.status() });
    }
  });

  page.on('requestfailed', request => {
    networkErrors.push({ url: request.url(), failure: request.failure()?.errorText });
  });

  try {
    console.log('Navigating to http://localhost:3012/liushipu/family-tree...');
    await page.goto('http://localhost:3012/liushipu/family-tree', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    console.log('\n=== Console Messages ===');
    consoleMessages.forEach(m => console.log(`[${m.type}] ${m.text}`));

    console.log('\n=== Network Errors ===');
    networkErrors.forEach(e => console.log(`${e.status || 'FAILED'}: ${e.url} - ${e.failure || ''}`));

    console.log('\n=== Page Content ===');
    const bodyText = await page.textContent('body');
    console.log(bodyText.substring(0, 500));

  } catch (error) {
    console.error('Test failed:', error.message);
  } finally {
    await browser.close();
  }
})();
