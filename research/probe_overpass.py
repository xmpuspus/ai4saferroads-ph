"""Feasibility probe: does PH OpenStreetMap carry the road network, posted maxspeed,
functional class, and VRU POIs needed for the open-proxy Speed Safety Score?

Real probe against the live Overpass API over a Metro Manila AOI (Makati/Mandaluyong/
EDSA corridor). Saves raw JSON to research/ and prints a summary. No mock data.

Run: python3 research/probe_overpass.py
"""

import json
import sys
import time
import urllib.request
import urllib.parse
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
# AOI: south, west, north, east  (Makati CBD + EDSA corridor + Mandaluyong)
BBOX = (14.55, 121.00, 14.60, 121.06)
MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

S, W, N, E = BBOX
BB = f"{S},{W},{N},{E}"

Q_ROADS = f"""
[out:json][timeout:120];
(way["highway"]({BB}););
out tags;
"""

Q_POIS = f"""
[out:json][timeout:90];
(
  nwr["amenity"="school"]({BB});
  nwr["amenity"="marketplace"]({BB});
  nwr["amenity"="hospital"]({BB});
  nwr["amenity"="place_of_worship"]({BB});
  nwr["highway"="bus_stop"]({BB});
  nwr["railway"="station"]({BB});
);
out tags;
"""


def fetch(query, label):
    last_err = None
    for url in MIRRORS:
        try:
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "User-Agent": "ai4saferroads-ph-feasibility-probe/0.1 (personal research)"
                },
            )
            with urllib.request.urlopen(req, timeout=130) as r:
                raw = r.read().decode("utf-8", "replace")
            j = json.loads(raw)
            print(f"[OK]   {label} via {url} -> {len(j.get('elements', []))} elements")
            return j
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[miss] {label} via {url}: {e}")
            time.sleep(2)
    print(f"[FAIL] {label}: {last_err}")
    return None


def main():
    roads = fetch(Q_ROADS, "roads")
    if roads is None:
        sys.exit("Overpass roads probe failed on all mirrors")
    (OUT / "probe_overpass_roads.json").write_text(json.dumps(roads))

    ways = [e for e in roads["elements"] if e.get("type") == "way"]
    hw = Counter()
    maxspeed_present = 0
    maxspeed_vals = Counter()
    sidewalk_present = 0
    lit_present = 0
    lanes_present = 0
    name_present = 0
    for w in ways:
        t = w.get("tags", {})
        hw[t.get("highway", "?")] += 1
        if "maxspeed" in t:
            maxspeed_present += 1
            maxspeed_vals[t["maxspeed"]] += 1
        if "sidewalk" in t:
            sidewalk_present += 1
        if t.get("lit"):
            lit_present += 1
        if "lanes" in t:
            lanes_present += 1
        if "name" in t:
            name_present += 1

    total = len(ways)
    drivable = {
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "unclassified",
        "residential",
        "living_street",
        "service",
        "motorway_link",
        "trunk_link",
        "primary_link",
        "secondary_link",
        "tertiary_link",
    }
    drivable_ways = [w for w in ways if w.get("tags", {}).get("highway") in drivable]
    drivable_ms = sum(1 for w in drivable_ways if "maxspeed" in w.get("tags", {}))

    print("\n================ ROAD NETWORK PROBE ================")
    print(f"AOI bbox (S,W,N,E): {BBOX}  (~5.5km x 6.6km, Metro Manila core)")
    print(f"Total highway ways:        {total}")
    print(f"Drivable ways:             {len(drivable_ways)}")
    print(
        f"Ways with maxspeed tag:    {maxspeed_present} "
        f"({maxspeed_present / total * 100:.1f}% of all highways)"
    )
    print(
        f"Drivable w/ maxspeed:      {drivable_ms} "
        f"({drivable_ms / max(len(drivable_ways), 1) * 100:.1f}% of drivable)"
    )
    print(
        f"Ways with name:            {name_present} ({name_present / total * 100:.1f}%)"
    )
    print(f"Ways with sidewalk tag:    {sidewalk_present}")
    print(f"Ways with lanes tag:       {lanes_present}")
    print(f"Ways with lit tag:         {lit_present}")
    print("\nHighway class histogram (functional class proxy):")
    for k, v in hw.most_common():
        print(f"  {k:20s} {v}")
    print("\nTop posted maxspeed values:")
    for k, v in maxspeed_vals.most_common(15):
        print(f"  {k:12s} {v}")

    pois = fetch(Q_POIS, "pois")
    if pois is not None:
        (OUT / "probe_overpass_pois.json").write_text(json.dumps(pois))
        pc = Counter()
        for e in pois["elements"]:
            t = e.get("tags", {})
            key = t.get("amenity") or t.get("railway") or t.get("highway") or "?"
            pc[key] += 1
        print("\n================ VRU POI PROBE ================")
        for k, v in pc.most_common():
            print(f"  {k:18s} {v}")

    summary = {
        "aoi_bbox_swne": BBOX,
        "total_highway_ways": total,
        "drivable_ways": len(drivable_ways),
        "maxspeed_present": maxspeed_present,
        "maxspeed_pct_all": round(maxspeed_present / total * 100, 1),
        "drivable_maxspeed_pct": round(
            drivable_ms / max(len(drivable_ways), 1) * 100, 1
        ),
        "name_pct": round(name_present / total * 100, 1),
        "sidewalk_present": sidewalk_present,
        "lanes_present": lanes_present,
        "highway_histogram": dict(hw.most_common()),
        "maxspeed_values": dict(maxspeed_vals.most_common()),
    }
    (OUT / "probe_overpass_summary.json").write_text(json.dumps(summary, indent=2))
    print(
        f"\nSaved: probe_overpass_summary.json, probe_overpass_roads.json, "
        f"probe_overpass_pois.json in {OUT}"
    )


if __name__ == "__main__":
    main()
