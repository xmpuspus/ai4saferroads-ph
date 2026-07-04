# Phase 2: crowdedness axis, the triple, and the satellite hook

Date: 2026-07-04. Every number recomputed this session; intermediates in
`tmp/correlate-20260704T013745Z/`. Scripts: `build/overlay/enrich_worldpop.py`,
`build/overlay/compute_overlay.py`, `build/overlay/correlate_crowd_deaths.py`.

## What was added

WorldPop PH 2020 constrained (~90 m, people/pixel, EPSG:4326) is now folded into the exposure
weight E. The core pipeline stays Python-stdlib; enrichment is a separate numpy/rasterio stage
(mirrors compute_overlay.py) that reads the scored network on disk and rescore without re-pulling
OSM. For each segment it samples residents in the ~3x3 cell block (~270 m) at points every ~150 m
along the line, averages to a residential density, and blends:

    E_poi = min(VRU sites within 150 m, 5) / 5
    E_pop = min(pop_density / DIV, 1),  DIV = 32,345 /km2  (90th pctile of per-segment density)
    E     = 1 - (1 - E_poi)(1 - E_pop)          # probabilistic OR, stays in [0,1]
    SSS   = 100 * min(max(0,gap),40)/40 * (0.5 + 0.5 E)

Design decisions (with the advisor):
- **Blend, not replace.** WorldPop constrained counts residents, so a road through a market or
  CBD reads low on population but high on POIs; the POI term compensates. Either signal can raise
  exposure; neither can invent risk where the gap is zero (the 0.5+0.5E floor is preserved).
- **Absolute, city-comparable normalisation.** DIV is a fixed divisor from the all-cities density
  distribution, not a within-city percentile, so scores stay comparable across the 51 cities.
- **The flagged set does not move.** sss>0 iff gap>0, and gap is independent of E, so which roads
  flag (7,589 real-posted), the flagged geojsons, and the coverage counts are all unchanged by the
  enrichment. Only SSS magnitude and per-city ranking move. Verified by assertion in the script.
- **Side effect: the score de-discretised.** Manila went from ~6 distinct flagged SSS values (the
  old "6-value ladder") to 359 spanning 6.2 to 75.0. Population density is continuous, so the
  score now is too.

## Findings (recomputed)

**Wealth finding is insulated and unchanged in story.** The wealth correlation now runs on the
raw gap (E-independent) instead of the exposure-weighted score, so folding in population cannot
contaminate it. Result: 3 of 43 cities significant (Bacolod -0.61 p=0.035, Tagum -0.61 p=0.023,
San Fernando -0.42 p=0.026), all poorer, Manila -0.11 (p=0.29). Same three cities as the old
score-based measure, no flips. Still ~chance (3/43).

**Crowdedness axis (new):**
- Flagged real-posted roads sit in denser places: median 14,620 people/km2 around them vs 9,326
  for unflagged real-posted roads; P(flagged denser than a random unflagged) = 0.588.
- But gap *magnitude* is density-independent at the cell level: Spearman +0.01 (p=0.92, n=1,157).
  Crowding decides which roads flag, not how large the mismatch is.

**The triple pulls apart (finding B, sharpened).** NCR has the most flagged roads (4,664) and the
densest flagged network (median 22,872/km2), yet the lowest road-death rate in the country (3.6
per 100k vs national 10.9, PSA SDG 3.6.1 2022). Across regions:
- flagged-road density vs death rate: Spearman -0.09 (n=15), null/inverse
- flagged per 100 scored vs death rate: Spearman -0.26 (p=0.24, n=17), null/inverse
Deadliest regions are rural: Cagayan Valley 22.1, Caraga 16.9, Davao 16.8. Deaths are by region
of usual residence, dense cities have low free-flow speed and better trauma care. The crowdedness
map and the death map answer different questions.

**The satellite hook (buildable, real).** Flagged real-posted roads in the top density decile
(>= 49,479/km2) with the largest posted-over-safe gap, per metro:

| Metro | Road | Posted→safe | Residential density | Coords |
|---|---|---|---|---|
| Manila | Mel Lopez Blvd (Tondo) | 60→30 | ~103,000/km2 | 14.5994, 120.9652 |
| Manila | C. M. Recto Ave | 60→30 | ~82,600/km2 | 14.6017, 120.9667 |
| Manila | Quezon Ave | 60→30 | ~75,500/km2 | 14.6235, 121.0081 |
| Cebu | Natalio Bacalso Ave | 60→30 | ~57,200/km2 | 10.2955, 123.8834 |
| Davao | Davao City Coastal Road | 60→30 | ~53,100/km2 | 7.0639, 125.6177 |

Real Esri World Imagery crops saved to `docs/satellite/`. The Mel Lopez crop shows a wide
multi-lane arterial curving through wall-to-wall Tondo rooftops: a road built for speed with
wall-to-wall housing on its edge, which is the finding made visible.

## Caveats (carried into public copy)

Correlation not causation; region deaths by residence not crash site; WorldPop constrained counts
residents not daytime foot traffic; city networks are urban-core AOIs; RWI/WorldPop grids are
coarse and spatially autocorrelated so p-values are optimistic.
