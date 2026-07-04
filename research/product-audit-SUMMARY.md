# Product Audit — Speed Safety Score (synthesis)

Date: 2026-06-25. Dimension reports: `product-audit-ux-obs.md`, `product-audit-intel-gaps.md`, `product-audit-rel-perf.md`, `product-audit-sec-ops.md`.

## Scores (pre-fix)
| Dimension | Score |
|---|---|
| UX | 62 |
| Observability | 38 |
| Intelligence | 52 |
| Feature Gaps | 38 |
| Reliability | 58 |
| Performance | 64 |
| Security | 58 |
| Operational | 64 |
| **Overall (weighted)** | **~55** |

## Ship-blockers (fix before anything else)
1. **e2e RED + false "all pass" badge/claims.** e2e.sh asserts three.js/satellite from the deleted 3D sim. README/DOSSIER claim 3D-on-satellite sim (now 2D canvas) and "e2e all pass" (fails). [rel-perf #4-5, sec-ops #9, intel #2]
2. **Methodology bug — one-way ≠ divided.** sss_pipeline.py `oneway=yes` → V_safe 50→70, under-flags undivided arterials. [intel #1]
3. **XSS — unescaped OSM `name`** in index.html popup setHTML + #roads innerHTML + sim.html sub. [sec-ops #1-3]
4. **No fetch error handling / no loading state** — silent blank map on any failure + city-switch race. [rel-perf #3,7; ux #1-2]
5. **Honesty: imputed scored equally + fake "traffic".** 81-98% imputed glowed same as real-posted (overstates ~2x); animated dots are random, labeled "traffic" (mock-data risk). [intel #4-5, ux #4]

## High-value (ship next)
6. Demote map 3D tilt → flat default (decoration). [ux #3]
7. Remove unbuilt "intersection density" claim from methodology/DOSSIER (narrated not built). [intel #3]
8. a11y: aria-pressed, keyboard road rows, focus-visible, full reduced-motion, non-color sim cues. [ux #5,9,10]
9. Data-version "as of <date>" stamp on the page + in cities.json. [ux/obs #6, sec-ops #11]
10. LICENSE file (badges reference it, file missing). [sec-ops #10]
11. SRI on unpkg maplibre. [sec-ops #7]
12. Pipeline: guard empty-Overpass-as-success; retry/backoff on 429. [rel-perf #6]
13. Core unit tests (parse_maxspeed, safe_speed) — currently zero. [rel-perf #11]

## Feature gaps (table-stakes to add)
14. Before/after recommended-limit view (the marketed C5, missing). [intel feature-gaps]
15. Road search + shareable deep-link (city in URL hash). [intel feature-gaps]
16. Data download links (geojson/csv). [intel feature-gaps]
17. Clean orphaned weight: sat_corridor.png unused by 2D sim; regenerate og-card. [rel-perf #10]

## Deferred (need NDA/bigger work, documented honestly)
- Operating-speed / 85th-pctile layer (NDA GPS-probe).
- Crash-data validation (PH DRIVER).
- P2W layer, temporal exposure, full-NCR AOI.

## Verified CORRECT (keep)
- Nilsson (60/30)^4=16 ("~16x"), 1-(30/60)^4=93.8% ("~94%"), Tefft 38% at 60 — all sourced/correct. [intel #8]
- Sim physics honest (reaction 23.3m > 22m gap at 60 → full-speed impact). [intel #8]
- Live security headers strong (HSTS, XFO, nosniff, CSP). [sec-ops #4,11]
- Mirror fallback + meaningful invariants. [rel-perf]
