"""Invariant checks for the Speed Safety Score outputs. Exit nonzero on any failure.

Runs against the full scored network (build/_fullnet) and confirms the deployed artifacts
exist (PMTiles, flagged subset, pois, wealth overlay). Asserts the methodology can't silently
regress: a score only where the posted limit exceeds the Safe System speed, grade-separated
roads never downgraded to a pedestrian speed, every over-posted segment carries a fatal-risk
reduction, scores in range, and the wealth correlation is a real number (not fabricated).
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "build" / "web" / "data"
FULLNET = ROOT / "build" / "_fullnet"
OVL = ROOT / "build" / "overlay"
SKIP_PMTILES = os.environ.get("E2E_SKIP_PMTILES") == "1"
fails = []


def check(cond, msg):
    print(("[PASS] " if cond else "[FAIL] ") + msg)
    if not cond:
        fails.append(msg)


cities_path = DATA / "cities.json"
check(cities_path.exists(), "cities.json exists")
cities = json.loads(cities_path.read_text()) if cities_path.exists() else []
check(len(cities) >= 1, f"cities.json lists cities (got {len(cities)})")

pmtiles_path = DATA / "sss_all.pmtiles"
if SKIP_PMTILES:
    print("[SKIP] combined PMTiles exists (E2E_SKIP_PMTILES=1)")
    print(
        "[SKIP] combined PMTiles is at least as fresh as the newest _fullnet segments"
    )
else:
    check(pmtiles_path.exists(), "combined PMTiles exists (full network render)")
    if pmtiles_path.exists() and FULLNET.exists():
        newest_seg_mtime = max(
            (p.stat().st_mtime for p in FULLNET.glob("sss_segments_*.geojson")),
            default=0,
        )
        check(
            pmtiles_path.stat().st_mtime >= newest_seg_mtime,
            "combined PMTiles is at least as fresh as the newest _fullnet segments "
            "(guards stale-tiles-beside-fresh-geojson)",
        )

for c in cities:
    key = c["key"]
    check(
        (DATA / f"sss_flagged_{key}.geojson").exists(), f"{key}: flagged subset shipped"
    )
    check((DATA / f"pois_{key}.geojson").exists(), f"{key}: pois shipped")
    seg_p = FULLNET / f"sss_segments_{key}.geojson"
    check(seg_p.exists(), f"{key}: full network geojson present")
    if not seg_p.exists():
        continue
    feats = json.loads(seg_p.read_text()).get("features", [])
    check(len(feats) > 0, f"{key}: full network has features ({len(feats)})")
    bad_score = bad_motorway = bad_red = bad_range = 0
    for f in feats:
        p = f["properties"]
        if p["sss"] > 0 and p["gap"] <= 0:
            bad_score += 1
        if p["highway"] in ("motorway", "motorway_link") and p["v_safe"] == 30:
            bad_motorway += 1
        if p["v_posted"] > p["v_safe"] and p["fatal_reduction_pct"] <= 0:
            bad_red += 1
        if not (0 <= p["sss"] <= 100) or not (0 <= p["fatal_reduction_pct"] < 100):
            bad_range += 1
    check(bad_score == 0, f"{key}: no score where gap<=0 ({bad_score})")
    check(bad_motorway == 0, f"{key}: no motorway downgraded to 30 ({bad_motorway})")
    check(
        bad_red == 0,
        f"{key}: every over-posted segment has a fatal-risk reduction ({bad_red})",
    )
    check(bad_range == 0, f"{key}: scores/reductions in range ({bad_range})")
    # wealth overlay is optional (small cities lack enough real-posted road to grid);
    # but if a city has stats, the GeoJSON it draws must ship and rho must be a real number
    st_p = OVL / f"overlay_stats_{key}.json"
    if st_p.exists():
        st = json.loads(st_p.read_text())
        check(
            (DATA / f"overlay_{key}.geojson").exists(),
            f"{key}: wealth overlay shipped (has stats)",
        )
        check(
            -1 <= st["spearman_rho"] <= 1 and 0 <= st["spearman_p"] <= 1,
            f"{key}: wealth correlation is a real value (rho={st['spearman_rho']})",
        )

print(
    f"\n{'ALL INVARIANTS PASS' if not fails else str(len(fails)) + ' INVARIANT(S) FAILED'}"
)
sys.exit(1 if fails else 0)
