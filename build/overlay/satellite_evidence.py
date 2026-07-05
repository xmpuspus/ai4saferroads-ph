"""Satellite width evidence for the headline flagged crash corridors.

OSM has no lane/width tag on most PH arterials, so the design-speed proxy leans on class +
alignment. Satellite imagery closes that gap with the physical evidence a skeptic can see:
these flagged roads are wide, dead-straight, multi-lane strips through dense housing - built
to carry lethal speed the moment they clear, whatever the daytime crawl.

For the top flagged real-posted roads in Manila / Cebu / Davao this pulls high-zoom Esri World
Imagery (same public service the map uses), draws the OSM road centerline plus a 25 m scale bar,
and writes an annotated crop and a JSON manifest. An automated grey-pixel width transect was
tried and discarded as unreliable over medians, elevated rail, and water; lane counts are read
by eye against the scale bar and hand-verified into the manifest before entering any copy.

Run: python3 build/overlay/satellite_evidence.py
"""
import io
import json
import math
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
WEBDATA = ROOT / "build" / "web" / "data"
OUT = WEBDATA / "sat"
OUT.mkdir(parents=True, exist_ok=True)
BUILD = ROOT / "build"
ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
LANE_M = 3.35  # typical urban lane width for the lane-count estimate

CITY_ROADS = {  # top flagged real-posted corridors to image, by city
    "manila": 4, "cebu": 2, "davao": 2,
}


def gpx(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n * 256
    y = (1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n * 256
    return x, y


def mpp(lat, z):
    return 156543.03392 * math.cos(math.radians(lat)) / (2 ** z)


def fetch_tile(z, x, y):
    url = ESRI.format(z=z, x=x, y=y)
    req = urllib.request.Request(url, headers={"User-Agent": "ai4saferroads-ph/0.4 (personal civic research)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def crop(lon, lat, z, half=1):
    x0, y0 = int(gpx(lon, lat, z)[0] // 256), int(gpx(lon, lat, z)[1] // 256)
    nt = half * 2 + 1
    canvas = Image.new("RGB", (256 * nt, 256 * nt))
    for i, tx in enumerate(range(x0 - half, x0 + half + 1)):
        for j, ty in enumerate(range(y0 - half, y0 + half + 1)):
            canvas.paste(fetch_tile(z, tx, ty), (i * 256, j * 256))
    origin = ((x0 - half) * 256, (y0 - half) * 256)   # global px of crop top-left
    return canvas, origin


def local_px(lon, lat, z, origin):
    gx, gy = gpx(lon, lat, z)
    return gx - origin[0], gy - origin[1]


def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def annotate(canvas, poly_px, mpp_, road, design, caption_extra=""):
    """Draw the actual OSM road centerline (reliable) + a 25 m scale bar + a caption. No
    fabricated width transect - width is read by eye off the scale bar and hand-verified."""
    d = ImageDraw.Draw(canvas, "RGBA")
    W, H = canvas.size
    if len(poly_px) >= 2:
        d.line(poly_px, fill=(91, 141, 184, 200), width=2)   # subject road centerline (steel blue)
    # scale bar 25 m, bottom-left
    bar = 25 / mpp_
    bx, by = 18, H - 26
    d.rectangle([bx - 6, by - 22, bx + bar + 46, by + 12], fill=(10, 12, 16, 200))
    d.line([(bx, by), (bx + bar, by)], fill=(255, 255, 255, 255), width=4)
    d.text((bx, by - 19), "25 m", font=font(15), fill=(255, 255, 255, 255))
    cap = f"{road}  •  built for ~{design} km/h, survivable 30{caption_extra}"
    tb = d.textbbox((0, 0), cap, font=font(17))
    d.rectangle([0, 0, W, tb[3] + 12], fill=(10, 12, 16, 205))
    d.text((12, 6), cap, font=font(17), fill=(240, 244, 250, 255))
    return canvas


def main():
    z = 18
    manifest = []
    for key, topn in CITY_ROADS.items():
        summ = json.loads((BUILD / f"sss_summary_{key}.json").read_text())
        flag = json.loads((WEBDATA / f"sss_flagged_{key}.geojson").read_text())
        heads = summ.get("headline_priority_roads_real_posted", [])[:topn]
        for r in heads:
            nm, sss = r["name"], r["sss"]
            feat = next((f for f in flag["features"]
                         if f["properties"].get("name") == nm and round(f["properties"]["sss"], 1) == round(sss, 1)), None)
            if not feat:
                continue
            coords = feat["geometry"]["coordinates"]
            mid_i = len(coords) // 2
            lon, lat = coords[mid_i]
            canvas, origin = crop(lon, lat, z, half=1)
            m = mpp(lat, z)
            design = r.get("v_design")
            # map the whole subject polyline into crop pixels (clip loosely to canvas)
            poly_px = [local_px(c[0], c[1], z, origin) for c in coords]
            poly_px = [(x, y) for (x, y) in poly_px if -80 <= x <= canvas.size[0] + 80 and -80 <= y <= canvas.size[1] + 80]
            annotate(canvas, poly_px, m, nm, design)
            slug = f"{key}_{nm.lower().replace(' ', '-').replace('.', '')}"
            canvas.save(OUT / f"{slug}.png")
            row = {"city": key, "road": nm, "sss": sss, "posted": r["posted_osm"], "safe": r["safe"],
                   "v_design": design, "lat": round(lat, 6), "lon": round(lon, 6),
                   "mpp": round(m, 3), "crop": f"data/sat/{slug}.png",
                   "lanes_verified": None, "width_m_verified": None}
            manifest.append(row)
            print(f"[sat] {key:7s} {nm:26s} design {design}  -> {slug}.png")
    # raw candidates only: the shipped sat_evidence.json is hand-verified (lane counts read
    # by eye, schema the map consumes) and must never be clobbered by a re-run
    (WEBDATA / "sat_evidence_raw.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nwrote {len(manifest)} crops -> {OUT}  + sat_evidence_raw.json (hand-verify into sat_evidence.json)")


if __name__ == "__main__":
    main()
