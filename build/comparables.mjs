import { chromium } from 'playwright';
const OUT = '../tmp/ux-audit-20260712T090000Z/comparables';
import { mkdirSync } from 'fs';
mkdirSync(OUT, { recursive: true });
const sites = [
  ['irap', 'https://demonstrator.vida.irap.org/'],
  ['visionzero', 'https://vzv.nyc/'],
  ['crashmapper', 'https://vis.crashmapper.org/'],
  ['kepler', 'https://kepler.gl/demo'],
  ['ours', 'https://ai4saferroads-ph.vercel.app/'],
];
const b = await chromium.launch({ args:['--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist','--enable-webgl','--in-process-gpu'] });
for (const [name, url] of sites) {
  const p = await (await b.newContext({ viewport:{width:1440,height:900}, deviceScaleFactor:1 })).newPage();
  const log = [];
  try {
    await p.goto(url, { waitUntil:'domcontentloaded', timeout:40000 });
    await p.waitForTimeout(8000); // let maps/tiles/UI settle
    await p.screenshot({ path: `${OUT}/${name}.png` });
    log.push(name+' OK '+(await p.title()).slice(0,60));
  } catch(e){ log.push(name+' FAIL '+String(e).slice(0,80)); try{ await p.screenshot({ path: `${OUT}/${name}.png` }); }catch{} }
  console.log(log.join(' | '));
  await p.context().close();
}
await b.close();
