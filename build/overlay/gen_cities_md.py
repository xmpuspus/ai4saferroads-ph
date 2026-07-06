"""Regenerate docs/cities.md from the per-city summaries + wealth overlay stats.

Keeps the per-city table in sync with the pipeline so every number corroborates findings.md.
Wealth rho/p are the gap-vs-wealth Spearman (the E-independent mismatch), matching findings.md.

Run: python3 build/overlay/gen_cities_md.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = ROOT / "build"
OVL = BUILD / "overlay"
DOCS = ROOT / "docs"
sys.path.insert(0, str(BUILD))
from sss_pipeline import CITIES  # noqa: E402


def main():
    rows = []
    tot = {"scored": 0, "real": 0, "flag": 0, "vru": 0}
    for k in CITIES:
        sp = BUILD / f"sss_summary_{k}.json"
        if not sp.exists():
            continue
        s = json.loads(sp.read_text())
        st = OVL / f"overlay_stats_{k}.json"
        rho = pv = None
        if st.exists():
            d = json.loads(st.read_text())
            rho, pv = d["spearman_rho"], d["spearman_p"]
        rows.append(
            {
                "label": CITIES[k]["label"],
                "scored": s["segments_total"],
                "real": s["segments_posted_real_osm"],
                "flag": s["segments_flagged_real_posted"],
                "vru": s["vru_pois"],
                "rho": rho,
                "p": pv,
            }
        )
        for key, col in (
            ("scored", "segments_total"),
            ("real", "segments_posted_real_osm"),
            ("flag", "segments_flagged_real_posted"),
            ("vru", "vru_pois"),
        ):
            tot[key] += s[col]
    rows.sort(key=lambda r: (r["flag"], r["real"]), reverse=True)

    def fmt(v):
        return f"{v:,}"

    def rp(r):
        if r["rho"] is None:
            return "- | -"
        return f"{r['rho']:+.2f} | {r['p']:.3f}"

    lines = [
        "# Per-city numbers",
        "",
        "All 51 cities scored from live OpenStreetMap, June 2026. `Flagged` = roads with a real "
        "posted limit above the Safe System speed. `ρ` / `p` = Spearman correlation between the "
        "raw speed-limit gap (the mismatch, independent of exposure weighting) and Meta Relative "
        "Wealth Index on a ~1.6 km grid (blank where the city has too little real-posted road to "
        "grid). Reproduce with `make data`, then `python3 build/overlay/compute_overlay.py` and "
        "`python3 build/overlay/gen_cities_md.py`. See [findings.md](findings.md).",
        "",
        "| City | Streets scored | Real posted limit | Flagged | VRU sites | Wealth ρ | p |",
        "|------|---------------:|------------------:|--------:|----------:|---------:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['label']} | {fmt(r['scored'])} | {fmt(r['real'])} | "
            f"{fmt(r['flag'])} | {fmt(r['vru'])} | {rp(r)} |"
        )
    lines.append(
        f"| **All 51 cities** | **{fmt(tot['scored'])}** | **{fmt(tot['real'])}** | "
        f"**{fmt(tot['flag'])}** | **{fmt(tot['vru'])}** | | |"
    )
    lines.append("")
    (DOCS / "cities.md").write_text("\n".join(lines))
    print(
        f"wrote docs/cities.md: {len(rows)} cities, flagged total {tot['flag']:,}, "
        f"VRU {tot['vru']:,}"
    )


if __name__ == "__main__":
    main()
