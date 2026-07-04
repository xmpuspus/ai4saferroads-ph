# Landscape refresh — competitive/policy scan, July 2026

Prior-art review written June 2026. This refresh checks four areas: the ITF/OECD AI report, the highways.today article, the ADB AI for Safer Roads Challenge status, and any new 2025-2026 open speed-gap mapping tools. Research date: 2026-07-03.

---

## 1. ITF/OECD report: "AI in Proactive Road Infrastructure Safety Management"

- **Title:** AI in Proactive Road Infrastructure Safety Management (ITF Roundtable 187)
- **Source:** International Transport Forum, covered by iRAP
- **Date:** published **December 20, 2021** — this is a 2021 report, not a 2026 one. Flagging this explicitly because it's easy to mistake for current given the "2026 landscape refresh" framing.
- **URL:** https://irap.org/benefit-of-ai-in-proactive-road-infrastructure-safety-management-itf-findings-published/

**Summary:** Findings from a February 2021 ITF roundtable (33 organizations, 15 countries) on where AI adds value in proactive (pre-crash) road infrastructure safety management. Endorses computer vision for automated road-attribute coding and predictive models for high-risk-location mapping. Central recommendation: build "a competitive market for sharing and monetising traffic and mobility data" and push vehicle manufacturers toward data sharing. Prominently features iRAP's AiRAP (accelerated/intelligent RAP) initiative — ML + LIDAR + telematics to code road attributes faster and cheaper than manual survey.

**Speed-gap relevance:** No mention of posted-speed-limit-vs-survivable-speed gap analysis. This is a general AI-for-road-safety-data report, not a speed-specific one.

**PH/APAC relevance:** None named specifically; participant list is unspecified nations.

**Current-era update:** ITF adopted two new policy recommendations at its Leipzig Summit, **May 28, 2025** — a "Comprehensive Road Safety" recommendation (with WHO) and a recommendation on transport authorities' use of AI (oversight, risk/benefit balancing, awareness). Source: https://irap.org/worlds-leading-transport-forum-unveils-new-policies-for-road-safety-and-ai/ — this does not reference or supersede the 2021 report; it's a separate, more recent policy layer. Neither document mentions speed-gap mapping or the Philippines.

**Verdict on differentiator:** Neutral. General-purpose AI-for-safety-data framing; doesn't touch the specific speed-limit-vs-safe-speed gap niche.

---

## 2. highways.today: "Rethinking Speed Limits with AI for Safer Roads"

- **Source:** Highways Today
- **Date:** May 26, 2026 (search result also showed a May 25 URL slug; publish date per article is May 26)
- **URL:** https://highways.today/2026/05/25/rethinking-speed-limits-with-ai/
- **Authors:** James Leather (Director, ADB Transport Sector Office), Priti Gautam (Senior Transport Specialist and Road Safety Lead, ADB), Richard Owen (data scientist, CEO of Agilysis)

**Summary:** Co-authored by ADB and Agilysis leadership, this piece is effectively the launch explainer for the ADB Challenge (below). It argues AI + mobility data + geospatial analytics can replace slow manual speed-limit surveys with network-scale reviews: analyze GPS/probe data from millions of trips to flag roads where posted limits create unacceptable risk. It explicitly invokes Safe System kinetic-energy logic — quoting that pedestrians hit at ~30 km/h have substantially better survival odds than at 50 km/h — which is the same core mechanic this project uses (posted-limit vs survivable-speed gap, pedestrian-exposure weighted).

**Tools/vendors named:** ADB (commissioner), Agilysis (Richard Owen's firm — see section 4), ITU/AI for Good, World Bank Group, Asia Pacific Road Safety Observatory (APRSO) as challenge partners, funded by the Japan Fund for Prosperous and Resilient Asia and the Pacific.

**OSM/open data:** Not mentioned in the article content retrieved.

**PH mention:** None specific to the Philippines; framed as pan-Asia-Pacific.

**Verdict on differentiator:** This is the single most on-point document found. It validates the exact problem framing (posted-limit vs Safe System survivable-speed gap, at network scale, via AI). It does not describe an existing open tool — it's a call to build one (via the Challenge). Strengthens the "this is a real, currently-recognized problem" case; does not by itself weaken the "no open OSM-based tool exists" claim.

---

## 3. ADB "AI for Safer Roads" Innovation Challenge

- **Source:** ADB Challenges platform + Asia Pacific Road Safety Observatory (APRSO) + RoadSafe + fundsforNGOs
- **URLs:**
  - https://challenges.adb.org/en/challenges/ai4saferroads (primary/live page)
  - https://www.aprso.org/news/adb-launches-ai-safer-roads-innovation-challenge
  - https://www.roadsafe.com/ai-for-safer-roads-innovation-challenge/

**Confirmed timeline (verified directly against the live ADB page, quoted):**
- Launched: May 20, 2026
- Submission deadline: **June 25, 2026** — page text verbatim: "Submit your AI model and geospatial analysis by 25 June." (An intermediate WebFetch pass returned a "July 5" date from the APRSO page; re-fetching that page directly showed no deadline text at all, and a second direct fetch of the ADB page confirmed June 25. Treating "July 5" as a fetch artifact, not a real extension.)
- Status as of today (2026-07-03): closed to submissions, in expert review (per ADB page: "followed by expert review" in the weeks after June 25)
- Shortlist of 5 teams: expected September 2026
- Refinement phase: September 2026
- Jury presentations: October 2026

**No shortlist, winners, or named submitted solutions have been published anywhere as of 2026-07-03.** Searched directly for announcement content; none found. This is expected — per the stated timeline, shortlist doesn't land until September.

**What the challenge asks for (per the live page):** teams of 1-5 build models that (1) evaluate posted speed limits against road function and Safe System principles, (2) identify segments exposing vulnerable road users to excessive risk, (3) produce spatial visualizations and "Speed Safety Scores" for government decision-making. Data provided to entrants: GPS probe data, road network data, Mapillary street imagery with ML-tagged features, optional context layers (population density, land use, school proximity). No mention of OSM specifically, no stated open-source requirement, no stated public-accessibility requirement for the resulting tool. Winning teams build directly on **ADB's own GIS platform** — i.e., the challenge's own artifacts are not framed as open, portable, or public by default.

**Verdict on differentiator:** This is the highest-relevance finding. ADB is explicitly soliciting the same artifact this project already built ("Speed Safety Score," posted-limit-vs-Safe-System-gap, spatial visualization) — meaning the problem is validated at the highest institutional level. But: (a) nothing has shipped yet — no shortlist until September, no winners until after October jury; (b) the mechanism is closed/sponsored (ADB proprietary GIS platform, probe + Mapillary data, no stated open-source or open-data mandate) — structurally different from an open, OSM-based, publicly-browsable map. The differentiator ("open, OSM-based, already built, freely browsable") holds **as of today**, but this is a live, time-boxed window — assume 5 competing solutions will exist by September–October 2026, and treat that as this project's next checkpoint to re-verify, not a settled conclusion.

---

## 4. New 2025-2026 tools/entrants — does "no open OSM-based posted-limit-vs-Safe-System-gap map" still hold?

Checked against the four named systems plus new entrants surfaced in search.

### iRAP / ViDA / AiRAP — the closest boundary case, not dismissible in one line
- **URLs:** https://irap.org/rap-tools/enabling-software/vida/, https://vida.irap.org/, https://irap.org/airap/
- iRAP's Safe System-based Star Rating (1-5 stars) is philosophically the same family as this project (survivable-speed logic drives the rating), and iRAP has covered the Philippines before: ~6,000 km of PH national highways star-rated 2011-2012 with World Bank GRSF support (most rated 1-2 star for vulnerable road users). ViDA (vida.irap.org) offers a free "Reader Account" to view published/unpublished Star Rating reports — so it's semi-public, not walled off.
- **Why it still doesn't collapse the claim — four specific conjuncts it fails:**
  1. **Data source:** iRAP Star Ratings run on surveyed/coded road-attribute data (increasingly via AiRAP's ML/LIDAR/telematics pipeline), not OSM tags. It's a parallel, closed data-collection pipeline, not built on open community map data.
  2. **Metric:** produces a composite 1-5 Star Rating across many risk factors (roadside hazards, intersection type, etc.), not an explicit, isolated "posted-limit minus survivable-speed" gap number per street segment.
  3. **Coverage/currency:** the PH data is national highways only, from 2011-2012 — not every drivable street across 51 cities, and 14+ years stale.
  4. **Access model:** requires account registration and is scoped to "final published/unpublished reports," not an open dataset or open API a third party can freely re-derive from.
- **2026 activity:** iRAP is actively expanding AiRAP-accredited suppliers (Transoft Solutions and The Floow joined Agilysis, Anditi, TomTom in 2026) and updating its Star Rating Model (new version referenced for May 2026) to better reflect vulnerable-road-user risk. Source: https://irap.org/2026/02/latest-metrics-quantify-partners-global-impact/, https://irap.org/piarc-report-on-artificial-intelligence-in-the-road-sector/. This is a maturing, well-funded ecosystem — worth monitoring, but structurally different from this project's approach today.

### GRSF (World Bank Global Road Safety Facility) — thinnest finding, stated explicitly
GRSF appears in this research only as a funding/collaboration partner (funded the original 2011-2012 PH iRAP survey; co-produced the iRAP/gTKP/World Bank Road Safety Toolkit: https://toolkit.irap.org/). No standalone GRSF mapping product or 2025-2026 tool launch surfaced in this scan. Not treating this as "GRSF has nothing new" — only as "nothing new surfaced," since GRSF's own site wasn't directly crawled beyond the toolkit page.

### USLIMITS2 (FHWA)
- **URL:** https://highways.dot.gov/safety/speed-management/uslimits2
- Point/segment-level engineering-study tool for US practitioners setting individual speed limits — not a network-scale map. FHWA is developing **USLIMITS3** (targeted late 2025/early 2026) and NCHRP 03-139 will update its decision rules. US-only scope; not a competitor to a PH network map regardless of version.

### Vision Zero mapping tools (NYC Vision Zero View, Portland/SF dashboards)
Crash and citation dashboards, not posted-limit-vs-safe-speed gap analysis. US city-specific, not OSM-network-scale, no PH relevance. No new 2025-2026 entrant changes this assessment.

### Commercial speed-limit mappers found in this scan (new information not in prior review)
- **SpeedMap Global** (https://speedmap.global/) — "a speed limit for every road on the planet," AI + geospatial, targets fleets/insurers/road authorities. Maps **posted limits only** — no comparison to a safe/survivable speed. Proprietary/commercial. Current coverage: UK, Ireland, Romania, Cyprus only. No Philippines.
- **Agilysis** (https://agilysis.co.uk/) — the firm behind the ADB/highways.today piece. Commercial UK-based product suite: RiskMap, Speed Compliance Tool, Crashmap Pro, Traffic Insights (via TomTom partnership). One of two accredited AiRAP data suppliers. UK-focused; no evidence of a public, open, PH-covering product.
- **Initiative für sichere Straßen "hazard score"** (https://www.safer-roads.org/products/risk-score/) — OSM-displayed risk score (1-5), but built from police crash data + crowdsourced hazard reports + vehicle sensor data — crash-frequency-based, not a posted-limit-vs-survivable-speed metric. Germany only, commercial (Mobility Data Space licensing for full access).
- **Derq "Road Safety Score"** (https://en.derq.com/safetyscore) — real-time computer-vision safety monitoring embedded in Derq's commercial dashboard product (INSIGHT suite); not a public map, not speed-gap-based, no PH mention found.

None of these four combine: (open data / OSM-based) + (posted-limit-vs-Safe-System-survivable-speed gap metric) + (network-scale, every drivable street) + (Philippines coverage) + (freely public).

### Explicit hedge on the negative claim
This is a scan, not an exhaustive audit — the claim below is "nothing surfaced in a targeted search of iRAP, GRSF, USLIMITS2/3, Vision Zero tooling, and commercial entrants (SpeedMap Global, Agilysis, safer-roads.org, Derq)," not "no such tool exists anywhere." A private, unlisted, or non-English-indexed tool could exist outside this scan's reach.

---

## Bottom line on the "genuine differentiator" claim

**Holds as of 2026-07-03, with two live qualifiers:**

1. **The problem is now institutionally validated, not this project's own framing.** ADB, Agilysis, and ITU/AI for Good are all actively pursuing "posted-limit vs Safe System survivable-speed gap, at network scale" as of May 2026 — this is the exact ADB Challenge brief and the exact highways.today thesis. That's a strong signal the approach is correct, not a signal it's already been done in the open.
2. **Nothing that combines open/OSM-based + explicit speed-gap metric + PH coverage + public access has shipped.** iRAP is the nearest relative but fails on data source (surveyed, not OSM), metric (composite Star Rating, not an explicit gap number), coverage (2011-2012 national highways, not 51 cities' full street network), and access (registration-gated reports, not open data). Commercial entrants (SpeedMap Global, Agilysis, safer-roads.org, Derq) are either posted-limit-only or crash-frequency-based, and none cover the Philippines.
3. **The moat is time-limited by design, not by nature.** ADB's own challenge will produce five shortlisted, jury-reviewed solutions to this identical problem by October 2026 — built on ADB's proprietary GIS platform with probe/Mapillary data, not open OSM data. That means the durable differentiator to lean on going forward is specifically "open source, OSM-based, freely browsable, already built" rather than "no one else is thinking about this" — the latter is now false. Re-check this claim after the September 2026 shortlist announcement.

---

## Sources cited

1. https://irap.org/benefit-of-ai-in-proactive-road-infrastructure-safety-management-itf-findings-published/
2. https://irap.org/worlds-leading-transport-forum-unveils-new-policies-for-road-safety-and-ai/
3. https://highways.today/2026/05/25/rethinking-speed-limits-with-ai/
4. https://challenges.adb.org/en/challenges/ai4saferroads
5. https://www.aprso.org/news/adb-launches-ai-safer-roads-innovation-challenge
6. https://www.roadsafe.com/ai-for-safer-roads-innovation-challenge/
7. https://irap.org/rap-tools/enabling-software/vida/
8. https://vida.irap.org/
9. https://irap.org/airap/
10. https://irap.org/2026/02/latest-metrics-quantify-partners-global-impact/
11. https://irap.org/piarc-report-on-artificial-intelligence-in-the-road-sector/
12. https://toolkit.irap.org/
13. https://highways.dot.gov/safety/speed-management/uslimits2
14. https://speedmap.global/
15. https://agilysis.co.uk/
16. https://www.safer-roads.org/products/risk-score/
17. https://en.derq.com/safetyscore
18. https://roadsafetyfund.un.org/projects/strengthening-speed-management-philippines (checked — PH speed-enforcement training project, 2019-2020, finalized; not a mapping tool, not current)
