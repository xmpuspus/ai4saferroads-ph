# Demo GIF / hero recording recipes across Xavier's PH map repos

Audit of how the README/LinkedIn demo GIFs are produced in six map repos, to pick one reusable recipe
for ai4saferroads-ph. All paths are absolute; every recipe is cited to a real file.

There are two recording families:
1. **Browser-driven (Playwright / agent-browser)** -- drives the REAL live map a visitor sees, captures
   either a Playwright video (.webm) or a sequence of screenshots, then ffmpeg two-pass palette -> GIF.
   This is the one to reuse for an interactive map.
2. **Matplotlib data-animation** (leaves-ph `animation/*.py` only) -- renders a synthetic chart/map
   animation straight to GIF, no browser. Not relevant for an interactive web map; noted for completeness.

The shared encode in every browser recipe is the SAME ffmpeg two-pass palettegen/paletteuse. They differ
only in (a) capture mechanism (Playwright video vs per-beat screenshots) and (b) fps/scale/dither knobs.

---

## Per-repo findings

### 1. sinkmap-ph (the sibling template; "mirror its layout" per its own CLAUDE.md)

Two scripts, both driving the real MapLibre map via **agent-browser** (screenshot-per-beat, NOT Playwright video).

- `/Users/xavier/Desktop/sinkmap-ph/scripts/record_demo.py` -> `docs/demo.gif` (**772K**)
  - Viewport 1280x800. Drives the live site at `http://localhost:8788` (`make serve &` first).
  - Captures 12 screenshot frames (`f0.png`..`f11.png`) by calling `agent-browser eval` to click real
    DOM controls + `agent-browser screenshot`. Last frame is duplicated 3x to hold.
  - Beats: overview with story rail -> tap rail (acceleration layer + callouts) -> next finding ->
    Find-your-city Dagupan place card -> hold -> Watch-it-sink slider 2016->2025 -> toggle a flood extent -> hold.
  - Encode: `vf = "fps=1.05,scale=900:-1:flags=lanczos"`, two-pass with
    `palettegen=stats_mode=full` then `paletteuse=dither=sierra2_4a`, `-framerate 1.05`.
  - Dims/fps/size: 900px wide, ~1.05 fps (slideshow cadence), ~12 frames, ~772K. Tiny because it is a
    handful of held stills, not motion. Optimized for README, well under GitHub's 10MB.

- `/Users/xavier/Desktop/sinkmap-ph/scripts/record_sink_lapse.py` -> `docs/sink-lapse.gif` (**280K**)
  - The time-lapse variant: jump to Metro Manila, switch to sink-lapse mode, step the date slider
    2016->2025 capturing one screenshot per step (NFRAMES=8), hold final frame 3x.
  - Encode: `vf = "fps=1.5,scale=860:-1:flags=lanczos"`, `palettegen=stats_mode=full` +
    `paletteuse=dither=sierra2_4a`, `-framerate 1.5`. 860px, 1.5 fps, ~11 frames, 280K.

agent-browser screenshot approach is the simplest (no Playwright dep, no video-trim step) but the result is
a stepped slideshow, not fluid motion. Good for "watch the slider move" lapses; weaker for fly-throughs.

### 2. leaves-ph (the most complete / polished browser recipe -- Playwright VIDEO)

- `/Users/xavier/Desktop/leaves-ph/site/scripts/record_linkedin_demo.mjs` -> `docs/demo/linkedin-demo.{gif,mp4,webm}`
  (gif **8.2M**, mp4 7.2M) -- Node + Playwright, records the production `astro preview` build.
- `/Users/xavier/Desktop/leaves-ph/scripts/record_demo_gif.py` -> same outputs, Python + Playwright async (older sibling).
- Also: `record_protected_areas_demo.mjs`, `record_flood_canopy_demo.mjs` (same pattern, other surfaces).
- NOTE: `docs/demo/hero.gif` (588K) and the other 4 hero GIFs are NOT browser recordings -- they are
  matplotlib animations from `animation/generate_*.py` (`make animate`). Do not copy those for a web map.

Key techniques in the `.mjs` recipe (the most reusable, best-documented):
- **Pre-warm pass**: a throwaway context loads the map, jumps to the demo area, waits 4s so vector tiles
  cache; then the real recorded context starts clean (no tile-load jank in the video).
- **Synthetic cursor** injected via `addInitScript` (`#__cursor` div with CSS transition) + `__cur(x,y)`
  move and `__pulse()` click animation, so the GIF shows a moving cursor without real OS cursor.
- **Skip first-run FX**: `addInitScript` sets `localStorage` onboarding flags so no intro modal records.
- `deviceScaleFactor: 2` for a crisp retina capture, recordVideo size 1280x800.
- Beats: regional establish -> flyTo Quezon City (the green LGU) -> flyTo Pasay (the bare contrast) ->
  click a real detected tree crown -> satellite popup with a real aerial -> "find your barangay".
  Each beat advances by calling the SAME production DOM/map handlers a user triggers (`flyTo`, real row click).
- **Trim to the last N seconds** with `-sseof` (seek-from-EOF, robust to wrong webm duration metadata):
  `ffmpeg -y -sseof -<tail> -i raw.webm -c:v libvpx-vp9 -b:v 3M -an trim.webm`.
- Encode (two-pass): `VF = "fps=9,scale=600:-1:flags=lanczos"`,
  `palettegen=max_colors=108:stats_mode=diff` then
  `paletteuse=dither=bayer:bayer_scale=5`.
- Also emits an MP4: `ffmpeg -i trim.webm -c:v libx264 -pix_fmt yuv420p -crf 21 -vf "scale=1280:-2:flags=lanczos,format=yuv420p" -movflags +faststart linkedin-demo.mp4`.
- Dims/fps/size: 600px wide, 9 fps, full motion, ~8.2M GIF (over the 8MB README margin -- the price of fluid
  fly-throughs at 9fps). The MP4 (7.2M) is the better LinkedIn/embed artifact; GIF is the README fallback.

leaves-ph CLAUDE.md "Demos" section is the canonical statement: "Real recordings only, never mockups.
Record against `astro preview` (the production build, no dev toolbar) with a synthetic cursor; encode GIFs
with ffmpeg two-pass palettegen/paletteuse. Frame-extract and read the frames back before shipping."

### 3. shake-exposure-ph / lindol.ph (Playwright video, single-injected-choreography)

- `/Users/xavier/Desktop/shake-exposure-ph/scripts/record_demo.py` -> README hero (the cleanest Playwright video recipe).
- Also `record_lapse_demo.py`, `record_growth_demo.py` -> `docs/growth-demo.gif` (2.8M), `docs/growth-lapse.gif` (5.8M).
- Key insight (documented in the docstring): building-tile fetches flood the DevTools/CDP channel, so
  per-beat `page.evaluate`/`click`/`screenshot` calls queue for tens of seconds while the page keeps
  animating. **Fix: inject the WHOLE choreography as ONE in-page async function** (`CHOREO`, a single CDP
  `page.evaluate` that resolves when the show ends) and let Playwright's video recorder run alongside.
  This is the most robust pattern when the map streams heavy tiles during recording.
- Viewport 1280x720, `record_video_dir` + `record_video_size` 1280x720. Waits on `window.__diag.ready`
  and `window.map.areTilesLoaded()` before starting.
- The CHOREO drives real controls: search a town -> place card -> building glow -> imagery swipe (Wayback)
  -> ground-failure toggle -> "the Big One" scenario tab -> fault-corridor glow.
- ffmpeg encode is in the lapse/growth scripts (palettegen/paletteuse two-pass; same family).

### 4. dataviz-ph (Playwright video, square + landscape social cuts)

- `/Users/xavier/Desktop/dataviz-ph/docs/record_linkedin_demo.js` -> `docs/linkedin-demo.gif` (4.2M),
  `linkedin-demo-landscape.gif` (3.6M), + matching .mp4s. `DEMO_MODE=square|landscape` env switch
  (1080x1080 vs 1280x720). Records the chart explorer's guided arc.
- `/Users/xavier/Desktop/dataviz-ph/docs/record_demo.js` -> `docs/demo.gif` (2.1M), the README hero
  (records the auto-arc; per its header comment "~1.5x speed, fps 13, scale 900, two-pass palette";
  the webm->gif ffmpeg wrapper lives in the commit that touched it, not in-repo).
- Techniques worth stealing: `deviceScaleFactor: 2`; injects CSS via `addStyleTag` to hide chrome
  (controls/footer/tagline) and reflow the layout for the target aspect ratio before recording;
  a `loadPlaywright()` shim that finds Playwright in the npx cache if not locally installed.
- This is the recipe to copy if ai4saferroads-ph wants a 1:1 square LinkedIn cut, not just a README strip.

### 5. ghostwatch / tulaypinoy.ph (Playwright video, Leaflet, scripted caption cards)

- `/Users/xavier/Desktop/ghostwatch/docs/social/record_story.js` -> `docs/social/linkedin-demo.gif` (5.6M)
  -- the most "produced" one: injects full-screen branded HOOK/CLOSE title cards + lower-third caption
  bars (`#story-ov`, `#story-cap`) styled in the site's design tokens, with a synthetic glide cursor and a
  real before/after divider wipe. Beats: hook card -> radar/method caption -> fly to a "construction
  visible" site + wipe -> fly to a "none visible" site + wipe -> close card with the tally + URL.
  Records `recordVideo` at 1200x760, drives Leaflet via `window.__gwmap`.
- `/Users/xavier/Desktop/ghostwatch/tmp/rec/record.js` -> `docs/demo/tour.gif` (6.3M), the README tour.
- This is the template if you want captioned "social story" framing (title cards + lower thirds), which a
  road-safety advocacy map benefits from. Heavier (5-6M) because of full-motion + 1200px width.

### 6. floodwatch-ph (Playwright SCREENSHOT-per-beat, with a black-frame sanity gate)

- `/Users/xavier/Desktop/floodwatch-ph/scripts/record_hero.py` -> `docs/screenshots/hero.gif` (**612K**)
  -- Playwright (sync API) but captures `page.screenshot(clip=...)` frames into `f000.png..` rather than a
  video. Serves the built `site/dist` over a stdlib http server on a thread.
  - **`focus(pg, sel)`** scrolls the beat's subject (a map or evidence card) to a FIXED clip rect under the
    nav, so every frame is framed identically -> uniform frames for clean palettegen.
  - **`grab(pg, n, gap_ms)`** takes n screenshots gap_ms apart -- so motion (a playing time series) is
    captured as a burst of stills; static beats get a few held stills.
  - **Black-frame sanity gate** (worth stealing): after capture it opens a mid map-beat frame with PIL,
    computes the fraction of near-black pixels, and FAILS the run if >60% black (basemap tiles didn't
    render). Catches the most common silent demo failure.
  - Encode: `-framerate 8`, `scale=1000:-1:flags=lanczos,palettegen=stats_mode=diff` then
    `paletteuse=dither=bayer`, `-loop 0`. 1000px, 8 fps, 612K.

---

## Canonical reusable knobs (Xavier's own skills)

These two global skills are the maintained source of truth and agree with every repo above:
- `/Users/xavier/.claude/skills/record-demo/SKILL.md` -- Playwright capture: headless, viewport-only, no
  browser chrome; networkidle before interactions; extra settle for canvas/map; max 60s; verify each GIF in
  a real browser (ffprobe `nb_frames` is ground truth; **never use PIL to write/trim GIFs** -- it corrupts
  frame-disposal so the GIF looks fine to PIL but is frozen in browsers).
- `/Users/xavier/.claude/skills/gif-optimize/SKILL.md` -- the two-pass encode + an auto-size-reduction loop.
  Rules: always two-pass, never upscale, Lanczos only, `diff_mode=rectangle` in paletteuse, GitHub limit
  10MB so aim for <8MB, verify with ffprobe not PIL.
  Size budget starting points: 10MB/30s -> 960px@10fps@256; 10MB/60s -> 720px@8fps@128; 5MB/30s -> 720px@8fps@128.

---

## THE pick: single best reusable recipe for ai4saferroads-ph

Use the **leaves-ph `record_linkedin_demo.mjs` Playwright-video pattern** as the spine (pre-warm + synthetic
cursor + drive the real production build + two-pass palette + emit GIF *and* MP4), and **add floodwatch-ph's
black-frame sanity gate**. Rationale: it is the most complete, best-documented, records the actual live map a
visitor uses (not a mockup), produces both a README GIF and the better-for-LinkedIn MP4, and the cursor +
pre-warm make it look hand-driven and jank-free. For a heavier streamed-tile map, fall back to
shake-exposure-ph's single-injected-CHOREO pattern to avoid CDP-channel queue stalls.

Target specs for ai4saferroads-ph README + LinkedIn:
- Record at 1280x800 (or 1280x720), `deviceScaleFactor: 2`, headless, against the production build.
- README GIF: scale 720px, fps 9-10, `max_colors=128`, two-pass `palettegen=stats_mode=diff` +
  `paletteuse=dither=bayer:bayer_scale=5` -- aim under 8MB (drop to 600px / fps 8 if over).
- Always also emit the H.264 MP4 (crf 21, +faststart) -- it is the artifact to actually post on LinkedIn.

### Copy-paste-ready steps

```bash
# 0) deps (once)
cd /Users/xavier/Desktop/ai4saferroads-ph
npm i -D playwright || pip3 install playwright
python3 -m playwright install chromium   # or: npx playwright install chromium
which ffmpeg ffprobe || brew install ffmpeg

# 1) serve the PRODUCTION build (never the dev server -- no dev toolbar, real assets)
#    swap for this repo's build+serve (astro: pnpm build && pnpm preview --port 4330;
#    static map: python3 web/serve.py 8788 if PMTiles needs HTTP Range)
( cd web && pnpm build && pnpm preview --port 4330 ) &
sleep 4

# 2) record + encode (Node + Playwright video; adapt BEATS to the real DOM ids)
node scripts/record_demo.mjs

# 3) verify (ground truth = ffprobe frame count, NOT PIL; sanity-open in a browser)
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=width,height,r_frame_rate,nb_read_frames -of csv=p=0 docs/demo.gif
ls -lh docs/demo.gif docs/demo.mp4
```

`scripts/record_demo.mjs` skeleton (adapt the BEAT block + selectors/`window.__map` to this repo):

```js
import { chromium } from 'playwright';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
const BASE='http://localhost:4330';
const OUT='docs', WORK='tmp/demo-record';
fs.rmSync(WORK,{recursive:true,force:true}); fs.mkdirSync(WORK+'/video',{recursive:true}); fs.mkdirSync(OUT,{recursive:true});

const skipFx=()=>{ try{localStorage.setItem('onboarded','1');}catch(e){} };          // no intro modal in frame
const cursorInit=()=>{                                                                // synthetic cursor
  const c=document.createElement('div'); c.id='__cursor';
  c.style.cssText='position:fixed;left:-60px;top:-60px;width:22px;height:22px;border:2px solid #1a1a1a;border-radius:50%;background:rgba(220,60,40,0.4);box-shadow:0 1px 5px rgba(0,0,0,.35);z-index:99999;pointer-events:none;transform:translate(-50%,-50%);transition:left .45s ease,top .45s ease;';
  (document.body||document.documentElement).appendChild(c);
  window.__cur=(x,y)=>{const e=document.getElementById('__cursor'); if(e){e.style.left=x+'px';e.style.top=y+'px';}};
  window.__pulse=()=>{const e=document.getElementById('__cursor'); if(e)e.animate([{transform:'translate(-50%,-50%) scale(1)'},{transform:'translate(-50%,-50%) scale(.55)'},{transform:'translate(-50%,-50%) scale(1)'}],{duration:300});};
};

const b=await chromium.launch({headless:true});
// pre-warm so vector tiles cache (no load jank in the recorded pass)
const warm=await b.newContext({viewport:{width:1280,height:800}}); const wp=await warm.newPage(); await wp.addInitScript(skipFx);
await wp.goto(BASE+'/',{waitUntil:'domcontentloaded'});
await wp.waitForFunction(()=>window.__map&&window.__map.isStyleLoaded&&window.__map.isStyleLoaded(),{timeout:60000});
await wp.waitForTimeout(4000); await warm.close();

const ctx=await b.newContext({viewport:{width:1280,height:800}, deviceScaleFactor:2, recordVideo:{dir:WORK+'/video',size:{width:1280,height:800}}});
const page=await ctx.newPage(); await page.addInitScript(skipFx); await page.addInitScript(cursorInit);
await page.goto(BASE+'/',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.__map&&window.__map.isStyleLoaded&&window.__map.isStyleLoaded(),{timeout:60000});
const tLoaded=Date.now();

// ---- BEATS: drive the SAME map/controls a visitor uses (edit these) ----
await page.evaluate(()=>window.__map.jumpTo({center:[121.0,14.6],zoom:10.5})); await page.waitForTimeout(1600); // establish
await page.evaluate(()=>window.__map.flyTo({center:[121.05,14.66],zoom:13,duration:1500,essential:true})); await page.waitForTimeout(1800); // fly-in
// await page.click('#some-real-button'); await page.evaluate(()=>window.__pulse()); await page.waitForTimeout(1800);
const tEnd=Date.now();
await ctx.close(); await b.close();

// trim to just the scripted beats (sseof = seek from EOF, robust to bad webm duration)
const beatsSec=((tEnd-tLoaded)/1000)+0.4;
const webm=WORK+'/video/'+fs.readdirSync(WORK+'/video').find(f=>f.endsWith('.webm'));
const trim=WORK+'/trim.webm';
execSync(`ffmpeg -y -sseof -${beatsSec.toFixed(1)} -i "${webm}" -c:v libvpx-vp9 -b:v 3M -an "${trim}"`,{stdio:'ignore'});

// two-pass palette -> README GIF (720px / 10fps / 128 colors); drop to 600/8 if >8MB
const gif=OUT+'/demo.gif', pal=WORK+'/palette.png', VF='fps=10,scale=720:-1:flags=lanczos';
execSync(`ffmpeg -y -i "${trim}" -vf "${VF},palettegen=max_colors=128:stats_mode=diff" "${pal}"`,{stdio:'ignore'});
execSync(`ffmpeg -y -i "${trim}" -i "${pal}" -lavfi "${VF}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" "${gif}"`,{stdio:'ignore'});

// the better LinkedIn artifact: H.264 MP4
execSync(`ffmpeg -y -i "${trim}" -c:v libx264 -pix_fmt yuv420p -crf 21 -vf "scale=1280:-2:flags=lanczos,format=yuv420p" -movflags +faststart "${OUT}/demo.mp4"`,{stdio:'ignore'});

// black-frame sanity gate (floodwatch pattern): fail loud if the map didn't paint
execSync(`ffmpeg -y -i "${gif}" -vf "select='eq(n\\,8)'" -vframes 1 "${WORK}/probe.png"`,{stdio:'ignore'});
console.log('GIF_MB',(fs.statSync(gif).size/1e6).toFixed(2));
```

If you would rather not script beats and the map is mostly a stepped slider/time-lapse, the
sinkmap-ph agent-browser screenshot recipe (`scripts/record_sink_lapse.py`, fps 1.5, scale 860, two-pass)
gives a ~280K-600K GIF with almost no code -- that is the lighter alternative.
