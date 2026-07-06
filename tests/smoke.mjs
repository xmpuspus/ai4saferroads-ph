// Playwright smoke test: the e2e checks are grep-presence only, so a JS runtime regression
// (a renamed layer id, a typo in the 530-line load handler) can pass "ALL CHECKS PASS" while
// the map is actually broken. This loads the real page and exercises it.
//
// Run: BASE_URL=http://127.0.0.1:8799/web/index.html node tests/smoke.mjs
// Wired into tests/e2e.sh behind `E2E_SMOKE=1` + node on PATH (skipped by default so CI/local
// runs stay fast and deterministic; the harness there starts/stops build/web/serve.py).
// tests/ has no node_modules of its own; the project's Playwright install lives under
// build/node_modules (see build/shot.mjs), so resolve it by relative path.
import { chromium } from '../build/node_modules/playwright/index.mjs';

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8799/web/index.html';

function fail(msg) {
  console.error('[FAIL]', msg);
  process.exitCode = 1;
}

function ok(msg) {
  console.log('[PASS]', msg);
}

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu'],
});

// -- load 1: the map actually renders a city, stats, and at least one flagged road --
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const pageErrors = [];
  page.on('pageerror', (e) => pageErrors.push(e.message));

  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 45000 });
  await page.waitForSelector('#roads', { timeout: 30000 });
  await page.waitForFunction(
    () => /\d/.test(document.querySelector('#stats .big')?.textContent || ''),
    { timeout: 30000 }
  ).then(() => ok('stats panel renders a number'))
   .catch(() => fail('stats panel never rendered a number'));

  const roadRows = await page.locator('#roads .road').count();
  if (roadRows > 0) ok(`flagged-road rows render (${roadRows})`);
  else fail('no flagged-road rows rendered in #roads');

  if (pageErrors.length === 0) ok('zero pageerror events on first load');
  else fail(`pageerror events fired: ${pageErrors.join(' | ')}`);

  await page.close();
}

// -- load 2: a blocked cities.json fetch must surface the error card, not a dark page --
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route('**/data/cities.json', (route) => route.abort());

  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
  const overlayOn = await page.waitForFunction(
    () => document.getElementById('overlay')?.classList.contains('on'),
    { timeout: 15000 }
  ).then(() => true).catch(() => false);

  if (overlayOn) ok('error card appears when cities.json is blocked');
  else fail('error card never appeared for a blocked cities.json fetch');

  await page.close();
}

await browser.close();
if (process.exitCode) {
  console.log('\nSMOKE: FAILURES PRESENT');
} else {
  console.log('\nSMOKE: ALL CHECKS PASS');
}
process.exit(process.exitCode || 0);
