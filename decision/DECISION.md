# DECISION — locked build for the ADB "AI for Safer Roads" Innovation Challenge

Converged 2026-06-25. Leader proven with a working, visually-inspected proof artifact (Prime Directive (a) met). Full evidence trail: `DOSSIER.md`. Proof: `../screenshots/sss_manila.png`, per-city `../build/sss_summary_*.json`.

> **Scope note (post-convergence):** Xavier reframed this as a for-fun personal showcase (sinkmap.ph / leaves.ph style), NOT an ADB submission. Sections 7–8 below keep the challenge-fit framing for reference, but the deliverable is a standalone open map for the portfolio. Replicability was proven first (Manila + Cebu + Hanoi), then the showcase was scaffolded (README, methodology page, e2e).

---

## 1. Chosen project (one-paragraph thesis)

**Speed Safety Score (SSS): an open, network-scale map of where Metro Manila's posted speed limits exceed the Safe System speed for each road's function and pedestrian/rider exposure.** For every road segment it computes the Safe-System recommended speed from the road's class and surrounding vulnerable-road-user (VRU) sites, compares it to the posted limit, converts the gap into a modeled fatal-risk multiple (Nilsson power model), weights it by VRU exposure, and renders a 0–100 priority score on a map. It answers the challenge's exact question — is the *limit itself* appropriate — not whether drivers speed. It is built entirely on open data (OpenStreetMap) so it is publicly showcaseable today, and the official ADB GPS-probe data drops into the same schema (replacing limit imputation and adding operating-speed divergence) for the NDA submission. One config runs the same pipeline on any Asia-Pacific city.

## 2. Speed Safety Score — definition (inputs → score)

Per segment:
1. `V_safe` (Safe System recommended speed) from context — Tingvall & Haworth 1999 / ITF-OECD 2018 / WHO survivable speeds:
   - 30 km/h where pedestrians/cyclists mix with motor traffic (VRU site ≤50 m, or local road with frontage, or sidewalk absent).
   - 50 km/h undivided arterial with side-impact intersections.
   - 70 km/h divided/one-way arterial or trunk (head-on only).
   - 100 km/h motorway (grade-separated; never pedestrian-downgraded — fixes the elevated-expressway false positive).
   - 20 km/h living street.
2. `V_posted` = OSM `maxspeed`; if absent, imputed from functional-class default and **flagged** (official GPS-probe replaces this).
3. `gap = V_posted − V_safe` (positive = posted too high).
4. `R = (V_posted / V_safe)^4` — Nilsson fatal exponent; the fatal-energy multiple the posted limit permits over the safe speed.
5. `E` ∈ [0,1] — VRU exposure: VRU sites within 150 m (cap 5) + sidewalk-absent bump.
6. **`SSS = 100 · min(gap,40)/40 · (0.5 + 0.5·E)`** (0–100; exposure can at most double a gap's score, never invents risk where gap = 0).
7. **Policy output (before/after):** recommended limit = `V_safe`; modeled fatal-risk reduction = `1 − (V_safe/V_posted)^4` (e.g. 60→30 ⇒ −93.75%).

Hits all three required solution features: Safe-Speed-Assessment (V_safe vs V_posted), Risk-Identification (SSS×E, VRU/P2W), Policy-ready output (recommended limit + modeled reduction + priority-segment map).

## 3. Methodology spec (sourced)

- Survivable-speed thresholds: Tingvall & Haworth 1999; ITF/OECD *Speed and Crash Risk* 2018; WHO Speed Management Manual.
- Speed→fatality: Nilsson Power Model 1981 (fatal ∝ v⁴, serious ∝ v³, injury ∝ v²); Elvik update.
- Pedestrian impact-speed fatality risk: Rosén & Sander 2009 (50 km/h > 2× risk at 40, > 5× at 30; ~5–10% at 30).
- Why PH specifically: WHO GSRRS 2023 — 11,062 est. road deaths (2021); ≈53% motorcyclists; 8.07M powered 2/3-wheelers (largest vehicle class); national urban limit 40 km/h, **local authorities can modify limits** (→ inconsistent posted limits across LGUs), manual enforcement.
- Novelty (claimed conservatively): iRAP Star Rating = operating-speed star-rating (ViDA API); World Bank GRSF *Guide for Safe Speeds* 2024 = manual guidance; PH DRIVER = crash tracking. None produce an open, OSM-based, network-scale *posted-limit-vs-Safe-System gap* layer. That is the niche.

## 4. Data plan

- **Official (NDA, drop-in):** GPS-probe operating speed + posted limits (replace step-2 imputation, add operating-speed divergence layer); road network attributes; Mapillary sign/feature ML; optional population/land-use/school/P2W layers. Same segment schema.
- **Open-proxy (built, verified GO):** OSM via Overpass/Geofabrik — road network + functional class + `maxspeed` + VRU POIs (schools/markets/hospitals/transit) + sidewalk/lanes/lit; WorldPop/GHSL population (personal GEE); ESA WorldCover land use. Live probe 2026-06-25: 12,420 drivable segments, 2,337 real posted limits, 786 VRU sites in the MM-core AOI (`research/probe_overpass_summary.json`).
- **Legal guardrail (from edsa-traffic-intelligence review):** no Waze/Google/TomTom/HERE/Mapbox-derived traffic in stored form → operating speed comes only from the NDA probe, never a scraped commercial source.

## 5. Architecture — reusing named portfolio assets (replicate-not-replace)

- **lindol.ph `pipeline/exposure.py`** (building × shaking-intensity join) → replicated as road-segment × VRU × speed-gap join. Same exposure-overlay method, new layer. Both kept side-by-side in framing: "the exposure method that counted buildings under shaking now counts road segments under speed risk."
- **lindol.ph `_gee_init.py`** → personal-GEE-key init (`leaves-ph/.ee-key.json`, project `poised-honor-217909`) for population/land-use. Personal credentials only.
- **sinkmap.ph `web/index.html`** single-file MapLibre + per-layer GeoJSON + `findings.json` + `methodology.html` + `serve.py` + **88-check `tests/e2e.sh`** → the proof map already follows this pattern; productionize for the submission.
- **leaves-ph `detection/`** CNN pattern → reserved for the optional Mapillary-CV enhancement (C4) if time permits post-shortlist.
- Deploy: Vercel auto-deploy (sinkmap/dataviz pattern).

## 6. Map / visualization design

- Priority-segment glow: muted grey road context + flagged segments colored and thickened by SSS (yellow→orange→red), so the worst corridors pop. (Built, inspected.)
- VRU layer: schools/markets/hospitals/transit as dots; "danger near a school" reads instantly.
- Before/after: per-segment popup + a planned slider — "posted 60 → Safe System 30, −94% modeled fatal risk."
- Policy panel: stats + named priority roads (real posted limit) + sourced methodology footer.
- APAC toggle: city selector (Manila now; Cebu + one non-PH APAC city to demo replicability).

## 7. Wow / showcase narrative (neutral, measurement+method+period)

"Across 12,420 Metro Manila road segments, 468 carry a posted limit higher than the Safe System speed for a road where people walk — including major arterials posted at 60 km/h beside schools and markets, where the survivable speed is 30. At 60 instead of 30 the modeled fatal-crash risk is ~16× higher. The map shows every such segment, what the limit should be, and the modeled risk reduction — from open data, replicable to any Asia-Pacific city." No "X was wrong" framing; the hero is the measurement, the Safe System method, and the 2026 OSM snapshot.

## 8. Build timeline (against verified deadline)

Binding outer bound **5 July 2026** (model component nominally 25 June; production GIS viz = Sept top-5 phase). Proof artifact already done.
- **Now → +2 days:** harden pipeline (full NCR AOI, intersection-density + divided-road detection, exposure refinement), productionize map (slider, city toggle, methodology page), e2e harness.
- **+2 → +4 days:** write the model/methodology note + Speed Safety Score spec as the submission doc; reproducible recipe; README + model card.
- **+4 → +6 days:** second-city demo (Cebu) for replicability; record a real demo; submit by 5 July. NDA-data drop-in slot kept open for the shortlist phase.

## 9. Reproducible proof recipe

```
cd ~/Desktop/ai4saferroads-ph
python3 research/probe_overpass.py        # data-surface feasibility probe
python3 build/sss_pipeline.py             # pull live OSM, compute SSS -> build/web/data/*.geojson + sss_summary.json
cd build && python3 -m http.server 8799 --bind 127.0.0.1 &
NODE_PATH=<npx-playwright> node shot.mjs   # render + screenshot -> screenshots/sss_map_1440.png
```

## 10. Open naming (needs conflict-check before finalizing, per portfolio rule)

Candidates (NOT yet checked against npm/GitHub/existing products): `saferlimits-ph`, `speedsafe-ph`, `limitcheck-ph`, `safespeed-ph`. Conflict-check before committing.
