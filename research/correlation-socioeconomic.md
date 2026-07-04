# Speed Safety Score: Socioeconomic & Pedestrian-Exposure Dataset Research

**Objective:** Identify open, accessible socioeconomic and pedestrian-exposure datasets that could reveal surprising spatial correlations with speed-limit mismatch (posted limits vs. Safe System limits) across Metro Manila, Cebu, and Hanoi.

**Date:** 2026-06-25  
**Status:** Verified; datasets marked GO/NO-GO for immediate integration

---

## 1. Population Density Grids

### WorldPop 100m Global Coverage
- **URL:** https://hub.worldpop.org/geodata/summary?id=6316 (Philippines) | https://hub.worldpop.org/geodata/summary?id=6449 (Vietnam)
- **Resolution:** 3 arc-seconds (~100m at equator)
- **Format:** GeoTIFF (WGS84, EPSG:4326)
- **License:** CC-BY 4.0 (attribution required, free for any use)
- **File size:** ~188 MB per country
- **Access:** Direct download, no authentication required
- **Methodology:** Random Forest dasymetric redistribution using OpenStreetMap, settlement locations, land cover, roads, building maps, satellite night lights
- **Status:** [GO] — Directly downloadable, suitable for pixel-level analysis

### Meta High Resolution Settlement Layer (HRSL)
- **URL:** https://registry.opendata.aws/dataforgood-fb-hrsl/
- **Resolution:** 30 meters
- **Format:** Cloud-optimized GeoTIFF (CoG) + CSV
- **License:** CC-BY 4.0
- **Access:** AWS S3 no-sign-request (no AWS account needed)
- **Coverage:** 93 LMI countries including Philippines and Vietnam
- **Includes:** Population counts + demographic estimates (children <5, women reproductive age, elderly)
- **S3 command:** `aws s3 ls --no-sign-request s3://dataforgood-fb-data/hrsl-cogs/`
- **Status:** [GO] — High-resolution settlement detail; 30m resolution captures informal settlement clusters better than 100m

### Global Human Settlement Layer (GHS-POP)
- **URL:** https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php | https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_POP
- **Resolution:** 100m (Mollweide projection)
- **Format:** GeoTIFF
- **License:** Creative Commons (free)
- **Access:** Direct download from Copernicus portal + Google Earth Engine
- **Epochs:** 1975–2030 in 5-year intervals
- **Status:** [GO] — Established baseline; Earth Engine access suitable for time-series analysis

---

## 2. Poverty / Income / Deprivation

### PSA Small Area Estimation (SAE) — City & Municipal Level
- **URL:** https://psa.gov.ph/statistics/poverty | https://psa.gov.ph/statistics/poverty/stat-tables
- **Granularity:** City/municipality level (114 cities + 1,483 municipalities in PH)
- **Indicators:** Poverty incidence rate, poverty gap, severity of poverty
- **Latest data:** 2023 (full year), released 2024
- **Format:** Published as tables + thematic maps (downloadable)
- **Method:** Census Empirical Best/Bayes estimation (World Bank Small Area Estimation)
- **Access:** Open portal (https://openstat.psa.gov.ph) — no authentication
- **Limitation:** City/municipality aggregate; insufficient for barangay-level or segment-level analysis
- **Status:** [NO-GO] — Too coarse for road-segment correlation; cannot pinpoint mismatch concentration in poorest barangays

### Meta Relative Wealth Index (RWI)
- **URL:** https://dataforgood.facebook.com/dfg/tools/relative-wealth-index#accessdata | https://data.humdata.org/dataset/relative-wealth-index
- **Resolution:** 2.4 km grid cells
- **Coverage:** 93 LMI countries (Philippines + Vietnam included)
- **Format:** CSV point data + GeoTIFF raster
- **Indicator:** Relative standard of living (de-identified connectivity + satellite imagery + nontraditional data)
- **License:** CC-BY 4.0
- **Access:** Direct download from HDX (Humanitarian Data Exchange) or Meta Data for Good portal
- **Status:** [GO] — Sub-city-level granularity (2.4 km) aligns better with road-segment analysis; captures wealth disparities within cities

### Humanitarian Data Exchange (HDX) Poverty Layers
- **URL:** https://data.humdata.org/dataset/relative-wealth-index
- **Note:** RWI dataset listed above; HDX also aggregates other LMI-country poverty proxies
- **Status:** [GO] — Central discovery portal for verified open datasets

---

## 3. Schools & Health Facilities (Official)

### Philippines: DepEd Schools Masterlist (Shapefile)
- **URL:** https://data.humdata.org/dataset/philippines-education-0-0
- **Format:** ESRI Shapefile (phl_schp_deped.zip, 1.2 MB) + attribute table with school names
- **Granularity:** National point layer, all DepEd schools
- **License:** EO 2, 2016 (public use permitted)
- **Access:** Direct download, no authentication
- **Status:** [GO] — Complete, official DepEd layer; directly usable for pedestrian-exposure near-schools overlay

### Philippines: DOH Health Facilities
- **URL:** https://nhfr.doh.gov.ph/VActivefacilitiesList (National Health Facility Registry)
- **Format:** Web registry (queryable) + ArcGIS feature service layer: https://www.arcgis.com/home/item.html?id=069345362c2d40cfaf0d00c9014c76d9
- **Granularity:** Facility-level (public + private health centers)
- **License:** Government of PH (public domain equivalent)
- **Access:** Web interface (no bulk download documented); ArcGIS layer may support export
- **Status:** [PARTIAL] — Official source; web interface available but bulk shapefile download not directly advertised; ArcGIS layer may require Esri client

### Vietnam: OSM Schools & Hospitals via Geofabrik
- **URL:** https://download.geofabrik.de/asia/vietnam.html
- **Format:** ESRI Shapefile (.shp.zip), GeoPackage (.gpkg.zip), OSM native (.pbf)
- **Granularity:** National POI layer extracted from OpenStreetMap
- **Coverage:** Schools (amenity=school) + hospitals (amenity=hospital, healthcare=hospital)
- **License:** ODbL (open)
- **Access:** Direct download, no authentication
- **Query alternative:** Overpass Turbo API or QuickMapTools (draw bounding box, export GeoJSON)
- **Status:** [GO] — OSM-derived but functional for Vietnam analysis; Hanoi-specific subset available via Overpass

---

## 4. Informal Settlements / Urban Poor Density

### GHSL Degree of Urbanisation (Rural-Urban Classification)
- **URL:** https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_SMOD_V2-0 | https://human-settlement.emergency.copernicus.eu/CFS.php
- **Resolution:** 1 km grid
- **Epochs:** 1975–2030 in 5-year intervals
- **Classification:** 10 settlement classes (from isolated hamlets to dense urban centers) using UN-recommended degree of urbanisation
- **Methodology:** Population density + contiguity thresholds
- **Limitation:** Coarse 1 km grid obscures small/informal settlements; rule-based classification doesn't label "informal" per se
- **Access:** Earth Engine (free, account required) + direct download from Copernicus
- **Status:** [PARTIAL] — Identifies urbanisation degree but doesn't isolate informal settlements; useful as a proxy but not definitive

### WorldPop + GHSL Layering Technique
- **Approach:** Combine GHS-POP (population) + GHSL-SMOD (urbanisation class) to identify high-density, sparse-infrastructure areas as informal-settlement proxies
- **Status:** [GO-DERIVED] — Not a direct dataset but a computational proxy

---

## 5. Night-time Lights (Economic Activity Proxy)

### VIIRS Nighttime Lights (NOAA)
- **URL:** https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V22 (Earth Engine)
- **Resolution:** Monthly (500m) + Annual (500m) composites
- **Temporal coverage:** 2012–2024
- **Indicator:** Radiance (nanoWatts/cm²/sr) as proxy for economic activity, electrification, development level
- **Processing:** Cloud-free, stray-light corrected, lunar-glint filtered
- **Limitation:** Seasonal noise, cloud cover gaps, saturation in bright cities
- **Access:** Google Earth Engine (free account required) + NOAA archives
- **Status:** [GO] — Directly accessible via Earth Engine; suitable for time-series correlation with speed-limit mismatch trends

---

## 6. Proposed Computable Overlays & Surprising Correlations

### Overlay 1: Speed-Limit Mismatch × Wealth Disparity (Primary recommendation)
- **Layers:** Road segments (mismatch score) + Meta RWI (2.4 km)
- **Join method:** Sample RWI at road-segment midpoint; aggregate RWI within 500m buffer of segment; compute correlation
- **Hypothesis:** Mismatch may concentrate in lower-RWI areas (informal/poorer neighborhoods) due to light traffic enforcement, informal settlements expanding into main roads, or under-resourced barangay traffic management
- **Surprising potential:** If true, reveals equity dimension: highest-risk pedestrian zones are also lowest-resource areas (no signals, no sidewalks, minimal enforcement)
- **Data sources:** Road segments (OSM + local traffic survey) + RWI (Meta HDX)
- **Status:** [GO] — Both datasets freely available; feasible for Hanoi + MM + Cebu immediately

### Overlay 2: Mismatch × School Proximity (Secondary)
- **Layers:** Road segments + DepEd schools (PH) + OSM schools (Vietnam)
- **Join method:** Flag road segments within 500m of any school; compute % of flagged segments with mismatch score >0.5
- **Hypothesis:** Schools in informal/dense urban areas may have disproportionate mismatch (posted limits=50 but Safe System=20 due to high foot traffic)
- **Surprising potential:** Reveals whether mismatch problem is concentrated near schools in deprived areas vs. uniformly distributed
- **Status:** [GO] — Schools data available for both countries

### Overlay 3: Mismatch × Night-Lights Decline (Exploratory)
- **Layers:** Road segments + VIIRS annual composites (2015–2024)
- **Join method:** Extract VIIRS trend at segment location; compute whether declining-light areas show higher mismatch (possibly indicating informal expansion into former industrial zones)
- **Hypothesis:** Historical industrial/mixed-use roads (bright in 2015, dim in 2024) may have undergone rapid informal settlement, changing pedestrian volumes without posted-limit updates
- **Status:** [GO-EXPLORATORY] — VIIRS accessible but temporal correlation requires 2-3 years of segment-level tagging (future data collection)

### Overlay 4: Informal Density Proxy (GHSL-SMOD + GHS-POP)
- **Layers:** Road segments + derived informal-proxy (high GHS-POP density + GHSL-SMOD low-urbanisation-class cells)
- **Join method:** Segment-level summary statistics (% of buffer in "sparse" + "very low density" + "low density" classes with >100 people/km²)
- **Hypothesis:** Mismatch peaks in transitional areas: high informal density but still main-road infrastructure
- **Limitation:** GHSL-SMOD cannot distinguish informal from rural; requires manual validation
- **Status:** [PARTIAL-GO] — Computable but crude proxy; best used as secondary signal

---

## Summary: GO Datasets for Immediate Integration

| Dataset | Purpose | Resolution | License | Access | Effort |
|---------|---------|-----------|---------|--------|--------|
| **Meta RWI** | Wealth disparity proxy | 2.4 km | CC-BY 4.0 | HDX download | Low |
| **WorldPop 100m** | Population baseline | 100 m | CC-BY 4.0 | Direct DL | Low |
| **HRSL 30m** | Fine-grain settlement | 30 m | CC-BY 4.0 | AWS S3 | Low |
| **DepEd Shapefile (PH)** | Schools | Points | EO 2, 2016 | HDX download | Low |
| **OSM Schools (VN)** | Schools | Points | ODbL | Geofabrik | Low |
| **VIIRS Annual** | Economic activity | 500 m | Public | Earth Engine | Low |
| **GHS-POP + SMOD** | Urban classification | 100 m + 1 km | CC-BY | Copernicus + EE | Low |

---

## Single Best GO Overlay: Speed Mismatch × Meta RWI

**The single strongest immediate overlay is: Road-segment mismatch score × Meta Relative Wealth Index**

**Why:**
- RWI directly captures wealth disparity (the primary equity signal), avoiding proxy-layering
- 2.4 km resolution is fine enough for city-level analysis yet aggregatable to segments
- Both datasets are free, openly licensed, and download-ready
- Result would directly surface: "mismatch is concentrated in the lowest-wealth urban areas"

**How to join:**
1. **Preparation:**
   - Download RWI CSV/GeoTIFF from HDX for PH + Vietnam
   - Reproject to local UTM zones (PH: UTM zone 51N; Vietnam: UTM zone 48N/49N)
   - Prepare road segments as LineString geometries (source: OSM or local traffic survey)

2. **Spatial join:**
   - For each road segment, compute segment midpoint and 500m buffer
   - Sample RWI raster at midpoint (point sample)
   - Aggregate RWI pixels within buffer: mean, std, min (percentile 10th)
   - Join RWI values to segment attributes

3. **Correlation analysis:**
   - Segment mismatch score: (posted_limit - safe_system_limit) / safe_system_limit (scaled 0–1)
   - Plot: RWI decile (x-axis, 10=richest) vs. % of segments with mismatch >0.5 (y-axis)
   - Compute Pearson/Spearman correlation coefficient
   - Flag barangays/wards where mismatch + low-RWI co-locate

4. **Output:**
   - GeoJSON: segments colored by mismatch + RWI interaction
   - CSV: barangay-level summary (avg RWI, % high-mismatch, population density, schools nearby)
   - 1-2 page findings memo: "Speed-limit mismatch concentrates in the lowest-wealth urban areas by X%"

**Tools:** QGIS (shapefile join) or Geopandas (Python script ~100 lines)

**Timeline:** 3–5 days (data download + join + analysis + visualization)

---

## Caveats & Next Steps

1. **Vietnam health facility data:** Official MOH dataset is not directly downloadable; OSM coverage is community-sourced and may be incomplete in rural Hanoi. Recommendation: use OSM for initial analysis, flag gaps for local validation.

2. **Informal settlement specificity:** GHSL-SMOD does not explicitly label "informal"; use as secondary signal only. Primary signal is RWI (wealth) + GHS-POP (population density) + DepEd/OSM schools (pedestrian exposure).

3. **Speed-limit ground truth:** This research assumes authoritative posted-limit data exists (from LTO, MMDA, Cebu City Traffic, Hanoi traffic authority). Verification of segment-level limits is a prerequisite; no open dataset covers this yet.

4. **Temporal dynamics:** All datasets are static or coarse-temporal (annual). Mismatch may be driven by rapid informal growth (2020–2026); VIIRS time-series could reveal this if segment-level tagging is done retrospectively.

---

## References & URLs

- [WorldPop Philippines 100m](https://hub.worldpop.org/geodata/summary?id=6316)
- [WorldPop Vietnam 100m](https://hub.worldpop.org/geodata/summary?id=6449)
- [Meta HRSL AWS Registry](https://registry.opendata.aws/dataforgood-fb-hrsl/)
- [GHSL GHS-POP 2023](https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php)
- [GHSL Earth Engine Catalog](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_POP)
- [PSA Poverty Statistics](https://psa.gov.ph/statistics/poverty)
- [Meta RWI HDX](https://data.humdata.org/dataset/relative-wealth-index)
- [DepEd Schools Shapefile (HDX)](https://data.humdata.org/dataset/philippines-education-0-0)
- [DOH National Health Facility Registry](https://nhfr.doh.gov.ph/VActivefacilitiesList)
- [Geofabrik Vietnam OSM Download](https://download.geofabrik.de/asia/vietnam.html)
- [VIIRS Nighttime Lights Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V22)
- [GHSL Degree of Urbanisation EE](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_SMOD_V2-0)
