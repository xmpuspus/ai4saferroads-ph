# PH road-crash / road-death data finer than region: research findings

Date: 2026-07-03
Method: WebSearch + WebFetch probes against live URLs. All 403s below are as observed by the WebFetch tool this session (likely bot/user-agent blocking on Philippine government domains, all of which returned 403 identically) — not a claim that a human browser would also fail. Where a claim depends on an artifact I could not directly open, that is flagged explicitly.

---

## 1. DRIVER / roadsafety.gov.ph (World Bank GRSF road crash data system)

**Status: OFFLINE. Not accessible.**

- `https://roadsafety.gov.ph/` — `ECONNREFUSED` on port 443 (connection refused, not a timeout or DNS issue) on two separate probe attempts today (2026-07-03).
- Confirmed via web search: as of 2025-09-03, a civil-society group (SafeTravelPH / Mobility Innovations Organization) told a DOTr budget hearing that the official site is down and that only their own unofficial mirror demo (`nctscrtip-driver.safetravel.ph`) exists for demonstration purposes. [SafeTravelPH DOTr budget-hearing submission PDF](https://docs.congress.hrep.online/download/CSO/2Sep2025+-+SafeTravelPH+Queries+for+DOTr+Budget+Hearing.pdf)
- I attempted the mirror directly: `https://nctscrtip-driver.safetravel.ph/` — `ENOTFOUND` (DNS does not resolve). The mirror itself appears to be gone too, or was only ever a temporary demo link, not a standing public instance.
- `safetravel.ph` (the NGO's own site) is reported elsewhere as having its "reporting map unable to connect to the server" — so even the NGO's own tooling is broken.
- Even when DRIVER was live, secondary sourcing says usage was thin: for the whole of 2019 the system logged only 352 unique fatality records nationally — far below true crash volume — because participating LGUs/police entered data inconsistently.
- No public bulk export, API, or CSV/GeoJSON download was ever documented for DRIVER in any source found — access model historically was account-based dashboard login for registered agency/researcher users (per DOST-ASTI: "Users can access DRIVERS at roadsafety.gov.ph with login credentials," contact `gridops@asti.dost.gov.ph` for access requests), not open bulk download even when the site worked.
- Background/history: [DOST-ASTI article](https://asti.dost.gov.ph/communications/news-articles/saving-lives-through-data-and-research-drivers-and-the-coare-facility/), [GRSF DRIVER program page](https://www.globalroadsafetyfacility.org/driver), [World Bank DRIVER PDF](https://documents1.worldbank.org/curated/en/245151560919065747/pdf/Data-for-Road-Incident-Visualization-Evaluation-and-Reporting-Lowing-the-Barriers-to-Evidence-Based-Road-Safety-Management-in-Resource-Constrained-Countries.pdf), [PNA article on DOTr's crash database](https://www.pna.gov.ph/articles/1024471) (403 to WebFetch, title/snippet only via search).

**Conclusion: DRIVER is not a usable data source right now at any granularity.** It was designed to be the best possible option (nationwide, geo-referenced, multi-agency) but the platform itself is down and there was never a public bulk-download/API even at peak operation.

---

## 2. PSA province-level road/land-transport deaths

**Status: PARTIAL — data appears to exist at province granularity, but I could not open a machine-downloadable file this session (systematic 403s on all psa.gov.ph / openstat.psa.gov.ph / psada.psa.gov.ph domains).**

Two distinct PSA data lines matter here, and they are NOT the same:

### 2a. OpenSTAT SDG indicator table (the one initially found) — NOT province-level
- `https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__3I__G03/0123I3D0361.px/...` = "3.6.1 Death rate due to road traffic injuries per 100,000 population" — this is an SDG-monitoring indicator table. These PX-Web SDG tables are structured for national/regional reporting, not province breakdown. WebFetch returned 403; could not confirm dimension list directly, but the table's SDG framing plus its indicator code (3.6.1) makes province-level rows unlikely. **Do not treat this as the province-level source.**

### 2b. PSA Vital Statistics "deaths by cause" (civil registration, ICD-10 V01–V99 transport-accident codes) — genuinely appears to reach province level
- PSA's own 2023 land-transport-deaths special release (`https://psa.gov.ph/system/files/vsd/signed_Special%20PR_Land%20Transport_0.pdf`, 403 to WebFetch, content read only via search-engine snippets) explicitly names province-level rankings: Pangasinan had the highest land-transport-accident deaths every year 2010–2023 except 2012; Nueva Ecija and Batangas in the top 5; Cagayan, Isabela, Davao del Norte in the top 10; Camarines Sur in the top 10 throughout except 2012; Quezon City highest among highly-urbanized cities since 2020. This level of specificity means PSA's underlying dataset is tabulated by province/HUC, even though the press release itself is a PDF narrative, not a machine-readable file.
- The likely machine-readable home for this data is PSA's Vital Statistics Report (VSR) / OpenSTAT "Number of Registered Deaths by Causes of Death and Sex" table set (`https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__1A__VS__DE/?tablelist=true` — 403 to WebFetch this session) and/or PSADA microdata (`https://psada.psa.gov.ph/`). Per PSA's own documentation (found via search, not directly opened), the Vital Statistics Report "lists down causes of all deaths... and presents data by region, province or city," and PSA's Vital Statistics Division can be reached at `m.villaver@psa.gov.ph` for direct data requests.
- **I could not confirm this session which exact table/file exposes the province rows in a downloadable format (XLSX/CSV), nor open the OpenSTAT table tree to see dimension options, because every PSA-family domain returned 403 to automated fetch.** This needs manual browser verification (open `openstat.psa.gov.ph` in an actual browser, drill into DB__1A__VS__DE → causes of death → filter to V01-V99 transport-accident codes → check if "province" is an available breakout dimension, and try the Excel export button) or a direct email to PSA Vital Statistics.
- Years: civil-registration cause-of-death data 2010–2023 confirmed reported; 2025 causes-of-death listed as "provisional as of 2026-02-28," implying the series continues to be updated annually.
- Format if unlocked: PX-Web tables typically export to Excel/CSV natively (standard PX-Web feature) — if province is indeed a selectable dimension, this becomes a genuine machine-downloadable, finer-than-region dataset.
- Caveat on data type: this is a *death registration* count (civil registrar cause-of-death coding), not a *crash location* dataset — it tells you where road-death victims were registered/resided, which correlates with but is not identical to where crashes occurred. Good for province-level burden mapping; not useful for point-level crash siting.

**Conclusion for item 2: the best real lead in this whole investigation, but not yet verified as machine-downloadable. Flag as "exists, access unconfirmed" — do not present to stakeholders as already-in-hand.**

---

## 3. LTO crash/accident open data, and MMARAS

**LTO: Status NO.** No open crash/accident dataset or API found.
- `data.gov.ph` LTO agency page (`https://data.gov.ph/?q=agencies/land-transportation-office`) loaded but returned no visible dataset listings in the WebFetch render (empty/portal-shell only) — could not confirm any LTO dataset exists there. Needs manual browser check to rule out a client-side-rendered dataset list WebFetch didn't execute.
- LTO's public communications (`lto.gov.ph/news/...`) describe a 2026-era internal "comprehensive data analysis" initiative on road accidents/road rage, framed as an internal government exercise, not a public data release.
- No LTO-specific open-data portal, download page, or API documented anywhere found.

**MMARAS (MMDA): Status NO for raw data, YES (but low value) for aggregate reports.**
- MMARAS is Metro-Manila-only (same ceiling as the MMDA set you already have), 2005–present, classifies crashes as Fatal/Non-fatal/Property-damage.
- A 2024-era FOI request specifically asked for the "MMARAS excel database" — the request page itself (`https://www.foi.gov.ph/requests/metro-manila-accident-reporting-and-analysis-system-mmaras-excel-database/`) returned 403 to WebFetch so the exact agency reply text could not be quoted directly, but search-engine summaries of MMDA's FOI policy state MMDA provides annual PDF reports but explicitly **does not** release the raw Excel database, citing risk of "data misinterpretation." Annual reports (PDF, not machine-readable rows) are posted 2005–2024 on MMDA's FOI page (`https://mmda.gov.ph/2-uncategorised/3345-freedom-of-information-foi.html`).
- Net effect: MMARAS does not currently beat the MMDA CSV you already have — it's the same city, likely the same underlying source, and the raw table is explicitly withheld.

**DPWH TARAS: Status NO — discontinued.**
- Traffic Accident Recording and Analysis System (national-roads-only, PNP-fed) was **discontinued in 2013/2014** per DPWH's own statement — deemed unsustainable (logistics of training/retraining PNP officers at 1,500 stations) and low-confidence data quality; also only ever covered national roads, not local roads.
- A September 2024 FOI request references "updating/encoding of TARAS," suggesting some revival attempt, but no evidence of a public dataset or portal resulting from it.

---

## 4. DOH ONEISS road-injury data

**Status: NO machine-readable open data. PARTIAL for aggregate PDF factsheets.**
- `https://oneiss.doh.gov.ph/` returned 403 to WebFetch.
- ONEISS is a hospital-based injury surveillance system (37 DOH + 98 government + 167-375 private hospitals reporting depending on year), covering transport/vehicular-crash cases 2010–2019 in published analyses (296,760 admitted patients over that decade in one peer-reviewed analysis).
- Output is published as periodic PDF factsheets (e.g., `oneiss.doh.gov.ph/factsheets/Final_1Q_2021_factsheet.pdf`, and DOH's "ONEISS Factsheet Volume 15, Issue 2" at `doh.gov.ph/data-publications/...`) — narrative/summary tables, not row-level or geolocated microdata, and no granularity finer than national aggregate was found in any factsheet title or abstract.
- This is patient-outcome surveillance (injury severity, risk factors: alcohol, seatbelt, helmet, phone use), not a crash-location dataset — even if it were open, it wouldn't give province/city crash counts directly, only hospital catchment-level injury counts at best.
- No public bulk download, API, or dashboard found.

---

## 5. data.gov.ph, HDX, Kaggle, GitHub, academic repos — nationwide/multi-city geolocated

**data.gov.ph: Status NO.** Site-restricted search (`site:data.gov.ph road accident/crash/traffic`) surfaced only Clark International Airport aviation-incident datasets under the Transportation topic. No road-crash dataset found on the portal.

**HDX: Status NO for crash data, YES for road network only.** `data.humdata.org` (393 PH datasets from 61 orgs) has road *network* geometry (OSM exports, WFP main-roads shapefile) but no crash/incident dataset was found in search or the group page.

**Kaggle:**
- `Manila Traffic Incident Data` (`kaggle.com/datasets/esparko/mmda-traffic-incident-data`) — **Status YES, downloadable**, but this is MMDA ALERT Twitter-scrape data (traffic *incidents*, not verified crash records), Metro Manila only, starting 2018-08-20. Not an improvement over what you have — same city, weaker data (social-media-derived, not police report).
- `Global Road Accidents Dataset` found in search is generic/global, not PH-specific — not relevant.

**Mendeley Data — EDSA set you already have:**
- `https://data.mendeley.com/datasets/hwbf6n4krw/1` — **Status YES, downloadable now**, CC BY 4.0, tabular/GIS-compatible, 2007–2016, EDSA corridor only (Metro Manila). This is the dataset already cited as your current best — confirmed still live and downloadable, no change.

**GitHub / independent projects — none downloadable, all leads dead-end:**
- Medium article "Mapping Traffic Accidents in Metro Manila" (Miguell Malacad) — describes MMDA/PNP-sourced Metro Manila records **2005–2015** (96,000+ rows in the 2015 file alone), geocoded via Libpostal + Geocoder, mapped in Carto. **No GitHub repo, Kaggle link, or download location given anywhere in the piece** — author only lists a LinkedIn contact. Dead end as a source unless you can reach the author directly; also still Metro-Manila-only even if obtained.
- Rappler's 2017 "#SaferRoadsPH" data project — gathered crash data from "over a dozen national and local government units, including police offices in various cities and provinces" nationwide, described in their own reporting as "probably the biggest single compilation of data on road crash incidents in the Philippines" at the time, with a notable deep-dive on **Cagayan province**. This is the only nationwide, multi-province compilation effort found anywhere in this research. **However: no raw dataset download was ever published** — output was journalism (microsite + stories at `r3.rappler.com/move-ph/issues/road-safety/171657-...` and `.../171778-road-crash-incidents-cagayan-valley`), not an open data release. Worth a direct outreach email to Rappler's MovePH team to ask if the underlying spreadsheet was retained/shareable, but as observed today there is no self-serve download.
- APRSO (Asia-Pacific Road Safety Observatory, ADB-hosted, `aprso.org/datasets`) — hosts country-level WHO-consensus fatality-by-road-user-type figures and policy indicators (speed limits, economic cost), not crash microdata, and nothing finer than country/region level found.

**Conclusion for item 5: nothing found beats what you have.** The one nationwide multi-province effort (Rappler) never published raw data; everything genuinely downloadable today (Kaggle, Mendeley) stays Metro-Manila/EDSA-only.

---

## 6. iRAP ViDA for Philippines

**Status: Historical assessment exists; no evidence of an open, current public map/download.**
- In 2011–2012, with World Bank GRSF support, DPWH star-rated ~6,000 km of national highways using iRAP methodology — most roads scored 1-2 star for vulnerable road users (pedestrians, cyclists, local motorcyclists identified as highest-risk groups).
- ViDA (`irap.org/tools/vida-software-to-save-lives/`) is iRAP's general online platform for hosting Star Rating results and Investment Plans globally, but access is typically restricted to registered iRAP members/partner-government users, not an open public download portal. No PH-specific public ViDA map link, export, or updated (post-2012) PH star-rating dataset was found in this search.
- This is a one-time, 14-year-old national-highway-only assessment (not comprehensive of all roads, not geolocated crash data — it's infrastructure risk scoring, a different data type entirely) and there's no indication it has been refreshed or opened since.

---

## Summary table

| # | Source | URL | Accessible now | Granularity | Years | Format | Direct download |
|---|--------|-----|-----------------|-------------|-------|--------|------------------|
| 1 | DRIVER / roadsafety.gov.ph | roadsafety.gov.ph | **NO** — site down (ECONNREFUSED); NGO mirror also dead (ENOTFOUND) | Would've been point-geolocated nationwide | N/A (historically thin, 352 fatality records in all of 2019) | Web dashboard only, no export even when live | None ever documented |
| 2 | PSA vital-statistics deaths by cause (V01-V99) | openstat.psa.gov.ph (DB__1A__VS__DE) / psada.psa.gov.ph | **PARTIAL** — 403 to automated fetch; province rows implied by PSA's own press release but table not opened this session | Province / HUC (per PSA's VSR documentation) | 2010–2023 confirmed, 2025 provisional | PX-Web, native Excel/CSV export if unlocked | Not confirmed — needs manual browser check or PSA email (m.villaver@psa.gov.ph) |
| 2b | PSA OpenSTAT SDG 3.6.1 indicator table | openstat.psa.gov.ph/.../0123I3D0361.px | 403 to WebFetch | Region-level only (SDG indicator convention) | N/A | PX-Web | Not the province source — do not use |
| 3a | LTO | data.gov.ph LTO page, lto.gov.ph | **NO** dataset found | N/A | N/A | N/A | None |
| 3b | MMARAS (MMDA) | mmda.gov.ph FOI page | **PARTIAL** — annual PDF reports only, raw Excel explicitly withheld | Metro Manila only (no better than existing MMDA set) | 2005–2024 | PDF | None |
| 3c | DPWH TARAS | n/a | **NO** — discontinued 2013/2014 | National roads only | pre-2013 | N/A | None |
| 4 | DOH ONEISS | oneiss.doh.gov.ph | **NO** open microdata; PDF factsheets only | National aggregate | 2010–2019 (analysis), ongoing factsheets | PDF | None |
| 5a | Kaggle MMDA Twitter incidents | kaggle.com/datasets/esparko/mmda-traffic-incident-data | **YES** | Metro Manila (point-ish, incident locations from tweets) | 2018– | CSV | Yes, Kaggle download |
| 5b | Mendeley EDSA crash data (existing) | data.mendeley.com/datasets/hwbf6n4krw/1 | **YES** (unchanged) | EDSA corridor, Metro Manila | 2007–2016 | Tabular/GIS | Yes, "Download All" |
| 5c | Rappler #SaferRoadsPH compilation | r3.rappler.com/move-ph/issues/road-safety/171657-... | **NO** raw data release | Would be multi-province nationwide | ~2017 vintage | Journalism only | None — email Rappler MovePH to ask |
| 5d | HDX Philippines | data.humdata.org/group/phl | **YES** but roads-network only, no crash data | N/A | N/A | Shapefile/GeoJSON | Yes, but wrong data type |
| 6 | iRAP star ratings PH | irap.org / ViDA | **NO** public open access found | National highways, ~6,000 km | 2011–2012, not refreshed | Infra risk scoring, not crash data | Member/partner access only |

---

## Bottom line

Nothing found today is a confirmed, ready-to-download dataset that beats PSA region-level OpenSTAT plus your existing Metro-Manila (MMDA) and EDSA-corridor (Mendeley) sets. The one genuinely promising lead — PSA's province-level land-transport death counts, evidenced by PSA's own 2023 press release naming province rankings (Pangasinan, Nueva Ecija, Batangas, Cagayan, Isabela, Davao del Norte, Camarines Sur) — is not yet confirmed as a machine-downloadable artifact; every PSA domain blocked automated fetch (403) this session. DRIVER, the only source that could have delivered nationwide geolocated points, is offline (site down, mirror also dead). Everything else (LTO, MMARAS, TARAS, ONEISS, iRAP, Rappler, GitHub/Medium projects) is either discontinued, withheld in raw form, aggregate-only, or was never published as open data.
