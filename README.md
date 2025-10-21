# Scientific Figures 3.8A-D for Thesis

This directory contains publication-quality scientific figures generated according to the shared house style specifications.

## Generated Figures

### Figure 3.8A - Predicted Dominant Pathway Map
- **Description**: Predicted dominant pathway in (Ri, ω/N) for continuous stratification
- **Type**: Heatmap with contours and overlays
- **Key Features**: 
  - Conversion-dominant basin near ω/N ≈ 1 at higher Ri
  - Shear-dominant tongue at low Ri
  - Amber conversion window overlay (0.8 ≤ ω/N ≤ 1.2)
  - Activity contours for both mechanisms

### Figure 3.8B - Layered Regime Map
- **Description**: Notch strength in (CZ, kδ) parameter space
- **Type**: Heatmap with isolines and inset illustrations
- **Key Features**:
  - Log scale for kδ axis (0.1 to 3)
  - Strength increases with CZ, decreases with kδ
  - Three isolines (weak/moderate/strong)
  - Mini TL(f) sketches showing comb patterns

### Figure 3.8C - Apparent Attenuation Curves
- **Description**: Qualitative scaling vs ω/N for selected Ri values
- **Type**: Line plot with multiple curves
- **Key Features**:
  - Four Ri values: 1.5, 1.0, 0.6, 0.3
  - Peak broadening and skirt growth as Ri decreases
  - Conversion window overlay
  - Annotated trends

### Figure 3.8D - Notch Depth Analysis
- **Description**: Notch depth vs kδ for several impedance contrasts
- **Type**: Line plot with curve family
- **Key Features**:
  - Log scale for kδ axis
  - Four CZ values: 0.05, 0.10, 0.20, 0.30
  - Monotonic decrease with kδ
  - Regime labels (thin → resonant → thick)

## Style Specifications

- **Canvas**: 2000×1400 px (landscape), white background
- **Typeface**: Helvetica/Arial family
- **Font Sizes**:
  - Titles: 28 pt bold
  - Axis labels: 22 pt
  - Tick labels: 16 pt
  - In-plot notes: 18-20 pt
  - Captions: 15 pt italic
- **Grid**: Light gray #E5E7EB (0.8 px), major ticks only
- **Line weights**: Primary curves 3 px; secondary 2-2.5 px
- **Colors**: Consistent mechanism colors throughout thesis

## File Formats

Each figure is available in three formats:
- **PDF**: Vector format for high-quality printing
- **PNG**: Raster format at 300 dpi for drafts/presentations  
- **SVG**: Vector format for web/editing compatibility

## Usage

To regenerate all figures:
```bash
python3 generate_all_figures.py
```

To generate individual figures:
```bash
python3 figure_3_8a.py  # Dominant pathway map
python3 figure_3_8b.py  # Layered regime map
python3 figure_3_8c.py  # Attenuation curves
python3 figure_3_8d.py  # Notch depth analysis
```

## Dependencies

- Python 3.x
- matplotlib
- numpy
- scipy

Install with: `pip install matplotlib numpy scipy`

## Quality Control Checklist

✅ Consistent ω/N range and amber band across frequency-based figures  
✅ Correct colormap polarity (darker = stronger)  
✅ Log axis formatting on kδ with readable tick labels  
✅ Legends positioned to avoid obscuring key features  
✅ All text ≥16pt at final print size  
✅ Vector formats (PDF/SVG) with embedded fonts  
✅ 300 DPI PNG versions for drafts  

## Notes

- All figures use synthetic/schematic data as specified
- Mathematical notation follows LaTeX conventions
- Color scheme maintains consistency with thesis style guide
- Figures are ready for direct inclusion in thesis document