# Per-city numbers

All 50 cities and Metro Manila scored from live OpenStreetMap, June 2026. `Flagged` = roads with a real posted limit above the Safe System speed. `ρ` / `p` = Spearman correlation between the raw speed-limit gap (the mismatch, independent of exposure weighting) and Meta Relative Wealth Index on a ~1.6 km grid (blank where the city has too little real-posted road to grid). Reproduce with `make data`, then `python3 build/overlay/compute_overlay.py` and `python3 build/overlay/gen_cities_md.py`. See [findings.md](findings.md).

| City | Streets scored | Real posted limit | Flagged | VRU sites | Wealth ρ | p |
|------|---------------:|------------------:|--------:|----------:|---------:|---:|
| Metro Manila | 87,123 | 14,163 | 5,328 | 5,669 | -0.14 | 0.189 |
| Cebu City | 22,402 | 2,027 | 727 | 858 | +0.17 | 0.474 |
| Davao City | 10,873 | 2,658 | 435 | 466 | +0.01 | 0.972 |
| San Fernando (Pampanga) | 10,209 | 708 | 322 | 342 | -0.20 | 0.334 |
| Angeles City | 14,211 | 974 | 243 | 431 | -0.13 | 0.538 |
| Calamba | 9,499 | 698 | 229 | 284 | -0.30 | 0.207 |
| Iloilo City | 6,433 | 758 | 199 | 398 | -0.19 | 0.440 |
| Cagayan de Oro | 8,555 | 441 | 148 | 307 | +0.25 | 0.321 |
| Iligan City | 2,265 | 176 | 117 | 176 | -0.19 | 0.520 |
| Koronadal | 3,274 | 476 | 105 | 86 | +0.08 | 0.807 |
| Bacolod | 8,167 | 475 | 98 | 258 | -0.63 | 0.035 |
| Malolos | 7,025 | 212 | 93 | 277 | -0.09 | 0.680 |
| Ozamiz | 1,209 | 164 | 88 | 73 | -0.44 | 0.216 |
| Dagupan | 2,534 | 169 | 84 | 165 | +0.08 | 0.685 |
| Tagum | 5,382 | 277 | 68 | 128 | -0.60 | 0.023 |
| Tarlac City | 6,751 | 242 | 68 | 175 | +0.10 | 0.690 |
| Sorsogon City | 999 | 134 | 67 | 64 | -0.70 | 0.059 |
| Mati | 1,336 | 197 | 65 | 42 | -0.37 | 0.308 |
| San Jose del Monte | 13,027 | 335 | 58 | 489 | +0.17 | 0.275 |
| Laoag | 1,835 | 200 | 55 | 98 | -0.48 | 0.046 |
| Olongapo | 3,803 | 124 | 55 | 169 | +0.12 | 0.700 |
| Antipolo | 14,955 | 324 | 53 | 418 | -0.11 | 0.706 |
| Dipolog | 1,283 | 101 | 52 | 74 | -0.57 | 0.167 |
| Baguio | 7,521 | 3,961 | 47 | 655 | +0.12 | 0.393 |
| Dasmarinas | 21,063 | 4,432 | 45 | 580 | -0.18 | 0.174 |
| Cotabato City | 1,599 | 106 | 44 | 111 | -0.61 | 0.044 |
| Ormoc | 1,884 | 99 | 43 | 116 | -0.17 | 0.557 |
| Legazpi City | 3,412 | 200 | 42 | 144 | -0.57 | 0.050 |
| Digos | 3,138 | 55 | 40 | 118 | -0.22 | 0.538 |
| Santiago City | 1,786 | 194 | 35 | 72 | +0.22 | 0.317 |
| Vigan | 1,632 | 186 | 34 | 110 | - | - |
| Tacloban | 3,823 | 59 | 32 | 311 | +0.20 | 0.584 |
| Batangas City | 6,272 | 514 | 31 | 383 | +0.17 | 0.600 |
| Urdaneta | 1,943 | 105 | 30 | 108 | +0.09 | 0.882 |
| Lipa City | 9,898 | 724 | 28 | 259 | +0.10 | 0.371 |
| Tuguegarao | 2,244 | 192 | 28 | 111 | +0.05 | 0.828 |
| Tagbilaran | 2,168 | 121 | 28 | 208 | -0.11 | 0.647 |
| Kidapawan | 1,726 | 97 | 26 | 57 | +0.04 | 0.600 |
| Pagadian | 1,678 | 67 | 26 | 101 | -0.10 | 0.769 |
| Calbayog | 696 | 30 | 22 | 58 | -0.06 | 0.917 |
| Dumaguete | 3,397 | 183 | 21 | 116 | -0.13 | 0.632 |
| Marawi | 1,123 | 39 | 19 | 85 | - | - |
| Lucena City | 4,079 | 231 | 18 | 145 | +0.07 | 0.714 |
| Zamboanga City | 5,804 | 110 | 16 | 159 | -0.26 | 0.333 |
| Roxas City | 2,625 | 56 | 7 | 103 | - | - |
| Surigao City | 1,082 | 18 | 6 | 51 | - | - |
| General Santos | 9,013 | 116 | 4 | 144 | -0.05 | 0.900 |
| Cabanatuan | 3,886 | 35 | 3 | 170 | - | - |
| Naga City | 3,212 | 7 | 3 | 164 | - | - |
| Puerto Princesa | 3,593 | 1 | 0 | 100 | - | - |
| Butuan | 3,976 | 0 | 0 | 213 | - | - |
| **50 cities + Metro Manila** | **357,423** | **37,971** | **9,435** | **16,399** | | |
