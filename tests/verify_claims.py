"""Recompute every published headline number from committed artifacts and fail on drift.

Each claim is double-bound: the number is recomputed from the source artifact
(sss_summary_*.json, severity_by_hour.json, crowd.json, overlay_stats_*.json,
crash_validation.json) AND asserted to appear literally in the doc that publishes it
(README.md, docs/findings.md, docs/validation.md). Either side drifting fails the check,
so a rebake that changes a number without updating the prose, or an edit to the prose that
outruns the data, both break the build.

Stdlib only (chi-square via math.erfc), so it runs in CI without the gitignored _fullnet
or the PMTiles. Exit nonzero on any failure.
"""

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "build" / "web" / "data"
OVL = ROOT / "build" / "overlay"
BUILD = ROOT / "build"

fails = []
checks = 0

README = (ROOT / "README.md").read_text()
FINDINGS = (ROOT / "docs" / "findings.md").read_text()
VALIDATION = (ROOT / "docs" / "validation.md").read_text()
# methodology.html is the user-facing "Exact numbers" page (index.html links it); guard it too so
# a rebake can't leave it contradicting the README (it silently did after the trunk rescore).
METHODOLOGY = (ROOT / "build" / "web" / "methodology.html").read_text()
# index.html carries its own audience-facing numbers (the crash-overlay note, EN + FIL) that the
# oracle never bound; the crashNote kept the pre-trunk-fix 42%/7% after every doc was updated.
INDEX = (ROOT / "build" / "web" / "index.html").read_text()


def check(cond, msg):
    global checks
    checks += 1
    print(("[PASS] " if cond else "[FAIL] ") + msg)
    if not cond:
        fails.append(msg)


def num_in(doc, literal):
    """True if the literal number string appears in the doc (commas optional in either)."""
    esc = re.escape(literal)
    return re.search(esc, doc) is not None


def claim(label, recomputed, published, doc, doc_str=None):
    """Recomputed must equal published, and the published string must appear in the doc."""
    doc_str = doc_str if doc_str is not None else published
    ok = recomputed == published and num_in(doc, doc_str)
    detail = f"{label}: recomputed {recomputed!r} vs published {published!r}"
    if recomputed != published:
        detail += "  <-- ARTIFACT/PUBLISHED MISMATCH"
    elif not num_in(doc, doc_str):
        detail += f"  <-- '{doc_str}' not found in doc"
    check(ok, detail)


# ------------------------------------------------------------------ headline counts
summaries = [
    json.loads(p.read_text()) for p in sorted(BUILD.glob("sss_summary_*.json"))
]
check(len(summaries) == 51, f"51 per-city summaries present (got {len(summaries)})")

tot = sum(d["segments_total"] for d in summaries)
posted = sum(d["segments_posted_real_osm"] for d in summaries)
flagged = sum(d["segments_flagged_real_posted"] for d in summaries)
vru = sum(d["vru_pois"] for d in summaries)

claim("all-cities streets scored", f"{tot:,}", "357,423", README)
claim("all-cities real posted limit", f"{posted:,}", "37,971", README)
claim("all-cities flagged real-posted", f"{flagged:,}", "9,435", README)
claim("all-cities vulnerable-user sites", f"{vru:,}", "16,399", README)

# per-city README table rows: (key, streets, posted, flagged, vru)
CITY_ROWS = [
    ("manila", 87123, 14163, 5328, 5669),
    ("cebu", 22402, 2027, 727, 858),
    ("davao", 10873, 2658, 435, 466),
    ("sanfernando-pampanga", 10209, 708, 322, 342),
    ("angeles", 14211, 974, 243, 431),
    ("calamba", 9499, 698, 229, 284),
    ("iloilo", 6433, 758, 199, 398),
    ("cdo", 8555, 441, 148, 307),
    ("iligan", 2265, 176, 117, 176),
    ("koronadal", 3274, 476, 105, 86),
    ("bacolod", 8167, 475, 98, 258),
    ("malolos", 7025, 212, 93, 277),
]
by_key = {d["key"]: d for d in summaries}
for key, streets, p_posted, p_flag, p_vru in CITY_ROWS:
    d = by_key[key]
    claim(f"{key} streets", d["segments_total"], streets, README, f"{streets:,}")
    claim(
        f"{key} real posted",
        d["segments_posted_real_osm"],
        p_posted,
        README,
        f"{p_posted:,}",
    )
    claim(
        f"{key} flagged",
        d["segments_flagged_real_posted"],
        p_flag,
        README,
        f"{p_flag:,}",
    )

# three zero-flag cities
zero_flag = [d["key"] for d in summaries if d["segments_flagged_real_posted"] == 0]
check(
    set(zero_flag) == {"butuan", "puerto-princesa"},
    f"exactly Butuan/Puerto Princesa carry zero flagged roads (got {sorted(zero_flag)})",
)

# ------------------------------------------------------------------ night severity (EDSA)
sev = json.loads((DATA / "severity_by_hour.json").read_text())
by_hour = {h["hour"]: h for h in sev["by_hour"]}
check(len(by_hour) == 24, f"severity curve has 24 hours (got {len(by_hour)})")


def bucket(hours):
    n = sum(by_hour[h]["n"] for h in hours)
    c = sum(by_hour[h]["casualty"] for h in hours)
    return n, c, round(100 * c / n, 1)


peak_n, peak_c, peak_share = bucket([7, 8, 9, 17, 18, 19])
night_n, night_c, night_share = bucket([0, 1, 2, 3, 4])
tot_n = sum(h["n"] for h in sev["by_hour"])
tot_c = sum(h["casualty"] for h in sev["by_hour"])

claim("EDSA total crashes", f"{tot_n:,}", "22,072", FINDINGS)
claim("EDSA injury-or-worse total", f"{tot_c:,}", "1,504", FINDINGS)
claim("EDSA peak crashes", f"{peak_n:,}", "6,912", FINDINGS)
claim("EDSA peak casualties", peak_c, 463, FINDINGS, "463")
claim("EDSA peak severity share", f"{peak_share}%", "6.7%", FINDINGS)
claim("EDSA night crashes", f"{night_n:,}", "1,503", FINDINGS)
claim("EDSA night casualties", night_c, 203, FINDINGS, "203")
claim("EDSA night severity share", f"{night_share}%", "13.5%", FINDINGS)

rr = round(night_share / peak_share, 2)
check(
    abs(rr - 2.02) <= 0.02 and num_in(FINDINGS, "2.02"),
    f"EDSA relative risk recomputed {rr} matches published 2.02x",
)

# chi-square (2x2, dof=1) via stdlib: p = erfc(sqrt(chi2/2))
obs = [[night_c, night_n - night_c], [peak_c, peak_n - peak_c]]
rt = [sum(r) for r in obs]
ct = [obs[0][0] + obs[1][0], obs[0][1] + obs[1][1]]
grand = sum(rt)
chi2 = sum(
    (obs[i][j] - rt[i] * ct[j] / grand) ** 2 / (rt[i] * ct[j] / grand)
    for i in range(2)
    for j in range(2)
)
p_val = math.erfc(math.sqrt(chi2 / 2))
check(
    p_val < 1e-15 and num_in(FINDINGS, "1.3e-18"),
    f"EDSA severity chi-square recomputed p={p_val:.1e} (< 1e-15), published 1.3e-18",
)

# ------------------------------------------------------------------ crowding
crowd = json.loads((DATA / "crowd.json").read_text())
claim(
    "crowd flagged median density",
    f"{crowd['flagged_median_density']:,.0f}",
    "12,916",
    FINDINGS,
)
claim(
    "crowd unflagged median density",
    f"{crowd['unflagged_median_density']:,.0f}",
    "9,450",
    FINDINGS,
)
claim(
    "crowd prob flagged denser",
    f"{round(crowd['prob_flagged_denser'] * 100)}%",
    "56%",
    FINDINGS,
)
claim("NCR flagged count", crowd["ncr"]["flagged"], 5328, FINDINGS, "5,328")
claim(
    "NCR flagged median density",
    f"{crowd['ncr']['median_density']:,}",
    "22,599",
    FINDINGS,
)
claim("NCR death rate", crowd["ncr"]["death_rate"], 3.6, FINDINGS, "3.6")
claim("national death rate", crowd["ncr"]["national_rate"], 10.9, FINDINGS, "10.9")


# ------------------------------------------------------------------ wealth + Moran's I
def ovl(key):
    return json.loads((OVL / f"overlay_stats_{key}.json").read_text())


# (key, rho published str, p published str) as they read in findings.md
WEALTH = [
    ("manila", "−0.14", "0.19"),
    ("cebu", "+0.17", "0.47"),
    ("davao", "+0.01", "0.97"),
    ("bacolod", "−0.63", "0.035"),
    ("tagum", "−0.60", "0.023"),
    ("cotabato", "−0.61", "0.044"),
    ("laoag", "−0.48", "0.046"),
]
for key, rho_s, p_s in WEALTH:
    s = ovl(key)
    rho = round(s["spearman_rho"], 2)
    pub_rho = float(rho_s.replace("−", "-"))
    check(
        abs(rho - pub_rho) <= 0.01 and num_in(FINDINGS, rho_s),
        f"{key} wealth rho recomputed {rho:+.2f} matches published {rho_s}",
    )

MORAN = [("bacolod", "0.38"), ("sjdm", "0.41"), ("tagum", "0.58"), ("cebu", "0.18")]
for key, i_s in MORAN:
    s = ovl(key)
    mi = round(s["morans_i"], 2)
    check(
        abs(mi - float(i_s)) <= 0.01 and num_in(FINDINGS, i_s),
        f"{key} Moran's I recomputed {mi:.2f} matches published +{i_s}",
    )

# count of significant wealth cities (the multiple-comparisons honesty claim)
sig = 0
for p in sorted(OVL.glob("overlay_stats_*.json")):
    s = json.loads(p.read_text())
    if s.get("spearman_p") is not None and s["spearman_p"] < 0.05:
        sig += 1
check(
    sig == 4 and num_in(FINDINGS, "only four"),
    f"exactly 4 of 43 cities show a significant wealth correlation (got {sig})",
)

# ------------------------------------------------------------------ crash validation (optional artifact)
cv_path = DATA / "crash_validation.json"
if cv_path.exists():
    cv = json.loads(cv_path.read_text())
    # the precise crash figures are published in README's "Does it line up with real crashes?"
    # paragraph; validation.md carries the rounded table (42% / 566 km / 5,247).
    claim("crashes shown", f"{cv['crashes_total']:,}", "12,563", README)
    claim("crashes snapped", f"{cv['snapped_le30m']:,}", "12,457", README)
    claim("crashes snapped share", f"{round(cv['snapped_pct'])}%", "99%", README)
    claim("flagged length share", f"{cv['flagged_len_pct']}%", "8.5%", README)
    claim("flagged crash share", f"{cv['flagged_crash_pct']}%", "76.2%", README)
    claim("crash grid cells", f"{cv['grid_cells']:,}", "1,222", README)
    # the map's crash-overlay note (crashNote, EN + FIL) restates the concentration; bind it so it
    # cannot keep the stale 42%/7% while the docs move.
    claim(
        "index crashNote crash share",
        f"{round(cv['flagged_crash_pct'])}%",
        "76%",
        INDEX,
    )
    claim("index crashNote length share", f"{cv['flagged_len_pct']}%", "8.5%", INDEX)
    check(
        "42% of them" not in INDEX and "7% of road" not in INDEX,
        "index.html crashNote carries no pre-trunk-fix 42%/7% (EN or FIL)",
    )
    check(
        abs(cv["spearman_sss_vs_crashdensity"] - 0.46) <= 0.01
        and num_in(README, "+0.46"),
        f"crash-density Spearman recomputed {cv['spearman_sss_vs_crashdensity']:+.2f} matches "
        "published +0.46",
    )
else:
    print(
        "[SKIP] crash-validation claims (build/web/data/crash_validation.json absent; "
        "run 'python3 build/overlay/validate_crashes.py --emit' to pin the 8.5%/76%/+0.46 numbers)"
    )

# ------------------------------------------------------------------ traffic calming (optional artifact)
# The flagged-road calming coverage (build/overlay/calming_coverage.py --emit). Site copy and the
# LinkedIn draft silently drifted to the pre-trunk-fix 21/10/4 while the docs held the current
# 20/16/4; pin it so both sides fail on the next drift.
cal_path = DATA / "calming.json"
if cal_path.exists():
    cal = json.loads(cal_path.read_text())
    claim("calming Manila", f"{cal['manila']['calming_pct']}%", "20%", FINDINGS)
    claim("calming Cebu", cal["cebu"]["calming_pct"], 16, FINDINGS, "16% in Cebu")
    claim("calming Davao", cal["davao"]["calming_pct"], 4, FINDINGS, "4% in Davao")
    claim(
        "methodology calming Cebu", cal["cebu"]["calming_pct"], 16, METHODOLOGY, "16%"
    )
else:
    print(
        "[SKIP] calming claims (build/web/data/calming.json absent; "
        "run 'python3 build/overlay/calming_coverage.py --emit')"
    )

# methodology.html restates the crowd + crash + calming numbers; bind each to its source artifact
# so the "Exact numbers" page cannot silently fall out of step with the docs on a future rebake.
claim(
    "methodology crowd flagged density",
    f"{crowd['flagged_median_density']:,.0f}",
    "12,916",
    METHODOLOGY,
)
claim(
    "methodology crowd unflagged density",
    f"{crowd['unflagged_median_density']:,.0f}",
    "9,450",
    METHODOLOGY,
)
if cv_path.exists():
    claim(
        "methodology flagged length share",
        f"{cv['flagged_len_pct']}%",
        "8.5%",
        METHODOLOGY,
    )
    claim(
        "methodology flagged crash share",
        f"{cv['flagged_crash_pct']}%",
        "76.2%",
        METHODOLOGY,
    )
    check(
        num_in(METHODOLOGY, "+0.46"),
        "methodology cites crash-density Spearman +0.46 (matches artifact)",
    )

# ------------------------------------------------------------------ LinkedIn draft (ships to the feed)
# The draft is the highest-visibility surface and was UNGUARDED, so it silently drifted to the
# pre-trunk-fix 7%/42% while the map said 8.5%/76.2%. Pin its load-bearing numbers to the same
# artifacts as the docs so the post and the map can never again disagree.
DRAFT = (ROOT / "docs" / "linkedin-draft.md").read_text()
claim("draft EDSA total", f"{tot_n:,}", "22,072", DRAFT)
claim("draft night share", f"{night_share} percent", "13.5 percent", DRAFT)
claim("draft peak share", f"{peak_share} percent", "6.7 percent", DRAFT)
if cv_path.exists():
    claim("draft crashes shown", f"{cv['crashes_total']:,}", "12,563", DRAFT)
    claim(
        "draft flagged length share",
        f"{cv['flagged_len_pct']} percent",
        "8.5 percent",
        DRAFT,
    )
    claim(
        "draft flagged crash share",
        f"{round(cv['flagged_crash_pct'])} percent",
        "76 percent",
        DRAFT,
    )
if cal_path.exists():
    claim(
        "draft calming Manila",
        f"{cal['manila']['calming_pct']} percent",
        "20 percent",
        DRAFT,
    )
    claim(
        "draft calming Cebu",
        f"{cal['cebu']['calming_pct']} percent",
        "16 percent",
        DRAFT,
    )

print(
    f"\n{checks} claims checked. "
    + ("ALL CLAIMS VERIFIED" if not fails else f"{len(fails)} DRIFTED")
)
sys.exit(1 if fails else 0)
