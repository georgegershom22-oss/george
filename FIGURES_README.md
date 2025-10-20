# Composite Attenuation Figures (3.7A–3.7C1)

This directory contains publication-ready figures for the composite attenuation concept, following the shared house style specifications.

## Generated Figures

### Figure 3.7A — Composite attenuation concept (block diagram)
**File:** `figure_3_7A.png` (2000×1400 px)

A comprehensive block diagram showing:
- **Inputs column** (left): Similarity variables (ω/N, Ri, kδ, C_Z, A_t, θ, r)
- **Similarity space thumbnail** (center-top): Visual cue showing conversion belt, shear-favored, and near-classical regions
- **Mechanism weighting module** (center): 100% stacked bar showing four mechanism shares that sum to unity
- **Combination node**: Σ symbol representing composite attenuation with Bayesian prior/posterior paths
- **Outputs column** (right): Predicted/measured observables (TL, coherence, PSD)
- **Color-coded legend**: All four mechanisms with consistent colors

### Figure 3.7B1 — Mechanism shares vs ω/N (High Ri)
**File:** `figure_3_7B1.png` (2000×1400 px)

100% stacked area chart showing mechanism shares under high Richardson number:
- **Classical** (grey): ~0.35–0.45 baseline, slowly rising with frequency
- **Mode conversion** (amber): Broad dome peaking at ~0.50 near ω/N ≈ 1
- **Shear-mediated** (teal): Minimal (<0.10) with slight shoulder near conversion band
- **Interfacial** (purple): Nearly flat and small (≤0.10) for continuous stratification
- Translucent amber conversion window (0.8–1.2) with dotted centerline at ω/N = 1

### Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri)
**File:** `figure_3_7B2.png` (2000×1400 px)

Same layout as B1 but showing marginal stability regime:
- **Classical** (grey): Reduced pedestal (~0.25–0.35) in conversion band
- **Mode conversion** (amber): Still domed but slightly lower peak (~0.40)
- **Shear-mediated** (teal): Expanded to ~0.35–0.40, rivaling conversion near ω/N ~ 1
- **Interfacial** (purple): Still minimal for continuous background
- Demonstrates how shear-mediated loss becomes competitive with conversion at lower Ri

### Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness)
**File:** `figure_3_7C1.png` (2000×1400 px)

100% stacked area chart showing dependence on interface thickness at fixed ω/N = 1:
- **x-axis**: Log scale kδ from 0.1 → 3 (thin → resonant → thick)
- **Interfacial** (purple): Peaks at ~0.60 for sharp layers (low kδ), monotonically decreases to ~0.10 at high kδ
- **Classical** (grey): Complementary increase as interface becomes diffuse
- **Mode conversion** (amber): Roughly constant (~0.25) with subtle bump near resonant thickness
- **Shear-mediated** (teal): Small and nearly flat (≤0.10)

## House Style Specifications

All figures follow these consistent standards:

### Canvas & Layout
- **Size**: 2000×1400 px (landscape)
- **Background**: White
- **DPI**: 100

### Typography
- **Font family**: Helvetica/Arial (sans-serif)
- **Titles**: 28 pt bold
- **Axis labels**: 22 pt
- **Tick labels**: 16 pt
- **In-plot notes**: 18–20 pt
- **Legends**: 16–18 pt
- **Captions**: 15 pt italic

### Color Palette (consistent across all panels)
- **Classical viscous-thermal**: `#6B7280` (neutral dark grey)
- **Mode conversion**: `#F4A261` (amber), darker `#C06A00` for curves
- **Interfacial scattering**: `#6A4C93` (purple)
- **Shear-mediated/baroclinic**: `#2A9D8F` (teal)
- **Grid**: `#E5E7EB` (light grey, 0.8 px)
- **Centerline**: `#9CA3AF` (dotted, 1.2 px)
- **Conversion window**: Translucent amber (20% opacity) over 0.8 ≤ ω/N ≤ 1.2

### Frequency Axis (when used)
- **Range**: ω/N ∈ [0.2, 2.2]
- **Ticks**: 0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0
- **Conversion band**: 0.8–1.2 with centerline at 1.0

### Line Styles
- **Primary lines**: 3 px
- **Secondary lines**: 2–2.5 px
- **Dotted guides**: 1–1.2 px
- **Dashed pattern**: 8–6
- **Caps/joins**: Round

## Python Scripts

Each figure has a corresponding Python script using matplotlib:
- `figure_3_7A.py` — Block diagram generator
- `figure_3_7B1.py` — High Ri shares
- `figure_3_7B2.py` — Marginal Ri shares
- `figure_3_7C1.py` — Interface thickness dependence

To regenerate any figure:
```bash
python3 figure_3_7A.py
python3 figure_3_7B1.py
python3 figure_3_7B2.py
python3 figure_3_7C1.py
```

## Dependencies

```bash
pip install matplotlib numpy
```

## Notes

- All stacked areas sum to exactly 1.0 at each point
- Smooth curves with no crossings (proper stacking order maintained)
- Annotations positioned to avoid overlapping data
- Legends placed inside axes with frame off
- Captions included within canvas below x-axis
