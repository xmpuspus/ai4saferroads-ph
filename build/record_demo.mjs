// Records a choreographed walkthrough of the REAL map (not a mockup) to webm.
// Beats walk the "Build the picture" stepper so the GIF SHOWS the argument:
//   banner + glowing roads -> (1) where people walk -> (2) where crashes happen ->
//   (3) what the limit is NOW (red corridors) -> (4) what it SHOULD be (the same roads flip green)
//   -> back to the overview -> Cebu -> home. Current vs proposed limits, 51 PH cities.
import { chromium } from 'playwright';
import { mkdirSync } from 'fs';

const URL = process.env.REC_URL || 'http://localhost:8810/web/index.html';
const DIR = '../recordings';
mkdirSync(DIR, { recursive: true });

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu'],
});
const ctx = await browser.newContext({
  viewport: { width: 1280, height: 800 }, deviceScaleFactor: 2,
  recordVideo: { dir: DIR, size: { width: 1280, height: 800 } },
});
const recStart = Date.now();
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
const click = (s, ms) => page.click(s).then(() => page.waitForTimeout(ms)).catch(() => errs.push('click ' + s));
const pick = (v, ms) => page.selectOption('#city', v).then(() => page.waitForTimeout(ms)).catch(() => errs.push('pick ' + v));

await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForSelector('#roads', { timeout: 30000 }).catch(() => errs.push('no panel'));
await page.waitForFunction(() => { const o = document.getElementById('overlay'); return o && !o.classList.contains('on'); }, { timeout: 30000 }).catch(() => errs.push('overlay stuck'));
await page.waitForTimeout(2500);                  // settle tiles after the loading overlay clears

// frame the build-up on central Manila so corridors + dots are both legible
await page.evaluate(() => window.__map.jumpTo({ center: [120.995, 14.605], zoom: 12.1 })).catch(() => errs.push('jump'));
await page.waitForTimeout(1400);
console.log('TRIM_S=' + ((Date.now() - recStart) / 1000).toFixed(1));  // where to start the gif

// The demo walks the hypothesis end to end: do speed limits impact crashes?
// (1) the question -> (2) crashes actually land on the flagged roads -> (3) and turn deadly
// when the road clears (speed) -> (4) the lever: drop to the safe limit and the risk falls.

// MOVE 1 — the question: the roads whose posted limit sits above the speed a person survives
await page.waitForTimeout(3200);                 // banner: each glowing road is posted over the survivable speed

// MOVE 2 — do crashes actually happen there? real satellite, then light up the 12,563 crash sites
await click('#layers > summary', 1000);          // open the Layers drawer
await click('#base button[data-v="sat"]', 3600); // switch to real Esri satellite imagery of the city
await click('#crashbtn', 5400);                  // the crashes land on the flagged corridors, tracing EDSA and C5 from space
await page.evaluate(() => { const d = document.getElementById('layers'); if (d) d.open = false; }).catch(() => {});
await page.waitForTimeout(900);

// MOVE 3 — but we crawl at 30, so is it speed? the severity-by-hour evidence + built-for-speed crops
await click('#sqbtn', 4400);                     // open "See the evidence": crashes peak in the jam, harm peaks when it clears
await page.evaluate(() => { const p = document.querySelector('.panel'); if (p) p.scrollBy({ top: 410, behavior: 'smooth' }); });
await page.waitForTimeout(3300);                 // scroll to the satellite crops: these roads are built for speed
await page.evaluate(() => { const p = document.querySelector('.panel'); if (p) p.scrollTo({ top: 0, behavior: 'smooth' }); });
await click('#sqbtn', 900);                      // close the evidence

// MOVE 4 — the lever: one corridor's limit now vs safe, then the whole network adopts the safe limit
await click('.road', 4200);                      // fly to Taft: 60 -> 30, cuts the chance of a deadly crash ~94%
await page.evaluate(() => window.__map.flyTo({ center: [120.995, 14.605], zoom: 13.4, duration: 1300 })).catch(() => errs.push('fly'));
await page.waitForTimeout(1600);                 // pull back so the flip reads across the network
await click('#layers > summary', 900);           // reopen the drawer for the road-colour switch
await click('#roadmode .seg button[data-m="proposed"]', 3000); // NOW is red-over-safe; flip to Safe...
await page.waitForTimeout(2600);                 // ...and the fast red corridors turn teal across the real city
await page.waitForTimeout(1400);                 // hold on the safer network over the crash-lit satellite

const video = page.video();
await ctx.close();
console.log('VIDEO=' + (await video.path()));
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
