"""Unit tests for the Speed Safety Score pipeline core (no network).

Guards the functions a regression would silently break: maxspeed parsing, the Safe System
V_safe classifier (including the one-way!=divided fix and the Skyway fix), the design-speed
proxy, and the POI-scan radius fix (pois_within must not miss a site 111-150m out).

Run as pytest:  python3 -m pytest tests/test_pipeline.py -q
Run as script:  python3 tests/test_pipeline.py   (used by tests/e2e.sh)
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("sss", ROOT / "build" / "sss_pipeline.py")
sss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sss)


def test_parse_maxspeed_plain_kmh():
    assert sss.parse_maxspeed("60") == 60


def test_parse_maxspeed_mph_converts_to_kmh():
    assert sss.parse_maxspeed("30 mph") == 48


def test_parse_maxspeed_none_value():
    assert sss.parse_maxspeed("none") is None


def test_parse_maxspeed_walk_value():
    assert sss.parse_maxspeed("walk") is None


def test_parse_maxspeed_missing_value():
    assert sss.parse_maxspeed(None) is None


def test_parse_maxspeed_out_of_range_rejected():
    assert sss.parse_maxspeed("200") is None


def test_safe_speed_primary_with_nearby_pedestrian_site():
    assert sss.safe_speed("primary", 1, {})[0] == 30


def test_safe_speed_residential_local_road():
    assert sss.safe_speed("residential", 0, {})[0] == 30


def test_safe_speed_motorway_never_ped_downgraded():
    assert sss.safe_speed("motorway", 5, {})[0] == 100


def test_safe_speed_trunk_never_ped_downgraded():
    assert sss.safe_speed("trunk", 5, {})[0] == 70


def test_safe_speed_oneway_arterial_is_not_divided():
    assert sss.safe_speed("primary", 0, {"oneway": "yes"})[0] == 50


def test_safe_speed_genuinely_divided_carriageway():
    assert sss.safe_speed("primary", 0, {"dual_carriageway": "yes"})[0] == 70


def test_safe_speed_undivided_secondary_arterial():
    assert sss.safe_speed("secondary", 0, {})[0] == 50


def test_safe_speed_living_street():
    assert sss.safe_speed("living_street", 0, {})[0] == 20


STRAIGHT = [[121.0, 14.500], [121.0, 14.502]]  # ~222 m dead-straight (sinuosity 1.0)
WINDING = [
    [121.0, 14.500],
    [121.0015, 14.5006],
    [121.0, 14.5012],
    [121.0015, 14.5018],
    [121.0, 14.502],
]


def test_design_speed_straight_primary():
    assert sss.design_speed("primary", STRAIGHT, {}) == 60


def test_design_speed_straight_motorway():
    assert sss.design_speed("motorway", STRAIGHT, {}) == 90


def test_design_speed_straight_residential():
    assert sss.design_speed("residential", STRAIGHT, {}) == 35


def test_design_speed_service():
    assert sss.design_speed("service", STRAIGHT, {}) == 25


def test_design_speed_winding_trimmed_below_straight_base():
    assert sss.design_speed("primary", WINDING, {}) < 60


def test_pois_within_finds_site_140m_out_two_cells_over():
    # A site 140m N of mid: the old hardcoded 3x3 window (+/-1 cell, ~111m) would miss it;
    # the radius-derived span must not (sss_pipeline.py:310-322 audit finding).
    mid = (14.6000, 121.0000)
    poi_lat = mid[0] + 140.0 / 111000.0
    poi_pts = [(poi_lat, mid[1], "school")]
    grid = sss.build_poi_grid(poi_pts)
    assert sss.pois_within(grid, poi_pts, mid, 150) == 1


def test_pois_within_excludes_site_outside_radius():
    mid = (14.6000, 121.0000)
    poi_lat = mid[0] + 200.0 / 111000.0
    poi_pts = [(poi_lat, mid[1], "school")]
    grid = sss.build_poi_grid(poi_pts)
    assert sss.pois_within(grid, poi_pts, mid, 150) == 0


def test_pois_within_50m_radius_unaffected_by_span_widening():
    # 50m always fit inside a single cell at PH latitudes (even the shortest lon cell, near
    # the northernmost bbox, is >100m wide) - confirms n50/v_safe never move from this fix.
    mid = (18.0000, 120.6000)
    near_pts = [(mid[0] + 40.0 / 111000.0, mid[1], "school")]
    grid = sss.build_poi_grid(near_pts)
    assert sss.pois_within(grid, near_pts, mid, 50) == 1
    far_pts = [(mid[0] + 60.0 / 111000.0, mid[1], "school")]
    grid2 = sss.build_poi_grid(far_pts)
    assert sss.pois_within(grid2, far_pts, mid, 50) == 0


if __name__ == "__main__":
    import sys

    import pytest

    raise SystemExit(pytest.main([str(Path(__file__).resolve()), "-q", *sys.argv[1:]]))
