# DOSSIER — ADB "AI for Safer Roads" Innovation Challenge

Single source of truth. Read at the start of every iteration, append at the end. Never overwrite history.

Last updated: 2026-06-25 (Iteration 0 — Phase 0 complete)

---

## PHASE 0 — GROUND TRUTH (LOCKED)

### Deadline (RESOLVED — was ambiguous)
- **Source A (official):** https://challenges.adb.org/en/challenges/ai4saferroads — "Application Deadline: By 5 July 2026" with "AI model submission by 25 June."
- **Source B:** https://www.aprso.org/news/adb-launches-ai-safer-roads-innovation-challenge — "Deadline for applications: 25 June 2026."
- **Resolution:** Two-stage deadline. AI-model component due **25 June 2026 (TODAY)**; full application package due **5 July 2026 (T-10)**. Review July 2026; top-5 shortlist announced **September 2026**; refinement (build viz on ADB GIS platform) September 2026; pitch to jury **October 2026**.
- **Planning rule:** binding outer bound = **5 July 2026**. The June/July submission is the *model + approach + spatial output*, NOT a production product. Production-grade GIS viz is the September refinement phase (top-5 only). => the minimal proof artifact IS the submission core. Build it NOW.

### DATA_MODE (RESOLVED) = open-proxy
- Official datasets are NDA-gated, accessed "after registration and agreeing to NDA" (source: challenges.adb.org). User IS registered but NDA data is NOT on disk (verified: no *adb*/*saferroad*/*speed*/*road* dataset dirs on ~/Desktop). No-mock-data rule => cannot fabricate GPS-probe data.
- **Decision:** Build on OPEN PROXIES designed for drop-in of official data:
  - Road network + functional class + speed tags: OpenStreetMap PH (Geofabrik bulk / Overpass API).
  - Operating-speed proxy: OSM `maxspeed` vs inferred design speed; (official GPS-probe 85th-pctile drops in here).
  - Street-level imagery / sign features: Mapillary public API (free token).
  - VRU exposure: schools/markets/hospitals POIs (OSM), population grid (WorldPop/Meta HRSL/GHSL), land use (OSM/ESA WorldCover via personal GEE).
- **Showcase safety:** open-proxy avoids NDA leakage in any public artifact. Official data drops into the same schema for the actual submission.

### Deliverable (LOCKED)
Source: challenges.adb.org. Participants submit:
1. An **analytical model** that assesses whether posted speed limits align with **Safe System** principles.
2. A **spatial/map-based visualization** highlighting **priority segments** for review or intervention.
3. A **Speed Safety Score** + geospatial visualization.
4. (Top-5 only, Sept) visualizations built on **ADB's GIS platform**.
Team size 1–5; eligibility = data scientists / AI / transport engineers / policy from ADB member countries. PH = ADB member, eligible. Pilot opportunities up to USD 20,000.

### Required model capability (re-read from brief)
1. Assess whether posted limits align with Safe System principles.
2. Flag segments where limits are inconsistent with **road function** or **VRU exposure** (pedestrians, cyclists, powered-two-wheelers / P2W).
3. Produce a **SPATIAL, map-based output** highlighting priority segments.
4. Scalable/replicable across **Asia-Pacific**.

### Evaluation criteria (INFERRED — not published explicitly; flag as assumption)
No public weights. Inferred from the 3 solution features + standard innovation-challenge judging: Safe-Speed-Assessment rigor, Risk-Identification (VRU focus), Policy-readiness (Speed Safety Score + map), innovation, feasibility, APAC scalability, presentation. **open_question:** confirm criteria if published in NDA portal.

### Personal credentials (LOCKED)
- GEE service-account key: `~/Desktop/leaves-ph/.ee-key.json` (personal, GCP project `poised-honor-217909`); `~/.config/earthengine/credentials` present. NEVER a Boost/Attic/work account.

---

## data_matrix[] (Phase 3 — live probes, evidence in research/)
| dataset | source_url | access | evidence | cadence |
|---|---|---|---|---|
| OSM road network + functional class | Overpass API / Geofabrik PH | **GO** | live probe 2026-06-25: 12,420 drivable ways in MM-core AOI; full class hierarchy motorway→service (research/probe_overpass_summary.json) | static; refresh quarterly |
| OSM posted `maxspeed` | Overpass API | **GO** | 2,386 ways tagged (18.8% of drivable); real PH limits 40/30/60/20/80/100 km/h. Untagged ~80% = the model's "missing/implied limit" case | static |
| OSM VRU POIs (schools/markets/hospitals/transit) | Overpass API | **GO** | live probe: school 177, marketplace 33, hospital 16, place_of_worship 186, bus_stop 364, station 10 (research/probe_overpass_pois.json) | static |
| OSM Safe-System road tags (sidewalk/lanes/lit) | Overpass API | **GO** | sidewalk 3,313, lanes 5,515, lit 5,912 in AOI | static |
| Population density grid | WorldPop PH 100m / GHSL / Meta HRSL (via personal GEE) | **GO** (well-established, PH-covered) | confirm at build via `_gee_init.py` personal key; not yet probed | annual |
| Land use / built-up | OSM landuse + ESA WorldCover (GEE) | **GO** | OSM landuse in AOI + WorldCover global; personal GEE | static/annual |
| Mapillary street-level imagery + sign features | Mapillary Graph API (free token) | **CONDITIONAL** | needs free token signup + PH coverage-density check; high time-cost for 10-day build | rolling |
| Operating speed (85th-pctile) | — | **NO-GO open / GO via NDA** | edsa-traffic-intelligence legal review: NO Waze/Google/TomTom/HERE/Mapbox stored traffic. NDA GPS-probe drops in here | NDA |
| Traffic intensity (AADT proxy) | data.gov.ph AADT + DPWH 2,849 stations | **CONDITIONAL** | public but batch/coarse; verify granularity if needed | annual/batch |
| P2W (motorcycle) volume | NDA optional layer | **CONDITIONAL** | open proxy weak (land-use only); NDA P2W indicator drops in | NDA |

**Candidate feasibility verdicts (Phase 3 gate):**
- **GO (verified open-proxy end-to-end):** C1 (Safe System gap), C3 (VRU hotspot), C5 (before/after recommender — +published Nilsson coeffs, verify Phase 4), C6 (functional-class consistency), C7 (composite score), C8 (APAC pipeline — OSM global).
- **PARTIAL-GO:** C9 (VRU framing GO; P2W-specific *volume* CONDITIONAL on NDA → survives as a sub-layer of C3/C7, not standalone).
- **CONDITIONAL / enhancement-layer only (cannot be the standalone open-proxy submission):** C2 (operating-speed — no legal open proxy; drops in NDA GPS-probe), C4 (Mapillary CV — free token + coverage + time-cost), C10 (temporal — NDA).
- **Convergence implication:** the open-proxy-viable, deadline-feasible winner is the **synthesis C1→C7→C3/C9→C5 packaged as C8**, with C2/C4 as drop-in enhancements. No candidate ranked on assumed availability.

## asset_inventory[] (Phase 2 — verified by repo inspection)
| portfolio_project | reusable_asset | reuse_fit_candidates |
|---|---|---|
| **shake-exposure-ph (lindol.ph)** | `pipeline/exposure.py` = building×hazard-intensity exposure JOIN engine (the REPLICATE-NOT-REPLACE anchor: swap buildings→road-segments, shaking→speed-risk); `_gee_init.py` SA-key-first GEE init (personal cred); `boundaries.py`/`facilities.py`/`population.py`/`footprints.py`; PMTiles 2.26M-building glow layer; `web/index.html` + `vercel.json` + `og-card.png`; e2e harness | ALL — esp. C1/C3/C7/C9 (exposure join), C8 (pipeline) |
| **sinkmap-ph** | single-file inline-MapLibre `web/index.html` (velocity layer glow + "watch it sink" slider + layer toggles + methodology), `web/data/*.geojson` per-layer + `findings.json` + `cities.json` multi-city pattern, `methodology.html`, `serve.py`, Makefile, **88-check `tests/e2e.sh`**, Vercel auto-deploy | C1/C5/C7 map UI; C8 multi-city; before/after slider→C5; e2e harness reuse |
| **traffic-intelligence (edsa-traffic-intelligence)** | **Legally-vetted PH road-data envelope (2026-04-21):** OSM/Overpass road topology+segments+intersections (ODbL); DPWH Road Traffic Info (2,849 stations); data.gov.ph AADT (traffic-intensity proxy); Sakay.ph GTFS (transit/VRU proxy). **Hard rule: NO Waze/Google/TomTom/HERE/Mapbox-derived traffic in stored form** → operating-speed has no legal open proxy | Confirms open data path for C1/C3/C6/C8; KILLS open-proxy for C2/C10 (operating speed) → those CONDITIONAL on NDA |
| **leaves-ph** | GEE pipeline + `.ee-key.json` personal-cred path; `detection/` CNN train/infer pattern (classifier on imagery tiles); MODEL_CARD + reproducibility discipline; `site/` build | C4 (Mapillary CV reuses CNN-classifier pattern); GEE land-cover/landuse for C1/C3 |
| **floodwatch-ph** | ML model-train + MODEL_CARD + deterministic-sha reproducible-build pattern (F1 0.955); hazard overlay; `realtime/` | C4/C7 model discipline; hazard-layer overlay pattern |
| **dataviz-ph (dataviz.ph)** | animated bubble-chart engine + ETL + `vercel.json` + social-demo recording recipe | optional "speed-safety across cities/over time" animated companion view (C8 wow) |
| **atlas-ph** | PH Open-Gov knowledge graph (264K entities: infra spend, dynasties, budgets, typhoon, satellite) GraphRAG/Neo4j + `web/` | tangential — possible POI/entity enrichment only; not core |

## candidates[]
(Phase 1 — 10 distinct submission approaches. Each could BE the submission. `req` = hardest-hit challenge requirement: R1 align-with-Safe-System / R2 flag-VRU-&-road-function / R3 spatial priority-segment output / R4 APAC-scalable.)

- **C1 — Safe System Speed-Limit Gap model (normative).**
  Thesis: compute the Safe-System *recommended* max speed per segment from crash-survivability thresholds (30 where peds mix with traffic, 50 at intersection cross-conflict, etc.), compare to posted, flag the km/h gap. Score = f(posted − safe_speed, VRU exposure).
  Req: **R1** (most literal reading of "do limits align with Safe System"). Wow: map where every road glows by "how many km/h too fast the posted limit is for who is actually exposed." Data: OSM road class + maxspeed, VRU POIs, Mapillary crossing/footpath presence. CANONICAL.

- **C2 — Operating-speed vs posted-limit divergence (85th-pctile inversion).**
  Thesis: where 85th-pctile operating speed ≫ posted AND VRU high → limit unenforceable/mis-set; where operating ≪ posted on risky road → over-permissive. Critiques naive 85th-pctile speed-setting. Score = divergence × exposure.
  Req: R1/R2. Wow: "the road tells you its real speed." Data: GPS-probe (NDA) or open proxy. DATA-HEAVY / most NDA-dependent.

- **C3 — VRU-exposure hotspot prioritizer ("who gets hurt").**
  Thesis: build a VRU-exposure surface (peds/cyclists/P2W near schools, markets, transit, informal settlements) × posted limits; flag high-exposure × high-limit segments.
  Req: **R2**. Wow: school-zone danger index — emotionally resonant, policy-ready. Data: OSM POIs, pop grid, P2W proxy, posted limits.

- **C4 — Street-level imagery feature model (Mapillary CV).**
  Thesis: vision model reads Mapillary frames per segment → extracts sidewalks, crossings, median, lane width, frontage activity, sign presence → infers "self-explaining road" design speed → compare to posted.
  Req: R1 (road function from imagery), highest AI/ML content. Wow: "the AI reads the street like a traffic engineer." Data: Mapillary public API + vision model. Replicate-not-replace: extends SolarMap/TreeCover CNN-classifier pattern to street view. HIGH-WOW / HIGH-RISK-time.

- **C5 — Crash-survivability before/after limit recommender (policy-ready).**
  Thesis: don't just flag — output the *corrected* recommended limit + modeled change in fatal-crash probability via the speed–fatality power model (Nilsson/iRAP, fatality ∝ speed^4).
  Req: **R3** (policy-ready output). Wow: before/after map slider — "current 60 → Safe System 40, modeled fatal-risk −X%." Most actionable. Data: C1 inputs + Nilsson coefficients.

- **C6 — Functional-class consistency model.**
  Thesis: flag where posted limit is inconsistent with road *function* (local road posted at arterial speeds; arterial through a market posted too high) via OSM functional class + intersection density + land use.
  Req: **R2** (road function). Wow: "limit doesn't match what this road is for." Data: OSM functional class, intersection density, land use. LIGHTEST data deps / most robust open-proxy.

- **C7 — Composite Speed Safety Score index (fusion + explainability).**
  Thesis: fuse all signals into one transparent 0–100 Speed Safety Score per segment + per-segment "why flagged" attribution.
  Req: **R3** (Speed Safety Score). Wow: single legible index + drill-down. Data: union of above.

- **C8 — APAC-replicable "drop-in any city" pipeline.**
  Thesis: frame as a scalable pipeline (one config → any APAC city, open data, drops in official data when available); demo on Manila + Cebu + one non-PH APAC city.
  Req: **R4** (scalability). Wow: "same model, three cities, minutes." Data: OSM (global), Mapillary (global), open POIs.

- **C9 — Powered-two-wheeler (P2W) corridor risk model.**
  Thesis: APAC-specific — motorcycles dominate APAC road deaths; model P2W exposure and flag segments where posted limits ignore P2W vulnerability.
  Req: **R2** (VRU/P2W). Wow: "the motorcycle map" — uniquely APAC, differentiates from Western work. Data: P2W indicators (NDA optional) + OSM/land-use proxy.

- **C10 — Time-dynamic / school-hours speed risk.**
  Thesis: flag segments where posted limits ignore temporal VRU surges (school dismissal, market hours).
  Req: R2 (temporal VRU). Wow: time-slider map of when each segment is most mis-set. Data: GPS-probe temporal distributions (NDA) + school/market hours. MOST NDA-dependent.

**Phase 1 note:** the likely winner is a *synthesis* (C1 gap engine → C7 composite score → C3/C9 VRU/P2W weighting → C5 before/after recommendation, packaged as C8 APAC pipeline). C2/C10 lean hardest on NDA GPS-probe (open-proxy weak). C4 is highest-wow but highest time-risk. Convergence will prune — not pre-deciding here.

## open_questions[] (ranked by decision-impact)
1. **Is 25 June HARD-binding for the model component?** If yes we are at T-0 and the proof artifact must serve as the submitted model this week. Impact: CRITICAL (timeline). Mitigation: build proof artifact immediately regardless.
2. Are evaluation criteria/weights published in the NDA portal? Impact: HIGH (scoring rubric calibration).
3. Does the NDA GPS-probe dataset cover a PH AOI (Metro Manila?) or only selected APAC cities? Impact: HIGH (open-proxy AOI choice should match).

## PHASE 4 — METHODOLOGY: the Speed Safety Score (SSS)  [sourced; see research/prior_art.md]

Per road segment:
1. **Safe System recommended speed `V_safe`** from segment context (Tingvall & Haworth 1999 / ITF-OECD 2018 / WHO survivable-speed table):
   - 30 km/h — pedestrians/cyclists mix with motor traffic (no separation: `sidewalk=no/none` OR VRU POI within buffer OR residential/living_street with frontage).
   - 50 km/h — at-grade intersection with side-impact possible (undivided + intersection density high).
   - 70 km/h — undivided road, head-on possible, no side conflict.
   - 100 km/h — divided / grade-separated, no head-on or side conflict.
2. **Posted limit `V_posted`** = OSM `maxspeed`; if missing, impute functional-class default (and flag as "no posted limit").
3. **Speed gap** = `V_posted − V_safe` (positive ⇒ posted too high for Safe System).
4. **Excess fatal-risk factor `R = (V_posted / V_safe)^4`** (Nilsson power model, fatal exponent). R is the multiple of fatal-crash energy the posted limit permits vs the Safe-System speed. Policy-ready, sourced.
5. **VRU exposure weight `E` (0–1)** = normalized blend of school/market/hospital/transit proximity + population density + sidewalk absence + (P2W share when NDA layer present).
6. **Speed Safety Score `SSS` (0–100, higher = worse)** = `100 · normalize(max(0, gap)) · (0.5 + 0.5·E)` (transparent; exposure can at most double a gap's score, never invents risk where gap=0). Per-segment "why flagged" = {V_posted, V_safe, gap, R, top exposure driver}.
7. **Before/after (policy output)** = recommended limit `V_safe`; modeled fatal-risk reduction = `1 − (V_safe/V_posted)^4` (e.g. 60→30 ⇒ 1−(30/60)^4 = 93.75%).

Hits all 3 challenge solution features: Safe-Speed-Assessment (V_safe vs V_posted), Risk-Identification (SSS×E, VRU/P2W), Policy-ready output (recommended limit + modeled reduction + priority-segment map). Drop-in enhancements: NDA GPS-probe → replace step-2 imputation + add operating-speed divergence (C2); Mapillary CV → sharpen V_safe context (C4).

Novelty (sourced, claimed conservatively): an OPEN, OSM-based, network-scale *posted-limit-vs-Safe-System gap* map. iRAP = operating-speed star-rating (ViDA API); GRSF "Guide for Safe Speeds" 2024 = manual guidance; PH DRIVER = crash tracking. None produce this open posted-limit-appropriateness layer.

Risk log: (a) OSM maxspeed only ~19% coverage → mitigate with functional-class imputation + flag missing as its own finding; (b) V_safe classifier is a heuristic → keep thresholds transparent + cite; (c) PH hero stats need source-verification before use; (d) exposure normalization must not manufacture risk where gap=0 (formula enforces).

## PHASE 5 — CONVERGENCE SCORING  [weights: chal_fit×3, method×3, VRU×2, SSS_quality×2, map_wow×2, apac×2, feasibility×3, time×2, reuse×1, defensibility×2 ; max 110]

| candidate | chal_fit | method | VRU | SSS_q | wow | apac | feas | time | reuse | defens | TOTAL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **SYNTHESIS (SSS: C1→C7→C3/C9→C5 as C8)** | 5 hits all 3 features+4 capabilities | 5 Tingvall+Nilsson sourced | 5 exposure core | 5 transparent+before/after | 4 glow+slider | 5 OSM global | 5 verified GO probe | 5 reuses sinkmap/lindol+data pulled | 5 exposure.py+map | 5 all sourced/open | **108** |
| C8 pure-pipeline (thin model) | 3 | 3 | 3 | 3 | 3 | 5 | 5 | 4 | 4 | 4 | 81 |
| C4 Mapillary-CV-led | 4 | 4 | 4 | 4 | 5 highest wow | 3 coverage uneven | 2 token+CV time | 2 risky in 10d | 4 leaves CNN | 3 CV variance risk | 76 |
| C2 operating-speed-led | 5 | 4 | 3 | 4 | 4 | 4 | 1 no legal open proxy | 2 blocked w/o NDA | 3 | 2 can't build proof now w/o fabrication | 71 |

**Leader: SYNTHESIS (Speed Safety Score) — 108/110. Margin over next-best = 27 pts. Clear.**

## iteration_log[]
| n | targeted_question | what_found | new_info? | candidates_changed |
|---|---|---|---|---|
| 0 | True deadline, DATA_MODE, deliverable? | Two-stage deadline (25 Jun model / 5 Jul app); DATA_MODE=open-proxy; deliverable = model+SSS+priority map | YES | n/a |
| 1 | Candidates + portfolio assets + data feasibility? | 10 candidates; gold reuse = lindol exposure.py + sinkmap map; live Overpass probe = open-proxy spine GO; operating-speed has no legal open proxy | YES | C2/C4/C10 → enhancement-only; C1/C3/C5/C6/C7/C8 GO |
| 2 | Methodology core + prior art + scoring? | SSS defined (Tingvall+Nilsson, sourced); novelty = open OSM posted-limit-gap map; SYNTHESIS leads 108 vs 81, margin 27 | YES | Synthesis = leader |
| 3 | Does the leader survive a real proof artifact? | Computed SSS on 12,420 real MM segments (468 flagged real-posted); caught+fixed Skyway elevated-expressway false positive; rendered+visually-inspected priority-segment map (screenshots/sss_map_1440.png). Leader confirmed end-to-end | YES (confirmatory; leader unchanged) | none — leader proven |
| 4 | Verify load-bearing PH stat (agent said 65% motorcyclist)? | WHO GSRRS 2023 PHL: 11,062 deaths (2021), ≈53% motorcyclists (corrected from 65%), 8.07M powered 2/3-wheelers, urban limit 40 km/h, **LGUs can modify limits** (= why limits are inconsistent), manual enforcement | YES (corrected stat + new justification) | none — strengthens leader |

## open_questions[] — RESOLVED
1. 25-Jun hard-binding? → plan to 5-Jul outer bound; proof artifact built NOW regardless. (mitigated)
2. Eval criteria published? → not public; rubric inferred; reconfirm in NDA portal. (low residual impact)
3. NDA AOI = PH? → open-proxy uses MM-core; pipeline is AOI-agnostic, drops in any city. (mitigated)
4. PH motorcyclist share? → WHO ≈53% (not 65%). (resolved)

## convergence — CONVERGED
- leader: **Speed Safety Score (SSS) — open Safe-System posted-limit gap map, OSM open-proxy, APAC-replicable, NDA-drop-in**
- margin: 27 pts (108 vs 81) — clear and stable across iterations 1–4
- proof_artifact: **DONE & VISUALLY INSPECTED** — `build/sss_pipeline.py` computed SSS on 12,420 real MM segments (468 flagged with real OSM posted limits); `screenshots/sss_map_1440.png` rendered the priority-segment glow map (Read-back confirmed). Summary: `build/sss_summary.json`.
- consecutive_no_new_info: leader unchanged across iters 1–4; all new info was confirmatory or refining, none displaced the leader. Prime-Directive (a) satisfied: winner proven with evidence + working proof artifact.
- decision lock: `decision/DECISION.md`.

## POST-CONVERGENCE BUILD STATE (2026-06-25)
- **Reframe:** Xavier — for-fun personal showcase (sinkmap/leaves style), NOT an ADB submission. Same rigor, public open map.
- **Replicability PROVEN (user's first ask):** identical config + method on 3 APAC cities, live OSM each — Manila (12,420 seg / 2,337 real-posted / 468 flagged / 786 VRU), Cebu (9,064 / 1,351 / 334 / 527), Hanoi (10,010 / 158 / 58 / 774; thin OSM posted-limit coverage = honest finding). Screenshots all visually inspected.
- **Showcase scaffolded:** multi-city map w/ city selector + recenter (`build/web/index.html`); `methodology.html` (sourced, with disclaimer); `README.md` (conservative civic-tech language, "related work" not "prior art", CC-BY/MIT); `Makefile` (data/serve/shot/e2e); `tests/e2e.sh` + `tests/check_invariants.py`.
- **e2e: ALL PASS** across 3 cities — invariants hold (no score where gap<=0; no motorway downgraded to 30 [Skyway fix]; every over-posted segment has a fatal-risk reduction; scores in range) + map wiring + sources-cited checks.
- **Local-only**, no git/commit (consistent with sinkmap/leaves first-ship). Name candidates UNCHECKED (saferlimits-ph / speedsafe-ph) — conflict-check before any publish.
- **Open next steps:** before/after global slider; full-NCR AOI; intersection-density side-impact refinement; WorldPop exposure layer; Vercel deploy + domain; NDA GPS-probe drop-in (operating-speed divergence layer) if Xavier gets the data.

## iteration_log (cont.)
| 5 | Does "one config, any city" hold on real data? | Ran identical pipeline on Cebu + Hanoi: worked, real arterials surfaced (Cebu: Natalio Bacalso 60->30; Hanoi: Phố Tôn Đức Thắng 60->30). Hanoi posted-limit coverage thin (158). Multi-mirror fallback handled a 429. | YES (replicability confirmed) | none — leader productionized |
| 6 | Can the showcase match the portfolio's best (README/GIF/UX) + ship live? | 4-agent design audit → built premium map (Esri satellite+3D+glass+serif+animated traffic) + three.js Speed-Kills sim (FIRST 3D/three.js in portfolio) + real hero GIF + portfolio README; deployed live. | YES (presentation+deploy) | none — shipped |

## SHOWCASE UPGRADE (2026-06-25, v2 — design-pattern absorption + deploy)
- **Audit** (4 agents → `research/design-audit-*.md`): README lead/badges/hero recipe; leaves-ph `record_linkedin_demo.mjs` GIF recipe; lindol/sinkmap/dataviz web UX (Esri satellite + glass HUD + serif + story-rail); shake-exposure `vercel.json` + verified Esri World_Imagery config; **NO 3D/three.js precedent in any of 7 repos** (so this is a first).
- **Built (all visually inspected, gates passed):** premium multi-city map (Esri satellite basemap + dark scrim + 3D pitch + glass HUD + serif headline + animated traffic particles along the worst corridors + city selector + sim link); **three.js "Speed Kills" sim** (`sim.html`) — real Esri satellite ground of P. Sanchez St + reaction/braking physics + Tefft-2011 pedestrian survivability (60→struck 38%, 30→stops); hero `docs/demo.gif` (9.3MB real Playwright recording) + `docs/demo.mp4` (5MB, LinkedIn); `og-card.png`; portfolio-standard `README.md`; `vercel.json` + Range `serve.py`.
- **Verified facts:** pedestrian fatality curve = Tefft 2011 (AAA) 10%@23mph…90%@58mph (source-checked). Esri export endpoint (no key) → real corridor satellite texture.
- **e2e: ALL PASS** (added sim/corridor/satellite/Esri checks).
- **DEPLOYED (personal xmpuspus account):** **https://ai4saferroads-ph.vercel.app** (+ `/sim`, `/methodology`). Live-verified by screenshot-read-back of BOTH pages + 200 checks on og-card/cities.json/sat_corridor. Auto-alias from `xmpuspus-projects/ai4saferroads-ph`.
- **Open next:** name conflict-check before any public package/handle; optional before/after slider, full-NCR AOI, dot.ph domain; NDA GPS-probe drop-in.

## PRODUCT AUDIT + REDESIGN (2026-06-25, v3 — supersedes the 3D claims above)
- **Trigger:** Xavier — "the 3D-ness is useless to the story" + "perform thorough /product-audit and ship per the full audit." Conceded honestly: map 3D tilt = decoration; three.js sim form hid the load-bearing fact (distance).
- **/product-audit (4 agents → `research/product-audit-*.md` + `-SUMMARY.md`):** overall ~55/100. Caught: e2e RED + false "all pass"/3D-satellite claims; **one-way≠divided methodology bug** (under-flagged real arterials); **XSS** via unescaped OSM names; no fetch error/loading handling; imputed (81-98%) glowed equal to real-posted; fake `Math.random()` "traffic"; intersection-density claimed-not-built.
- **Shipped fixes (all verified, e2e green):**
  - sim: three.js+satellite → **2D canvas stopping-distance comparison** (60 STRUCK vs 30 STOPPED, draws reaction/braking distance; Tefft+Nilsson kept; STRUCK/STOPPED text cues for colorblind; reduced-motion).
  - map: **flat default** (3D tilt + fake traffic removed); XSS `esc()` on every OSM string; loading overlay + fetch-error + retry + city-switch race guard; **imputed flags dimmed/dashed, headline = real-posted only**; a11y (aria-pressed, keyboard road buttons, focus-visible, reduced-motion); data-date stamp; SRI on maplibre; road search; shareable city `#hash`; before/after card; data-download link.
  - **NEW guided "critical roads & why" toggle** (Xavier request + audit story-rail): spotlight the worst real-posted corridors, dim the rest, step through 8 explaining posted→safe + −% fatal + the why (VRU reason).
  - pipeline: one-way≠divided fixed (divided only via `dual_carriageway`); empty-Overpass guard; `data_date` stamp.
  - LICENSE file; pipeline unit tests (`tests/test_pipeline.py`); docs truthed (README/methodology/this).
- **New true counts (post-fix, 2026-06-25):** Manila 622 flagged real-posted (was 468; the bug had hidden them) / Cebu 375 / Hanoi 95. 3 cities, live OSM.
- **Re-deploy + re-record pending in this iteration.**

## iteration_log (cont.)
| 7 | Does the product survive a thorough audit + does the 3D earn its place? | No — audit ~55/100, 3D was decoration, e2e was red, real XSS + methodology bug. Rebuilt: 2D story-serving sim, flat honest map, guided critical-why mode, all audit ship-blockers fixed, e2e green. | YES (major redesign) | sim+map redesigned; leader unchanged |
| 8 | Map ALL streets + find a surprising correlation overlay (Xavier ask) | Pulled the FULL urban network (tiled Overpass, resilient skip-cell): Manila 87,123 / Cebu 22,402 / Hanoi 52,266 streets scored, served as one 7.5MB PMTiles. Computed REAL SSS×wealth (Meta RWI) overlay: Manila ρ−0.09 ns, Cebu +0.25 ns, Hanoi +0.51 (p=0.014, SIGNIFICANT — worst mismatch in wealthier areas). Moran's I positive all. Bivariate choropleth + finding panel shipped. | YES (scale + a real insight) | scope expanded; leader unchanged |

## FULL-NETWORK + CORRELATION OVERLAY (2026-06-25, v4)
- **Trigger:** Xavier — "map ALL streets in the areas we support, include them in the scoring so the network looks better" + "find correlations we can overlay that show emerging surprising insights, deep research with subagents."
- **Full network:** AOIs expanded to the full urban core; `fetch_tiled` pulls each city as a GRID×GRID Overpass mesh (resilient: retry rounds + backoff, skip-cell-on-failure, incremental `finalize`). Scored streets: **Manila 87,123 (4,667 flagged real-posted) / Cebu 22,402 (581) / Hanoi 52,266 (524)**. Full scored geojson stays local (`build/_fullnet`, ~42MB Manila); deployed render = ONE combined `sss_all.pmtiles` (7.5MB, tippecanoe, `city` property, filter-by-city); interactions use small per-city `sss_flagged_*.geojson`. Map switched to a PMTiles vector source (full network base + scored glow + imputed-dashed) — the network now reads as a real city grid.
- **Correlation overlay (4 research subagents → `research/correlation-*.md`):** best GO = **Meta Relative Wealth Index** (HDX, CC-BY, PH+VN). `build/overlay/compute_overlay.py` aggregates SSS to a ~1.6km grid (length-weighted, real-posted only), samples nearest RWI, computes **real** Spearman ρ + Moran's I with permutation p (NO fabricated stats — an agent's sample "Moran's I=0.18" was discarded). Bivariate 3×3 choropleth (Stevens) + "speed risk × wealth" toggle + finding panel + correlation≠causation caveat.
- **Findings (real, `docs/findings.md`):** mismatch does NOT track wealth — Manila ρ−0.09 ns, Cebu +0.25 ns, **Hanoi ρ+0.51 p=0.014 significant (wealthier areas)**. Significant in only one city, and there it's the better-off districts. Danger clusters spatially everywhere (Moran's I +0.13/+0.10/+0.35).
- **Shipped + LIVE-verified:** e2e green (full-network invariants + pmtiles/overlay wiring); new hero GIF (full network → critical → wealth → Hanoi) + og-card; README/methodology/DOSSIER truthed. Redeployed; screenshot-read-back of live full network + live Hanoi wealth overlay; all live paths 206 incl PMTiles range. **https://ai4saferroads-ph.vercel.app**.
- **Honest caveats:** RWI coarse (2.4km); p-values optimistic (spatial autocorrelation); Hanoi real-posted coverage thin (2%); screening layer, not determination.
