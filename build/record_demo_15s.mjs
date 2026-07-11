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
// open already zoomed on the Metro core so the satellite + crashes read in the first second
await page.evaluate(() => window.__map.jumpTo({ center: [121.02, 14.57], zoom: 12.6 })).catch(() => errs.push('jump'));
await page.waitForTimeout(1200);
console.log('TRIM_S=' + ((Date.now() - recStart) / 1000).toFixed(1));

// BEAT 1 — real satellite, real crashes tracing the flagged roads, panning up EDSA
await jsClick('#base button[data-v="sat"]', 1600);
await jsClick('#crashbtn', 300);
await page.evaluate(() => window.__map.easeTo({ center: [121.048, 14.61], zoom: 12.9, duration: 4200, easing: t => t })).catch(() => errs.push('pan'));
await sub('12,563 real crashes. 76% of them land on the 8.5% of road we flag as built too fast.', 3800);

// BEAT 2 — dive to EDSA street level: the road those reports sit on, seen from space
await page.evaluate(() => window.__map.flyTo({ center: [121.052, 14.617], zoom: 16.6, duration: 3400 })).catch(() => errs.push('dive'));
await sub('This is EDSA. Ten lanes of highway running straight through homes and shops.', 3600);

// BEAT 3 — the fix: drop the crash overlay, dark base, flip to safe limits, pull back.
// crashes stay coral, so they must come off or they occlude the teal safe roads.
await jsClick('#crashbtn', 300);                                                       // crash dots off
await jsClick('#base button[data-v="dark"]', 800);                                     // let the dark base settle
console.log('MARK_FLIP=' + ((Date.now() - recStart) / 1000).toFixed(2));
await jsClick('#roadmode .seg button[data-m="proposed"]', 1000);                       // give the teal recolor time to paint
await page.evaluate(() => window.__map.easeTo({ center: [121.0, 14.585], zoom: 11.4, duration: 2600 })).catch(() => errs.push('rise'));
await sub('Bring each road to a speed people survive. The risk of a deadly crash drops about two thirds.', 3600);

// BEAT 4 — where to find it
await sub('Every street, 51 Philippine cities. ai4saferroads-ph.vercel.app', 2700);
await page.evaluate(() => { document.getElementById('rec-sub').style.opacity = 0; }).catch(() => {});
await page.waitForTimeout(800);

console.log('MARK_END=' + ((Date.now() - recStart) / 1000).toFixed(2));
const video = page.video();
await ctx.close();
console.log('VIDEO=' + (await video.path()));
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
