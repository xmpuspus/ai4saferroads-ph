"""Speed Safety Score (SSS) pipeline - open-proxy, multi-city (APAC-replicable).

Pulls REAL OpenStreetMap drivable road geometry + posted maxspeed + VRU POIs for ANY
city AOI, computes the Safe System recommended speed (V_safe), the posted-limit gap, the
Nilsson excess-fatal-risk factor, a VRU exposure weight, and a 0-100 Speed Safety Score
per segment. Emits per-city GeoJSON + a cities.json index for the map.

Same config runs any Asia-Pacific city (the challenge's scalability requirement). NDA
GPS-probe data drops into the same schema (replaces maxspeed imputation, adds operating-
speed divergence). No mock data - every number is computed from live OSM.

Run:  python3 build/sss_pipeline.py            # all cities
      python3 build/sss_pipeline.py manila     # one city
Methodology + sources: ../decision/DECISION.md, ../decision/DOSSIER.md (Phase 4).
"""

import json
import math
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

DATA_DATE = date.today().isoformat()  # OSM is pulled live; stamp the snapshot date

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
WEBDATA = BUILD / "web" / "data"
WEBDATA.mkdir(parents=True, exist_ok=True)
FULLNET = (
    BUILD / "_fullnet"
)  # full scored network (local only; feeds tippecanoe + overlay)
FULLNET.mkdir(exist_ok=True)

# Each city = same method, different AOI. bbox = (south, west, north, east).
# Full urban-core extents; the road pull is tiled into a GRID x GRID mesh so Overpass
# returns each cell without timing out, then ways are merged + deduped by id.
GRID = 3


# Major Philippine cities. bbox = (south, west, north, east) around the verified downtown
# (Nominatim-geocoded). Manila + Cebu keep their wider metro extents.
def _box(lat, lon, dlat=0.055, dlon=0.05):
    return (
        round(lat - dlat, 4),
        round(lon - dlon, 4),
        round(lat + dlat, 4),
        round(lon + dlon, 4),
    )


CITIES = {
    "manila": {
        "label": "Metro Manila",
        "bbox": (14.49, 120.95, 14.69, 121.11),
        "center": [121.02, 14.59],
        "zoom": 11.6,
    },
    "cebu": {
        "label": "Cebu City",
        "bbox": (10.26, 123.84, 10.40, 123.95),
        "center": [123.89, 10.32],
        "zoom": 12.2,
    },
    "davao": {
        "label": "Davao City",
        "bbox": _box(7.0648, 125.6081),
        "center": [125.6081, 7.0648],
        "zoom": 12.4,
    },
    "zamboanga": {
        "label": "Zamboanga City",
        "bbox": _box(6.9047, 122.0765),
        "center": [122.0765, 6.9047],
        "zoom": 12.4,
    },
    "cdo": {
        "label": "Cagayan de Oro",
        "bbox": _box(8.4756, 124.6422),
        "center": [124.6422, 8.4756],
        "zoom": 12.4,
    },
    "gensan": {
        "label": "General Santos",
        "bbox": _box(6.1122, 125.1722),
        "center": [125.1722, 6.1122],
        "zoom": 12.4,
    },
    "iloilo": {
        "label": "Iloilo City",
        "bbox": _box(10.6933, 122.5733),
        "center": [122.5733, 10.6933],
        "zoom": 12.5,
    },
    "bacolod": {
        "label": "Bacolod",
        "bbox": _box(10.6763, 122.9514),
        "center": [122.9514, 10.6763],
        "zoom": 12.5,
    },
    "baguio": {
        "label": "Baguio",
        "bbox": _box(16.4180, 120.5980, 0.045, 0.045),
        "center": [120.5980, 16.4180],
        "zoom": 12.8,
    },
    "batangas": {
        "label": "Batangas City",
        "bbox": _box(13.7553, 121.0591),
        "center": [121.0591, 13.7553],
        "zoom": 12.5,
    },
    "butuan": {
        "label": "Butuan",
        "bbox": _box(8.9477, 125.5432),
        "center": [125.5432, 8.9477],
        "zoom": 12.5,
    },
    "tacloban": {
        "label": "Tacloban",
        "bbox": _box(11.2432, 125.0083),
        "center": [125.0083, 11.2432],
        "zoom": 12.6,
    },
    "puerto-princesa": {
        "label": "Puerto Princesa",
        "bbox": _box(9.7530, 118.7350, 0.06, 0.055),
        "center": [118.7350, 9.7530],
        "zoom": 12.4,
    },
    "angeles": {
        "label": "Angeles City",
        "bbox": _box(15.1500, 120.5870),
        "center": [120.5870, 15.1500],
        "zoom": 12.6,
    },
    "naga": {
        "label": "Naga City",
        "bbox": _box(13.6240, 123.1850, 0.045, 0.045),
        "center": [123.1850, 13.6240],
        "zoom": 12.8,
    },
    "legazpi": {
        "label": "Legazpi City",
        "bbox": _box(13.1389, 123.7346, 0.05, 0.05),
        "center": [123.7346, 13.1389],
        "zoom": 12.6,
    },
    "dagupan": {
        "label": "Dagupan",
        "bbox": _box(16.0430, 120.3338, 0.045, 0.045),
        "center": [120.3338, 16.0430],
        "zoom": 12.7,
    },
    "antipolo": {
        "label": "Antipolo",
        "bbox": _box(14.5872, 121.1759),
        "center": [121.1759, 14.5872],
        "zoom": 12.5,
    },
    "olongapo": {
        "label": "Olongapo",
        "bbox": _box(14.8250, 120.2778),
        "center": [120.2778, 14.8250],
        "zoom": 12.6,
    },
    "lucena": {
        "label": "Lucena City",
        "bbox": _box(13.9269, 121.6135),
        "center": [121.6135, 13.9269],
        "zoom": 12.6,
    },
    "santiago": {
        "label": "Santiago City",
        "bbox": _box(16.6916, 121.5479, 0.045, 0.045),
        "center": [121.5479, 16.6916],
        "zoom": 12.7,
    },
    "iligan": {
        "label": "Iligan City",
        "bbox": _box(8.2455, 124.2543),
        "center": [124.2543, 8.2455],
        "zoom": 12.5,
    },
    "cabanatuan": {
        "label": "Cabanatuan",
        "bbox": _box(15.4846, 120.9758),
        "center": [120.9758, 15.4846],
        "zoom": 12.6,
    },
    "tarlac": {
        "label": "Tarlac City",
        "bbox": _box(15.4861, 120.5893),
        "center": [120.5893, 15.4861],
        "zoom": 12.6,
    },
    "sanfernando-pampanga": {
        "label": "San Fernando (Pampanga)",
        "bbox": _box(15.0283, 120.6938),
        "center": [120.6938, 15.0283],
        "zoom": 12.6,
    },
    "malolos": {
        "label": "Malolos",
        "bbox": _box(14.8438, 120.8114),
        "center": [120.8114, 14.8438],
        "zoom": 12.6,
    },
    "sjdm": {
        "label": "San Jose del Monte",
        "bbox": _box(14.8102, 121.0474),
        "center": [121.0474, 14.8102],
        "zoom": 12.5,
    },
    "lipa": {
        "label": "Lipa City",
        "bbox": _box(13.9421, 121.1385),
        "center": [121.1385, 13.9421],
        "zoom": 12.5,
    },
    "calamba": {
        "label": "Calamba",
        "bbox": _box(14.2066, 121.1551),
        "center": [121.1551, 14.2066],
        "zoom": 12.6,
    },
    "dasmarinas": {
        "label": "Dasmarinas",
        "bbox": _box(14.3271, 120.9371),
        "center": [120.9371, 14.3271],
        "zoom": 12.6,
    },
    "urdaneta": {
        "label": "Urdaneta",
        "bbox": _box(15.9760, 120.5669, 0.045, 0.045),
        "center": [120.5669, 15.9760],
        "zoom": 12.7,
    },
    "laoag": {
        "label": "Laoag",
        "bbox": _box(18.1973, 120.5935, 0.045, 0.045),
        "center": [120.5935, 18.1973],
        "zoom": 12.7,
    },
    "vigan": {
        "label": "Vigan",
        "bbox": _box(17.5755, 120.3873, 0.04, 0.04),
        "center": [120.3873, 17.5755],
        "zoom": 12.9,
    },
    "tuguegarao": {
        "label": "Tuguegarao",
        "bbox": _box(17.6119, 121.7300, 0.045, 0.045),
        "center": [121.7300, 17.6119],
        "zoom": 12.7,
    },
    "sorsogon": {
        "label": "Sorsogon City",
        "bbox": _box(12.9708, 124.0053, 0.045, 0.045),
        "center": [124.0053, 12.9708],
        "zoom": 12.7,
    },
    "roxas": {
        "label": "Roxas City",
        "bbox": _box(11.5895, 122.7501),
        "center": [122.7501, 11.5895],
        "zoom": 12.6,
    },
    "dumaguete": {
        "label": "Dumaguete",
        "bbox": _box(9.3055, 123.3080, 0.045, 0.045),
        "center": [123.3080, 9.3055],
        "zoom": 12.7,
    },
    "tagbilaran": {
        "label": "Tagbilaran",
        "bbox": _box(9.6272, 123.8788, 0.045, 0.045),
        "center": [123.8788, 9.6272],
        "zoom": 12.7,
    },
    "ormoc": {
        "label": "Ormoc",
        "bbox": _box(11.0090, 124.6094),
        "center": [124.6094, 11.0090],
        "zoom": 12.6,
    },
    "calbayog": {
        "label": "Calbayog",
        "bbox": _box(12.0670, 124.5947, 0.05, 0.05),
        "center": [124.5947, 12.0670],
        "zoom": 12.6,
    },
    "cotabato": {
        "label": "Cotabato City",
        "bbox": _box(7.2238, 124.2467),
        "center": [124.2467, 7.2238],
        "zoom": 12.6,
    },
    "koronadal": {
        "label": "Koronadal",
        "bbox": _box(6.5004, 124.8435),
        "center": [124.8435, 6.5004],
        "zoom": 12.6,
    },
    "kidapawan": {
        "label": "Kidapawan",
        "bbox": _box(7.0096, 125.0905, 0.045, 0.045),
        "center": [125.0905, 7.0096],
        "zoom": 12.7,
    },
    "tagum": {
        "label": "Tagum",
        "bbox": _box(7.4471, 125.8095),
        "center": [125.8095, 7.4471],
        "zoom": 12.6,
    },
    "digos": {
        "label": "Digos",
        "bbox": _box(6.7441, 125.3555, 0.045, 0.045),
        "center": [125.3555, 6.7441],
        "zoom": 12.7,
    },
    "pagadian": {
        "label": "Pagadian",
        "bbox": _box(7.8250, 123.4366, 0.045, 0.045),
        "center": [123.4366, 7.8250],
        "zoom": 12.7,
    },
    "dipolog": {
        "label": "Dipolog",
        "bbox": _box(8.5864, 123.3449, 0.045, 0.045),
        "center": [123.3449, 8.5864],
        "zoom": 12.7,
    },
    "ozamiz": {
        "label": "Ozamiz",
        "bbox": _box(8.1470, 123.8460, 0.045, 0.045),
        "center": [123.8460, 8.1470],
        "zoom": 12.7,
    },
    "surigao": {
        "label": "Surigao City",
        "bbox": _box(9.7905, 125.4936, 0.045, 0.045),
        "center": [125.4936, 9.7905],
        "zoom": 12.7,
    },
    "marawi": {
        "label": "Marawi",
        "bbox": _box(8.0047, 124.2854, 0.045, 0.045),
        "center": [124.2854, 8.0047],
        "zoom": 12.7,
    },
    "mati": {
        "label": "Mati",
        "bbox": _box(6.9522, 126.2167, 0.045, 0.045),
        "center": [126.2167, 6.9522],
        "zoom": 12.7,
    },
}

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

DRIVABLE = {
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

# Functional-class default posted limit (km/h), used ONLY when OSM maxspeed is absent.
# Urban APAC context; flagged as imputed in output. NDA GPS-probe replaces this step.
CLASS_DEFAULT = {
    "motorway": 100,
    "motorway_link": 60,
    "trunk": 80,
    "trunk_link": 50,
    "primary": 60,
    "primary_link": 40,
    "secondary": 50,
    "secondary_link": 40,
    "tertiary": 40,
    "tertiary_link": 30,
    "unclassified": 40,
    "residential": 30,
    "living_street": 20,
    "service": 20,
}


def fetch(query, label):
    """Try every mirror over several rounds with backoff. Returns None if all rounds fail
    (the caller skips that tile) - a single flaky cell must not kill a 30-minute run."""
    last = None
    for rnd in range(3):
        for url in MIRRORS:
            try:
                data = urllib.parse.urlencode({"data": query}).encode()
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "User-Agent": "ai4saferroads-ph/0.3 (personal civic research)"
                    },
                )
                with urllib.request.urlopen(req, timeout=200) as r:
                    j = json.loads(r.read().decode("utf-8", "replace"))
                print(
                    f"[OK]   {label}: {len(j.get('elements', []))} elements via {url}"
                )
                return j
            except Exception as e:  # noqa: BLE001
                last = e
                print(f"[miss] {label} via {url} (round {rnd + 1}): {e}")
                time.sleep(
                    4 + rnd * 12
                )  # back off harder each round (429/504 recovery)
    print(f"[FAIL] {label}: {last} - skipping this tile")
    return None


PARTIAL_FAIL_THRESHOLD = (
    0.20  # abort a city if more than this fraction of its tiles failed
)


def fetch_tiled(s, w, n, e, grid, body_fn, label, out="geom"):
    """Fetch a large AOI by splitting it into grid x grid Overpass queries and merging
    unique elements by (type, id). Avoids single-query timeouts on full-city pulls."""
    seen = {}
    dlat, dlon = (n - s) / grid, (e - w) / grid
    cells = grid * grid
    failed = 0
    for i in range(grid):
        for j in range(grid):
            cs, cn = s + i * dlat, s + (i + 1) * dlat
            cw, ce = w + j * dlon, w + (j + 1) * dlon
            bb = f"{cs:.5f},{cw:.5f},{cn:.5f},{ce:.5f}"
            q = f"[out:json][timeout:120];({body_fn(bb)};);out {out};"
            jj = fetch(q, f"{label} cell {i * grid + j + 1}/{cells}")
            if jj is None:
                failed += 1
                continue  # tile failed after all retries; keep going with partial coverage
            for el in jj.get("elements", []):
                seen[(el.get("type"), el.get("id"))] = el
            time.sleep(2.0)  # be polite to the public Overpass mirrors
    fail_frac = failed / cells
    if fail_frac > PARTIAL_FAIL_THRESHOLD:
        raise SystemExit(
            f"[FAIL] {label}: {failed}/{cells} tiles failed ({fail_frac:.0%}) - "
            f"refusing to finalize this city (partial coverage over "
            f"{PARTIAL_FAIL_THRESHOLD:.0%})"
        )
    if failed:
        print(
            f"[WARN] {label}: {failed}/{cells} tiles failed ({fail_frac:.0%}) - "
            f"shipping partial coverage"
        )
    print(f"[OK]   {label}: {len(seen)} unique elements (tiled {grid}x{grid})")
    return {"elements": list(seen.values())}


def parse_maxspeed(v):
    """Return int km/h or None."""
    if not v:
        return None
    v = str(v).strip().lower()
    if v in ("none", "walk", "signals", "variable"):
        return None
    num = ""
    for ch in v:
        if ch.isdigit():
            num += ch
        elif num:
            break
    if not num:
        return None
    kmh = int(num)
    if "mph" in v:
        kmh = round(kmh * 1.60934)
    return kmh if 5 <= kmh <= 130 else None


def haversine(a, b):
    (la1, lo1), (la2, lo2) = a, b
    r = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = math.radians(la2 - la1), math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


CELL_DEG = 0.001  # POI bucket size (~111 m north-south)
M_PER_DEG_LAT = 111000.0  # metres per degree of latitude (near-constant)


def build_poi_grid(poi_pts):
    """Bucket (lat, lon, kind) points into CELL_DEG x CELL_DEG cells for fast radius scans."""
    grid = defaultdict(list)
    for i, (lat, lon, _k) in enumerate(poi_pts):
        grid[(round(lat, 3), round(lon, 3))].append(i)
    return grid


def pois_within(grid, poi_pts, mid, radius_m):
    """Count POIs within radius_m of mid=(lat,lon), scanning only the grid cells that could
    plausibly hold one. The cell span is derived from the radius (not hardcoded to 3x3) so a
    150 m call cannot miss a site that landed one cell further out than a single ~111 m
    neighbor - longitude cells shrink with cos(lat), so the lon span is computed separately."""
    la, lo = mid
    lat_span = math.ceil(radius_m / M_PER_DEG_LAT / CELL_DEG)
    lon_m_per_deg = M_PER_DEG_LAT * max(math.cos(math.radians(la)), 0.01)
    lon_span = math.ceil(radius_m / lon_m_per_deg / CELL_DEG)
    c = 0
    for i in range(-lat_span, lat_span + 1):
        for j in range(-lon_span, lon_span + 1):
            for idx in grid.get(
                (round(la + i * CELL_DEG, 3), round(lo + j * CELL_DEG, 3)), []
            ):
                plat, plon, _k = poi_pts[idx]
                if haversine(mid, (plat, plon)) <= radius_m:
                    c += 1
    return c


def safe_speed(cls, n50, t):
    """Safe System recommended speed (km/h) - transparent classifier (DOSSIER Phase 4).
    Grade-separated classes checked first so 2D POI proximity can never downgrade an
    elevated expressway to a pedestrian speed (fixes the Skyway false positive)."""
    name = str(t.get("name", "")).lower()
    # Segregated bus rapid transit / busway: physically separated from general traffic and
    # pedestrians even though OSM tags it highway=service, so it is not a ped-mixing road
    # (fixes the EDSA Busway false positive).
    if cls == "service" and (
        "busway" in name
        or "brt" in name
        or t.get("busway")
        or t.get("bus") == "designated"
        or (t.get("access") in ("no", "private") and (t.get("psv") or t.get("bus")))
    ):
        return 70, "segregated busway/BRT (no at-grade pedestrian mixing)"
    if cls in ("motorway", "motorway_link"):
        return 100, "grade-separated, no conflict"
    if cls in ("trunk", "trunk_link"):
        return 70, "trunk highway (head-on only; no at-grade ped mixing assumed)"
    if cls == "living_street":
        return 20, "living street (shared space)"
    if n50 > 0:
        return 30, f"pedestrian activity ({n50} VRU site<=50m)"
    if cls in ("residential", "service", "unclassified"):
        return 30, "local road, frontage/pedestrian mixing"
    if cls in (
        "tertiary",
        "tertiary_link",
        "secondary",
        "secondary_link",
        "primary",
        "primary_link",
    ):
        # Only a genuine divided carriageway removes side-impact conflict. one-way alone
        # does NOT mean divided (most one-way urban arterials are undivided), so default
        # arterials to the side-impact survivable speed (50) unless OSM marks them divided.
        if t.get("dual_carriageway") == "yes" or t.get("divider") not in (None, "no"):
            return 70, "divided carriageway (head-on only, no side impact)"
        return 50, "undivided arterial, side-impact intersections"
    return 50, "default urban arterial"


# Free-flow design-speed proxy (km/h): the speed the built form invites when the road is
# CLEAR. Congestion-independent, unlike the daytime operating average a jam produces - it is
# the same at 3am and at noon. From the functional-class design-speed norm (PH DPWH / AASHTO
# urban ranges), adjusted DOWN only where the alignment actually curves. Labelled a proxy:
# lanes/width would sharpen it, but OSM lane/width coverage is thin and class + alignment set
# the free-flow speed. This is the axis that answers "we only crawl at 30": the crawl is the
# jam, the road is built for this.
DESIGN_FREEFLOW = {
    "motorway": 90,
    "motorway_link": 60,
    "trunk": 70,
    "trunk_link": 55,
    "primary": 60,
    "primary_link": 45,
    "secondary": 50,
    "secondary_link": 40,
    "tertiary": 45,
    "tertiary_link": 40,
    "unclassified": 40,
    "residential": 35,
    "living_street": 15,
    "service": 25,
}


def sinuosity(coords):
    """Path length / straight-line endpoint distance. 1.0 = dead straight; higher = winding.
    coords are [lon, lat] pairs."""
    if len(coords) < 2:
        return 1.0
    path = 0.0
    for i in range(len(coords) - 1):
        path += haversine(
            (coords[i][1], coords[i][0]), (coords[i + 1][1], coords[i + 1][0])
        )
    chord = haversine((coords[0][1], coords[0][0]), (coords[-1][1], coords[-1][0]))
    return path / chord if chord > 5 else 1.0


def design_speed(cls, coords, t):
    """Free-flow design-speed proxy (km/h) the geometry invites when the road is clear.
    Segregated busways/BRT read as their high grade-separated free-flow via class; curves
    cap the achievable speed."""
    if cls == "service" and (
        "busway" in str(t.get("name", "")).lower()
        or t.get("busway")
        or t.get("bus") == "designated"
    ):
        return 60  # BRT running way, free-flowing when clear
    base = DESIGN_FREEFLOW.get(cls, 40)
    s = sinuosity(coords)
    if s >= 1.30:
        base *= 0.72  # winding: alignment physically caps speed
    elif s >= 1.10:
        base *= 0.88  # mildly curved
    return max(15, min(95, int(round(base / 5.0) * 5)))


def build_city(key, cfg):
    s, w, n, e = cfg["bbox"]
    print(f"\n########## {key} - {cfg['label']} ##########")
    roads = fetch_tiled(
        s, w, n, e, GRID, lambda bb: f"way['highway']({bb})", f"{key} roads", "geom"
    )
    pois = fetch_tiled(
        s,
        w,
        n,
        e,
        max(2, GRID - 1),
        lambda bb: (
            f"nwr['amenity'='school']({bb});nwr['amenity'='marketplace']({bb});"
            f"nwr['amenity'='hospital']({bb});nwr['amenity'='place_of_worship']({bb});"
            f"nwr['highway'='bus_stop']({bb});nwr['railway'='station']({bb})"
        ),
        f"{key} pois",
        "center",
    )

    poi_pts = []
    for el in pois["elements"]:
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        tt = el.get("tags", {})
        kind = tt.get("amenity") or tt.get("railway") or tt.get("highway") or "poi"
        poi_pts.append((lat, lon, kind))
    grid = build_poi_grid(poi_pts)

    feats, sss_vals, worst = [], [], []
    stats = Counter()
    for way in roads["elements"]:
        if way.get("type") != "way":
            continue
        t = way.get("tags", {})
        cls = t.get("highway")
        if cls not in DRIVABLE:
            continue
        geom = way.get("geometry") or []
        if len(geom) < 2:
            continue
        coords = [[p["lon"], p["lat"]] for p in geom]
        mid_node = geom[len(geom) // 2]
        mid = (mid_node["lat"], mid_node["lon"])

        v_posted = parse_maxspeed(t.get("maxspeed"))
        imputed = v_posted is None
        if imputed:
            v_posted = CLASS_DEFAULT.get(cls, 40)

        n50 = pois_within(grid, poi_pts, mid, 50)
        n150 = pois_within(grid, poi_pts, mid, 150)
        sidewalk = str(t.get("sidewalk", "")).lower()
        sidewalk_absent = sidewalk in ("no", "none")

        v_safe, why = safe_speed(cls, n50, t)
        v_design = design_speed(
            cls, coords, t
        )  # free-flow speed the built form invites when clear
        design_gap = v_design - v_safe  # congestion-independent excess over survivable
        gap = v_posted - v_safe
        R = round((v_posted / v_safe) ** 4, 2)
        E = min(n150, 5) / 5.0
        if sidewalk_absent:
            E = min(1.0, E + 0.2)
        gap_norm = min(max(0, gap), 40) / 40.0
        sss = round(100 * gap_norm * (0.5 + 0.5 * E), 1)
        fatal_red = (
            round((1 - (v_safe / v_posted) ** 4) * 100, 1) if v_posted > v_safe else 0.0
        )

        sss_vals.append(sss)
        stats["total"] += 1
        if imputed:
            stats["imputed_posted"] += 1
        if gap > 0:
            stats["gap_positive"] += 1
        if sss > 0:
            worst.append(
                (sss, t.get("name", ""), cls, v_posted, v_safe, fatal_red, why, imputed)
            )

        feats.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {
                    "city": key,
                    "name": t.get("name", ""),
                    "highway": cls,
                    "v_posted": v_posted,
                    "posted_imputed": imputed,
                    "v_safe": v_safe,
                    "gap": gap,
                    "R": R,
                    "v_design": v_design,
                    "design_gap": design_gap,
                    "exposure": round(E, 2),
                    "vru_150m": n150,
                    "sss": sss,
                    "recommended": v_safe,
                    "fatal_reduction_pct": fatal_red,
                    "why": why,
                },
            }
        )

    if stats["total"] == 0:
        raise SystemExit(
            f"[FAIL] {key}: Overpass returned 0 drivable ways "
            f"(empty/blocked response) - refusing to ship an empty city"
        )
    # full scored network stays local (feeds tippecanoe PMTiles + the wealth overlay)
    (FULLNET / f"sss_segments_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats})
    )
    # small real-posted-flagged subset ships for map interactions (search, critical mode, fly-to)
    flagged = [
        f
        for f in feats
        if f["properties"]["sss"] > 0 and f["properties"]["posted_imputed"] is False
    ]
    (WEBDATA / f"sss_flagged_{key}.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": flagged})
    )
    (WEBDATA / f"pois_{key}.geojson").write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [lo, la]},
                        "properties": {"kind": k},
                    }
                    for (la, lo, k) in poi_pts
                ],
            }
        )
    )

    worst.sort(key=lambda x: x[0], reverse=True)
    flagged = [x for x in worst if x[0] > 0]
    flagged_real = [x for x in flagged if not x[7]]
    by_name = {}
    for x in flagged_real:
        nm = x[1] or ""
        if not nm:
            continue
        if nm not in by_name or x[0] > by_name[nm][0]:
            by_name[nm] = x
    headline = sorted(by_name.values(), key=lambda y: y[0], reverse=True)[:10]

    summary = {
        "key": key,
        "label": cfg["label"],
        "center": cfg["center"],
        "zoom": cfg["zoom"],
        "data_date": DATA_DATE,
        "data_source": "OpenStreetMap via Overpass",
        "segments_total": stats["total"],
        "segments_posted_real_osm": stats["total"] - stats["imputed_posted"],
        "segments_posted_imputed": stats["imputed_posted"],
        "segments_gap_positive": stats["gap_positive"],
        "segments_flagged_sss_gt0": len(flagged),
        "segments_flagged_real_posted": len(flagged_real),
        "sss_max": max(sss_vals) if sss_vals else 0,
        "sss_mean_flagged": round(sum(x[0] for x in flagged) / max(len(flagged), 1), 1),
        "vru_pois": len(poi_pts),
        "headline_priority_roads_real_posted": [
            {
                "sss": s,
                "name": nm,
                "class": c,
                "posted_osm": vp,
                "safe": vs,
                "fatal_reduction_pct": fr,
                "why": wy,
            }
            for (s, nm, c, vp, vs, fr, wy, _i) in headline
        ],
    }
    (BUILD / f"sss_summary_{key}.json").write_text(json.dumps(summary, indent=2))

    print(
        f"  segments {stats['total']} | real-posted {summary['segments_posted_real_osm']} "
        f"| flagged(real) {len(flagged_real)} | VRU {len(poi_pts)} | max SSS {summary['sss_max']}"
    )
    for s, nm, c, vp, vs, fr, wy, _i in headline[:5]:
        print(
            f"    SSS {s:5.1f} | {(nm or '(unnamed)')[:30]:30s} | {vp}->{vs} | -{fr:.0f}% fatal | {wy}"
        )
    return summary


def make_combined_pmtiles(keys):
    """Tile ALL cities' full scored networks into one PMTiles (features carry a `city`
    property), so the browser renders 100k+ segments smoothly and the map filters by city
    instead of swapping sources."""
    srcs = [
        str(FULLNET / f"sss_segments_{k}.geojson")
        for k in keys
        if (FULLNET / f"sss_segments_{k}.geojson").exists()
    ]
    if not srcs:
        print("[WARN] no full-network geojson to tile")
        return
    out = WEBDATA / "sss_all.pmtiles"
    cmd = [
        "tippecanoe",
        "-q",
        "--force",
        "-zg",
        "--minimum-zoom=9",
        "--drop-densest-as-needed",
        "--extend-zooms-if-still-dropping",
        "--no-tile-size-limit",
        "-l",
        "segments",
        "-o",
        str(out),
    ] + srcs
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:  # noqa: BLE001
        # fatal, not a WARN: a failed retile leaves fresh GeoJSON shipping beside a stale
        # PMTiles, so fly-to/search would point at roads the map never draws.
        raise SystemExit(
            f"[FAIL] tippecanoe failed: {e} - refusing to ship stale PMTiles "
            f"beside fresh GeoJSON"
        )
    print(f"[OK]   combined pmtiles -> {out.name} ({out.stat().st_size // 1024} KB)")


def finalize(all_keys):
    """Rebuild cities.json + the combined PMTiles from EVERY city that has a full-network
    geojson on disk (not just the ones built this run), so cities can be (re)built one at a
    time and the deployed artifacts still reflect all of them."""
    have = [
        k
        for k in all_keys
        if (FULLNET / f"sss_segments_{k}.geojson").exists()
        and (BUILD / f"sss_summary_{k}.json").exists()
    ]
    index = [json.loads((BUILD / f"sss_summary_{k}.json").read_text()) for k in have]
    (WEBDATA / "cities.json").write_text(json.dumps(index, indent=2))
    make_combined_pmtiles(have)
    print(
        f"\nFinalized {len(have)} cities -> cities.json + sss_all.pmtiles "
        f"({', '.join(s['label'] for s in index)})"
    )


def main():
    want = [a for a in sys.argv[1:] if a in CITIES] or list(CITIES)
    for key in want:
        build_city(key, CITIES[key])
    finalize(list(CITIES))


if __name__ == "__main__":
    main()
