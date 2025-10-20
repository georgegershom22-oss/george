# Scientific Figures 3.7A-C1 - Generation Summary

## Generated Files

All figures have been successfully generated in both **SVG (vector)** and **PNG (raster)** formats:

### Figure 3.7A - Composite Attenuation Concept (Block Diagram)
- `figure_3_7A.svg` (128 KB) - Vector format
- `figure_3_7A.png` (213 KB) - Raster format
- **Description**: Block diagram showing how similarity variables feed a mechanism-weighting module to produce shares that combine into composite attenuation predictions

### Figure 3.7B1 - Mechanism Shares vs ω/N (High Ri)
- `figure_3_7B1.svg` (125 KB) - Vector format
- `figure_3_7B1.png` (146 KB) - Raster format
- **Description**: 100% stacked area chart showing mechanism shares under high Richardson number (stable stratification) with continuous background

### Figure 3.7B2 - Mechanism Shares vs ω/N (Marginal Ri)
- `figure_3_7B2.svg` (125 KB) - Vector format
- `figure_3_7B2.png` (150 KB) - Raster format
- **Description**: 100% stacked area chart showing expanded shear-mediated contribution at marginal Richardson number

### Figure 3.7C1 - Mechanism Shares vs kδ
- `figure_3_7C1.svg` (133 KB) - Vector format
- `figure_3_7C1.png` (153 KB) - Raster format
- **Description**: 100% stacked area chart showing how interfacial share depends on interface sharpness parameter kδ at fixed ω/N=1

## Style Specifications

All figures follow the shared house style:

- **Canvas**: 2000×1400 px (landscape), white background
- **Typeface**: Helvetica/Arial
  - Titles: 28 pt bold
  - Axis labels: 22 pt
  - Tick labels: 16 pt
  - Annotations: 18-20 pt
  - Caption: 15 pt italic
- **Grid**: Light grey #E5E7EB (0.8 px)
- **Color scheme** (consistent across all panels):
  - Classical viscous-thermal: #6B7280 (grey)
  - Mode conversion: #F4A261 (amber)
  - Interfacial scattering: #6A4C93 (purple)
  - Shear-mediated/baroclinic: #2A9D8F (teal)

## Python Scripts

The following Python scripts can be used to regenerate or modify the figures:

- `figure_3_7A.py` - Generates Figure 3.7A
- `figure_3_7B1.py` - Generates Figure 3.7B1
- `figure_3_7B2.py` - Generates Figure 3.7B2
- `figure_3_7C1.py` - Generates Figure 3.7C1

### Requirements
```bash
pip install matplotlib numpy
```

### Regenerate Figures
```bash
python3 figure_3_7A.py
python3 figure_3_7B1.py
python3 figure_3_7B2.py
python3 figure_3_7C1.py
```

## Notes

- SVG files are recommended for publication as they are true vector graphics and scale perfectly
- PNG files are provided as raster previews at 100 DPI
- All figures maintain the exact specifications from the style guide
- Mechanism shares are normalized to sum to 1.0 at all points
- The conversion window (0.8 ≤ ω/N ≤ 1.2) is marked with a translucent amber band where applicable
