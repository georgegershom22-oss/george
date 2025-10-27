# ML-Driven Inverse Design of Welding Parameters — Fabricated Dataset

This package contains a fully fabricated, self-consistent dataset for research and prototyping.
It is designed for both forward modeling (quality prediction) and inverse design (parameter selection for target reliability under thermal cycling).

## Contents
- `data/dataset.csv`: combined table with inputs, characterization, and performance targets
- `data/part1_inputs.csv`: only input parameters (design space)
- `data/part2_characterization.csv`: immediate post-join quality metrics
- `data/part3_performance.csv`: thermal cycling performance/targets
- `data/splits/train.csv`, `val.csv`, `test.csv`: ML splits (stratified)
- `schema.json`: column units, types, and descriptions
- `metadata.json`: dataset-level stats and provenance

## Rows
Total rows: 9000

## Key Columns (units)
- **technique** (-): Welding technique used (USW/Laser/RSW)
- **anode_material** (-): Anode/base material name
- **anode_symbol** (-): Anode/base material symbol
- **cathode_material** (-): Cathode/base material name
- **cathode_symbol** (-): Cathode/base material symbol
- **tab_thickness_um** (µm): Tab thickness
- **surface_coating** (-): Surface finish/coating
- **power_W** (W): Power (USW/RSW avg; Laser avg if CW)
- **pulse_energy_J** (J): Laser pulse energy (if pulsed)
- **amplitude_um** (µm): USW vibration amplitude
- **force_N** (N): Clamping/electrode force
- **weld_time_ms** (ms): Weld dwell time
- **speed_mm_s** (mm/s): Laser travel speed
- **pulse_frequency_Hz** (Hz): Laser pulse repetition frequency
- **preheat_temp_C** (°C): Pre-heat temperature of samples
- **ambient_humidity_pct** (%): Ambient relative humidity
- **clamp_area_mm2** (mm²): Approximate clamp/electrode contact area
- **linear_energy_density_J_per_mm** (J/mm): Laser linear energy density (if available)
- **total_energy_input_J** (J): Estimated total energy input
- **nugget_diameter_mm** (mm): Weld nugget diameter (post-join)
- **bond_area_mm2** (mm²): Bonded area (π·d²/4)
- **porosity_pct** (%): Measured porosity in weld region
- **imc_thickness_um** (µm): Intermetallic compound layer thickness
- **peak_temp_C** (°C): Peak temperature observed/estimated
- **haz_width_mm** (mm): Heat-affected zone width
- **contact_resistance_mOhm** (mΩ): Initial electrical contact resistance
- **tensile_shear_strength_N** (N): Tensile shear strength at room temperature
- **peel_strength_N** (N): Peel strength at room temperature
- **visual_defect_score** (0-100): Higher = fewer visual defects
- **microhardness_HV** (HV): Microhardness (Vickers)
- **forward_pass_fail** (bool): Immediate pass/fail screen
- **pressure_MPa** (MPa): Contact pressure derived from force/area
- **effective_energy_J** (J): Effective energy after conduction/pressure factors
- **resistance_growth_pct_1000cyc** (%): Resistance growth after 1000 thermal cycles
- **strength_retention_pct_1000cyc** (%): Strength retention after 1000 cycles
- **cycles_to_failure** (cycles): Cycles to failure in thermal cycling
- **crack_growth_mm** (mm): Crack growth after thermal cycling
- **delamination_probability** (0-1): Probability of delamination under cycling
- **reliability_class** (A/B/C): Performance class (A best)

## Notes
- Values are fabricated using domain-inspired heuristics; they are not measured data.
- Missing values appear in technique-specific columns that do not apply (e.g., `amplitude_um` for Laser).
- Splits are stratified by `technique` and `reliability_class` with a fixed random seed for reproducibility.
- This dataset is suitable for supervised ML (forward) and conditional generation/inverse design experiments.