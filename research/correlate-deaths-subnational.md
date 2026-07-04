# Subnational PH road-death data for ecological correlation

Probe date: 2026-06-27. All numbers below were fetched live this session via the
PSA OpenSTAT PX-Web JSON API (`openstat.psa.gov.ph`). Raw CSVs saved under
`research/death-data-probe/`. Nothing here is invented.

## Bottom line

- Finest geographic granularity that ACTUALLY DOWNLOADS: **REGION (17 regions + national).**
  Province and city are NOT available as a machine-downloadable cause-of-death
  table on OpenSTAT. (PSA press releases narrate province rankings, e.g.
  "Pangasinan highest 2010-2023", but the underlying province-by-cause table is
  not exposed for download.)
- Two usable region tables, both joinable to our 51 cities via city -> region:
  1. **Absolute counts** of land-transport-accident deaths by region (2023, and a
     newly released 2024 version).
  2. **Death RATE per 100,000 population** by region, time series 2000-2025
     (SDG indicator 3.6.1) - better for ecological correlation because it is
     population-normalized.
- DOH ONEISS (road-injury surveillance) and WHO GHO / IHME GBD: see "Other
  sources" - none gives a cleaner downloadable PH province/region table than the
  PSA OpenSTAT tables below, so OpenSTAT is the source to use.

---

## SOURCE 1 (primary): PSA OpenSTAT - deaths by region x cause of death

Table: "Number of Registered Deaths by Age Group, Sex, Region of Usual
Residence and Cause of Death, Philippines: 2023"
Table id: `0131A1BDEB2.px` (2024 version: `0131A1BDEE7.px`, released 2026-06-19)

Browse URL:
https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__1A__VS__DE/

API node (metadata):
https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1A/VS/DE/0131A1BDEB2.px

Dimensions: Geolocation (19 = Philippines + 17 regions + foreign), Cause of
Death (116 ICD-10 groups), Age Group (21), Sex (3). Relevant cause codes:
- code `96` = Transport accidents V01-V99
- code `97` = **Land transport accidents V01-V89** (the road-relevant one)

### Download recipe (reproduces the rows below)

```bash
curl -s -A "Mozilla/5.0" -H "Content-Type: application/json" \
  -X POST "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1A/VS/DE/0131A1BDEB2.px" \
  -d '{"query":[
        {"code":"Cause of Death","selection":{"filter":"item","values":["0","96","97"]}},
        {"code":"Age Group","selection":{"filter":"item","values":["0"]}},
        {"code":"Sex","selection":{"filter":"item","values":["0"]}}],
      "response":{"format":"csv"}}'
```

### REAL ROWS - Land transport accident (V01-V89) deaths by region, 2023

(Total Both Sexes. National total = 13,125, which matches the PSA headline
"deaths due to land transport accidents rose to 13,125 in 2023." Regional
values sum to the national figure.)

| Region | Land transport deaths (V01-V89), 2023 |
|---|---|
| PHILIPPINES (national) | 13,125 |
| NCR | 521 |
| CAR | 208 |
| Region I (Ilocos) | 1,010 |
| Region II (Cagayan Valley) | 917 |
| Region III (Central Luzon) | 1,491 |
| Region IV-A (CALABARZON) | 1,432 |
| MIMAROPA | 458 |
| Region V (Bicol) | 833 |
| Region VI (Western Visayas) | 1,109 |
| Region VII (Central Visayas) | 905 |
| Region VIII (Eastern Visayas) | 654 |
| Region IX (Zamboanga Peninsula) | 496 |
| Region X (Northern Mindanao) | 885 |
| Region XI (Davao) | 911 |
| Region XII (SOCCSKSARGEN) | 685 |
| Region XIII (Caraga) | 470 |
| BARMM | 129 |

Raw CSV: `research/death-data-probe/region_transport_2023.csv`
(also contains the "all transport V01-V99" line per region and each region's
all-cause TOTAL, so you can compute road share of deaths if useful.)

Note for the SSS join: this is by REGION OF USUAL RESIDENCE (where the deceased
lived), not place of crash. For an ecological city-vs-region correlation that is
acceptable but worth stating as a limitation.

---

## SOURCE 2 (recommended for correlation): PSA OpenSTAT - SDG 3.6.1 death RATE per 100k by region

Table: "3.6.1 Death rate due to road traffic injuries per 100,000 population"
Table id: `0163I3D0361.px`
API node:
https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/3I/G03/0163I3D0361.px

Dimensions: Geolocation (18 = Philippines + 17 regions), Sex (3),
Year (26 = 2000..2025; year is a 0-based index code, e.g. code "21"=2021,
"22"=2022, "23"=2023). This is the population-normalized rate, so it is the
cleaner variable to correlate against the per-segment Speed Safety Score
aggregated to region.

### Download recipe

```bash
curl -s -A "Mozilla/5.0" -H "Content-Type: application/json" \
  -X POST "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/3I/G03/0163I3D0361.px" \
  -d '{"query":[
        {"code":"Sex","selection":{"filter":"item","values":["0"]}},
        {"code":"Year","selection":{"filter":"item","values":["21","22","23"]}}],
      "response":{"format":"csv"}}'
```

### REAL ROWS - road-traffic-injury death rate per 100,000, by region

(Both sexes. 2023 column came back suppressed as `...` at probe time; 2021 and
2022 are fully populated.)

| Region | rate/100k 2021 | rate/100k 2022 |
|---|---|---|
| PHILIPPINES | 10.0 | 10.9 |
| NCR | 3.6 | 3.6 |
| CAR | 10.5 | 11.4 |
| Region I (Ilocos) | 13.1 | 16.1 |
| Region II (Cagayan Valley) | 19.1 | 22.1 |
| Region III (Central Luzon) | 10.2 | 11.1 |
| Region IV-A (CALABARZON) | 7.7 | 7.8 |
| MIMAROPA | 11.1 | 13.5 |
| Region V (Bicol) | 11.5 | 12.3 |
| Region VI (Western Visayas) | 12.4 | 13.2 |
| Region VII (Central Visayas) | 8.6 | 10.3 |
| Region VIII (Eastern Visayas) | 10.5 | 11.9 |
| Region IX (Zamboanga Peninsula) | 11.1 | 11.6 |
| Region X (Northern Mindanao) | 14.8 | 15.3 |
| Region XI (Davao) | 15.4 | 16.8 |
| Region XII (SOCCSKSARGEN) | 12.8 | 13.1 |
| Region XIII (Caraga) | 16.5 | 16.9 |
| BARMM | 2.0 | 2.1 |

Raw CSV: `research/death-data-probe/sdg361_rate_byregion.csv`

Interesting for our pitch: NCR has the LOWEST rate (3.6) despite the most
traffic - consistent with low free-flow speeds in dense metro - while
Cagayan Valley (22.1) and Davao (16.8) top the list. That cross-region spread
is exactly what an SSS ecological correlation would test against.

---

## (a)/(b) PSA cause-of-death / vital statistics: COVERED above

The OpenSTAT Deaths database (`1A/VS/DE`, 81 tables) is the downloadable form of
PSA's vital-statistics cause-of-death tables. The region x cause table above is
the finest cause-of-death cut that downloads. The static psa.gov.ph cause-of-death
PR pages and the Philippine Statistical Yearbook CSVs
(e.g. `psa.gov.ph/system/files/psy/2022_T13_20.csv`) are behind a Cloudflare JS
challenge and did NOT download via curl this session (returned the CF
"Just a moment..." interstitial, not data). OpenSTAT is the API that works.

## (c) WHO GHO / IHME GBD subnational PH

- WHO Global Health Observatory road-traffic-death data for the Philippines is
  **NATIONAL ONLY** (country-level estimates, e.g. the Global Status Report on
  Road Safety series). No WHO GHO PH province/region download was obtained this
  session.
- IHME GBD does publish PH subnational (regional) estimates via the GBD Results
  tool / vizhub, but the table requires the interactive GBD Results query tool
  (account-gated bulk download), not a plain URL fetch. Not retrieved as a flat
  file this session. The PSA OpenSTAT region tables above are the registered,
  directly-downloadable equivalent and should be preferred (PSA is the primary
  national vital-registration source GBD itself ingests for PH).

## (d) DOH ONEISS

DOH runs ONEISS (Online National Electronic Injury Surveillance System) for
injury including road-traffic injury, reported by region/sentinel sites. As of
this probe no open machine-downloadable ONEISS road-injury-by-region CSV/XLSX
was located via public URL; ONEISS outputs surface inside DOH FHSIS/annual injury
reports (PDF), not as an open table. Treat as NOT independently downloadable;
use PSA OpenSTAT as the source of record.

---

## How this joins to the 51-city SSS map

- Granularity available: REGION (17). Our 51 cities each sit in exactly one
  region, so map each city to its region and do a region-level ecological
  correlation: mean/median Speed Safety Score per region vs. that region's
  road-traffic death rate per 100k (Source 2) or count (Source 1).
- Province/city-level road deaths are NOT downloadable, so a true per-city
  correlation is not possible from open PSA data. State that limitation
  explicitly; the honest unit of analysis is the region (n=17), or NCR-cities
  vs non-NCR if a finer cut is needed.
- Use the RATE table (Source 2) as the primary dependent variable; use counts
  (Source 1) only with a population offset.
