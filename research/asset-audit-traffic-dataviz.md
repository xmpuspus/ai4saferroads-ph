# Asset Audit: traffic-intelligence + dataviz-ph -> ai4saferroads-ph

Extraction-only audit for the ADB "AI for Safer Roads" build (Safe-System speed-limit
map of Metro Manila + optional animated speed-safety-across-cities/over-time companion).
No quality critique. Goal: transplantable assets + the legal data envelope.

Source repos:
- `/Users/xavier/Desktop/traffic-intelligence` (edsa-traffic-intelligence) — CLAUDE.md only; holds the legally-vetted PH road-data envelope.
- `/Users/xavier/Desktop/dataviz-ph` (dataviz.ph) — animated bubble engine, ETL, vercel.json, social-demo recipe.

---

## (a) PH road-data legal envelope

Source of truth: `traffic-intelligence/CLAUDE.md`, Section 2 (Non-Negotiable Constraints)
and Section 3 (Data Sources). ToS status was verified on **2026-04-21**. The file's own
rule: any source not on the GREEN list must be re-verified against its current ToS, with
the specific clause cited, before use. Default answer is **no**.

### GO (GREEN — use freely with attribution)

| Source | What it gives the speed-safety build | Legal basis (quoted from CLAUDE.md, verified 2026-04-21) |
|---|---|---|
| OpenStreetMap / Overpass | Road topology, segment geometry, intersection geometry, landmarks. The road network the speed-limit map is drawn on; also carries `maxspeed=*` tags where mapped. | "ODbL, attribution required ... Use for EDSA segment boundaries, intersection geometry, basemap." (Sec 3 GREEN table) |
| MMDA TNAV (mmda.gov.ph) | Categorical Light/Moderate/Heavy per segment/direction, every 10-15 min, Metro Manila arterials incl. EDSA. Closest legal proxy for an "operating speed" / congestion signal. | "Public gov site, no formal ToS. Scrape politely (1 req / 30s). Keep raw HTML archive." (Sec 3 GREEN; Sec 2 rule 5) |
| DPWH Road Traffic Information (2,849 stations) | Batch survey station counts, nationwide. Volume / classified-count context behind speed exposure. | "Public gov. Secondary; not real-time." (Sec 3 GREEN table) |
| data.gov.ph — AADT (Annual Average Daily Traffic) | Annual nationwide AADT, historical extracts. Exposure denominator for risk-per-vehicle framing; the "over time / across cities" axis material. | "Open gov data. Pair with FOI for granular EDSA history." (Sec 3 GREEN table) |
| Sakay.ph GTFS (github.com/sakayph/gtfs) | Static transit network (jeepney/bus/rail), Metro Manila. Multimodal overlay / vulnerable-road-user context. | "MIT. Staleness flagged Nov 2025; verify freshness on each pull." (Sec 3 GREEN table) |
| FOI.gov.ph (MMDA) | Historical EDSA flow 2018-present, incident data. 20-day request cycle. Long-run trend + crash/incident history. | "Open. Prior requests partially successful. File early." (Sec 3 GREEN table) |
| @MMDA on X (read-only) | Advisories (incidents, closures, clearances). Event overlay only. | "X free-tier read API. Cache aggressively." Sec 2 rule 6: stay within free-tier caps, no bulk archive. |

YELLOW (display-only, never extract values):
- Mapbox Traffic v1 vector tiles — **basemap overlay only, never extract values, attribution mandatory** (Sec 3 YELLOW; Sec 2 rule 2 permits Mapbox tiles *for display only*).
- MRT-3 / LRT-1 status via social — fragile, supplementary correlation signal only.

### HARD NO (RED — no exceptions)

The single governing rule, quoted verbatim (Sec 3 "Hard RED"):

> "Waze CCP and Waze livemap; Google Maps Distance Matrix/Routes/Directions as a stored
> dataset; TomTom Traffic Flow/Incidents/Stats; HERE Traffic API v7; Mapbox Movement
> Data; LTFRB CPUVMS / ETMS GPS; Grab/Angkas/JoyRide telemetry."

Per-source rationale (Sec 2, verified 2026-04-21):
- **Waze** (rule 1): "Waze for Cities is government-partner-only; T&C prohibit public redistribution. Waze livemap scraping violates Waze ToS explicitly (anti-automation clause)."
- **Google Maps traffic** (rule 2): "Google Maps Platform Service-Specific Terms 3.2.3 forbid storing Directions/Routes/Distance Matrix content beyond 30 days. A historical public dataset is not permitted."
- **TomTom / HERE / Mapbox Movement** (rule 3): "TomTom has a derivative-work ban, HERE has an open-source-incompatibility clause, Mapbox Movement is enterprise-only. All three are ToS-incompatible with an open-source citizen dashboard."
- **LTFRB CPUVMS/ETMS GPS + Grab/Angkas/JoyRide telemetry** (rule 4): "All closed. Do not attempt to scrape or reverse-engineer."

### Implication for an "operating speed" open proxy

No GREEN source exposes a numeric operating-speed feed in stored form. Every probe-based
speed dataset (Waze/Google/TomTom/HERE/Mapbox Movement) is HARD NO for a stored, open,
redistributable dataset. So a legal open "operating speed" layer must be **derived**, not
ingested: MMDA TNAV categorical congestion (Light/Moderate/Heavy per segment) is the only
GREEN near-real-time speed-state proxy, and it is categorical, not km/h. For the
Safe-System speed-limit map, the GREEN stack supports: posted/limit layer + road class
(OSM `maxspeed`/`highway`), exposure (AADT, DPWH counts), and a congestion-state proxy
(MMDA TNAV) — but a true measured km/h operating-speed layer cannot be sourced legally in
stored form from commercial probe data. Frame operating speed as a TNAV-derived categorical
proxy or collect it independently.

---

## (b) Reusable assets table

| Repo | File path | What it does (1 line) | How it helps the speed-safety build |
|---|---|---|---|
| dataviz-ph | `public/app.js` | The whole client chart engine: ECharts init, `makeView`, 5 chart types (bubbles/line/bar/map/panels), trails, compare-year, autoplay sequencer, hash state, a11y mirror table. | Drop-in animated bubble + choropleth-map engine for "speed-safety across cities / over time". The map type already does PH choropleth; the bubble type already does the Rosling sweep. |
| dataviz-ph | `public/app.js` lines ~3872-3944 (`startPlay`/`stopPlay`/`playTick`) | Self-managed `setInterval` year-stepper (1500ms if <=3 panels else 1100ms, speed-scaled); ECharts `animationDurationUpdate` tweens bubbles between years; `universalTransition`/forced series-id reuse morphs points across frames. | This IS the animation pattern: frames = panel years, ECharts tweens positions on `setOption`. Copy `playTick`+`startPlay` verbatim for the over-time companion view. |
| dataviz-ph | `public/app.js` lines ~771-855 (auto-trails), ~1447-1576 (map/`registerMap`/`visualMap`) | Auto-trail builder (markLine of a point's path across years) + `echarts.registerMap("ph-provinces", geo)` choropleth with sequential-blue `visualMap`. | Trails = "which cities moved most on speed-vs-crash"; the choropleth block is the Metro Manila speed-limit map renderer (swap geojson + value field). |
| dataviz-ph | `public/vendor/echarts-custom-5.6.0-r2.min.js` (666 KB) | Custom ECharts 5.6.0 build (Canvas + SVG renderers, DataZoomInside), vendored + SRI-loaded, no build step. | Use the same vendored, no-build, SRI-pinned ECharts. Library = **Apache ECharts 5.6.0**, animation via `setOption` tweening, not a frame-render loop. |
| dataviz-ph | `etl/build.py` | ETL orchestrator: pulls every source, computes derived series + seeded 10k-shuffle permutation p-values, runs `validate` gate, writes `public/data/*.json`. | Template for the road-data ETL: one orchestrator, per-source modules, derived indicators, stats baked at build, JSON out. Permutation-p machinery reusable for speed-vs-crash correlation claims. |
| dataviz-ph | `etl/philgeps.py` | Source module: fetches remote parquet chunks into `.etl_cache/`, dedups on stable id, attributes to PSGC, groups by (area, year). | Pattern for fetch-cache-attribute-aggregate. Reuse the cache-dir + dedup-on-stable-id + PSGC-join shape for OSM/DPWH/AADT ingestion. |
| dataviz-ph | `etl/validate.py` | Build gate: coverage (N units/anchor year), (psgc,year) uniqueness, range bounds, YoY-jump + median-drift warnings; raises on violation. | Drop in as the data gate so a wrong-numbers commit fails CI. Adapt coverage to "all Metro Manila cities present per year". |
| dataviz-ph | `etl/geojson_build.py` | Builds `ph-provinces.geojson` dissolved to the app's 82-unit model (faeldon/philippines-json-maps ADM2, PSGC-coded), committed like the vendored JS. | Same recipe to build a Metro Manila city/barangay geojson for the speed-limit choropleth. Run once, commit the asset. |
| dataviz-ph | `etl/interpolate.py`, `etl/psa_openstat.py`, `etl/psgc.py` | Year interpolation, PSA OpenStat puller, PSGC name normalization/parent-HUC folding. | `psgc.py` name-normalization is mandatory for joining any PH dataset to geometry. Reuse as-is. |
| dataviz-ph | `vercel.json` | Static `public/` deploy, `framework: null`, `cleanUrls`, strict CSP (`script-src 'self'`, `frame-ancestors *` for embeds), security headers, tiered cache (vendor immutable 1yr, data 1h, app.js/style.css 5min). | Copy verbatim. Exactly the static-site + embeddable-iframe + locked-CSP posture ADB will want. Swap cache paths. |
| dataviz-ph | `docs/record_demo.js` | Playwright recorder: fresh context, deviceScaleFactor 2, `recordVideo` webm, syncs to named animation beats via `window.__datavizph_arcBeat()`. | The hero-GIF recorder. Reuse the Playwright `recordVideo` + beat-sync skeleton for an autoplay speed-safety hero. |
| dataviz-ph | `docs/record_linkedin_demo.js` | Social-cut recorder: square (1080x1080) / landscape (1280x720) via `DEMO_MODE`, injects CSS to hide chrome, drives play + tab switches via `window.__datavizph_startPlay/stopPlay`. | The social/LinkedIn demo recipe. Square + landscape, chrome-hiding CSS, scripted clicks. Reuse for the ADB share cut. |
| dataviz-ph | ffmpeg recipe (commit `66c7248` body) | Two-pass palette GIF: `ffmpeg -ss 1.5 -i in.webm` -> palettegen `max_colors=96` + paletteuse `bayer_scale=5`, `setpts=PTS/2.0` (2x speed), `fps=9`, `scale=680`. Cuts 5.9MB -> 2.3MB. | The webm->GIF conversion recipe. Use the same two-pass palette params for a small, sharp social GIF. |
| dataviz-ph | `docs/build_og_cards.js` + `etl/build_share_pages.py` | Per-view OG/share cards: build-time `/s/<id>` pages with computed meta + 1200x630 PNGs rendered via Playwright. | If the build needs shareable per-view cards (e.g. per-city speed-safety), this is the static-site-friendly pattern (crawlers don't run JS, so pre-render). |
| dataviz-ph | `tests/test_committed_data_integrity.py`, `tests/browser/`, `.github/workflows/ci.yml`+`smoke.yml` | Data-gate-against-real-committed-JSON test + Playwright browser tests (self-skip without Chromium) + CI (ruff+pytest, SHA-pinned) + 6-hourly prod smoke. | Reuse the CI shape: real-data gate blocks wrong numbers, browser test asserts the chart actually rendered a series, smoke watches prod. |
| dataviz-ph | `pyproject.toml` + `requirements.lock` | Exact-pinned runtime deps (httpx, pandas 3.0.3, pyarrow, shapely, tenacity, numpy) that reproduce committed data byte-for-byte. | Copy the pinned, reproducible-build dep set for the ETL. |
| traffic-intelligence | `CLAUDE.md` (Sec 2-3, 11) | The legal envelope (above) + the required attribution string. | Governs every data-source decision. Attribution string (Sec 11) is the template for the ADB site footer. |

### Stack summary (what to transplant)

- **Animation engine:** Apache **ECharts 5.6.0** (vendored, SRI, no build step). Frames are panel years; a `setInterval` (`startPlay`/`playTick`) advances the year and calls `setOption`, and ECharts tweens bubble positions via `animationDurationUpdate` + stable series ids / `universalTransition`. Choropleth map is the same engine (`registerMap` + `visualMap`).
- **ETL pattern:** one `build.py` orchestrator -> per-source modules (fetch into `.etl_cache/`, dedup on stable id, normalize names via `psgc.py`, attribute to geometry, group by area/year) -> `validate.py` gate (coverage/uniqueness/range, raises on violation) -> write `public/data/*.json` + `manifest.json` provenance. Stats (permutation p-values) baked at build, never hardcoded in prose.
- **Deploy:** static `public/` to Vercel, `framework: null`, `cleanUrls`, locked CSP with `frame-ancestors *` for embeds, tiered cache. Push to main auto-deploys.
- **Demo recipe:** Playwright `recordVideo` (deviceScaleFactor 2) driven by exposed `window.__*_startPlay/stopPlay` hooks + beat accessors -> webm -> two-pass-palette ffmpeg GIF (`max_colors=96`, `bayer_scale=5`, `setpts=PTS/2.0`, `fps=9`, `scale=680`). Square + landscape via a `DEMO_MODE` env switch.
