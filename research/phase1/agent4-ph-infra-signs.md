# PH Road Infrastructure & Sign Data — Independent Signals Beyond OSM Speed Limits

Research date: 2026-07-03. Goal: find open, machine-readable sources for actual speed limits, traffic volume, or road conditions in the Philippines, since OSM posted speed limit tags cover only ~11% of PH streets.

---

## 1. DPWH AADT (Annual Average Daily Traffic)

**Status: NO — still PDF-atlas-only / blocked, confirms and extends the June finding.**

Checked four separate DPWH surfaces:

- **data.gov.ph dataset page**: https://data.gov.ph/index/public/dataset/Annual%20Average%20Daily%20Traffic%20(AADT)/ua1r4ams-fav9-yyqw-kdww-kjbqxpiev6la — page loads but is a thin client-rendered shell; no CSV/API resource could be confirmed attached (WebFetch returned no dataset content, only the portal chrome). Even where data.gov.ph lists AADT, DPWH datasets on this portal typically link out to the source agency rather than hosting a file.
- **DPWH GIS Road Traffic Information page**: https://www.dpwh.gov.ph/dpwh/gis/rti — **SSL certificate error** ("unable to verify the first certificate") on both this URL and the DPWH_ATLAS_2024 URL below. This is a new failure mode beyond the June WAF block — DPWH's own TLS chain is broken for automated fetchers.
- **DPWH Road Data Atlas 2024**: https://www.dpwh.gov.ph/dpwh/DPWH_ATLAS_2024/Road%20Data%202024/index.htm (found via search) — same cert failure; from the URL structure and known DPWH pattern this is the PDF/atlas-style viewer, consistent with the June finding that AADT is atlas-only.
- **ArcGIS REST endpoints**: `https://apps.dpwh.gov.ph/arcgis/rest/services/Leng/RoadNetwork_RoadClassification/MapServer` and `https://apps2.dpwh.gov.ph/arcgis/sharing/portals/self?f=pjson` both return **HTTP 403 Forbidden**. Search corroborates this is a WAF/bot-detection block, not a dead service — a 2020 blog (bnhr.xyz) documents adding `https://apps.dpwh.gov.ph/ArcGIS/rest/services` as a QGIS ArcGIS Feature Service connection successfully, so a real desktop client (different TLS/user-agent fingerprint) may get through where a scripted fetch does not. Unverified whether this still works in 2026.
- **FOI portal**: https://www.foi.gov.ph/requests/annual-average-daily-traffic-aadt-dpwh-401330277645/ and the 2010-2024 AADT + road-project request — both returned 403 to WebFetch. Search snippets confirm these are FOI *requests* (citizen asking DPWH for the data), not resolved datasets with attachments — i.e., AADT is being requested precisely because it isn't otherwise published.

**Net: no change from June.** AADT remains locked in PDF road-data atlases and ArcGIS services fronted by a WAF that blocks scripted access. The only plausible route is a QGIS/ArcGIS-client connection to `apps.dpwh.gov.ph/ArcGIS/rest/services` (untested here) or a manual FOI request.

**Granularity/format if ever obtained:** road-section-level AADT counts by vehicle class (car/truck/bus), per DPWH District Engineering Office, published as PDF tables in the annual Road Data Atlas.

**Feature use:** would be the single best proxy for real-world speed limit *inference* (higher AADT + narrower carriageway = lower practical speed), but currently unusable as a machine-readable input.

---

## 2. Mapillary traffic-sign detections for PH

**Status: PARTIAL — API is real and queryable, coverage is thin and patchy, requires a free developer token.**

- **Auth**: Mapillary Graph API (`graph.mapillary.com`) and tile API (`tiles.mapillary.com`) require a client access token or user access token, sent as `?access_token=TOKEN` or `Authorization: OAuth TOKEN`. Free to register a Mapillary developer app. Source: https://www.mapillary.com/developer/api-documentation
- **Query pattern for speed-limit signs**:
  ```
  https://graph.mapillary.com/map_features?access_token=$TOKEN&fields=id,object_value,geometry,first_seen_at&bbox=minLon,minLat,maxLon,maxLat
  ```
  Filter `object_value` for the `regulatory--maximum-speed-limit-*` sign class family (Mapillary's traffic-sign taxonomy: `{category}--{name}--{appearance-group}`, documented at https://www.mapillary.com/developer/api-documentation/traffic-signs). Mapillary recognizes ~1,500 sign classes across 100 countries, including speed-limit signs.
  - **Hard constraint**: bbox queries against `/map_features` (and `/images`, and detection search) must be **smaller than 0.01 degrees square** (~1.1km x 1.1km at the equator) per query — a whole city requires tiling many small bbox calls.
  - Vector tiles alternative for bulk/visual use: `https://tiles.mapillary.com/maps/vtp/mly_map_feature_traffic_sign/2/{z}/{x}/{y}` (same auth).
  - Rate limit: 10,000 search requests/minute per app (no confirmed free-tier cap beyond that).
- **PH coverage**: no quantitative coverage numbers found for Metro Manila/Cebu/Davao. Mapillary's own Feb 2026 blog post (https://blog.mapillary.com/update/2025/02/26/harnessing-mapillary-for-open-mapping-in-the-philippines) describes **community-driven, still-early collection** — partnerships with biking communities in Metro Manila, and planned 2025 imagery collection in Baguio City and Iloilo City with UP Resilience Institute/UP Industrial Engineering. This confirms coverage is real but sparse and geographically uneven (secondary roads and provincial cities are explicitly described as gaps being actively filled, not already covered). No image-density or detection-count figures were published. Google Street View is separately noted (via search) as denser/more consistent for PH than Mapillary or KartaView.

**Feature use:** for road segments that DO have Mapillary imagery, the `map_features` traffic-sign query gives an actual point-located speed-limit sign value — a much stronger ground-truth signal than OSM's `maxspeed` tag where present. But given sparse/patchy PH coverage, this would need to be treated as a supplementary layer (fill-in where available) rather than a primary feature, and a per-segment coverage flag should be computed before trusting an "absence of sign" as "no limit."

---

## 3. Building footprints as a road-segment crowdedness/roof-density proxy

**Status: YES (Google Open Buildings v3) / YES (Microsoft Global ML + regional PH-specific set) — both genuinely downloadable, format differs.**

### Google Open Buildings v3
- Source: https://sites.research.google/gr/open-buildings/ ; Earth Engine catalog: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons
- Coverage: Africa, Latin America/Caribbean, South Asia and Southeast Asia (Philippines included since the Oct 2022 SE Asia expansion) — 1.8B building detections from 50cm satellite imagery.
- **Format: CSV only** (not GeoJSON/shapefile natively) — one CSV per S2 level-4 cell, up to 7.8GB per cell, 178GB total polygon dataset worldwide. Each row: lat/lon, area, confidence score, WKT polygon, Plus Code.
- **Download paths**: (a) Earth Engine asset `GOOGLE/Research/open-buildings/v3/polygons` for programmatic country-clip extraction; (b) official Colab notebook that downloads by country/region (`open_buildings_download_region_polygons.ipynb`); (c) manual S2-cell click-through on the download page; (d) HDX curated country-level cuts for ~20 countries (Philippines' presence on HDX not confirmed in this pass — worth a direct check at data.humdata.org/organization/google-open-buildings).
- License: CC BY 4.0, free commercial/non-commercial use with attribution.

### Microsoft Global ML Building Footprints
- Global repo: https://github.com/microsoft/GlobalMLBuildingFootprints — country/quadkey files listed in `dataset-links.csv` at `https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv`. Format: line-delimited GeoJSON packed as `.csv.gz`. License: ODbL / CDLA Permissive 2.0 (source states CDLA Permissive 2.0).
- **PH-specific regional set**: https://github.com/microsoft/IdMyPhBuildingFootprints — 88.6M building polygons across Indonesia, Malaysia, Philippines combined, imagery-sourced Maxar 2016-2020, line-delimited GeoJSON. This is the more targeted PH entry point.

### Thinking Machines TM Open Buildings (PH-specific, hand-annotated, best quality but narrow coverage)
- Source repo: https://github.com/thinkingmachines/ph-open-buildings ; HDX: https://data.humdata.org/dataset/tm-open-buildings-philippines (direct fetch 403'd, confirmed via search cache)
- **12 cities only**: Dagupan, Palayan, Navotas, Mandaluyong, Muntinlupa, Legazpi, Iloilo, Mandaue, Tacloban, Zamboanga, Davao, Cagayan de Oro. 250m x 250m manually-annotated tiles with roof/building attributes, traced from Mapbox Satellite Streets imagery (Aug-Sep 2023). License ODbL (feeds back into OSM). Available via Kaggle and HDX.
- Highest-quality but far narrower geography than the two automated global datasets above.

**Feature use:** building-footprint density (count or roof area per 100m buffer around a road segment) is a genuine, currently-untapped crowdedness/urbanicity proxy computable today for essentially the whole country via Google Open Buildings v3 or Microsoft's IdMyPhBuildingFootprints, with the 12-city Thinking Machines set as a higher-fidelity validation subset.

---

## 4. OSM road width/lane-count/oneway completeness for PH

**Status: NO dedicated PH completeness study found — general OSM literature only, no PH-specific numbers.**

- HDX hosts the standard HOTOSM export: https://data.humdata.org/dataset/hotosm_phl_roads (direct fetch 403'd; confirmed live via search cache) — monthly-updated export including `highway`, `surface`, `smoothness`, `width`, `lanes`, `oneway`, `bridge`, `source` tags. This is a *data source*, not a completeness study — it doesn't quantify what fraction of PH ways actually carry `width`/`lanes` values (this repo's own OSM speed-limit figure of ~11% appears to be the closest existing benchmark, computed in-house rather than from external literature).
- General (non-PH-specific) findings from the OSM literature that would carry over: `width` is "frequently null" globally, and `lanes` tags are commonly applied to a representative section of a longer way rather than to every point, so lane counts should be treated as a minimum/indicative value, not an exact per-segment count, even where present. (OSM wiki: Key:lanes; Completeness wiki page general methodology — buffer-and-count against an external reference source.)
- No PH-specific academic or municipal study quantifying width/lane/oneway tagging completeness was found in three search passes.

**Net:** this remains an open gap — if a completeness number is needed, it would have to be computed directly from an HOTOSM PH roads extract (count tagged vs total ways) rather than cited from existing literature.

**Feature use:** none new; confirms the project's own from-scratch tag-completeness computation is the only route, same as the existing 11% speed-limit figure.

---

## 5. Overture Maps transportation + buildings for PH

**Status: YES, accessible today — but speed-limit/lane attributes for PH segments likely inherit OSM's own sparsity, not an independent signal.**

- Transportation theme reached General Availability Dec 19, 2024 (86M km of roads worldwide): https://overturemaps.org/announcements/2024/overture-general-availability-of-transportation-dataset/. Buildings theme GA since July 2024.
- **Access**: hosted as GeoParquet on S3/Azure blob, queryable via:
  - CLI: `overturemaps download --bbox=<minLon,minLat,maxLon,maxLat> -f geojson --type=segment` (transportation) or `--type=building`
  - DuckDB direct query against `s3://overturemaps-us-west-2/release/<date>/theme=transportation/type=segment/*` with a spatial bbox predicate pushed into the Parquet scan (no full download needed) — https://docs.overturemaps.org/getting-data/duckdb/
  - Docs: https://docs.overturemaps.org/getting-data/
- **Schema**: segment features carry `road.class`, `surface`, `width`/`width_rules`, `speed_limits`, `lanes`, and access/turn restrictions via a linear-referencing model (attributes can vary along a segment as a fraction of its length) — https://docs.overturemaps.org/schema/reference/transportation/segment/, https://docs.overturemaps.org/schema/concepts/by-theme/transportation/
- **Caveat on data provenance for PH**: Overture's transportation layer is built from a mix of OSM plus commercial contributors (TomTom is a named data partner — https://www.tomtom.com/newsroom/behind-the-map/how-tomtom-makes-overture-transportation-layer/). TomTom's own PH road coverage/attribution depth is unconfirmed; no PH-specific coverage or attribute-fill-rate figures were found. Given OSM is very likely the dominant contributor for a country with limited commercial mapping investment like the Philippines, Overture's `speed_limits` field for PH roads should be assumed to inherit the same ~11% sparsity as raw OSM until proven otherwise, not treated as an independently-collected improvement.
- Buildings theme is queried the same way (`--type=building`) and is a second building-footprint data source for the crowdedness proxy described in section 3, though Google Open Buildings v3 / Microsoft footprints are likely denser for PH specifically.

**Feature use:** Overture is the easiest single access point to query PH road geometry + attempted attribute fields at scale (DuckDB bbox query, no auth, no WAF), but treat any populated `speed_limits`/`lanes` value as no more authoritative than OSM's own tag until spot-checked, since it's largely OSM-derived for this country.

---

## Summary Table

| # | Source | Access | Format | New signal vs. OSM maxspeed? |
|---|--------|--------|--------|-------------------------------|
| 1 | DPWH AADT | NO (WAF 403 + cert errors, PDF-atlas only) | PDF | Would be strong, but blocked |
| 2 | Mapillary sign detections | PARTIAL (free token, real API, sparse PH coverage) | JSON via Graph API | Yes, where imagery exists |
| 3a | Google Open Buildings v3 | YES | CSV (WKT polygons) | Indirect (density proxy) |
| 3b | Microsoft Global ML / IdMyPhBuildingFootprints | YES | GeoJSONL (.csv.gz) | Indirect (density proxy) |
| 3c | Thinking Machines TM Open Buildings | YES (12 cities only) | GeoJSON/OSM | Indirect, highest quality, narrow |
| 4 | OSM lane/width completeness study | NO dedicated study exists | N/A | N/A — must self-compute |
| 5 | Overture Maps transportation | YES (no auth, DuckDB/CLI) | GeoParquet | Likely NOT independent (OSM-derived for PH) |
