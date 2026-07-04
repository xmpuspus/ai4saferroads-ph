"""Phase 2 crowdedness + deaths analysis (the speed x crowdedness x deaths triple).

Reads the WorldPop-enriched network (build/_fullnet, carries pop_density per segment) and
the PSA region death tables, then computes, all from real data:

  1. Segment-level crowdedness: do flagged real-posted roads sit in DENSER places than
     unflagged real-posted roads? (pooled across all cities; medians + rank-biserial)
  2. Cell-level pooled: mismatch (gap) vs residential density across every gridded cell.
  3. The triple at region level: aggregate each region's flagged-road crowding + gap, join
     PSA road-death rate/100k (2022) and count (2023, land transport V01-V89). Correlate.
  4. "Fast road through the densest housing" hook: flagged real-posted segments in the top
     residential-density decile with the largest posted-over-safe gap, 3-5 named per metro,
     with lat/lon for satellite crops.

Region death data: PSA OpenSTAT (recomputed this session; IDs 0131A1ADEB2.px counts,
0163I1A0361.px rate). Ecological: deaths are by region of usual residence, not crash site.

Run: python3 build/overlay/correlate_crowd_deaths.py
"""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = ROOT / "build"
FULLNET = BUILD / "_fullnet"
WEBDATA = BUILD / "web" / "data"
OVL = BUILD / "overlay"
sys.path.insert(0, str(BUILD))
from sss_pipeline import CITIES  # noqa: E402

OUT = Path(open("/tmp/ai4sr_correlate_dir.txt").read().strip()) if Path(
    "/tmp/ai4sr_correlate_dir.txt").exists() else OVL

# city -> PSA region key (2023 17-region structure; region of usual residence)
CITY_REGION = {
    "manila": "NCR", "baguio": "CAR",
    "dagupan": "I", "laoag": "I", "vigan": "I", "urdaneta": "I",
    "tuguegarao": "II", "santiago": "II",
    "angeles": "III", "sanfernando-pampanga": "III", "malolos": "III", "sjdm": "III",
    "cabanatuan": "III", "tarlac": "III", "olongapo": "III",
    "antipolo": "IV-A", "lipa": "IV-A", "batangas": "IV-A", "lucena": "IV-A",
    "calamba": "IV-A", "dasmarinas": "IV-A",
    "puerto-princesa": "MIMAROPA",
    "naga": "V", "legazpi": "V", "sorsogon": "V",
    "iloilo": "VI", "bacolod": "VI", "roxas": "VI",
    "cebu": "VII", "dumaguete": "VII", "tagbilaran": "VII",
    "tacloban": "VIII", "ormoc": "VIII", "calbayog": "VIII",
    "zamboanga": "IX", "pagadian": "IX", "dipolog": "IX",
    "cdo": "X", "iligan": "X", "ozamiz": "X",
    "davao": "XI", "tagum": "XI", "digos": "XI", "mati": "XI",
    "gensan": "XII", "koronadal": "XII", "kidapawan": "XII",
    "butuan": "XIII", "surigao": "XIII",
    "marawi": "BARMM", "cotabato": "BARMM",
}
REGION_NAME = {
    "NCR": "NCR", "CAR": "Cordillera", "I": "Ilocos", "II": "Cagayan Valley",
    "III": "Central Luzon", "IV-A": "CALABARZON", "MIMAROPA": "MIMAROPA", "V": "Bicol",
    "VI": "Western Visayas", "VII": "Central Visayas", "VIII": "Eastern Visayas",
    "IX": "Zamboanga Pen.", "X": "Northern Mindanao", "XI": "Davao", "XII": "SOCCSKSARGEN",
    "XIII": "Caraga", "BARMM": "BARMM",
}
# PSA road-death rate/100k 2022 (0163I1A0361.px) and land-transport count 2023 (0131A1ADEB2.px)
DEATH_RATE_2022 = {"NCR": 3.6, "CAR": 11.4, "I": 16.1, "II": 22.1, "III": 11.1, "IV-A": 7.8,
                   "MIMAROPA": 13.5, "V": 12.3, "VI": 13.2, "VII": 10.3, "VIII": 11.9,
                   "IX": 11.6, "X": 15.3, "XI": 16.8, "XII": 13.1, "XIII": 16.9, "BARMM": 2.1}
DEATH_COUNT_2023 = {"NCR": 521, "CAR": 208, "I": 1010, "II": 917, "III": 1491, "IV-A": 1432,
                    "MIMAROPA": 458, "V": 833, "VI": 1109, "VII": 905, "VIII": 654, "IX": 496,
                    "X": 885, "XI": 911, "XII": 685, "XIII": 470, "BARMM": 129}


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p(x, y, observed, k=4999):
    y = np.asarray(y, float)
    n = len(y)
    cnt = sum(abs(spearman(x, np.roll(y, (sh * 7919) % n))) >= abs(observed) - 1e-12
              for sh in range(1, k + 1))
    return (cnt + 1) / (k + 1)


def seg_midpoint(coords):
    m = coords[len(coords) // 2]
    return m[1], m[0]  # lat, lon


def load_city(key):
    """Return lists of (gap, density) for real-posted flagged and real-posted unflagged."""
    p = FULLNET / f"sss_segments_{key}.geojson"
    if not p.exists():
        return None
    fc = json.loads(p.read_text())
    flagged, unflagged = [], []
    named_flagged = []
    for f in fc["features"]:
        pr = f["properties"]
        if pr.get("posted_imputed") is not False:
            continue
        dens = pr.get("pop_density", 0.0)
        if pr["sss"] > 0:
            flagged.append((pr["gap"], dens))
            if pr.get("name"):
                la, lo = seg_midpoint(f["geometry"]["coordinates"])
                named_flagged.append((pr["name"], pr["gap"], dens, pr["v_posted"],
                                      pr["v_safe"], pr["sss"], round(la, 5), round(lo, 5),
                                      pr.get("pop_density_peak", dens)))
        else:
            unflagged.append((pr["gap"], dens))
    return flagged, unflagged, named_flagged


def main():
    keys = [k for k in CITIES if (FULLNET / f"sss_segments_{k}.geojson").exists()]

    # ---- 1. segment-level: flagged vs unflagged density (pooled) ----
    flag_d, unflag_d = [], []
    per_region = {}   # region -> {"flag_dens":[], "flag_gap":[], "n_flag":0}
    per_city_metric = {}
    for k in keys:
        flagged, unflagged, _ = load_city(k)
        fd = [d for _, d in flagged]
        ud = [d for _, d in unflagged]
        fg = [g for g, _ in flagged]
        flag_d += fd
        unflag_d += ud
        reg = CITY_REGION.get(k)
        r = per_region.setdefault(reg, {"flag_dens": [], "flag_gap": [], "n_flag": 0,
                                        "cities": []})
        r["flag_dens"] += fd
        r["flag_gap"] += fg
        r["n_flag"] += len(fd)
        r["cities"].append(k)
        per_city_metric[k] = {"region": reg, "n_flag": len(fd),
                              "median_flag_density": round(st.median(fd), 0) if fd else 0,
                              "mean_gap": round(st.mean(fg), 1) if fg else 0}

    med_flag = st.median(flag_d) if flag_d else 0
    med_unflag = st.median(unflag_d) if unflag_d else 0
    # rank-biserial via Mann-Whitney U (large n -> subsample deterministically for speed)
    rng = np.random.default_rng(42)
    a = np.array(flag_d)
    b = np.array(unflag_d)
    sa = a if len(a) <= 8000 else rng.choice(a, 8000, replace=False)
    sb = b if len(b) <= 8000 else rng.choice(b, 8000, replace=False)
    # fraction of (flagged, unflagged) pairs where flagged is denser
    wins = sum(float((sb < fv).sum()) for fv in sa)
    ties = sum(float((sb == fv).sum()) for fv in sa)
    total = len(sa) * len(sb)
    prob_denser = (wins + 0.5 * ties) / total
    seg = {"n_flagged_realposted": len(flag_d), "n_unflagged_realposted": len(unflag_d),
           "median_density_flagged": round(med_flag, 0),
           "median_density_unflagged": round(med_unflag, 0),
           "prob_flagged_denser_than_unflagged": round(prob_denser, 3)}

    # ---- 2. pooled cell-level gap vs density ----
    cg, cd = [], []
    for k in keys:
        op = WEBDATA / f"overlay_{k}.geojson"
        if not op.exists():
            continue
        for f in json.loads(op.read_text())["features"]:
            cg.append(f["properties"]["gap"])
            cd.append(f["properties"].get("pop_density", 0))
    rho_cell = spearman(cg, cd)
    p_cell = perm_p(cg, cd, rho_cell)
    pooled = {"n_cells": len(cg), "rho_gap_density": round(rho_cell, 3),
              "p": round(p_cell, 4)}

    # ---- 3. region-level triple ----
    regions = []
    for reg, d in per_region.items():
        if not d["flag_dens"]:
            continue
        regions.append({
            "region": reg, "name": REGION_NAME.get(reg, reg), "cities": len(d["cities"]),
            "n_flagged": d["n_flag"],
            "median_flag_density": round(st.median(d["flag_dens"]), 0),
            "mean_gap": round(st.mean(d["flag_gap"]), 1),
            "death_rate_2022": DEATH_RATE_2022.get(reg),
            "death_count_2023": DEATH_COUNT_2023.get(reg)})
    regions.sort(key=lambda r: r["death_rate_2022"] or 0, reverse=True)
    rd = [r for r in regions if r["death_rate_2022"] is not None]
    dens_x = [r["median_flag_density"] for r in rd]
    flag_x = [r["n_flagged"] for r in rd]
    rate_y = [r["death_rate_2022"] for r in rd]
    rho_dens_death = spearman(dens_x, rate_y)
    rho_flag_death = spearman(flag_x, rate_y)
    triple = {"n_regions": len(rd),
              "rho_flagdensity_vs_deathrate": round(rho_dens_death, 3),
              "p_flagdensity_vs_deathrate": round(perm_p(dens_x, rate_y, rho_dens_death), 4),
              "rho_nflagged_vs_deathrate": round(rho_flag_death, 3),
              "p_nflagged_vs_deathrate": round(perm_p(flag_x, rate_y, rho_flag_death), 4)}

    # ---- 4. fast-road-through-densest-housing hook ----
    dens_all = np.array([d for _, d in
                         [(g, d) for k in keys for g, d in (load_city(k)[0] or [])]])
    decile9 = float(np.percentile(dens_all, 90)) if len(dens_all) else 0
    hooks = {}
    for k in ("manila", "cebu", "davao", "cdo", "iloilo", "bacolod", "cagayan", "antipolo"):
        if k not in keys:
            continue
        _, _, named = load_city(k)
        # in top decile of density AND meaningful gap, dedup by name keeping max gap
        cand = [x for x in named if x[2] >= decile9 and x[1] >= 20]
        by_name = {}
        for x in cand:
            nm = x[0]
            if nm not in by_name or x[1] > by_name[nm][1]:
                by_name[nm] = x
        top = sorted(by_name.values(), key=lambda x: (x[1], x[2]), reverse=True)[:5]
        hooks[k] = [{"road": x[0], "gap_kmh": x[1], "density_km2": round(x[2], 0),
                     "posted": x[3], "safe": x[4], "sss": x[5], "lat": x[6], "lon": x[7],
                     "density_peak_km2": round(x[8], 0)} for x in top]

    result = {"segment_crowding": seg, "pooled_cell": pooled,
              "density_decile90_km2": round(decile9, 0),
              "triple_region": triple, "regions": regions,
              "fast_road_dense_housing": hooks,
              "caveats": ["Correlation, not causation.",
                          "Region deaths are by usual residence, not crash location.",
                          "WorldPop constrained counts residents, not daytime foot traffic.",
                          "City road networks are urban-core AOIs, not whole provinces."]}
    (OUT / "crowd_deaths_stats.json").write_text(json.dumps(result, indent=2))

    # console
    print("=== 1. SEGMENT CROWDING (flagged vs unflagged, real-posted, pooled) ===")
    print(f"  flagged median density   {seg['median_density_flagged']:>8.0f}/km2  (n={seg['n_flagged_realposted']:,})")
    print(f"  unflagged median density {seg['median_density_unflagged']:>8.0f}/km2  (n={seg['n_unflagged_realposted']:,})")
    print(f"  P(flagged denser than unflagged) = {seg['prob_flagged_denser_than_unflagged']}")
    print(f"=== 2. POOLED CELL gap~density: rho={pooled['rho_gap_density']:+.3f} p={pooled['p']:.4f} (n={pooled['n_cells']}) ===")
    print(f"=== 3. TRIPLE (region, n={triple['n_regions']}) ===")
    print(f"  flagged-road density vs death rate: rho={triple['rho_flagdensity_vs_deathrate']:+.3f} p={triple['p_flagdensity_vs_deathrate']:.3f}")
    print(f"  n flagged roads     vs death rate: rho={triple['rho_nflagged_vs_deathrate']:+.3f} p={triple['p_nflagged_vs_deathrate']:.3f}")
    print("  region                 cities nflag  medDens   gap  rate22  cnt23")
    for r in regions:
        print(f"  {r['name']:20s} {r['cities']:4d} {r['n_flagged']:6d} {r['median_flag_density']:8.0f} {r['mean_gap']:5.1f} {str(r['death_rate_2022']):>6} {str(r['death_count_2023']):>6}")
    print(f"=== 4. FAST ROAD THROUGH DENSEST HOUSING (top-decile density>= {decile9:.0f}/km2) ===")
    for k, lst in hooks.items():
        if lst:
            print(f"  {k}:")
            for h in lst:
                print(f"     {h['road'][:34]:34s} gap {h['gap_kmh']:+3d} ({h['posted']}->{h['safe']}) dens {h['density_km2']:.0f}/km2 @ {h['lat']},{h['lon']}")
    print(f"\nwrote {OUT/'crowd_deaths_stats.json'}")


if __name__ == "__main__":
    main()
