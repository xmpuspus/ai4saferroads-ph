"""Rebuild crashes_manila.geojson WITH per-point properties (date, time, place, what was
involved) so the map can show a tooltip on hover. Source: MMDA traffic-alert CSV (2018-2020,
github.com/PotatoC0der/mmda_traffic_analysis). Filters to genuine vehicular crashes (drops
stalled-vehicle and other non-crash alerts) and dedupes the duplicate tweets that report the
same incident. Prints the recomputed count so copy can be corrected to it.

Run: python3 build/overlay/emit_crashes_manila.py <path-to-mmda_traffic.csv>
"""

import csv
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WEBDATA = ROOT / "build" / "web" / "data"


def find_csv():
    if len(sys.argv) > 1:
        return sys.argv[1]
    hits = sorted(glob.glob(str(ROOT / "tmp" / "verify-*" / "mmda_traffic.csv")))
    if not hits:
        sys.exit(
            "mmda_traffic.csv not found; pass the path (see research/correlate-crash-refresh.md)"
        )
    return hits[-1]


CRASH_KEYS = ("ACCIDENT", "COLLISION", "HIT", "ON FIRE", "SIDESWIPE", "SIDE SWIPE")


def is_crash(t):
    t = t.upper()
    return any(k in t for k in CRASH_KEYS)


def ok_ll(la, lo):
    return 13.5 < la < 15.5 and 120.0 < lo < 122.0


rows = list(csv.DictReader(open(find_csv())))
feats, seen, years = [], set(), set()
for r in rows:
    if not is_crash(r.get("Type", "")):
        continue
    try:
        la, lo = float(r["Latitude"]), float(r["Longitude"])
    except (TypeError, ValueError):
        continue
    if not ok_ll(la, lo):
        continue
    key = (r.get("Date"), r.get("Time"), round(la, 5), round(lo, 5), r.get("Type"))
    if key in seen:
        continue
    seen.add(key)
    d = r.get("Date") or ""
    if len(d) >= 4:
        years.add(d[:4])
    feats.append(
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lo, 6), round(la, 6)]},
            "properties": {
                "date": d,
                "time": (r.get("Time") or "").strip(),
                "place": (r.get("Location") or "").strip().title(),
                "city": (r.get("City") or "").strip(),
                "type": (r.get("Type") or "").strip().title(),
                "involved": (r.get("Involved") or "").strip().upper(),
            },
        }
    )

(WEBDATA / "crashes_manila.geojson").write_text(
    json.dumps({"type": "FeatureCollection", "features": feats})
)
print(
    f"crashes: {len(feats)} (years {min(years)}-{max(years)}) -> crashes_manila.geojson"
)
