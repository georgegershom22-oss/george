# Figure 3.6A–C: Combined Publication-Quality Scientific Figure

This repository contains the implementation for generating a combined scientific figure (3.6A–C) showing shear-mediated attenuation effects in stratified flows.

## Generated Files

### Outputs
- `/workspace/out/figures/figure_3_6_combined.png` - High-resolution PNG (1800×1200 px)
- `/workspace/out/figures/figure_3_6_combined.svg` - Vector SVG format

### Source Code
- `figs/house_style.py` - Shared styling module with publication standards
- `figs/figure_3_6_combined.py` - Main script generating the combined figure

## Figure Description

The combined figure contains three main panels:

**Figure 3.6A** - Shear-dominance index heatmap on (Ri, ω/N) parameter space
- Shows where shear-mediated attenuation dominates composite loss
- Bright regions indicate higher shear-dominance index (0-1 scale)
- Features conversion window overlay and marginal stability guide

**Figure 3.6B** - Time-frequency TL fluctuation intensity comparison
- Left panel: High Ri (narrow conversion band modulation)
- Right panel: Marginal Ri (intermittent broadband bursts)
- Shared colorbar for direct comparison

**Figure 3.6C** - Coherence loss and spectral broadening analysis
- Top right: Coherent fraction vs Ri with variability band
- Bottom: PSD comparison showing spectral broadening under marginal Ri

## House Style Features

- Canvas: 1800 × 1200 px landscape, white background
- Typography: Sans-serif fonts with specified point sizes (28pt titles, 22pt labels, etc.)
- Grid: Light gray (#E5E7EB), 0.8px thickness
- Color palette: Color-blind robust (deep blue, steel blue, contrast magenta)
- Heatmaps: Cividis colormap with darker = higher intensity
- Conversion window: Translucent amber band with dotted centerline

## Usage

```bash
cd figs
python3 figure_3_6_combined.py
```

The script will generate both PNG and SVG versions in the output directory.

## Dependencies

- Python 3.x
- numpy
- matplotlib

Install with: `pip install numpy matplotlib`