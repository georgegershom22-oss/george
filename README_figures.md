# Publication-Quality Figures 3.5A, 3.5B, 3.5C

## Overview
This directory contains three publication-quality figures following the specified house style for a thesis on finite-thickness interface acoustics. All figures are generated programmatically using matplotlib for precise, reproducible results.

## House Style Specifications
- **Canvas Size**: 2000 × 1400 px (landscape), white background
- **Margins**: 90 px L/R, 80 px top, 110 px bottom
- **Grid**: Subtle light-gray (#E5E7EB, 0.8 px) major grid only
- **Typography**: Helvetica/Arial family
  - Panel titles: 28 pt bold
  - Axis labels: 22 pt
  - Tick labels: 16 pt
  - In-plot callouts: 18–20 pt
  - Legend: 16–18 pt
- **Colors** (color-blind safe):
  - Primary curve: deep blue #1F78B4
  - Secondary curve: steel blue #457B9D
  - High-contrast accent: magenta #B3007D
  - Classical baseline: dark gray #555555, dashed
  - Amber conversion window: #F4A261 at 18–22% opacity
- **Line weights**: axes 2 px; primary curves 3 px; secondary 2–2.5 px

## Generated Files

### Figure 3.5A - Finite-thickness interface geometry and controls
**Files**: `figure_3_5a.png`, `figure_3_5a.pdf`, `figure_3_5a.svg`

**Purpose**: Schematic defining finite-thickness interface (thickness δ), contrast metrics (Atwood At and impedance contrast CZ), and incidence geometry (angle θ), while visually hinting at phase-thickness (kzδ) and partial R/T processes.

**Features**:
- Main panel with stratified water column (blue gradient)
- Horizontal translucent magenta band representing finite-thickness interface
- Incident, reflected, and transmitted acoustic rays (orange)
- Internal multiple passes showing etalon-like phase accumulation
- Layer property labels and contrast metric annotations
- Right mini-column with three micro-plots:
  - ρ(z) profiles (sharp → moderate → diffuse)
  - c₀(z) profiles (stepped → smooth)
  - Optical thickness gauge (kδ = 0.1, 1, 3)
- Legend box explaining ray notation and interface representation

### Figure 3.5B - Transmission vs frequency for three regimes
**Files**: `figure_3_5b.png`, `figure_3_5b.pdf`, `figure_3_5b.svg`

**Purpose**: Shows how finite thickness and contrast control the spectral structure of transmission across three interface regimes.

**Features**:
- X-axis: Normalized frequency ω/N (0.2 → 3.5)
- Y-axis: Transmissivity |T|² (0 → 1)
- Three curves:
  - **Sharp/high-contrast** (magenta): Deep, frequent notches (6–14 dB equivalent)
  - **Moderate** (deep blue): Shallower, less frequent notches
  - **Diffuse/low-contrast** (teal): Weak, broad ripples (nearly smooth)
- Amber conversion window band (0.8 ≤ ω/N ≤ 1.2)
- Dotted centerline at ω/N = 1
- Spacing indicator showing quasi-periodic notch structure
- Homogeneous baseline for reference

### Figure 3.5C - Reflectivity vs incidence angle at fixed contrast
**Files**: `figure_3_5c.png`, `figure_3_5c.pdf`, `figure_3_5c.svg`

**Purpose**: Shows angular dependence of reflectivity |R|² at fixed contrast while varying phase-thickness kδ, isolating thickness effects from contrast.

**Features**:
- X-axis: Incidence angle θ (0° → 80°)
- Y-axis: Reflectivity |R|² (0 → 1)
- Three curves at fixed contrast:
  - **kδ = 0.1** (purple): Thin/sharp with pronounced angular lobes
  - **kδ = 1** (orange): Resonant thickness with strongest interference lobes
  - **kδ = 3** (teal): Thick/diffuse with smoothed, muted angular variation
- Callout annotations explaining physical behavior
- Dotted guide line at representative angle
- Legend with fixed contrast notation

## File Formats
Each figure is exported in three formats:
- **PNG** (300 DPI): High-resolution raster for sharing and presentations
- **PDF**: Vector format with embedded fonts for submission
- **SVG**: Scalable vector format for editing and web use

## Technical Implementation
All figures are generated using Python 3 with matplotlib, ensuring:
- Exact adherence to house style specifications
- Reproducible results with consistent formatting
- Vector-clean output suitable for publication
- Proper font handling and color management
- Mathematical notation using LaTeX rendering

## Usage Notes
- Figures are ready for direct inclusion in thesis documents
- PDF versions have embedded fonts for reliable rendering
- SVG versions can be further edited in vector graphics software if needed
- All figures maintain consistent styling across the series
- Color choices are verified for color-blind accessibility

## Source Code
The Python scripts (`figure_3_5a.py`, `figure_3_5b.py`, `figure_3_5c.py`) contain the complete generation code and can be modified to adjust specific parameters while maintaining the overall house style.