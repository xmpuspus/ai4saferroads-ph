// Records the hero walkthrough of the REAL map (not a mockup) to webm, with a subtitle
// rail baked into the page so the GIF narrates itself for someone who has never seen the
// project: the question -> the glowing roads -> real crashes on satellite tracing them ->
// a street-level dive onto EDSA itself -> the night severity flip -> the fix (Safe view)
// -> where to find it. The panel stays
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
  viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1,  // dsf2 thrashes under memory pressure; video is 1280x800 either way
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
  const st = document.createElement('style');     // recording aid: real popups, enlarged to gif scale
  st.textContent = '.maplibregl-popup-content{zoom:1.34}';  // sized so the risk-cut line clears the subtitle rail
  document.head.appendChild(st);
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
await sub('Traffic keeps cars under 30. Will a lower limit make anyone safer?', 3500);

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

// BEAT 3b — hover a real crash dot: the tooltip is the proof each dot is a report
const dot = await page.evaluate(async () => {
  const fc = await (await fetch('data/crashes_manila.geojson')).json();
  const m = window.__map, c = m.getCenter();
  let best = null, bestd = 1e9;
  for (const f of fc.features) {
    if (!/edsa/i.test(f.properties.place || '')) continue;  // the dive beat names EDSA, so stay on it
    const [lng, lat] = f.geometry.coordinates;
    const d = Math.hypot(lng - c.lng, lat - c.lat);
    if (d < bestd) { bestd = d; best = f; }
  }
  const pt = m.project(best.geometry.coordinates);
  return { x: pt.x, y: pt.y, lng: best.geometry.coordinates[0], lat: best.geometry.coordinates[1] };
}).catch(() => (errs.push('dot'), null));
if (dot) { await page.mouse.move(dot.x, dot.y, { steps: 6 }); await page.mouse.move(dot.x + 1, dot.y + 1, { steps: 2 }); }
await page.waitForTimeout(500);
await sub('Every dot is a real report with a date, a time, and what happened.', 4800);
await page.waitForTimeout(600);
await page.mouse.move(60, 400, { steps: 4 });    // off the dots so the tooltip clears
await page.waitForTimeout(300);

// BEAT 3c — dive to street level: the road those reports sit on, seen from space
if (dot) await page.evaluate(d => window.__map.flyTo({ center: [d.lng, d.lat], zoom: 17.35, duration: 3800 }), dot).catch(() => errs.push('dive'));
await sub('This is EDSA from above. Ten lanes of highway running straight through homes and shops.', 4600);
await page.waitForTimeout(700);                  // let the z17 tiles sharpen before the pull-back
await page.evaluate(() => window.__map.easeTo({ center: [121.052, 14.617], zoom: 13.05, duration: 2600 })).catch(() => errs.push('rise'));
await sub('No sign changes what this road is built for.', 3600);

// BEAT 4 — night: back to the dark base, the severity flip
await jsClick('#base button[data-v="dark"]', 1000);
await sub('Total crashes peak in rush hour, when traffic is heaviest.', 3400);
await sub('But on EDSA, once the road clears at night, a crash is twice as likely to injure or kill.', 4600);

// BEAT 4b — hover a flagged road: limit now vs the safe speed, and the risk cut
await jsClick('#crashbtn', 300);                 // crash layer owns hover while on; release it
let road = null;
for (let attempt = 0; attempt < 3 && !road; attempt++) {
  if (attempt) await page.waitForTimeout(700);
  road = await page.evaluate(() => {
  const m = window.__map, c = m.getCanvas();
  const W = c.clientWidth, H = c.clientHeight;
  // upper-middle band: the popup opens downward from the point, so anchoring high
  // keeps its numbers clear of the subtitle rail. Prefer the post's exact story,
  // a named road posted 60 where 30 is survivable
  let fallback = null;
  for (let y = Math.round(H * 0.20); y < H * 0.30; y += 20)
    for (let x = Math.round(W * 0.32); x < W * 0.88; x += 20) {
      const fs = m.queryRenderedFeatures([x, y], { layers: ['net-real'] });
      if (!fs.length || !fs[0].properties.name) continue;
      const pr = fs[0].properties;
      if (pr.v_posted >= 60 && pr.v_safe <= 30) return { x, y };
      if (pr.v_posted >= 60 && !fallback) fallback = { x, y };
    }
  return fallback;
  }).catch(e => (errs.push('road ' + e.message), null));
}
console.log('ROAD_PROBE=' + JSON.stringify(road));
// open the popup with the map's own click event (same delegation wrapper, same hit-test,
// same handler as a real tap). The pointer stays parked away from the line: under
// recordVideo the hover hit-test flickers and its mouseleave keeps closing the popup.
await page.mouse.move(60, 400, { steps: 2 });
await page.waitForTimeout(200);
let popupOpen = false;
if (road) popupOpen = await page.evaluate(r => {
  const m = window.__map, pt = new maplibregl.Point(r.x, r.y);
  m.fire('click', { point: pt, lngLat: m.unproject(pt), originalEvent: new MouseEvent('click') });
  return !!document.querySelector('.maplibregl-popup-content');
}, road).catch(() => false);
console.log('POPUP_OPEN=' + popupOpen);
await sub('Tap any road for its limit now, the speed a person survives, and the risk cut.', 5000);
await page.evaluate(() => document.querySelectorAll('.maplibregl-popup').forEach(el => el.remove()));
await page.waitForTimeout(300);

// BEAT 5 — the fix: flip the network to the safe limits and pull back
console.log('MARK_FLIP=' + ((Date.now() - recStart) / 1000).toFixed(2));  // palette-segment boundary for the encode
await jsClick('#roadmode .seg button[data-m="proposed"]', 350);
await page.evaluate(() => window.__map.easeTo({ center: [121.0, 14.58], zoom: 11.3, duration: 3000 })).catch(() => errs.push('cam5'));
await sub('The fix is the road itself. Bring each one down to a speed people survive.', 3600);
await sub('Crash research says that cuts the risk of a deadly crash here by about two thirds.', 4200);

// BEAT 6 — where to find it (the URL gets its own line so it never wraps)
await sub('Every street. 51 Philippine cities. Free and open.', 2400);
await sub('ai4saferroads-ph.vercel.app', 2600);
await page.evaluate(() => { document.getElementById('rec-sub').style.opacity = 0; }).catch(() => {});
await page.waitForTimeout(900);

console.log('MARK_END=' + ((Date.now() - recStart) / 1000).toFixed(2));
const video = page.video();
await ctx.close();
console.log('VIDEO=' + (await video.path()));
if (errs.length) console.log('ERRORS:\n' + errs.slice(0, 8).join('\n'));
await browser.close();
