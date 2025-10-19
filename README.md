# Figure 3.6 Series - Shear Dominance Analysis

This repository contains Python scripts to generate publication-quality figures for shear dominance analysis as specified in the detailed requirements.

## Figures Overview

### Figure 3.6A - Shear-dominance index on (Ri, ω/N)
- **Purpose**: Visualizes regions where shear-mediated loss is most influential
- **Key Features**:
  - Heatmap with bright horizontally elongated island centered at (Ri≈0.4, ω/N≈1)
  - Translucent amber conversion window overlay (0.8≤ω/N≤1.2)
  - Perceptually uniform colormap (Viridis)
  - Optional dashed guide at Ri=0.25 marking marginal stability

### Figure 3.6B - Time-frequency TL fluctuation intensity
- **Purpose**: Compares fluctuation patterns between high and marginal Ri conditions
- **Left Panel**: High Ri with narrow conversion band activity
- **Right Panel**: Marginal Ri with intermittent broadband bursts
- **Key Features**:
  - Shared colorbar and y-axis
  - Amber conversion band overlay on both panels
  - Contrasting patterns demonstrating regime differences

### Figure 3.6C - Coherent fraction and PSD broadening
- **Purpose**: Shows coherence loss and spectral changes with decreasing Ri
- **Left Panel**: Coherent fraction vs Ri curve with localized dip
- **Right Panel**: PSD comparison between high and marginal Ri
- **Key Features**:
  - Deep blue monotone decreasing curve with shaded variability region
  - Bandwidth comparison arrows showing spectral broadening
  - Clear demonstration of marginal Ri effects

## Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- matplotlib >= 3.7.2
- numpy >= 1.24.3
- scipy >= 1.11.1

## Usage

### Generate All Figures
```bash
python generate_all_figures.py
```

This will create a `figures/` directory containing all three figures in PNG, PDF, and SVG formats.

### Generate Individual Figures
```bash
python figure_3_6a.py  # Shear-dominance index heatmap
python figure_3_6b.py  # Time-frequency TL fluctuation
python figure_3_6c.py  # Coherent fraction & PSD broadening
```

## Output Formats

Each figure is saved in three formats:
- **PNG**: 300 DPI raster images for presentations and quick viewing
- **PDF**: Vector format for publication-quality prints
- **SVG**: Editable vector format for further customization in vector graphics software

## Design Specifications

All figures follow these consistent design principles:
- **Canvas**: 1800×1200 px (landscape), white background
- **Typography**: Helvetica/Arial family
  - Title: 28 pt bold
  - Axis labels: 22 pt
  - Tick labels: 16 pt
  - In-plot notes: 18-20 pt
- **Grid**: Light gray (#E5E7EB), 0.8 px, major ticks only
- **Colors**: Colorblind-safe palette
  - Deep blue: #1F78B4
  - Steel blue: #457B9D
  - Amber: #F4A261 (20% opacity for overlays)
  - Gray: #9CA3AF (dotted lines)
- **Line weights**: 
  - Axes: 2 px
  - Curves: 3 px
  - Guides: 1-1.2 px

## Physics Context

These figures illustrate key aspects of shear-mediated turbulent loss in stratified flows:
- **Shear Dominance Index (SDI)**: Quantifies where shear-driven processes dominate energy transfer
- **Richardson Number (Ri)**: Ratio of stratification to shear strength
- **Frequency Ratio (ω/N)**: Normalized frequency relative to buoyancy frequency
- **Conversion Band**: Critical frequency range (0.8-1.2) where mode conversion occurs

## Notes

- Figures use synthetic data that qualitatively represents the expected physics
- Actual experimental/simulation data can be substituted by modifying the data generation functions
- Color maps are perceptually uniform and colorblind-friendly
- All text remains legible at typical publication column widths

## License

This code is provided as-is for academic and research purposes.