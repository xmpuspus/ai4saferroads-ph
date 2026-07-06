"""Correlation overlay: does speed-limit mismatch line up with wealth (or with crowding)?

Joins the per-segment network to Meta's Relative Wealth Index (RWI) on a ~1.6 km grid and
computes REAL Spearman rank correlations and Moran's I spatial autocorrelation (permutation
p-values, no fabricated numbers), then writes a bivariate choropleth GeoJSON for the map plus
a stats file. Correlation, not causation: the caveat ships with the finding.

The mismatch variable is the raw posted-over-safe GAP (km/h), not the exposure-weighted SSS.
Gap is independent of the exposure weight E, so folding WorldPop population density into E
(build/overlay/enrich_worldpop.py) cannot contaminate the wealth finding. The old SSS-vs-wealth
rho is kept alongside for comparison / flip-detection. Crowding uses the per-segment WorldPop
density carried on the enriched network.

Run: python3 build/overlay/compute_overlay.py [manila cebu davao ...]
Needs the enriched network (build/_fullnet/sss_segments_<key>.geojson) + build/overlay/<cc>_rwi.csv.
"""

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
WEBDATA = ROOT / "build" / "web" / "data"
FULLNET = ROOT / "build" / "_fullnet"
OVL = ROOT / "build" / "overlay"

# city -> (RWI country csv, bbox S,W,N,E)  bboxes mirror sss_pipeline.CITIES
sys.path.insert(0, str(ROOT / "build"))
from sss_pipeline import CITIES  # noqa: E402

RWI = {}  # all cities are PH -> phl_rwi.csv (override per-key if needed)
STEP = 0.015  # ~1.6 km grid cells
MIN_LEN = 250.0  # require >=250 m of real-posted road in a cell to score it
# Joshua Stevens bivariate palette (rows = SSS mismatch low->high, cols = wealth low->high)
BIV = [
    ["#e8e8e8", "#ace4e4", "#5ac8c8"],
    ["#dfb0d6", "#a5add3", "#5698b9"],
    ["#be64ac", "#8c62aa", "#3b4994"],
]


def seglen(coords):
    d = 0.0
    for a, b in zip(coords, coords[1:]):
        dx = (a[0] - b[0]) * math.cos(math.radians((a[1] + b[1]) / 2))
        dy = a[1] - b[1]
        d += math.hypot(dx, dy) * 111320
    return d


def terciles(vals):
    q1, q2 = np.quantile(vals, [1 / 3, 2 / 3])
    return q1, q2


def t_of(v, q1, q2):
    return 0 if v <= q1 else (1 if v <= q2 else 2)


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p(x, y, stat_fn, observed, k=999, seed_vals=None):
    # deterministic permutation p-value (no Math.random equivalent issues): rotate y
    n = len(y)
    count = 0
    for shift in range(1, k + 1):
        yp = np.roll(y, (shift * 7919) % n)
        if abs(stat_fn(x, yp)) >= abs(observed) - 1e-12:
            count += 1
    return (count + 1) / (k + 1)


def morans_i(cells, vals):
    # queen contiguity on integer grid indices (i,j)
    idx = {c: k for k, c in enumerate(cells)}
    n = len(cells)
    x = np.array(vals, float)
    xb = x.mean()
    z = x - xb
    num = 0.0
    W = 0.0
    for k, (i, j) in enumerate(cells):
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                nb = (i + di, j + dj)
                if nb in idx:
                    num += z[k] * z[idx[nb]]
                    W += 1
    den = (z**2).sum()
    if W == 0 or den == 0:
        return 0.0
    return (n / W) * (num / den)


def build_city(key):
    seg_p = FULLNET / f"sss_segments_{key}.geojson"
    rwi_p = OVL / f"{RWI.get(key, 'phl')}_rwi.csv"
    if not seg_p.exists() or not rwi_p.exists():
        print(f"[skip] {key}: missing {seg_p.name} or {rwi_p.name}")
        return None
    s, w, n, e = CITIES[key]["bbox"]

    # 1) aggregate REAL-POSTED segments to grid cells (length-weighted means of gap, sss, density)
    fc = json.loads(seg_p.read_text())
    acc = {}  # (i,j) -> [gap*L, sss*L, dens*L, Lsum]
    for f in fc["features"]:
        p = f["properties"]
        if p.get("posted_imputed") is not False:  # only real OSM posted limits
            continue
        coords = f["geometry"]["coordinates"]
        if len(coords) < 2:
            continue
        mid = coords[len(coords) // 2]
        lon, lat = mid
        i, j = int((lat - s) / STEP), int((lon - w) / STEP)
        L = seglen(coords) or 1.0
        a = acc.setdefault((i, j), [0.0, 0.0, 0.0, 0.0])
        a[0] += max(0, p["gap"]) * L
        a[1] += p["sss"] * L
        a[2] += p.get("pop_density", 0.0) * L
        a[3] += L

    # 2) RWI points in bbox
    pts = []
    with open(rwi_p) as fh:
        for row in csv.DictReader(fh):
            la, lo = float(row["latitude"]), float(row["longitude"])
            if s <= la <= n and w <= lo <= e:
                pts.append((la, lo, float(row["rwi"])))
    if not pts:
        print(f"[skip] {key}: no RWI points in bbox")
        return None
    plat = np.array([p[0] for p in pts])
    plon = np.array([p[1] for p in pts])
    prwi = np.array([p[2] for p in pts])

    # 3) per qualifying cell: mean gap / sss / density + nearest-RWI
    cells, gap_v, sss_v, dens_v, rwi_v = [], [], [], [], []
    for (i, j), (gsum, ssum, dsum, lsum) in acc.items():
        if lsum < MIN_LEN:
            continue
        clat = s + (i + 0.5) * STEP
        clon = w + (j + 0.5) * STEP
        d2 = (plat - clat) ** 2 + (plon - clon) ** 2
        cells.append((i, j))
        gap_v.append(gsum / lsum)
        sss_v.append(ssum / lsum)
        dens_v.append(dsum / lsum)
        rwi_v.append(float(prwi[int(d2.argmin())]))

    nclen = len(cells)
    if nclen < 12:
        print(f"[skip] {key}: only {nclen} qualifying cells")
        return None
    gap_a, sss_a, dens_a, rwi_a = (
        np.array(gap_v),
        np.array(sss_v),
        np.array(dens_v),
        np.array(rwi_v),
    )

    # 4) statistics (real, computed). Primary wealth finding uses GAP (E-independent).
    rho = spearman(gap_a, rwi_a)  # mismatch (gap) vs wealth  <- finding A
    p_rho = perm_p(gap_a, rwi_a, spearman, rho)
    rho_sss = spearman(sss_a, rwi_a)  # exposure-weighted SSS vs wealth (compare)
    p_sss = perm_p(sss_a, rwi_a, spearman, rho_sss)
    rho_dens = spearman(gap_a, dens_a)  # mismatch (gap) vs crowding  <- new axis
    p_dens = perm_p(gap_a, dens_a, spearman, rho_dens)
    moran = morans_i(cells, gap_v)  # spatial clustering of the mismatch
    p_moran = perm_p(
        np.arange(nclen, dtype=float),
        gap_a,
        lambda a, b: morans_i(cells, list(b)),
        moran,
        k=199,
    )

    # 5) bivariate classes + GeoJSON cells (mismatch gap x wealth, and mismatch gap x crowding)
    g1, g2 = terciles(gap_a)
    r1, r2 = terciles(rwi_a)
    d1, d2 = terciles(dens_a)
    feats = []
    for (i, j), gv, sv, dv, rv in zip(cells, gap_v, sss_v, dens_v, rwi_v):
        gt, rt, dt = t_of(gv, g1, g2), t_of(rv, r1, r2), t_of(dv, d1, d2)
        x0, y0 = w + j * STEP, s + i * STEP
        feats.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [x0, y0],
                            [x0 + STEP, y0],
                            [x0 + STEP, y0 + STEP],
                            [x0, y0 + STEP],
                            [x0, y0],
                        ]
                    ],
                },
                "properties": {
                    "gap": round(gv, 1),
                    "sss": round(sv, 1),
                    "rwi": round(rv, 3),
                    "pop_density": round(dv, 0),
                    "sss_t": gt,
                    "rwi_t": rt,
                    "cls": gt * 3 + rt,
                    "color": BIV[gt][rt],
                    "crowd_t": gt * 3 + dt,
                    "color_crowd": BIV[gt][dt],
                },
            }
        )
    (WEBDATA / f"overlay_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats})
    )

    # plain-language direction (on the GAP-vs-wealth finding)
    if p_rho < 0.05 and rho < -0.15:
        direction = (
            "poorer",
            "the worst speed-limit mismatch falls in the city's lower-wealth areas",
        )
    elif p_rho < 0.05 and rho > 0.15:
        direction = (
            "wealthier",
            "the worst speed-limit mismatch falls in the city's higher-wealth areas",
        )
    else:
        direction = (
            "neither",
            "speed-limit mismatch shows no clear wealth pattern, "
            "it is spread across rich and poor areas alike",
        )
    if p_dens < 0.05 and rho_dens > 0.15:
        crowd_finding = "the worst speed-limit mismatch sits in the more crowded areas"
    elif p_dens < 0.05 and rho_dens < -0.15:
        crowd_finding = "the worst speed-limit mismatch sits in the less crowded areas"
    else:
        crowd_finding = (
            "the size of the mismatch does not track how crowded a place is, "
            "crowding decides which roads get flagged rather than how large the "
            "gap is"
        )
    stats = {
        "key": key,
        "cells": nclen,
        "step_deg": STEP,
        "spearman_rho": round(rho, 3),
        "spearman_p": round(p_rho, 4),
        "spearman_rho_sss_wealth": round(rho_sss, 3),
        "spearman_p_sss_wealth": round(p_sss, 4),
        "spearman_rho_gap_density": round(rho_dens, 3),
        "spearman_p_gap_density": round(p_dens, 4),
        "crowd_finding": crowd_finding,
        "morans_i": round(moran, 3),
        "morans_p": round(p_moran, 4),
        "rwi_points_in_bbox": len(pts),
        "direction": direction[0],
        "finding": direction[1],
        "mismatch_var": "gap_kmh",
        "biv": BIV,
    }
    (OVL / f"overlay_stats_{key}.json").write_text(json.dumps(stats, indent=2))
    print(
        f"[OK]   {key}: {nclen} cells | gap~wealth rho={rho:+.3f}(p={p_rho:.3f}) | "
        f"sss~wealth rho={rho_sss:+.3f}(p={p_sss:.3f}) | gap~dens rho={rho_dens:+.3f}(p={p_dens:.3f}) | "
        f"Moran(gap)={moran:+.3f}(p={p_moran:.3f})"
    )
    return stats


def main():
    want = [a for a in sys.argv[1:] if a in CITIES] or list(CITIES)
    for k in want:
        build_city(k)
    # rebuild the index from EVERY city that has stats on disk (incremental-safe)
    out = [
        json.loads((OVL / f"overlay_stats_{k}.json").read_text())
        for k in CITIES
        if (OVL / f"overlay_stats_{k}.json").exists()
    ]
    (WEBDATA / "overlay_index.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote overlay_index.json ({len(out)} cities)")


if __name__ == "__main__":
    main()
