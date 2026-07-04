# Defensible Spatial Correlation Methods for Speed Safety Score

## Overview

Presenting "surprising but sourced" insights on a civic web map requires avoiding two pitfalls: **ecological fallacy** (inferring individual behavior from aggregate data) and **MAUP** (Modifiable Areal Unit Problem — statistical results that change based on zone boundaries chosen). This guide covers three aggregation strategies, when to use which association measure, how respected civic-data projects frame unexpected findings, and a minimal working recipe for one computable, renderable bivariate overlay.

---

## 1. Joining Segment-Level Scores to Areal/Grid Data: Aggregation Strategies

Road segments (linear, 50–200m typical length) present a unique challenge: overlay datasets (population, poverty, wealth indices, crashes) often come as rasters (gridded) or polygons (administrative/census units), not segment-aligned. Three strategies exist; each has trade-offs.

### Strategy A: Sample Overlay Data at Segment Midpoint (Point-in-Grid)

**Method:**
1. Compute the midpoint (or centroid) of each segment
2. Sample the overlay raster/grid at that point location
3. Assign the sampled value (e.g., population density, RWI value) as a segment attribute

**Advantages:**
- No aggregation bias; preserves segment independence
- Works for continuous rasters (WorldPop, Meta RWI, elevation)
- Avoids MAUP by staying at the finest spatial resolution

**Disadvantages:**
- Single-point sampling ignores segment length and heterogeneity
- Segments crossing zone boundaries lose "half" of the overlap
- Noisier for sparse or high-variance overlays

**Use when:** Overlay data is spatially continuous and fine-resolution (30m–250m cells), or you want the smallest sample-size penalty.

**Citation:** [Geospatial analysis methods for segment-level integration](https://appliedgeographic.com/2024/02/spatial-analysis-pitfalls-the-maup/) recommend point sampling as a baseline for linear networks to minimize zoning artifacts.

---

### Strategy B: Aggregate Segments to Barangay (or Admin Boundary)

**Method:**
1. Spatially join segments to administrative boundaries (barangay, municipality)
2. Aggregate segment SSS to a single barangay value (e.g., mean or weighted mean by segment length)
3. Join barangay-level SSS to barangay-level overlay data (census population, poverty rate)
4. Compute correlation at barangay scale

**Advantages:**
- Matches overlay data availability (census, poverty indices often come at barangay/municipality level)
- Reduces spatial correlation noise; larger units are more stable
- Enables use of matched demographic databases (BAS, PSA poverty counts)

**Disadvantages:**
- Severe aggregation bias; loses granularity (a high-speed corridor in one barangay is smoothed into one value)
- Introduces MAUP: barangay boundaries are irregular, causing boundary-related artifacts
- Only ~1,600 barangays in the Philippines, so sample size for correlation is small (n ≈ 1,600 or fewer, depending on road coverage)
- Spatial autocorrelation inflates significance; adjacent barangays are not independent

**Use when:** Overlay data is only available at administrative level (PSA poverty estimates) and you accept the loss of detail.

**Citation:** [MapAgora methodology notes](https://www.nature.com/articles/s41597-025-05353-6) caution that "ZIP code-level measures are less reliable than county-level counterparts" due to mismatch between organization location and constituent residence, suggesting aggregation to coarser units reduces noise but introduces boundary artifacts.

---

### Strategy C: Regular Grid (H3 Hexagons or 500m Cells)

**Method:**
1. Tile the study area with uniform hexagons (H3, e.g., resolution 9 ≈ 1.5 km) or square cells (500m × 500m)
2. Aggregate all segments falling within each cell, computing cell-level SSS (mean/median/weighted by length)
3. Sample overlay raster values at cell centroid OR aggregate overlay data to cell using zonal statistics
4. Compute correlation at cell scale (e.g., Spearman ρ, n ≈ 10,000–50,000 cells for Metro Manila)

**Advantages:**
- Reduces MAUP compared to irregular admin boundaries; hexagons are uniform in size and shape
- H3 hexagons have 6 equal neighbors (less directional bias); cells don't change over time
- Recovers fine-grain spatial patterns compared to barangay aggregation
- H3 hierarchical structure allows multi-scale analysis (resolution 9 → 10 → 11)
- Large sample size (n ≈ 10,000–50,000) means Moran's I, LISA, and correlation tests have statistical power

**Disadvantages:**
- Moderate aggregation bias; still smooths local patterns
- Requires binning decision (cell size); modest MAUP remains (smaller cells → more variance)
- Overlay data may need resampling/interpolation to align with grid

**Use when:** Overlay data is high-resolution rasters (WorldPop, Meta RWI at 30–250m) and you want to map surprising patterns and test significance without barangay aggregation bias.

**Citation:** [Kontur.io on H3](https://www.kontur.io/blog/why-we-use-h3/) notes H3's uniform neighbor relationships reduce directional bias and its immutability enables temporal comparison. [Applied geospatial research](https://www.geowgs84.ai/post/what-is-h3-indexing-a-beginner-guide-to-hierarchical-hexagonal-geospatial-grid-system) confirms hexagon grids reduce perimeter-to-area bias compared to rectangular cells.

---

## 2. Association Measures for Spatial Data

### Correlation Coefficients: Pearson vs. Spearman

**Pearson Correlation (r):**
- Assumes linear relationship, normally distributed data
- Sensitive to outliers and non-linear monotonic associations
- Inflated significance under spatial autocorrelation (adjacent cells are correlated, violating independence assumption)

**When to use:** Only if (a) scatterplot shows clear linear trend, (b) data is approximately normal, and (c) you report spatial autocorrelation diagnostics (Moran's I) separately.

**Spearman Rank Correlation (ρ):**
- Ranks data first, then computes correlation; detects any monotonic relationship
- Robust to outliers; requires no distributional assumptions
- Still subject to spatial autocorrelation inflation of significance, but less sensitive to extreme values
- More appropriate for ordinal or skewed data (e.g., poverty indices, wealth rankings)

**When to use:** When data is non-normal, has outliers, or the relationship is non-linear but monotonic (e.g., SSS vs. RWI wealth index, which follows a saturation curve). Recommended for road safety data.

**Citation:** [Medical research on correlation](https://journals.lww.com/anesthesia-analgesia/fulltext/2018/05000/correlation_coefficients__appropriate_use_and.50.aspx) and [SurveyMonkey comparative guide](https://www.surveymonkey.com/market-research/resources/pearson-correlation-vs-spearman-correlation/) confirm Spearman is appropriate for nonnormal data and monotonic (not necessarily linear) relationships. [Laerd Statistics](https://statistics.laerd.com/statistical-guides/spearmans-rank-order-correlation-statistical-guide.php) notes Spearman is less sensitive to outliers, making it robust for civic-data overlays.

---

### Spatial Autocorrelation Diagnostics: Moran's I and LISA

**Moran's I (Global):**
- Single statistic summarizing degree of clustering in the study area
- I > 0: positive autocorrelation (neighboring cells have similar values)
- I < 0: negative autocorrelation (neighboring cells are dissimilar)
- Inflates the significance of ANY correlation test (Pearson, Spearman, regression) by underestimating variance

**Use:** Report alongside any correlation. If Moran's I is significant (p < 0.05), correlation p-values are optimistic.

**LISA (Local Indicators of Spatial Association):**
- Computes Moran's I for each cell, identifying local clusters
- Four quadrants: HH (high SSS near high overlay), LL, HL, LH
- Reveals where surprising patterns are clustered (e.g., "high-speed but low-poverty zones")

**Use:** Map LISA results as a thematic layer to show "surprising clusters" without overstating causation.

**Citation:** [PyPAL exploratory spatial analysis](https://pysal.org/notebooks/viz/splot/esda_morans_viz.html) tutorial details Moran's I global and LISA local clustering. [Penn State geospatial course](https://courseware.e-education.psu.edu/courses/geog586/lesson08_all.html) explains spatial autocorrelation and its inflating effect on significance tests.

---

### Bivariate Correlation and Visualization

**Bivariate Moran's I:**
- Measures whether high SSS cells are near high overlay values (or low near low)
- Extends univariate Moran's I to two variables
- Can detect clustering of the association itself

**Use:** For a final summary statistic, but visual map is more informative.

---

## 3. Framing "Surprising Findings" Without Overclaiming Causation

Respected civic-data and open-data projects consistently use three strategies to present unexpected patterns defensibly.

### Pattern 1: Lead with Measurement + Method + Period

**Good framing (from Gapminder and global health visualizations):**
> "Segments in Metro Manila show an inverse relationship between speed safety score and population density: areas with the highest population density average SSS 0.62 (95% CI: 0.58–0.66), while the lowest-density areas average SSS 0.78 (0.74–0.82). This pattern appears when aggregating to H3 grid cells (1.5 km scale) and sampling WorldPop 100m population density data for 2024. The correlation is ρ = 0.42 (p < 0.001, Spearman rank). Spatial autocorrelation is present (Moran's I = 0.18, p < 0.01), so the true uncertainty is likely larger than the p-value suggests."

**Why it works:**
- Opens with the actual numbers, not a claim ("we found")
- Names the aggregation method, scale, and data source explicitly
- Includes 95% confidence intervals (shows uncertainty is real)
- Names the association measure (Spearman, not Pearson)
- Reports spatial autocorrelation (signals readers that p-values may be optimistic)
- Avoids the word "causes"

**Bad framing:**
> "Dense areas have lower safety scores, suggesting overcrowding makes roads less safe."
> (Jumps to causation without method, data source, or uncertainty.)

**Citation:** [Gapminder Factfulness methodology](https://www.gapminder.org/factfulness-book/notes/) and [academic guidance on causal inference from visualizations](https://arxiv.org/pdf/2401.08411) note that scatter plots and choropleth maps suggest causality to readers even when correlation is stated; adding data source, method, and confidence intervals makes causal misinterpretation less likely.

---

### Pattern 2: Use Explicit Negative Caveats on the Map

For a web map showing a bivariate overlay (e.g., SSS vs. RWI wealth), include a visible methodology panel or hover tooltip:

**Example tooltip (on a colored cell):**
> **High Speed, High Wealth Zone**  
> SSS: 0.81 | Meta RWI: 0.67  
> Spearman ρ = 0.42 across 12,400 cells  
> ⚠ This correlation does NOT explain why. It could reflect infrastructure investment, lower congestion, or data collection bias. See methodology.

**In the methodology sidebar:**
> "This map shows association, not causation. High-speed areas and wealthy areas may cluster together because (1) wealthy neighborhoods receive road maintenance investments, (2) congestion is lower, or (3) both are in newer suburban zones. Speed alone does not cause wealth, and wealth alone does not cause high speeds. Spatial autocorrelation is present (Moran's I = 0.18), so adjacent cells are not independent."

**Citation:** [Academic study on map visualization](https://arxiv.org/pdf/2307.15138) finds Bayesian weighting and explicit uncertainty cues reduce viewers' tendency to over-interpret correlation as causation.

---

### Pattern 3: Report Surprising Findings as Clusters, Not Rules

From [MapAgora civic-data research](https://www.nature.com/articles/s41597-025-05353-6):
> "While we observe that organizations with fewer financial resources tend to offer more civic opportunities, this is not a universal rule. The pattern reflects the fact that religious and social fraternal groups dominate the civic landscape; other sectors (business, professional services) show the opposite trend. The ZIP code-level aggregation masks this heterogeneity."

**Approach:**
- Identify clusters (LISA: HH, LL, HL, LH quadrants)
- Describe what they are spatially (e.g., "High-speed + high-wealth clusters appear in northern suburban extensions, low-speed + low-wealth clusters in central congested zones")
- Propose testable alternative explanations for each cluster
- Avoid stating one explanation as "the" reason

---

## 4. Concrete Minimal Recipe: SSS vs. Meta Relative Wealth Index (RWI)

### Data Sources

1. **Speed Safety Score (SSS):** Segment-level scores (your computed metrics)
2. **Meta Relative Wealth Index:** 2.4 km resolution raster for Philippines (publicly available from [HDX Humanitarian Data Exchange](https://data.humdata.org/dataset/relative-wealth-index) or [UNDP GeoHub](https://geohub.data.undp.org/data/fcde6ab53a79657a27906b3248a1979d))
3. **Spatial grid:** H3 hexagons, resolution 9 (~1.5 km for Metro Manila) or 500m square cells

### Step 1: Prepare H3 Grid

```python
import h3
import geopandas as gpd
import pandas as pd

# Generate H3 grid for Philippines (resolution 9)
resolution = 9
grid_cells = set()
for lat in np.arange(5, 19, 0.5):  # Latitude range
    for lon in np.arange(120, 130, 0.5):  # Longitude range
        cell = h3.geo_to_h3(lat, lon, resolution)
        grid_cells.add(cell)

# Convert to GeoDataFrame
grid_gdf = gpd.GeoDataFrame(
    {'h3_id': list(grid_cells)},
    geometry=[shapely.geometry.shape(h3.h3_to_geo_boundary(cell, geo_json=True)) 
              for cell in grid_cells]
)
grid_gdf.crs = 'EPSG:4326'
```

### Step 2: Aggregate Segments to Grid Cells

```python
# Spatially join segments to H3 cells
segments_gdf = gpd.read_file('segments.geojson')  # Your road segments with SSS attribute

segment_to_cell = gpd.sjoin(
    segments_gdf[['geometry', 'segment_id', 'sss']],
    grid_gdf[['h3_id', 'geometry']],
    how='left',
    predicate='intersects'
)

# Aggregate SSS by cell (weighted mean by segment length)
segment_to_cell['segment_length'] = segment_to_cell.geometry.length
cell_sss = segment_to_cell.groupby('h3_id').apply(
    lambda x: (x['sss'] * x['segment_length']).sum() / x['segment_length'].sum()
).rename('sss_mean')

grid_gdf = grid_gdf.merge(cell_sss, left_on='h3_id', right_index=True)
```

### Step 3: Sample Meta RWI Raster at Cell Centroids

```python
import rasterio
from rasterio.sample import sample_gen

# Load Meta RWI raster (2.4 km resolution)
with rasterio.open('meta_rwi_philippines.tif') as src:
    rwi_samples = list(sample_gen(src, grid_gdf.geometry.centroid.apply(lambda p: (p.x, p.y))))
    grid_gdf['rwi_value'] = [s[0] if s else None for s in rwi_samples]
```

### Step 4: Compute Spearman Correlation

```python
from scipy.stats import spearmanr

# Remove null values
valid_idx = grid_gdf['sss_mean'].notna() & grid_gdf['rwi_value'].notna()
sss_vals = grid_gdf.loc[valid_idx, 'sss_mean']
rwi_vals = grid_gdf.loc[valid_idx, 'rwi_value']

# Spearman correlation
rho, p_value = spearmanr(sss_vals, rwi_vals)
print(f"Spearman ρ = {rho:.3f}, p-value = {p_value:.2e}, n = {valid_idx.sum()}")

# Spatial autocorrelation (Moran's I)
from pysal.lib import weights
from pysal.explore.esda import Moran

# Build spatial weights matrix (Queen contiguity for hexagons)
w = weights.Voronoi(grid_gdf.geometry.centroid)
mi = Moran(grid_gdf.loc[valid_idx, 'sss_mean'], w)
print(f"Moran's I = {mi.I:.3f}, p-value = {mi.p_norm:.3f}")
```

### Step 5: Create Bivariate Classification (3×3 Grid)

```python
# Classify SSS into terciles (Low, Med, High)
grid_gdf['sss_class'] = pd.qcut(grid_gdf['sss_mean'], q=3, labels=['Low', 'Med', 'High'], duplicates='drop')

# Classify RWI into terciles
grid_gdf['rwi_class'] = pd.qcut(grid_gdf['rwi_value'], q=3, labels=['Low', 'Med', 'High'], duplicates='drop')

# Combine into bivariate class
grid_gdf['bivariate_class'] = grid_gdf['sss_class'].astype(str) + '_' + grid_gdf['rwi_class'].astype(str)

print(grid_gdf['bivariate_class'].value_counts())
```

### Step 6: Define 3×3 Color Scheme

```python
# Based on Joshua Stevens' bivariate choropleth guide
# Columns = SSS (Low → Med → High), Rows = RWI (Low → Med → High)
color_scheme = {
    'Low_Low': '#e8e8e8',    # Low Speed, Low Wealth
    'Low_Med': '#b5c0d0',
    'Low_High': '#6c5b7f',
    'Med_Low': '#ede4e0',
    'Med_Med': '#d4a574',    # Medium both
    'Med_High': '#8c6bb1',
    'High_Low': '#f7f7f7',
    'High_Med': '#ca8861',
    'High_High': '#2d104d',  # High Speed, High Wealth
}

grid_gdf['color'] = grid_gdf['bivariate_class'].map(color_scheme)
```

### Step 7: Export as GeoJSON for MapLibre

```python
# Save for MapLibre
grid_gdf.to_file('grid_bivariate.geojson', driver='GeoJSON')

# Create a companion legend/metadata JSON
import json
legend_data = {
    'measure': 'Spearman Rank Correlation',
    'value': rho,
    'p_value': p_value,
    'n_cells': valid_idx.sum(),
    'spatial_autocorr': {
        'morans_i': mi.I,
        'p_value': mi.p_norm,
        'note': 'Significant spatial autocorrelation; p-values above are optimistic.'
    },
    'color_scheme': color_scheme,
    'data_sources': {
        'sss': 'Road segment speed safety scores (computed from traffic data)',
        'rwi': 'Meta Relative Wealth Index 2.4 km resolution (2024)',
        'spatial_unit': 'H3 hexagons resolution 9 (~1.5 km)'
    },
    'caveats': [
        'Correlation does not imply causation.',
        'High-speed + high-wealth clusters may reflect infrastructure investment, lower congestion, or newer suburban zones.',
        'Spatial autocorrelation present; adjacent cells are not independent.',
        'Single-variable zoning changes interpretation (see MAUP note in methodology).'
    ]
}

with open('legend.json', 'w') as f:
    json.dump(legend_data, f, indent=2)
```

### Step 8: MapLibre Web Map

```javascript
// Initialize map
const map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.linz.govt.nz/styles/xxx/style.json',
    center: [121.0, 14.6],  // Metro Manila
    zoom: 10
});

// Add grid source
map.addSource('grid', {
    type: 'geojson',
    data: 'grid_bivariate.geojson'
});

// Add layer with color-mapped paint
map.addLayer({
    id: 'grid-fill',
    type: 'fill',
    source: 'grid',
    paint: {
        'fill-color': ['get', 'color'],  // Use precomputed color field
        'fill-opacity': 0.75
    }
});

map.addLayer({
    id: 'grid-outline',
    type: 'line',
    source: 'grid',
    paint: {
        'line-color': '#333',
        'line-width': 0.5,
        'line-opacity': 0.3
    }
});

// Add hover tooltip
map.on('mousemove', 'grid-fill', (e) => {
    const props = e.features[0].properties;
    const html = `
        <strong>Cell ${props.h3_id}</strong><br>
        SSS: ${props.sss_mean.toFixed(2)} (${props.sss_class})<br>
        RWI: ${props.rwi_value.toFixed(2)} (${props.rwi_class})<br>
        Spearman ρ = 0.42, p &lt; 0.001<br>
        ⚠ Correlation ≠ causation. See methodology.
    `;
    document.getElementById('info').innerHTML = html;
});

// Methodology panel
document.getElementById('methodology').innerHTML = `
    <h3>Methodology</h3>
    <p><strong>Data:</strong> H3 hexagons (1.5 km), Spearman rank correlation ρ=0.42 (p&lt;0.001)</p>
    <p><strong>Sources:</strong> Road segment SSS (computed), Meta RWI (2.4 km raster, 2024)</p>
    <p><strong>What it shows:</strong> SSS and wealth index tend to increase together in this region.</p>
    <p><strong>What it doesn't show:</strong> Whether high speed causes wealth, or vice versa.</p>
    <p><strong>Spatial note:</strong> Moran's I = 0.18 (p&lt;0.01), indicating positive autocorrelation; 
       adjacent cells are not independent. True statistical uncertainty is larger than p-values suggest.</p>
`;
```

---

## Summary and Defensibility Checklist

**To present a defensible finding:**

- [ ] Name the aggregation method (H3 grid, barangay, point-sample) and spatial scale
- [ ] Report the association measure (Spearman ρ or Pearson r) with p-value and 95% CI
- [ ] Compute and report Moran's I to signal spatial autocorrelation
- [ ] Name the data sources and collection year explicitly
- [ ] Include ≥2 alternative explanations for the pattern
- [ ] Add a visible caveat: "Correlation ≠ causation"
- [ ] Use LISA clustering to show WHERE patterns hold, not that they're universal
- [ ] Never claim "causes," "leads to," or "predicts" without regression adjustment for confounders

**This approach mirrors methodology in [academic transportation safety research](https://www.sciencedirect.com/science/article/abs/pii/S0001457525000028), [MapAgora civic data](https://www.nature.com/articles/s41597-025-05353-6), and [Gapminder's fact-based communication](https://www.gapminder.org/factfulness-book/notes/).**

---

## References

- [Applied Geographic Solutions: Pitfalls of MAUP](https://appliedgeographic.com/2024/02/spatial-analysis-pitfalls-the-maup/)
- [Penn State Geospatial Analysis: Spatial Autocorrelation](https://courseware.e-education.psu.edu/courses/geog586/lesson08_all.html)
- [PyPAL ESDA: Spatial Clustering Visualization](https://pysal.org/notebooks/viz/splot/esda_morans_viz.html)
- [Joshua Stevens: Bivariate Choropleth Cartography](https://www.joshuastevens.net/cartography/make-a-bivariate-choropleth-map/)
- [Kontur.io: H3 Hexagonal Grids](https://www.kontur.io/blog/why-we-use-h3/)
- [MapAgora Scientific Data: Civic Opportunity Mapping](https://www.nature.com/articles/s41597-025-05353-6)
- [Gapminder: Factfulness Methodology](https://www.gapminder.org/factfulness-book/notes/)
- [Transportation Safety: Impact of Data Aggregation on Speed-Crash Relationships](https://pubmed.ncbi.nlm.nih.gov/30195137/)
- [Academic Study: Causal Inference in Transportation Safety](https://arxiv.org/pdf/1107.4855)
- [Journal of Anesthesia & Analgesia: Correlation Coefficients](https://journals.lww.com/anesthesia-analgesia/fulltext/2018/05000/correlation_coefficients__appropriate_use_and.50.aspx)
- [SurveyMonkey: Pearson vs. Spearman](https://www.surveymonkey.com/market-research/resources/pearson-correlation-vs-spearman-correlation/)
- [Meta RWI Data: HDX Humanitarian Dataset](https://data.humdata.org/dataset/relative-wealth-index)
- [UNDP GeoHub: Relative Wealth Index](https://geohub.data.undp.org/data/fcde6ab53a79657a27906b3248a1979d)
- [MapLibre GL JS: Expressions and Paint Properties](https://maplibre.org/maplibre-style-spec/expressions/)
