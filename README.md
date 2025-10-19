# Shear-Dominance Analysis Figures

This repository contains Python scripts to generate publication-quality figures for shear-dominance analysis in stratified turbulence.

## Generated Figures

### Figure 3.6A — Shear-dominance index on (Ri, ω/N)
- **File**: `figure_3_6a.py`
- **Description**: Heatmap showing shear-dominance index with bright regions indicating where shear-mediated loss dominates
- **Features**:
  - Viridis colormap (darker = higher intensity)
  - Conversion window overlay (amber band at 0.8 ≤ ω/N ≤ 1.2)
  - Marginal stability line at Ri = 0.25
  - Peak intensity near (Ri ≈ 0.4, ω/N ≈ 1)

### Figure 3.6B — Time–frequency TL fluctuation intensity
- **File**: `figure_3_6b.py` 
- **Description**: Dual-panel comparison showing different Richardson number regimes
- **Left Panel**: High Ri - narrow conversion-band modulation
- **Right Panel**: Marginal Ri - intermittent broadband bursts
- **Features**:
  - Shared colorbar for intensity comparison
  - Time axis: 0-60 seconds
  - Frequency axis: ω/N from 0.2 to 2.2
  - Conversion band overlay on both panels

### Figure 3.6C — Coherence loss and spectral broadening
- **File**: `figure_3_6c.py`
- **Description**: Dual-panel analysis of coherence and spectral properties
- **Left Panel**: Coherent fraction vs Ri with variability region
- **Right Panel**: PSD comparison showing bandwidth differences
- **Features**:
  - Monotonic decrease in coherent fraction with decreasing Ri
  - Localized dip near marginal Ri (≈ 0.3-0.5)
  - Bandwidth indicators showing spectral broadening

## Usage

### Generate Individual Figures
```bash
python3 figure_3_6a.py  # Generate Figure 3.6A
python3 figure_3_6b.py  # Generate Figure 3.6B  
python3 figure_3_6c.py  # Generate Figure 3.6C
```

### Generate All Figures
```bash
python3 generate_all_figures.py
```

## Output Formats

Each figure is saved in three formats:
- **PNG** (300 DPI): High-quality raster for presentations and drafts
- **PDF** (vector): Publication-ready scalable graphics with embedded fonts
- **SVG** (vector): Web-compatible format for further editing

## Dependencies

- Python 3.7+
- matplotlib
- numpy
- scipy

Install dependencies:
```bash
pip install matplotlib numpy scipy
```

## Styling Specifications

All figures follow consistent styling:
- **Canvas**: 1800×1200 px (landscape), white background
- **Typography**: Helvetica/Arial fallback; title 28pt bold; axis labels 22pt; tick labels 16pt
- **Grid**: Light gray (#E5E7EB), 0.8px weight, major ticks only
- **Colors**: 
  - Deep blue (#1F78B4) for primary data
  - Steel blue (#457B9D) for secondary/variability
  - Amber (#F4A261) for conversion window overlay
  - Light gray (#E5E7EB) for grid
  - Medium gray (#9CA3AF) for guide lines
- **Line weights**: Axes 2px, curves 3px, dotted guides 1-1.2px

## Physical Interpretation

These figures illustrate key aspects of shear-dominance in stratified turbulence:

1. **Shear-dominance peaks** near the conversion frequency (ω/N ≈ 1) under marginal Richardson numbers
2. **Spectral confinement** occurs at high Ri, while **broadband activity** emerges at marginal Ri
3. **Coherence loss** and **increased variability** characterize the transition to marginal stability

The analysis captures the transition from stable, coherent dynamics to intermittent, broadband turbulent activity as the Richardson number decreases toward marginal stability.