"""Apply the segregated-busway guard to the already-scored network without re-pulling OSM.

The pipeline now guards busways at classification time (build/sss_pipeline.py safe_speed), but
the scored network on disk predates that guard. The enriched network does not carry the raw
OSM bus/psv tags, so this stage uses the road name (EDSA Busway, *BRT*) to zero the score on
segregated bus lanes, then rebuilds the affected city's flagged geojson and summary counts so
every artifact stays self-consistent. Idempotent.

Run: python3 build/overlay/fix_busway.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = ROOT / "build"
FULLNET = BUILD / "_fullnet"
WEBDATA = BUILD / "web" / "data"
sys.path.insert(0, str(BUILD))
from sss_pipeline import CITIES  # noqa: E402

BUSWAY = re.compile(r"\b(busway|bus rapid|brt)\b", re.I)


def resummarize(key, feats):
    """Rebuild the flagged geojson + summary counts from the (possibly edited) features."""
    worst, sss_vals = [], []
    cnt = {"total": 0, "imputed": 0, "gap_pos": 0, "flag": 0, "flag_real": 0}
    for f in feats:
        p = f["properties"]
        sss_vals.append(p["sss"])
        cnt["total"] += 1
        if p.get("posted_imputed"):
            cnt["imputed"] += 1
        if p["gap"] > 0:
            cnt["gap_pos"] += 1
        if p["sss"] > 0:
            cnt["flag"] += 1
            worst.append((p["sss"], p.get("name", ""), p["highway"], p["v_posted"], p["v_safe"],
                          p.get("fatal_reduction_pct", 0), p.get("why", ""),
                          p.get("posted_imputed", False)))
            if not p.get("posted_imputed"):
                cnt["flag_real"] += 1
    worst.sort(key=lambda x: x[0], reverse=True)
    flagged_real = [x for x in worst if not x[7]]
    by_name = {}
    for x in flagged_real:
        nm = x[1] or ""
        if nm and (nm not in by_name or x[0] > by_name[nm][0]):
            by_name[nm] = x
    headline = sorted(by_name.values(), key=lambda y: y[0], reverse=True)[:10]

    flagged_feats = [f for f in feats if f["properties"]["sss"] > 0
                     and f["properties"]["posted_imputed"] is False]
    (WEBDATA / f"sss_flagged_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": flagged_feats}))
    summ = json.loads((BUILD / f"sss_summary_{key}.json").read_text())
    summ["segments_flagged_sss_gt0"] = cnt["flag"]
    summ["segments_flagged_real_posted"] = cnt["flag_real"]
    summ["segments_gap_positive"] = cnt["gap_pos"]
    summ["sss_max"] = max(sss_vals) if sss_vals else 0
    summ["sss_mean_flagged"] = round(sum(x[0] for x in worst) / max(len(worst), 1), 1)
    summ["headline_priority_roads_real_posted"] = [
        {"sss": s, "name": nm, "class": c, "posted_osm": vp, "safe": vs,
         "fatal_reduction_pct": fr, "why": wy}
        for (s, nm, c, vp, vs, fr, wy, _i) in headline]
    (BUILD / f"sss_summary_{key}.json").write_text(json.dumps(summ, indent=2))
    return cnt["flag_real"]


def main():
    total_zapped = 0
    for key in CITIES:
        p = FULLNET / f"sss_segments_{key}.geojson"
        if not p.exists():
            continue
        fc = json.loads(p.read_text())
        zapped = 0
        for f in fc["features"]:
            pr = f["properties"]
            if (pr.get("highway") == "service" and pr["sss"] > 0
                    and BUSWAY.search(pr.get("name") or "")):
                pr["sss"] = 0.0
                pr["v_safe"] = 70
                pr["gap"] = pr["v_posted"] - 70
                pr["why"] = "segregated busway/BRT (no at-grade pedestrian mixing)"
                zapped += 1
        if zapped:
            p.write_text(json.dumps(fc))
            fr = resummarize(key, fc["features"])
            print(f"[fix] {key}: zeroed {zapped} busway segment(s); flagged_real now {fr}")
            total_zapped += zapped
    print(f"done: {total_zapped} segregated-busway segment(s) removed from the flagged set")


if __name__ == "__main__":
    main()
