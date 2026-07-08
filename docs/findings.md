# Surprising findings: Speed Safety Score

Computed from live data, not asserted. Every number below comes from the pipeline and the
overlay scripts in this repo (`build/sss_pipeline.py`, `build/overlay/compute_overlay.py`,
`build/overlay/enrich_worldpop.py`, `build/overlay/correlate_crowd_deaths.py`), run on
OpenStreetMap, Meta's Relative Wealth Index, WorldPop 2020, and PSA death records for 51
Philippine cities. Re-run them to reproduce. Full per-city table: [cities.md](cities.md).
Crash validation: [validation.md](validation.md).

## 0. Is speed even the problem? The harm hides when the road clears

The objection every Filipino raises is that the cities are gridlocked, so real speeds sit far
below the posted limit most of the day. "The limit is 60, traffic keeps us under 30, and we still crash."
The data answers it, and the answer is not the naive one.

On the Mendeley EDSA crash set (22,072 records, 2007-2016, the one open PH set we found with both
severity and timestamps), **total crashes peak in the rush hour**, tracking traffic volume rather
than empty roads. That kills the simple "crashes happen at night" story. But total crashes are not deaths.
When we split by severity, the picture inverts: the **share of crashes that injure or kill roughly
doubles in the late-night window**, when EDSA finally clears and vehicles reach the speed the road
is built for.

| Window | Crashes per hour | Share that injure or kill |
|--------|-----------------:|--------------------------:|
| Rush-hour peak (7-9am, 5-7pm) | 1,152 | 6.7% |
| Late night (12am-5am, road clears) | 301 | 13.5% |

Relative risk 2.02x, chi-square p = 1.3e-18: 203 of the 1,503 late-night crashes injured or
killed, against 463 of 6,912 in the peak (the full set holds 1,504 injury-or-worse crashes). Across all 24
hours the share that injure or kill runs inverse to the crash count (Spearman -0.79): the emptier
the road, the more likely the crash that does happen hurts someone. This is the 4th-power
speed-severity law (Nilsson) showing up in real data: congested traffic produces fender-benders,
and a crash on the clear road is about twice as likely to injure or kill.

Two honest caveats. The late-night window has **less enforcement and more impaired
driving** too, so the severity jump points to speed, it does not prove it alone. Night
property-damage-only crashes are also likely under-reported (fewer police out, the alert feeds
skew to daytime), which shrinks the denominator and can inflate the casualty share on its own. And it is one
road, EDSA, the exact place the objection is strongest. The fatal count itself (22 fatal crashes
in the set) is too small to read hour by hour, which is why the test runs on injury-or-worse, not
deaths alone.

What carries the "built for speed" claim independent of the hour is the **satellite**. OpenStreetMap
has no width tag on most arterials, so the imagery closes the gap: the flagged roads are wide,
straight, multi-lane strips through dense housing (EDSA at ten-plus lanes, Taft Avenue, Cebu's
Natalio Bacalso Avenue, the new Davao City Coastal Road). And the fix is physical, not a sign: only
**20%** of Manila's flagged roads have any traffic calming within 100 m, 16% in Cebu, 4% in Davao.
A crossing manages where people cross. It does not change how fast the car arrives.

Reproduce: `build/overlay/emit_severity_artifact.py` (the hourly split), `build/overlay/satellite_evidence.py`
(the crops). Full test, including the confounds, in `tmp/verify-*/PHASE1_VERDICT.md`.

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
exceeds the safe speed. The imputed majority never glows. The honest headline is the
real-posted count: 9,435 flagged segments. Two cities (Butuan, Puerto Princesa)
have so little posted-limit data they carry no flagged roads at all. The missing limits are
not a flaw to hide: they are exactly where official posted-limit data would add the most.

## 2. Speed-limit mismatch is not a wealth story

You might expect the most dangerous speed limits to fall on poorer neighbourhoods. Joined to
Meta's Relative Wealth Index on a ~1.6 km grid, and measured on the raw posted-over-safe gap
(the mismatch itself, before any exposure weighting), across the 43 cities with enough
real-posted road to grid, the relationship is **absent almost everywhere and significant in
only four**:

| City | Spearman ρ (gap vs wealth) | p | Reading |
|------|--------------------------:|---:|---------|
| Metro Manila | −0.14 | 0.19 | no relationship |
| Cebu City | +0.17 | 0.47 | no relationship |
| Davao City | +0.01 | 0.97 | no relationship |
| Bacolod | −0.63 | 0.035 | **worst mismatch in poorer areas, significant** |
| Tagum | −0.60 | 0.023 | **worst mismatch in poorer areas, significant** |
| Cotabato | −0.61 | 0.044 | **worst mismatch in poorer areas, significant** |
| Laoag | −0.48 | 0.046 | **worst mismatch in poorer areas, significant** |

Thirty-nine of forty-three cities show no significant link, and none of the three biggest metros
does either. Where it **is** significant, all four cities point the same way: the worst
speed-limit mismatch falls on the **poorer** districts. But four significant results out of
43 tests is about what chance alone produces (43 × 0.05 ≈ 2), so even this is a weak signal,
not a national pattern. The honest read: where a posted limit is most out of step with its
road is **not** a wealth story. It is structural, and where wealth does seem to matter it is
a handful of mid-size cities where the poorer side carries the gap, worth a local look rather
than a country-wide claim.

(The correlation is run on the raw gap, which is independent of the exposure weight. Running
it on the full exposure-weighted score instead gives the same cities and the same story,
so folding population density into exposure does not manufacture or hide a wealth link.)

## 3. But the danger does cluster, along particular roads, not by income

The mismatch is not random noise. Moran's I (spatial autocorrelation) on the gap is positive
and significant in several cities, Bacolod +0.38 (p = 0.035), San Jose del Monte +0.41
(p = 0.025), Tagum +0.58 (p = 0.025), Cebu City +0.18 (p = 0.02), meaning high-mismatch cells
sit next to other high-mismatch cells. There are distinct hotspot stretches of road. The danger is
concentrated somewhere even when it is not concentrated by income, and the map's job is to show
exactly where. (Metro Manila, significant on the earlier flagged set, drops just below the
line at +0.08, p = 0.10 once the trunk fix widened the flagged set. Treat it as a lead, not a hotspot.)

## 4. The crowded, the mismatched, and the deadly are three different maps

This is the new axis. WorldPop 2020 population is now folded into the exposure weight, so
"crowdedness" is a real number per road, not a proxy. Three things you would expect to stack
on top of each other instead pull apart.

- **Flagged roads do sit where people are packed.** A flagged real-posted road has a median
  residential density of 12,916 people/km² around it, against 9,450 for an unflagged
  real-posted road. Pick a flagged road and a random unflagged one and the flagged one is the
  denser of the two 56% of the time. The mismatch lands on the busy arterials that cut through
  dense cores, which is what makes it worth flagging.
- **But a bigger gap does not mean a denser place.** At the ~1.6 km cell level the *size* of
  the speed-limit gap barely tracks density at all (Spearman +0.01, p = 0.92, n = 1,157 cells).
  Crowdedness decides *which* roads get flagged, not *how large* the mismatch is. Those are two
  different questions, and only the first has a crowding answer.
- **And the death map points the opposite way.** Metro Manila has by far the most flagged roads
  (5,328) and the densest flagged network in the country (a median 22,599 people/km² around its
  flagged roads), yet the **lowest** road-death rate of any region: 3.6 per 100,000 against a
  national 10.9 (PSA SDG 3.6.1, 2022). Across regions, the crowdedness of the flagged network
  runs slightly *inverse* to the death rate (Spearman −0.17, n = 15), and flagged roads per 100
  scored runs −0.26 (p = 0.24, n = 17). The deadliest regions are rural: Cagayan Valley 22.1,
  Caraga 16.9, Davao 16.8. Deaths are counted by region of residence, dense cities have low
  free-flow speed and better trauma care, and the urban map and the death map are answering
  different questions on purpose.

**The one you can see from space.** The clearest picture of the mismatch is a wide, fast
road slicing through packed low-rise rooftops. In Metro Manila the sharpest examples, all
flagged real-posted roads in the top decile of residential density with a posted limit far over
the survivable speed, are Mel Lopez Boulevard (posted 60, survivable 30, ~103,000 people/km²
around it), C. M. Recto Avenue (60→30), Samson Road (60→30, ~77,759 people/km²), Capulong Street
(60→30), and Quezon Avenue (60→30). In Cebu it is Natalio Bacalso Avenue (60→30). In Davao, the Davao
City Coastal Road (60→30). These are the roads where the survivable-speed gap and the crowd sit
directly on top of each other, and a satellite crop shows why: the road is built for speed and
the ground beside it is wall-to-wall housing.

## Caveats

- Correlation, not causation. A relationship, or its absence, does not explain why.
- Forty-three cities tested at p < 0.05 will throw roughly two false positives by chance. The
  four significant wealth correlations are barely above that floor. Treat them as leads.
- The Relative Wealth Index is a model at ~2.4 km and WorldPop is ~90 m constrained
  (residents, not daytime foot traffic). The grid is coarse and nearby cells are not
  independent, so p-values are optimistic.
- The mismatch metric uses only segments with a real posted limit, to avoid imputation bias.
- Region death rates are by region of usual residence, not crash location. Reading them as a
  city-level score would be the ecological fallacy.
- This is a screening layer to prioritise segments for review, not a final determination.

## Sources

OpenStreetMap (ODbL) · Meta Relative Wealth Index, Data for Good (CC-BY) · WorldPop PH 2020
constrained (CC-BY) · PSA OpenSTAT road-death rate SDG 3.6.1 and land-transport deaths by
region · Safe System speeds: Tingvall & Haworth 1999, ITF/OECD 2018, WHO · Nilsson (1981)
power model · Tefft (2011), AAA.
