import { chromium } from 'playwright';
const URL = 'http://localhost:8777/web/index.html';
const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu']
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
const errs = [];
page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForSelector('#roads', { timeout: 30000 });
await page.waitForTimeout(3500);
// the crash toggle lives inside the collapsed Layers panel; open it first
await page.evaluate(() => { const d = document.getElementById('layers'); if (d) d.open = true; });
await page.waitForTimeout(300);
// enable the crash layer
await page.click('#crashbtn');
await page.waitForTimeout(2500);
// project a real crash point to screen pixels, then hover it
const pt = await page.evaluate(async () => {
  const fc = await (await fetch('data/crashes_manila.geojson')).json();
  const m = window.__map;
  // pick a crash near the current center for a reliable on-screen hit
  const c = m.getCenter();
  let best = null, bestd = 1e9;
  for (const f of fc.features.slice(0, 4000)) {
    const [lng, lat] = f.geometry.coordinates;
    const d = Math.hypot(lng - c.lng, lat - c.lat);
    if (d < bestd) { bestd = d; best = f; }
  }
  const p = m.project(best.geometry.coordinates);
  return { x: p.x, y: p.y, props: best.properties };
});
console.log('nearest crash props:', JSON.stringify(pt.props));
await page.mouse.move(pt.x, pt.y, { steps: 4 });
await page.waitForTimeout(400);
await page.mouse.move(pt.x + 1, pt.y + 1, { steps: 2 });
await page.waitForTimeout(700);
const tip = await page.evaluate(() => {
  const el = document.querySelector('.maplibregl-popup-content');
  return el ? el.innerText : null;
});
console.log('TOOLTIP_TEXT:', JSON.stringify(tip));
await page.screenshot({ path: '../screenshots/crashtip_1440.png', fullPage: false });
console.log('SHOT_OK crashtip');
if (errs.length) console.log('CONSOLE_ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
