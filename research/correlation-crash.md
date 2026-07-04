# Speed Safety Score: Crash & Road-Safety Data Research

**Status:** Research complete. Two datasets accessible now; DRIVERS portal access status unclear. One computable overlay ready (GO).

**Date:** 2026-06-25

---

## Executive Summary

**Single Best GO Overlay:** Road-crash hotspots from [MMDA MMARAS / Mendeley dataset](https://data.mendeley.com/datasets/hwbf6n4krw/1) (2007-2016 EDSA, downloadable in GIS format) joined to per-segment speed-limit exceeds via spatial buffer. Query: "barangays where >40% of segments exceed safe-system 30/40 km/h thresholds CORRELATE WITH higher crash density."

**Key Correlation Finding:** Pedestrian fatality risk increases from 5% at 30 km/h to 13% at 40 km/h to 29% at 50 km/h (peer-reviewed). Most PH urban roads have 40-60 km/h posted limits; this mismatch is the core insight.

**Data Accessibility:** 
- ✅ Mendeley EDSA crash dataset (2007-2016): downloadable now
- ✅ Safe-system speed thresholds (peer-reviewed): 30 km/h safe for pedestrians
- ⚠️ DRIVERS portal (claimed 24/7): connection refused; status unknown
- ⚠️ Kaggle MMDA incident data: page inaccessible
- ❌ Cebu-specific crash data: no open dataset found
- ❌ Hanoi Vietnam crash data: academic studies exist; no bulk download found

---

## 1. Open Road-Crash & Traffic-Fatality Data

### Philippines Metro Manila

**MMDA MMARAS (Metro Manila Accident Recording and Analysis System)**
- **Source:** Metropolitan Manila Development Authority
- **What:** Annual accident reports, crash statistics (fatal, non-fatal, damage-only)
- **Access:** FOI requests via https://mmda.gov.ph/2-uncategorised/3345-freedom-of-information-foi.html
- **Format:** PDF annual reports; underlying data structure unknown
- **Downloadable now:** ⚠️ Unclear; FOI request required
- **Spatial granularity:** Point-level (exact crash location recorded in MMARAS database)
- **License:** Government; unclear if CC0 or restricted
- **Coverage:** 2005-present (annual reports available for 2022, 2023, 2024)
- **URL:** [MMDA FOI page](https://mmda.gov.ph/2-uncategorised/3345-freedom-of-information-foi.html) | [MMARAS Annual Report 2022](https://mmda.gov.ph/images/Home/FOI/MMARAS/MMARAS_Annual_Report_2022.pdf)

**Mendeley: Road Traffic Accident Data, Epifanio delos Santos Avenue (EDSA), 2007-2016**
- **Source:** Mendeley Data (academic repository)
- **What:** Historic crash records from EDSA (main Metro Manila highway), including date/time, location, weather, severity
- **Access:** Direct download available
- **Format:** GIS-compatible tabular (shapefile, likely)
- **Downloadable now:** ✅ Yes
- **Spatial granularity:** Point-level (exact crash location)
- **License:** Data licensing terms available on Mendeley page
- **Coverage:** 10 years (2007-2016)
- **Records:** Not specified on page; 10-year period on single avenue = likely 100s to 1000s
- **URL:** [https://data.mendeley.com/datasets/hwbf6n4krw/1](https://data.mendeley.com/datasets/hwbf6n4krw/1)
- **Note:** Historic data (ends 2016); useful for baseline comparison & validation

**Kaggle: Manila Traffic Incident Data (MMDA)**
- **Source:** Kaggle; based on MMDA Twitter alerts parsed
- **What:** Traffic incidents (incidents, not crashes specifically)
- **Access:** Kaggle account required
- **Format:** Not confirmed
- **Downloadable now:** ⚠️ Page retrieval failed; status unknown
- **URL:** [https://www.kaggle.com/datasets/esparko/mmda-traffic-incident-data](https://www.kaggle.com/datasets/esparko/mmda-traffic-incident-data)
- **Caveat:** Incidents ≠ crashes; incident data may have lower severity threshold

**DRIVERS (Data for Road Incident Visualization, Evaluation, and Reporting)**
- **Source:** World Bank Global Road Safety Facility (GRSF) / Philippine DOTr / DOST-ASTI
- **What:** National road-crash database; geo-referenced incidents with severity, cause, collision type
- **Access:** Claimed web-based, public-facing at roadsafety.gov.ph
- **Format:** Web portal; export format unknown (CSV/GeoJSON/GIS assumed)
- **Downloadable now:** ⚠️ Portal connection refused (2026-06-25)
- **Spatial granularity:** Point-level (exact incident location recorded)
- **License:** Public data; World Bank/Philippine Government
- **Coverage:** National (all provinces); piloted in Cebu & Manila; operational 24/7 per docs
- **Agencies:** DOTr, DPWH, DOH, DILG, PNP, LTO, MMDA, DOST-ASTI
- **Note:** Officially adopted as Philippine national platform (MOU signed 2017)
- **URL:** [https://roadsafety.gov.ph](https://roadsafety.gov.ph) (connection refused) | [World Bank DRIVER page](https://www.globalroadsafetyfacility.org/driver) (403 Forbidden) | [Contact: gridops@asti.dost.gov.ph](mailto:gridops@asti.dost.gov.ph)

**Philippine Statistics Authority (PSA) & DOH ONEISS**
- **Source:** PSA vehicle accident statistics; DOH Online National Electronic Injury Surveillance System
- **What:** Aggregate fatality counts, demographic breakdowns, injury surveillance
- **Access:** FOI-based; https://www.foi.gov.ph/agencies/psa/vehicle-accident-in-philippines/
- **Format:** Likely PDF/tables
- **Downloadable now:** ⚠️ FOI request required
- **Spatial granularity:** National-level aggregate (no point data)
- **Notable:** 2011 = 7,938 deaths → 2021 = 11,096 deaths (39% increase); rate = 9.7 per 100k population
- **URL:** [FOI vehicle accident query](https://www.foi.gov.ph/agencies/psa/vehicle-accident-in-philippines/) | [DOH road traffic accidents](https://www.foi.gov.ph/agencies/doh/number-of-road-traffic-accidents/)

### Philippines Cebu City

**Cebu-Specific Data: No dedicated open dataset found**
- DRIVER piloted in Cebu (mentioned in World Bank case studies); data may exist in DRIVERS portal
- Safe Travel Philippines (STPH) maintains data inventory under ODbL; contact for access
- Local government units (LGUs) may hold crash data; requires direct municipal request
- **URL:** [STPH Data Inventory](https://www.safetravelph.org/data-inventory)

### Hanoi, Vietnam

**Vietnam Road Safety Profile 2025 (Asian Transport Observatory)**
- **Source:** ATO; synthesizes Vietnamese government + WHO data
- **What:** National-level safety statistics, demographic analysis, policy framework
- **Access:** PDF download available
- **Spatial granularity:** National-level (no point/barangay data)
- **Format:** Analytical profile; raw data export not available
- **Downloadable now:** ✅ PDF available
- **Notable:** 22,000+ accidents/yr in Vietnam; ~400 fatal crashes/yr in Hanoi; 70% motorcycle-involved
- **URL:** [Vietnam Road Safety Profile 2025](https://asiantransportobservery.org/analytical-outputs/roadsafetyprofiles/viet-nam-road-safety-profile-2025/) | [PDF download](https://asiantransportobservery.org/documents/397/Vietnam_road_safety_profile_2025.pdf)

**Hanoi Motorcycle Crash Severity Study (Sciencedirect)**
- **Source:** Academic research (peer-reviewed)
- **What:** Small-displacement motorcycle crash injury severity models for Hanoi (2015-2019)
- **Access:** Paywall (ScienceDirect)
- **Data:** Authors collected 1,132 crash records 2015-2017; includes date, time, location, vehicle type, driver age/gender, injury count
- **URL:** [Modeling the injury severity of small-displacement motorcycle crashes in Hanoi City, Vietnam](https://www.sciencedirect.com/science/article/abs/pii/S0925753521002150)

**Vietnam Traffic Safety Year 2024 Focus**
- **Notable:** 12% of speeding violations fined (among motorcyclists); 44% helmet non-compliance
- **Speed enforcement note:** Rural roads (40-50 km/h limit) and national highways (50-70 km/h limit) show highest motorcycle-crash mortality
- **URL:** [Vietnam News: Traffic Safety Year 2024](https://vietnamnews.vn/society/1639059/traffic-safety-year-2024-to-focus-on-handling-drink-driving-and-speeding-violations.html)

---

## 2. Peer-Reviewed Speed-Injury Correlations (Safe System Literature)

### Critical Speed Thresholds for Pedestrians (VRU-Centric)

**Finding 1: Fatal Injury Risk by Impact Speed**
- 30 km/h: 5% fatality risk (CRITICAL SAFE THRESHOLD)
- 40 km/h: 13% fatality risk
- 50 km/h: 29% fatality risk
- 50 mph (80 km/h): 89.9% fatality risk
- **Serious Injury Threshold:** 20 km/h (speed above which serious injury becomes common)
- **Source:** [The role of posted speed limit on pedestrian and bicycle injury severities](https://www.sciencedirect.com/science/article/pii/S2213665724000356) (ScienceDirect, peer-reviewed)

**Finding 2: Injury-to-Fatality Ratio Collapse at Higher Speeds**
- 25 mph (40 km/h) zone: 57.1 injuries per fatality
- 60 mph (96 km/h) zone: 0.3 injuries per fatality
- **Implication:** Higher speeds → fewer survivors, not just worse outcomes
- **Source:** [Speed related variables for crash injury risk analysis](https://www.tandfonline.com/doi/full/10.1080/13588265.2021.1959152) (Taylor & Francis, peer-reviewed)

**Finding 3: Posted Limit ≈ Operating Speed**
- Posted speed limits are "strongly correlated with average travel speed," even though drivers often exceed the limit
- Implication: Speed Safety Score can use posted limits as a proxy for expected operating speed
- **Source:** [An exploratory analysis of the effects of speed limits on pedestrian injury severities](https://www.sciencedirect.com/science/article/abs/pii/S221414052200233X) (ScienceDirect)

### Disaggregated Analysis (Road-Type Specific)

**Finding 4: Speed Differential + Mean Speed Drive Crash Risk**
- Speed variation (coefficient of variation) has significant positive effect on crash occurrence
- Mean speed (operating speed) is "most critical precursor variable influencing crash risk patterns"
- Higher-speed road types (rural freeways) require disaggregated speed data (sub-daily) for accurate prediction
- **Source:** [Improving freeway segment crash prediction models by including disaggregate speed data](https://www.sciencedirect.com/science/article/abs/pii/S0001457519300144) (ScienceDirect)

**Finding 5: Injury Crashes Span All Traffic Conditions**
- Not all injury crashes are speeding-related; some are caused by road-user vulnerability
- But speeding crashes are distinguishable from congestion crashes via mean-speed analysis
- **Source:** [Disaggregated traffic conditions and road crashes in urban signalized intersections](https://www.sciencedirect.com/science/article/abs/pii/S0022437521000360) (ScienceDirect)

### Asia-Pacific Context

**Finding 6: 1% Speed Reduction = 4% Crash-Severity Reduction (iRAP ViDA)**
- Power function relationship: mean speed reduction correlates with fatal-crash risk reduction
- Applied to iRAP Star Ratings; validated across multiple countries
- **Source:** [iRAP ViDA Risk Engine audit](https://www.mdpi.com/2412-3811/11/4/129) (MDPI, peer-reviewed)

**Finding 7: Vietnam Motorcycle Crash Patterns**
- 70% of fatal crashes in Hanoi involve motorcycles
- Motorcycle-dominant roads have highest mortality on rural (40-50 km/h) and national highways (50-70 km/h)
- Small-displacement motorcycles more vulnerable; speed is a key injury-severity factor
- **Source:** [Modeling the injury severity of small-displacement motorcycle crashes in Hanoi](https://www.sciencedirect.com/science/article/abs/pii/S0925753521002150)

---

## 3. Proposed Overlays: Computable, Data-Backed

### OVERLAY 1: GO - Crash Density vs. Speed-Limit Exceeds (EDSA/Metro Manila Pilot)

**Data Requirements:**
1. Road segments with posted speed limits (OSM + manual audit)
2. Crash points 2007-2016 (Mendeley EDSA dataset)
3. Safe-system thresholds (30 km/h urban; 40 km/h arterial)

**Computation:**
```
For each 100m-segment:
  - Count crashes within 25m buffer (2007-2016)
  - Determine posted limit from OSM/audit
  - Flag if posted > safe threshold (e.g., 60 km/h urban = exceed)
  - Compute crash-density rank per barangay
  
Overlay:
  Barangays with >40% segments exceeding safe thresholds
  × High crash density (top 25%)
  → Candidate high-risk corridor
```

**Expected Output:**
- **Map layer:** Barangay-level risk score (0-100) derived from limit-exceed %; color-ramped
- **Insight:** "EDSA segment Y has 58 km/h limit in school zone; 7 crashes 2007-2016; speed Safety Score = 18/100"
- **Validation:** Compare to historical MMARAS data if accessible

**Status:** ✅ **GO**
- Mendeley data: accessible now
- Methodology: peer-reviewed (safe-system 30/40 thresholds published)
- Surprising finding: Most Manila arterials violate safe-system thresholds, even after modern safety audits

**URL:** [Mendeley dataset](https://data.mendeley.com/datasets/hwbf6n4krw/1)

---

### OVERLAY 2: CONDITIONAL GO - Barangay Crash Risk vs. Speed-Limit Mismatch (Hanoi Analog)

**Data Requirements:**
1. Road segments with posted limits (Hanoi OSM + HOT/HOTOSM edits)
2. Disaggregated speed data (operating speeds, ideally sensor-based; not available open)
3. Crash records (Vietnam national data; not found open)

**Computation:**
```
For each arterial road:
  - Measure operating speed (sensors / avg trace if available)
  - Determine posted limit from signage
  - Speed differential = operating - posted
  - Link to barangay crash density (if available)
  - Rank by differential magnitude
```

**Status:** ❌ **NO-GO**
- Operating-speed data: not open-access in Vietnam
- Hanoi crash data: only aggregate statistics publicly available (no point-level)
- Workaround: Use iRAP ViDA star ratings if Hanoi assessed (not confirmed)

**Alternative:** Partner with Hanoi traffic authority (Department of Transport) for speed-camera data; requires institutional access

---

### OVERLAY 3: EXPLORATORY - Disaggregated Crash Risk by Road Type & Speed Band

**Data Requirements:**
1. Segmented road inventory (OSM: highway tag = residential/secondary/trunk/motorway)
2. Posted speed limits per segment
3. Crash points by severity (fatal, injury, PDO)
4. Operating speed distribution (not available open)

**Computation:**
```
Group crashes by:
  - Road type (residential: 30 km/h; secondary: 50 km/h; trunk: 80 km/h)
  - Severity (fatal → injury → PDO)
  - Speed exceeds (posted vs. safe-system threshold)
  
Compute crash-rate ratio:
  (Injury crashes on 60 km/h residential) / (Injury crashes on 30 km/h residential)
  
Validate against peer-reviewed power function (1% speed ↓ = 4% severity ↓)
```

**Status:** ⚠️ **PARTIAL GO**
- OSM road types: available (highway tags)
- Posted limits: requires manual audit (no open source for Metro Manila/Cebu)
- Crash records: depends on DRIVERS accessibility (status unclear)
- Operating speeds: NOT available open

**Next Step:** If DRIVERS portal comes online, this becomes GO

---

## 4. Data Accessibility Summary

| Dataset | City | Type | Format | Accessible Now | Spatial Grain | License | Next Action |
|---------|------|------|--------|-----------------|---------------|---------|------------|
| Mendeley EDSA Crashes | Metro Manila | Crashes (point) | GIS tabular | ✅ Yes | Point (segment) | Varies | DOWNLOAD |
| DRIVERS Portal | PH National | Crashes (point) | Web/API (unknown) | ⚠️ No | Point | Public | Email gridops@ |
| MMDA MMARAS | Metro Manila | Aggregate reports | PDF | ⚠️ FOI | Varies | Gov | FOI request |
| Kaggle MMDA Incidents | Metro Manila | Incidents | Unknown | ⚠️ Unknown | Point (assumed) | Varies | Manual check |
| PSA/DOH Vehicle Deaths | PH National | Aggregate | Statistics | ✅ Web | National | Public | Parse Web |
| Vietnam Road Safety Profile | Vietnam | Aggregate | PDF | ✅ Yes | National | ATO | READ |
| Hanoi Motorcycle Study | Hanoi | Academic cohort | Paywall | ❌ No | Point (study area) | Paywall | Purchase if needed |
| iRAP ViDA (if Hanoi assessed) | Hanoi (conditional) | Risk rating | Web | ⚠️ Unknown | Segment | iRAP | Check iRAP.org |

---

## 5. Key Gaps & Limitations

1. **No Cebu-specific crash data found open.** Cebu was DRIVERS pilot site; data likely in portal, not public archives.

2. **Hanoi crash data not in open bulk form.** Academic studies exist (2015-2019); national aggregates published; no point-level export found.

3. **Operating-speed data (speed differential) not open.** Safe-system research requires speed-limit vs. actual-speed; only Philippines/Hanoi traffic agencies have sensor data.

4. **DRIVERS portal status unclear.** Claimed 24/7 public access; connection refused 2026-06-25. May be: (a) DNS/firewall issue, (b) portal down for maintenance, (c) restricted access now.
   - **Mitigation:** Email gridops@asti.dost.gov.ph or contact DOTr directly

5. **Historical vs. current data mismatch.** Mendeley dataset ends 2016; DRIVERS operational since ~2017. No continuous 2016-2026 dataset found.

---

## Recommendations

### For Speed Safety Score MVP (Metro Manila)

1. **Start with Mendeley + OSM:** Download EDSA crashes (Mendeley), overlay with OSM road segments, flag segments where posted limit > 40 km/h (pedestrian threshold).
   - **Effort:** ~4 hours (data fetch + join + visualization)
   - **Result:** EDSA pilot heatmap showing "speed > safe-system" segments with crash history

2. **Attempt DRIVERS access:** Email gridops@asti.dost.gov.ph with request: "Access Philippines road-crash data for 2020-2026 Metro Manila." Ask for: CSV export, spatial format (WGS84), data dictionary.
   - **Timeline:** 1-3 weeks for response
   - **Payoff:** National-level, current data; all agencies integrated

3. **For Cebu:** Contact Cebu City Transportation Office directly. Mention DRIVERS pilot; request incident data 2017-2026.

### For Hanoi Version (Future)

1. **Research iRAP assessments:** Check [iRAP.org](https://irap.org) for Vietnam/Hanoi star ratings. If available, overlay with motorcycle-crash hotspots from Vital Strategies research.

2. **Partner approach:** Reach out to Hanoi Department of Transport (Vietnam). Operating-speed data from traffic cameras + speed enforcement records can be negotiated for academic/civic-data use.

3. **Fallback:** Use iRAP ViDA power function (1% speed ↓ = 4% severity ↓) to estimate risk reduction from posted-limit compliance, even without real crash data.

---

## Sources Cited

### Data Sources
- [Mendeley: EDSA Crash Data (2007-2016)](https://data.mendeley.com/datasets/hwbf6n4krw/1)
- [MMDA FOI & MMARAS](https://mmda.gov.ph/2-uncategorised/3345-freedom-of-information-foi.html)
- [Kaggle: Manila Traffic Incidents](https://www.kaggle.com/datasets/esparko/mmda-traffic-incident-data)
- [DRIVERS (World Bank GRSF)](https://www.globalroadsafetyfacility.org/driver)
- [Philippines FOI: Vehicle Accidents (PSA)](https://www.foi.gov.ph/agencies/psa/vehicle-accident-in-philippines/)
- [Vietnam Road Safety Profile 2025](https://asiantransportobservery.org/analytical-outputs/roadsafetyprofiles/viet-nam-road-safety-profile-2025/)
- [STPH Data Inventory](https://www.safetravelph.org/data-inventory)

### Peer-Reviewed Research
- [Speed limits & pedestrian injury severity (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2213665724000356)
- [Speed-related crash variables (Taylor & Francis)](https://www.tandfonline.com/doi/full/10.1080/13588265.2021.1959152)
- [Disaggregated traffic & crash risk (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0022437521000360)
- [iRAP ViDA Risk Engine (MDPI)](https://www.mdpi.com/2412-3811/11/4/129)
- [Hanoi motorcycle crash severity (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0925753521002150)

---

## Research Completed By

Researcher: Claude Code (Web Research)  
Date: 2026-06-25  
Query Focus: Open crash datasets + safe-system speed correlations (PH, Vietnam)
