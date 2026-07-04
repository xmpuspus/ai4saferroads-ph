# Design audit: deploy pattern + 3D/satellite/animation precedent

Audited 2026-06-25 for ai4saferroads-ph setup. Read-only across sibling PH map repos.
Target layout for this repo: a single-file static map under `build/web/`.

---

## Part A: Deploy pattern for a single static web/ directory

Three precedents inspected. Two carry a `vercel.json`; sinkmap-ph deploys a bare `web/` dir with no config file at all.

### A.1 sinkmap-ph (NO vercel.json — bare web/ dir, project root = web/)

- No `vercel.json` anywhere in the repo (verified `find -maxdepth 2`).
- The Vercel project is linked at the `web/` subdir: `web/.vercel/project.json`:
  ```json
  {"projectId":"prj_eVXsYPpUJ5A3FCT2cw4d6QKTxe7r","orgId":"team_SV9POOXe0NwYJqOCfp7Jl1ei","projectName":"web"}
  ```
  (org `team_SV9POOXe0NwYJqOCfp7Jl1ei` = `xmpuspus-projects`, personal account)
- `web/.gitignore` is just `.vercel`.
- Deploy method (from `CLAUDE.md` "## Deploy"):
  - Push to `main` = Vercel prod deploy (auto; project "web" under xmpuspus-projects, PERSONAL account).
  - The clean alias must be re-pointed manually every deploy:
    `cd web && vercel alias set <newest web-XXXX deploy> sinkmap-ph.vercel.app`
    (grab the newest from `vercel ls`).
  - Verify-live = screenshot-read-back + `make e2e BASE=https://sinkmap-ph.vercel.app`.
- Local dev: `make serve` -> `web/serve.py` (Range-capable, port 8788).
- Downside of this pattern: NO security headers, NO cleanUrls, NO cache-control, and the alias has to be hand-pointed after every deploy (because there is no Git-connected rootDirectory promoting the alias automatically). This is the weakest of the three. Do not copy it.

### A.2 shake-exposure-ph / lindol.ph (vercel.json present, rootDirectory=web, Git auto-deploy)

`web/vercel.json` (verbatim):
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "geolocation=(self), camera=(), microphone=(), payment=(), usb=(), interest-cohort=()" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: blob: https:; connect-src 'self' https:; worker-src 'self' blob:; child-src 'self' blob:; font-src 'self' data:; manifest-src 'self'" }
      ]
    },
    {
      "source": "/(.*).(json|geojson|csv)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=300, stale-while-revalidate=86400" }
      ]
    },
    {
      "source": "/(.*).(png|webp)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=300, stale-while-revalidate=86400" }
      ]
    }
  ]
}
```

`web/.vercelignore`:
```
data/buildings.pmtiles
data/wvf/buildings.pmtiles
data/exposure_by_municipality.geojson
data/wvf/exposure_by_municipality.geojson
data/digdig/exposure_by_municipality.geojson
data/events/us6000rdrz/exposure_by_municipality.geojson
```

- Build/output/root settings: there is NO `outputDirectory` / `framework` key in this vercel.json. Instead the Vercel **project** has `rootDirectory = web` (set in the dashboard / project settings, documented in CLAUDE.md "## Deploy"). The whole `web/` dir IS the static site; vercel.json only adds headers.
- Deploy method (CLAUDE.md): Vercel project `lindol-ph` (team xmpuspus-projects), rootDirectory `web`, Git-connected to github.com/xmpuspus/lindol-ph. A push to main produces a production deployment (verified `githubCommitSha == HEAD`). Public alias `https://lindol-ph.vercel.app`. Vercel serves Range natively (probed 206) — matters for PMTiles.
- CSP allows `https://unpkg.com` for script + style because MapLibre/PMTiles load from unpkg with SRI hashes. `script-src` includes `'unsafe-inline'`.
- Big binaries (PMTiles >100MB) are kept out of git/deploy via `.vercelignore` and served from Vercel Blob with Range+CORS instead.

### A.3 dataviz.ph (vercel.json present, framework=null, outputDirectory=public, cleanUrls)

`vercel.json` (verbatim):
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": null,
  "outputDirectory": "public",
  "cleanUrls": true,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=(), interest-cohort=()" },
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors *; object-src 'none'" }
      ]
    },
    { "source": "/vendor/(.*)", "headers": [ { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" } ] },
    { "source": "/data/(.*)",   "headers": [ { "key": "Cache-Control", "value": "public, max-age=3600, must-revalidate" } ] },
    { "source": "/locales/(.*)","headers": [ { "key": "Cache-Control", "value": "public, max-age=3600, must-revalidate" } ] },
    { "source": "/og/(.*)",     "headers": [ { "key": "Cache-Control", "value": "public, max-age=86400, must-revalidate" } ] },
    { "source": "/app.js",      "headers": [ { "key": "Cache-Control", "value": "public, max-age=300" } ] },
    { "source": "/style.css",   "headers": [ { "key": "Cache-Control", "value": "public, max-age=300" } ] }
  ]
}
```

`.vercelignore`:
```
# Static deploy: only public/ (the outputDirectory) and vercel.json ship.
/*
!/public
!/vercel.json
```

- Build/output/root: `framework: null` (no build step), `outputDirectory: "public"`, `cleanUrls: true`. Vercel **project root is the repo root** here (NOT a subdir); `outputDirectory` tells Vercel the static files live in `public/`. The `.vercelignore` allowlist (`/*`, then `!/public`, `!/vercel.json`) keeps the 600MB+ ETL cache, .venv, tmp out of the upload.
- Deploy method (CLAUDE.md): Host Vercel, Git integration. Push to `main` auto-deploys prod; feature branches get preview deploys. Vendored ECharts under `public/vendor/` with SRI; strict CSP `script-src 'self'` (no inline scripts, external JS only). CI runs ruff + pytest + Playwright but does NOT deploy (Vercel does).
- Strictest CSP of the three (`script-src 'self'` only — all JS must be same-origin/vendored). `frame-ancestors *` to allow embeds.

### A.4 RECOMMENDED recipe to reuse for build/web/ single-file map

The target here is a map (MapLibre-style), so model it on **shake-exposure-ph** (which serves a MapLibre map with CDN scripts + PMTiles Range), but borrow dataviz's cleaner `outputDirectory`+`.vercelignore` allowlist so the Python/ETL/tests never upload.

Note the rootDirectory choice: shake/sinkmap set the Vercel project `rootDirectory = web` (subdir IS the site). dataviz keeps root at repo root and uses `outputDirectory`. For `build/web/` either works; the cleanest single-file approach is to set the Vercel project **rootDirectory = build/web** in the dashboard and drop a `vercel.json` inside `build/web/` with headers only (the shake model). If you want everything driven from one repo-root config instead, use `outputDirectory: "build/web"` at repo root (the dataviz model) — but then `cleanUrls` + an allowlist `.vercelignore` should live at repo root too.

Cleanest single `build/web/vercel.json` to reuse (headers-only, project rootDirectory set to `build/web`, CSP tuned for a MapLibre + CDN map):
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "geolocation=(self), camera=(), microphone=(), payment=(), usb=(), interest-cohort=()" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: blob: https:; connect-src 'self' https:; worker-src 'self' blob:; child-src 'self' blob:; font-src 'self' data:; manifest-src 'self'" }
      ]
    },
    {
      "source": "/(.*).(json|geojson|csv|pmtiles)",
      "headers": [ { "key": "Cache-Control", "value": "public, max-age=300, stale-while-revalidate=86400" } ]
    },
    {
      "source": "/(.*).(png|webp|jpg)",
      "headers": [ { "key": "Cache-Control", "value": "public, max-age=300, stale-while-revalidate=86400" } ]
    }
  ]
}
```
(If you serve satellite/Esri tiles or remote DEM, widen `connect-src`/`img-src` to `https:` — the rule above already allows `https:` for img and connect, which covers Esri/Carto/NASA raster tiles.)

Deploy commands (the reuse recipe):
```bash
# one-time link (run inside build/web), personal account:
cd build/web && vercel link            # pick/create project under xmpuspus-projects, set rootDirectory=build/web

# thereafter Git auto-deploy: push to main = prod deploy (preferred, like all 3 siblings)
git push origin main

# manual deploy if ever needed:
cd build/web && vercel --prod

# local dev (Range-capable, needed for PMTiles):
python3 build/web/serve.py 8777        # copy serve.py verbatim from shake/sinkmap

# verify live (do NOT trust curl for JS maps — screenshot-read-back + e2e):
make e2e BASE=https://<project>.vercel.app
```

Copy `serve.py` verbatim from `shake-exposure-ph/web/serve.py` or `sinkmap-ph/web/serve.py` (identical Range-capable handler) into `build/web/serve.py` — PMTiles needs HTTP 206 locally; stdlib http.server returns 200+full-file and silently corrupts tiles.

Domain wiring (from sinkmap + lindol CLAUDE.md): dot.ph parks fresh apexes on ParkLogic. Set the apex A record to Vercel and prove before declaring live. Two IPs seen in memory/notes: lindol used `76.76.21.21`; sinkmap's newer note used `216.198.79.1`. Use the IP Vercel shows in the project Domains tab for the specific project, then verify with `curl --resolve <domain>:443:<that-ip> https://<domain>/` and query public resolvers (`dig @8.8.8.8`, `dig @1.1.1.1`), never the local resolver.

---

## Part B: 3D / satellite / animation precedent across the 7 repos

Searched: sinkmap-ph, shake-exposure-ph, leaves-ph, ghostwatch, sar-ghostwatch, dataviz-ph, floodwatch-ph. Verified the load-bearing hits against source.

### three.js / deck.gl / globe.gl — NONE FOUND in any of the 7 repos.
No three.js, no deck.gl, no globe.gl, no react-globe anywhere. No WebGL 3D layer of any kind.

### MapLibre/Mapbox 3D (pitch / terrain / fill-extrusion / DEM / hillshade) — NONE FOUND.
No `setPitch`, `setTerrain`, `fill-extrusion`, `raster-dem`, `hillshade`, or sky layer in any repo. All maps are flat 2D raster/vector. (sinkmap and floodwatch use MapLibre but stay top-down 2D; shake uses MapLibre 2D; ghostwatch uses Leaflet 2D.)

### Satellite / aerial imagery basemaps — FOUND in 4 repos.

**shake-exposure-ph** — `web/index.html` (VERIFIED against source):
- Esri World Imagery as a MapLibre raster source/layer (lines 666-668):
  ```js
  tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
  tileSize:256, maxzoom:17, attribution:'Esri, Maxar, Earthstar Geographics'}},
  layers:[{id:'esri',type:'raster',source:'esri'}, ...]
  ```
- Esri Wayback historical satellite (line 1376, for the "watch it grow" time-lapse), added as a MapLibre raster source with `tileSize:256, maxzoom:17` (lines 1319-1321):
  ```js
  return [`https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/${rnum}/{z}/{y}/{x}`];
  ```
  Note: raster sources are capped at `maxzoom:17` on purpose — Wayback's oldest PH releases 404 past z17 and rural World_Imagery thins out (comment at lines 660-661). This is the most directly reusable satellite basemap pattern: a plain MapLibre raster source pointed at Esri ArcGIS Online, no API key.

**leaves-ph** — `site/src/components/MapView.astro` (Astro, reported by agent; not line-verified but technique consistent with shake):
- Esri World Imagery basemap source (~line 341): `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`, attribution `Imagery © Esri, Maxar, Earthstar Geographics`.
- On-demand Esri `export` endpoint for per-crown aerial snapshots (~line 554): `https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=...&format=jpg&f=image`.

**ghostwatch** — React-Leaflet app (reported by agent):
- Esri World Imagery TileLayer in `web/src/lib/constants.ts` (`TILE_LAYERS.satellite`): `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`, used by `MiningMap.tsx`, `ProjectMap.tsx`.
- Esri Wayback before/after slider in `web/src/components/satellite/WaybackComparison.tsx`: `https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/${rnum}/{z}/{y}/{x}` — Leaflet + CSS-clip wipe transition.

**floodwatch-ph** — MapLibre (Astro), `site/src/lib/realtimeClient.ts` (reported by agent):
- NASA GIBS true-colour basemap `fetchGibsTrueColor()`: `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{id}/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg` (VIIRS/MODIS, dated daily mosaic; OFF by default).
- NASA GIBS VIIRS flood layer `fetchVIIRS()`: `VIIRS_Combined_Flood_1-Day`.

**sinkmap-ph** — NO satellite basemap. Carto light raster only (VERIFIED):
```js
tiles:["https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", ".../b..."]
```
The word "satellite" appears only in prose copy ("measured from satellite radar"). No imagery basemap.

**dataviz-ph** — no map at all (ECharts bubbles). **sar-ghostwatch** — docs only, no code.

### Animated / particle / flow layers — FOUND in 1 repo (floodwatch-ph). No particle/WebGL flows anywhere.

**floodwatch-ph** (reported by agent) — time-series raster frame animation, NOT particles:
- RainViewer radar playback `wireRainPlayback()` in `site/src/components/CorridorWatch.astro` (~lines 1117-1219): `setInterval(step, 900)` swaps radar tile frames; source `https://api.rainviewer.com/public/weather-maps.json`, tiles `{host}{path}/256/{z}/{x}/{y}/2/1_1.png`. Observed past frames only.
- Flood-extent time slider in `site/src/components/MapView.astro` (~lines 565-605): `map.setPaintProperty()` opacity cross-fade (650-700ms) driven by `setInterval(step, 1600)`.

No `deck.gl` TripsLayer, no particle systems, no animated `line-dasharray` flow, no wind/flow fields in any repo.

### Bottom line for ai4saferroads-ph
- Satellite basemap precedent to copy directly: **shake-exposure-ph's plain MapLibre Esri World Imagery raster source** (no key, `maxzoom:17`, the verified config above). Same one-liner works in floodwatch/leaves/ghostwatch.
- Animated traffic/flow precedent: closest is **floodwatch-ph's frame-swap `setInterval` raster animation** (radar/flood time-series). That is the existing animation idiom in the portfolio. There is NO deck.gl/three.js/particle-flow precedent — if animated traffic flows are wanted, this would be NEW for the portfolio (deck.gl TripsLayer or animated GeoJSON line-dasharray would have to be introduced fresh).
- 3D precedent: none. Any pitch/terrain/extrusion/globe would be a first for these repos.
