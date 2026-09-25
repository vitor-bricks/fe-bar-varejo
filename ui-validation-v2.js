const { chromium } = require('@playwright/test');
const fs = require('fs');

async function validateUI() {
  let browser;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();

    // Set up console and error logging BEFORE navigation
    const consoleMessages = [];
    const pageErrors = [];

    page.on('console', msg => {
      const obj = {
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      };
      consoleMessages.push(obj);
      console.log(`[${msg.type().toUpperCase()}] ${msg.text()}`);
    });

    page.on('pageerror', error => {
      pageErrors.push({
        type: 'error',
        text: `Uncaught: ${error.message}`,
        stack: error.stack
      });
      console.error(`[PAGE ERROR] ${error.message}`);
    });

    console.log('\n=== Part 1: Main Dashboard (Torre de Controle tab) ===\n');

    // Navigate with hard reload
    console.log('1. Navigating to http://127.0.0.1:8777 with hard reload...');
    try {
      const response = await page.goto('http://127.0.0.1:8777', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });
      console.log(`   Response status: ${response.status()}`);
    } catch (err) {
      console.error(`   Navigation error: ${err.message}`);
    }

    // Do a hard reload
    await page.reload({ waitUntil: 'domcontentloaded' });
    console.log('2. Hard reload complete');

    // Wait for root element to be populated with React content
    console.log('3. Waiting for React to mount and render...');
    try {
      await page.waitForFunction(
        () => {
          const root = document.getElementById('root');
          return root && root.children.length > 0;
        },
        { timeout: 10000 }
      );
      console.log('   ✓ React mounted');
    } catch (err) {
      console.log('   ✗ React did not mount within timeout');
      console.log(`   Root element content: ${await page.locator('#root').innerHTML()}`);
    }

    // Wait for specific content elements
    console.log('4. Waiting for specific page content...');
    await page.waitForTimeout(2000); // Extra wait for async data loads

    // Take screenshot
    console.log('5. Taking full-page screenshot...');
    await page.screenshot({ path: '/tmp/tower_dashboard2.png', fullPage: true });
    console.log('   Screenshot saved to /tmp/tower_dashboard2.png');

    // Get page structure
    console.log('\n6. Page structure analysis:');
    const html = await page.locator('body').innerHTML();
    console.log(`   HTML length: ${html.length} chars`);

    // Check for key elements
    const hasRoot = await page.locator('#root').count() > 0;
    console.log(`   Has #root element: ${hasRoot}`);

    const headerPresent = await page.locator('header').count() > 0;
    console.log(`   Header present: ${headerPresent}`);

    const h1Text = await page.locator('h1').first().textContent();
    console.log(`   H1 text: "${h1Text}"`);

    // Verify rendered elements
    console.log('\n7. Verifying rendered elements:');

    const kpiCount = await page.locator('[class*="kpi"]').count();
    console.log(`   KPI tiles: ${kpiCount} found`);

    const svgCount = await page.locator('svg').count();
    console.log(`   SVG elements (charts): ${svgCount} found`);

    const tableCount = await page.locator('table').count();
    console.log(`   Tables: ${tableCount} found`);

    const cardCount = await page.locator('[class*="card"]').count();
    console.log(`   Cards: ${cardCount} found`);

    // Get all visible text
    const bodyText = await page.locator('body').textContent();
    console.log('\n8. Page text content validation:');
    console.log(`   Page contains "Torre de Controle": ${bodyText.includes('Torre de Controle')}`);
    console.log(`   Page contains "Genie": ${bodyText.includes('Genie')}`);
    console.log(`   Page contains "Pergunte": ${bodyText.includes('Pergunte')}`);

    // Check for tab elements
    const tabCount = await page.locator('[class*="tab"]').count();
    console.log(`   Tab elements found: ${tabCount}`);

    console.log('\n=== Part 2: Genie Tab Interaction ===\n');

    console.log('9. Looking for and clicking Genie tab...');
    const tabs = await page.locator('[class*="tab"]').all();
    let genieTabFound = false;
    for (const tab of tabs) {
      const text = await tab.textContent();
      if (text && text.includes('Genie')) {
        console.log(`   ✓ Found Genie tab with text: "${text}"`);
        await tab.click();
        await page.waitForTimeout(500);
        genieTabFound = true;
        break;
      }
    }
    if (!genieTabFound) {
      console.log('   ✗ Genie tab not found');
    }

    // Look for "Perguntar" button
    console.log('10. Looking for "Perguntar" button...');
    const buttons = await page.locator('button').all();
    let perguntarFound = false;
    for (const button of buttons) {
      const text = await button.textContent();
      if (text && text.includes('Perguntar')) {
        console.log(`   ✓ Found button with text: "${text}"`);
        // Only click if not disabled
        const disabled = await button.isDisabled();
        if (!disabled) {
          await button.click();
          console.log('   ✓ Button clicked');
          perguntarFound = true;
          // Wait for response
          await page.waitForTimeout(3000);
        } else {
          console.log('   ✗ Button is disabled');
        }
        break;
      }
    }
    if (!perguntarFound) {
      console.log('   ✗ Perguntar button not found');
    }

    // Take screenshot after Genie interaction
    console.log('11. Taking Genie interaction screenshot...');
    await page.screenshot({ path: '/tmp/tower_genie2.png', fullPage: true });
    console.log('   Screenshot saved to /tmp/tower_genie2.png');

    // Check for response elements
    console.log('\n12. Verifying Genie response elements:');
    const answerDiv = await page.locator('[class*="answer"]').count() > 0;
    console.log(`   Answer div present: ${answerDiv}`);

    const sqlBlock = await page.locator('pre[class*="sql"]').count() > 0;
    console.log(`   SQL block present: ${sqlBlock}`);

    const resultTable = await page.locator('table').count() > 1; // Should have at least 2 tables (worklist + genie result)
    console.log(`   Result table present: ${resultTable}`);

    // Summary
    console.log('\n=== Summary ===\n');
    console.log('Rendered cleanly?', headerPresent && h1Text && h1Text.includes('Torre de Controle') ? 'YES' : 'NO');

    // Console errors
    const allErrors = [...consoleMessages.filter(m => m.type === 'error'), ...pageErrors];
    console.log(`\nExact console errors if any: ${allErrors.length > 0 ? '\n' + allErrors.map((e, i) => `  [${i + 1}] ${e.text}`).join('\n') : 'none'}`);

    // Main dashboard elements
    console.log('\nMain dashboard elements present:');
    console.log(`  ${headerPresent ? '✓' : '✗'} Header`);
    console.log(`  ${kpiCount >= 3 ? '✓' : '✗'} KPI tiles (${kpiCount})`);
    console.log(`  ${svgCount > 0 ? '✓' : '✗'} Charts (${svgCount} SVG elements)`);
    console.log(`  ${tableCount > 0 ? '✓' : '✗'} Worklist table`);
    console.log(`  ${cardCount > 0 ? '✓' : '✗'} Content cards (${cardCount})`);

    // Genie interaction
    console.log('\nGenie interaction: ', genieTabFound && perguntarFound ? 'Tab clicked and button found' : 'See details above');

    console.log('\nCritical issues:', allErrors.length === 0 ? 'None' : `${allErrors.length} JavaScript error(s)`);

    await page.close();
  } catch (error) {
    console.error('Test error:', error.message);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

validateUI().catch(console.error);
