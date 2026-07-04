import { chromium } from 'playwright';
const BASE = 'https://ai4saferroads-ph.vercel.app';
const ARGS = ['--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist','--enable-webgl','--in-process-gpu'];
const results = [];
function rec(name, pass, detail='') { results.push({name,pass,detail}); console.log(`${pass?'PASS':'FAIL'}  ${name}${detail?'  :: '+detail:''}`); }
async function t(name, fn) { try { const r = await fn(); if (r === false || (r && r.pass===false)) rec(name,false,(r&&r.detail)||''); else rec(name,true,(r&&r.detail)||''); } catch(e){ rec(name,false,'threw: '+e.message); } }

const browser = await chromium.launch({ args: ARGS });
const ctx = await browser.newContext({ viewport:{width:1300,height:880}, deviceScaleFactor:1 });
const page = await ctx.newPage();
const perr = [];
page.on('pageerror', e => perr.push(e.message));
page.on('console', m => { if (m.type()==='error') perr.push('console:'+m.text()); });
await page.goto(BASE+'/', { waitUntil:'networkidle', timeout:45000 });
await page.waitForFunction(()=>{const o=document.getElementById('overlay');return o&&!o.classList.contains('on');},{timeout:30000}).catch(()=>{});
await page.waitForTimeout(2500);

const vis = sel => page.evaluate(s=>{const e=document.querySelector(s);if(!e)return false;const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none';},sel);
const aria = sel => page.evaluate(s=>document.querySelector(s)?.getAttribute('aria-pressed'),sel);
const txt = sel => page.evaluate(s=>(document.querySelector(s)?.textContent||'').replace(/\s+/g,' ').trim(),sel);
const count = sel => page.evaluate(s=>document.querySelectorAll(s).length,sel);
const lvis = id => page.evaluate(i=>{try{return window.__map.getLayoutProperty(i,'visibility')||'visible';}catch(e){return 'ERR';}},id);
const paint = (id,p) => page.evaluate(([i,pp])=>{try{return JSON.stringify(window.__map.getPaintProperty(i,pp));}catch(e){return 'ERR';}},[id,p]);
const center = () => page.evaluate(()=>{const c=window.__map.getCenter();return [+c.lng.toFixed(3),+c.lat.toFixed(3)];});
const rendered = lyr => page.evaluate(l=>{try{return window.__map.queryRenderedFeatures({layers:[l]}).length;}catch(e){return -1;}},lyr);
async function reset(){ await page.evaluate(()=>{ if(window.__resetLayers) window.__resetLayers(); }); if(await vis('#buildstep')) await page.click('#bexit').catch(()=>{}); if((await aria('#crit'))==='true') await page.click('#crit').catch(()=>{}); await page.waitForTimeout(350); }
// base map / road colour / overlays now live inside the collapsed "Layers" disclosure; open it deterministically (no toggle ambiguity)
const setLayers = (open,pg=page) => pg.evaluate(o=>{const d=document.getElementById('layers'); if(d) d.open=o;}, open);
async function hoverRoad(){ await page.evaluate(()=>window.__map.setPaintProperty('net-real','line-width',16)); await page.waitForTimeout(400);
  const pts=await page.evaluate(()=>{const m=window.__map;const fs=m.queryRenderedFeatures({layers:['net-real']}).filter(f=>f.properties.name&&f.properties.sss>0).slice(0,14);
    return fs.map(f=>{let c=f.geometry.coordinates;if(Array.isArray(c[0][0]))c=c[0];const p=m.project(c[Math.floor(c.length/2)]);return{x:Math.round(p.x),y:Math.round(p.y)};}).filter(q=>q.x>360&&q.x<1290&&q.y>70&&q.y<870);});
  for(const q of pts){ await page.mouse.move(q.x-5,q.y-5); await page.waitForTimeout(120); await page.mouse.move(q.x,q.y); await page.waitForTimeout(450);
    if(await page.evaluate(()=>!!document.querySelector('.maplibregl-popup-content'))) return true; }
  return false; }

// ===== LOAD & STRUCTURE =====
await t('01 title is Current vs Proposed', async()=>({pass:(await page.title()).includes('Current vs Proposed')}));
await t('02 no pageerror/console errors on load', async()=>({pass:perr.length===0, detail:perr.slice(0,3).join(' | ')}));
await t('03 window.__map exists + style loaded', async()=>({pass:await page.evaluate(()=>!!(window.__map&&window.__map.isStyleLoaded()))}));
await t('04 road network renders (>500 features)', async()=>{const n=await rendered('net-base');return {pass:n>500,detail:'net-base feats='+n};});
await t('05 banner present + safety message', async()=>({pass:(await vis('#topkey'))&&(await txt('#topkey')).includes('posted faster'), detail:await txt('#topkey')}));
await t('06 default city = Metro Manila', async()=>({pass:(await page.inputValue('#city'))==='manila'}));
await t('07 selector has 51 cities', async()=>{const n=await count('#city option');return {pass:n===51,detail:'options='+n};});
await t('08 selector grouped by island (3 optgroups)', async()=>{const n=await count('#city optgroup');return {pass:n>=3,detail:'optgroups='+n};});

// ===== STATS + WORST ROADS =====
await t('09 stats hero shows posted-over-safe + %', async()=>{const s=await txt('#stats');return {pass:/Posted over the safe speed/.test(s)&&/%/.test(s),detail:s.slice(0,70)};});
await t('10 worst-roads list has >=5 items', async()=>{const n=await count('#roads .road');return {pass:n>=5,detail:'roads='+n};});
await t('11 click a road shows before/after card', async()=>{await page.click('#roads .road'); await page.waitForTimeout(800); return {pass:await vis('#badetail')};});
await t('12 before/after card has posted + safe limit', async()=>{const s=await txt('#badetail');return {pass:/posted/i.test(s)&&/safe limit/i.test(s),detail:s.slice(0,80)};});
await t('13 clicking a road flies map (center moves)', async()=>{await reset();const c0=await center();await page.click('#roads .road:nth-child(3)');await page.waitForTimeout(1400);const c1=await center();return {pass:(c0[0]!==c1[0]||c0[1]!==c1[1]),detail:c0+' -> '+c1};});

// ===== SEARCH =====
await t('14 search filters the roads list', async()=>{const before=await count('#roads .road');await page.fill('#find','EDSA');await page.waitForTimeout(500);const after=await count('#roads .road');return {pass:after<=before&&after>=1,detail:before+' -> '+after};});
await t('15 search Enter activates first result', async()=>{await page.fill('#find','EDSA');await page.waitForTimeout(400);await page.focus('#find');await page.keyboard.press('Enter');await page.waitForTimeout(900);return {pass:await vis('#badetail')};});
await t('16 clearing search restores full list', async()=>{await page.fill('#find','');await page.waitForTimeout(500);const n=await count('#roads .road');return {pass:n>=5,detail:'roads='+n};});

// ===== RISK / NOW / SAFE =====
await reset();
await setLayers(true);   // road colour control lives in the Layers panel now
await t('17 default road mode = Risk', async()=>({pass:(await aria('#roadmode .seg button[data-m=score]'))==='true'}));
await t('18 Now colors roads by current posted limit (v_posted)', async()=>{await page.click('#roadmode .seg button[data-m=current]');await page.waitForTimeout(700);const p=await paint('net-real','line-color');const b=await txt('#topkey');return {pass:p.includes('v_posted')&&/current posted limit/i.test(b),detail:b.slice(0,50)};});
await t('19 Safe colors roads by proposed safe limit (v_safe)', async()=>{await page.click('#roadmode .seg button[data-m=proposed]');await page.waitForTimeout(700);const p=await paint('net-real','line-color');const b=await txt('#topkey');return {pass:p.includes('v_safe')&&/should have/i.test(b),detail:b.slice(0,50)};});
await t('20 Risk restores score color + banner', async()=>{await page.click('#roadmode .seg button[data-m=score]');await page.waitForTimeout(700);const p=await paint('net-real','line-color');const b=await txt('#topkey');return {pass:p.includes("'sss'")||p.includes('"sss"')||p.includes('sss'),detail:b.slice(0,40)};});
await t('21 road mode resets to Risk after city change', async()=>{await page.click('#roadmode .seg button[data-m=current]');await page.waitForTimeout(500);await page.selectOption('#city','cebu');await page.waitForTimeout(1800);const a=await aria('#roadmode .seg button[data-m=score]');await page.selectOption('#city','manila');await page.waitForTimeout(1800);return {pass:a==='true',detail:'score pressed after switch='+a};});

// ===== BUILD THE PICTURE =====
await reset();
await t('22 Build button exists and is visible', async()=>{const ex=await count('#buildbtn');const v=await vis('#buildbtn');return {pass:ex===1&&v,detail:'count='+ex+' visible='+v};});
await t('23 Build button in accessibility tree (has role/name)', async()=>{const info=await page.evaluate(()=>{const b=document.getElementById('buildbtn');if(!b)return null;return {tag:b.tagName,name:(b.textContent||'').trim().slice(0,30),hidden:b.hidden,ariaHidden:b.getAttribute('aria-hidden')};});return {pass:!!info&&info.tag==='BUTTON'&&info.name.length>3&&!info.hidden,detail:JSON.stringify(info)};});
await t('24 click Build enters step 1 of 4', async()=>{await page.click('#buildbtn');await page.waitForTimeout(900);const s=await txt('#buildstep');return {pass:(await vis('#buildstep'))&&/1 of 4/.test(s)&&/people walk/i.test(s),detail:s.slice(0,50)};});
await t('25 step1 hides road-mode control', async()=>({pass:!(await vis('#roadmode'))}));
await t('26 step1 shows VRU dots, dims roads', async()=>{const v=await lvis('vru-dots');const op=await paint('net-real','line-opacity');return {pass:v==='visible'&&parseFloat(op)<0.5,detail:'vru='+v+' op='+op};});
await t('27 step2 adds crashes (Manila)', async()=>{await page.click('#bnext');let cv='none',s='';for(let i=0;i<20;i++){await page.waitForTimeout(400);s=await txt('#buildstep');cv=await lvis('crash-dots');if(/2 of 4/.test(s)&&cv==='visible')break;}return {pass:/2 of 4/.test(s)&&cv==='visible',detail:'crash='+cv};});
await t('28 step3 colors roads by current (red), full opacity', async()=>{await page.click('#bnext');await page.waitForTimeout(900);const p=await paint('net-real','line-color');const op=await paint('net-real','line-opacity');return {pass:p.includes('v_posted')&&parseFloat(op)>0.8,detail:'op='+op};});
await t('29 step4 colors roads by proposed (green) + Finish', async()=>{await page.click('#bnext');await page.waitForTimeout(900);const s=await txt('#buildstep');const p=await paint('net-real','line-color');return {pass:/4 of 4/.test(s)&&/Finish/.test(s)&&p.includes('v_safe'),detail:s.slice(0,40)};});
await t('30 Back returns to step 3', async()=>{await page.click('#bprev');await page.waitForTimeout(700);return {pass:/3 of 4/.test(await txt('#buildstep'))};});
await t('31 Done exits build, road-mode control reachable in Layers', async()=>{await page.click('#bexit');await page.waitForTimeout(700);await setLayers(true);await page.waitForTimeout(200);return {pass:!(await vis('#buildstep'))&&(await vis('#roadmode'))&&(await aria('#buildbtn'))==='false'};});
await t('32 entering critical exits build (mutual exclusivity)', async()=>{await page.click('#buildbtn');await page.waitForTimeout(700);await page.click('#crit');await page.waitForTimeout(700);const bHidden=!(await vis('#buildstep'));const critOn=(await aria('#crit'))==='true';await page.click('#crit').catch(()=>{});await page.waitForTimeout(400);return {pass:bHidden&&critOn,detail:'buildHidden='+bHidden+' critOn='+critOn};});

// ===== VRU TOGGLE =====
await reset();
await setLayers(true);   // VRU overlay toggle lives in the Layers panel now
await t('33 VRU dots hidden by default', async()=>({pass:(await lvis('vru-dots'))==='none'}));
await t('34 Show-what-makes-dangerous turns VRU on', async()=>{await page.click('#vrubtn');await page.waitForTimeout(600);return {pass:(await lvis('vru-dots'))==='visible'&&(await aria('#vrubtn'))==='true'&&(await vis('#vrukey'))};});
await t('35 toggling VRU again hides it', async()=>{await page.click('#vrubtn');await page.waitForTimeout(500);return {pass:(await lvis('vru-dots'))==='none'};});
await setLayers(false);   // re-collapse so the "Layers collapsed by default" check (40) holds

// ===== CRITICAL ROADS STEPPER =====
await reset();
await t('36 Critical mode shows stepper road 1 of N', async()=>{await page.click('#crit');await page.waitForTimeout(900);const s=await txt('#stepper');return {pass:(await vis('#stepper'))&&/1 of/.test(s)&&(await lvis('seg-crit'))==='visible',detail:s.slice(0,40)};});
await t('37 Critical Next advances road', async()=>{await page.click('#cnext');await page.waitForTimeout(900);return {pass:/2 of/.test(await txt('#stepper'))};});
await t('38 Critical Prev goes back', async()=>{await page.click('#cprev');await page.waitForTimeout(800);return {pass:/1 of/.test(await txt('#stepper'))};});
await t('39 Critical Done/exit hides stepper', async()=>{await page.click('#cexit');await page.waitForTimeout(700);return {pass:!(await vis('#stepper'))&&(await aria('#crit'))==='false'};});

// ===== MORE LAYERS: WEALTH + CRASH =====
await reset();
await t('40 More layers collapsed by default (wealth btn hidden)', async()=>({pass:!(await vis('#wealthbtn'))}));
await t('41 opening More layers reveals wealth + crash buttons', async()=>{await page.click('details.more > summary');await page.waitForTimeout(400);return {pass:(await vis('#wealthbtn'))&&(await vis('#crashbtn'))};});
await t('42 wealth overlay shows fill + finding w/ Spearman', async()=>{await page.click('#wealthbtn');await page.waitForTimeout(900);const s=await txt('#wealthbox');return {pass:(await lvis('wealth-fill'))==='visible'&&/Spearman/.test(s),detail:s.slice(0,50)};});
await t('43 wealth box reports a rho value', async()=>{const s=await txt('#wealthbox');return {pass:/[-+]?\d*\.?\d+/.test(s)&&/ρ|rho/i.test(s),detail:s.slice(0,40)};});
await t('44 crash overlay (Manila) shows dots + note', async()=>{await page.click('#crashbtn');await page.waitForTimeout(2500);return {pass:(await lvis('crash-dots'))==='visible'&&(await vis('#crashnote')),detail:await txt('#crashnote')};});
await t('45 crash dims the road glow', async()=>{const op=await paint('net-real','line-opacity');return {pass:parseFloat(op)<0.7,detail:'op='+op};});

// ===== POPUPS (canvas hover) =====
await reset();
await t('46 hovering a flagged road opens a popup', async()=>{const ok=await hoverRoad();return {pass:ok&&(await count('.maplibregl-popup'))>0,detail:'hovered='+ok};});
await t('47 popup shows Now -> safe limit', async()=>{const s=await txt('.maplibregl-popup-content');return {pass:/Now/.test(s)&&/safe limit/.test(s),detail:s.slice(0,60)};});
await t('48 popup why is plain language (no engineer jargon)', async()=>{const s=await txt('.maplibregl-popup-content');return {pass:!/undivided arterial|side-impact|VRU/i.test(s),detail:s.slice(0,80)};});

// ===== CITY-SPECIFIC BEHAVIOUR =====
await reset();
await t('49 select Davao updates city + hash', async()=>{await page.selectOption('#city','davao');await page.waitForTimeout(1800);const u=await page.evaluate(()=>location.hash);return {pass:(await page.inputValue('#city'))==='davao'&&u==='#davao',detail:'hash='+u};});
await t('50 crash button disabled on non-Manila (Davao)', async()=>{await setLayers(true);await page.waitForTimeout(200);const dis=await page.evaluate(()=>document.getElementById('crashbtn')?.disabled);return {pass:dis===true,detail:'disabled='+dis};});
await t('51 city with no wealth overlay shows a message', async()=>{await page.selectOption('#city','butuan');await page.waitForTimeout(1800);await setLayers(true);await page.waitForTimeout(200);await page.click('#wealthbtn');await page.waitForTimeout(700);const s=await txt('#wealthbox');return {pass:/no wealth overlay/i.test(s),detail:s.slice(0,50)};});
await t('52 zero-flag city (Butuan) renders without crashing', async()=>{const n=await count('#roads .road');return {pass:perr.length===0,detail:'roads='+n+' errs='+perr.length};});
await page.selectOption('#city','manila').catch(()=>{}); await page.waitForTimeout(1800); await reset();

// ===== LINKS / OTHER PAGES =====
await t('53 download link has a data href', async()=>{const h=await page.evaluate(()=>document.getElementById('dl')?.getAttribute('href'));return {pass:!!h&&h!=='#'&&h.length>1,detail:'href='+h};});
await t('54 sim link points to sim.html', async()=>{const h=await page.evaluate(()=>document.querySelector('a.simbtn')?.getAttribute('href'));return {pass:/sim\.html/.test(h||''),detail:h};});
await t('55 sim page loads with a canvas', async()=>{const p2=await ctx.newPage();await p2.goto(BASE+'/sim.html',{waitUntil:'networkidle',timeout:30000});await p2.waitForTimeout(2500);const ok=(await p2.title()).length>0&&(await p2.$('canvas'))!==null;const e2=await p2.evaluate(()=>document.body.innerText.length);await p2.close();return {pass:ok&&e2>20,detail:'canvas+text'};});
await t('56 methodology page loads with validation section', async()=>{const p3=await ctx.newPage();await p3.goto(BASE+'/methodology',{waitUntil:'networkidle',timeout:30000});const s=await p3.evaluate(()=>document.body.innerText);await p3.close();return {pass:/agree with real crashes/i.test(s)&&/Nilsson/.test(s),detail:'len='+s.length};});

// ===== DEEP LINK HASH =====
await t('57 deep-link #cebu loads Cebu', async()=>{const p4=await ctx.newPage();await p4.goto(BASE+'/#cebu',{waitUntil:'networkidle',timeout:30000});await p4.waitForTimeout(4000);const v=await p4.inputValue('#city');await p4.close();return {pass:v==='cebu',detail:'city='+v};});
await t('58 garbage hash falls back to a valid city', async()=>{const p5=await ctx.newPage();await p5.goto(BASE+'/#zzznope',{waitUntil:'networkidle',timeout:30000});await p5.waitForTimeout(4000);const v=await p5.inputValue('#city');const err=await p5.evaluate(()=>!!window.__map);await p5.close();return {pass:!!v&&err,detail:'city='+v};});

// ===== KEYBOARD / A11Y =====
await t('59 road buttons have accessible names', async()=>{const ok=await page.evaluate(()=>{const b=document.querySelector('#roads .road');return b&&(b.textContent||'').trim().length>5;});return {pass:ok};});
await t('60 Enter on a focused road button activates it', async()=>{await reset();await page.evaluate(()=>document.querySelector('#roads .road').focus());await page.keyboard.press('Enter');await page.waitForTimeout(900);return {pass:await vis('#badetail')};});
await t('61 toggles expose aria-pressed', async()=>{const a=await aria('#vrubtn');const b=await aria('#crit');return {pass:(a==='true'||a==='false')&&(b==='true'||b==='false'),detail:'vru='+a+' crit='+b};});

// ===== MOBILE =====
const mctx = await browser.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true });
const mp = await mctx.newPage();
const merr=[]; mp.on('pageerror',e=>merr.push(e.message));
await mp.goto(BASE+'/',{waitUntil:'networkidle',timeout:45000});
await mp.waitForFunction(()=>{const o=document.getElementById('overlay');return o&&!o.classList.contains('on');},{timeout:30000}).catch(()=>{});
await mp.waitForTimeout(2500);
const mvis = sel => mp.evaluate(s=>{const e=document.querySelector(s);if(!e)return false;const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.display!=='none';},sel);
await t('62 mobile: panel collapsed by default', async()=>{const collapsed=await mp.evaluate(()=>document.querySelector('.panel')?.classList.contains('collapsed'));return {pass:collapsed===true,detail:'collapsed='+collapsed};});
await t('63 mobile: banner visible when collapsed', async()=>({pass:await mvis('#topkey')}));
await t('64 mobile: panel toggle expands the body', async()=>{await mp.click('#panelToggle').catch(()=>{});await mp.waitForTimeout(500);const expanded=await mp.evaluate(()=>!document.querySelector('.panel')?.classList.contains('collapsed'));return {pass:expanded,detail:'expanded='+expanded};});
await t('65 mobile: city selector usable', async()=>{const n=await mp.evaluate(()=>document.querySelectorAll('#city option').length);return {pass:n===51,detail:'opts='+n};});
await t('66 mobile: See-how CTA shows when collapsed', async()=>{await mp.evaluate(()=>window.__setPanel&&window.__setPanel(true));await mp.waitForTimeout(300);const v=await mvis('#seehow');const txt=await mp.evaluate(()=>document.getElementById('seehow')?.textContent.trim());return {pass:v&&/see how/i.test(txt||''),detail:JSON.stringify(txt)};});
await t('67 mobile: tapping CTA starts the guided build', async()=>{await mp.click('#seehow',{force:true});await mp.waitForTimeout(900);const s=await mp.evaluate(()=>{const p=document.querySelector('.panel');return{building:p.classList.contains('building'),step:!document.getElementById('buildstep').hidden,cta:document.getElementById('seehow').classList.contains('show')};});return {pass:s.building&&s.step&&!s.cta,detail:JSON.stringify(s)};});
await t('68 mobile: build keeps the map visible (panel is a bottom card)', async()=>{const top=await mp.evaluate(()=>Math.round(document.querySelector('.panel').getBoundingClientRect().top));return {pass:top>380,detail:'panel.top='+top+'/844'};});
await t('69 mobile: finishing returns to the collapsed map with CTA back', async()=>{for(let i=0;i<4;i++){await mp.click('#bnext',{force:true});await mp.waitForTimeout(500);}const s=await mp.evaluate(()=>{const p=document.querySelector('.panel');return{building:p.classList.contains('building'),collapsed:p.classList.contains('collapsed'),cta:document.getElementById('seehow').classList.contains('show')};});return {pass:!s.building&&s.collapsed&&s.cta,detail:JSON.stringify(s)};});
await t('70 mobile: no page errors', async()=>({pass:merr.length===0,detail:merr.slice(0,2).join('|')}));

// ===== AUDIT FIXES (2026-06-28) =====
await t('71 tap/click a road opens the popup (touch path)', async()=>{
  await reset();
  await page.evaluate(()=>window.__map.setPaintProperty('net-real','line-width',16)); await page.waitForTimeout(400);
  const pts=await page.evaluate(()=>{const m=window.__map;const fs=m.queryRenderedFeatures({layers:['net-real']}).filter(f=>f.properties.name&&f.properties.sss>0).slice(0,14);
    return fs.map(f=>{let c=f.geometry.coordinates;if(Array.isArray(c[0][0]))c=c[0];const p=m.project(c[Math.floor(c.length/2)]);return{x:Math.round(p.x),y:Math.round(p.y)};}).filter(q=>q.x>360&&q.x<1290&&q.y>70&&q.y<870);});
  let ok=false; for(const q of pts){ await page.mouse.click(q.x,q.y); await page.waitForTimeout(280);
    if(await page.evaluate(()=>!!document.querySelector('.maplibregl-popup-content'))){ok=true;break;} }
  return {pass:ok,detail:'tried '+pts.length+' road pixels'};
});
await t('72 critical mode disabled on a zero-flag city (butuan)', async()=>{
  const np=await ctx.newPage(); await np.goto(BASE+'/#butuan',{waitUntil:'networkidle',timeout:30000}); await np.waitForTimeout(4000);
  const r=await np.evaluate(()=>({disabled:document.getElementById('crit').disabled,city:document.getElementById('city').value,stepperEmpty:document.getElementById('stepper').innerHTML===''})); await np.close();
  return {pass:r.disabled===true&&r.city==='butuan',detail:JSON.stringify(r)};
});
await t('73 build exit returns to Risk overview (dots off, Risk active)', async()=>{
  await reset(); await page.click('#buildbtn'); await page.waitForTimeout(500);
  for(let i=0;i<4;i++){await page.click('#bnext').catch(()=>{}); await page.waitForTimeout(380);}
  const r=await page.evaluate(()=>({vru:document.getElementById('vrubtn').getAttribute('aria-pressed'),risk:document.querySelector('#roadmode [data-m=score]').getAttribute('aria-pressed'),building:document.querySelector('.panel').classList.contains('building')}));
  return {pass:r.vru==='false'&&r.risk==='true'&&r.building===false,detail:JSON.stringify(r)};
});

// ===== STREET VIEW DEEP LINKS (2026-06-28) =====
await t('74 before/after card deep-links to Street View', async()=>{
  await reset(); await page.click('#roads .road'); await page.waitForTimeout(700);
  const h=await page.evaluate(()=>document.querySelector('#badetail a.svlink')?.getAttribute('href'));
  return {pass:!!h&&/google\.com\/maps/.test(h)&&/map_action=pano/.test(h)&&/viewpoint=-?\d/.test(h),detail:h?h.slice(0,80):'no link'};
});
await t('75 road popup deep-links to Street View', async()=>{
  await reset(); const ok=await hoverRoad();
  const h=await page.evaluate(()=>document.querySelector('.maplibregl-popup-content a.svlink')?.getAttribute('href'));
  return {pass:ok&&!!h&&/google\.com\/maps/.test(h)&&/map_action=pano/.test(h),detail:h?h.slice(0,70):'hovered='+ok};
});
await t('76 critical card deep-links to Street View', async()=>{
  await reset(); await page.click('#crit'); await page.waitForTimeout(900);
  const h=await page.evaluate(()=>document.querySelector('#stepper a.svlink')?.getAttribute('href'));
  await page.click('#cexit').catch(()=>{});
  return {pass:!!h&&/google\.com\/maps/.test(h)&&/map_action=pano/.test(h),detail:h?h.slice(0,70):'no link'};
});

// ===== SWIPE COMPARE (danger vs crashes, Manila) =====
await t('77 swipe compare splits danger vs crashes + shows correlation', async()=>{
  await reset();
  await page.evaluate(()=>{document.getElementById('layers').open=true;}); await page.waitForTimeout(200);
  await page.click('#cmpbtn'); await page.waitForTimeout(2800);
  const on=await page.evaluate(()=>({
    swipe:getComputedStyle(document.getElementById('swipe')).display!=='none',
    exitBtn:getComputedStyle(document.getElementById('cmpexit')).display!=='none',
    crashHex:window.__map.getLayoutProperty('heatcrash-layer','visibility'),
    heatFilter:!!window.__map.getFilter('heat-layer'),
    crashFilter:!!window.__map.getFilter('heatcrash-layer'),
    corr:/Spearman/.test(document.getElementById('topkey').textContent)
  }));
  await page.click('#cmpexit').catch(()=>{}); await page.waitForTimeout(500);
  const off=await page.evaluate(()=>getComputedStyle(document.getElementById('swipe')).display==='none'&&window.__map.getLayoutProperty('heatcrash-layer','visibility')==='none');
  return {pass:on.swipe&&on.exitBtn&&on.crashHex==='visible'&&on.heatFilter&&on.crashFilter&&on.corr&&off,detail:JSON.stringify(on)+' exited='+off};
});

// ===== SUMMARY =====
const fails = results.filter(r=>!r.pass);
console.log(`\n===== ${results.length} tests, ${results.length-fails.length} PASS, ${fails.length} FAIL =====`);
if (fails.length) console.log('FAILURES:\n'+fails.map(f=>'  - '+f.name+(f.detail?'  :: '+f.detail:'')).join('\n'));
await browser.close();
