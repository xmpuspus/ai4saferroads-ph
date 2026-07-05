// Regenerate the Open Graph card as a real 1200x630 screenshot of the live reframe map.
import { chromium } from 'playwright';
const URL = process.env.OG_URL || 'http://localhost:8777/web/index.html';
const OUT = process.env.OG_OUT || 'web/og-card.png';
const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu']
});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForSelector('#roads', { timeout: 30000 });
await page.waitForTimeout(6000); // tiles + hexbins settle
await page.screenshot({ path: OUT, fullPage: false });
console.log('OG_OK ->', OUT);
if (errs.length) console.log('ERRORS:', errs.slice(0, 5).join(' | '));
await browser.close();
