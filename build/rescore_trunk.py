"""Rescore cached segments after the trunk safe-speed fix, without re-pulling OSM.

Round-1 doubt-loop finding (craft critic): `safe_speed` gave every OSM `trunk` segment
v_safe=70 ("no at-grade ped mixing") BEFORE the pedestrian downgrade, so at-grade national
arterials (EDSA, Roxas, MacArthur) were structurally unflaggable while the priority list named
them. The fix (sss_pipeline.safe_speed) keeps 70 only for trunk that names itself an
expressway/flyover/viaduct, and lets the rest fall through to the arterial logic (n50>0 -> 30
pedestrian downgrade, else undivided-arterial 50). This recomputes v_safe/gap/sss for the
affected trunk segments from the cached _fullnet, keeping the data vintage so the scoreboard move
is attributable to the fix alone.

Only trunk/trunk_link segments change. HARD INVARIANT: every non-trunk segment must rescore to a
byte-identical sss (its gap is untouched); any drift is a bug in this script's exposure/score
reuse, not an edge case - abort. Flag counts DO move for trunk (that is the point), so there is no
count invariant like rescore_pois.py has.

Run:  python3 build/rescore_trunk.py            # all cities, then re-tile PMTiles
      python3 build/rescore_trunk.py manila     # one city, no re-tile
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
    build_headline,
    build_poi_grid,
    finalize,
    pois_within,
    safe_speed,
)
from rescore_pois import (  # noqa: E402
    exposure,
    load_poi_pts,
    score,
)

TRUNK = ("trunk", "trunk_link")


def rescore_city(key):
    seg_p = FULLNET / f"sss_segments_{key}.geojson"
    if not seg_p.exists():
        return None
    feats = json.loads(seg_p.read_text())["features"]
    poi_pts = load_poi_pts(key)
    grid = build_poi_grid(poi_pts)

    old_real = sum(
        1
        for f in feats
        if f["properties"]["sss"] > 0 and not f["properties"]["posted_imputed"]
    )
    trunk_changed, worst, sss_vals, gap_pos = 0, [], [], 0
    for f in feats:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        mid_c = coords[len(coords) // 2]
        mid = (mid_c[1], mid_c[0])
        n150 = pois_within(grid, poi_pts, mid, 150)
        e = exposure(n150, p.get("pop_density", 0.0))

        if p["highway"] in TRUNK:
            n50 = pois_within(grid, poi_pts, mid, 50)
            v_safe, why = safe_speed(p["highway"], n50, {"name": p.get("name", "")})
            if v_safe != p["v_safe"]:
                trunk_changed += 1
            vp = p["v_posted"]
            p["v_safe"] = v_safe
            p["gap"] = vp - v_safe
            p["R"] = round((vp / v_safe) ** 4, 2)
            p["v_design"] = p.get("v_design", v_safe)
            p["design_gap"] = p["v_design"] - v_safe
            p["recommended"] = v_safe
            p["why"] = why
            p["fatal_reduction_pct"] = (
                round((1 - (v_safe / vp) ** 4) * 100, 1) if vp > v_safe else 0.0
            )

        new_sss = score(p["gap"], e)
        # non-trunk gaps are untouched, so their score must reproduce exactly; if not, the
        # exposure/score reuse is wrong and everything downstream would be quietly off
        if p["highway"] not in TRUNK and abs(new_sss - p["sss"]) > 1e-9:
            raise SystemExit(
                f"[FAIL] {key}: non-trunk sss drift on '{p.get('name', '')}' "
                f"({p['sss']} -> {new_sss}) - exposure/score reuse is not faithful"
            )
        p["vru_150m"] = n150
        p["exposure"] = round(e, 3)
        p["sss"] = new_sss
        sss_vals.append(new_sss)
        if p["gap"] > 0:
            gap_pos += 1
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
                    p.get("v_design"),
                )
            )

    seg_p.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    flagged_feats = [
        f
        for f in feats
        if f["properties"]["sss"] > 0 and not f["properties"]["posted_imputed"]
    ]
    (WEBDATA / f"sss_flagged_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": flagged_feats})
    )

    worst.sort(key=lambda x: x[0], reverse=True)
    flagged_real = [x for x in worst if not x[7]]

    sp = BUILD / f"sss_summary_{key}.json"
    summ = json.loads(sp.read_text())
    summ["segments_gap_positive"] = gap_pos
    summ["segments_flagged_sss_gt0"] = len(worst)
    summ["segments_flagged_real_posted"] = len(flagged_real)
    summ["sss_max"] = max(sss_vals) if sss_vals else 0
    summ["sss_mean_flagged"] = round(sum(x[0] for x in worst) / max(len(worst), 1), 1)
    summ["headline_priority_roads_real_posted"] = build_headline(flagged_real)
    sp.write_text(json.dumps(summ, indent=2))
    print(
        f"  {key:22s} trunk changed {trunk_changed:4d} | flagged real "
        f"{old_real:5d} -> {len(flagged_real):5d} (+{len(flagged_real) - old_real})"
    )
    return len(flagged_real) - old_real


def main():
    keys = (
        [sys.argv[1]]
        if len(sys.argv) > 1
        else [
            p.name.split("sss_segments_")[1].split(".geojson")[0]
            for p in sorted(FULLNET.glob("sss_segments_*.geojson"))
        ]
    )
    total = 0
    for k in keys:
        d = rescore_city(k)
        if d is not None:
            total += d
    print(f"\nnet new flagged real-posted across {len(keys)} cities: +{total}")
    if len(sys.argv) <= 1:
        # rebuild cities.json (the flagged counts the map/compare panel reads) AND re-tile the
        # PMTiles - both must move with the rescore, or the UI shows stale per-city numbers
        finalize(list(CITIES))


if __name__ == "__main__":
    main()
