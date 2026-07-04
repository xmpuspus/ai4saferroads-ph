# Exposure datasets for crash-correlation control

Goal: a real, downloadable exposure layer (traffic volume or population) to control
correlations on the speed-limit-mismatch map (51 PH cities). Crash counts track
traffic volume, so we need an independent exposure denominator.

All checks below were run live on 2026-06-27. Every "Y" row was fetched THIS session
and the HTTP evidence is pasted. Anything not downloadable is marked NOT ACCESSIBLE.

## Ranked options

| # | Source | URL | Accessible now | Granularity | Format | Direct download |
|---|--------|-----|----------------|-------------|--------|-----------------|
| 1 | WorldPop PH 2020 (constrained, BSGM) | https://hub.worldpop.org/geodata/summary?id=49861 | YES (HTTP 200, 22.8 MB) | ~100 m raster, people/pixel | GeoTIFF | https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/PHL/phl_ppp_2020_constrained.tif |
| 2 | WorldPop PH 2020 (unconstrained) | https://hub.worldpop.org/geodata/summary?id=... (popyear 2020) | YES (HTTP 200, 188.8 MB) | ~100 m raster, people/pixel | GeoTIFF | https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/PHL/phl_ppp_2020.tif |
| 3 | Meta/Facebook HRSL PH (HDX, "AI for Good at Meta") | https://data.humdata.org/dataset/philippines-high-resolution-population-density-maps-demographic-estimates | YES (302 -> S3, HTTP 200, 55.9 MB) | ~30 m raster, people/pixel | GeoTIFF (zip) | https://data.humdata.org/dataset/6d9f35c0-4764-49ee-b364-329db0b7a47d/resource/4a178155-b746-4f04-8f1b-2a79cc6f5153/download/phl_general_2020_geotiff.zip |
| 3b | Meta/Facebook HRSL PH (CSV variant) | same dataset | YES (same dataset, listed) | ~30 m point CSV (lat,lon,pop) | CSV (zip) | https://data.humdata.org/dataset/6d9f35c0-4764-49ee-b364-329db0b7a47d/resource/0b35adea-5104-4598-868f-d4266d05c55a/download/phl_general_2020_csv.zip |
| 4 | DPWH AADT / Annual Traffic Count | https://www.dpwh.gov.ph/dpwh/gis/rti and https://data.gov.ph (AADT dataset) | NOT ACCESSIBLE (machine) | per-station / per-road segment | PDF atlas / FOI request | none -- see notes |

## Evidence (pasted live, 2026-06-27)

### 1. WorldPop PH 2020 constrained (BEST)
hub.worldpop.org REST metadata (id 49861):
- title: "The spatial distribution of population in 2020, Philippines"
- files: GIS/Population/Global_2000_2020_Constrained/2020/BSGM/PHL/phl_ppp_2020_constrained.tif
- format: Geotiff ; license: https://hub.worldpop.org/data/licence.txt (CC BY 4.0)

`curl -sIL` on the direct .tif:
```
HTTP/1.1 200 OK
Content-Length: 22779445
Content-Disposition: attachment
Content-Type: image/tiff
```
Constrained = population only placed on mapped built settlements (cleaner denominator
for urban road work than the unconstrained version, which smears people across all cells).

### 2. WorldPop PH 2020 unconstrained
`curl -sIL https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/PHL/phl_ppp_2020.tif`:
```
HTTP/1.1 200 OK
Last-Modified: Thu, 22 Nov 2018 18:11:49 GMT
Content-Length: 188757526
Content-Disposition: attachment
Content-Type: image/tiff
```
(Note: the v1/maxar_v1 path `.../2020/maxar_v1/PHL/phl_ppp_2020_constrained.tif` returns
HTTP 404 -- the correct constrained path is the BSGM one in row 1.)

### 3. Meta HRSL PH (finer 30 m)
HDX package `philippines-high-resolution-population-density-maps-demographic-estimates`,
org "AI for Good at Meta", license CC BY. General-population GeoTIFF resource:
```
HTTP/2 302
location: https://s3.us-east-1.amazonaws.com/hdx-production-filestore/resources/4a178155-.../phl_general_2020_geotiff.zip?AWSAccessKeyId=...
HTTP/1.1 200 OK
Content-Type: application/zip
Content-Length: 55890943
```
Resolves through HDX -> presigned S3 and returns a 55.9 MB zip. Also a CSV variant
(lat, lon, population per ~30 m cell) at the resource URL in row 3b.

### 4. DPWH AADT -- NOT ACCESSIBLE as a machine download this session
- `https://www.dpwh.gov.ph/` and `/dpwh/gis/rti` are served behind Incapsula WAF;
  the RTI ("Road Traffic Information") page returns HTTP 200 but is JS-rendered with no
  static CSV/Excel/shapefile link or ArcGIS REST (FeatureServer/MapServer) endpoint
  exposed to curl. WebFetch on it failed TLS chain verification ("unable to verify the
  first certificate").
- DPWH GIS subdomains probed and all dead/unreachable: dpwhgis.dpwh.gov.ph,
  gis.dpwh.gov.ph, opendata.dpwh.gov.ph (no HTTP response).
- data.gov.ph hosts an "Annual Average Daily Traffic (AADT)" dataset page, but
  data.gov.ph is an Angular SPA: both `/api/3/action/package_search?q=AADT` and the
  dataset URL return the HTML app shell, not a CKAN JSON payload or a resource file.
  No direct download URL is obtainable programmatically.
- HDX has NO DPWH AADT dataset (search `philippines traffic count AADT road` -> 1 hit,
  and it is HeiGIT "Accessibility Indicators", not traffic volume).
- Public AADT that exists is locked in PDF atlases (NCR AADT DPWH Atlas on Scribd,
  Region IV-A 2018-2022 PDF) or behind an FOI request (foi@dpwh.gov.ph, 60-day SLA).
  Not a clean, downloadable, machine-readable table this session.

## Recommendation

Use **WorldPop PH 2020 constrained (row 1)** as the primary exposure control:
single 22.8 MB GeoTIFF, 100 m, one direct URL, returns HTTP 200 right now, CC BY,
population placed only on built settlements. Sum/zonal-stat population in a buffer
around each scored road segment to get a per-segment exposure denominator.

If you want a finer denominator, **Meta HRSL (row 3, ~30 m)** is also live and
downloadable; trade-off is a 55.9 MB zip and the extra step of unzipping.

Traffic volume (DPWH AADT) would be the more direct exposure proxy, but it is NOT
machine-downloadable: best path is an FOI request, otherwise population is the
practical control.

Sources:
- WorldPop hub: https://hub.worldpop.org/geodata/summary?id=49861
- HDX Meta HRSL PH: https://data.humdata.org/dataset/philippines-high-resolution-population-density-maps-demographic-estimates
- DPWH RTI: https://www.dpwh.gov.ph/dpwh/gis/rti
- data.gov.ph AADT: https://data.gov.ph/index/public/dataset/Annual%20Average%20Daily%20Traffic%20(AADT)/ua1r4ams-fav9-yyqw-kdww-kjbqxpiev6la
- DPWH FOI: https://www.foi.gov.ph/agencies/dpwh/
