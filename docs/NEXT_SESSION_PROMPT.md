# Next-session prompt — ai4saferroads-ph enhancement pass

Copy the block below into a fresh session started in `~/Desktop/ai4saferroads-ph`.
It is written to be run top to bottom. Everything above the fenced block is context for you (Xavier); the fenced block is the prompt.

Why this shape: the goal is to enhance the shipped project so it earns attention when shared publicly, and to do it in the order that avoids poisoning the output. Data-source verification and correlation work come before the audits; `/deslop` runs last so it cleans final copy, not text that is about to be replaced; `/deep-research` sits behind the Workflow approval gate.

---

```
ultrawork enhance ai4saferroads-ph so it earns attention when shared publicly, don't stop until every phase below is verified done.

PROJECT
- Path: ~/Desktop/ai4saferroads-ph  (NOT a git repo — no branches, no PR, no CI; deploy is `vercel --prod` from build/web on Xavier's PERSONAL Vercel account only)
- Live: https://ai4saferroads-ph.vercel.app
- What it is: an open map that scores every drivable street in 51 PH cities against the speed a person can survive a crash at. Speed Safety Score (SSS) = gap between OSM posted limit and the Safe System survivable speed, weighted by pedestrian exposure. 357,423 streets scored, 7,589 flagged (real posted limit over safe speed). Single static MapLibre + PMTiles file (build/web/index.html); Python-stdlib pipeline (build/sss_pipeline.py).
- Framing: this is Xavier's weekend take on the ADB "AI for Safer Roads" Innovation Challenge (launched May 20 2026, submissions closed June 25, shortlist Sept 2026, jury Oct 2026). The challenge question is "where are speed limits misaligned with real-world road conditions." Xavier did not enter; he is sharing it as an open, reproducible reference. Sharing now rides the challenge's Sept visibility window.
- Goal Xavier stated: surprising, counterintuitive findings that make sense once you see them on a map or satellite image. Explore where high posted-speed gaps, crowdedness (population density), and deaths coincide. Verify the project's current data sources are still live, and source new ones that unlock the above.

READ THESE FIRST (they hold the specifics — do not re-derive them)
- docs/findings.md — the THREE counterintuitive findings already computed and shipped (see below).
- docs/validation.md — the crash-validation experiments (flagged roads = 7.3% of network, 42% of crashes).
- research/product-audit-SUMMARY.md + the four product-audit-*.md dimension reports (June 25 baseline, overall ~55/100, with a ship-blocker list).
- research/product-audit-intel-gaps.md — model/score defects with file:line (the highest-signal doc).
- research/design-audit-webux.md — the UI/UX pattern library lifted from sibling projects (lindol.ph, sinkmap-ph, dataviz-ph). This is the source for the frontend pass; apply from it, don't re-derive.
- research/correlate-exposure.md, research/correlate-deaths-subnational.md — the data sources already probed for crowdedness and deaths, with live download recipes.
- research/prior_art.md — the June competitive landscape (iRAP, USLIMITS2, GRSF, DRIVER, Mapillary). /deep-research refreshes this.

HARD GUARDRAILS
1. STALE CONTRADICTION — kill it before anything gets "corroborated": research/RECIPE_SSS_RWI_OVERLAY.md line 5 claims a POSITIVE wealth association ("ρ = 0.42, p < 0.001, high-speed high-wealth clusters"). That is a pre-computation planning placeholder and it is the OPPOSITE of the real computed result. docs/findings.md is the truth: Manila ρ = −0.09 (p 0.35), "not a wealth story," and where it is significant it is the POORER districts that carry the gap. Discard the RECIPE's ρ=0.42 and any "wealthy areas are faster" language. Never let 0.42 reach public copy. If the RECIPE is kept at all, stamp it "SUPERSEDED — see docs/findings.md."
2. Every specific number in public copy must be recomputed from the pipeline/overlay scripts this session, sourced inline, not asserted. Xavier's data-integrity rules are unforgiving here.
3. Civic-tech PH language: conservative, defensible. "Flagged for review," "warrants further investigation," never an accusation. Keep the public-data disclaimer block. A flag means a segment warrants review, not that a limit is wrong.
4. No AI jargon and no em-dashes in any human-facing copy (README, LinkedIn, methodology, findings). Deslop enforces this at the end.
5. Personal accounts only. GEE/GCP-backed pipelines use Xavier's personal service account (leaves-ph .ee-key.json, GCP poised-honor-217909), never a work account.

THE THREE FINDINGS ALREADY SHIPPED (build on these, find MORE like them)
A. Danger does not track wealth. Across 43 gridded cities the mismatch–wealth link is significant in only 3, and in all 3 it is the POORER side that carries the worst mismatch — but 3/43 at p<0.05 is barely above chance. Not a wealth story.
B. NCR has the MOST flagged roads yet the LOWEST road-death rate (3.6/100k vs national 10.9). Highest death rates are regions with few flagged urban roads (Cagayan Valley 22.1, Davao 16.8, Caraga 16.9). Deaths are counted by region of residence, dense cities have low free-flow speed and better trauma care — the urban map and the death map point at different places, on purpose.
C. Flagged roads have MORE pedestrian crossings than unflagged ones (Manila 36 m vs 71 m to nearest), not fewer — because they are arterials. What they lack is traffic calming (only 21% Manila / 10% Cebu / 4% Davao). A crossing manages where you cross; it does not change how fast the car arrives. The protection that exists addresses the wrong variable.

PHASES — run in this order.

PHASE 0 — Verify the existing data pipeline is still live (fast, do first)
Re-probe each source the project already depends on and record HTTP status + a row count in tmp/verify-<UTC-timestamp>/:
- OSM Overpass (build/sss_pipeline.py geometry + maxspeed + VRU POIs) — pull one city, confirm non-empty.
- MMDA crash mirror github.com/PotatoC0der/mmda_traffic_analysis (data_mmda_traffic_spatial.csv).
- PSA OpenSTAT region death tables (recipes in research/correlate-deaths-subnational.md).
- Meta Relative Wealth Index (HDX).
- WorldPop PH 2020 constrained .tif and Meta HRSL (recipes in research/correlate-exposure.md).
Any source that has gone dark: document the substitution in the README roadmap with the honest reason, don't ship broken data.

PHASE 1 — /deep-research (BEHIND THE WORKFLOW APPROVAL GATE)
/deep-research uses the multi-agent Workflow harness. Per Xavier's standing rule, Workflow is OFF by default and needs explicit approval EACH run — a skill instruction is not consent. Before launching, tell Xavier one line: "this fans out ~N agents, OK?" and WAIT for a yes in the conversation. (Reason the rule exists: a lindol.ph research run once spawned ~104 agents without agreement.) If Xavier declines the fan-out, fall back to 4-5 plain WebSearch/WebFetch agents instead.
Research goal: refresh research/prior_art.md to the current 2026 state and, more importantly, find NEW data sources and methods that unlock counterintuitive map/satellite findings. Seed it with these fresh sources already surfaced (the repo's June snapshot lacks them):
- IEEE: "Unveiling Roadway Hazards: Enhancing Fatal Crash Risk Estimation Through Multiscale Satellite Imagery and Self-Supervised Cross-Matching" (crash risk from satellite tiles alone).
- Unite.AI: "AI Predicts Accident Hot-Spots From Satellite Imagery and GPS Data."
- AAAI 2026: "Beta Distribution Learning for Reliable Roadway [risk]" (arxiv 2511.04886).
- ITF/OECD: "AI in Proactive Road Infrastructure Safety Management."
- highways.today (May 2026): "Rethinking Speed Limits with AI" (the ADB challenge writeup).
Also hunt for: any open PH province/city-level crash or death table finer than PSA region (province was NOT downloadable as of June); a machine-readable DPWH AADT traffic-volume layer (was WAF/FOI-blocked); DRIVER / roadsafety.gov.ph access (was unreachable); iRAP ViDA API access; Mapillary/street-view speed-sign detection for PH; and any dataset that supports a satellite-derived built-environment feature.

PHASE 2 — Correlation enhancement (the counterintuitive-findings engine; Xavier's core ask)
Save all intermediates to tmp/correlate-<UTC-timestamp>/. Recompute every stat; state Spearman ρ + p + n and Moran's I; display the correlation-not-causation caveat.
2a. CROWDEDNESS AXIS — fold WorldPop into exposure. WorldPop PH 2020 constrained is ALREADY DOWNLOADED but the pipeline still computes exposure E from POI proximity only (build/sss_pipeline.py exposure block, ~lines 191-203; confirm current state). Add a population-density term to E via zonal sum in a buffer around each segment. This IS the "crowdedness" axis Xavier asked for. Then WorldPop density × speed-gap × region deaths gives the speed × crowdedness × deaths triple.
2b. The map/satellite hooks — test and, where they hold, build a map layer + a real satellite crop:
   - Fast road through the densest housing: segments with the largest posted-over-safe gap that also sit in the top WorldPop-density decile. On satellite these read as a wide fast corridor slicing through packed low-rise rooftops. Annotate 3-5 named examples per metro.
   - Satellite-model vs SSS DISAGREEMENT: if Phase 1 finds a usable satellite crash-risk model, the counterintuitive story is where the satellite risk and the SSS flag DISAGREE, not where they agree.
   - Rural-highway death gap: the map flags city arterials, but the deadliest regions are rural (Cagayan Valley, Davao, Caraga). Make the "the map points at cities, the deaths are on rural highways" tension explicit and visual — it is finding B taken one step further.
   - P2W / motorcycle axis: 53-65% of PH road deaths are motorcyclists, but P2W enters neither V_safe nor E. Even documenting it as exposure context is a named APAC differentiator.
2c. Re-verify findings A/B/C against current data; update docs/findings.md only with recomputed numbers.

PHASE 3 — /product-audit (re-run against the ~55 baseline)
Run the 8-dimension audit again and diff against research/product-audit-SUMMARY.md. First confirm whether the June ship-blockers are fixed or still open:
- oneway=yes misread as "divided" → V_safe inflated 50→70 (was sss_pipeline.py:128-129) — silent false negatives on the exact roads the tool exists to catch.
- sim.html / e2e mismatch — docs once claimed a "three.js 3D over satellite" sim while the shipped sim is a 2D canvas, and e2e.sh asserted the 3D and FAILED. Confirm docs and e2e now match what ships.
- XSS on unescaped OSM `name` in popups (index.html + sim.html).
- Imputed limits (81-98% of data) glowing on the map at the same weight as real-posted, and animated "traffic" dots that are random. Honest in the counts, overstated in the picture — confirm the map now distinguishes imputed from measured.
- EDSA Busway (a segregated bus lane) surfacing as a priority road — class-error false positive.
- Score is effectively a 6-value ladder dressed as continuous 0-100.
Fix what is still open; note anything genuinely deferred with the honest reason (no silent deferrals).

PHASE 4 — UI/UX bug + polish pass (use the named skills)
Invoke /ui-ux and /frontend-design (or /ui-ux-pro-max) and apply the concrete patterns already catalogued in research/design-audit-webux.md — do not re-derive them:
- Premium read = dark Esri-satellite basemap + 15% dim scrim + one hot accent + backdrop-filter glass HUD (lindol.ph recipe).
- Story rail: lead with ONE finding, tap to fly + reveal a layer + drop callouts (sinkmap recipe). Turn the map into a guided narrative on first touch.
- A real before/after: "adopt Safe System limits" toggle that recolors the network by post-adoption SSS and totals the city-wide modeled fatal-risk reduction (the marketed feature; confirm whether it shipped). Bonus: a "watch it" time element like lindol's Esri Wayback scrubber if a temporal layer exists.
- Accessibility + honesty: sr-only ranked table of the deadliest segments, aria-pressed toggles, keyboard-operable rows, focus-visible, full reduced-motion, esc() on every upstream string, provenance/data-version stamp on the panel.
MANDATORY visual gate (Xavier's hard rule): per-viewport Playwright screenshots at 1920x1080 AND 1440x900, then READ each screenshot back and confirm it looks right. "It rendered" is not "it looks good." Greps miss layout breakage; the screenshot is the verification.

PHASE 5 — /deslop (LAST — final copy pass over everything human-facing)
Only after Phases 2-4 have changed the copy. Run /deslop over: README lead + body, docs/linkedin-draft.md, build/web/methodology.html, docs/findings.md, and any new finding write-ups. Strip AI tells, em-dashes, and jargon; keep Xavier's direct voice and the conservative civic-tech language. Re-verify the README lead and the hero demo.gif still match the shipped product (they drift silently after a re-center).

PHASE 6 — Publish
Regenerate the OG card and, if the visuals changed, the hero demo.gif from the LIVE site (real recording via build/record_demo.mjs, never a mockup). Refresh docs/linkedin-draft.md with the strongest recomputed counterintuitive finding as the hook (lead with substance, not "51 cities scored"). Deploy `vercel --prod` from build/web on Xavier's personal account. Fingerprint the live homepage against the local build before calling it shipped.

CORROBORATION (Xavier said "corroborate all of these")
Cross-read the outputs of Phases 1-5 against each other before publishing. Any number that appears in two places (README, findings.md, methodology, LinkedIn, OG card) must match to the digit. Any claim in one artifact that another contradicts (like the RECIPE ρ=0.42) is a defect, not a nuance — reconcile to the recomputed value.

Start: cd ~/Desktop/ai4saferroads-ph && read docs/findings.md, research/product-audit-intel-gaps.md, and research/design-audit-webux.md, then run PHASE 0 data-source verification.
```

---

## If you want a shorter variant

Drop Phases 1 and 6 and run it as a pure "audit + counterintuitive-findings + UI/UX" pass. Phase 2 (WorldPop crowdedness + deaths join) is the single highest-leverage piece for Xavier's stated "surprising, counterintuitive, visible-on-satellite" goal; if you only do one phase, do that one.
