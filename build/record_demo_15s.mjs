// A ~15s cut of the hero walk, built for the LinkedIn feed: it opens on the most arresting
// frame (real crash dots over satellite tracing the flagged roads), dives to EDSA, then flips
// the network to safe limits. No slow question intro. Every subtitle number comes from the
// shipped artifacts (crash_validation.json: 8.5% of length carries 76.2% of crashes).
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
  viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1,
  recordVideo: { dir: DIR, size: { width: 1280, height: 800 } },
});
const recStart = Date.now();
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
const jsClick = (sel, ms) => page.evaluate(s => { const el = document.querySelector(s); if (el) el.click(); else throw new Error('missing ' + s); }, sel)
  .then(() => page.waitForTimeout(ms)).catch(() => errs.push('click ' + sel));
const sub = async (text, ms) => {
  await page.evaluate(t => { const d = document.getElementById('rec-sub');
    d.style.opacity = 0; setTimeout(() => { d.textContent = t; d.style.opacity = 1; }, 240); }, text).catch(() => errs.push('sub'));
  await page.waitForTimeout(ms);
};

await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForSelector('#roads', { timeout: 30000 }).catch(() => errs.push('no panel'));
await page.waitForFunction(() => { const o = document.getElementById('overlay'); return o && !o.classList.contains('on'); }, { timeout: 30000 }).catch(() => errs.push('overlay stuck'));
await page.waitForTimeout(2200);

await page.evaluate(() => {
  window.__setPanel(true);
  const d = document.createElement('div'); d.id = 'rec-sub';
  d.style.cssText = 'position:fixed;left:50%;bottom:36px;transform:translateX(-50%);' +
    'max-width:960px;padding:15px 28px;background:rgba(10,13,18,0.84);' +
    'border:1px solid rgba(255,255,255,0.15);border-radius:14px;color:#F2F5F9;' +
    'font:600 31px/1.35 "IBM Plex Sans",system-ui,sans-serif;text-align:center;' +
    'z-index:99;opacity:0;transition:opacity .4s;box-shadow:0 8px 30px rgba(0,0,0,.5)';
  document.body.appendChild(d);
}).catch(() => errs.push('setup'));
// open on the glowing danger network over the dark base: the red roads pose the question
await page.evaluate(() => window.__map.jumpTo({ center: [121.02, 14.585], zoom: 11.5 })).catch(() => errs.push('jump'));
await page.waitForTimeout(800);
console.log('TRIM_S=' + ((Date.now() - recStart) / 1000).toFixed(1));

// BEAT 1 — lead with the question itself, held over the glowing danger network with a slow zoom
await page.evaluate(() => window.__map.easeTo({ center: [121.03, 14.60], zoom: 11.78, duration: 3400, easing: t => t })).catch(() => errs.push('pan'));
await sub('Will a lower speed limit actually make us safer?', 2900);

// BEAT 2 — the answer starts with the road, not the sign: dive to EDSA on satellite, where crashes cluster
await jsClick('#base button[data-v="sat"]', 700);
await jsClick('#crashbtn', 300);
await page.evaluate(() => window.__map.flyTo({ center: [121.052, 14.617], zoom: 15.6, duration: 3500 })).catch(() => errs.push('dive'));
await sub('Not the sign. The road is built for speed, and most crashes cluster on roads like EDSA.', 3800);

// BEAT 3 — the fix: build each road for a survivable speed, deadly-crash risk drops two thirds
await jsClick('#crashbtn', 300);                                                       // crash dots off
await jsClick('#base button[data-v="dark"]', 700);                                     // dark base back
console.log('MARK_FLIP=' + ((Date.now() - recStart) / 1000).toFixed(2));
await jsClick('#roadmode .seg button[data-m="proposed"]', 900);                        // give the teal recolor time to paint
await page.evaluate(() => window.__map.easeTo({ center: [121.0, 14.585], zoom: 11.3, duration: 2700 })).catch(() => errs.push('rise'));
await sub('Build each road for a speed people survive and the risk a crash kills drops about two thirds.', 3800);

// BEAT 4 — where to find it; hold the URL on the final frame instead of fading it out
await sub('Every street, 50 cities and Metro Manila. ai4saferroads-ph.vercel.app', 3000);
await page.waitForTimeout(500);

console.log('MARK_END=' + ((Date.now() - recStart) / 1000).toFixed(2));
const video = page.video();
await ctx.close();
console.log('VIDEO=' + (await video.path()));
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
