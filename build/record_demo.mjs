// Records the hero walkthrough of the REAL map (not a mockup) to webm, with a subtitle
// rail baked into the page so the GIF narrates itself for someone who has never seen the
// project: the question -> the glowing roads -> real crashes on satellite tracing them ->
// the night severity flip -> the fix (Safe view) -> where to find it. The panel stays
// collapsed to its headline so the map and the subtitles carry the whole argument.
// Every subtitle number comes from the shipped artifacts (docs/findings.md, validation.md).
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
// JS-dispatch clicks so controls inside the collapsed panel still fire
const jsClick = (sel, ms) => page.evaluate(s => { const el = document.querySelector(s); if (el) el.click(); else throw new Error('missing ' + s); }, sel)
  .then(() => page.waitForTimeout(ms)).catch(() => errs.push('click ' + sel));
// lower-third subtitle: fade the line in, hold it for ms
const sub = async (text, ms) => {
  await page.evaluate(t => { const d = document.getElementById('rec-sub');
    d.style.opacity = 0; setTimeout(() => { d.textContent = t; d.style.opacity = 1; }, 260); }, text).catch(() => errs.push('sub'));
  await page.waitForTimeout(ms);
};

await page.goto(URL, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForSelector('#roads', { timeout: 30000 }).catch(() => errs.push('no panel'));
await page.waitForFunction(() => { const o = document.getElementById('overlay'); return o && !o.classList.contains('on'); }, { timeout: 30000 }).catch(() => errs.push('overlay stuck'));
await page.waitForTimeout(2200);                  // settle tiles after the loading overlay clears

await page.evaluate(() => {
  window.__setPanel(true);                        // collapse to the headline; the map is the star
  const d = document.createElement('div'); d.id = 'rec-sub';
  d.style.cssText = 'position:fixed;left:50%;bottom:36px;transform:translateX(-50%);' +
    'max-width:900px;padding:15px 28px;background:rgba(10,13,18,0.84);' +
    'border:1px solid rgba(255,255,255,0.15);border-radius:14px;color:#F2F5F9;' +
    'font:600 31px/1.35 "IBM Plex Sans",system-ui,sans-serif;text-align:center;' +
    'z-index:99;opacity:0;transition:opacity .45s;box-shadow:0 8px 30px rgba(0,0,0,.5)';
  document.body.appendChild(d);
}).catch(() => errs.push('setup'));
await page.evaluate(() => window.__map.jumpTo({ center: [121.0, 14.58], zoom: 11.05 })).catch(() => errs.push('jump'));
await page.waitForTimeout(1500);
console.log('TRIM_S=' + ((Date.now() - recStart) / 1000).toFixed(1));  // where to start the gif

// BEAT 1 — the question, over the whole glowing metro (dark base)
await sub('Metro Manila. The speed limit on many of these roads is 60.', 3400);
await sub('Traffic crawls at 30. So does the limit even matter?', 3500);

// BEAT 2 — what the glow means, easing into the city core
await page.evaluate(() => window.__map.easeTo({ center: [120.995, 14.605], zoom: 12.4, duration: 3200 })).catch(() => errs.push('cam2'));
await sub('Watch the glowing roads. Each one is posted above the speed a person can survive.', 4200);

// BEAT 3 — real satellite, real crashes, panning up EDSA
await jsClick('#base button[data-v="sat"]', 2200);
await jsClick('#crashbtn', 300);
await page.evaluate(() => window.__map.easeTo({ center: [121.02, 14.55], zoom: 13.05, duration: 1800 })).catch(() => errs.push('cam3'));  // drift toward EDSA while the count reads
await sub('12,563 real crashes from MMDA reports, 2018 to 2020.', 4000);
await page.evaluate(() => window.__map.easeTo({ center: [121.052, 14.617], zoom: 13.05, duration: 4800, easing: t => t })).catch(() => errs.push('pan'));
await sub('They pile up on the glowing roads. 42% happen on just 7% of the street network.', 4800);

// BEAT 4 — night: back to the dark base, the severity flip
await jsClick('#base button[data-v="dark"]', 1000);
await sub('Total crashes peak in rush hour, when traffic is heaviest.', 3400);
await sub('But on EDSA, once the road clears at night, a crash is twice as likely to injure or kill.', 4600);

// BEAT 5 — the fix: flip the network to the safe limits and pull back
await jsClick('#crashbtn', 250);
await jsClick('#roadmode .seg button[data-m="proposed"]', 350);
await page.evaluate(() => window.__map.easeTo({ center: [121.0, 14.58], zoom: 11.3, duration: 3000 })).catch(() => errs.push('cam5'));
await sub('The fix is the road itself. Bring each one down to a speed people survive.', 3800);
await sub('Crash research says that cuts the risk of a deadly crash here by about two thirds.', 4200);

// BEAT 6 — where to find it (the URL gets its own line so it never wraps)
await sub('Every street. 51 Philippine cities. Free and open.', 2400);
await sub('ai4saferroads-ph.vercel.app', 2600);
await page.evaluate(() => { document.getElementById('rec-sub').style.opacity = 0; }).catch(() => {});
await page.waitForTimeout(900);

const video = page.video();
await ctx.close();
console.log('VIDEO=' + (await video.path()));
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
