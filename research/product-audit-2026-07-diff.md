# Product audit re-run: 2026-07-04 diff vs the June ~55 baseline

Confirmed against current source. Each June ship-blocker (from `product-audit-SUMMARY.md`)
re-checked, fixed or already-fixed noted with evidence.

## June ship-blockers

| # | Ship-blocker | Status | Evidence |
|---|---|---|---|
| 1 | e2e RED + false "all pass"; docs claim three.js 3D-on-satellite sim | **FIXED** | `sim.html` is a 2D canvas (`getContext('2d')`, line 66); `tests/e2e.sh` asserts "sim is a 2D canvas" / "map defaults flat (no 3D tilt)" / "no fake-traffic", no three.js/sat assertion; `bash tests/e2e.sh` → ALL CHECKS PASS; README describes the 2D canvas; DOSSIER records the walk-back at line 207. |
| 2 | Methodology bug: oneway=yes → V_safe 50→70 | **FIXED** | `sss_pipeline.py:230-233` now requires `dual_carriageway=yes`/`divider` for the 70 tier; one-way alone stays 50. `test_pipeline.py`: "one-way arterial is NOT divided -> 50" passes. |
| 3 | XSS on unescaped OSM `name` | **FIXED** | `esc()` in `index.html:303` applied at every sink (popup 723, road list 421-423, before/after 430, city labels 528, critical 671); `sim.html` escapes `CORR.name` (62-63); e2e checks both. |
| 4 | Imputed scored+glowed equal to real; fake "traffic" dots | **FIXED** | Shipped `sss_flagged_*.geojson` is real-posted only; the map draws imputed as a distinct faint-dashed `net-imputed` layer excluded from counts (legend line 280); the only animated points are real `vru-dots`/`crash-dots` from data (no `Math.random` traffic). |
| 5 | EDSA Busway false positive (segregated bus lane flagged) | **FIXED** | Pipeline `safe_speed` now guards segregated busway/BRT service ways (returns 70); `build/overlay/fix_busway.py` zeroed the 3 existing EDSA Busway segments (7,589 → 7,586 flagged). Not in any headline. |
| 6 | Score is a 6-value ladder dressed as 0-100 | **FIXED (by Phase 2)** | Folding continuous WorldPop density into exposure took Manila from ~6 distinct flagged SSS values to 359, spanning 6.2 to 75.0. |

## June high-value items

- Intersection-density claim: pipeline still does not compute it, and now no doc claims it does
  (README limitation names it as not-yet-computed). Honest.
- POI-only exposure (Medium intel finding): **addressed**: WorldPop residential density is now
  folded into E (`enrich_worldpop.py`); README/methodology updated.
- Crash validation (High feature gap): **shipped**: `validation.md`, flagged 7.3%/42%.
- Before/after recommended-limit view, road search, deep-links, data download: present
  (`showBeforeAfter`, road `find` input, `hashchange`, `dl` download link; all e2e-checked).

## Net

The June overall ~55 is materially improved: the two structural model defects (oneway, ladder)
are gone, the map no longer overstates risk (imputed distinct, no fake traffic), the sim/e2e
credibility gap is closed (green + honest docs), a class-error FP is removed, and the two biggest
feature gaps (crash validation, population exposure) are now shipped. Remaining honest gaps are
the ones that need NDA/paid data (operating speed, AADT, sub-metre imagery) or a bigger pull
(intersection density, full-NCR AOI), documented in the README limitations and `prior_art.md`.
