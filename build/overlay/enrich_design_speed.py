"""Backfill the congestion-independent design-speed proxy (v_design) onto the already-scored
network, without a fresh multi-hour Overpass pull. Reads each city's full scored geojson,
computes v_design + design_gap from highway class + geometry (via the same design_speed() the
pipeline now uses), writes it back, re-emits the web flagged subset and per-city summary with
the new fields, then re-tiles the combined PMTiles so the map's network carries v_design.

Run: python3 build/overlay/enrich_design_speed.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "build"))
from sss_pipeline import CITIES, design_speed, finalize  # noqa: E402

FULLNET = ROOT / "build" / "_fullnet"
WEBDATA = ROOT / "build" / "web" / "data"
BUILD = ROOT / "build"


def enrich_city(key):
    fp = FULLNET / f"sss_segments_{key}.geojson"
    if not fp.exists():
        return None
    fc = json.loads(fp.read_text())
    design_gaps = []
    for f in fc["features"]:
        p = f["properties"]
        cls = p.get("highway")
        coords = f["geometry"]["coordinates"]
        vd = design_speed(cls, coords, {"name": p.get("name", "")})
        p["v_design"] = vd
        p["design_gap"] = vd - p["v_safe"]
        if p.get("sss", 0) > 0 and p.get("posted_imputed") is False:
            design_gaps.append(vd - p["v_safe"])
    fp.write_text(json.dumps(fc))

    # web flagged subset (real-posted, sss>0) now carries v_design / design_gap
    flagged = [f for f in fc["features"]
               if f["properties"]["sss"] > 0 and f["properties"]["posted_imputed"] is False]
    (WEBDATA / f"sss_flagged_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": flagged}))

    # summary: add v_design onto each headline road (match by name+sss) + a design stat block
    sp = BUILD / f"sss_summary_{key}.json"
    if sp.exists():
        summ = json.loads(sp.read_text())
        # index fullnet real-posted flagged by (name, sss) for the headline join
        idx = {}
        for f in flagged:
            pr = f["properties"]
            idx[(pr.get("name", ""), round(pr["sss"], 1))] = pr["v_design"]
        for r in summ.get("headline_priority_roads_real_posted", []):
            r["v_design"] = idx.get((r.get("name", ""), round(r.get("sss", 0), 1)))
        n = len(design_gaps)
        summ["design"] = {
            "n_flagged_real": n,
            "flagged_design_gap_positive": sum(1 for g in design_gaps if g > 0),
            "flagged_design_gap_pos_pct": round(100 * sum(1 for g in design_gaps if g > 0) / max(n, 1), 1),
            "median_design_gap": (sorted(design_gaps)[n // 2] if n else 0),
        }
        sp.write_text(json.dumps(summ, indent=2))
    return len(flagged)


def main():
    keys = list(CITIES)
    done = 0
    for k in keys:
        r = enrich_city(k)
        if r is not None:
            done += 1
            print(f"[design] {k:22s} flagged real-posted enriched: {r}")
    print(f"\nenriched {done} cities; re-tiling PMTiles + cities.json ...")
    finalize(keys)


if __name__ == "__main__":
    main()
