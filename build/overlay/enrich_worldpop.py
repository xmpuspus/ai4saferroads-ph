"""WorldPop population-exposure enrichment (Phase 2 crowdedness axis).

The core pipeline (build/sss_pipeline.py) stays Python-stdlib and derives the posted-limit
gap plus a POI-proximity exposure weight E. This stage layers a continuous *residential
crowdedness* term into E from WorldPop PH 2020 constrained (~90 m, people/pixel, EPSG:4326),
then recomputes the Speed Safety Score. It mirrors compute_overlay.py: a numpy/rasterio
step that runs after the stdlib pipeline, reading build/_fullnet and rewriting the enriched
network + shipped flagged geojson + per-city summary.

What changes and what does not:
  - gap, v_safe, R, fatal_reduction, why  -> unchanged (E-independent)
  - which segments flag (sss>0 <=> gap>0)  -> unchanged (E can only scale 0.5..1.0)
  - SSS magnitude, per-city top-10 ranking, sss_max, sss_mean_flagged -> recomputed
Exposure blend: E = 1 - (1-E_poi)(1-E_pop), a probabilistic OR of the POI term
(min(VRU<=150m,5)/5) and a population term (min(pop_density/DIV,1)). Either a POI cluster
or dense housing raises exposure; neither can invent risk where the gap is zero. The older
sidewalk-absent +0.2 bump is dropped (it fired on almost no segments and treated unmapped
sidewalks as present); WorldPop residential density is the better, denser exposure signal.

WorldPop constrained places people only on mapped built settlements, so it measures
*residents*, not daytime/market foot traffic. That is why the POI term is kept in the blend.

Run:  python3 build/overlay/enrich_worldpop.py            # sample -> calibrate DIV -> rescore
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = ROOT / "build"
FULLNET = BUILD / "_fullnet"
WEBDATA = BUILD / "web" / "data"
OVL = BUILD / "overlay"
TIF = Path(os.environ.get("WORLDPOP_TIF", OVL / "phl_ppp_2020_constrained.tif"))

sys.path.insert(0, str(BUILD))
from sss_pipeline import CITIES  # noqa: E402

PAD = 0.008           # degrees of raster margin around each city bbox
SAMPLE_STEP_M = 150   # drop a sample point roughly every 150 m along a segment
MAX_SAMPLES = 12      # cap samples per segment (long arterials)


def haversine(la1, lo1, la2, lo2):
    r = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = math.radians(la2 - la1), math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def densify(coords, step_m, max_pts):
    """coords are [lon,lat] pairs -> up to max_pts (lat,lon) sample points along the line."""
    pts = [(coords[0][1], coords[0][0])]
    acc = 0.0
    for (lo1, la1), (lo2, la2) in zip(coords, coords[1:]):
        d = haversine(la1, lo1, la2, lo2)
        acc += d
        if acc >= step_m:
            pts.append((la2, lo2))
            acc = 0.0
    last = (coords[-1][1], coords[-1][0])
    if pts[-1] != last:
        pts.append(last)
    if len(pts) > max_pts:  # thin evenly, keep endpoints
        idx = np.linspace(0, len(pts) - 1, max_pts).round().astype(int)
        pts = [pts[i] for i in sorted(set(idx))]
    return pts


class CityPop:
    """A WorldPop window loaded for one city bbox, with a fast 3x3-block density sampler."""

    def __init__(self, ds, bbox):
        s, w, n, e = bbox
        win = from_bounds(w - PAD, s - PAD, e + PAD, n + PAD, ds.transform)
        self.arr = ds.read(1, window=win).astype("float64")
        self.arr[self.arr < 0] = 0.0          # nodata (-99999) and negatives -> 0 residents
        self.t = ds.window_transform(win)
        self.h, self.wid = self.arr.shape
        self.px_h_m = abs(self.t.e) * 111320.0        # N-S metres per pixel
        self.inv = ~self.t

    def density(self, lat, lon):
        """Residents/km2 in the ~3x3 WorldPop cell block (~270 m) around a point, and the
        resident count in that block. Returns (density_per_km2, residents)."""
        cf, rf = self.inv * (lon, lat)
        c, r = int(cf), int(rf)
        if r < 0 or c < 0 or r >= self.h or c >= self.wid:
            return 0.0, 0.0
        r0, r1 = max(0, r - 1), min(self.h, r + 2)
        c0, c1 = max(0, c - 1), min(self.wid, c + 2)
        block = self.arr[r0:r1, c0:c1]
        people = float(block.sum())
        px_w_m = self.t.a * 111320.0 * math.cos(math.radians(lat))  # E-W metres per pixel
        area_km2 = (block.shape[0] * self.px_h_m) * (block.shape[1] * px_w_m) / 1e6
        return (people / area_km2 if area_km2 > 0 else 0.0), people


def seg_pop(citypop, coords):
    """Mean residential density along a segment (exposure) + peak density (hotspot hook)."""
    pts = densify(coords, SAMPLE_STEP_M, MAX_SAMPLES)
    dens = [citypop.density(la, lo)[0] for (la, lo) in pts]
    return (sum(dens) / len(dens) if dens else 0.0), (max(dens) if dens else 0.0)


def exposure(vru_150m, pop_density, div):
    e_poi = min(vru_150m, 5) / 5.0
    e_pop = min(pop_density / div, 1.0) if div > 0 else 0.0
    return 1.0 - (1.0 - e_poi) * (1.0 - e_pop)


def score(gap, E):
    gap_norm = min(max(0, gap), 40) / 40.0
    return round(100 * gap_norm * (0.5 + 0.5 * E), 1)


def main():
    keys = [k for k in CITIES if (FULLNET / f"sss_segments_{k}.geojson").exists()]
    ds = rasterio.open(TIF)

    # PASS 1: sample residential density for every segment; hold light arrays in memory.
    print(f"PASS 1 - sampling WorldPop for {len(keys)} cities ...")
    dens_mean = {}   # key -> list[float] aligned to feature order
    dens_peak = {}
    for k in keys:
        cp = CityPop(ds, CITIES[k]["bbox"])
        fc = json.loads((FULLNET / f"sss_segments_{k}.geojson").read_text())
        dm, dp = [], []
        for f in fc["features"]:
            c = f["geometry"]["coordinates"]
            m, pk = seg_pop(cp, c)
            dm.append(m)
            dp.append(pk)
        dens_mean[k] = dm
        dens_peak[k] = dp
        print(f"  {k:24s} {len(dm):6d} segments  median dens={np.median(dm):8.0f}/km2")

    all_d = np.array([v for k in keys for v in dens_mean[k]], float)
    pos = all_d[all_d > 0]
    pctl = {p: float(np.percentile(pos, p)) for p in (50, 75, 90, 95, 99)}
    DIV = round(pctl[90], 1)   # saturate exposure at the 90th-pctile residential density
    dump = {"n_segments": int(all_d.size), "n_pos_density": int(pos.size),
            "density_per_km2_pctiles_over_pos": {str(p): round(v, 1) for p, v in pctl.items()},
            "DIV_used": DIV, "note": "E_pop = min(pop_density/DIV, 1); DIV = 90th pctile of "
            "per-segment mean residential density over segments with any resident nearby."}
    CD = Path(open("/tmp/ai4sr_correlate_dir.txt").read().strip()) if Path(
        "/tmp/ai4sr_correlate_dir.txt").exists() else OVL
    (CD / "pop_density_distribution.json").write_text(json.dumps(dump, indent=2))
    print(f"  density pctiles/km2: {dump['density_per_km2_pctiles_over_pos']}  -> DIV={DIV}")

    # PASS 2: recompute E + SSS, rewrite enriched network + flagged geojson + summary.
    print("PASS 2 - rescoring ...")
    tot_changed = 0
    for k in keys:
        fc = json.loads((FULLNET / f"sss_segments_{k}.geojson").read_text())
        feats = fc["features"]
        dm, dp = dens_mean[k], dens_peak[k]
        worst = []
        sss_vals = []
        cnt = {"total": 0, "imputed": 0, "gap_pos": 0, "flag": 0, "flag_real": 0}
        for f, md, pk in zip(feats, dm, dp):
            p = f["properties"]
            E = exposure(p.get("vru_150m", 0), md, DIV)
            new_sss = score(p["gap"], E)
            p["exposure"] = round(E, 3)
            p["pop_density"] = round(md, 1)
            p["pop_density_peak"] = round(pk, 1)
            p["sss"] = new_sss
            sss_vals.append(new_sss)
            cnt["total"] += 1
            if p.get("posted_imputed"):
                cnt["imputed"] += 1
            if p["gap"] > 0:
                cnt["gap_pos"] += 1
            if new_sss > 0:
                cnt["flag"] += 1
                worst.append((new_sss, p.get("name", ""), p["highway"], p["v_posted"],
                              p["v_safe"], p.get("fatal_reduction_pct", 0), p.get("why", ""),
                              p.get("posted_imputed", False)))
                if not p.get("posted_imputed"):
                    cnt["flag_real"] += 1

        (FULLNET / f"sss_segments_{k}.geojson").write_text(json.dumps(fc))
        flagged_feats = [f for f in feats if f["properties"]["sss"] > 0
                         and f["properties"]["posted_imputed"] is False]
        (WEBDATA / f"sss_flagged_{k}.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": flagged_feats}))

        worst.sort(key=lambda x: x[0], reverse=True)
        flagged_real = [x for x in worst if not x[7]]
        by_name = {}
        for x in flagged_real:
            nm = x[1] or ""
            if nm and (nm not in by_name or x[0] > by_name[nm][0]):
                by_name[nm] = x
        headline = sorted(by_name.values(), key=lambda y: y[0], reverse=True)[:10]

        summ = json.loads((BUILD / f"sss_summary_{k}.json").read_text())
        # counts are E-invariant: assert, don't recompute blindly
        assert summ["segments_total"] == cnt["total"], (k, "total drift")
        assert summ["segments_flagged_real_posted"] == cnt["flag_real"], (k, "flag_real drift")
        assert summ["segments_flagged_sss_gt0"] == cnt["flag"], (k, "flag drift")
        summ["sss_max"] = max(sss_vals) if sss_vals else 0
        summ["sss_mean_flagged"] = round(sum(x[0] for x in worst) / max(len(worst), 1), 1)
        summ["exposure_model"] = "POI-proximity OR WorldPop residential density (2020 constrained)"
        summ["headline_priority_roads_real_posted"] = [
            {"sss": s, "name": nm, "class": c, "posted_osm": vp, "safe": vs,
             "fatal_reduction_pct": fr, "why": wy}
            for (s, nm, c, vp, vs, fr, wy, _i) in headline]
        (BUILD / f"sss_summary_{k}.json").write_text(json.dumps(summ, indent=2))
        tot_changed += cnt["total"]

    ds.close()
    print(f"PASS 2 done: rescored {tot_changed:,} segments across {len(keys)} cities. DIV={DIV}")


if __name__ == "__main__":
    main()
