# Scientific Thesis Figures Generator

This project generates four publication-quality scientific figures (3.8A-D) for a thesis on acoustic wave propagation in stratified media.

## Features

- **Publication-ready quality**: 2000×1400 px landscape format with white background
- **Consistent styling**: Helvetica/Arial fonts with standardized sizes across all figures
- **Vector and raster output**: Both PDF (vector) and PNG (300 DPI) formats
- **Professional color scheme**: Carefully selected colors for different mechanisms

## Generated Figures

### Figure 3.8A - Dominant Pathway Map
- Heatmap showing conversion-dominant vs shear-dominant regions in (Ri, ω/N) space
- Amber indicates conversion dominance, teal indicates shear dominance
- Includes activity contours and the characteristic conversion band

### Figure 3.8B - Layered Regime Map
- Notch strength prediction in (C_Z, kδ) parameter space
- Shows how impedance contrast and interface thickness affect comb-like notches
- Log-scale x-axis for interface thickness parameter

### Figure 3.8C - Apparent Attenuation Curves
- Frequency-dependent attenuation for different Richardson numbers
- Demonstrates peak broadening and skirt growth with decreasing Ri
- Four representative curves from stable to near-critical conditions

### Figure 3.8D - Notch Depth vs Interface Thickness
- Shows decay of notch depth with increasing interface thickness
- Multiple curves for different impedance contrasts
- Log-scale x-axis with regime annotations

## Requirements

- Python 3.7+
- matplotlib 3.9.2
- numpy 1.26.4
- scipy 1.14.1
- pillow 10.4.0

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Generate all figures:
```bash
python3 generate_figures.py
```

This will create 8 files:
- `figure_3_8A.pdf` and `figure_3_8A.png`
- `figure_3_8B.pdf` and `figure_3_8B.png`
- `figure_3_8C.pdf` and `figure_3_8C.png`
- `figure_3_8D.pdf` and `figure_3_8D.png`

## Technical Details

### Color Palette
- **Amber** (#F4A261): Mode conversion mechanism
- **Teal** (#2A9D8F): Shear-mediated mechanism
- **Purple** (#6A4C93): Interfacial scattering
- **Gray** (#6B7280): Classical viscous-thermal
- **Grid** (#E5E7EB): Light gray for major gridlines

### Typography
- **Titles**: 28pt bold
- **Axis labels**: 22pt
- **Tick labels**: 16pt
- **In-plot notes**: 18-20pt
- **Legends**: 16-18pt
- **Captions**: 15pt italic

### Common Elements
- Conversion window overlay: 0.8 ≤ ω/N ≤ 1.2 (translucent amber)
- Frequency axis: ω/N ∈ [0.2, 2.2] with specific tick positions
- Grid: Light gray, 0.8px width, major ticks only

## Physics Context

These figures illustrate acoustic wave propagation in stratified oceanic environments:
- **Conversion**: Energy transfer between wave modes
- **Shear**: Shear-mediated attenuation mechanisms
- **Richardson number (Ri)**: Stability parameter
- **Impedance contrast (C_Z)**: Acoustic property mismatch
- **Interface thickness (kδ)**: Transition layer scale

## Output Quality

- **PDF files**: Vector format, suitable for publication
- **PNG files**: 300 DPI, suitable for presentations and drafts
- **Font embedding**: TrueType fonts embedded in PDFs
- **Color fidelity**: Consistent RGB values across all figures

## License

This code is provided for academic use in thesis preparation.