# Prior Art & Methodology Landscape: Speed Limit Appropriateness Assessment for Safe System Implementation

**Project:** ADB "AI for Safer Roads" Innovation Challenge  
**Research Date:** June 2026 (refreshed 2026-07-04)  
**Focus:** Speed limit appropriateness mapping, Safe System speed thresholds, existing tools and APAC context

---

## 2026-07 refresh (what changed since June)

Verified live this session. Detailed backing: `research/phase1/agent1-satellite-methods.md`,
`agent2-landscape-2026.md`, `agent3-ph-crash-data.md`, `agent4-ph-infra-signs.md`.

**The differentiator still holds.** As of July 2026 there is still no open, OSM-based,
network-scale posted-limit-vs-Safe-System-gap map. iRAP remains the closest boundary case
(Safe System based, has covered PH highways, ViDA is semi-public) but it runs on surveyed, not
OSM, data, scores a composite Star Rating rather than an explicit gap, its PH coverage is a
one-time 2011-2012 national-highway assessment, and access is gated. New commercial entrants
(SpeedMap Global, safer-roads.org, Derq) are posted-limit-only or crash-based and none cover PH.

**ADB Challenge status:** submissions closed 25 June 2026, now in expert review, shortlist due
September, jury October. Winning solutions will run on ADB's proprietary GIS platform, not open
OSM data. The highways.today (26 May 2026) "Rethinking Speed Limits with AI" piece, co-authored
by ADB and Agilysis, is the launch explainer for this exact thesis, not evidence of a shipped
open tool. Correction to the seed list: the ITF/OECD "AI in Proactive Road Infrastructure Safety
Management" report is from **December 2021**, not 2026, and carries no speed-gap content.

**Satellite crash-risk models do not port to the Philippines.** The 2024-2026 papers that
predict fatal-crash risk from satellite tiles alone (Liang et al. IEEE JSTARS 2024; Elallaf et
al. arXiv 2511.04886, AAAI 2026; Najjar et al. AAAI 2017) all need sub-metre imagery (0.3-1.2
m/px) and a geocoded crash-label training set. Sentinel-2 at ~10 m is roughly 30x too coarse and
the Philippines has no open geocoded crash corpus to train or transfer from. So a "satellite risk
vs our score" disagreement layer is not reproducible with open PH data, and we do not claim it.

**What IS buildable from open data (the honest satellite hook):** built-environment features.
Jiao et al. (arXiv 2505.06762) show POI density, building footprints, land use and intersection
density predict crash severity with zero satellite-crash labels. Google Open Buildings v3 and
Microsoft's PH building footprints (88.6M polygons, no auth) give a nationwide building/roof
density feature; WorldPop gives residential density (now folded into our exposure weight). The
"fast road through the densest housing" finding is exactly this: visible on satellite, computed
from open data, no proprietary imagery or crash labels required.

**Finer-than-region PH crash/death data: still none downloadable.** DRIVER (roadsafety.gov.ph)
is offline; LTO has no open portal; MMARAS is PDF-only; DPWH TARAS was discontinued in 2013; DOH
ONEISS is national-aggregate PDF. PSA holds province-level road-death rows (its 2023 press
release ranks provinces, Pangasinan highest) but exposes no downloadable province table; every
PSA domain 403'd to automated fetch this session. PSA region level (17) remains the finest open
cut. DPWH AADT is still PDF-atlas-only behind a WAF. Region-of-residence PSA death rates plus the
2018-2020 MMDA Metro-Manila crash points remain the best open validation data, unchanged.

---

## 1. iRAP (International Road Assessment Programme) Star Rating + Speed Model

### Overview
The International Road Assessment Programme (iRAP) is a proven methodology used in more than 140 countries to assess how much safety is "built in" to road design for all users (vehicle occupants, motorcyclists, pedestrians, cyclists). iRAP grades roads 1-5 stars, where 5-star is safest and 1-star is highest risk.

### Speed Integration (v3.10 Update, May 2026)
**Key Finding:** iRAP's latest **Star Rating Model v3.10** incorporates operating speed directly into infrastructure risk assessment. The model now:
- Produces Star Ratings based on **operating speeds alone** (50th and 85th percentile)
- Implements 1 km/h speed increments and 1,000 vehicle-per-lane flow increments
- Recognizes that **operating speeds have a significant bearing** on Star Ratings
- Uses the **larger of posted speed limit OR operating speed** (85th percentile) as the determinant

**Practical Application:** In Brunei, initial assessments showed that urban roads rated 3-star for vehicle occupants would markedly improve to 4-5 star **if observed operating speeds could be reduced**, demonstrating that speed management alone can improve safety ratings without infrastructure overhaul.

### Star Rating for Designs (SR4D)
The **Star Rating Demonstrator** within ViDA (iRAP's software platform) enables rapid testing of design alternatives:
- Quick production of Star Ratings at individual locations
- Test effect of road attribute changes on risk and ratings
- Operate at: **demonstrator.vida.irap.org**

### API & Integration
- **ViDA API** enables integration with road authority systems and asset management tools
- **GitHub SDK:** `iRAP-software/package-vida-api-sdk` (still in development)
- **API Access:** Contact support@irap.org to request permissions for data transfer and Star Rating retrieval

**Source:** [iRAP v3.10 Update](https://irap.org/irap-launches-updated-star-rating-model-version-3-10-advancing-global-road-safety/), [iRAP Methodology](https://irap.org/methodology/), [iRAP Tools](https://irap.org/tools/), [ViDA Star Rating Demonstrator](https://irap.org/rap-tools/enabling-software/star-rating-demonstrator/), [Brunei Case Study](https://journalofroadsafety.org/article/161219-enhancing-irap-star-ratings-in-brunei/)

---

## 2. USLIMITS2 (US FHWA Expert System Tool)

### Purpose
Web-based tool for setting reasonable, safe, consistent speed limits on all facility types (rural local roads, residential streets, urban freeways). Applicable across North America but demonstrates methodology replicable globally.

### Input Factors
The tool considers:
- **Operating speeds** (50th and 85th percentile)
- Annual average daily traffic (AADT)
- Roadway characteristics and geometric conditions
- Level of development / land use context
- Crash and injury rates
- On-street parking presence
- Pedestrian/bicycle activity extent
- Road type (local, collector, arterial, highway)

### Method
1. Users input observed 50th and 85th percentile speeds + road characteristics
2. Tool recommends speed limit value
3. Outputs list of issues for further investigation
4. **Critical:** 85th percentile is considered "best indicator of reasonable and safe speed" but is now **being deprioritized** in favor of Safe System thresholds

### Limitation in Safe System Context
USLIMITS2 marks a **transition point** in US guidance: the tool allows speeds down to the **50th percentile in certain cases**, departing from the strict 85th percentile rule. This reflects growing recognition that Safe System principles require context-appropriate speeds, not driver-behavior-dictated speeds.

**Source:** [USLIMITS2 Tool](https://highways.dot.gov/safety/speed-management/uslimits2), [FHWA Speed Limit Setting Handbook](https://highways.dot.gov/sites/fhwa.dot.gov/files/Speed-Limit-Setting-Handbook.pdf), [Georgia Case Study](https://highways.dot.gov/safety/speed-management/georgia-department-transportation-setting-speed-limits-help-uslimits2)

---

## 3. Safe System Critique of 85th Percentile & Survivable Speed Thresholds

### The Problem with 85th Percentile Rule
**Critique (FHWA, Smart Growth America, FHWA Safe System Approach for Speed Management):**
- **Does not account for** crash experience, road characteristics, context, presence of pedestrians/cyclists
- **Causes speed creep** when applied repeatedly; roads gradually become faster
- **Inappropriate for urban environments** where roads serve mixed users (pedestrians, cyclists, transit)
- **Ignores Safe System holism** — speed cannot be determined in isolation from road design, vehicle design, and road users
- **Perverse outcome:** A straight, wide road without traffic-calming invites speeding but receives higher limits under 85th percentile logic

### Self-Explaining Roads Concept
Roads should communicate appropriate speeds **through design**, not enforcement alone:
- Straight wide lanes → drivers speed (design failure)
- Complete Streets with traffic-calming, narrowed lanes, pedestrian refuges → drivers self-regulate (design success)
- Safe speeds supported by design = sustainable behavior change

**Source:** [FHWA Safe System Approach](https://highways.dot.gov/sites/fhwa.dot.gov/files/Safe_System_Approach_for_Speed_Management.pdf), [Our Streets MN on 85th Percentile Critique](https://www.ourstreetsmn.org/2024/07/25/how-the-85th-percentile-rule-is-ineffective-and-dangerous/), [SSTI Analysis](https://ssti.us/2020/01/27/setting-speed-limits-based-on-safety-not-driver-behavior-2/)

---

## 4. Safe System Survivable Speed Thresholds (Primary Source Evidence)

### Canonical Speed Limits by Road Context
**WHO Speed Management Manual & Global Road Safety Facility (GRSF) Guide for Safe Speeds:**

| Road Context | Safe Speed Limit | Rationale | Source |
|---|---|---|---|
| **Pedestrian activity zones** (urban mixed-use, intersections, schools, markets) | ≤30 km/h | Pedestrian fatality risk = 80% at 50 km/h; drops to ~10% at 30 km/h impact speed. Based on Ashton & Mackay (1979) and EuroNCAP crash test standards. | WHO 2004, GRSF 2024, iRAP |
| **Roads with side-on crash risk** (intersections between cars, mid-block crossing) | ≤50 km/h | EuroNCAP side-impact standard; 50 km/h (30 mph) is Safe System threshold for survivable side crashes | WHO, GRSF 2024 |
| **Roads with head-on crash risk** (undivided roads, passing zones) | ≤70 km/h | Designed to prevent fatal frontal crashes; requires median separation or no opposing traffic | WHO, GRSF 2024 |
| **High-speed separated facilities** (grade-separated highways, motorways) | >70 km/h | Only safe with infrastructure separating crash types (medians, barriers, grade separation); no pedestrians/cyclists | WHO, GRSF 2024 |

### Speed-Crash Risk Elasticity (ITF/OECD 2018)
**Disproportional relationship between speed and crash severity:**
- **1% increase in average speed** → 2% increase in injury crash frequency
- **1% increase in average speed** → 3% increase in severe crash frequency  
- **1% increase in average speed** → 4% increase in fatal crash frequency
- **Speed contributes to >30% of all fatal crashes globally**

This nonlinear relationship is the scientific foundation for why Safe System speeds (30/50/70) are non-negotiable thresholds, not guidelines.

**Source:** [WHO Speed Management Manual 2013](https://cdn.who.int/media/docs/default-source/documents/health-topics/road-traffic-injuries/3146-wbk-speed-mgmt-2nd-edition-131023-electronic.pdf), [ITF/OECD Speed and Crash Risk 2018](https://www.itf-oecd.org/speed-crash-risk), [GRSF Guide for Safe Speeds 2024](https://www.globalroadsafetyfacility.org/publications/guide-safe-speeds-managing-traffic-speeds-save-lives-and-improve-livability), [ETSC Fact Sheet](https://archive.etsc.eu/documents/Speed%20Fact%20Sheet%207.pdf)

### Vision Zero / Tingvall-Haworth (1999)
Established the ethical basis for prioritizing safety above all else. The 30 km/h pedestrian threshold derives from this work and crash test standards (Ashton & Mackay 1979 established the original 30 km/h survival threshold; later studies found 40-50 km/h for some scenarios, but 30 km/h is the global consensus for high-pedestrian environments).

**Source:** [FHWA Safe System Approach for Speed Management](https://highways.dot.gov/sites/fhwa.dot.gov/files/Safe_System_Approach_for_Speed_Management.pdf), [ResearchGate Vehicle Impact Speed Research](https://www.researchgate.net/publication/301293925_Exploration_of_Vehicle_Impact_Speed_-_Injury_Severity_Relationships_for_Application_in_Safer_Road_Design)

---

## 5. Existing Tools & Projects for Speed Limit Appropriateness Mapping

### **Global Initiatives (No Equivalent ADB/World Bank Full Solution Found)**

#### World Bank Global Road Safety Facility (GRSF) - "Guide for Safe Speeds" Framework
**Status:** NEW (March 2024)  
**What it provides:**
- "Roads-for-Life" framework for determining safe speeds in low/middle-income country contexts
- Evidence-based interventions: infrastructure, enforcement, education, vehicle technology
- City-wide 30 km/h speed limit guidance
- Examines risks in: inner cities, city outskirts, towns, villages, non-built-up areas, workzones
- **Does NOT provide:** automated mapping tool or API; is a guidance manual for manual implementation

**Deployment:** Used for speed management webinars across Latin America and Caribbean. Supporting ~$315M in World Bank financing (FY24) dedicated to road safety projects.

**Source:** [GRSF Guide for Safe Speeds](https://www.globalroadsafetyfacility.org/publications/guide-safe-speeds-managing-traffic-speeds-save-lives-and-improve-livability), [World Bank Road Safety Unit 2024](https://www.globalroadsafetyfacility.org/news/new-dedicated-unit-and-initiatives-world-bank-mark-major-advancement-global-road-safety)

#### CAREC Road Safety Engineering Manual 7: "Why and How to Manage Speed"
**Status:** Published by ADB/CAREC (Central Asia Regional Economic Cooperation)  
**Scope:** Central Asian focus but broadly applicable  
**Key Finding:** Reducing travel speeds by 10 km/h would **halve crash deaths** in CAREC countries  
**Content:** Safe System principles for speed management, not automated tools

**Source:** [ADB/CAREC Manual 7](https://www.adb.org/publications/carec-road-safety-engineering-manage-speed), [CAREC Program](https://carecprogram.org/?publication=carec-road-safety-engineering-manual-7-why-and-how-to-manage-speed)

#### iRAP Road Safety Toolkit
**What it provides:**
- Consolidated resource on speed management and traffic calming
- Part of collaboration between iRAP, gTKP (Global Transport Knowledge Partnership), World Bank GRSF
- Guidance, not automated network analysis

**Source:** [Road Safety Toolkit](https://toolkit.irap.org/), [Road Safety Data Portal](https://toolkit.irap.org/management/road-safety-data/)

---

### **Regional Initiatives**

#### Philippines: OpenTraffic + DRIVER System (World Bank + Grab + DOTC)
**Status:** OPERATIONAL (launched ~2016)  
**Components:**
1. **OpenTraffic** — Translates anonymized Grab driver GPS data into traffic statistics (speeds, flows, intersection delays)
2. **DRIVER** (Data for Road Incident Visualization, Evaluation, and Reporting) — Identifies crash blackspots; prioritizes interventions; improves emergency response
3. **Speed Management UN Road Safety Fund Project** (completed 2020) — Trained 170+ speed enforcers; engaged 75k+ people via social media on appropriate speeds

**What it does NOT do:** Assess speed limit appropriateness per se; focuses on observed speeds and crash hotspots, not Safe System speed threshold validation.

**Source:** [World Bank Philippines OpenTraffic](https://www.worldbank.org/en/news/press-release/2016/04/05/philippines-real-time-data-can-improve-traffic-management-in-major-cities), [UN Road Safety Fund Philippines Project](https://roadsafetyfund.un.org/projects/strengthening-speed-management-philippines), [World Bank Open Traffic Initiative](https://thedocs.worldbank.org/en/doc/513661445369530688-0190022015/original/OpenTrafficCompletionReport1.pdf)

#### Rio de Janeiro Speed Limit Digitization (World Bank GRSF + Mapillary)
**Status:** COMPLETED  
**Method:**
- Street-level imagery collection over 3,300 km of roads
- Mapillary object detection for traffic sign inventory: **53,389 traffic signs catalogued**
- Built comprehensive spatial database of posted speed limits
- Achieves 98% detection rate with Mapillary's 1,500 traffic-sign-class classifier

**Key Insight:** This is **data collection**, not appropriateness assessment. Inventory ≠ validation.

**Source:** [World Bank Blog on Intelligent Speed Assistance](https://blogs.worldbank.org/en/transport/intelligent-speed-assistance0), [Mapillary Traffic Sign Detection](https://blog.mapillary.com/update/2018/06/15/global-sign.html), [Mapillary Dataset ECCV 2020](https://research.mapillary.com/publication/eccv20d)

#### Mapillary Traffic Sign Detection (Global)
**Capability:**
- 105K annotated street-level images, 400+ traffic sign classes
- 1,500 sign classes across 100+ countries
- 98% detection rate for speed limit signs
- City implementations: Clovis (CA) uses Mapillary for sign inventory and maintenance tracking

**Limitation:** Detects **posted** signs, not appropriateness; cannot assess if a 60 km/h limit is Safe System-aligned.

**Source:** [Mapillary Traffic Sign Dataset](https://arxiv.org/pdf/1909.04422), [Mapillary Blog on Clovis Implementation](https://blog.mapillary.com/update/2018/11/14/streamlining-traffic-sign-inventory-in-clovis.html)

---

### **Open Data & Research Tools (Not Turn-Key)**

#### Speed Limit Extraction from OSM + GPS Probe Data
**Research Finding:** Academic work demonstrates feasibility of combining:
- **OSM speed limit tags** (coverage ~13-15% in North America; lower in developing regions)
- **GPS probe data** (80th percentile free-flow speed from anonymized traces)
- **Validation:** If speed limit / mean observed speed ratio is consistent, infer alignment

**Limitation:** OSM coverage is sparse in Philippines and APAC; manual data entry required for comprehensive inventory.

**Source:** [Road Speed Limit Extraction via GPS & OSM](https://www.researchgate.net/publication/287194946_Road_Speed_Limit_Extraction_and_Vehicle_Speed_Recording_Using_GPS_and_Open_Street_Map), [OSM Philippines Wiki](https://wiki.openstreetmap.org/wiki/Philippines/Mapping_conventions/Roads)

#### World Bank Open Data Initiative
**Provides:** Traffic data, infrastructure databases, but NOT speed-limit-appropriateness assessment. General toolkit for open data programs.

**Source:** [World Bank Open Data](https://data.worldbank.org/), [Open Government Data Toolkit](https://opendatatoolkit.worldbank.org/)

---

### **Conclusion: Novelty Assessment**
**No existing tool directly addresses speed limit appropriateness mapping** (comparing posted speeds against Safe System thresholds and road context) **at network scale in APAC.**
- iRAP Star Rating integrates speed but focuses on overall infrastructure risk, not specifically "is this speed limit appropriate?"
- GRSF Guide provides framework but requires manual implementation per city
- DRIVER/OpenTraffic systems focus on observed-speed hotspots, not Safe System validation
- Mapillary detects posted signs but cannot assess appropriateness
- **Opportunity:** Combining iRAP Star Rating data + Safe System thresholds + OSM + crash data + GPS probe speeds = novel network-scale speed appropriateness assessment

---

## 6. APAC Road Safety Context: Philippines Motorcycle Deaths

### Key Statistics

#### Global & Regional
- **58% of world's 1.3M road deaths occur in Asia-Pacific region**
- **Southeast Asia:** 20.7 deaths per 100,000 population (2nd highest after Africa at 26.6)
- **Motorcyclist share globally:** ~30% of all road deaths
- **Southeast Asia motorcyclist share:** **43-46% of all road deaths** (highest global concentration)

#### Philippines Specific (WHO Global Status Report on Road Safety 2023)
- **Total annual road deaths:** 11,096 (2021 PSA Report)
- **Trend:** +39% increase from 2011 (7,938) to 2021 (11,096) — **worsening trend**
- **Motorcyclist share:** **65% of all road crash victims** (Department of Health)
- **Vulnerable road users total:** >50% of all deaths (motorcyclists, pedestrians, cyclists)
- **Gender:** 84% of deaths are male (high motorcycle rider concentration)
- **Economic burden:** Road traffic injuries cost ~2.6% of GDP
- **Geographic spread:** Higher concentration in Metro Manila, but nationwide problem

#### Comparative APAC Context
- **Thailand:** Highest motorcyclist death rate globally; ~60% of all road deaths are motorcyclists
- **Malaysia:** ~60% of road deaths involve motorcycles
- **Cambodia:** >65% of deaths involve motorcyclists; 79.3 deaths per 100k motorcycles (highest SE Asia rate)
- **Regional pattern:** Powered two-wheelers (motorcycles, tricycles) are THE critical vulnerable user group

### Policy Implications for Speed Safety Score
**Majority of crash victims in Philippines are motorcyclists** — speed limit appropriateness must account for:
1. Motorcycle stability at different speeds (29-35 km/h optimal for control; >60 km/h = reduced reaction time)
2. Mixed-traffic zones where motorcycles compete with cars (30 km/h zones = motorcycle survivability zones)
3. Highway segments with high motorcycle volumes (require graduated speed management, not blanket limits)

**Source:** [WHO Global Status Report 2023 - Philippines Country Profile](https://www.who.int/publications/m/item/road-safety-phl-2023-country-profile), [WHO Philippines Press Release Dec 2023](https://www.who.int/philippines/news/detail/18-12-2023-dotr--who--road-safety-partners-launch-global-status-report-on-road-safety-2023-in-the-philippines), [Asian Transport Observatory - Philippines Road Safety 2025](https://asiantransportobservatory.org/analytical-outputs/roadsafetyprofiles/philippines-road-safety-profile-2025/), [Pulitzer Center SE Asia Motorcycle Deaths](https://pulitzercenter.org/stories/southeast-asia-death-rides-moto), [Wikipedia Traffic Death Rate](https://en.wikipedia.org/wiki/List_of_countries_by_traffic-related_death_rate)

---

## 7. Framework for Implementing Speed Safety Score (ADB Innovation Challenge)

### Methodological Foundation (Synthesized)

The Speed Safety Score should assess alignment between **posted speed limits** and **Safe System principles** using:

1. **Safe System Speed Thresholds** (WHO/GRSF/iRAP consensus):
   - 30 km/h: pedestrian-mixing zones (dense urban)
   - 50 km/h: intersection/side-crash risk zones
   - 70 km/h: limited conflict roads
   - Higher: only with separated infrastructure

2. **Road Context Inputs** (iRAP + USLIMITS2 pattern):
   - Road type (local, collector, arterial, highway)
   - Land use (urban, peri-urban, rural)
   - Presence of pedestrians/cyclists (density score)
   - Traffic composition (% motorcycles critical in PH)
   - Posted speed limit vs. observed 85th percentile speed
   - Crash history (fatal, serious, minor)
   - Infrastructure features (barriers, median, traffic-calming)

3. **Data Sources** (Open, APAC-available):
   - **OSM:** Road geometry, road class, speed tags (sparse in PH, requires validation)
   - **GPS Probe Data:** Observed speeds (Grab, local ride-hailing, volunteer data)
   - **Crash Data:** National Traffic Management Authority / PSA open datasets
   - **Satellite/Street Imagery:** Mapillary, Google Street View for land-use context
   - **Traffic Counts:** Municipal records or estimation from probe data

4. **Output: Speed Safety Score**
   - **Green (5 stars):** Posted limit = Safe System threshold for context; infrastructure supports it
   - **Yellow (3-4 stars):** Posted limit is 5-15 km/h above Safe System threshold; marginal compliance
   - **Red (1-2 stars):** Posted limit >15 km/h above Safe System threshold; high crash risk for context
   - **Flag:** Observed speed significantly ≠ posted speed (enforcement gap or inappropriate limit)

5. **Priority Segments**
   - Red + high motorcyclist share + high observed speed = urgent intervention
   - Yellow + school/market proximity = medium priority
   - Green + alignment = baseline

### Reference Implementation Touchpoints
- **iRAP ViDA API:** Request access to integrate Star Rating context
- **GRSF Roads-for-Life framework:** Template for context-appropriate speed assignment
- **CAREC Manual 7:** Technical justification for speed reduction impact (~10 km/h = ~50% death reduction)
- **OSM Philippines Mapping Conventions:** Use standardized speed tags
- **DRIVER System:** Leverage existing crash blackspot data

---

## Summary: Decision-Relevant Findings for ADB Innovation Challenge

1. **Safe System Survivable Speeds Are Non-Negotiable:**
   - 30 km/h where pedestrians mix with motors (pedestrian survival ~10% at 30 km/h vs. 80% at 50 km/h)
   - 50 km/h for side-crash risk; 70 km/h for head-on only
   - Scientifically grounded in crash test standards + epidemiology (Ashton & Mackay 1979, Tingvall & Haworth 1999, WHO 2004, ITF/OECD 2018)

2. **85th Percentile Rule Is Obsolete for Safe System:**
   - FHWA USLIMITS2 now permits 50th percentile in urban contexts
   - Safe System requires speed SET BY CONTEXT (road design, users, function), not DICTATED BY DRIVER BEHAVIOR
   - Speed creep + inappropriate urban speeds are documented failures of the old rule

3. **iRAP Star Rating v3.10 (May 2026) Integrates Operating Speed:**
   - ViDA API available for integration (contact support@irap.org)
   - Star Rating Demonstrator accessible at demonstrator.vida.irap.org
   - Methodology proven in 140+ countries; immediately replicable in PH context

4. **No Equivalent Network-Scale Speed Appropriateness Tool Exists:**
   - World Bank GRSF released "Guide for Safe Speeds" (Mar 2024) but is manual guidance, not automated tool
   - DRIVER system (PH) tracks observed speeds + crashes, but doesn't assess Safe System alignment
   - Mapillary detects posted signs (98% accuracy) but cannot validate appropriateness
   - **YOUR TOOL WILL BE NOVEL:** Combining iRAP + Safe System thresholds + crash data + GPS probe speeds + motorcyclist concentration = first network-scale speed appropriateness assessment for APAC

5. **Philippines Motorcycle Crisis Is Framing Device:**
   - **65% of PH road deaths are motorcyclists** (vs. 43-46% APAC average; 30% global)
   - Speed management has outsized impact on motorcycle safety (control degradation >60 km/h; survivability <30 km/h in mixed zones)
   - 11,096 annual deaths in 2021 (up 39% from 2011) — interventions validated by Speed Safety Score are high-leverage

6. **Data Availability in Philippines:**
   - OSM coverage: ~13-15% of roads have speed tags (low, requires validation)
   - GPS probe data: Grab + other ride-hailing available; can estimate observed speeds
   - Crash data: PSA + Department of Health + DOTC public datasets
   - Imagery: Mapillary + Google Street View sufficient for land-use context
   - **Recommendation:** Start with Metro Manila (highest concentration, best data density) and expand

---

## References (Complete URL List)

### iRAP & Star Rating
- [iRAP v3.10 Update (May 2026)](https://irap.org/irap-launches-updated-star-rating-model-version-3-10-advancing-global-road-safety/)
- [iRAP Methodology](https://irap.org/methodology/)
- [iRAP Tools](https://irap.org/tools/)
- [Star Rating for Designs](https://irap.org/rap-tools/enabling-software/star-rating-demonstrator/)
- [iRAP ViDA Software](https://irap.org/tools/vida-software-to-save-lives/)
- [iRAP ViDA API SDK](https://github.com/iRAP-software/package-vida-api-sdk)
- [Brunei Case Study](https://journalofroadsafety.org/article/161219-enhancing-irap-star-ratings-in-brunei/)
- [Road Safety Foundation SR4D](https://roadsafetyfoundation.org/irap-tools-and-methodology/star-rating-for-designs/)

### USLIMITS2 (FHWA)
- [USLIMITS2 Tool Home](https://highways.dot.gov/safety/speed-management/uslimits2)
- [FHWA Speed Limit Setting Handbook](https://highways.dot.gov/sites/fhwa.dot.gov/files/Speed-Limit-Setting-Handbook.pdf)
- [Georgia Case Study](https://highways.dot.gov/safety/speed-management/georgia-department-transportation-setting-speed-limits-help-uslimits2)
- [Speed Limit Basics](https://highways.dot.gov/safety/speed-management/speed-limit-basics)

### Safe System Speed & Critique
- [FHWA Safe System Approach for Speed Management](https://highways.dot.gov/sites/fhwa.dot.gov/files/Safe_System_Approach_for_Speed_Management.pdf)
- [Our Streets MN: 85th Percentile Rule Critique](https://www.ourstreetsmn.org/2024/07/25/how-the-85th-percentile-rule-is-ineffective-and-dangerous/)
- [SSTI Speed Limits Based on Safety](https://ssti.us/2020/01/27/setting-speed-limits-based-on-safety-not-driver-behavior-2/)
- [California Safe Speeds Toolkit](https://safetrec.berkeley.edu/tools/california-safe-speeds-toolkit/california-safe-speeds-toolkit-research-speeds-speed-limits-and)

### WHO Safe System Thresholds
- [WHO Speed Management Manual 2013](https://cdn.who.int/media/docs/default-source/documents/health-topics/road-traffic-injuries/3146-wbk-speed-mgmt-2nd-edition-131023-electronic.pdf)
- [ETSC Fact Sheet on Speed](https://archive.etsc.eu/documents/Speed%20Fact%20Sheet%207.pdf)
- [WHO Setting Speed Limits Guidance](https://www.who.int/docs/default-source/documents/health-topics/road-traffic-injuries/setting-speed-limits.pdf)

### ITF/OECD Speed and Crash Risk
- [ITF/OECD Speed and Crash Risk 2018](https://www.itf-oecd.org/speed-crash-risk)
- [ETSC OECD Speed Findings](https://etsc.eu/oecd-study-says-inappropriate-speed-responsible-up-to-30-of-all-fatal-crashes)
- [NRSO Summary](https://www.nrso.ntua.gr/itf-speed-and-crash-risk-2018/)

### World Bank / GRSF
- [GRSF Home](https://www.globalroadsafetyfacility.org/)
- [GRSF Guide for Safe Speeds 2024](https://www.globalroadsafetyfacility.org/publications/guide-safe-speeds-managing-traffic-speeds-save-lives-and-improve-livability)
- [GRSF News: Guide Launch](https://www.globalroadsafetyfacility.org/news/launch-guide-safe-speeds)
- [World Bank Road Safety Unit 2024](https://www.globalroadsafetyfacility.org/news/new-dedicated-unit-and-initiatives-world-bank-mark-major-advancement-global-road-safety)
- [World Bank OpenTraffic Initiative](https://thedocs.worldbank.org/en/doc/513661445369530688-0190022015/original/OpenTrafficCompletionReport1.pdf)
- [World Bank Blog: Intelligent Speed Assistance](https://blogs.worldbank.org/en/transport/intelligent-speed-assistance0)

### CAREC (ADB)
- [CAREC Manual 7: Why and How to Manage Speed](https://www.adb.org/publications/carec-road-safety-engineering-manage-speed)
- [CAREC Manual 5: Star Ratings](https://www.adb.org/sites/default/files/publication/814761/carec-rse-manual-5-star-ratings-road-safety-audit.pdf)
- [CAREC Program](https://carecprogram.org/?publication=carec-road-safety-engineering-manual-7-why-and-how-to-manage-speed)
- [Asia Pacific Road Safety Observatory](https://www.aprso.org/publications/carec-road-safety-engineering-manuals)

### Philippines Road Safety
- [WHO Global Status Report 2023 - Philippines](https://www.who.int/publications/m/item/road-safety-phl-2023-country-profile)
- [WHO Philippines Press Release Dec 2023](https://www.who.int/philippines/news/detail/18-12-2023-dotr--who--road-safety-partners-launch-global-status-report-on-road-safety-2023-in-the-philippines)
- [Asian Transport Observatory - PH Road Safety 2025](https://asiantransportobservatory.org/analytical-outputs/roadsafetyprofiles/philippines-road-safety-profile-2025/)
- [UN Road Safety Fund: Strengthening Speed Management PH](https://roadsafetyfund.un.org/projects/strengthening-speed-management-philippines)
- [Open Data Philippines - AADT](https://data.gov.ph/index/public/dataset/Annual%20Average%20Daily%20Traffic%20(AADT)/ua1r4ams-fav9-yyqw-kdww-kjbqxpiev6la)
- [OSM Philippines Mapping Conventions](https://wiki.openstreetmap.org/wiki/Philippines/Mapping_conventions/Roads)

### APAC Motorcycle Deaths
- [Pulitzer Center: Southeast Asia Death Rides a Moto](https://pulitzercenter.org/stories/southeast-asia-death-rides-moto)
- [Wikipedia: Traffic Death Rates by Country](https://en.wikipedia.org/wiki/List_of_countries_by_traffic-related_death_rate)
- [ResearchGate: Motorcycle Death Rates APAC](https://www.researchgate.net/figure/Motorcycle-crash-related-death-rate-per-100-000-population-and-100-000-registered_tbl1_260115974)

### Speed Limit Data & Tools
- [Road Speed Limit Extraction via GPS & OSM](https://www.researchgate.net/publication/287194946_Road_Speed_Limit_Extraction_and_Vehicle_Recording_Using_GPS_and_Open_Street_Map)
- [Mapillary Traffic Sign Dataset](https://arxiv.org/pdf/1909.04422)
- [Mapillary Sign Detection Blog](https://blog.mapillary.com/update/2018/06/15/global-sign.html)
- [Mapillary Clovis Implementation](https://blog.mapillary.com/update/2018/11/14/streamlining-traffic-sign-inventory-in-clovis.html)
- [Road Safety Toolkit](https://toolkit.irap.org/)

### ADB Philippines Projects
- [ADB Road Safety Action Plan Overview](https://www.adb.org/publications/road-safety-action-plan-overview)
- [ADB Road Improvement Project Philippines](https://www.adb.org/projects/41076-044/main)
- [ADB Transport Sector Assessment Philippines](https://www.adb.org/documents/philippines-transport-sector-assessment-strategy-and-road-map)

---

## Document History
- **Author:** Research Team, ADB "AI for Safer Roads" Innovation Challenge
- **Date:** June 2026
- **Classification:** Open Research
- **Next Steps:** Integrate findings into Speed Safety Score design specification and validation framework
