import { chromium } from 'playwright';

const URL = process.env.SHOT_URL || 'http://localhost:8799/web/index.html';
const OUT = process.env.SHOT_OUT || '../screenshots/sss_map_1440.png';

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu']
});
const VW = parseInt(process.env.SHOT_W || '1440', 10);
const VH = parseInt(process.env.SHOT_H || '900', 10);
const page = await browser.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 2, isMobile: VW < 600 });
const errs = [];
page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));

const WAITSEL = process.env.SHOT_WAITSEL || '#roads';
const DELAY = parseInt(process.env.SHOT_DELAY || '4500', 10);
await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForSelector(WAITSEL, { timeout: 30000 }).catch(() => errs.push(WAITSEL + ' never appeared'));
if (process.env.SHOT_CITY) {
  await page.selectOption('#city', process.env.SHOT_CITY).catch(() => errs.push('select failed'));
  await page.waitForTimeout(1200);
}
if (process.env.SHOT_CLICK) {
  await page.click(process.env.SHOT_CLICK).catch(() => errs.push('click ' + process.env.SHOT_CLICK + ' failed'));
  await page.waitForTimeout(1800);
}
await page.waitForTimeout(DELAY); // tiles / webgl / animation settle

await page.screenshot({ path: OUT, fullPage: false });
console.log('SHOT_OK ->', OUT);
if (errs.length) console.log('CONSOLE_ERRORS:\n' + errs.slice(0, 12).join('\n'));
await browser.close();
