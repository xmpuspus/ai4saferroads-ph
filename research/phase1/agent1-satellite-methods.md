# Satellite/built-environment crash-risk methods (2024-2026) — reproducibility scan

Research task: find recent academic methods deriving crash-risk or dangerous-road signals
from satellite imagery or open built-environment features, judge open-data reproducibility
for a Philippine speed-safety-score map (OSM speed limits + Meta RWI + WorldPop).

All sources below were fetched directly (arXiv, IEEE Xplore, Semantic Scholar, ResearchGate,
PMC, GitHub, AAAI OJS, MIT News) on 2026-07-03. Two fetches (IEEE Xplore full text,
ResearchGate PDF for the 2024 "Unveiling Roadway Hazards" paper) returned HTTP 403/empty —
those gaps are marked explicitly rather than filled with guesses.

---

## 1. IEEE "Unveiling Roadway Hazards" (item 1 of task)

**Title:** Unveiling Roadway Hazards: Enhancing Fatal Crash Risk Estimation Through
Multiscale Satellite Imagery and Self-Supervised Cross-Matching
**Authors:** Gongbo Liang, Janet Zulu, Xin Xing, Nathan Jacobs
**Venue/Year:** IEEE Journal of Selected Topics in Applied Earth Observations and Remote
Sensing (JSTARS), 2024
**URLs:**
- https://ieeexplore.ieee.org/document/10313931/ (paywalled, full text returned 403)
- https://www.researchgate.net/publication/375543736 (abstract page returned empty on fetch)
- https://www.semanticscholar.org/paper/0d8ceffb16e38c0ab898d96c2b6073856c0c8ac1
- https://ui.adsabs.harvard.edu/abs/2024IJSTA..17..535L/abstract

**Method summary:** Trains a fatal-crash classifier on satellite imagery alone (no GPS,
no road network graph). The novelty is a self-supervised pretraining task the authors call
MSCM (multi-scale cross-matching): the network learns to match/align the same ground
location across three zoom levels of satellite imagery before it ever sees a crash label,
then this pretrained backbone is fine-tuned on the classification task. The authors frame
"sole reliance on satellite imagery" as the practical advantage — usable where GPS/traffic
telemetry doesn't exist.

**Exact input features:** MSCM dataset — 240,828 satellite image tiles across 80,276
distinct locations in Texas (Gulf Coast, Hill Country, Prairies and Lakes regions), each
location captured at three resolutions (1.19 m/px, 0.60 m/px, 0.30 m/px), 768×768 px tiles.
No hand-engineered features (road width, lane count) — raw pixels only, features learned by
the CNN. Ground truth: Texas fatal-crash locations 2010-2020 (16,451 positive locations;
63,825 negative locations sampled 250-1250 m from a fatal-crash site).

**Reported accuracy:** Not confirmed independently (IEEE full text 403'd). Downstream paper
(source 2 below, from the same lab) cites this as the baseline pretraining source.

**Reproducible with open data — PARTIAL, and mainly blocked on imagery, not method:**
- The 0.3-1.2 m/px resolution is sub-meter — Sentinel-2 (10 m) is roughly 30x too coarse to
  reproduce these tiles. Would need Maxar/Airbus Pleiades-grade commercial tasking or a
  high-res national orthophoto program; the PH doesn't have a public one at this resolution.
  Esri World Imagery basemap tiles are viewable at comparable resolution in some PH cities
  but usage terms restrict bulk scraping/reprocessing for model training.
- The self-supervised pretraining task itself (multi-scale same-location matching) needs no
  crash labels and is fully reproducible on any imagery source, including free-tier
  scraped Esri/Google tiles, if resolution is adequate — this is the transferable half of
  the method.
- The fatal-crash fine-tuning stage requires PH crash-location ground truth, which doesn't
  exist at this granularity (MMDA/PNP data is aggregate, not geocoded per-crash).
- No dataset or code release found; project site (see source 2) does not link a repo for
  this specific 2024 paper.

**Map-layer idea:** Not directly portable as a labeled risk layer (no PH crash labels to
fine-tune on). The reusable piece is the pretext task: run the multi-scale cross-matching
pretraining on Esri/Sentinel-2 tiles over Metro Manila as an unsupervised "visual anomaly"
embedding, then flag road segments whose embedding is an outlier relative to neighbors —
frame as "visually unusual road environment" rather than "crash risk," since it has no
supervised crash signal to justify the latter label.

---

## 2. arXiv 2511.04886 (AAAI 2026) (item 2 of task)

**Title:** Beta Distribution Learning for Reliable Roadway Crash Risk Assessment
**Authors:** Ahmad Elallaf, Nathan Jacobs, Xinyue Ye, Mei Chen, Gongbo Liang
**Venue/Year:** Accepted to AAAI 2026 (confirmed — the arXiv PDF header itself states
"Accepted to AAAI 2026"); submitted to arXiv 2025-11-07.
**URLs:**
- https://arxiv.org/abs/2511.04886
- https://arxiv.org/html/2511.04886 (full text, used for verbatim quotes below)
- https://www.gb-liang.com/projects/betarisk (project page)

**Method summary:** Direct follow-up to source 1, from an overlapping author team
(Jacobs, Liang). Same MSCM Texas satellite dataset and the same self-supervised
pretrained weights from the 2024 IEEE paper ("weights generated by following the
pre-training procedure described in the original work," citing `liang2024unveiling`).
The contribution is architectural: instead of a point-estimate crash-risk score, the model
outputs a full Beta probability distribution (two parallel heads on a ResNet-50 backbone —
a distribution-learning head producing shape parameters α, β, and an auxiliary binary
crash/no-crash classification head), giving an uncertainty-aware risk estimate instead of a
single number. Note: an early web-search snippet surfaced a stray "four major metropolitan
areas, population ≈20 million" framing line from the intro — cross-checked against the full
text and confirmed the actual experiments run only on the Texas MSCM regions; that population
figure is scene-setting language, not a second dataset. Flagging this because it's exactly
the kind of claim this task asked to verify before repeating.

**Exact input features:** Same as source 1 — 768×768 px tiles at 1.19/0.60/0.30 m/px,
Texas fatal-crash locations 2010-2020 (16,451 positive / 63,825 negative).

**Reported metrics (verbatim from paper):** F1 = 0.576, Precision = 0.630, Recall = 0.531,
AUC = 0.866, PRC = 0.649, Expected Calibration Error = 0.088, Brier score = 0.121; claimed
17-23% recall improvement over deterministic baselines, and the ensemble variant gets "3%
higher recall... at 1/3 the computational cost" vs. a baseline ensemble.

**Reproducible with open data — PARTIAL, same blocker as source 1:** identical imagery
resolution problem (sub-meter, not available free for PH), and the project page claims the
underlying dataset ("MTSL-RoadRisk") is "publicly available for research purposes" but no
working download link was found anywhere (arXiv, project page, GitHub search) — treat that
claim as unverified. No code repo found for the Beta-head implementation itself.

**Map-layer / disagreement idea:** If PH ever gets sub-meter open imagery (e.g., a future
national orthophoto release), the Beta-distribution head is the more useful piece to copy
for a public map than a point-estimate score — it would let the map show a confidence band
on the visual-risk layer, directly comparable to how the existing Speed-Safety-Score could
carry its own uncertainty. Short of that, no near-term implementation path.

---

## 3. Unite.AI article -> underlying paper (item 3 of task)

**Article:** "AI Predicts Accident Hot-Spots From Satellite Imagery and GPS Data" — Unite.AI
(published 2021, not 2024-2026; flagging the date mismatch since the task described this as
part of the 2024-2026 sweep)
**URL:** https://www.unite.ai/ai-predicts-accident-hot-spots-from-satellite-imagery-and-gps-data/

**Underlying paper:** Inferring High-Resolution Traffic Accident Risk Maps Based on
Satellite Imagery and GPS Trajectories
**Authors:** Songtao He, Mohammad Amin Sadeghi, Sanjay Chawla, Mohammad Alizadeh, Hari
Balakrishnan, Samuel Madden — MIT CSAIL + Qatar Computing Research Institute
**Venue/Year:** ICCV 2021, pp. 11977-11985
**URLs:**
- https://openaccess.thecvf.com/content/ICCV2021/html/He_Inferring_High-Resolution_Traffic_Accident_Risk_Maps_Based_on_Satellite_Imagery_ICCV_2021_paper.html
- https://news.mit.edu/2021/deep-learning-helps-predict-traffic-crashes-1012
- Code: https://github.com/songtaohe/accidentRiskMap (GPL-3.0, code only — README is a
  placeholder/TODO, no bundled data)

**Method summary:** NOT satellite-alone — combines four inputs in one deep model: satellite
imagery (lane count, hard-shoulder presence, pedestrian density visual cues), GPS
trajectories (density/speed/direction of traffic flow), road maps, and historical accident
counts. Trained/evaluated on 2017-2018 crash data, tested on 2019-2020 outcomes across
Boston, LA, Chicago, NYC (7,488 km² total). Produces 5 m resolution risk maps — an order of
magnitude finer than prior KDE-based hotspot maps, and the paper's stated advantage over KDE
is that KDE only re-plots past crashes while this model flags locations with no recorded
crash history that later experienced one.

**Exact input features:** GPS trajectories from a proprietary 2015-2017 fleet dataset (7.6M
km of 1-second-sampled traces, not public); satellite imagery (source/resolution not
disclosed in the article); OSM-style road network; historical crash counts per city.

**Reproducible with open data — PARTIAL:** code is genuinely open (GitHub, GPL-3.0), but
the load-bearing input — dense, city-scale GPS trajectory data — is proprietary and not
substitutable with anything open at comparable density for PH cities (no PH equivalent of a
7.6M-km fleet-GPS dataset exists publicly; ride-hailing/telco data would need a commercial
deal). The satellite + road-map branches alone are reproducible, but the paper's own ablation
implies GPS is a primary risk-discriminating signal, so dropping it likely degrades results
substantially (not independently verified — the ICCV PDF text extraction failed, so this is
inferred from the abstract/description only).

**Map-layer / disagreement idea:** Without GPS, this doesn't reproduce as a crash-risk
layer. But it's useful precedent for a much simpler open-data proxy: OSM already tags
`lanes`, `shoulder`, and `sidewalk` on many PH ways — a "visual features this paper flagged
as risk-relevant, extracted from OSM tags instead of satellite CNNs" pass would approximate
20% of this paper's satellite branch for near-zero cost, and could feed a disagreement flag
("posted speed says safe, but no shoulder + high lane count").

---

## 4. 2024-2026 built-environment-from-satellite work (item 4 of task)

### 4a. Brkić, Ševrović, Medak, Miler — Sensors (Basel), 2023

**Title:** Utilizing High Resolution Satellite Imagery for Automated Road Infrastructure
Safety Assessments
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10181693/

**Method summary:** Detects iRAP (International Road Assessment Programme) star-rating
attributes directly from 0.3 m Pleiades Neo satellite tiles using a YOLOv5 object detector,
trained on 1,951 annotated images (2,515 samples) split into 20 m × 120 m road segments.

**Exact input features/outputs:** School-zone markings; four classes of pedestrian
crossings (on/off the inspected road, with/without refuge islands); divided-carriageway
presence (physical median). Reported: accuracy 0.974, precision 0.905, recall 0.864,
mAP 0.916 (mean across classes; per-class range 0.950-0.988).

**Reproducible with open data — PARTIAL, method yes / imagery no:** Pleiades Neo is
commercial tasked imagery (per-km² pricing) and the authors state outright "the data are not
publicly available due to the privacy of provided satellite imagery." The YOLOv5 recipe
itself is fully reusable — it just needs 0.3-0.5 m imagery and a hand-labeled training set
for PH road markings/medians, which is a real but bounded data-collection cost (not a method
blocker).

**Map-layer / disagreement idea:** iRAP-style "median present / absent" is exactly the kind
of counterintuitive layer the project wants — a road with a high posted speed limit AND no
median (undetected by OSM tags, which rarely encode median presence in PH data) would be a
concrete disagreement case: "Speed-Safety-Score says moderate risk, median-detection layer
says undivided high-speed road, actual risk higher."

### 4b. Najjar, Kaneko, Miyanaga — AAAI 2017 (pre-2024, included as the key
weak-supervision precedent that directly answers the "reproducible without PH crash data"
question)

**Title:** Combining Satellite Imagery and Open Data to Map Road Safety
**URL:** https://ojs.aaai.org/index.php/AAAI/article/view/11168

**Method summary (full abstract confirmed via AAAI OJS):** CNN trained on raw satellite
imagery to directly predict a 3-level road-safety score, using 647,000 NYC Police Department
traffic-accident reports (4 years) as training labels. Critically, the trained NYC model was
then applied, with no retraining, to Denver satellite imagery and compared against 3 years
of Denver PD crash data — 73% accuracy on this cross-city transfer (vs. 78% same-city).

**Exact input features:** Raw satellite pixels only, no hand-engineered features; "open
data" in the title refers to the public police accident-report datasets used as labels, not
built-environment features.

**Reproducible with open data — NO for retraining on PH data (no PH-equivalent geocoded
per-crash open dataset), PARTIAL for direct transfer:** the transferability result (NYC-
trained model scoring 73% on Denver) is the single most relevant data point in this whole
survey for a no-PH-crash-data project — it demonstrates a satellite-only risk model can
generalize across cities without local crash labels. But: (a) no code/model release found in
any search here, so the actual weights aren't reusable, and (b) Manila/Cebu street
morphology (narrow lanes, jeepney/tricycle traffic, informal roadside density) is visually
very unlike NYC/Denver, so domain transfer confidence should be treated as low even if the
paper's own transfer result looked reasonable in a US-to-US context.

**Map-layer / disagreement idea:** Strongest conceptual fit for the project's constraint
(no PH crash data), but not implementable today without the authors' model weights or a
from-scratch retrain on a source city with open per-crash geocoded data (e.g., NYC Open Data
still publishes this) followed by direct pixel-level transfer to Manila imagery — flag as a
"could pursue if reproducing the NYC training run" idea, not a quick layer.

### 4c. Jiao, Baik, Choi, Xu — arXiv 2505.06762, 2025

**Title:** Investigating Robotaxi Crash Severity with Geographical Random Forest and the
Urban Environment
**URL:** https://arxiv.org/abs/2505.06762

**Method summary:** Uses a Geographical Random Forest (GRF) — a spatially localized variant
of random forest that lets feature importance vary by location rather than fitting one
global model — to relate crash severity to built-environment context: points of interest
density, building footprints, land use, intersection density, and transit-stop proximity.
Trained on the California autonomous-vehicle collision dataset for San Francisco.

**Exact input features:** POI density, building footprints, land-use classification,
intersection density, public-transit stop proximity (feature sourcing not fully specified in
the abstract — likely municipal GIS/OSM, not satellite CNN features).

**Reproducible with open data — PARTIAL:** the built-environment features themselves (POI,
building footprint, land use, intersections, transit stops) are all derivable for PH cities
from OSM + Google/Microsoft Open Buildings + PH DOTr transit data — fully reproducible as an
unsupervised feature layer. What's not reproducible is the supervised half: PH has no
AV-collision-severity dataset (or any geocoded crash-severity dataset) to fit the GRF against,
so this can only become an unsupervised built-environment density layer, not a calibrated
severity model, unless paired with a proxy label.

**Map-layer / disagreement idea:** Compute intersection density + building density (via
Google Open Buildings, which covers the Philippines) per road segment as a standalone
"built-environment complexity" layer; flag segments where high posted speed coincides with
high intersection/building density as a disagreement case, independent of any crash-label
requirement — this is the most immediately buildable idea in the whole survey since neither
input needs proprietary data or PH crash records.

### Bonus, flagged but not fully verified: Zhang, Duan, Koutsopoulos, Zhang — KDD 2026

**Title:** Learning Multimodal Embeddings for Traffic Accident Prediction and Causal
Estimation
**URL:** https://arxiv.org/abs/2512.02920

One satellite image per road-network node, combined with road-type/weather/traffic-volume
features in a graph neural network, plus causal matching-estimator analysis, trained on 9M
accident records across six US states from "official sources." Reproducibility: NO for the
supervised/causal part (needs the 9M-record proprietary accident dataset); the satellite
node-embedding idea is conceptually reusable but under-specified in the fetched abstract —
did not verify architecture details or open-data availability beyond this. Including for
completeness only; would need the full paper (not just abstract) before acting on it.

---

## Cross-source reproducibility summary

| # | Source | Year | Satellite-only? | Needs PH crash labels? | Open-data verdict |
|---|--------|------|------------------|--------------------------|--------------------|
| 1 | Unveiling Roadway Hazards (IEEE) | 2024 | Yes | Yes (fine-tune stage) | Partial — imagery res. blocks it |
| 2 | Beta Distribution Learning (AAAI 2026) | 2025/26 | Yes | Yes (fine-tune stage) | Partial — same imagery blocker |
| 3 | He et al. (ICCV 2021, via Unite.AI) | 2021 | No (+ GPS) | Yes | Partial — code open, GPS data isn't |
| 4a | Brkić et al. (Sensors) | 2023 | Yes | No (iRAP attributes, not crash labels) | Partial — method yes, commercial imagery no |
| 4b | Najjar et al. (AAAI) | 2017 | Yes | No at inference (transfer) / Yes at training | Partial — best conceptual fit, no weights released |
| 4c | Jiao et al. (arXiv) | 2025 | No (GIS features) | Yes for severity model | Partial-to-yes for the feature layer alone |
| bonus | Zhang et al. (KDD 2026) | 2026 | Partial | Yes | No — insufficiently verified |

**Bottom line for this project:** every satellite-imagery-only crash model found (1, 2, 4b)
needs either sub-meter commercial imagery PH doesn't have publicly, or crash labels PH
doesn't have geocoded. The one path that's actually buildable this quarter with data already
in hand is 4c's built-environment recipe — intersection density + Google Open Buildings
building density per OSM road segment — as an unsupervised "complexity" layer to run against
the existing Speed-Safety-Score for disagreement flags, with 4a's iRAP median-detection idea
as a stretch goal contingent on acquiring or hand-labeling higher-resolution PH imagery.
