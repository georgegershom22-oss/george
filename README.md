# Scientific Figure Series 3.9A-D

High-precision scientific visualizations for acoustic transmission loss analysis, created with Python and matplotlib.

## Overview

This project generates a series of four scientific figures (3.9A through 3.9D) that visualize various aspects of acoustic transmission loss and wave propagation in stratified media. The figures follow a strict house style with precise specifications for dimensions, typography, colors, and layout.

## Figures Produced

### Figure 3.9A - Frequency Sweep Signatures
- Shows transmission loss vs normalized frequency (ω/N)
- Displays three traces: classical baseline, continuous stratification with conversion bump, and continuous + interfaces with spectral notches
- Features amber conversion band overlay at 0.8 ≤ ω/N ≤ 1.2

### Figure 3.9B - Angle-Frequency Plate  
- 2D heatmap showing notch trajectories that shift with incidence angle
- Horizontal amber band shows angle-independent conversion region
- Demonstrates how interface-induced notches vary with obliquity angle θ

### Figure 3.9C - Time Correlation
- Dual-panel plot showing array coherence γ²(t) and Richardson number Ri(t)
- Highlights correlation between low-Ri bursts and coherence drops
- Features vertical alignment guides and translucent overlay bands

### Figure 3.9D - Mechanism-Share Waterfall
- Stacked bar chart showing relative contributions of four loss mechanisms
- Compares four canonical regimes: High-Ri continuous, Marginal-Ri continuous, Layered sharp, Layered diffuse
- Color-coded by mechanism: Classical (gray), Conversion (amber), Interfacial (purple), Shear (teal)

## Technical Specifications

### Canvas & Typography
- **Dimensions**: 2000 × 1400 px (landscape orientation)
- **Background**: White
- **Typeface**: Helvetica/Arial (or DejaVu Sans fallback)
  - Titles: 28 pt bold
  - Axis labels: 22 pt
  - Tick labels: 16 pt
  - In-plot notes: 18-20 pt
  - Captions: 15 pt italics

### Color Palette
- Classical viscous-thermal: `#6B7280` (dark gray)
- Mode conversion: `#F4A261` (amber)
- Mode conversion dark: `#C06A00` (darker amber)
- Interfacial scattering: `#6A4C93` (purple)
- Shear-mediated/baroclinic: `#2A9D8F` (teal)
- Primary data trace: `#1F78B4` (deep blue)
- Grid lines: `#E5E7EB` (light gray)

### Export Formats
- PNG at 300 DPI for print
- Vector PDF with embedded fonts

## Installation

```bash
# Install required packages
pip install -r requirements.txt
```

Requirements:
- numpy >= 1.21.0
- matplotlib >= 3.5.0
- scipy >= 1.7.0

## Usage

```bash
# Generate all four figures
python3 figure_3_9_series.py
```

This will create 8 files in the current directory:
- `figure_3_9A.png` and `figure_3_9A.pdf`
- `figure_3_9B.png` and `figure_3_9B.pdf`
- `figure_3_9C.png` and `figure_3_9C.pdf`
- `figure_3_9D.png` and `figure_3_9D.pdf`

## Code Structure

The main script `figure_3_9_series.py` contains:
- Shared configuration constants for colors, fonts, and line styles
- Helper functions for common styling operations
- Four figure generation functions (`create_figure_3_9A()` through `create_figure_3_9D()`)
- Main execution function that generates and exports all figures

## Quality Assurance

All figures maintain:
- Consistent ω/N range and amber conversion band placement
- Uniform color palette across the series
- Proper sum-to-unity for stacked shares in Figure 3.9D
- Readable legends and labels at print resolution
- Clean vector graphics with embedded fonts

## License

This scientific visualization code is provided as-is for research and educational purposes.