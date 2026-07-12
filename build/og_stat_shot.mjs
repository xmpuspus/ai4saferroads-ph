// Purpose-built OG share card PROPOSAL: hero stat "76% of crashes on 8.5% of roads" over the
// live glowing network, big type that survives the feed thumbnail downscale. Renders to a file
// in the audit dir; does NOT touch the live og-card.png. Run from build/.
import { chromium } from 'playwright';
const URL = process.env.OG_URL || 'http://localhost:8799/web/index.html';
const OUT = process.env.OG_OUT || '../tmp/ux-audit-20260712T090000Z/og-thesis-card.png';
const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl', '--in-process-gpu'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: Number(process.env.OG_DSR || 2) });
await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForSelector('#roads', { state: 'attached', timeout: 30000 });
// frame the dense QC/Manila core so the bright red arterials fill the right of the card
await page.evaluate(() => { window.__map.jumpTo({ center: [121.005, 14.63], zoom: 11.5 }); });
await page.waitForTimeout(500);
await page.evaluate(() => Promise.race([new Promise(r => window.__map.once('idle', r)), new Promise(r => setTimeout(r, 4000))]));
await page.waitForTimeout(1200);

// strip the app chrome and lay a purpose-built stat card over the map
await page.evaluate(() => {
  for (const sel of ['.panel', '.topkey', '#seehow', '.stamp', '.maplibregl-control-container', '#mylocbtn'])
    document.querySelectorAll(sel).forEach(e => e.style.display = 'none');
  const o = document.createElement('div');
  o.style.cssText = 'position:fixed;inset:0;z-index:50;padding:0 64px;display:flex;flex-direction:column;justify-content:center;' +
    'background:linear-gradient(100deg,rgba(9,12,17,.97) 0%,rgba(9,12,17,.9) 40%,rgba(9,12,17,.5) 64%,rgba(9,12,17,0) 86%);' +
    'font-family:var(--font-body,system-ui,sans-serif)';
  o.innerHTML = `
    <div style="font-family:var(--font-data,monospace);font-size:19px;letter-spacing:.16em;text-transform:uppercase;color:#9DB4CC;font-weight:600">AI for safer roads &middot; Metro Manila</div>
    <div style="margin-top:16px;font-family:var(--font-display,sans-serif);font-size:39px;line-height:1.12;color:#F2F5F9;font-weight:700;max-width:840px">Will a lower speed limit <span style="color:#FB6A50">actually make us safer?</span></div>
    <div style="margin-top:20px;display:flex;align-items:baseline;gap:20px;font-family:var(--font-display,sans-serif)">
      <span style="font-size:128px;line-height:.86;color:#5FC6AF;font-weight:800">&minus;66%</span>
      <span style="font-size:41px;color:#F2F5F9;font-weight:700;max-width:340px;line-height:1.1">the chance a crash kills</span>
    </div>
    <div style="margin-top:22px;font-size:28px;color:#CDD6E0;font-weight:500;max-width:860px;line-height:1.36">but only when the road is built to keep people clear of the fast traffic, not just a lower sign.</div>
    <div style="margin-top:28px;display:flex;align-items:center;gap:16px">
      <span style="font-family:var(--font-data,monospace);font-size:22px;color:#160a08;font-weight:700;background:#FB6A50;padding:9px 16px;border-radius:10px">ai4saferroads-ph.vercel.app</span>
      <span style="font-family:var(--font-data,monospace);font-size:17px;color:#7E93AB">Modeled drop across Metro Manila's flagged roads</span>
    </div>`;
  document.body.appendChild(o);
});
await page.waitForTimeout(400);
await page.screenshot({ path: OUT, fullPage: false });
console.log('OG_STAT_OK ->', OUT);
await browser.close();
