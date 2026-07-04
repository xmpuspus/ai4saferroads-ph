# README + repo-metadata design audit (Xavier's PH civic-tech repos)

Source files read (only these):
- leaves-ph/README.md, leaves-ph/CITATION.cff, leaves-ph/MODEL_CARD.md
- sinkmap-ph/README.md
- shake-exposure-ph/README.md (branded lindol.ph)
- ghostwatch/README.md (deploys as tulaypinoy.ph)
- solar-map-ph/README.md
- floodwatch-ph/README.md
- dataviz-ph/README.md

Goal: extract the best reusable README patterns for a new repo, **ai4saferroads-ph** (a road-safety "Speed Safety Score" map).

---

## 1. The LEAD pattern (the first identity statement)

There are two lead shapes in the portfolio. Both open with what the project IS, in plain English, never a tagline or a slogan.

**Shape A: a `> blockquote` one-paragraph thesis** (the heaviest, most "measured-record" repos). It packs identity + sensor + period + the single surprising finding + what the map carries, then stops.

- sinkmap-ph (verbatim):
  > **sinkmap.ph** is the measured record of how fast the ground is sinking under Philippine cities, from open Sentinel-1 satellite radar, 2016-2025, shown next to where the floods actually hit. Seven cities are measured across Luzon, the Visayas, and Mindanao. [...] The fastest sinking in Metro Manila is **inland** in the Bulacan/Pampanga lowland, not the coast [...]

- floodwatch-ph (verbatim):
  > FloodWatch.PH: an open, reproducible measurement of where DPWH flood-control money was spent and where the water still came, for the Philippines, from public satellite data. The civic spine is the gap between what a flood-prediction model predicts and what the past flood record shows [...]

- solar-map-ph (verbatim, doubles as a version-history line):
  > SolarMap.PH: open-source rooftop solar detection from public satellite imagery. **v1.0** ships Greater Metro Manila as the calibrated reference region (F1 = 0.870 [...]). **v1.1** extends cross-domain coverage [...]

**Shape B: a plain first sentence (no blockquote)**, used by the lighter / more consumer-facing repos. Identity in one line, then a sentence of mechanic.

- leaves-ph (verbatim):
  > An interactive map of Metro Manila's tree canopy, measured from satellite imagery. Drag the year, search your barangay, and click any tree to see it from the sky.

- shake-exposure-ph / lindol.ph (verbatim):
  > The measured record of how Philippine earthquake exposure is growing, built from open data. It counts how much of the built environment sits under the strongest modeled shaking [...]
  > *Lindol* is Tagalog for earthquake. (Repository name: shake-exposure-ph.)

- dataviz-ph (verbatim, the most consumer/punchy):
  > Animated bubble charts of Philippine public data. Pick a story, hit play.

- ghostwatch (verbatim, a single declarative line then a paragraph):
  > Satellite verification of public infrastructure: see whether it was built, from space.

**Recurring tokens in every lead:** "measured record" / "measurement" / "open" / "reproducible" / "from public satellite data" / "for the Philippines" + an interaction verb pair ("drag the year, click any X"). The lead almost always states the time window (2016-2025) and the geography (Metro Manila / the Philippines).

**Takeaway for ai4saferroads-ph:** Lead with the blockquote thesis (Shape A) because a Speed Safety Score is a measured-index project. State: what it measures (a per-road-segment safety score), the input (open road + crash + speed data, name the sources at a high level), the geography + period, and the one surprising finding if you have it. End the lead with the interaction verbs ("search a road, drag the threshold, click any segment").

---

## 2. Badge sets (which, what order, what they signal)

Badges only appear on the "serious instrument" repos (leaves, sinkmap, solar-map, floodwatch). The consumer ones (dataviz, lindol, ghostwatch) carry few or none. ghostwatch carries only 3 (License, Python, Next.js). dataviz and lindol carry none.

Observed order, left to right, is consistent: **CI -> License -> Language -> [domain/method badge] -> [validation/metric badge] -> [reproducible-build hash] -> Status -> DOI**.

- leaves-ph: `CI` | `DOI` | `License: MIT (code) / CC-BY-4.0 (data)` | `Python 3.11+` | `Status: alpha`
- solar-map-ph: `CI` | `License: MIT` | `Data: CC-BY-4.0` | `Python 3.11+` | `Reproducible build (deterministic sha256 5cc0a093)` | `F1 0.87 @ t=0.85` | `DOI`
- floodwatch-ph: `CI` | `License: MIT` | `Data: CC-BY-4.0` | `Python 3.11+` | `Reproducible build (deterministic sha256 b7c70253)` | `Track B F1 0.955 event-disjoint` | `DOI`
- sinkmap-ph: `License: MIT (code) / CC-BY-4.0 (data)` | `Python 3.9+` | `InSAR: Sentinel-1 HyP3 + MintPy` | `Validated: 3 metros vs Aslan 2024` | `e2e: 88 checks` | `Status: alpha`

What each badge signals:
- **CI** -> the build/test pipeline is green (links to the actions workflow).
- **License split** -> code is MIT, data is CC-BY-4.0. Often one combined badge, sometimes two.
- **Python 3.x+** -> the language floor.
- **Method/domain badge** (sinkmap's "InSAR: Sentinel-1 HyP3 + MintPy") -> tells a peer what the pipeline actually is, in one badge.
- **Validation/metric badge** (F1, "Validated vs Aslan 2024", "e2e: N checks") -> the single number that proves it works; links to MODEL_CARD or a findings doc.
- **Reproducible-build hash badge** -> the classifier is bit-exact (`deterministic sha256 <prefix>`); links to the reproducible-build section.
- **Status: alpha** (orange) -> honest maturity signal.
- **DOI** -> a Zenodo badge; links to the minted DOI. Only on repos with a CITATION.cff + Zenodo webhook.

All badges are shields.io static badges except CI (GitHub Actions badge) and DOI (Zenodo badge). The metric/validation badges are `success` (green) colored; Status is `orange`.

**Takeaway for ai4saferroads-ph:** Carry `CI | License: MIT / Data: CC-BY-4.0 | Python 3.11+ | [method badge, e.g. "Road safety index: OSM + crash data"] | [validation badge once you have one] | [reproducible sha256 if a model ships] | Status: alpha`. Add the DOI badge only once a Zenodo release is minted. Skip a metric badge until a real number exists (do not fabricate one).

---

## 3. Hero image / GIF placement, caption, alt text

The hero is **always a real recording**, placed **immediately after the lead/badges**, and **always clickable to the live site**.

- Placement: GIF comes right after the lead paragraph (leaves, sinkmap, floodwatch, ghostwatch) or right after the lead + a one-line "live site" pointer.
- The image is wrapped in a link to the live deployment: `[![alt](docs/demo.gif)](https://site.url)` (leaves, sinkmap). ghostwatch uses an HTML `<p align="center">` block with `<img width="800">` + a separate centered `<em>` caption link.
- **Alt text is a full descriptive sentence**, not "demo". It narrates exactly what the GIF shows, in order. Example (leaves): "Exploring the Leaves.PH interactive map: the Metro Manila tree-canopy map, the contrast between Quezon City at 22% canopy and Pasay near the airport at about 3%, and individual trees shown from the sky [...]".
- **Caption style: a `<sub>` block** (sinkmap, solar-map, floodwatch) or italic `*...*` line (leaves, dataviz, lindol) directly under the GIF. The caption (a) declares it is a **real recording** of the live site, (b) names the recorder script (`via scripts/record_demo.py`, ``LINDOL_EE_KEY=... -m pipeline.exposure_growth``), and (c) walks the beats the viewer is seeing with the actual numbers ("the readout climbs to ~325 mm").
- Several repos carry **multiple GIFs**, each under its own feature section (leaves has 4: linkedin-demo, protected-areas, known-vs-predicted, remaining-canopy; dataviz has a landscape + a square social cut).

Caption verbatim examples:
- sinkmap: `<sub>Real recording of the live map ([sinkmap-ph.vercel.app](...), via scripts/record_demo.py): the nationwide overview, the key-findings panel [...] "watch it sink" accumulating 2016-2025 displacement on Metro Manila (the readout climbs to ~325 mm) [...]</sub>`
- floodwatch: `<sub>Real recording of the running site. Three beats: the home thesis [...]; the /lookup area check returning one conservative gap sentence [...]; and the 2024 Carina historical time series stepping through 4 real Sentinel-1 acquisition dates [...]</sub>`

**Takeaway for ai4saferroads-ph:** First artifact after lead+badges = a real recording of the live map, wrapped in a link to the deployed site. Alt text = a full sentence narrating the beats (the score map, a high-risk corridor, click a segment for its score breakdown). Caption in a `<sub>` block: "Real recording of the live map (via scripts/record_demo.py): ..." + the actual beats with real numbers. Never an HTML mockup or stitched screenshots (global rule).

---

## 4. Section order and which sections recur

Two families. The **CV/model repos** (solar-map, floodwatch, leaves) and the **map-only repos** (sinkmap, lindol, dataviz) share a backbone but differ on the model sections.

Canonical section backbone (in observed order):

1. **Lead + badges + hero GIF** (+ optional headline-finding paragraph and a results table right under the hero).
2. **What this measures** / **What the data shows** / **What it measures** — defines the single quantity, and immediately draws the exposure-not-damage / correlation-not-causation line.
3. **What [the radar/satellite] actually shows** (sinkmap, ghostwatch) — the honest core: where the method works and where it does not.
4. **What's in this repo** / **Project layout** — a bulleted directory tour (sinkmap, floodwatch, solar-map) OR an ASCII tree (solar-map, floodwatch, ghostwatch).
5. **What this is not** — a bulleted list of explicit non-claims. **This section appears in 6 of 7 repos** (leaves "What it is not", sinkmap, solar-map, floodwatch, ghostwatch implicitly via Disclaimer). Highest-recurrence honesty section.
6. **Privacy and responsible use** (solar-map, floodwatch) — DPO line, takedown channel, RA 10173 posture. Only on repos that touch building/rooftop-level data.
7. **Quickstart / Reproduce / Run it** — a copy-paste block. Always present. Often split into "Quickstart for researchers" (the model) + "Quickstart for the site".
8. **The reproducible-build / model section** (`Detection pipeline (reproducible)`, `Track B`) — `make train` / `make hash-verify` with the sha256 assertion.
9. **Headline numbers, with footnotes** (solar-map, floodwatch) — every number with its caveat inline.
10. **Method / Methodology in one paragraph** — a single dense paragraph, plus a link to the full `/methodology` page.
11. **Policy context** (solar-map, floodwatch) — "This dataset only matters because the policy context is contested." Names the actors.
12. **Data / Data products / Data files / Use the data** — a table: file | schema | notes. Always present.
13. **Data sources / Data attribution** — a bulleted or tabled list of every upstream source with its license + URL. Always present.
14. **Roadmap** (often titled "Roadmap (honest 'not yet')") — bullets of what is not done yet.
15. **License and attribution** — code MIT, data CC-BY-4.0, the redistribution attribution string, the required upstream attribution line.
16. **Citation** — bibtex block + a pointer to CITATION.cff + "a versioned Zenodo DOI is minted at each tagged release."
17. **Disclaimer / Public-record disclaimer** — the un-strippable `> blockquote` boilerplate (see section 6).
18. **Contact and corrections** — open a GitHub issue; private security advisory for RA 10173 concerns.

**Always-present sections (every repo):** the lead, a "what it measures / what the data shows", a run/reproduce block, a data-sources list, a license line, and a public-record disclaimer.
**Near-always (6/7):** "What this is not".
**Conditional:** Privacy/DPO + Policy context + Model card sections appear only where the data resolution or the political stakes warrant them.

**Takeaway for ai4saferroads-ph:** Use the map-only backbone (it is not a per-building privacy case unless the crash data is person-level): Lead+badges+hero -> What the Speed Safety Score measures -> What the data actually shows (where the score is reliable / where coverage is thin) -> What's in this repo -> What this is not -> Reproduce -> Headline numbers with footnotes -> Method in one paragraph -> Policy context (road-safety / DPWH-roads accountability) -> Data files table -> Data sources -> Roadmap -> License + attribution -> Citation -> Disclaimer -> Contact. Add Privacy/DPO only if any input is person-level crash data.

---

## 5. Tone / voice rules visible in the prose

These are consistent across every README and are enforced by the per-project CLAUDE.md files and CI sweeps:

- **Plain English, short sentences.** No marketing adjectives. "It counts how much of the built environment sits under the strongest modeled shaking" — verbs and nouns, no "robust" / "comprehensive" / "cutting-edge".
- **No emoji anywhere.** Zero emoji in all 7 READMEs.
- **No em-dashes.** Commas, colons, periods, parentheses instead. CI sweeps for them (leaves, sinkmap, lindol CLAUDE.md all flag this).
- **No AI-jargon / eng-bro verbs** ("land", "fold in", "leverage", "seamless"). Enforced by `check_ai_fingerprints.py` in floodwatch.
- **Conservative civic language is non-negotiable.** Every flag is "a prompt to look, never an accusation" / "warrants review, not a verdict". The word "fraud" is banned; "candidate" / "statistical indicator" / "flagged for review" are used. Sinkmap/lindol: "Correlation, not causation."
- **Positive framing** (lindol, sinkmap CLAUDE.md): say what each surface IS, not what it is not — except in the dedicated "What this is not" section, which is the one place negative framing is allowed.
- **"Related work", not "prior art".** solar-map titles its comparison `docs/research/related-work.md` and writes "Related work and prior tooling in the same space". floodwatch and ghostwatch use "Related work shows the pieces separately". Never "prior art".
- **Honesty as a feature, stated out loud.** Headers literally say "Roadmap (honest 'not yet')", "Headline numbers, with footnotes", "Honesty notes", "Honest gaps", "Roadmap" with caveats. floodwatch reports an IoU of 0.054 and says "This is reported plainly because it is honest, not because it is flattering."
- **Compute-before-narrate, stated.** "Every number is computed by scripts/analysis.py and baked into findings.json, not hand-typed." (sinkmap) / "All the finding text is written by pipeline/findings.py, never typed by hand" (lindol).
- **Bilingual signal.** EN/TL toggle is mentioned in the prose (dataviz, lindol, floodwatch, solar-map) and a Tagalog project name is glossed (`Lindol is Tagalog for earthquake`).
- **First-person plural is rare; the project is the subject.** "SolarMap.PH publishes statistical indicators", "FloodWatch is two tracks". Not "we built".

**Takeaway for ai4saferroads-ph:** Plain English, short sentences, no emoji, no em-dashes, no AI-jargon. A "Speed Safety Score" is a screen/prioritization tool, never a verdict on a road or a driver — say so. Use "candidate high-risk corridor" / "warrants engineering review", never "dangerous road" as an accusation. Title roadmap "Roadmap (honest 'not yet')". State that every number is computed, not typed.

---

## 6. How method / data / limitations / disclaimer / license / sources are each presented

- **Method**: two layers. (a) A one-paragraph "Method" or "Methodology in one paragraph" / "Method, in one line" in the README — dense, names the algorithm, the inputs, the caveat. (b) A pointer to the full `/methodology` page on the live site and/or `docs/methodology.md`. Several repos also carry a numbered step list (ghostwatch "How It Works" 1-6, lindol "Method" 1-6) and/or a mermaid flowchart (ghostwatch).
- **Data / data products**: a markdown **table** — `File | Schema | Notes` (leaves, dataviz, solar-map SCHEMA.md) — listing every published file with its columns and a one-line note ("hash-pinned", "derived from the CSV"). Plus "every file is regenerated by `make X`" and a sha256 manifest for download verification.
- **Limitations**: lives in three places — the **"What this is not"** bullets (hard non-claims), a **"Caveats"** / "Known biases and limitations" section (the MODEL_CARD carries the model-specific ones), and inline **footnotes on every headline number**. floodwatch's "Headline numbers, with footnotes" is the model: each number is followed by its honest caveat in the same bullet.
- **Disclaimer**: an un-strippable `> blockquote` near the end, near-identical boilerplate across repos:
  > All data sourced from public records. [Project] computes statistical indicators only. Specific allegations, if any, require independent investigation and corroboration.
  ghostwatch carries a longer bolded **Disclaimer:** paragraph inside the body too. The disclaimer is also repeated on every analytics surface in the app (per CLAUDE.md), not just the README.
- **License**: a short "License" or "License and attribution" section: `Code: MIT. Data products: CC-BY-4.0.` + a `Cite as` one-liner + the **required upstream attribution line** (leaves spells out the full Copernicus/Hansen/ESA/WDPA string verbatim). Author named: "Author: Xavier Puspus."
- **Sources**: a "Data sources (all free, all public)" bulleted list (lindol) or a `Source | Description | Access` table (ghostwatch), each entry = name + what it provides + license + URL. Stated emphatically that everything is free and public ("all free, all public", "No proprietary or restricted datasets are required").

**Takeaway for ai4saferroads-ph:** Method = one dense README paragraph + a link to a `/methodology` page. Data files in a `File | Schema | Notes` table. Limitations split across "What this is not" + footnoted headline numbers + a Caveats section. The exact public-record disclaimer blockquote, verbatim with the project name swapped. License = MIT code / CC-BY-4.0 data + a Cite-as line + every upstream source's required attribution. Sources in a table with license + URL, headed "all free, all public".

---

## 7. Length / density

- **Short and punchy:** dataviz-ph and lindol leads; ghostwatch's one-line lead. The consumer repos open light.
- **Medium:** leaves-ph (~175 lines), sinkmap-ph (~224 lines) — feature sections + tables + reproduce + license, no CLI reference.
- **Long / reference-manual:** ghostwatch (~670 lines) and solar-map-ph (~374 lines) — they double as the full docs (CLI reference tables, Python API examples, config tables, adapters, comparison tables). These are the repos meant to be cloned and run by others.
- floodwatch-ph (~220 lines) and lindol (~370 lines) sit in between — dense but no API reference.

Density technique: **tables everywhere** (data files, sources, env vars, comparison matrices, per-region status, headline metrics), **fenced code blocks** for every runnable step with **inline `# comment` annotations showing real output** (ghostwatch shows the actual JSON a `verify` call returns). Prose is broken by `##` headers every 15-40 lines; long sections get `###` subheaders.

**Takeaway for ai4saferroads-ph:** Target the medium band (leaves/sinkmap, ~180-220 lines). Lead light, then feature sections with one results table, a reproduce block, a data-files table, sources, license, disclaimer. Reserve a long CLI/API-reference layout only if the road-safety scorer ships as a pip-installable tool others run (like ghostwatch). For a map-first project, medium is the right weight.

---

## 8. What makes them read human-written and LinkedIn-credible

- **A real, specific surprising finding in the lead.** "The fastest sinking in Metro Manila is inland, not the coast." "DPWH spend shows no clear link to poverty (rho +0.12)." Specific, counterintuitive, sourced. This is the hook a human shares.
- **Concrete numbers with units and provenance, never round marketing figures.** "448,909 buildings inside the MMI 7+ zone", "69.9 MWp", "rho = -0.25 (p = 0.026)". Every number traces to a file or a computation. No "thousands of", no "significant".
- **Admitting what does not work, in the open.** floodwatch publishing IoU 0.054 and explaining why. solar-map listing a blue-stadium false positive. lindol reporting coherence-limited non-results "as honest non-results, not forced numbers." This candor is the strongest human signal.
- **The honesty headers** ("Roadmap (honest 'not yet')", "Headline numbers, with footnotes", "Honest gaps") read like a person wrote them, not a launch page.
- **Reproducibility as proof, not a claim.** "Every number is reproducible from a clean clone." `make hash-verify` asserts a sha256. The reader can check.
- **No AI fingerprints:** no emoji, no em-dashes, no "delve/leverage/comprehensive/seamless", no rule-of-three padding, no "In today's world" openers, no section-divider ASCII art. Just nouns and verbs.
- **Civic restraint:** "a prompt to look, never an accusation" everywhere. This reads as responsible, not sensational — the exact tone a serious civic-tech audience trusts.
- **Real recordings, captioned with the recipe.** The hero is the live tool, and the caption tells you how it was recorded, so it is verifiable.
- **A DOI + CITATION.cff + MODEL_CARD.** These academic-credibility artifacts signal the author treats the work as citable research, which lands well with a technical/policy audience.

**Takeaway for ai4saferroads-ph:** Lead with one true, specific, sourced surprising finding about road safety (e.g. "the highest-scoring corridors are not the expressways but a handful of national secondary roads"). Every number traces to a file. Admit coverage gaps openly. Title the roadmap honestly. Ship a CITATION.cff + a real recording. Keep civic restraint: a high score is a prompt for engineering review, never a claim that a road is unsafe or that anyone is at fault.

---

## README template for ai4saferroads-ph (ready to use)

Fill the bracketed placeholders. Do NOT invent numbers — leave a placeholder until the pipeline computes a real value. No emoji, no em-dashes, no AI-jargon.

```markdown
# ai4saferroads.ph

[![CI](https://github.com/xmpuspus/ai4saferroads-ph/actions/workflows/ci.yml/badge.svg)](https://github.com/xmpuspus/ai4saferroads-ph/actions/workflows/ci.yml)
[![License: MIT (code) / CC-BY-4.0 (data)](https://img.shields.io/badge/license-MIT%20%2F%20CC--BY--4.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Method: OSM roads + crash record + speed](https://img.shields.io/badge/method-OSM%20roads%20%2B%20crash%20%2B%20speed-success.svg)](docs/methodology.md)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](README.md)
<!-- Add once real: [![Validated: ...](...)] [![Reproducible build sha256 ...](...)] [![DOI](...)] -->

> **ai4saferroads.ph** is the measured record of where Philippine roads score most dangerous to drive,
> computed per road segment from open data: the [OSM road network / official crash records / speed
> and geometry signals], for [geography], [period]. Each segment carries a Speed Safety Score and the
> factors behind it. [One true surprising finding once computed, e.g. "the highest-scoring corridors
> are national secondary roads, not the expressways."] A single-file [MapLibre] map carries the score
> layer, a threshold slider, per-segment cards, and a methodology page, with the
> screen-not-verdict disclaimer throughout.

[![ai4saferroads.ph walkthrough: the national Speed Safety Score map, a high-scoring corridor flying into view with its callout, and a single segment clicked open to show its score breakdown](docs/demo.gif)](https://ai4saferroads-ph.vercel.app)

<sub>Real recording of the live map ([ai4saferroads-ph.vercel.app](https://ai4saferroads-ph.vercel.app),
via `scripts/record_demo.py`): the nationwide score overview, the key-findings panel, a high-score
corridor card, and the threshold slider re-painting the map. The apex **ai4saferroads.ph** goes live
once its dot.ph A record points to the host.</sub>

## What the Speed Safety Score measures

This measures **relative road-safety risk** per segment: a 0-100 score combining [crash density,
road geometry, speed environment, and exposure] from open data. It is a prioritization screen, not
a verdict on any road and not a claim about any driver. Where a segment scores high is a place to
send an engineering review, not a finding of negligence. Correlation, not causation: a score reflects
the inputs above, not a proven cause of any crash.

## What the data actually shows

[Where the score is reliable: dense, well-mapped corridors with good crash coverage. Where it is
thin: rural roads with sparse crash records or incomplete OSM geometry, reported as honest
low-confidence rather than a forced score. State the coverage boundary plainly.]

## What's in this repo

- **`pipeline/`**: [the scoring pipeline. ingest.py pulls the OSM road network + crash records;
  score.py computes the per-segment Speed Safety Score; validate.py is the GO/NO-GO gate.]
- **`site/`**: [the single-file MapLibre map (index.html): score layer, threshold slider,
  per-segment cards, EN/TL copy, methodology.html. serve.py is Range-capable.]
- **`scripts/`**: [build the web layers; record the demo GIF.]
- **`tests/`**: pytest over the scoring math + invariants, plus `e2e.sh`, a [N]-check behavioral
  suite that drives the live map.

## What this is not

- Not a verdict on any road. A high score is a prompt for engineering review, never an accusation.
- Not a claim about any driver or operator. The score has no person-level input [confirm].
- Not a crash predictor or a real-time hazard feed. It is a standing measurement from past data.
- Not a substitute for DPWH / MMDA / LTO road-safety assessments. It is an independent,
  reproducible screen, complementary to and never a replacement for those.

## Reproduce

```bash
git clone https://github.com/xmpuspus/ai4saferroads-ph
cd ai4saferroads-ph
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

make ingest      # pull OSM roads + crash records
make score       # compute per-segment Speed Safety Score
make verify      # release gate (must return all PASS)
make test        # pytest, no network
make serve       # Range-capable dev server, then open site/index.html
```

[If a model ships, add a "Reproducible build" section with `make hash-verify` asserting the sha256.]

## Headline numbers, with footnotes

[Every number followed by its caveat in the same bullet. Compute first, then write. Examples:]
- [N segments scored across [geography]; M flagged high-risk at the published threshold.
  Counts are model estimates over the OSM segments that carried usable geometry and crash data.]
- [The score reproduces [known anchor] within [band].]

## Method in one paragraph

[One dense paragraph: the inputs, the per-segment scoring, the calibration, the one caveat.
Full algorithm and caveats on `/methodology`.]

## Policy context

[Why this matters: the contested road-safety / road-spending accountability gap. Name the actors
(DPWH, MMDA, LTO, LGUs). Conservative language throughout; every analytics surface carries the
public-records disclaimer.]

## Data files

All under `site/public/data/` (CC-BY-4.0). Every file is regenerated by `make score`.

| File | Schema | Notes |
|---|---|---|
| [`segments_score.geojson`] | [(segment_id, road_name, score, factors, length_m)] | [hash-pinned] |
| [`summary.json`] | [headline counts + provenance] | [the panel reads this] |

## Data sources (all free, all public)

- **OpenStreetMap** (ODbL): road network geometry + tags. Completeness varies by area.
- **[Crash record source]** ([license]): [what it provides]. [URL]
- **[Speed / geometry source]** ([license]): [what it provides]. [URL]
- [...]

All inputs are publicly licensed. No proprietary or restricted datasets are required.

## Roadmap (honest "not yet")

- [What is not done yet, stated plainly: coverage gaps, regions not scored, calibration anchors missing.]

## License and attribution

Code: MIT (see [`LICENSE`](LICENSE)). Data products: CC-BY-4.0.
Cite as `ai4saferroads.ph (2026), https://github.com/xmpuspus/ai4saferroads-ph`.
Required upstream attribution: [the OSM + crash-source attribution line, verbatim].
Author: Xavier Puspus.

## Citation

```bibtex
@software{puspus_ai4saferroads_ph_2026,
  author = {Puspus, Xavier},
  title  = {{ai4saferroads.ph: an open Speed Safety Score for Philippine roads}},
  year   = {2026},
  url    = {https://github.com/xmpuspus/ai4saferroads-ph}
}
```

[`CITATION.cff`](CITATION.cff) is the machine-readable form. A versioned Zenodo DOI is minted at each tagged release.

## Public-record disclaimer

> All data sourced from public records. ai4saferroads.ph computes statistical indicators only.
> Specific allegations, if any, require independent investigation and corroboration.

## Contact and corrections

Score corrections, missing roads, methodological questions: open a GitHub issue at
https://github.com/xmpuspus/ai4saferroads-ph/issues.
```
```
```
