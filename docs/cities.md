# Per-city numbers

All 51 cities scored from live OpenStreetMap, June 2026. `Flagged` = roads with a real posted limit above the Safe System speed. `ρ` / `p` = Spearman correlation between the raw speed-limit gap (the mismatch, independent of exposure weighting) and Meta Relative Wealth Index on a ~1.6 km grid (blank where the city has too little real-posted road to grid). Reproduce with `make data`, then `python3 build/overlay/compute_overlay.py` and `python3 build/overlay/gen_cities_md.py`. See [findings.md](findings.md).

| City | Streets scored | Real posted limit | Flagged | VRU sites | Wealth ρ | p |
|------|---------------:|------------------:|--------:|----------:|---------:|---:|
| Metro Manila | 87,123 | 14,163 | 4,664 | 5,669 | -0.11 | 0.289 |
| Cebu City | 22,402 | 2,027 | 581 | 858 | +0.21 | 0.246 |
| Davao City | 10,873 | 2,658 | 364 | 466 | +0.06 | 0.887 |
| Calamba | 9,499 | 698 | 229 | 284 | -0.30 | 0.207 |
| Angeles City | 14,211 | 974 | 202 | 431 | -0.12 | 0.418 |
| Iloilo City | 6,433 | 758 | 135 | 398 | -0.15 | 0.600 |
| San Fernando (Pampanga) | 10,209 | 708 | 134 | 342 | -0.42 | 0.026 |
| Koronadal | 3,274 | 476 | 99 | 86 | +0.10 | 0.730 |
| Bacolod | 8,167 | 475 | 98 | 258 | -0.61 | 0.035 |
| Cagayan de Oro | 8,555 | 441 | 72 | 307 | +0.02 | 0.965 |
| Tagum | 5,382 | 277 | 68 | 128 | -0.61 | 0.023 |
| San Jose del Monte | 13,027 | 335 | 58 | 489 | +0.17 | 0.275 |
| Antipolo | 14,955 | 324 | 53 | 418 | -0.11 | 0.706 |
| Mati | 1,336 | 197 | 49 | 42 | -0.35 | 0.385 |
| Ozamiz | 1,209 | 164 | 49 | 73 | +0.09 | 0.857 |
| Olongapo | 3,803 | 124 | 48 | 169 | +0.03 | 0.900 |
| Tarlac City | 6,751 | 242 | 47 | 175 | -0.09 | 0.658 |
| Dasmarinas | 21,063 | 4,432 | 45 | 580 | -0.18 | 0.174 |
| Laoag | 1,835 | 200 | 38 | 98 | -0.35 | 0.182 |
| Digos | 3,138 | 55 | 38 | 118 | -0.30 | 0.384 |
| Dipolog | 1,283 | 101 | 33 | 74 | +0.14 | 0.585 |
| Batangas City | 6,272 | 514 | 31 | 383 | +0.17 | 0.600 |
| Cotabato City | 1,599 | 106 | 31 | 111 | -0.23 | 0.348 |
| Ormoc | 1,884 | 99 | 31 | 116 | -0.35 | 0.166 |
| Dagupan | 2,534 | 169 | 30 | 165 | -0.18 | 0.421 |
| Iligan City | 2,265 | 176 | 29 | 176 | -0.20 | 0.560 |
| Tagbilaran | 2,168 | 121 | 28 | 208 | -0.11 | 0.647 |
| Sorsogon City | 999 | 134 | 27 | 64 | -0.31 | 0.412 |
| Malolos | 7,025 | 212 | 24 | 277 | -0.55 | 0.240 |
| Vigan | 1,632 | 186 | 24 | 110 | - | - |
| Baguio | 7,521 | 3,961 | 23 | 655 | +0.08 | 0.659 |
| Dumaguete | 3,397 | 183 | 21 | 116 | -0.13 | 0.632 |
| Lipa City | 9,898 | 724 | 20 | 259 | +0.23 | 0.223 |
| Santiago City | 1,786 | 194 | 20 | 72 | +0.23 | 0.226 |
| Marawi | 1,123 | 39 | 19 | 85 | - | - |
| Kidapawan | 1,726 | 97 | 18 | 57 | +0.16 | 0.599 |
| Legazpi City | 3,412 | 200 | 17 | 144 | -0.43 | 0.200 |
| Tacloban | 3,823 | 59 | 17 | 311 | +0.41 | 0.167 |
| Pagadian | 1,678 | 67 | 16 | 101 | +0.36 | 0.461 |
| Zamboanga City | 5,804 | 110 | 15 | 159 | -0.26 | 0.333 |
| Calbayog | 696 | 30 | 13 | 58 | +0.56 | 0.084 |
| Lucena City | 4,079 | 231 | 8 | 145 | +0.04 | 0.928 |
| Roxas City | 2,625 | 56 | 7 | 103 | - | - |
| Tuguegarao | 2,244 | 192 | 5 | 111 | -0.06 | 0.653 |
| General Santos | 9,013 | 116 | 4 | 144 | -0.06 | 0.950 |
| Cabanatuan | 3,886 | 35 | 2 | 170 | - | - |
| Urdaneta | 1,943 | 105 | 1 | 108 | +0.09 | 0.823 |
| Naga City | 3,212 | 7 | 1 | 164 | - | - |
| Surigao City | 1,082 | 18 | 0 | 51 | - | - |
| Puerto Princesa | 3,593 | 1 | 0 | 100 | - | - |
| Butuan | 3,976 | 0 | 0 | 213 | - | - |
| **All 51 cities** | **357,423** | **37,971** | **7,586** | **16,399** | | |
