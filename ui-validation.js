const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

async function validateUI() {
  let browser;
  try {
    browser = await chromium.launch();
    const context = await browser.createBrowserContext();
    const page = await context.newPage();

    console.log('\n=== Part 1: Main Dashboard (Torre de Controle tab) ===\n');

    // Navigate with hard reload
    console.log('1. Navigating to http://127.0.0.1:8777 with hard reload...');
    await page.goto('http://127.0.0.1:8777', { waitUntil: 'domcontentloaded' });
    await page.reload({ waitUntil: 'networkidle' });

    // Wait for React to mount
    console.log('2. Waiting for React to mount...');
    await page.waitForTimeout(2000);

    // Take initial screenshot
    console.log('3. Taking full-page screenshot...');
    await page.screenshot({ path: '/tmp/tower_dashboard2.png', fullPage: true });
    console.log('   Screenshot saved to /tmp/tower_dashboard2.png');

    // Get console messages
    console.log('\n4. Collecting console messages...');
    const consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      });
    });

    page.on('pageerror', error => {
      consoleMessages.push({
        type: 'error',
        text: `Uncaught exception: ${error.message}`,
        stack: error.stack
      });
    });

    // Wait a moment to capture any initial console messages
    await page.waitForTimeout(1000);

    console.log(`   Total console messages: ${consoleMessages.length}`);
    const errorMessages = consoleMessages.filter(msg => msg.type === 'error');
    const warnMessages = consoleMessages.filter(msg => msg.type === 'warning');
    console.log(`   Errors: ${errorMessages.length}`);
    console.log(`   Warnings: ${warnMessages.length}`);

    if (errorMessages.length > 0) {
      console.log('\n   ERROR MESSAGES:');
      errorMessages.forEach((err, i) => {
        console.log(`   [${i + 1}] ${err.text}`);
      });
    }

    // Verify rendered elements
    console.log('\n5. Verifying rendered elements:');

    // Check for KPI tiles
    const kpiCount = await page.locator('div[class*="kpi"], div[class*="tile"]').count();
    console.log(`   ✓ KPI tiles: ${kpiCount} found`);

    // Check for "tendência diária" SVG chart
    const lineChartPresent = await page.locator('svg').count() > 0;
    console.log(`   ${lineChartPresent ? '✓' : '✗'} "Tendência diária" SVG line chart: ${lineChartPresent ? 'visible' : 'not found'}`);

    // Check for "Receita em risco por região" bar chart
    const barChartElements = await page.locator('svg rect, [class*="bar"]').count();
    console.log(`   ${barChartElements > 0 ? '✓' : '✗'} "Receita em risco por região" bar chart: ${barChartElements > 0 ? 'visible' : 'not found'}`);

    // Check for "Worklist de reposição" table
    const tablePresent = await page.locator('table, [role="table"]').count() > 0;
    console.log(`   ${tablePresent ? '✓' : '✗'} "Worklist de reposição" table: ${tablePresent ? 'visible' : 'not found'}`);

    // Check for AI rationale cards
    const cardCount = await page.locator('[class*="card"], [class*="rationale"]').count();
    console.log(`   ✓ AI rationale cards: ${cardCount} found`);

    // Get page content for verification
    const pageText = await page.textContent('body');
    console.log('\n6. Page text content validation:');
    console.log(`   Page contains "Torre de Controle": ${pageText.includes('Torre de Controle') ? 'yes' : 'no'}`);
    console.log(`   Page contains "Genie": ${pageText.includes('Genie') ? 'yes' : 'no'}`);

    // Take screenshot after initial load
    console.log('\n=== Part 2: Genie Tab Interaction ===\n');
    console.log('6. Clicking on "Pergunte ao Genie" tab...');

    // Look for tab that might be labeled as Genie or similar
    const genieTab = await page.locator('[class*="tab"], button').filter({ hasText: /genie|Genie|Pergunte/i }).first();
    if (genieTab) {
      await genieTab.click();
      console.log('   ✓ Tab clicked');
      await page.waitForTimeout(500);
    } else {
      console.log('   ✗ Genie tab not found');
    }

    // Look for "Perguntar" button
    console.log('7. Looking for "Perguntar" button...');
    const perguntar = await page.locator('button').filter({ hasText: /perguntar|ask|question/i }).first();
    if (perguntar) {
      console.log('   ✓ "Perguntar" button found');
      await perguntar.click();
      console.log('   ✓ "Perguntar" button clicked');

      // Wait for response
      await page.waitForTimeout(2000);
    } else {
      console.log('   ✗ "Perguntar" button not found');
    }

    // Take screenshot after Genie interaction
    console.log('8. Taking Genie interaction screenshot...');
    await page.screenshot({ path: '/tmp/tower_genie2.png', fullPage: true });
    console.log('   Screenshot saved to /tmp/tower_genie2.png');

    // Verify Genie response elements
    console.log('\n9. Verifying Genie response elements:');
    const answerPresent = await page.locator('text=/answer|response|resultado/i').count() > 0;
    console.log(`   ${answerPresent ? '✓' : '✗'} Answer text appears: ${answerPresent ? 'yes' : 'no'}`);

    const sqlBlockPresent = await page.locator('code, [class*="sql"], pre').count() > 0;
    console.log(`   ${sqlBlockPresent ? '✓' : '✗'} SQL block is rendered: ${sqlBlockPresent ? 'yes' : 'no'}`);

    const resultTablePresent = await page.locator('table, [role="table"]').count() > 0;
    console.log(`   ${resultTablePresent ? '✓' : '✗'} Result table appears: ${resultTablePresent ? 'yes' : 'no'}`);

    console.log('\n=== Summary ===\n');
    console.log('Screenshots saved:');
    console.log('  - /tmp/tower_dashboard2.png (main dashboard)');
    console.log('  - /tmp/tower_genie2.png (Genie interaction)');

    // Check for critical issues
    console.log('\nCritical issues found:');
    if (errorMessages.length > 0) {
      console.log(`  - ${errorMessages.length} JavaScript error(s) in console`);
    } else {
      console.log('  - None (no JS errors)');
    }

    // Print full console error details
    if (errorMessages.length > 0) {
      console.log('\nFull error details:');
      errorMessages.forEach((err, i) => {
        console.log(`\nError ${i + 1}:`);
        console.log(`  Type: ${err.type}`);
        console.log(`  Message: ${err.text}`);
        if (err.stack) {
          console.log(`  Stack: ${err.stack}`);
        }
      });
    }

    await context.close();
  } catch (error) {
    console.error('Test error:', error);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

validateUI().catch(console.error);
