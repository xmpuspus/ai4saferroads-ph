"""Re-validate against real crashes using the EXACT crash set the map ships
(crashes_manila.geojson, 2018-2020 MMDA alerts), so the displayed count and the validation
numbers share one base. Snaps each crash to its nearest scored Manila segment (<=30 m) and
reports: flagged network length share, share of snapped crashes on flagged roads, and the
crash-density vs Speed-Safety-Score rank correlation at a ~550 m grid.

Run: python3 build/overlay/validate_crashes.py
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SEG = ROOT / "build" / "_fullnet" / "sss_segments_manila.geojson"
CRASH = ROOT / "build" / "web" / "data" / "crashes_manila.geojson"
SNAP_M, CELL, MPD = 30.0, 0.0015, 111320.0


def seg_len_m(c):
    d = 0.0
    for a, b in zip(c, c[1:]):
        mlat = math.radians((a[1] + b[1]) / 2)
        d += math.hypot((a[0] - b[0]) * math.cos(mlat) * MPD, (a[1] - b[1]) * MPD)
    return d


def pt_seg_dist_m(px, py, ax, ay, bx, by):
    clat = math.cos(math.radians(py))
    Ax, Ay = (ax - px) * clat * MPD, (ay - py) * MPD
    Bx, By = (bx - px) * clat * MPD, (by - py) * MPD
    dx, dy = Bx - Ax, By - Ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(Ax, Ay)
    t = max(0.0, min(1.0, -(Ax * dx + Ay * dy) / L2))
    return math.hypot(Ax + t * dx, Ay + t * dy)


feats = json.loads(SEG.read_text())["features"]
segs, index = [], defaultdict(list)
for f in feats:
    c = f["geometry"]["coordinates"]
    if len(c) < 2:
        continue
    si = len(segs)
    segs.append({"c": c, "p": f["properties"], "len": seg_len_m(c), "n": 0})
    for x, y in c:
        index[(int(x / CELL), int(y / CELL))].append(si)

crashes = [
    f["geometry"]["coordinates"] for f in json.loads(CRASH.read_text())["features"]
]
snapped = 0
grid_crash, grid_sss = defaultdict(int), defaultdict(list)
for lo, la in crashes:
    best, bd = None, SNAP_M
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for si in index.get((int(lo / CELL) + dx, int(la / CELL) + dy), []):
                c = segs[si]["c"]
                for a, b in zip(c, c[1:]):
                    d = pt_seg_dist_m(lo, la, a[0], a[1], b[0], b[1])
                    if d < bd:
                        bd, best = d, si
    if best is not None:
        snapped += 1
        segs[best]["n"] += 1
        gk = (round(lo, 3), round(la, 3))  # ~110 m lon, coarser grid below
        grid_crash[(int(lo / 0.005), int(la / 0.005))] += 1


def is_flag(p):
    return p["sss"] > 0 and p["posted_imputed"] is False


flag_len = sum(s["len"] for s in segs if is_flag(s["p"]))
tot_len = sum(s["len"] for s in segs)
flag_crashes = sum(s["n"] for s in segs if is_flag(s["p"]))

# grid Spearman: crash density (crashes per km of road in the cell) vs mean SSS, ~550 m cell,
# matching the validation method (normalised for road length so busy long roads do not dominate)
cell_sss, cell_len = defaultdict(list), defaultdict(float)
for s in segs:
    c = s["c"][len(s["c"]) // 2]
    k = (int(c[0] / 0.005), int(c[1] / 0.005))
    cell_sss[k].append(s["p"]["sss"])
    cell_len[k] += s["len"]
cells = [
    k for k in cell_sss if cell_len[k] > 200
]  # cells with enough road to be meaningful
xs = [sum(cell_sss[k]) / len(cell_sss[k]) for k in cells]
ys = [grid_crash.get(k, 0) / (cell_len[k] / 1000) for k in cells]  # crashes per km


def spearman(x, y):
    n = len(x)

    def rank(a):
        idx = sorted(range(n), key=lambda i: a[i])
        r = [0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and a[idx[j + 1]] == a[idx[i]]:
                j += 1
            for k in range(i, j + 1):
                r[idx[k]] = (i + j) / 2 + 1
            i = j + 1
        return r

    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    return num / (dx * dy) if dx and dy else 0


rho = spearman(xs, ys)


# per-bucket table (matches validation.md): flagged real-posted / real-posted not flagged /
# imputed-or-no-posted, with length (km), snapped crashes, and crashes per km
def bucket(s):
    p = s["p"]
    if p["posted_imputed"] is True:
        return "imputed"
    return "flagged" if p["sss"] > 0 else "real_not_flagged"


buckets = defaultdict(lambda: {"len": 0.0, "n": 0})
for s in segs:
    b = buckets[bucket(s)]
    b["len"] += s["len"]
    b["n"] += s["n"]
tbl = {
    k: {
        "km": round(v["len"] / 1000, 0),
        "crashes": v["n"],
        "len_pct": round(100 * v["len"] / tot_len, 1),
        "crash_pct": round(100 * v["n"] / max(snapped, 1), 1),
        "per_km": round(v["n"] / (v["len"] / 1000), 2) if v["len"] else 0,
    }
    for k, v in buckets.items()
}

res = {
    "crashes_total": len(crashes),
    "snapped_le30m": snapped,
    "snapped_pct": round(100 * snapped / len(crashes), 1),
    "flagged_len_pct": round(100 * flag_len / tot_len, 1),
    "flagged_crash_pct": round(100 * flag_crashes / max(snapped, 1), 1),
    "grid_cells": len(cells),
    "spearman_sss_vs_crashdensity": round(rho, 2),
    "buckets": tbl,
}
print(json.dumps(res, indent=2))

# --emit pins the validation numbers into a committed artifact so tests/verify_claims.py can
# recheck them in CI without the gitignored _fullnet (which this script needs to recompute).
if "--emit" in sys.argv:
    out = ROOT / "build" / "web" / "data" / "crash_validation.json"
    out.write_text(json.dumps(res, indent=2) + "\n")
    print(f"\nwrote {out}")
