"""Traffic-calming coverage of the flagged roads, per city, reproducible from OSM.

For each flagged real-posted segment, is there a traffic-calming feature (hump, table,
chicane, raised crossing) within 100 m of its midpoint? Emits the share per city so the
number the docs publish ("20% of Manila's flagged roads, 16% in Cebu, 4% in Davao") is
pinned to a committed artifact instead of drifting silently after a rescore.

Inputs: build/overlay/protective/protective_<key>.json (OSM crossing/signal/calming points,
pulled once) and the gitignored build/_fullnet/sss_segments_<key>.geojson (current scores).
So this regenerates when _fullnet is present; the emitted calming.json is what ships and what
tests/verify_claims.py checks. Run: python3 build/overlay/calming_coverage.py --emit
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROT = Path(__file__).resolve().parent / "protective"
FULLNET = ROOT / "build" / "_fullnet"
OUT = ROOT / "build" / "web" / "data" / "calming.json"
M_PER_DEG = 111320.0
CELL = 0.003  # ~330 m index cell
CITIES = ["manila", "cebu", "davao"]


def dist_m(lon1, lat1, lon2, lat2):
    clat = math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot((lon1 - lon2) * clat, (lat1 - lat2)) * M_PER_DEG


def coverage(key):
    prot_p = PROT / f"protective_{key}.json"
    seg_p = FULLNET / f"sss_segments_{key}.geojson"
    if not prot_p.exists() or not seg_p.exists():
        return None
    calm = [
        (p["lon"], p["lat"])
        for p in json.loads(prot_p.read_text())
        if p["kind"] == "calming"
    ]
    ix = defaultdict(list)
    for lo, la in calm:
        ix[(int(lo / CELL), int(la / CELL))].append((lo, la))

    def near_calm(lo, la):
        ci, cj = int(lo / CELL), int(la / CELL)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for plo, pla in ix.get((ci + di, cj + dj), ()):
                    if dist_m(lo, la, plo, pla) <= 100.0:
                        return True
        return False

    feats = json.loads(seg_p.read_text())["features"]
    flagged = with_calm = 0
    for f in feats:
        p = f["properties"]
        if p.get("posted_imputed") is not False or p["sss"] <= 0:
            continue
        flagged += 1
        c = f["geometry"]["coordinates"]
        lo, la = c[len(c) // 2]
        if near_calm(lo, la):
            with_calm += 1
    return {
        "flagged": flagged,
        "with_calming_100m": with_calm,
        "calming_100m_pct": round(100 * with_calm / flagged, 1),
        "calming_pct": round(100 * with_calm / flagged),
    }


def main():
    out = {}
    for key in CITIES:
        cov = coverage(key)
        if cov is None:
            print(f"[skip] {key}: missing input (need _fullnet + protective_{key}.json)")
            continue
        out[key] = cov
        print(f"{key}: {cov['calming_100m_pct']}% of {cov['flagged']} flagged roads")
    if "--emit" in sys.argv:
        OUT.write_text(json.dumps(out, indent=2) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
