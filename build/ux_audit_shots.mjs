// UX audit capture: drive a served copy of the map at desktop + mobile, screenshot the core
// flows, save PNGs for read-back, and flag any two consecutive frames that are byte-identical
// (the silent-failure mode). Defaults to the LOCAL server so it sees local edits, not prod.
// Run from build/ (playwright is here):  AUD_DEV=mobile node ux_audit_shots.mjs
import { chromium } from 'playwright';
import { mkdirSync, readFileSync, existsSync } from 'fs';

const URL = process.env.AUD_URL || 'http://localhost:8799/web/index.html';
const OUT = process.env.AUD_OUT || 'tmp-ux';
const DEV = process.env.AUD_DEV || 'desktop';
mkdirSync(OUT, { recursive: true });

const isMobile = DEV === 'mobile';
const viewport = isMobile ? { width: 390, height: 844 } : { width: 1920, height: 1080 };
const P = isMobile ? 'm' : 'd';

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu'],
});
const ctx = await browser.newContext({
  viewport, deviceScaleFactor: isMobile ? 2 : 1,
  isMobile, hasTouch: isMobile,
  userAgent: isMobile ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' : undefined,
  geolocation: { latitude: 14.5995, longitude: 120.9842 }, permissions: ['geolocation'],
});
const page = await ctx.newPage();
const log = [];
page.on('pageerror', e => log.push('PAGEERR ' + e.message));

// byte-diff assertion: warn loudly if a shot is identical to the previous one (silent-failure catch)
let prevPath = null;
const shot = async (name) => {
  const path = `${OUT}/${P}-${name}.png`;
  await page.screenshot({ path });
  if (prevPath && existsSync(prevPath) && existsSync(path)) {
    const a = readFileSync(prevPath), b = readFileSync(path);
    if (a.length === b.length && a.equals(b)) log.push(`!! IDENTICAL to prev: ${name} (frame did not change)`);
  }
  prevPath = path; log.push('shot ' + name);
};
const wait = (ms) => page.waitForTimeout(ms);
const click = (sel, ms = 700) => page.evaluate(s => { const el = document.querySelector(s); if (el) el.click(); else throw new Error('missing ' + s); }, sel).then(() => wait(ms)).catch(() => log.push('clickfail ' + sel));

await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForSelector('#roads', { state: 'attached', timeout: 30000 }).catch(() => log.push('no #roads'));
await page.waitForFunction(() => { const o = document.getElementById('overlay'); return o && !o.classList.contains('on'); }, { timeout: 20000 }).catch(() => log.push('overlay stuck'));
await wait(3500);

// 01 COLD OPEN
await shot('01-cold-open');

// 02 GUIDED TOUR
await click('#seehow', 1400);
await shot('02-tour-step1');
await page.evaluate(() => { const c = document.getElementById('buildstep') || document.getElementById('ovcard'); if (!c) return;
  const next = [...c.querySelectorAll('button')].find(b => /next|susunod|→/i.test(b.textContent)); if (next) next.click(); }).catch(() => {});
await wait(1200); await shot('02-tour-step2');
// dismiss the tour cleanly through its own exit path if present
await page.evaluate(() => { const c = document.getElementById('buildstep'); if (c) { const done = [...c.querySelectorAll('button')].find(b => /done|tapos/i.test(b.textContent)); if (done) done.click(); }
  const o = document.getElementById('overlay'); if (o) o.classList.remove('on'); }).catch(() => {});
await wait(800);
if (isMobile) { await page.evaluate(() => window.__setPanel && window.__setPanel(true)).catch(() => {}); await wait(600); }

// 03 ROAD DETAIL: jump to EDSA, pick a road feature near viewport CENTER, hover (desktop) / tap (mobile)
const roadPt = await page.evaluate(() => {
  const m = window.__map; if (!m) return null;
  m.jumpTo({ center: [121.052, 14.617], zoom: 15 });
  return new Promise(res => { m.once('idle', () => {
    const c = m.getCanvas(), cx = c.clientWidth / 2, cy = c.clientHeight / 2, r = 60;
    const ids = m.getStyle().layers.map(l => l.id).filter(id => /net-hit|net-real|net-base/.test(id));
    const feats = m.queryRenderedFeatures([[cx - r, cy - r], [cx + r, cy + r]], { layers: ids });
    if (!feats.length) { res({ none: true, ids }); return; }
    const f = feats[0]; let ll; const g = f.geometry;
    if (g.type === 'LineString') ll = g.coordinates[Math.floor(g.coordinates.length / 2)];
    else if (g.type === 'MultiLineString') ll = g.coordinates[0][Math.floor(g.coordinates[0].length / 2)];
    else ll = m.getCenter().toArray();
    const px = m.project(ll);
    res({ x: Math.round(px.x), y: Math.round(px.y), name: f.properties && f.properties.name });
  }); });
}).catch(e => ({ err: String(e) }));
log.push('roadPt ' + JSON.stringify(roadPt));
await wait(1200);
if (roadPt && roadPt.x != null) {
  if (isMobile) await page.touchscreen.tap(roadPt.x, roadPt.y).catch(() => log.push('tapfail'));
  else await page.mouse.move(roadPt.x, roadPt.y);
  await wait(1300);
  const popups = await page.locator('.maplibregl-popup').count();
  log.push('popups after road interact: ' + popups);
}
await shot('03-road-detail');

// 04 SEARCH: set value + dispatch input so the live filter fires (fill() failed on mobile)
await page.evaluate(() => { const el = document.getElementById('find'); if (!el) return;
  el.focus(); el.value = 'EDSA'; el.dispatchEvent(new Event('input', { bubbles: true })); }).catch(() => log.push('searchfail'));
await wait(1200);
await shot('04-search');
await page.evaluate(() => { const el = document.getElementById('find'); if (el) { el.value = ''; el.dispatchEvent(new Event('input', { bubbles: true })); } }).catch(() => {});
await wait(500);

// 05 MY-LOCATION
await click('#mylocbtn', 2500);
await shot('05-my-location');

// 06 SAFE FLIP, pulled back to metro scale so the teal network payoff actually shows
await page.evaluate(() => window.__map && window.__map.jumpTo({ center: [121.0, 14.58], zoom: 10.6 })).catch(() => {});
await wait(1200);
await click('#roadmode button[data-m="proposed"]', 2000);
await shot('06-safe-flip');

console.log('LOG:\n' + log.join('\n'));
await ctx.close();
await browser.close();
