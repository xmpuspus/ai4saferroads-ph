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

await page.waitForTimeout(2700);                 // beat 1 — banner + glowing roads posted over the safe speed
await click('#buildbtn', 3300);                  // step 1 — where people walk: schools/markets/hospitals
await click('#bnext', 3300);                     // step 2 — where crashes happen: red dots on the same roads
await click('#bnext', 3500);                     // step 3 — the limit NOW: red corridors signed 60+ km/h
await click('#bnext', 4400);                     // step 4 — what it SHOULD be: the same roads flip GREEN
await click('#bnext', 1500);                     // Finish — back to the glowing overview
await click('#layers > summary', 1100);          // open the Layers drawer
await click('#crowdbtn', 4300);                  // speed risk x crowding: bivariate + the finding
await click('#crowdbtn', 900);                   // turn crowding off
await click('#layers > summary', 700);           // close the drawer
await pick('cebu', 2900);                        // another city, same map
await pick('manila', 2000);                      // home
await click('.road', 3400);                      // tap a worst road: radar ping + what the limit should be

const video = page.video();
await ctx.close();
console.log('VIDEO=' + (await video.path()));
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
