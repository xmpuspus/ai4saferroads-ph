# Crash-Dataset Refresh — geolocated PH road-crash data for SSS validation

Re-probe date: 2026-06-27. Goal: a real, downloadable, geolocated (lat/lon) PH road-crash
dataset to join crashes onto SSS road segments. Every row below was fetched live this session;
HTTP status and proof are pasted.

## Ranked table

| Rank | Source | URL | Accessible now | Granularity | Years | Key fields | Direct download |
|---|---|---|---|---|---|---|---|
| 1 | Mendeley EDSA RTA (UP Diliman / MMDA) | https://data.mendeley.com/datasets/hwbf6n4krw | YES | POINT (3,047 unique lat/lon along EDSA) | 2007-2016 | Y, X (lat/lon), DATETIME_PST, SEVERITY, killed_*/injured_* breakdown, COLLISION_TYPE, MAIN_CAUSE, WEATHER, LIGHT, ROAD | https://data.mendeley.com/public-files/datasets/hwbf6n4krw/files/5444e91a-c151-4513-92af-9e2e3610df75/file_downloaded |
| 2 | MMDA traffic incidents (esparko Kaggle, GitHub mirror) | https://github.com/PotatoC0der/mmda_traffic_analysis | YES | POINT (lat/lon, Metro Manila wide) | 2018 (Aug onward) | Date, Time, City, Location, Latitude, Longitude, High_Accuracy, Direction, Type, Lanes_Blocked, Involved, Tweet, Source | https://raw.githubusercontent.com/PotatoC0der/mmda_traffic_analysis/main/data_mmda_traffic_spatial.csv |
| 3 | Safe Travel PH open-data inventory (ODbL) | https://www.safetravelph.org/data-inventory | PARTIAL (Google Drive folder loads; file list not machine-enumerable via curl) | unknown (folder) | unknown | unknown | https://drive.google.com/drive/folders/1HY1BDSVR6ppVE4SJCZFwDY-ZK1d0nzqk |
| 4 | roadsafety.gov.ph (DRIVER / World Bank GRSF) | https://roadsafety.gov.ph | NO — connection timeout (no export found) | n/a | n/a | n/a | NOT ACCESSIBLE |
| 5 | data.gov.ph | https://data.gov.ph | NO crash dataset (site up, no CKAN API, search returns no road-crash dataset) | n/a | n/a | n/a | NOT ACCESSIBLE |
| 6 | HDX (data.humdata.org) | https://data.humdata.org | NO PH crash POINT data (only road-surface + Nepal crash records) | n/a | n/a | n/a | NOT ACCESSIBLE |

## Evidence per lead

### 1. Mendeley EDSA RTA 2007-2016 (hwbf6n4krw) — BEST
Public file-listing API (no auth):
`GET https://data.mendeley.com/public-api/datasets/hwbf6n4krw/files?folder_id=root&version=1`
returned:
```
[{"filename":"RTA_EDSA_2007-2016.zip", "size":2639368,
  "download_url":"https://data.mendeley.com/public-files/datasets/hwbf6n4krw/files/5444e91a-c151-4513-92af-9e2e3610df75/file_downloaded",
  "content_type":"application/zip", "status":"COMPLETED"}]
```
(Note: `api.data.mendeley.com` returned `Unauthorized`; the `data.mendeley.com/public-api/...`
path is the unauthenticated one that works.)

Downloaded zip -> HTTP 200, 2,639,368 bytes. Contains one file:
`RTA_EDSA_2007-2016.xls` (12,805,632 bytes).

Real columns (read with pandas+xlrd):
```
LOCATION_TEXT, ROAD, WEATHER, LIGHT, DESC, REPORTING_AGENCY, MAIN_CAUSE,
INCIDENTDETAILS_ID, DATE_UTC, TIME_UTC, ADDRESS, killed_driver, killed_passenger,
killed_pedestrian, injured_driver, injured_passenger, injured_pedestrian,
killed_uncategorized, injured_uncategorized, killed_total, injured_total,
DATETIME_PST, SEVERITY, Y, X, COLLISION_TYPE
```
`Y` = latitude, `X` = longitude. Sample rows (head):
```
ROAD=EDSA  DATETIME_PST=2014-06-30 13:40:00  SEVERITY=Property  Y=14.657714  X=121.019788  ADDRESS=Congressional Ave...
ROAD=EDSA  DATETIME_PST=2014-03-17 09:00:00  SEVERITY=Property  Y=14.657714  X=121.019788
ROAD=EDSA  DATETIME_PST=2013-11-26 10:00:00  SEVERITY=Injury    Y=14.657714  X=121.019788  injured_passenger=1
```
Spread (computed): 22,072 rows, 3,047 unique (Y,X) pairs — real per-location geolocation,
not one repeated point. Lat 14.5354-14.6579, Lon 120.9837-121.0600 (the EDSA corridor).
Date range 2007-01-01 to 2016-12-28. Totals: 23 killed, 2,067 injured.
Caveat: EDSA corridor only (single arterial), older (ends 2016), severity skews to Property.

### 2. MMDA traffic incidents — esparko Kaggle dataset, GitHub mirror
GitHub repo search (`q=mmda+traffic+incident`) -> `PotatoC0der/mmda_traffic_analysis`.
Tree listing showed `data_mmda_traffic_spatial.csv`.
Raw fetch -> 17,336 data rows. Header + real sample rows:
```
Date,Time,City,Location,Latitude,Longitude,High_Accuracy,Direction,Type,Lanes_Blocked,Involved,Tweet,Source
2018-08-20,7:55 AM,Pasig City,ORTIGAS EMERALD,14.586343,121.061481,1,EB,VEHICULAR ACCIDENT,1.0,TAXI AND MC,"MMDA ALERT: Vehicular accident at Ortigas Emerald EB...",https://twitter.com/mmda/status/1031330201970532352
2018-08-20,9:13 AM,Makati City,EDSA ROCKWELL,14.559818,121.040737,1,SB,VEHICULAR ACCIDENT,1.0,SUV AND L300,"MMDA ALERT: Vehicular accident at EDSA Rockwell SB...",https://twitter.com/mmda/status/1031358966989615104
```
Has explicit `Latitude`/`Longitude`, Metro Manila wide (Pasig, Mandaluyong, Makati, ...),
plus `High_Accuracy` geocode-confidence flag. This is the geocoded version of the esparko
"mmda-traffic-incident-data" Kaggle set (sourced from MMDA Twitter alerts).
Caveat: `Type` mixes true crashes (VEHICULAR ACCIDENT) with non-crash incidents
(STALLED L300 ...). Filter `Type` to vehicular-accident rows before joining. 2018-start.

### 3. Safe Travel PH (safetravelph.org/data-inventory) — ODbL claim
`GET https://www.safetravelph.org/data-inventory` -> HTTP 200. Page links its open data to a
Google Drive folder: `https://drive.google.com/drive/folders/1HY1BDSVR6ppVE4SJCZFwDY-ZK1d0nzqk`
(also a sibling `/open-data` page). License referenced: ODbL
(opendatacommons.org/licenses/odbl/1-0/). The Drive folder returns HTTP 200 (948,581 bytes of
HTML) but curl cannot enumerate the per-file list (JS-rendered Drive UI). Needs a browser to
open the folder and pick files — PARTIAL, not a one-shot curl download.

### 4. roadsafety.gov.ph (DRIVER / World Bank GRSF) — NOT ACCESSIBLE
`https://roadsafety.gov.ph` -> curl (28) connection timed out (12s, retried 10s; tried
`http://`, `https://www.` = DNS no-resolve). Tried `/api/`, `/api/records/`, `/data/` -> all
timeout HTTP 000. No data export, API, WMS/WFS, or tiles reachable this session.

### 5. data.gov.ph — NO crash dataset
`https://data.gov.ph` -> HTTP 200, but it is NOT a CKAN portal: `/api/3/action/package_search`
returns `Content-Type: text/html` (not JSON) and the body is not parseable as CKAN.
`/search?q=road+accident` -> HTTP 200 but no dataset result rows. No downloadable road-crash /
traffic-accident dataset found.

### 6. HDX (data.humdata.org) — NO PH crash POINT data
CKAN API live and parsed:
- `q=philippines+road+crash` (count 22): top hits are Road Surface Data, OSM Roads Export,
  Planet Road Surface, World Bank Infrastructure/Urban indicators. No crash points.
- `q=philippines+traffic+accident` (count 18): crash-records hits are all **Nepal**
  (Road Traffic Accident Records 2013, Causes of Road Accidents 2013); PH hits are only
  World Bank indicator tables. No PH crash POINT dataset.

## Recommendation for SSS validation
Use **both 1 and 2 together**: EDSA (1) gives the cleanest severity-tagged, per-location
crash points for the EDSA arterial (good for a focused validation on the corridor where SSS
mismatch matters most), and the MMDA GitHub CSV (2) gives Metro-Manila-wide coverage for a
broader spatial join (filter `Type` to vehicular-accident rows). Neither covers all 51 cities;
both are Metro Manila. roadsafety.gov.ph DRIVER remains the only national source and is still
unreachable — treat as FOI/contact-required, not open download.
