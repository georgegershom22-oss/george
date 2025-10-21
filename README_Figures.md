# Figure 3.9A–D: Scientific Visualization Suite

## Overview

This repository contains a Python-based implementation for generating high-quality scientific figures with precise styling specifications. The figures illustrate acoustic wave propagation phenomena including mode conversion, interfacial scattering, and stratification effects.

## Programming Language Choice: Python with Matplotlib

**Why Python?**

Python with matplotlib was chosen as the optimal tool for this visualization task because:

1. **Precision Control**: Matplotlib provides exact control over every visual element (dimensions, colors, fonts, line weights, spacing)
2. **Export Quality**: Native support for both raster (PNG at exact DPI) and vector (PDF with embedded fonts) formats
3. **Scientific Standard**: Industry-standard for scientific visualization with extensive documentation
4. **Reproducibility**: Script-based approach ensures consistent, version-controlled outputs
5. **Mathematical Typography**: Excellent LaTeX-like math rendering for scientific notation
6. **Flexibility**: Supports complex layouts (stacked panels, heatmaps, annotations, overlays)

## Generated Figures

### Figure 3.9A — Frequency Sweep Signatures
- **Content**: Transmission loss vs. normalized frequency (ω/N)
- **Key Features**: 
  - Classical baseline (homogeneous medium)
  - Continuous stratification with conversion bump at ω/N ≈ 1
  - Interfacial scattering notches overlaid on conversion bump
  - Amber conversion band overlay (0.8 ≤ ω/N ≤ 1.2)
- **Files**: `Figure_3_9A.png`, `Figure_3_9A.pdf`

### Figure 3.9B — Angle–Frequency Plate
- **Content**: 2D heatmap showing notch behavior across angle and frequency
- **Key Features**:
  - Interface-induced notches that shift with incidence angle θ
  - Fixed conversion band centered at ω/N ≈ 1 (angle-independent)
  - Perceptual colormap with labeled colorbar
- **Files**: `Figure_3_9B.png`, `Figure_3_9B.pdf`

### Figure 3.9C — Time Correlation
- **Content**: Dual-panel time series showing coherence and Richardson number
- **Key Features**:
  - Top panel: Array coherence γ²(t) for band near ω/N ≈ 1
  - Bottom panel: Richardson number Ri(t)
  - Synchronized low-Ri burst annotations spanning both panels
  - Conversion-band dip visualization
- **Files**: `Figure_3_9C.png`, `Figure_3_9C.pdf`

### Figure 3.9D — Mechanism-Share Waterfall
- **Content**: 100% stacked column chart showing loss mechanism contributions
- **Key Features**:
  - Four canonical regimes (High-Ri continuous, Marginal-Ri continuous, Layered sharp, Layered diffuse)
  - Color-coded mechanism shares (Classical, Conversion, Interfacial, Shear)
  - In-band numeric labels for precise values
- **Files**: `Figure_3_9D.png`, `Figure_3_9D.pdf`

## Style Specifications

All figures adhere to consistent house style:

### Canvas & Typography
- **Dimensions**: 2000 × 1400 px (landscape), white background
- **Typeface**: Helvetica/Arial (fallback to DejaVu Sans)
- **Font Sizes**:
  - Titles: 28 pt bold
  - Axis labels: 22 pt
  - Tick labels: 16 pt
  - In-plot notes: 18–20 pt
  - Legends: 16–18 pt
  - Captions: 15 pt italic

### Color Palette
- **Classical viscous–thermal**: #6B7280 (dark gray)
- **Mode conversion**: #F4A261 (amber), #C06A00 (darker amber for emphasis)
- **Interfacial scattering**: #6A4C93 (purple)
- **Shear-mediated/baroclinic**: #2A9D8F (teal)
- **Primary TL/measurement**: #1F78B4 (deep blue)
- **Grid**: #E5E7EB (light gray, 0.8 px)
- **Guides**: #9CA3AF (faint gray, 1.2 px)

### Line Specifications
- **Primary curves**: 3 px, round caps/joins
- **Secondary curves**: 2–2.5 px
- **Dashed lines**: 8–6 pattern
- **Dotted guides**: 1–1.2 px

### Export Formats
- **PNG**: 300 DPI, high-resolution raster
- **PDF**: Vector format with embedded TrueType fonts

## Usage

### Running the Script

```bash
# Install dependencies
pip3 install numpy matplotlib

# Generate all figures
python3 generate_figure_3_9.py
```

### Output

The script generates 8 files:
- 4 PNG files (300 DPI, suitable for publications)
- 4 PDF files (vector format, scalable without quality loss)

### Customization

The script is modular and well-documented. Key parameters are defined at the top:

```python
# Canvas dimensions
DPI = 300
WIDTH_PX = 2000
HEIGHT_PX = 1400

# Typography
TITLE_SIZE = 28
AXIS_LABEL_SIZE = 22
TICK_LABEL_SIZE = 16

# Colors (all in one place)
COLOR_CLASSICAL = '#6B7280'
COLOR_CONVERSION = '#F4A261'
# ... etc
```

To modify a specific figure, locate its function:
- `create_figure_3_9A()` — Frequency sweep
- `create_figure_3_9B()` — Angle–frequency heatmap
- `create_figure_3_9C()` — Time correlation
- `create_figure_3_9D()` — Mechanism shares

## Technical Details

### Dependencies
- **numpy** (≥1.20): Numerical computations and array generation
- **matplotlib** (≥3.3): Plotting and visualization

### Key Implementation Features

1. **Precise Positioning**: All elements positioned with exact pixel/point coordinates
2. **Mathematical Notation**: LaTeX-style math rendering using matplotlib's mathtext
3. **Font Embedding**: PDF exports include embedded fonts for cross-platform consistency
4. **Grid Alignment**: GridSpec for precise multi-panel layouts
5. **Color Management**: Hex colors for exact reproduction
6. **Anti-aliasing**: High-quality rendering with proper line caps/joins

### Data Generation

The script generates synthetic but realistic data that matches the qualitative behavior described in the specifications:

- **Frequency sweeps**: Gaussian bumps and notches with controlled FWHM
- **Heatmaps**: 2D arrays with angle-dependent features
- **Time series**: Periodic signals with superimposed transient events
- **Stacked charts**: Normalized shares summing to unity

## Quality Checklist

Before using the figures, verify:

- ✅ Consistent ω/N range (0.2–2.2) across frequency plots
- ✅ Amber conversion band appears at 0.8 ≤ ω/N ≤ 1.2 where applicable
- ✅ Heatmap polarity consistent (darker = higher values)
- ✅ Mechanism shares sum to 1.0 for each regime
- ✅ Legends visible and not obscuring data features
- ✅ All labels readable at print resolution
- ✅ Both PNG (300 DPI) and PDF (vector) exports successful
- ✅ Fonts properly embedded in PDF

## Citation

If using these figures or the generation script, please cite appropriately and ensure compliance with your publication's figure guidelines.

## License

This script is provided as-is for scientific visualization purposes. Modify and adapt as needed for your research.

---

**Generated**: 2025-10-21  
**Python Version**: 3.x  
**matplotlib Version**: 3.10+  
**numpy Version**: 2.3+
