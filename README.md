# Real-Time Training & Validation Dataset Generator

## Phase 2: Core Real-Time Training & Validation Data

This repository contains a comprehensive dataset generation system for training and validating Digital Twin and Reinforcement Learning systems for ceramic sintering processes. The system generates realistic, high-frequency data streams including DIC (Digital Image Correlation) video, furnace control data, and synchronized sensor measurements.

## 🎯 Purpose

Generate a complete dataset for:
- **Reinforcement Learning Agent Training**: State-action-reward-next_state tuples
- **Digital Twin Validation**: Real-time process monitoring and control
- **Multi-objective Optimization**: Warpage, strain, and density optimization
- **Real-time Process Control**: Furnace control and sensor data integration

## 🚀 Features

### 1. High-Frequency DIC Video Generation
- **Resolution**: 1920x1080 (configurable)
- **Frame Rate**: 120 FPS (configurable)
- **Duration**: 3600 seconds per episode (configurable)
- **Speckle Patterns**: Temperature-dependent, material-specific
- **Deformation Simulation**: Realistic thermal expansion and sintering shrinkage

### 2. Synchronized Furnace Control & Sensor Data
- **Multi-zone Control**: 6 independent heating zones
- **Thermocouple Network**: 12 temperature sensors
- **Atmospheric Monitoring**: Pressure, oxygen content, gas flow
- **Realistic Thermal Dynamics**: Zone coupling, response delays, noise

### 3. Real-Time Strain Analysis
- **Displacement Fields**: Sub-pixel accuracy correlation
- **Strain Components**: εxx, εyy, εxy, principal strains
- **Von Mises Strain**: Equivalent strain calculation
- **Curvature Analysis**: Sample warpage detection

### 4. RL State Representation
- **Fused Features**: DIC, thermal, and process metrics
- **Normalized Vectors**: Standardized for RL training
- **Dimensionality**: Configurable (default: 50 dimensions)
- **Feature Engineering**: Derivatives, heterogeneity, curvature

### 5. Multi-Objective Reward Function
- **Warpage Penalty**: Based on sample curvature
- **Strain Penalty**: Maximum strain limits
- **Density Reward**: Target density achievement
- **Temperature Uniformity**: Thermal gradient minimization
- **Power Efficiency**: Energy consumption optimization

## 📁 Repository Structure

```
├── dataset_generator.py          # Main dataset generation module
├── advanced_data_generator.py    # Advanced DIC and furnace simulation
├── data_validator.py            # Dataset validation and quality checks
├── data_analyzer.py             # Comprehensive analysis and visualization
├── generate_dataset.py          # Main execution script
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd real-time-training-dataset
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python generate_dataset.py --help
   ```

## 🚀 Quick Start

### Basic Usage

Generate a dataset with default settings:
```bash
python generate_dataset.py
```

### Advanced Usage

Generate a custom dataset:
```bash
python generate_dataset.py \
    --episodes 100 \
    --material zirconia \
    --duration 7200 \
    --fps 240 \
    --resolution 2560x1440 \
    --output my_dataset \
    --validate \
    --analyze \
    --visualize
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--episodes` | Number of episodes to generate | 50 |
| `--material` | Material type (alumina/zirconia/silicon_carbide) | alumina |
| `--duration` | Episode duration in seconds | 3600 |
| `--fps` | DIC video frame rate | 120 |
| `--resolution` | Video resolution (WIDTHxHEIGHT) | 1920x1080 |
| `--output` | Output directory | real_time_training_dataset |
| `--validate` | Run validation after generation | False |
| `--analyze` | Run analysis after generation | False |
| `--visualize` | Generate visualizations | False |
| `--config` | Configuration file path | config.yaml |

## 📊 Generated Data Formats

### 1. HDF5 Format (`training_data.h5`)
- **states**: RL state vectors (N × state_dim)
- **actions**: Action vectors (N × action_dim)
- **rewards**: Reward values (N × 1)
- **timestamps**: Synchronized timestamps (N × 1)
- **episodes**: Episode identifiers (N × 1)
- **timesteps**: Timestep identifiers (N × 1)

### 2. CSV Format (`detailed_data.csv`)
- **Episode/Timestep Info**: episode, timestep, timestamp
- **Reward Components**: reward, warpage_penalty, strain_penalty, density_reward
- **DIC Features**: max_principal_strain, strain_heterogeneity, max_displacement
- **Thermal Features**: max_temperature, temp_gradient, total_power
- **Process Features**: cycle_progress, estimated_density

### 3. Video Format (`episode_XXX_dic.mp4`)
- **DIC Video Streams**: High-resolution, high-frame-rate video
- **Displacement Data**: Synchronized displacement fields
- **Metadata**: Timestamps, temperature profiles

## 🔧 Configuration

The system is highly configurable through `config.yaml`:

```yaml
# DIC Video Settings
dic:
  width: 1920
  height: 1080
  fps: 120
  duration: 3600
  material_type: "alumina"

# Furnace Control
furnace:
  num_zones: 6
  num_thermocouples: 12
  max_power: 100.0

# RL State Representation
rl_state:
  state_dim: 50
  feature_scaling: "standard"

# Reward Function
reward:
  weights:
    warpage: 1.0
    strain: 0.5
    density: 0.3
```

## 📈 Data Analysis

The system includes comprehensive analysis tools:

### 1. Reward Analysis
- Distribution plots
- Time series analysis
- Component breakdown
- Episode progression

### 2. State Space Analysis
- PCA visualization
- Clustering analysis
- Correlation matrices
- Dimensionality analysis

### 3. Physical Relationships
- Temperature vs. strain correlations
- Density progression
- Process optimization insights

### 4. Validation Reports
- Data integrity checks
- Physical constraint validation
- Quality metrics
- HTML reports with visualizations

## 🧪 Material Properties

### Alumina (Default)
- **Thermal Expansion**: 8×10⁻⁶ /°C
- **Sintering Temperature**: 1200°C
- **Linear Shrinkage**: 15%
- **Young's Modulus**: 200 GPa

### Zirconia
- **Thermal Expansion**: 10×10⁻⁶ /°C
- **Sintering Temperature**: 1400°C
- **Linear Shrinkage**: 12%
- **Young's Modulus**: 200 GPa

### Silicon Carbide
- **Thermal Expansion**: 4×10⁻⁶ /°C
- **Sintering Temperature**: 1800°C
- **Linear Shrinkage**: 8%
- **Young's Modulus**: 400 GPa

## 🔍 Validation & Quality Assurance

The system includes comprehensive validation:

### Data Integrity
- NaN/infinite value detection
- Shape consistency checks
- Required dataset validation

### Physical Constraints
- Temperature range validation
- Strain limit checks
- Power consumption limits

### Temporal Consistency
- Timestamp monotonicity
- Episode progression validation
- Synchronization checks

### Reward Function Validation
- Range validation
- Consistency checks
- Component analysis

## 📊 Performance Metrics

### Generation Speed
- **DIC Video**: ~2-3 minutes per episode (1920x1080, 120 FPS)
- **Strain Analysis**: ~1-2 minutes per episode
- **Total Time**: ~5-10 minutes per episode (depending on hardware)

### Memory Usage
- **Peak RAM**: ~8-16 GB (depending on resolution and duration)
- **Disk Space**: ~2-5 GB per episode (including video)

### Quality Metrics
- **Validation Score**: >0.8 (out of 1.0)
- **Data Integrity**: 100% (no NaN/infinite values)
- **Physical Consistency**: >95% (within realistic bounds)

## 🎯 Use Cases

### 1. Reinforcement Learning Training
- **State Space**: 50-dimensional feature vectors
- **Action Space**: 6-dimensional furnace control
- **Reward Signal**: Multi-objective optimization
- **Episodes**: Configurable (default: 50-100)

### 2. Digital Twin Validation
- **Real-time Monitoring**: DIC video streams
- **Process Control**: Furnace parameter optimization
- **Quality Prediction**: Strain and density estimation

### 3. Process Optimization
- **Multi-objective Optimization**: Warpage, strain, density
- **Control Strategy Development**: RL-based control
- **Parameter Sensitivity**: Material and process analysis

## 🔬 Scientific Applications

### Materials Science
- **Sintering Behavior**: Realistic material response
- **Thermal Analysis**: Temperature-dependent properties
- **Mechanical Properties**: Strain and stress analysis

### Process Engineering
- **Control Optimization**: RL-based control strategies
- **Quality Assurance**: Real-time monitoring
- **Process Development**: Parameter optimization

### Machine Learning
- **Reinforcement Learning**: State-action-reward tuples
- **Computer Vision**: DIC video analysis
- **Time Series**: Process monitoring and prediction

## 🚀 Advanced Features

### 1. Realistic Material Behavior
- Temperature-dependent properties
- Sintering shrinkage simulation
- Thermal expansion effects
- Material-specific characteristics

### 2. Advanced DIC Analysis
- Sub-pixel accuracy
- Noise reduction
- Confidence scoring
- Multiple correlation methods

### 3. Sophisticated Furnace Simulation
- Zone coupling effects
- Response time delays
- Atmospheric conditions
- Realistic thermal dynamics

### 4. Comprehensive Validation
- Multi-level quality checks
- Physical constraint validation
- Statistical analysis
- Automated reporting

## 📚 Documentation

### Generated Reports
1. **Validation Report** (`validation_report.html`)
2. **Comprehensive Analysis** (`comprehensive_analysis_report.html`)
3. **Generation Summary** (`generation_summary.json`)

### Visualization Files
1. **Reward Analysis** (`reward_analysis.png`)
2. **State Space Analysis** (`state_analysis.png`)
3. **Action Space Analysis** (`action_analysis.png`)
4. **Episode Progression** (`episode_progression.png`)
5. **Physical Relationships** (`physical_relationships.png`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Materials Science Community**: For sintering process insights
- **Computer Vision Community**: For DIC algorithm development
- **Reinforcement Learning Community**: For RL training methodologies
- **Process Engineering Community**: For furnace control strategies

## 📞 Support

For questions, issues, or contributions:
- **Issues**: Use GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Email**: [Contact information]

## 🔄 Version History

- **v1.0.0**: Initial release with basic DIC and furnace simulation
- **v1.1.0**: Added advanced material properties and validation
- **v1.2.0**: Enhanced RL state representation and reward functions
- **v2.0.0**: Complete rewrite with comprehensive analysis and validation

---

**Note**: This dataset generator is designed for research and educational purposes. For production use, additional validation and testing may be required.