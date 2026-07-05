"""Unit tests for the Speed Safety Score pipeline core (no network).

Guards the two functions a regression would silently break: maxspeed parsing and the
Safe System V_safe classifier (including the one-way!=divided fix and the Skyway fix).
Run: python3 tests/test_pipeline.py   (plain asserts, no pytest dependency)
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("sss", ROOT / "build" / "sss_pipeline.py")
sss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sss)

fails = []


def eq(got, want, msg):
    ok = got == want
    print(("[PASS] " if ok else "[FAIL] ") + f"{msg}  (got {got!r})")
    if not ok:
        fails.append(msg)


# parse_maxspeed
eq(sss.parse_maxspeed("60"), 60, "parse '60' -> 60")
eq(sss.parse_maxspeed("30 mph"), 48, "parse '30 mph' -> 48 km/h")
eq(sss.parse_maxspeed("none"), None, "parse 'none' -> None")
eq(sss.parse_maxspeed("walk"), None, "parse 'walk' -> None")
eq(sss.parse_maxspeed(None), None, "parse None -> None")
eq(sss.parse_maxspeed("200"), None, "parse out-of-range '200' -> None")

# safe_speed classifier
eq(sss.safe_speed("primary", 1, {})[0], 30, "primary with pedestrian site<=50m -> 30")
eq(sss.safe_speed("residential", 0, {})[0], 30, "residential local road -> 30")
eq(sss.safe_speed("motorway", 5, {})[0], 100, "motorway never ped-downgraded (Skyway fix) -> 100")
eq(sss.safe_speed("trunk", 5, {})[0], 70, "trunk never ped-downgraded -> 70")
eq(sss.safe_speed("primary", 0, {"oneway": "yes"})[0], 50,
   "one-way arterial is NOT 'divided' -> 50 (one-way!=divided fix)")
eq(sss.safe_speed("primary", 0, {"dual_carriageway": "yes"})[0], 70,
   "genuinely divided carriageway -> 70")
eq(sss.safe_speed("secondary", 0, {})[0], 50, "undivided secondary arterial -> 50")
eq(sss.safe_speed("living_street", 0, {})[0], 20, "living street -> 20")

# design_speed proxy (free-flow speed the built form invites; curvature only trims it)
STRAIGHT = [[121.0, 14.500], [121.0, 14.502]]   # ~222 m dead-straight (sinuosity 1.0)
eq(sss.design_speed("primary", STRAIGHT, {}), 60, "straight primary design speed -> 60")
eq(sss.design_speed("motorway", STRAIGHT, {}), 90, "straight motorway design speed -> 90")
eq(sss.design_speed("residential", STRAIGHT, {}), 35, "straight residential design speed -> 35")
eq(sss.design_speed("service", STRAIGHT, {}), 25, "service design speed -> 25")
# a winding alignment is trimmed below the straight class base
WINDING = [[121.0, 14.500], [121.0015, 14.5006], [121.0, 14.5012], [121.0015, 14.5018], [121.0, 14.502]]
_dw = sss.design_speed("primary", WINDING, {})
eq(_dw < 60, True, f"winding primary trimmed below straight base (got {_dw})")

print(f"\n{'ALL PIPELINE TESTS PASS' if not fails else str(len(fails)) + ' FAILED'}")
raise SystemExit(1 if fails else 0)
