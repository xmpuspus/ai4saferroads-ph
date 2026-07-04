import { chromium } from 'playwright';

const URL = process.env.SHOT_URL || 'http://localhost:8799/web/index.html';
const OUT = process.env.SHOT_OUT || '../screenshots/popup_check.png';

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu']
});
const page = await browser.newPage({ viewport: { width: 1200, height: 760 }, deviceScaleFactor: 2 });
const errs = [];
page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));

await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForFunction(() => window.__map && window.__map.isStyleLoaded(), { timeout: 30000 }).catch(() => errs.push('style never loaded'));
await page.waitForTimeout(3500);

await page.evaluate(() => {
  const m = window.__map;
  const html = '<b>Rizal Avenue</b><br>primary &middot; posted 60 km/h<br>' +
    'Safe System: <b>30 km/h</b> &middot; gap +30<br>' +
    'Score <b>75</b> &middot; &minus;93.8% modeled fatal risk<br>' +
    '<span style="color:#9bb0c2">pedestrian activity (1 VRU site&lt;=50m)</span>';
  new maplibregl.Popup({ closeButton: false, maxWidth: '260px' })
    .setLngLat(m.getCenter()).setHTML(html).addTo(m);
});
await page.waitForTimeout(900);

await page.screenshot({ path: OUT, fullPage: false });
console.log('SHOT_OK ->', OUT);
if (errs.length) console.log('CONSOLE_ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
