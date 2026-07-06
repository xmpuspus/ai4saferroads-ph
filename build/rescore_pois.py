"""Rescore cached segments after widening the POI proximity scan (sss_pipeline.pois_within),
without re-pulling OSM.

Only n150 (POIs within 150m, feeding the exposure weight E) can move: the scan bug only
misses sites in the 111-150m range, and 50m (the n50 radius that feeds v_safe/gap/R/why via
safe_speed()) always fit inside the old 3x3 window regardless (a single grid cell is ~108m+
even at PH's least favorable longitude). So v_safe, gap, R, why, v_design and design_gap are
untouched here - the fatal-risk math and the posted-vs-safe classification do not depend on
the buggy call. This is asserted, not assumed: see HARD INVARIANT below.

Reuses the WorldPop population-density blend that build/overlay/enrich_worldpop.py already
baked into build/_fullnet (the `pop_density` property per segment, and the DIV calibration
constant), so the rescored E matches the exposure model currently live on the map instead of
reverting to the older sidewalk-bonus formula build_city() computes on a fresh pull.

HARD INVARIANT: flagged status is `sss > 0 and posted_imputed is False`, and sss > 0 iff
gap > 0 (gap = v_posted - v_safe, both untouched by this script). So every flagged count must
come out byte-identical to what shipped before the rescore. Any city where it does not is a
bug in this script, not a rare edge case - abort immediately and report it; nothing is
restored (the caller re-runs from the untouched _fullnet cache).

Run:  python3 build/rescore_pois.py            # all cities
      python3 build/rescore_pois.py manila     # one city
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sss_pipeline import (  # noqa: E402
    BUILD,
    CITIES,
    FULLNET,
    WEBDATA,
    build_poi_grid,
    finalize,
    pois_within,
)

# 90th-percentile residential density calibrated once by enrich_worldpop.py
# (build/tmp/correlate-20260704T013745Z/pop_density_distribution.json). A POI-scan fix must
# not silently re-derive this - that would shift every city's score, not just the ones the
# bug touched.
DIV = 32345.2


def exposure(n150, pop_density):
    e_poi = min(n150, 5) / 5.0
    e_pop = min(pop_density / DIV, 1.0) if DIV > 0 else 0.0
    return 1.0 - (1.0 - e_poi) * (1.0 - e_pop)


def score(gap, e):
    gap_norm = min(max(0, gap), 40) / 40.0
    return round(100 * gap_norm * (0.5 + 0.5 * e), 1)


def load_poi_pts(key):
    fp = WEBDATA / f"pois_{key}.geojson"
    fc = json.loads(fp.read_text())
    pts = []
    for f in fc["features"]:
        lo, la = f["geometry"]["coordinates"]
        pts.append((la, lo, f["properties"].get("kind", "poi")))
    return pts


def rescore_city(key):
    seg_p = FULLNET / f"sss_segments_{key}.geojson"
    if not seg_p.exists():
        return None
    fc = json.loads(seg_p.read_text())
    feats = fc["features"]
    poi_pts = load_poi_pts(key)
    grid = build_poi_grid(poi_pts)

    old_flag = sum(1 for f in feats if f["properties"]["sss"] > 0)
    old_flag_real = sum(
        1
        for f in feats
        if f["properties"]["sss"] > 0 and f["properties"]["posted_imputed"] is False
    )

    changed, deltas, worst, sss_vals = 0, [], [], []
    for f in feats:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        mid_c = coords[len(coords) // 2]
        mid = (mid_c[1], mid_c[0])
        n150 = pois_within(grid, poi_pts, mid, 150)
        e = exposure(n150, p.get("pop_density", 0.0))
        new_sss = score(p["gap"], e)
        if abs(new_sss - p["sss"]) > 1e-9:
            changed += 1
            deltas.append(new_sss - p["sss"])
        p["vru_150m"] = n150
        p["exposure"] = round(e, 3)
        p["sss"] = new_sss
        sss_vals.append(new_sss)
        if new_sss > 0:
            worst.append(
                (
                    new_sss,
                    p.get("name", ""),
                    p["highway"],
                    p["v_posted"],
                    p["v_safe"],
                    p.get("fatal_reduction_pct", 0),
                    p.get("why", ""),
                    p.get("posted_imputed", False),
                )
            )

    new_flag = len(worst)
    new_flag_real = sum(1 for x in worst if not x[7])
    if new_flag != old_flag or new_flag_real != old_flag_real:
        raise SystemExit(
            f"[FAIL] {key}: flagged count moved (total {old_flag}->{new_flag}, "
            f"real-posted {old_flag_real}->{new_flag_real}) - aborting, a POI-scan rescore "
            f"must never change which segments are flagged"
        )

    seg_p.write_text(json.dumps(fc))
    flagged_feats = [
        f
        for f in feats
        if f["properties"]["sss"] > 0 and f["properties"]["posted_imputed"] is False
    ]
    (WEBDATA / f"sss_flagged_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": flagged_feats})
    )

    worst.sort(key=lambda x: x[0], reverse=True)
    flagged_real = [x for x in worst if not x[7]]
    by_name = {}
    for x in flagged_real:
        nm = x[1] or ""
        if nm and (nm not in by_name or x[0] > by_name[nm][0]):
            by_name[nm] = x
    headline = sorted(by_name.values(), key=lambda y: y[0], reverse=True)[:10]

    sp = BUILD / f"sss_summary_{key}.json"
    summ = json.loads(sp.read_text())
    old_top10 = [r["name"] for r in summ.get("headline_priority_roads_real_posted", [])]
    # counts are recompute-invariant by construction above; assert against the summary too
    assert summ["segments_total"] == len(feats), (key, "segments_total drift")
    assert summ["segments_flagged_real_posted"] == new_flag_real, (
        key,
        "flag_real drift",
    )
    assert summ["segments_flagged_sss_gt0"] == new_flag, (key, "flag drift")

    summ["sss_max"] = max(sss_vals) if sss_vals else 0
    summ["sss_mean_flagged"] = round(sum(x[0] for x in worst) / max(len(worst), 1), 1)
    new_headline = [
        {
            "sss": s,
            "name": nm,
            "class": c,
            "posted_osm": vp,
            "safe": vs,
            "fatal_reduction_pct": fr,
            "why": wy,
        }
        for (s, nm, c, vp, vs, fr, wy, _i) in headline
    ]
    # v_design rode along on headline entries (enrich_design_speed.py's join); carry it over
    vdesign = {
        (f["properties"].get("name", ""), round(f["properties"]["sss"], 1)): f[
            "properties"
        ].get("v_design")
        for f in flagged_feats
    }
    for r in new_headline:
        vd = vdesign.get((r["name"], round(r["sss"], 1)))
        if vd is not None:
            r["v_design"] = vd
    summ["headline_priority_roads_real_posted"] = new_headline
    sp.write_text(json.dumps(summ, indent=2))

    new_top10 = [r["name"] for r in new_headline]
    return {
        "key": key,
        "segments": len(feats),
        "changed": changed,
        "deltas": deltas,
        "reordered": old_top10 != new_top10,
        "old_top10": old_top10,
        "new_top10": new_top10,
    }


def main():
    want = [a for a in sys.argv[1:] if a in CITIES] or list(CITIES)
    reports = []
    for key in want:
        r = rescore_city(key)
        if r is None:
            print(f"[skip] {key}: no cached full-network geojson")
            continue
        reports.append(r)
        mean_d = sum(r["deltas"]) / len(r["deltas"]) if r["deltas"] else 0.0
        max_d = max((abs(d) for d in r["deltas"]), default=0.0)
        print(
            f"[rescore] {key:22s} {r['segments']:6d} segs | {r['changed']:5d} sss changed "
            f"| mean delta {mean_d:+.2f} | max delta {max_d:.2f} "
            f"| reordered top10: {r['reordered']}"
        )

    total_segs = sum(r["segments"] for r in reports)
    total_changed = sum(r["changed"] for r in reports)
    all_deltas = [d for r in reports for d in r["deltas"]]
    reordered_cities = [r["key"] for r in reports if r["reordered"]]
    print(
        f"\n{total_changed}/{total_segs} segments changed sss across {len(reports)} cities"
    )
    if all_deltas:
        print(
            f"mean delta {sum(all_deltas) / len(all_deltas):+.3f} | "
            f"max |delta| {max(abs(d) for d in all_deltas):.2f}"
        )
    print(f"top-10 reordered in: {reordered_cities or 'none'}")

    finalize(list(CITIES))


if __name__ == "__main__":
    main()
