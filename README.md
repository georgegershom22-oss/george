# SOFC Low-Fidelity Dataset Generation

This repository contains a comprehensive framework for generating low-fidelity training data for Solid Oxide Fuel Cell (SOFC) simulations. The implementation creates a 1D system-level lumped electrochemical model that mimics the behavior of COMSOL Multiphysics simulations.

## Overview

The dataset generation framework implements **Phase 1** of the multi-fidelity training data generation process:

- **Model Type**: 1D System-Level Lumped Electrochemical Model
- **Target Samples**: 10,200+ simulations
- **Key Outputs**: V-I curves, stack temperature, electrochemical efficiency
- **Parameter Ranges**: Operating temperature (700-900°C), fuel utilization, current density, anode porosity, and more

## Files Structure

```
/workspace/
├── sofc_model.py           # Core SOFC electrochemical model
├── dataset_generator.py    # Parametric sweep and dataset generation
├── visualize_dataset.py    # Visualization and validation tools
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
└── sofc_lf_dataset/       # Generated dataset directory (created after running)
    ├── sofc_lf_dataset.csv    # Main dataset file
    ├── dataset_metadata.json  # Generation metadata
    ├── dataset_analysis.json  # Statistical analysis
    ├── dataset_validation.json # Validation results
    └── plots/                 # Visualization plots
```

## Key Features

### SOFC Model (`sofc_model.py`)
- **Nernst Voltage Calculation**: Thermodynamic equilibrium voltage based on gas partial pressures
- **Activation Overpotential**: Butler-Volmer kinetics with temperature-dependent exchange current densities
- **Ohmic Overpotential**: Ionic and electronic resistance losses
- **Concentration Overpotential**: Mass transport limitations
- **Heat Balance**: Stack temperature calculation considering heat generation
- **V-I Curve Generation**: Complete polarization curves for each parameter set

### Parameter Ranges
The model varies the following parameters across realistic ranges:

#### Operating Conditions
- Operating Temperature: 700-900°C (973.15-1173.15 K)
- Fuel Utilization: 70-95%
- Air Utilization: 15-30%

#### Geometric Parameters
- Cell Area: 50-200 cm²
- Anode Thickness: 300-800 μm
- Cathode Thickness: 30-100 μm
- Electrolyte Thickness: 5-20 μm

#### Material Properties
- Anode/Cathode Porosity: 25-55%
- Tortuosity: 2-5
- Exchange Current Densities: 1000-10000 A/m²
- Activation Energies: 100-180 kJ/mol

#### Transport Properties
- Ionic Conductivity: 20,000-50,000 S/m
- Electronic Conductivity: 60,000-120,000 S/m

### Output Variables
Each simulation generates the following key outputs:
- **V-I Curve**: Complete current-voltage relationship
- **Operating Point**: Voltage, current density, and power density
- **Stack Temperature**: Thermal analysis results
- **Electrochemical Efficiency**: Energy conversion efficiency
- **All Input Parameters**: For traceability and analysis

## Usage

### 1. Install Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 2. Generate Dataset
```bash
python3 dataset_generator.py
```

This will:
- Generate 10,200 SOFC simulation samples
- Use parallel processing for faster execution
- Save results to `sofc_lf_dataset/sofc_lf_dataset.csv`
- Create metadata and analysis files

### 3. Visualize and Validate
```bash
python3 visualize_dataset.py
```

This will:
- Create comprehensive visualizations
- Validate physical constraints
- Generate validation reports
- Save plots to `sofc_lf_dataset/plots/`

## Dataset Characteristics

### Expected Runtime
- **Per Sample**: ~10 seconds (matching COMSOL specification)
- **Total Dataset**: ~28 hours for 10,200 samples (with parallel processing)
- **Parallel Speedup**: 4-8x depending on available CPU cores

### Dataset Size
- **Samples**: 10,200+
- **Features**: ~30 input parameters + 10+ output variables
- **File Size**: ~15-20 MB (CSV format)
- **Memory Usage**: ~100-200 MB during generation

### Quality Metrics
The validation framework checks for:
- Physical constraint violations (efficiency 0-1, positive voltages, etc.)
- Parameter range compliance
- Statistical consistency
- Missing or invalid data

## Model Physics

### Electrochemical Model
The model implements fundamental SOFC physics:

1. **Nernst Equation**: 
   ```
   E_nernst = -ΔG/(2F) + (RT)/(2F) * ln((p_H2 * √p_O2)/p_H2O)
   ```

2. **Butler-Volmer Kinetics**:
   ```
   η_act = (RT)/(2F) * ln(i/i_0)
   ```

3. **Ohmic Losses**:
   ```
   η_ohmic = i * (R_ionic + R_electronic)
   ```

4. **Mass Transport**:
   ```
   η_conc = (RT)/(2F) * ln(1/(1 - i/i_limit))
   ```

5. **Cell Voltage**:
   ```
   V_cell = E_nernst - η_act_anode - η_act_cathode - η_ohmic - η_conc
   ```

### Temperature Dependencies
- Exchange current densities: Arrhenius relationship
- Ionic conductivity: Exponential temperature dependence
- Gas diffusion: Temperature and porosity effects

## Applications

This dataset is designed for:
- **Machine Learning**: Training surrogate models for SOFC performance prediction
- **Multi-Fidelity Modeling**: Low-fidelity component for hierarchical modeling
- **Parameter Sensitivity Analysis**: Understanding key parameter effects
- **Design Optimization**: Initial screening of design parameters
- **Educational Purposes**: Understanding SOFC electrochemical behavior

## Validation and Quality Assurance

The framework includes comprehensive validation:
- **Physical Constraints**: Ensures all outputs are physically meaningful
- **Parameter Ranges**: Verifies inputs are within specified bounds
- **Statistical Analysis**: Checks for proper distributions and correlations
- **Visualization**: Provides intuitive plots for data quality assessment

## Customization

### Modifying Parameter Ranges
Edit the `parameter_ranges` dictionary in `dataset_generator.py`:

```python
self.parameter_ranges = {
    'operating_temperature': (973.15, 1173.15),  # Modify range
    'fuel_utilization': (0.70, 0.95),           # Add new parameters
    # ... other parameters
}
```

### Changing Sample Size
Modify the `n_samples` parameter:

```python
generator = SOFCDatasetGenerator(n_samples=20000)  # Generate 20k samples
```

### Adding New Outputs
Extend the `simulate_single_case` method in `sofc_model.py` to include additional calculated variables.

## Performance Optimization

### Parallel Processing
The framework automatically uses multiple CPU cores:
- Default: min(CPU_count, 8) processes
- Customizable via `n_processes` parameter
- Memory-efficient chunked processing

### Memory Management
- Intermediate results saved every 1000 samples
- Graceful handling of failed simulations
- Automatic cleanup of temporary data

## Troubleshooting

### Common Issues
1. **Memory Errors**: Reduce `n_samples` or use sequential processing
2. **Numerical Instabilities**: Check parameter ranges for extreme values
3. **Slow Performance**: Ensure parallel processing is enabled
4. **Missing Dependencies**: Install all packages from `requirements.txt`

### Debug Mode
Enable detailed logging by modifying the simulation functions to include print statements or logging.

## Future Extensions

Potential enhancements:
- **Multi-cell Stack Modeling**: Extend to full stack simulations
- **Dynamic Operating Conditions**: Time-varying inputs
- **Degradation Models**: Include aging effects
- **3D Geometry Effects**: Incorporate spatial variations
- **Advanced Materials**: New electrode and electrolyte materials

## References

This implementation is based on established SOFC modeling principles from:
- Electrochemical modeling literature
- COMSOL Multiphysics documentation
- SOFC system design guidelines
- Multi-fidelity modeling best practices

## License

This code is provided for research and educational purposes. Please cite appropriately if used in publications.