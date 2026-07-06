# Validation: does the map agree with real crashes?

The Speed Safety Score applies a published physical model. It does not prove that model. This
page is about a different, testable question: do the roads the model flags line up with where
crashes actually happen? Every number here is computed by the scripts in
`tmp/correlate-20260627/` against real external datasets, not asserted.

## What is proven vs what is applied

The speed-to-fatality relationship (fatal risk scales with roughly the fourth power of speed)
is established crash-data research: Nilsson (1981) on Swedish speed changes, Elvik's
meta-analyses, Rosen and Sander (2009), and Tefft (2011) for pedestrians. This project
**applies** that curve to every road. It does not, and cannot, re-derive it: the Philippines
has no open segment-level crash-and-speed dataset to fit it from. So the honest claim is
"applied at network scale," never "proved."

What we *can* test with open data is whether the map's output is consistent with real crashes.

## Experiment A: reported crashes concentrate on the flagged roads

**Data.** 17,312 geolocated Metro Manila road incidents from the MMDA traffic-alert dataset
(2018-2020, point lat/lon, via the open `PotatoC0der/mmda_traffic_analysis` mirror of MMDA's
Twitter alerts). Filtered to actual crashes (vehicular accident, multiple collision, self
accident, hit-and-run, and similar) and deduplicated, leaving 12,563 with valid coordinates
(the exact set the map shows). Of these, 12,457 (99%) snapped to a scored road within 30 m of our Metro
Manila network.

**Result.**

| Road bucket | Network length | Reported crashes | Crashes per km |
|------|---------------:|-----------------:|---------------:|
| Flagged (real posted limit over safe speed) | 566 km (7.3%) | 5,247 (42%) | 9.26 |
| Real posted limit, not flagged | 1,333 km | 5,423 | 4.07 |
| Imputed or no posted limit | 5,897 km | 1,787 | 0.30 |

The roads the model flags are **7.3% of the network but carry 42% of reported crashes**, at
9.3 crashes/km against 0.3/km for roads with no posted-limit problem.

Aggregated to a 550 m grid and normalised by road length (so this is not just "more road, more
crashes"), crash density rises with the score: crash density per km against the cell's mean Speed
Safety Score gives **Spearman +0.41** over 1,222 cells, recomputed on the 12,563 crashes the map
now shows (`build/overlay/validate_crashes.py`). The association holds through the exposure weight
folding in WorldPop residential density and through the crash-set refresh, because the flagged set
does not move when exposure changes, so the headline (7.3% of length, 42% of crashes) is stable.

Within road class the same direction holds (flagged primary roads 18 crashes/km vs 2.3 for
unflagged primary), though almost every Manila arterial is flagged, so the unflagged comparison
group is small and that ratio is suggestive rather than decisive.

**What this does and does not show.** It shows the flags land where crashes concentrate, which
is what the model predicts. It is an association on an imperfect sample, not proof the limit
causes the crash. Honest limits:

- The MMDA alert set is a convenience sample biased toward monitored arterials, which is exactly
  where flagged roads are. That inflates the association.
- There is no open traffic-volume (AADT) layer for Metro Manila, so we cannot fully separate
  "mismatched limit" from "busier road." The within-class comparison is the best control
  available without it.
- The crashes are mostly vehicle-to-vehicle. Only ~115 are tagged pedestrian. So this tests the
  broad "mismatched roads are more crash-prone" claim, not the specific pedestrian-survival
  mechanism the score is built on.
- Crashes are 2018-2020. Limits are read from 2026 OpenStreetMap. Acceptable for stable
  arterials, not for roads that changed.

## Experiment B: the regional death rate does NOT track the map (and that is expected)

To check the other unit of analysis, we mapped all 51 cities to their region and correlated each
region's speed-mismatch metric (flagged roads per 100 scored) against the PSA road-traffic death
rate per 100,000 (SDG 3.6.1, 2022, from PSA OpenSTAT).

**Result: Spearman -0.26 (permutation p = 0.235, n = 17 regions), no relationship, if anything
weakly inverse.** Metro Manila has by far the most flagged roads (5.4 per 100 scored) and the
**lowest** death rate in the country (3.6 per 100k, against a national 10.9). The highest death
rates are in regions with few flagged urban roads in our sample (Cagayan Valley 22.1, Caraga
16.9, Davao 16.8).

This is not a contradiction of Experiment A. It is what you expect when the unit is wrong:

- PSA counts deaths by region of **residence**, not by where the crash happened. Metro Manila
  residents killed on provincial highways count against their home region.
- Dense cities have congestion (lower operating speeds despite high posted limits) and far better
  trauma care, so fewer crashes turn fatal.
- Our flagged count is itself confounded by OpenStreetMap posted-limit coverage, which is much
  denser in big cities.

The lesson is the one the methodology already warns about: this map is a segment-level screening
tool, and it validates at the segment level. Regional residence-based death rates are the wrong
yardstick, and reading them as one would be the ecological fallacy.

## Experiment C: do the flagged roads lack pedestrian crossings? (mostly no, and that is the point)

A natural follow-up: are the flagged fast-plus-pedestrians roads the ones without
protection, too? We pulled OpenStreetMap pedestrian crossings, traffic signals, and traffic calming
for Manila, Cebu, and Davao and measured, for each flagged segment, the distance to the nearest
one.

The naive hypothesis did not hold. In the well-mapped metros the flagged roads are **better**
covered by crossings, not worse: in Metro Manila a flagged segment's nearest crossing is a median
36 m away versus 71 m for unflagged real-posted roads. In Cebu, 22 m versus 54 m. The reason is
simple, and it is a confound: flagged roads are arterials, and arterials have crossings at their
signalised intersections. (Davao, where OSM crossing data is sparse, runs the other way: 70% of
flagged roads have no crossing within 100 m.)

What flagged roads consistently lack is **traffic calming** (the thing that actually lowers
speed): only 21% of flagged roads in Manila, 10% in Cebu, and 4% in Davao have any within 100 m.

That distinction is the whole argument. A crossing manages *where* people cross. It does not
change *how fast the car arrives*. A marked crossing on a road posted 60 where 30 is survivable
still leaves the pedestrian exposed to a 60 km/h impact. So "the roads have crossings" is not
reassurance, it is the point: the protection that exists addresses the wrong variable. The fix
is the limit and the calming that enforces it, which is what the score measures.

## Data sources

- MMDA traffic-alert crashes (2018-2020), open mirror:
  `github.com/PotatoC0der/mmda_traffic_analysis` (`data_mmda_traffic_spatial.csv`).
- Mendeley EDSA crash dataset (2007-2016, 22,072 records, point-level) for EDSA:
  `data.mendeley.com/datasets/hwbf6n4krw` (fetched: a single-road supplement, mostly
  unflagged road, so not used as the headline).
- PSA OpenSTAT, road-traffic death rate by region (SDG 3.6.1) and land-transport-accident deaths
  by region (2023): `openstat.psa.gov.ph`.
- WorldPop Philippines 2020 100 m population (CC BY), now folded into the exposure weight so
  the score reflects residential density, not just POI proximity:
  `data.worldpop.org/.../PHL/phl_ppp_2020_constrained.tif`.

## Honest next steps (not yet done)

- A pedestrian-specific test once a pedestrian-tagged crash set is available (the open MMDA set
  is too sparse on that field).
- A traffic-volume control: DPWH Annual Average Daily Traffic exists but is locked behind a WAF
  and FOI, so it needs a request, not a download.
- A severity-by-time test on more than EDSA, once another open PH set carries both
  severity and timestamps (EDSA is one arterial, and its 22 fatal crashes are too few to read by hour).
- The national DRIVER crash portal (roadsafety.gov.ph) would give location-based, current,
  nationwide crashes, but it was unreachable and needs an access request.
