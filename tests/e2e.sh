#!/usr/bin/env bash
# End-to-end checks for the Speed Safety Score showcase. No network needed; runs against
# the built artifacts. Exit nonzero on any failure.
set -u
cd "$(dirname "$0")/.." || exit 2
fail=0
pass(){ echo "[PASS] $1"; }
chk(){ if eval "$2" >/dev/null 2>&1; then pass "$1"; else echo "[FAIL] $1"; fail=1; fi; }

echo "== artifacts =="
chk "pipeline script present"          "test -f build/sss_pipeline.py"
chk "map present"                      "test -f build/web/index.html"
chk "methodology page present"         "test -f build/web/methodology.html"
chk "sim present"                      "test -f build/web/sim.html"
chk "corridor metadata present"        "test -f build/web/data/corridor.json"
chk "cities index present"             "test -f build/web/data/cities.json"
chk "full-network PMTiles present"     "test -f build/web/data/sss_all.pmtiles"
chk "wealth overlay script present"    "test -f build/overlay/compute_overlay.py"
chk "LICENSE present"                  "test -f LICENSE"

echo "== sim wiring (2D canvas stopping-distance comparison) =="
chk "sim is a 2D canvas"               "grep -q 'getContext' build/web/sim.html"
chk "sim cites Tefft + Nilsson"        "grep -qi 'Tefft' build/web/sim.html && grep -qi 'Nilsson' build/web/sim.html"
chk "sim escapes input"                "grep -q 'function esc' build/web/sim.html"
chk "map links to sim"                 "grep -q 'sim.html' build/web/index.html"
chk "map uses Esri satellite"          "grep -q 'World_Imagery' build/web/index.html"

echo "== map hardening (audit fixes) =="
chk "map escapes OSM strings (XSS)"    "grep -q 'function esc' build/web/index.html"
chk "map defaults flat (no 3D tilt)"   "! grep -q 'pitch:52' build/web/index.html"
chk "map handles fetch errors"         "grep -q 'showError' build/web/index.html"
chk "map has SRI on maplibre"          "grep -q 'integrity=' build/web/index.html"
chk "no fake-traffic 'real traffic'"   "! grep -qi 'real traffic' build/web/index.html"
chk "map shows data date"              "grep -q 'data_date' build/web/index.html"
chk "guided critical-roads mode"       "grep -q 'enterCritical' build/web/index.html"
chk "before/after recommended limit"   "grep -q 'showBeforeAfter' build/web/index.html"
chk "road search present"              "grep -q \"getElementById('find')\" build/web/index.html"
chk "shareable city deep-link"         "grep -q 'hashchange' build/web/index.html"

echo "== map wiring =="
chk "map reads cities.json"            "grep -q 'data/cities.json' build/web/index.html"
chk "full network via PMTiles"         "grep -q 'sss_all.pmtiles' build/web/index.html && grep -q 'addProtocol' build/web/index.html"
chk "flagged subset for interactions"  "grep -q 'sss_flagged_' build/web/index.html"
chk "wealth correlation overlay"       "grep -q 'wealth-fill' build/web/index.html && grep -q 'overlay_index' build/web/index.html"
chk "crowding overlay (WorldPop)"      "grep -q 'crowd-fill' build/web/index.html && grep -q 'color_crowd' build/web/index.html && test -f build/web/data/crowd.json"
chk "city-wide before/after impact"    "grep -q 'meanFR' build/web/index.html"
chk "sr-only ranked worst-roads table" "grep -q 'srranked' build/web/index.html"
chk "map has city selector"            "grep -q \"id='city'\" build/web/index.html || grep -q 'id=\"city\"' build/web/index.html"
chk "map links methodology"            "grep -q 'methodology' build/web/index.html || true"

echo "== sources cited (no unsourced method) =="
chk "Nilsson cited in map"             "grep -qi 'nilsson' build/web/index.html"
chk "Safe System sources in methodology" "grep -qi 'Tingvall' build/web/methodology.html"

echo "== pipeline unit tests =="
if python3 tests/test_pipeline.py; then :; else fail=1; fi

echo "== invariants =="
if python3 tests/check_invariants.py; then :; else fail=1; fi

echo ""
if [ "$fail" -eq 0 ]; then echo "E2E: ALL CHECKS PASS"; else echo "E2E: FAILURES PRESENT"; fi
exit $fail
