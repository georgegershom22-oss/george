# Scientific Figures 3.8A-D for Thesis

## Summary

I've generated all four publication-quality scientific figures using **Python with matplotlib**, which is the industry-standard tool for creating precise, reproducible scientific visualizations.

## Generated Files

All figures are available in both formats:
- **PDF** (vector format - perfect for LaTeX/publication, scalable without quality loss)
- **PNG** (high-resolution raster at 300 DPI - for presentations/web)

### Figure 3.8A — Dominant Pathway Map
**Files:** `figure_3_8A.pdf`, `figure_3_8A.png`

A heatmap showing the dominant energy dissipation pathway in (Ri, ω/N) parameter space for continuous stratification:
- Custom amber→gray→teal colormap (0 = conversion-dominant, 1 = shear-dominant)
- Solid amber contours marking conversion high-activity zones
- Dashed teal contours marking shear high-activity zones
- Translucent amber band overlay at 0.8 ≤ ω/N ≤ 1.2
- Dotted centerline at ω/N = 1

### Figure 3.8B — Notch Strength Regime Map
**Files:** `figure_3_8B.pdf`, `figure_3_8B.png`

A heatmap in (Cz, kδ) space showing predicted notch strength:
- Log-scale x-axis for interface thickness kδ
- Heat intensity increases with impedance contrast Cz, decreases with kδ
- Dashed isolines labeled "weak", "moderate", "strong"
- Bottom braces annotating "thin → resonant → thick" regimes

### Figure 3.8C — Attenuation vs Frequency
**Files:** `figure_3_8C.pdf`, `figure_3_8C.png`

Line plots showing apparent attenuation (transmission loss) vs ω/N for four Ri values:
- **Ri = 1.5** (deep blue, stable): narrow conversion peak
- **Ri = 1.0** (steel blue): moderately broadened peak
- **Ri = 0.6** (teal, marginal): significantly broader peak with elevated skirts
- **Ri = 0.3** (magenta dashed, near-critical): flat dome with prominent broadband shoulders
- Amber conversion band overlay (0.8–1.2)
- Annotations showing peak widening and skirt growth as Ri decreases

### Figure 3.8D — Notch Depth vs Interface Thickness
**Files:** `figure_3_8D.pdf`, `figure_3_8D.png`

Line plots showing notch depth decay with kδ for different impedance contrasts:
- **Cz = 0.05, 0.10, 0.20, 0.30** (light purple → dark purple)
- Log-scale x-axis for kδ
- Monotone decreasing curves (depth decreases as kδ increases)
- Higher Cz values always yield deeper notches
- Bottom braces annotating "thin → resonant → thick" regimes

## Style Compliance

All figures strictly follow the specifications:
✓ Canvas: 2000×1400 px (landscape), white background
✓ Typeface: Helvetica/Arial with specified font sizes (28pt bold titles, 22pt axis labels, 16pt ticks)
✓ Grid: light gray #E5E7EB (0.8 px)
✓ Mechanism colors: amber #F4A261, teal #2A9D8F, purple #6A4C93, etc.
✓ Line weights: 3px primary curves, 2-2.5px secondary
✓ Common frequency axis: ω/N ∈ [0.2, 2.2] with specified ticks
✓ Conversion band overlay where relevant (amber 20% opacity, dotted centerline)
✓ Legends: inside axes, frameless, 16-18pt
✓ Captions: 15pt italics

## Usage

### In LaTeX
```latex
\begin{figure}
  \centering
  \includegraphics[width=\textwidth]{figure_3_8A.pdf}
  \caption{Your caption here}
  \label{fig:3.8A}
\end{figure}
```

### Regenerating Figures
To regenerate or modify the figures:
```bash
python3 generate_figures.py
```

The script `generate_figures.py` contains all the figure generation code with detailed comments. You can modify:
- Color schemes
- Data/formulas
- Annotations
- Layout parameters

## Dependencies

Required Python packages (already installed):
- numpy
- matplotlib

To install on a new system:
```bash
pip install numpy matplotlib
```

## Quality Checklist ✓

- [x] Consistent ω/N range and amber band wherever frequency appears
- [x] Heatmaps: colormap polarity matches semantics (darker = stronger)
- [x] Log axis on kδ for 3.8B/D with readable tick labels
- [x] Legends don't obscure key features
- [x] PDF/SVG (vector; fonts embedded) ✓
- [x] PNG 300 DPI for drafts ✓

---

**Note:** The data shown is schematic/illustrative following your specifications. Replace the mathematical formulas in the Python script with your actual physics model/data if you have specific numerical values.
