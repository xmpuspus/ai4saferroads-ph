# Surprising findings: Speed Safety Score

Computed from live data, not asserted. Every number below comes from the pipeline and the
overlay scripts in this repo (`build/sss_pipeline.py`, `build/overlay/compute_overlay.py`,
`build/overlay/enrich_worldpop.py`, `build/overlay/correlate_crowd_deaths.py`), run on
OpenStreetMap, Meta's Relative Wealth Index, WorldPop 2020, and PSA death records for 51
Philippine cities. Re-run them to reproduce. Full per-city table: [cities.md](cities.md).
Crash validation: [validation.md](validation.md).

## 1. Most streets have no posted limit at all

Across the 51 cities, 357,423 drivable streets are scored, but only 37,971 carry a posted
limit in OpenStreetMap: about 11% overall. Coverage swings wildly by city:

| City | Streets scored | With a real posted limit | Share |
|------|---------------:|-------------------------:|------:|
| Baguio | 7,521 | 3,961 | 53% |
| Davao City | 10,873 | 2,658 | 24% |
| Dasmarinas | 21,063 | 4,432 | 21% |
| Metro Manila | 87,123 | 14,163 | 16% |
| Cebu City | 22,402 | 2,027 | 9% |
| Butuan | 3,976 | 0 | 0% |
| **All 51 cities** | **357,423** | **37,971** | **11%** |

The map keeps two cases visually separate: bright glow only where a **real** posted limit
exceeds the safe speed; the imputed majority never glows. The honest headline is the
real-posted count: 7,586 flagged segments. Three cities (Butuan, Puerto Princesa, Surigao)
have so little posted-limit data they carry no flagged roads at all. The missing limits are
not a flaw to hide: they are exactly where official posted-limit data would add the most.

## 2. Speed-limit mismatch is not a wealth story

You might expect the most dangerous speed limits to fall on poorer neighbourhoods. Joined to
Meta's Relative Wealth Index on a ~1.6 km grid, and measured on the raw posted-over-safe gap
(the mismatch itself, before any exposure weighting), across the 43 cities with enough
real-posted road to grid, the relationship is **absent almost everywhere and significant in
only three**:

| City | Spearman ρ (gap vs wealth) | p | Reading |
|------|--------------------------:|---:|---------|
| Metro Manila | −0.11 | 0.29 | no relationship |
| Cebu City | +0.21 | 0.25 | no relationship |
| Davao City | +0.06 | 0.89 | no relationship |
| Bacolod | −0.61 | 0.035 | **worst mismatch in poorer areas; significant** |
| Tagum | −0.61 | 0.023 | **worst mismatch in poorer areas; significant** |
| San Fernando (Pampanga) | −0.42 | 0.026 | **worst mismatch in poorer areas; significant** |

Forty of forty-three cities show no significant link, and none of the three biggest metros
does either. Where it **is** significant, all three cities point the same way: the worst
speed-limit mismatch falls on the **poorer** districts. But three significant results out of
43 tests is about what chance alone produces (43 × 0.05 ≈ 2), so even this is a weak signal,
not a national pattern. The honest read: where a posted limit is most out of step with its
road is **not** a wealth story. It is structural, and where wealth does seem to matter it is
a handful of mid-size cities where the poorer side carries the gap, worth a local look rather
than a country-wide claim.

(The correlation is run on the raw gap, which is independent of the exposure weight. Running
it on the full exposure-weighted score instead gives the same three cities and the same story,
so folding population density into exposure does not manufacture or hide a wealth link.)

## 3. But the danger does cluster, by corridor, not by income

The mismatch is not random noise. Moran's I (spatial autocorrelation) on the gap is positive
and significant in several cities, Metro Manila +0.09 (p = 0.035), Bacolod +0.33 (p = 0.035),
San Jose del Monte +0.41 (p = 0.025), Tagum +0.54 (p = 0.025), meaning high-mismatch cells
sit next to other high-mismatch cells. There are distinct hotspot corridors. The danger is
concentrated somewhere even when it is not concentrated by income, and the map's job is to show
exactly where. (Malolos, significant on the earlier score-based measure, drops just below the
line on the gap measure at +0.41, p = 0.08; treat it as a lead, not a corridor.)

## 4. The crowded, the mismatched, and the deadly are three different maps

This is the new axis. WorldPop 2020 population is now folded into the exposure weight, so
"crowdedness" is a real number per road, not a proxy. Three things you would expect to stack
on top of each other instead pull apart.

- **Flagged roads do sit where people are packed.** A flagged real-posted road has a median
  residential density of 14,620 people/km² around it, against 9,326 for an unflagged
  real-posted road. Pick a flagged road and a random unflagged one and the flagged one is the
  denser of the two 59% of the time. The mismatch lands on the busy arterials that cut through
  dense cores, which is what makes it worth flagging.
- **But a bigger gap does not mean a denser place.** At the ~1.6 km cell level the *size* of
  the speed-limit gap barely tracks density at all (Spearman +0.01, p = 0.92, n = 1,157 cells).
  Crowdedness decides *which* roads get flagged, not *how large* the mismatch is. Those are two
  different questions, and only the first has a crowding answer.
- **And the death map points the opposite way.** Metro Manila has by far the most flagged roads
  (4,664) and the densest flagged network in the country (a median 22,872 people/km² around its
  flagged roads), yet the **lowest** road-death rate of any region: 3.6 per 100,000 against a
  national 10.9 (PSA SDG 3.6.1, 2022). Across regions, the crowdedness of the flagged network
  runs slightly *inverse* to the death rate (Spearman −0.09, n = 15), and flagged roads per 100
  scored runs −0.26 (p = 0.24, n = 17). The deadliest regions are rural: Cagayan Valley 22.1,
  Caraga 16.9, Davao 16.8. Deaths are counted by region of residence, dense cities have low
  free-flow speed and better trauma care, and the urban map and the death map are answering
  different questions on purpose.

**The one you can see from space.** The clearest picture of the mismatch is a wide, fast
corridor slicing through packed low-rise rooftops. In Metro Manila the sharpest examples, all
flagged real-posted roads in the top decile of residential density with a posted limit far over
the survivable speed, are Mel Lopez Boulevard (posted 60, survivable 30, ~103,000 people/km²
around it), C. M. Recto Avenue (60→30), Capulong Street (60→30), Quezon Avenue (60→30), and
Magsaysay Boulevard (60→30). In Cebu it is Natalio Bacalso Avenue (60→30); in Davao, the Davao
City Coastal Road (60→30). These are the roads where the survivable-speed gap and the crowd sit
directly on top of each other, and a satellite crop shows why: the road is built for speed and
the ground beside it is wall-to-wall housing.

## Caveats

- Correlation, not causation. A relationship, or its absence, does not explain why.
- Forty-three cities tested at p < 0.05 will throw roughly two false positives by chance; the
  three significant wealth correlations are barely above that floor. Treat them as leads.
- The Relative Wealth Index is a model at ~2.4 km and WorldPop is ~90 m constrained
  (residents, not daytime foot traffic); the grid is coarse and nearby cells are not
  independent, so p-values are optimistic.
- The mismatch metric uses only segments with a real posted limit, to avoid imputation bias.
- Region death rates are by region of usual residence, not crash location; reading them as a
  city-level score would be the ecological fallacy.
- This is a screening layer to prioritise segments for review, not a final determination.

## Sources

OpenStreetMap (ODbL) · Meta Relative Wealth Index, Data for Good (CC-BY) · WorldPop PH 2020
constrained (CC-BY) · PSA OpenSTAT road-death rate SDG 3.6.1 and land-transport deaths by
region · Safe System speeds: Tingvall & Haworth 1999, ITF/OECD 2018, WHO · Nilsson (1981)
power model · Tefft (2011), AAA.
