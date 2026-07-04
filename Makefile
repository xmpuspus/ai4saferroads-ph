.PHONY: data serve shot e2e clean all
PORT ?= 8799

data:            ## pull live OSM + compute Speed Safety Score for all cities
	python3 build/sss_pipeline.py

serve:           ## serve the map at http://127.0.0.1:$(PORT)/web/index.html (Range-capable, needed for PMTiles)
	python3 build/web/serve.py $(PORT)

shot:            ## render screenshots for a few cities (needs node + playwright chromium)
	cd build && for c in manila cebu davao; do \
	  SHOT_CITY=$$c SHOT_OUT=../screenshots/sss_$$c.png node shot.mjs ; done

e2e:             ## run invariant + wiring checks against built artifacts
	bash tests/e2e.sh

clean:           ## remove generated data + screenshots
	rm -f build/web/data/*.geojson build/web/data/cities.json build/sss_summary_*.json
	rm -f screenshots/*.png

all: data e2e    ## rebuild data then verify
