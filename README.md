# SOFC High-Fidelity Simulation Dataset Generator

This project generates comprehensive high-fidelity numerical datasets for Solid Oxide Fuel Cell (SOFC) thermo-mechanical modeling using Physics-Informed Data-Driven approaches.

## 🎯 Overview

The dataset generator creates synthetic data from 3D Finite Element Analysis (FEA) and Computational Fluid Dynamics (CFD) simulations of SOFC systems. This data serves as the foundation for training physics-informed neural networks for real-time performance and stress prediction.

## 📊 Dataset Structure

### Input Parameters (Features)
- **Operating Conditions**: Voltage/Current Density, Air/Fuel Flow Rates, Inlet Temperatures
- **Material Properties**: Porosity, Permeability, Conductivities, Mechanical Properties (Young's Modulus, CTE)
- **Geometric Parameters**: Layer thicknesses, Active area, Flow channel design

### Output Fields (Labels)
- **Electrochemical Fields**: Current density distribution, Overpotential distribution
- **Thermal Fields**: 3D Temperature distribution T(x,y,z)
- **Stress/Strain Fields**: von Mises stress, Strain tensors, Displacement fields
- **Species Fields**: H₂, H₂O concentration distributions

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- FEniCS/DOLFIN (for finite element simulations)
- GMSH (for mesh generation)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd sofc_dataset_generator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Test the installation**:
```bash
python test_simulation.py
```

4. **Generate your first dataset**:
```bash
python run_dataset_generation.py --samples 10 --test
```

## 📋 Usage Examples

### Basic Dataset Generation
```bash
# Generate 100 samples with default settings
python run_dataset_generation.py --samples 100

# Generate with parallel processing
python run_dataset_generation.py --samples 500 --parallel --workers 8

# Test mode (fast, coarse mesh)
python run_dataset_generation.py --samples 20 --test
```

### Advanced Usage
```bash
# Use custom configuration
python run_dataset_generation.py --config my_config.yaml --samples 1000

# Generate with visualization
python run_dataset_generation.py --samples 200 --visualize

# Specify output directory
python run_dataset_generation.py --samples 100 --output my_dataset_folder
```

### Using the Python API
```python
from src.main import SOFCSimulationRunner

# Initialize runner
runner = SOFCSimulationRunner('config/simulation_config.yaml')

# Generate dataset
statistics = runner.generate_dataset(n_samples=100, parallel=True)

# Validate results
validation = runner.validate_dataset()
```

## 📁 Project Structure

```
sofc_dataset_generator/
├── 📂 src/
│   ├── 🔧 geometry/          # SOFC geometry and mesh generation
│   ├── ⚡ simulation/        # Multi-physics simulation modules
│   │   ├── electrochemical.py    # Current density, overpotential
│   │   ├── thermal.py            # Temperature distribution
│   │   ├── mechanical.py         # Stress/strain analysis
│   │   └── species_transport.py  # H₂, H₂O, O₂ transport
│   ├── 🎲 sampling/          # Parameter sampling (Latin Hypercube)
│   ├── 💾 export/           # Data export and storage (HDF5, VTK)
│   └── 📊 visualization/    # Results visualization and analysis
├── 📂 config/               # Configuration files
├── 📂 notebooks/           # Jupyter analysis notebooks
├── 📂 data/               # Generated datasets (created during execution)
├── 📋 requirements.txt    # Python dependencies
├── 🧪 test_simulation.py  # Test script
└── 🚀 run_dataset_generation.py  # Main execution script
```

## 🔧 Configuration

Edit `config/simulation_config.yaml` to customize:

- **Dataset size**: Number of samples
- **Parameter ranges**: Operating conditions, material properties
- **Simulation settings**: Mesh density, solver tolerances
- **Output fields**: Which variables to save

Example configuration snippet:
```yaml
dataset:
  n_samples: 1000
  output_dir: "data/sofc_dataset"

operating_conditions:
  voltage: [0.6, 0.9]
  current_density: [0.1, 1.0]
  fuel_inlet_temp: [1073, 1173]

simulation:
  mesh_density: "medium"
  relative_tolerance: 1e-6
```

## 📈 Analysis and Visualization

### Jupyter Notebooks
```bash
jupyter notebook notebooks/dataset_analysis.ipynb
```

### Python API
```python
from src.visualization.visualizer import SOFCVisualizer

# Load dataset
viz = SOFCVisualizer('data/sofc_dataset')

# Generate plots
viz.plot_parameter_distributions()
viz.plot_performance_metrics()
viz.create_interactive_dashboard()

# Generate complete report
viz.generate_analysis_report()
```

## 🔬 Multi-Physics Simulation Details

### 1. Electrochemical Model
- **Equations**: Charge conservation, Butler-Volmer kinetics
- **Outputs**: Electric potential, current density, overpotentials
- **Coupling**: Provides heat sources for thermal analysis

### 2. Thermal Model
- **Equations**: Heat conduction with electrochemical sources
- **Outputs**: Temperature distribution, heat flux
- **Coupling**: Temperature affects material properties and species transport

### 3. Mechanical Model
- **Equations**: Linear elasticity with thermal expansion
- **Outputs**: Stress, strain, displacement fields
- **Coupling**: Thermal stresses from temperature gradients

### 4. Species Transport
- **Equations**: Mass conservation with reaction sources
- **Outputs**: H₂, H₂O, O₂, N₂ concentrations
- **Coupling**: Reaction rates from electrochemical current

## 📊 Output Data Formats

### HDF5 (Primary ML Format)
```
sample_000001.h5
├── inputs/           # Parameter values
├── outputs/
│   ├── electrochemical/
│   │   ├── fields/   # 3D field data
│   │   └── metrics/  # Scalar performance metrics
│   ├── thermal/
│   ├── mechanical/
│   └── species_transport/
└── mesh/            # Geometry and connectivity
```

### VTK (Visualization)
- Compatible with ParaView, VisIt
- 3D field visualization
- Vector and scalar data

### CSV (Analysis)
- Parameter summaries
- Performance metrics
- Easy integration with pandas/scikit-learn

## 🎯 Applications

This dataset is designed for:

1. **Physics-Informed Neural Networks (PINNs)**
2. **Reduced-Order Modeling**
3. **Real-time Performance Prediction**
4. **Digital Twin Development**
5. **Optimization and Control**
6. **Failure Prediction and Reliability Analysis**

## 🔍 Quality Assurance

### Automated Validation
- Parameter range checking
- Physical consistency tests
- Data completeness verification
- Outlier detection

### Manual Verification
- Mesh quality assessment
- Convergence monitoring
- Physics-based sanity checks

## 🚀 Performance and Scaling

### Computational Requirements
- **Memory**: 2-8 GB RAM per simulation
- **CPU**: Multi-core recommended (4-16 cores)
- **Storage**: ~10-100 MB per sample (depends on mesh size)
- **Time**: 1-30 minutes per sample (depends on complexity)

### Scaling Guidelines
- **Small dataset** (10-100 samples): Single machine, test mode
- **Medium dataset** (100-1000 samples): Multi-core, medium mesh
- **Large dataset** (1000+ samples): Cluster/cloud, parallel processing

## 🐛 Troubleshooting

### Common Issues

1. **FEniCS Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install fenics

# Conda
conda install -c conda-forge fenics
```

2. **GMSH Not Found**:
```bash
# Ubuntu/Debian  
sudo apt-get install gmsh

# macOS
brew install gmsh
```

3. **Memory Issues**:
- Reduce mesh density in config
- Use fewer parallel workers
- Process samples in smaller batches

4. **Convergence Problems**:
- Relax solver tolerances
- Check parameter ranges
- Verify mesh quality

### Getting Help
- Check log files in `output_directory/logs/`
- Run test simulation: `python test_simulation.py`
- Review validation report
- Check GitHub issues (if applicable)

## 🤝 Contributing

We welcome contributions! Please see:
- Code style: Black formatting
- Testing: pytest for unit tests
- Documentation: Sphinx for docs
- Issues: GitHub issue tracker

## 📚 Citation

If you use this dataset generator in your research, please cite:

```bibtex
@thesis{sofc_dataset_2024,
  title={Physics-Informed Data-Driven Modeling of SOFC Thermo-Mechanics for Real-Time Performance and Stress Prediction},
  author={[Your Name]},
  year={2024},
  school={[Your Institution]},
  type={[Thesis Type]}
}
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FEniCS Project for finite element framework
- GMSH for mesh generation
- Scientific Python ecosystem (NumPy, SciPy, matplotlib)
- SOFC research community for domain knowledge