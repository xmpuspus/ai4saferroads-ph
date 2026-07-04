# Web-app / map UX audit — patterns to reuse in ai4saferroads-ph

Source repos read (frontends only):
- `~/Desktop/sinkmap-ph/web/index.html` + `methodology.html` (MapLibre map app, single file)
- `~/Desktop/shake-exposure-ph/web/index.html` + `methodology.html` (MapLibre + PMTiles map app, single file; brand lindol.ph)
- `~/Desktop/dataviz-ph/public/index.html` + `style.css` + `app.js` + `docs/og.html` (ECharts data-explorer, no map basemap)
- `~/Desktop/leaves-ph/` — NO web frontend. It is a Python detection/animation pipeline (`animation/`, `detection/`, `pipeline/`) that emits GIFs/MP4s. Nothing to extract for a map UX. Skipped.

The two map apps (sinkmap, lindol) are the closest templates for a road-safety map. dataviz is the source for chart panels, the play/time engine, the OG-card pattern, and the accessibility mirror.

---

## 1. Color systems + typography

### sinkmap.ph (light, scientific, diverging)
File: `sinkmap-ph/web/index.html` lines 14, 333-335.
```
--ink:#10212b  --muted:#5b6b75  --line:#e2e8ec  --sink:#b2182b  --rise:#2166ac  --bg:#f7f9fa
```
- Diverging ramp (RdBu, colorblind-safe), used as the legend gradient (line 37):
  `linear-gradient(90deg,#b2182b,#ef8a62,#fddbc7,#f7f7f7,#d1e5f0,#67a9cf,#2166ac)`
- Analysis ramps deliberately NOT red/green (line 333-335): accel = PuOr `#7f3b08,#ed9b39,#f7f6f5,#998fbf,#2d004b`; tilt single-hue purple `#f7f7f7,#7b1fa2`. The repo comment is explicit: changing accel colors means updating colormap + CSS RAMP + the blurb color words together.
- Exposure glow color `#ff5a1f`.

### lindol.ph (dark, dramatic, sequential-hazard)
File: `shake-exposure-ph/web/index.html` lines 26-29.
```
--bg:#0b0f16  --ink:#eef2f7  --muted:#9aa6b6  --line:rgba(255,255,255,.12)
--accent:#ff6a3d  --mmi6:#ffe08a  --mmi7:#f3823f  --mmi8:#b5231a
```
- This is the premium one for a hazard map. Near-black bg + one hot accent (`#ff6a3d`) + a 3-stop hazard ramp. The full MMI legend scale (line 290-296) is 7 stops: `#a0c8f0,#bce8a8,#f7f776,#fdc330,#f3823f,#d6492b,#b5231a`.
- Facility category colors (line 1153): school `#f5d76e`, hospital `#ff8da1`, bridge `#8fd0ff`.
- Popup link blue `#8fc1f0`.

### dataviz.ph (light editorial + categorical)
File: `dataviz-ph/public/style.css` lines 1-15.
```
--ink:#111  --muted:#595959  --rule:#e6e6e6  --bg:#fff  --soft:#f7f7f8  --soft2:#f0f0f2
--brand:#0e7c86  --brand-hot:#0a5f67
categorical: --luzon:#2b6cb0 --visayas:#38a169 --mindanao:#d97706 --ncr:#6b46c1 --barmm:#c53030
```
- Sequential single-hue blue RAMP for choropleth/quantile (`app.js` line 57): `["#dce8f5","#9ec3e3","#5a93c7","#2b6cb0","#08306b"]`.

### Typography (consistent across all three)
- Body stack everywhere: `-apple-system, Helvetica, Arial, sans-serif` (lindol/sinkmap) or `-apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif` (dataviz).
- The one premium move: serif for the editorial headline. dataviz uses `Georgia, "Iowan Old Style", Palatino, "Times New Roman", serif` on `#story-headline` and the OG card H1 (style.css line 174, og.html line 19). Sans body, serif hero headline reads "publication", not "dashboard".
- Big stat number is the hook: lindol `.stat` is 38px / weight 680 / `letter-spacing:-.025em` in the accent color (index line 53); sinkmap `.rate` is 30px/700 (line 53). Always `font-variant-numeric:tabular-nums` on any number that updates (lindol line 83/96/171).
- Kicker/eyebrow pattern: 11px, `letter-spacing:.14em`, uppercase, muted (lindol `.kicker` line 37).

---

## 2. Map style, basemap, layer paint (the copy-paste expressions)

### Basemaps (no API key in any of them)
- sinkmap: CARTO light raster `https://{a,b}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png` (index line 293-296). Clean light base for a scientific read.
- lindol: Esri World Imagery raster `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` + a 15%-opacity `#0b0f16` background dim layer on top to mute the satellite (index line 664-670). This satellite + dim-scrim combo is what makes lindol feel premium and serious. `maxZoom:18`, raster `maxzoom:17` (older imagery 404s past 17).
- Nav control: `new maplibregl.NavigationControl({showCompass:false})` placed `bottom-right` in both.

### Image-overlay layers (sinkmap's whole data model)
sinkmap drapes pre-rendered colorized PNG rasters as `type:"image"` sources over geographic bounds (index line 559-561):
```js
map.addSource("v-"+id,{type:"image",url:png,
  coordinates:[[west,north],[east,north],[east,south],[west,south]]});
map.addLayer({id,type:"raster",source,paint:{"raster-opacity":0.85}});
```
Flood overlays use `"raster-resampling":"nearest"` for crisp class edges (line 593). This is the cheapest way to put a continuous model surface on a map — render the ramp server-side, ship a PNG, no vector tiling.

### Per-feature glow (the premium "exposure" look)
- sinkmap building glow (index line 565-566): `circle, radius 3, color #ff5a1f, opacity 0.5, "circle-blur":0.5`. The `circle-blur` is what turns dots into glow.
- lindol per-building fill from PMTiles, zoom-gated, colored by data band (index line 1044-1046):
```js
paint:{
 'fill-opacity':['interpolate',['linear'],['zoom'],10,0,11.5,0.92],
 'fill-color':['interpolate',['linear'],['get','mmi'],6,'#ffe08a',7,'#f3823f',8,'#b5231a',8.4,'#7a1106']}
```
The zoom-driven fill-opacity (invisible at z10, full at z11.5) is the handoff from circles to buildings.

### Proportional exposure circles that fade into the glow (lindol, index line 1069-1074) — strong pattern
```js
paint:{
 'circle-radius':['+',3,['*',0.085,['sqrt',['get','mmi7']]]],   // sqrt = area-true
 'circle-color':'#ff6a3d',
 'circle-opacity':['interpolate',['linear'],['zoom'],11.5,0.55,12.5,0],   // fade OUT as buildings fade IN
 'circle-stroke-color':'#fff','circle-stroke-width':1.1,
 'circle-stroke-opacity':['interpolate',['linear'],['zoom'],11.5,0.85,12.5,0]}
```
The circle fade-out (11.5→12.5) is timed to start only after the building glow is already at full paint, so no zoom band reads empty. Copy this dual-layer choreography directly for "crashes per road segment" circles → individual crash points on zoom.

### Heatmap opacity that varies by zoom (lindol, index line 1149)
`const SHAKE_OPACITY=['interpolate',['linear'],['zoom'],8,0.5,12,0.28];` — faint regional, fainter up close so buildings show through.

### Fault line styling (lindol, index line 1054-1055) — reusable for road centerlines / risk corridors
`line-color:#ff3b30, line-width:2.5, line-dasharray:[2,1.4]`

### Facility points by category match expression (lindol, index line 1167-1170)
```js
'circle-color':['match',['get','kind'],'school',FAC,'hospital',FAC,FAC],
'circle-radius':3.2,'circle-stroke-color':'#0b0f16','circle-stroke-width':0.8
```

### Choropleth (if you want a province/region road-fatality map without a basemap) — dataviz ECharts
`app.js` line 1450 `echarts.registerMap("ph-provinces", geo)`; `visualMap` piecewise for log-skewed data, continuous for bounded % (line 1503-1543); `roam:"scale"` so single-finger drag still scrolls the page on mobile (line 1579).

---

## 3. Interaction patterns

### Time slider + play button ("watch it sink" / "watch it grow") — the signature move
- sinkmap mode toggle Rate vs "Watch it sink" (index line 460-485). The lapse: a range `<input>` 0..N, a play button that `setInterval(...,950)` advancing `FRAME=(FRAME+1)%len`, updating image overlays via `src.updateImage({url})`. Frames preloaded as `new Image()` so playback doesn't flicker (line 553).
- lindol "Watch it grow" (index line 1310-1372): a full-screen overlay (`.grow`, `position:fixed;inset:0`) with its OWN isolated MapLibre map, scrubbing real Esri Wayback historical satellite tiles year by year. Year label 27px accent (`.grow-year`), play/pause, scrub `<input range>`, Esc-to-close, `prefers-reduced-motion` respected. This is the most LinkedIn-worthy single feature in the set — a real before/after time machine over satellite imagery.
- dataviz play engine (`index.html` line 132-148, style.css 994-1048): circular accent `#big-play` bottom-left + a speed pill cycling 1x/2x/0.5x. Year scrub via arrow keys (Home/End jump to first/last). Worth copying for any temporal road-crash trend.

### Story rail (sinkmap) — the best "first-touch insight" pattern
`sinkmap-ph/web/index.html` lines 64-94 (CSS), 200-223 (markup), 359-443 (JS). A bottom card that leads with ONE finding and walks the rest with prev/next chevrons + a dot indicator (`#r-dots`). Tap a card → `selectFinding()` flies the camera (`flyTo duration:900`), toggles the analysis layer, drops labeled callout markers, swaps the inline ramp. Second tap closes it. A `#findings` left drawer is the "see all 10" full list, reusing the same `selectFinding()`. On phones the rail becomes a bottom sheet and controls dock above it via `layoutMobile()` height math. Copy this whole pattern for "top 10 deadliest roads / blackspots — tap to fly there."

### Findings list as panel bullets (lindol, index line 98-102 CSS, 486-506 JS)
Simpler alternative: a `#findings` block of accent-dotted `<li>` lines, text generated from computed numbers (`findings.json`), per-view insight headline that changes with the active tab. Good for "what the data reveals" without a guided tour.

### View/scenario picker tabs (lindol, index line 41-50 CSS, 605-615 JS)
One row per event/scenario; the active row unfolds a one-line provenance (`.vprov` hidden until `.on`). Scales past two tabs. Reuse for "recent year / 5-year / scenario" road-safety views.

### Find-your-place
- sinkmap: a styled `<select>` with optgroups (Measured / Coherence-limited), flies + opens the card (index line 530-545).
- lindol: a live search input + national fallback list + "Use my location" geolocation button (index line 900-946). Diacritic-insensitive matching (`norm()` strips combining marks so "dasmarinas" finds Dasmariñas, line 704). Keyed by stable polygon ID never name (PH town names repeat) — a hard-won correctness rule worth inheriting for any road/LGU lookup.

### Popups / place card
- lindol place card (index line 802-845): one tap answers the point for every view; whole-band words only ("severe shaking here (MMI 7+, modeled)"), nearest mapped fault distance, building/people counts in a 2-col `.pr` grid. A bare map tap opens the same card for any point; tap on an interactive layer keeps its own answer; tap while a card is open dismisses it.
- Overlapping-feature click resolves to the feature whose CENTER is nearest the click, not `e.features[0]` (topmost = often a huge neighbor) (index line 1110-1121). Inherit this for dense crash points.

### Permalink state in the URL (lindol, index line 628-638)
`history.replaceState` writes `v`(view)/`c`(center)/`z`(zoom)/`p`(pinned point)/`lang` on every moveend, so any screenshot or shared link reproduces exactly what its author saw, and `?q=<town>` is a name-addressable deep link. High-value for shareable "look at this road" links.

---

## 4. Panel / legend / HUD / stat-card design

### The glass HUD panel (lindol — the premium container)
`shake-exposure-ph/web/index.html` line 33-36:
```css
.panel{position:absolute;top:18px;left:18px;width:352px;
  background:rgba(11,15,22,.84);backdrop-filter:blur(10px);
  border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:18px;z-index:5}
```
`backdrop-filter:blur(10px)` over a dark translucent fill is the single biggest "premium" tell. The layers control (`.ctrl`) and legend (`.legend`) reuse the exact same recipe (line 141-143, 158-159). sinkmap's panels are the light-mode equivalent: white, `border-radius:10px`, `box-shadow:0 1px 8px rgba(16,33,43,.08)` (index line 18).

### Stat card
- Big accent number + small label below (lindol `.stat` 38px accent / `.stat-label` 12.5px muted, index line 234-235).
- sinkmap place card: 30px/700 rate with a small unit `<small>`, a GO/coherence-limited `.badge` pill, then dashed-underline key/value rows `.kv` (index line 53-57, 500-514).

### Legend ramps
- Gradient bar + min/0/max ticks: sinkmap `.ramp` (index line 36-38) is a CSS `linear-gradient` div with a flex `.ramp-x` of labels under it. The legend text and ramp swap together when the mode changes (`setLegend()`, line 319).
- lindol legend (index line 288-298): a flex row of 7 equal `<span>` color chips + a tick row `4 5 6 7 8`, plus a one-line glyph key ("○ circle = buildings exposed · ▦ buildings glow at zoom-in").

### Inline SVG micro-chart (no chart library) — lindol growth column chart
`shake-exposure-ph/web/index.html` line 1226-1246. Hand-built `<svg viewBox="0 0 316 88">` column chart: 0 baseline (honest proportions), latest bar in accent, endpoints labeled, year ticks. ~20 lines, zero dependency. Perfect for a "fatalities by year" spark-column inside the panel.

### Provenance at the point of claim
Both apps print the data version/retrieval date right under the stat (lindol `#prov`, index line 1013-1015) and a `.src` source string per view. Build trust without a separate page.

---

## 5. 3D / satellite / animation already in use

- No `fill-extrusion` / terrain / map-pitch 3D anywhere. lindol's CLAUDE.md notes a `grow3d.html` was built and then DELETED as "decoration — showed the same number the chart shows." Treat 3D as opt-in only if it carries information the 2D view can't.
- Satellite imagery: lindol's whole basemap is Esri World Imagery (dimmed), and the "watch it grow" feature streams Esri Wayback historical tiles for a real time-lapse (index line 1374-1377, `wayback.maptiles.arcgis.com/.../tile/{rnum}/{z}/{y}/{x}`).
- Animation in use: the pulsing epicenter marker — a pure-CSS `@keyframes ping` ring that scales 0.5→2.6 and fades, `2.4s` infinite, on a `.epi` dot (lindol index line 164-166). Killed under `prefers-reduced-motion`. Reuse for a crash-cluster or blackspot "pulse here" marker. sinkmap preloads lapse frames as `Image()` objects for flicker-free playback. dataviz cross-fades stories with `#chart{transition:opacity .42s}` + `.arc-dim{opacity:.12}` and a one-shot button pulse on hand-off (style.css 1052-1069).
- Honor `prefers-reduced-motion` everywhere: `const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches; const FLY = reduceMotion ? 0 : 900;` (lindol index line 341-342) — kills camera flights and the pulse.

---

## 6. Methodology page, loading/empty states, accessibility, mobile

### Methodology page pattern (consistent template)
`sinkmap-ph/web/methodology.html`, `shake-exposure-ph/web/methodology.html`. Standalone page, same palette as the map, `max-width:760px` centered column, a "← back to the map" link, a lede, sectioned H2s, a validation/results table, and a tinted disclaimer box (`.box.disc`). The required closing block in both: "All data is from public sources. This tool computes statistical/physical indicators only. Any specific allegation requires independent investigation and corroboration." Carry this disclaimer verbatim for a road-safety tool that names dangerous roads.

### Loading / empty / failure states (mature, copy these)
- Loading spinner: `#loading[role=status]::before` CSS keyframe spinner, `border-top-color` accent (dataviz style.css 385-396).
- Buildings streaming: a transient "Loading buildings…" hint on `sourcedataloading`, restored on `sourcedata` (lindol index line 687-697) so a slow mobile fetch doesn't read as broken.
- Never silent-blank: sinkmap renders the findings TEXT before adding map layers, guards each `addLayer` in its own try, retries the findings fetch 3x, and shows a `load_fail` message if all fail (index line 612-648). lindol records each secondary-layer fetch failure and surfaces ONE quiet `#failnote` "Some map layers could not load. Reload to try again." (index line 336-339).
- Map-fallback notice: dataviz shows an amber transient `#chart-notice` strip that auto-hides (index line 103-106, style.css 306-340).

### Accessibility
- `sr-only` text mirror of the data: dataviz ships a full screen-reader `<table>` of the current view + an `aria-live="polite"` one-line summary that updates on year change (only the summary is announced; announcing 82 rows per scrub floods SR) (index line 117-131, 274-281). For a road map: an sr-only ranked table of the deadliest segments.
- `:focus-visible{outline:2px solid <accent>;outline-offset:2px}` everywhere (lindol index line 194, dataviz style.css 499-510).
- WCAG 2.5.5: every touch target forced to `min-height:44px` on small screens (dataviz style.css 1234-1248); even a 22px "i" badge gets a transparent 44px `::before` hit area (style.css 859-867).
- All list rows keyboard-operable (`tabindex="0"` + Enter/Space handlers, lindol index line 935).
- Escape user-supplied/upstream strings before injecting into HTML: `esc()` (lindol index line 325) / `escapeHtml()` (dataviz) — a poisoned upstream record can't become script.
- Reduced-motion branch kills pulses, flights, transitions in all three.

### Mobile / responsive
- Panel → bottom sheet: `@media(max-width:700px){.panel{top:auto;bottom:0;left:0;right:0;border-radius:14px 14px 0 0;max-height:42vh;overflow-y:auto}}` (lindol index line 173-191). sinkmap docks the mode toggle + legend just above the rail via JS height math (`layoutMobile()`, index line 385-392).
- Layers control shrinks and hides its fine print unless the layer is on (lindol line 182-185).
- dataviz: chart goes full-width and leads; finding/caveat get JS-moved below the chart so the chart hits the fold; chart-type buttons become a 2x2 grid; the story-switcher becomes a horizontally-scrolled row with a mask-image fade edge (style.css 1251-1289).

---

## 7. The 3-5 things that make these feel premium — copy these first

1. **Dark satellite basemap + dim scrim + one hot accent + glass-blur HUD.** lindol's `#0b0f16` Esri-imagery base with a 15% dark background layer, plus `backdrop-filter:blur(10px)` translucent panels and a single `#ff6a3d` accent. This combination alone is 80% of the "premium" read. (index line 33-36, 664-670)

2. **A play/time-lapse with a big accent button and a real before/after.** "Watch it sink" image-overlay scrubbing (sinkmap) and especially "Watch it grow" streaming real Esri Wayback historical satellite years (lindol). A genuine time machine over imagery is the most shareable feature here. (sinkmap index line 460-485; lindol index line 1310-1372)

3. **The story rail: lead with ONE finding, walk the rest, each taps to fly + reveal a layer + drop callouts.** Turns a map into a guided narrative on first touch without a wall of text. (sinkmap index line 359-443)

4. **Serif headline over sans body + a big tabular-nums accent stat.** The Georgia hero headline (dataviz) and the 38px accent `.stat` (lindol) make it read as a publication, not a dashboard. (dataviz style.css 174-180; lindol index line 53, 234)

5. **Choreographed zoom handoff: proportional glowing circles that fade out exactly as per-feature detail fades in** (`circle-blur` + zoom-interpolated opacity timed so no zoom band is empty). The motion feels designed, not default. (lindol index line 1069-1074, 1044-1046)

Bonus, near-free and high-trust: the **OG share card as a real 1200×630 HTML page** rendered to PNG (serif headline + the computed finding + a decorative scatter), one per view, with `og:*`/`twitter:*` meta — this is what makes a LinkedIn paste look intentional. (`dataviz-ph/docs/og.html`; lindol `og-card.png` is a real screenshot of the live view at 1200×630.)
