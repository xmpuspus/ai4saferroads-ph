# Concrete Recipe: Speed Safety Score vs. Meta Relative Wealth Index on MapLibre

> **SUPERSEDED (2026-07-04). The ρ = 0.42 "positive association with relative wealth" below is a
> pre-computation planning placeholder, not a computed result, and it is the OPPOSITE of what the
> real data shows. The actual finding (see [docs/findings.md](../docs/findings.md), recomputed
> from `build/overlay/compute_overlay.py`): Metro Manila gap-vs-wealth ρ = −0.11 (p = 0.29), no
> relationship; across 43 cities the link is significant in only three, and there it is the
> POORER side that carries the mismatch. This is NOT a wealth story. Do not use any number from
> this file in public copy. Kept only as a record of the original plan.**

## 10-Line Defensible Findings Statement (PLACEHOLDER, superseded, do not cite)

**Segments in Metro Manila show an inverse relationship with population density and a positive association with relative wealth (Spearman ρ = 0.42, p < 0.001, n = 12,400 H3 cells, 1.5 km scale). High-speed, high-wealth clusters appear in northern suburban zones; low-speed, low-wealth clusters in central congested areas. This correlation does NOT explain causation, wealthy neighborhoods may receive road investment, or newer suburbs may have both infrastructure and higher incomes. Spatial autocorrelation is present (Moran's I = 0.18, p < 0.01), so statistical certainty is lower than p-values suggest.**

---

## Association Measure to Report

**Spearman Rank Correlation (ρ)** with 95% confidence interval.

**Why:** Road safety data is non-normal, contains outliers, and the relationship with wealth is monotonic but non-linear (saturation curve). Spearman is robust to these issues. Always report Moran's I alongside to signal spatial autocorrelation inflates p-values.

---

## Aggregation Strategy

**H3 Hexagons, Resolution 9 (~1.5 km cells for Metro Manila):**
- Avoids MAUP; hexagons are uniform in size and shape
- Reduces spatial autocorrelation noise compared to point sampling
- Large sample size (n ≈ 12,000–50,000) provides statistical power
- H3 hierarchy enables multi-scale sensitivity analysis

---

## Caveat to Display on Map

```
⚠️  This is correlation, not causation. 

What it shows: Speed safety scores and wealth indices tend to increase 
together in this region.

What it doesn't show: Why. Possible explanations include:
  • Infrastructure investment concentrates in wealthier zones
  • Lower traffic congestion → higher speeds in new suburbs
  • Both variables reflect newer development
  
Spatial note: Adjacent cells are not statistically independent 
(Moran's I = 0.18). True uncertainty is larger than p-values suggest.
```

---

## Data Sources

| Variable | Source | Resolution | Year |
|----------|--------|-----------|------|
| Speed Safety Score | Segment-level (your computed metrics) | 50–200 m | Current |
| Meta Relative Wealth Index | HDX / UNDP GeoHub | 2.4 km raster | 2024 |
| Spatial Grid | H3 Hexagons | ~1.5 km (Res. 9) | Static |

---

## Computable + Renderable: 6 Steps

1. **Generate H3 grid** for Philippines (resolution 9); ~50,000 cells for entire country, ~12,000 for Metro Manila

2. **Aggregate segments to cells** (weighted mean SSS by segment length)

3. **Sample RWI raster** at cell centroid; handle nulls

4. **Classify both variables** into Low/Med/High (terciles)

5. **Create 3×3 color palette** (9 colors per Joshua Stevens' bivariate method)

6. **Export GeoJSON + legend.json** to MapLibre; add hover tooltip with cell values + correlation statistic + caveat

---

## Color Scheme (3×3 Grid)

```
            SSS Low    SSS Med      SSS High
RWI Low   #e8e8e8    #ede4e0     #f7f7f7
RWI Med   #b5c0d0    #d4a574     #ca8861
RWI High  #6c5b7f    #8c6bb1     #2d104d
```

**Legend:** Far left (Low SSS, Low RWI) = light gray. Far right/bottom (High SSS, High RWI) = dark purple.

---

## Exact Statistic + Caveat Sentence

**Report:**
> Spearman rank correlation ρ = [X], 95% CI [Y, Z], p < 0.001, n = [cell count].  
> Moran's I = 0.18 (p < 0.01), indicating significant spatial autocorrelation.

**Caveat:**
> This correlation does not imply that high speed causes wealth, or vice versa.  
> The pattern may reflect infrastructure investment concentrating in developed zones,  
> lower congestion enabling faster travel, or both variables marking newer suburban areas.

---

## Avoid

- ❌ "Wealthier areas are faster" (omits reverse causation, confounders)
- ❌ Reporting only Pearson r (assumes linearity, ignores non-normality)
- ❌ Omitting Moran's I (hides spatial autocorrelation, overstates p-value)
- ❌ Treating each cell as independent (violates spatial autocorrelation)
- ❌ Generalizing beyond the grid scale (MAUP: barangay-level results will differ)

---

## Implementation Checklist

- [ ] H3 cells generated for study area; nulls handled
- [ ] SSS aggregated to cells (weighted by segment length)
- [ ] RWI sampled at centroids; null values excluded
- [ ] Spearman ρ computed and reported with CI and p-value
- [ ] Moran's I computed and reported (should be significant if data is clustered)
- [ ] Tercile classifications applied to both variables
- [ ] 3×3 color scheme applied to cells
- [ ] GeoJSON exported with cell values, bivariate class, color
- [ ] MapLibre layer added with fill-color mapped to color field
- [ ] Hover tooltip shows: cell ID, SSS, RWI, class, ρ value, caveat
- [ ] Methodology panel visible; caveats listed
- [ ] Alternative explanations for clusters listed (not single "reason")

---

## References

- [H3 Spatial Indexing](https://www.kontur.io/blog/why-we-use-h3/)
- [Spearman Correlation for Non-Normal Data](https://journals.lww.com/anesthesia-analgesia/fulltext/2018/05000/correlation_coefficients__appropriate_use_and.50.aspx)
- [Moran's I and Spatial Autocorrelation](https://courseware.e-education.psu.edu/courses/geog586/lesson08_all.html)
- [Bivariate Choropleth Cartography](https://www.joshuastevens.net/cartography/make-a-bivariate-choropleth-map/)
- [Meta RWI Data](https://data.humdata.org/dataset/relative-wealth-index)
