import { chromium } from 'playwright';

const URL = process.env.SHOT_URL || 'http://localhost:8799/web/index.html';
const OUT = process.env.SHOT_OUT || '../screenshots/popup_reorder.png';

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu']
});
const page = await browser.newPage({ viewport: { width: 1200, height: 760 }, deviceScaleFactor: 2 });
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));

await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForFunction(() => window.__map && window.__map.isStyleLoaded(), { timeout: 30000 }).catch(() => errs.push('style not loaded'));
await page.waitForTimeout(4000);

// fatten the scored line so the hover lands on it, then hover a real named flagged road
await page.evaluate(() => window.__map.setPaintProperty('net-real', 'line-width', 12));
await page.waitForTimeout(600);
const pt = await page.evaluate(() => {
  const m = window.__map;
  const fs = m.queryRenderedFeatures({ layers: ['net-real'] })
    .filter(f => f.properties.name && f.properties.sss > 0);
  if (!fs.length) return null;
  let c = fs[0].geometry.coordinates;
  if (Array.isArray(c[0][0])) c = c[0];
  const mid = c[Math.floor(c.length / 2)];
  const p = m.project(mid);
  return { x: p.x, y: p.y, name: fs[0].properties.name };
});
if (!pt) { console.log('NO_FEATURE'); await browser.close(); process.exit(0); }
console.log('hovering:', pt.name, 'at', Math.round(pt.x), Math.round(pt.y));
await page.mouse.move(pt.x, pt.y);
await page.waitForTimeout(500);
await page.mouse.move(pt.x + 1, pt.y + 1);
await page.waitForTimeout(900);
const hasPopup = await page.$('.maplibregl-popup');
console.log('popup present:', !!hasPopup);
await page.screenshot({ path: OUT });
console.log('SHOT_OK ->', OUT);
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 6).join('\n'));
await browser.close();
