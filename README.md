# Scientific Figures 3.9A-D Generation

This project generates publication-quality scientific figures following precise styling specifications for Figure 3.9A-D series.

## Generated Files

### Figures
- **figure_3_9a.png/pdf** - Frequency sweep signatures
- **figure_3_9b.png/pdf** - Angle-frequency plate heatmap  
- **figure_3_9c.png/pdf** - Time correlation with stacked panels
- **figure_3_9d.png/pdf** - Mechanism-share waterfall chart

### Code
- **generate_figures.py** - Main Python script for figure generation

## Shared House Style Specifications

### Canvas & Typography
- **Canvas**: 2000 × 1400 px (landscape), white background
- **Typeface**: DejaVu Sans (Helvetica/Arial equivalent)
- **Font sizes**: Titles 28pt bold, axis labels 22pt, tick labels 16pt, in-plot notes 18-20pt, legends 16-18pt, captions 15pt italic
- **Grid**: Light gray #E5E7EB (0.8px), major ticks only

### Color Palette
- **Classical viscous-thermal**: #6B7280 (dark gray)
- **Mode conversion**: #F4A261 (amber), darker lines #C06A00
- **Interfacial scattering**: #6A4C93 (purple)  
- **Shear-mediated/baroclinic**: #2A9D8F (teal)
- **Primary data curve**: #1F78B4 (deep blue)
- **Conversion window**: Translucent amber (#F4A261, 18-22% opacity) for 0.8 ≤ ω/N ≤ 1.2
- **Centerline**: #9CA3AF dotted at ω/N = 1

### Line Styling
- **Primary curves**: 3px weight
- **Secondary curves**: 2-2.5px weight  
- **Dashed lines**: 8-6 dash pattern
- **Dotted guides**: 1-1.2px weight
- **Round caps/joins** throughout

## Figure Descriptions

### Figure 3.9A - Frequency Sweep Signatures
Shows conversion bump (continuous stratification only) and the same bump overlaid with interfacial notches (continuous + interfaces). Features:
- Classical baseline (gray dashed, gently rising)
- Continuous stratification (blue solid with broad bump at ω/N ≈ 1)
- Continuous + interfaces (purple with narrow spectral notches)
- Amber conversion band overlay (0.8-1.2)
- Annotated notch spacing

### Figure 3.9B - Angle-Frequency Plate  
2D heatmap showing notch motion with angle while conversion band remains fixed near f ≈ N. Features:
- Interface-induced notches that shift with incidence angle θ
- Fixed horizontal conversion band at ω/N ≈ 1
- Perceptual colormap (darker = higher transmission loss)
- Colorbar for transmission loss scale

### Figure 3.9C - Time Correlation
Two stacked panels showing array coherence vs Richardson number over time. Features:
- Top panel: Array coherence γ²(t) for ω/N ≈ 1 band
- Bottom panel: Richardson number Ri(t) 
- Persistent conversion-band dip in coherence
- Sharp coherence drops aligned with low-Ri bursts
- Translucent teal bands marking low-Ri episodes

### Figure 3.9D - Mechanism-Share Waterfall
Stacked bar chart showing mechanism shares across four canonical regimes. Features:
- Four regime categories with 100% stacked bars
- Color-coded mechanism shares (Classical, Conversion, Interfacial, Shear)
- Quantitative proportions summing to unity
- In-bar value labels where space permits

## Usage

```bash
python3 generate_figures.py
```

## Requirements
- Python 3.x
- matplotlib
- numpy  
- scipy

## Export Formats
All figures are exported in both:
- **PNG**: 300 DPI for high-quality raster output
- **PDF**: Vector format with embedded fonts for publication

## Quality Control Checklist
✅ Consistent ω/N range and amber conversion band across frequency plots  
✅ Consistent heatmap polarity (darker = higher) across all plates
✅ Mechanism shares sum to 1.0 for each regime column
✅ Legends positioned to avoid obscuring features
✅ All labels readable at publication print width
✅ Both PNG (300 DPI) and vector PDF exports with embedded fonts