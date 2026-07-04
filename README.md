# Current vs Proposed Speed Limits

> An open map of every street's current posted speed limit, the proposed safe limit, and why
> the two differ, across 51 Philippine cities. Where a city posts a limit higher than the speed
> a person can survive a crash at, the map shows the gap: 357,423 streets scored from
> OpenStreetMap, 7,586 posted above the safe speed. In Metro Manila, 4,664 of them, including
> arterials posted 60 km/h beside schools where the speed a pedestrian survives is 30. The Speed
> Safety Score is the index that ranks those gaps. And the danger does not track wealth: across
> the 43 cities with enough data the link is significant in only three, and there it is the
> poorer districts that carry the worst mismatch ([findings](docs/findings.md)).

[![Live](https://img.shields.io/badge/live-ai4saferroads--ph.vercel.app-success.svg)](https://ai4saferroads-ph.vercel.app)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC-BY-4.0](https://img.shields.io/badge/data-CC--BY--4.0-blue.svg)](LICENSE)
[![Method: Safe System + Nilsson](https://img.shields.io/badge/method-Safe%20System%20%2B%20Nilsson-success.svg)](build/web/methodology.html)
[![Source: OpenStreetMap](https://img.shields.io/badge/source-OpenStreetMap-success.svg)](https://www.openstreetmap.org)
[![Cities: 51](https://img.shields.io/badge/cities-51%20across%20PH-success.svg)](docs/cities.md)
[![e2e: all pass](https://img.shields.io/badge/e2e-all%20checks%20pass-success.svg)](tests/e2e.sh)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#limitations)

[![Current vs proposed speed limits: Metro Manila in satellite, corridors posted above the safe speed glowing, with a switch across Philippine cities](docs/demo.gif)](https://ai4saferroads-ph.vercel.app)

<sub>Real recording of the live map (via `build/record_demo.mjs`). The full street network of
each city is scored; "critical roads &amp; why" walks the worst corridors with the reason each
is flagged; the "speed risk &times; wealth" overlay then shows the danger does not track wealth
in the big metros. Live: [ai4saferroads-ph.vercel.app](https://ai4saferroads-ph.vercel.app).</sub>

## What it shows

The question is not whether drivers speed. It is whether the posted limit itself fits the
road and the people on it. For every drivable road segment the model computes:

- a **Safe System recommended speed** from the road's class and the vulnerable-user sites
  around it (schools, markets, hospitals, transit),
- the **gap** to the **posted limit** (OpenStreetMap `maxspeed`),
- a **Speed Safety Score** (0 to 100) that weights the gap by pedestrian exposure,
- the **recommended limit** and the **modeled fatal-risk reduction** from adopting it.

Roads with a real posted limit above the safe speed glow from yellow to magenta. Roads whose
limit had to be imputed from their class are shown faint and dashed, kept out of the headline
counts. The official ADB GPS-probe data drops into the same segment schema when available,
replacing imputed limits and adding an operating-speed layer.

## See why the limit is the story

[![Same corridor at 60 vs 30 km/h: the 60 car strikes a pedestrian at the crossing, the 30 car stops short](screenshots/sim_v2.png)](https://ai4saferroads-ph.vercel.app/sim.html)

<sub>[Live](https://ai4saferroads-ph.vercel.app/sim.html): the same driver, the same 22 m,
on a real flagged corridor (P. Sanchez Street, Metro Manila). At the posted 60 km/h the
reaction distance alone (23 m) is longer than the gap, so the car reaches the crossing before
it can brake and strikes the pedestrian, a 38% fatality risk (Tefft 2011). At the Safe System
30 km/h the same car stops 5 m short. The contrast comes from real reaction-and-braking
physics, drawn so you can see where each car stops.</sub>

## Cities (live OpenStreetMap, June 2026)

51 cities are scored, from Metro Manila to regional centres across Luzon, the Visayas, and
Mindanao. The top of the list by flagged-road count:

| City | Streets scored | With a real posted limit | Flagged: limit over safe speed | Vulnerable-user sites |
|------|----------------:|-------------------------:|-------------------------------:|----------------------:|
| Metro Manila | 87,123 | 14,163 | 4,664 | 5,669 |
| Cebu City | 22,402 | 2,027 | 581 | 858 |
| Davao City | 10,873 | 2,658 | 364 | 466 |
| Calamba | 9,499 | 698 | 229 | 284 |
| Angeles City | 14,211 | 974 | 202 | 431 |
| Iloilo City | 6,433 | 758 | 135 | 398 |
| San Fernando (Pampanga) | 10,209 | 708 | 134 | 342 |
| Koronadal | 3,274 | 476 | 99 | 86 |
| Bacolod | 8,167 | 475 | 98 | 258 |
| Cagayan de Oro | 8,555 | 441 | 72 | 307 |
| Tagum | 5,382 | 277 | 68 | 128 |
| San Jose del Monte | 13,027 | 335 | 58 | 489 |
| **All 51 cities** | **357,423** | **37,971** | **7,586** | **16,399** |

Full per-city numbers are in [docs/cities.md](docs/cities.md). The whole urban network of each
city is pulled, scored, and served as vector tiles so the entire street grid draws at once.
Posted-limit coverage in OpenStreetMap varies a lot: dense in Metro Manila, thin in smaller
cities, and sparse enough in three (Butuan, Puerto Princesa, Surigao) that they carry no
flagged roads at all. That gap is the point, not a flaw: it is exactly where official
posted-limit data would add the most.

Three patterns fall out of the data, and none goes the way you would guess. The mismatch does
not track wealth. It does sit on the crowded arterials (WorldPop puts a median 14,620 people per
km² around a flagged road, against 9,326 for one that fits), yet the size of the gap does not
track how crowded a place is. And the crowded, most-flagged region, Metro Manila, has the
country's lowest road-death rate, because the deaths are on rural highways and counted by region
of residence. The crowded, the mismatched, and the deadly are three different maps. Full numbers
and the "speed risk × crowding" overlay: [docs/findings.md](docs/findings.md).

## What's in this repo

- `build/sss_pipeline.py`: pulls live OpenStreetMap road geometry, posted limits, and
  vulnerable-user sites for any city; computes the Speed Safety Score; writes per-city GeoJSON.
- `build/web/index.html`: the map: every street scored (MapLibre + PMTiles), a city selector
  grouped by island, a guided "critical roads & why" mode, "speed risk × wealth" and "speed risk
  × crowding" overlays, road search, shareable city links, per-road before/after, and a city-wide
  modeled fatal-risk cut. Single static file.
- `build/overlay/`: `enrich_worldpop.py` folds WorldPop population density into the exposure
  weight; `compute_overlay.py` joins the scores to Meta's Relative Wealth Index and computes the
  Spearman correlations + Moran's I; `correlate_crowd_deaths.py` builds the crowding-and-deaths
  analysis (see `docs/findings.md`).
- `build/web/sim.html`: the stopping-distance comparison (2D canvas, 60 vs 30 km/h).
- `build/web/methodology.html`: the full method and sources.
- `tests/e2e.sh`, `tests/test_pipeline.py`, `tests/check_invariants.py`: unit, wiring, and
  invariant checks.
- `decision/`: the research and decision trail; `research/`: the product audit.

## Run it

```sh
make data     # pull live OSM and score all cities
make serve    # http://127.0.0.1:8799/web/index.html  (Range-capable serve.py)
make e2e      # unit + wiring + invariant checks, all pass
make shot     # render screenshots (needs node + playwright chromium)
```

The pipeline uses the Python standard library only. The site is static; deploy is a single
`vercel --prod` from `build/web`.

## Method, briefly

Safe System survivable speeds, 30 km/h where people walk, 50 at side-impact intersections,
70 on a divided carriageway, 100 grade-separated, come from Tingvall and Haworth (1999),
ITF/OECD *Speed and Crash Risk* (2018), and the WHO Speed Management Manual. The
speed-to-fatality relationship is the Nilsson power model (1981): fatal crash risk scales with
the fourth power of speed, so 60 to 30 km/h is about a 94% modeled reduction. Pedestrian
fatality risk by impact speed in the comparison view follows Tefft (2011, AAA Foundation).
Full spec and sources: [methodology page](build/web/methodology.html).

This matters in the Philippines specifically: WHO (2023) estimates 11,062 road deaths, about
53% of them motorcyclists, on a fleet where powered two- and three-wheelers are the largest
vehicle class. The national urban limit is 40 km/h, but local governments set their own
limits, which is how posted limits drift out of step with the road.

## Does it line up with real crashes?

The model applies a published physical law (Nilsson); it does not prove one. But the map's
output can be tested. Joining 12,526 geolocated Metro Manila crashes (2018-2020, MMDA traffic
alerts) to the scored network: the flagged roads are 7% of the network length but carry 42% of
reported crashes, and on a 550 m grid, normalized for road length, crash density rises with the
score (Spearman +0.35, p = 0.002). The flags land where crashes concentrate. This is an
association on a convenience sample biased to arterials, with no traffic-volume control, so it is
consistent with the model, not proof a limit causes a crash. A regional cross-check against PSA
death rates behaves differently, and is expected to (deaths are by region of residence, not crash
site, so Metro Manila has the most flagged roads yet the lowest death rate). Full method, numbers,
and caveats: [docs/validation.md](docs/validation.md).

## Limitations

- OpenStreetMap posted-limit coverage varies by city; imputed limits are flagged, drawn faint,
  and kept out of the headline counts. A few cities have so little posted data they carry no
  flagged roads.
- The recommended-speed classifier is a transparent heuristic from open tags. Intersection
  density and divided-carriageway detection are not yet computed, so arterials default to the
  side-impact survivable speed (50) unless OSM marks them divided.
- Exposure combines point-of-interest proximity with WorldPop residential density; it still
  does not capture daytime foot traffic or measured traffic volume.
- This is a screening layer to prioritize segments for review, not a final determination.

## Related work

iRAP Star Rating (operating-speed road risk; ViDA platform), World Bank GRSF *Guide for Safe
Speeds* (2024, guidance), and FHWA USLIMITS2 (an expert system for setting limits). This
project adds an open, network-scale layer comparing posted limits to Safe System speeds from
OpenStreetMap, and a way to see what a given gap does to a person.

## Disclaimer

Indicators are derived from open data and published road-safety research. A flag means a
segment warrants review, not that any posted limit is wrong; limits may have local context
this screening does not capture. Not affiliated with ADB, WHO, the World Bank, or iRAP.

## License

Code MIT. Derived data CC-BY-4.0. Road and satellite data © OpenStreetMap contributors
(ODbL), © Esri, Maxar, Earthstar Geographics, © CARTO.

## Sources

Tingvall and Haworth (1999) · ITF/OECD, *Speed and Crash Risk* (2018) · WHO Speed Management
Manual · Nilsson (1981) power model; Elvik updates · Rosén and Sander (2009) · Tefft (2011),
AAA Foundation · WHO Global Status Report on Road Safety 2023 (Philippines) · OpenStreetMap.
