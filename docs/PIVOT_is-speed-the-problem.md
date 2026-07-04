# Next-session brief: "Is speed even the problem?" (operating-speed pivot)

Copy the fenced block into a fresh session in `~/Desktop/ai4saferroads-ph`. Everything above the fence is context for Xavier.

Why this exists: the tool scores the gap between the OSM posted limit and the Safe System survivable speed. Xavier's objection is the one every Filipino will raise: Metro Manila is gridlocked, real speeds are far below the posted limit most of the day, so "the limit is too high" feels academic. "The limit is 60, we crawl at 30, and we still crash. Is speed even the problem?" This brief turns that objection into the next version of the tool.

What was already checked this session (do not re-derive, and do not ignore): the MMDA crash set (17,312 incidents, 12,585 crash-type, timestamped) does NOT support the naive "crashes happen at night when the road clears." Total crashes PEAK in the morning rush (7-9am), 41% fall in the 7 peak/congested hours vs 12% in the 8 night hours (744/hr peak vs 186/hr night). Total crashes track traffic VOLUME, not empty roads. So the simple version of the pivot is wrong and must not be shipped.

The honest pivot survives that, because total crashes are not deaths. A fender-bender in a jam is a crash, not a fatality; fatal risk scales with about the fourth power of speed. The deaths are the high-speed moments the average and the jam both hide. MMDA has no severity field. The Mendeley EDSA set does (killed_/injured_ counts, SEVERITY, DATETIME_PST, lat/lon), so it is the one open PH set that can test whether DEATHS skew to the high-speed hours. That test is the make-or-break of the pivot.

---

```
ultrawork rework ai4saferroads-ph around the question "is speed even the problem?" for Philippine traffic, don't stop until every phase is verified done.

PROJECT
- Path: ~/Desktop/ai4saferroads-ph  (NOT a git repo; deploy is `vercel --prod` from build/web on Xavier's PERSONAL Vercel account `xmpuspus` only)
- Live: https://ai4saferroads-ph.vercel.app
- What it is now: an open map scoring every drivable street in 51 PH cities against the Safe System survivable speed. Speed Safety Score (SSS) = gap between OSM posted limit and survivable speed, weighted by exposure (POI proximity + WorldPop residential density). 357,423 streets scored, 7,586 flagged. Findings A/B/C/D in docs/findings.md.
- The critique to answer: PH cities are congested, so real operating speeds sit far below posted limits most of the day. A skeptic says "the limit is 60, we crawl at 30, and still crash, so speed is not the problem." The current tool has no operating-speed layer, which its own June audit named the #1 gap (product-audit-intel-gaps.md: no operating-speed / 85th-percentile layer, the axis iRAP and USLIMITS2 are built on).

THE HONEST THESIS (test each, follow the data, do not assume)
- H1: operating speeds are far below posted limits in the jam, so the raw posted-limit gap overstates the everyday, average risk. TRUE by intuition; quantify it with a real or proxy speed layer.
- H2: deaths (not total crashes) concentrate where and when the road CLEARS and vehicles actually reach the limit: off-peak hours, motorways and cleared arterials, and powered two-wheelers filtering through gaps. This is the load-bearing claim. It is NOT yet proven and the naive total-crash version is already falsified (MMDA crashes peak in rush hour, volume effect). Prove or disprove H2 on severity data.
- H3: if H2 holds, the fix is not a lower number on a sign that no one obeys in traffic and no one enforces. It is road design that caps speed even when the road is empty (traffic calming, geometry). This deepens the shipped Finding C (flagged roads have crossings but lack calming, so the protection addresses the wrong variable).
- The core reframe for the skeptic: fatality exposure is to the MAX speed a road permits near people, not the average. A pedestrian on a road posted 60 with no calming is exposed to 60 the moment it clears, whatever the daily average. "Average 30" is a red herring for death.

SCOPE DECISION (recommend, then confirm with Xavier before large teardown)
- Recommended: REFRAME + a new data axis, NOT a teardown. Keep the Safe System scoring as the foundation (it defines the survivable speed). Add an operating-speed / design-speed axis and a severity-by-time axis, and re-lead the narrative to answer the objection. The tool becomes "where and when can vehicles actually reach lethal speed near people, and is the road built to prevent it?" A full pivot (dropping the posted-limit framing) is on the table only if the data forces it; ask Xavier before that.

PHASES

PHASE 0 - data probe (fast, first; log HTTP status + row/field counts to tmp/verify-<UTC>/)
Operating / observed speed (personal accounts only):
- TomTom Traffic Index (free, public): city-level average speed + congestion for Manila, Cebu, Davao. Manila is a flagship congested city. Good for the headline framing; city-level only.
- TomTom Traffic Stats / Move / O-D API: per-segment historical average speed. Paid with trial credits. Check the free allowance.
- Mapbox (free tier, traffic-aware) and HERE (freemium): can they return typical/observed speed per road or corridor.
- Grab / World Bank OpenTraffic legacy: OpenTraffic once produced per-segment speeds from Grab GPS for Manila/Cebu (~2016-2019). Likely defunct; probe for any archived dataset. (Uber Movement is dead since 2023 and Uber is not in PH; skip.)
Design-speed proxy (fully open, the strongest reproducible path): estimate the speed a road INVITES from OSM lanes, width, oneway/dual_carriageway, class, and sinuosity/curvature, plus presence of calming. This is congestion-independent and arguably the right variable. Pull the needed OSM tags via the existing Overpass pipeline.
Severity + time crash data (the make-or-break):
- Mendeley EDSA RTA 2007-2016 (data.mendeley.com/datasets/hwbf6n4krw; recipe in research/correlate-crash-refresh.md): killed_driver/passenger/pedestrian, injured_*, SEVERITY, COLLISION_TYPE, MAIN_CAUSE, DATETIME_PST, Y/X. Download it.
- MMDA already checked: total crashes peak in rush hour (see tmp/verify-*/mmda_traffic.csv), no severity field. Reuse for volume context only.

PHASE 1 - the make-or-break test (do this before building anything)
On the EDSA severity data, compute fatal (killed_total>0) vs non-fatal crashes by hour of day, and by COLLISION_TYPE / MAIN_CAUSE. Question: do DEATHS skew to the low-congestion, high-speed hours even though TOTAL crashes peak in rush hour? Report the real distribution with n and a rate, not a vibe. If fatals skew off-peak/high-speed, H2 holds and the pivot has a spine. If they do not, STOP and tell Xavier what the data actually says; the reframe must follow the data, not the story. Also check whether "overspeeding" shows up as MAIN_CAUSE and at what share.

PHASE 2 - the operating/design-speed layer
Build the best speed axis Phase 0 made available, in this preference order: (a) real per-segment operating speed if a source is reachable on a personal account, else (b) a transparent OSM design-speed proxy, clearly labelled as a proxy. Per segment, hold three numbers: posted limit, survivable speed (V_safe), and operating/design speed. Reframe the danger to foreground the operating/design speed: a road is dangerous where it INVITES or ALLOWS over-survivable speed AND people are exposed, regardless of the congested average. Where operating speed is well below posted (chronic congestion), say so honestly, and shift the flag to "the road still permits lethal speed when it clears + no calming."

PHASE 3 - the temporal / enforcement dimension
Add the time axis: crashes (and fatals, on EDSA) by hour; the "clear-road window" when speeds are high. Frame the enforcement gap: a posted limit far above operating speed that is unenforced and uncalmed does nothing; the only lever that binds is physical (calming). Tie this to the shipped Finding C calming numbers (Manila 21% / Cebu 10% / Davao 4%).

PHASE 4 - map + narrative
Map layers: operating/design speed vs posted vs survivable (a 3-way per segment); a temporal view (crash-by-hour, the clear-road window); the calming gap. Re-lead the copy to answer the objection head on. Keep the shipped SSS/wealth/crowding work; add these axes. Reuse the Tufte-MBB dot styling and the breathing/ping animation system already in build/web/index.html. MANDATORY visual gate: Playwright screenshots at 1920x1080 AND 1440x900, read each back.

PHASE 5 - deslop + publish
/deslop over all human-facing copy (UI strings included, the whole map was plain-Englished this session; keep that bar). Recompute every number, corroborate to the digit across README/findings/methodology/map/LinkedIn. Regenerate OG card + hero demo.gif from the live site. Deploy `vercel --prod` from build/web, fingerprint live vs local.

HARD GUARDRAILS (carry over)
1. Do not ship the naive "crashes happen at night" claim. MMDA total crashes peak in rush hour. Separate fatal severity from frequency and prove H2 on real severity data, or drop it.
2. Every number recomputed this session, sourced inline, not asserted. Verify data sources live before building on them.
3. Civic-tech PH language: conservative, defensible. "Flagged for review," never an accusation. Keep the public-data disclaimer.
4. No AI jargon, no em-dashes, no colons-in-prose in human-facing copy (UI included). /deslop enforces at the end.
5. Personal accounts only for any speed/traffic API (TomTom/Mapbox/HERE/GCP), never a work account. The stale ρ=0.42 in research/RECIPE_SSS_RWI_OVERLAY.md is SUPERSEDED; never let it into copy.

READ FIRST
- docs/findings.md (findings A/B/C/D, the shipped story), docs/validation.md (crash validation, the region-death decoupling).
- research/product-audit-intel-gaps.md (the operating-speed gap, file:line), research/prior_art.md (2026 refresh: iRAP/USLIMITS2 are operating-speed tools; satellite crash models not PH-reproducible).
- research/correlate-crash-refresh.md (EDSA Mendeley + MMDA recipes), research/phase2-crowdedness.md (the crowding triple).
- tmp/verify-*/mmda_traffic.csv (the crash-by-hour result is reproducible from this).

Start: cd ~/Desktop/ai4saferroads-ph && read docs/findings.md and research/product-audit-intel-gaps.md, then run PHASE 0, then PHASE 1 (the make-or-break EDSA severity-by-hour test) before building anything.
```
