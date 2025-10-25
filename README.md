# Real-Time Training & Validation Dataset Generator

A comprehensive system for generating high-fidelity, real-time training and validation datasets for Digital Twin and Reinforcement Learning applications in advanced manufacturing processes.

## Overview

This system generates a complete dataset including:

### 1. High-Frequency DIC Data Stream
- **Visual Data**: High-resolution, high-frame-rate video (1920x1080 @ 30 FPS) with realistic speckle patterns
- **Derived Data**: Real-time full-field displacement (U, V, W) and strain (εxx, εyy, εxy) maps
- **Key Metrics**: Maximum principal strain, strain heterogeneity, sample curvature
- **Metadata**: Synchronized timestamps with furnace controller

### 2. Synchronized Furnace Control & Sensor Data
- **Inputs (Actions)**: Commands to furnace heating zones (power, temperature setpoints)
- **Outputs (States)**: Temperature readings from 12 thermocouples, atmospheric gas readings
- **Control Data**: 6 heating zones with realistic temperature profiles
- **Synchronization**: Time-synchronized with DIC stream at 1 Hz update frequency

### 3. RL State-Action-Reward-Next_State Tuples
- **State (s)**: Compressed system condition including:
  - DIC metrics (max principal strain, strain heterogeneity, curvature)
  - Thermal metrics (key thermocouple temperatures)
  - Process metrics (time, temperature uniformity, atmospheric conditions)
- **Action (a)**: Furnace parameter changes (temperature adjustments per zone)
- **Reward (r)**: Multi-objective optimization function:
  ```
  Reward = -(w1 * |warpage_rate| + w2 * |max_strain| + w3 * (target_density - current_density)²)
  ```
- **Next State (s')**: System state after action execution

## Features

### 🎯 **Realistic Physics-Based Simulation**
- Sintering-induced shrinkage and warpage modeling
- Temperature-dependent material behavior
- Realistic noise and spatial variation
- Multi-zone furnace control simulation

### 📊 **Comprehensive Data Visualization**
- Displacement and strain field visualizations
- Temperature profile and control action plots
- RL training data analysis and correlation matrices
- Animated visualizations (GIF format)

### 🔧 **Advanced Data Processing**
- Efficient HDF5 storage with compression
- Data normalization and preprocessing
- Temporal synchronization across all data streams
- Batch loading for machine learning training

### 📈 **Multi-Objective Optimization**
- Configurable reward function weights
- Warpage rate minimization
- Strain level optimization
- Density target achievement

## Installation

1. **Clone or download the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Usage
```bash
python run_dataset_generation.py
```

### Advanced Usage
```bash
python run_dataset_generation.py \
    --duration 12.0 \
    --dic-fps 60 \
    --furnace-freq 2.0 \
    --thermocouples 16 \
    --heating-zones 8 \
    --create-animations \
    --output-dir my_dataset
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--duration` | 8.0 | Sample duration in hours |
| `--dic-fps` | 30 | DIC camera frame rate |
| `--furnace-freq` | 1.0 | Furnace update frequency (Hz) |
| `--thermocouples` | 12 | Number of temperature sensors |
| `--heating-zones` | 6 | Number of furnace heating zones |
| `--image-width` | 1920 | DIC image width |
| `--image-height` | 1080 | DIC image height |
| `--output-dir` | real_time_dataset | Output directory |
| `--create-animations` | False | Generate animated visualizations |
| `--batch-size` | 32 | Batch size for data loading |
| `--sequence-length` | 10 | Sequence length for time series models |

## Dataset Structure

```
real_time_dataset/
├── dic_data.h5                    # DIC video frames and derived data
├── furnace_data.h5                # Furnace control and sensor data
├── rl_data.h5                     # RL training tuples
├── metadata.json                  # Dataset metadata
├── generation_metadata.json       # Generation parameters and timing
├── execution_summary.json         # Complete execution summary
├── data_quality_report.json       # Data quality analysis
├── analysis_results.json          # Detailed analysis results
├── *.png                          # Static visualizations
└── *.gif                          # Animated visualizations (if created)
```

## Data Format

### DIC Data (dic_data.h5)
- `video_frames`: Raw video frames with speckle pattern (N, H, W)
- `displacement_u/v/w`: Displacement fields (N, H, W)
- `strain_xx/yy/xy`: Strain fields (N, H, W)
- `max_principal_strain`: Key metric over time (N,)
- `strain_heterogeneity`: Strain uniformity metric (N,)
- `sample_curvature`: Sample warpage metric (N,)
- `timestamps`: Synchronized timestamps (N,)

### Furnace Data (furnace_data.h5)
- `zone_temperatures`: Temperature readings per zone (N, 6)
- `zone_power`: Power levels per zone (N, 6)
- `thermocouple_temps`: Temperature sensor readings (N, 12)
- `oxygen_levels`: Atmospheric oxygen concentration (N,)
- `nitrogen_levels`: Atmospheric nitrogen concentration (N,)
- `actions`: Control actions (temperature changes) (N, 6)
- `timestamps`: Synchronized timestamps (N,)

### RL Data (rl_data.h5)
- `states`: State vectors (N, 11) - DIC + thermal + process metrics
- `actions`: Action vectors (N, 6) - zone temperature changes
- `rewards`: Reward values (N,) - multi-objective optimization
- `next_states`: Next state vectors (N, 11)
- `timestamps`: Synchronized timestamps (N,)

## Usage Examples

### Python API Usage

```python
from dataset_generator import RealTimeDatasetGenerator
from data_loader import RealTimeDataLoader, DatasetConfig
from data_visualizer import DatasetVisualizer

# Generate dataset
generator = RealTimeDatasetGenerator(
    sample_duration_hours=8.0,
    dic_fps=30,
    furnace_update_freq=1.0
)

dic_data = generator.generate_dic_data_stream()
furnace_data = generator.generate_furnace_control_data()
rl_data = generator.generate_rl_state_representation(dic_data, furnace_data)

generator.save_dataset(dic_data, furnace_data, rl_data, "my_dataset")

# Load and analyze data
config = DatasetConfig(dataset_dir="my_dataset")
data_loader = RealTimeDataLoader(config)

# Load specific data
dic_data = data_loader.load_dic_data()
rl_data = data_loader.load_rl_data()

# Create batch loader for training
batch_loader = data_loader.create_batch_loader('rl', batch_size=32)

# Visualize data
visualizer = DatasetVisualizer("my_dataset")
visualizer.visualize_dic_data()
visualizer.visualize_furnace_data()
visualizer.visualize_rl_data()
```

### Machine Learning Integration

```python
# Create sequence dataset for time series models
sequence_data = data_loader.create_sequence_dataset(sequence_length=10)

# Create train/validation split
train_data, val_data = data_loader.create_train_val_split(rl_data, val_ratio=0.2)

# Normalize data
normalized_states, norm_params = data_loader.normalize_data(
    train_data['states'], method='z_score'
)
```

## Advanced Features

### Data Synchronization
All data streams are automatically synchronized to a common time base, ensuring perfect temporal alignment between DIC measurements, furnace control actions, and sensor readings.

### Multi-Objective Reward Function
The reward function balances multiple objectives:
- **Warpage Rate**: Minimize sample curvature changes
- **Strain Level**: Minimize maximum principal strain
- **Density Target**: Achieve target sintering density

### Realistic Physics Modeling
- Sintering shrinkage based on time-temperature profiles
- Warpage due to temperature gradients
- Material behavior evolution during process
- Realistic noise and measurement uncertainty

### Comprehensive Analysis
- Temporal correlation analysis
- Frequency content analysis
- Data quality assessment
- Statistical summaries and recommendations

## Performance

### Dataset Sizes (8-hour process)
- **DIC Data**: ~2.5 GB (30 FPS, 1920x1080)
- **Furnace Data**: ~50 MB (1 Hz, 6 zones, 12 thermocouples)
- **RL Data**: ~10 MB (28,800 training tuples)
- **Total**: ~2.6 GB

### Generation Time
- **8-hour dataset**: ~5-10 minutes
- **12-hour dataset**: ~8-15 minutes
- **24-hour dataset**: ~15-30 minutes

## Applications

### Reinforcement Learning
- **State Space**: 11-dimensional (DIC + thermal + process metrics)
- **Action Space**: 6-dimensional (heating zone controls)
- **Reward Function**: Multi-objective optimization
- **Training Data**: 28,800+ state-action-reward-next_state tuples

### Digital Twin Validation
- **Real-time DIC**: High-frequency displacement/strain monitoring
- **Process Control**: Furnace parameter optimization
- **Quality Prediction**: Warpage and density estimation

### Process Optimization
- **Multi-objective**: Balance warpage, strain, and density
- **Real-time Control**: Adaptive furnace parameter adjustment
- **Quality Assurance**: Continuous process monitoring

## File Descriptions

| File | Description |
|------|-------------|
| `dataset_generator.py` | Core dataset generation engine |
| `data_visualizer.py` | Comprehensive visualization tools |
| `data_loader.py` | Data loading and analysis toolkit |
| `run_dataset_generation.py` | Main execution script |
| `requirements.txt` | Python dependencies |

## Contributing

This system is designed for advanced manufacturing research and development. Contributions are welcome for:
- Enhanced physics modeling
- Additional sensor types
- Improved visualization tools
- Machine learning integration examples

## License

This project is designed for research and educational purposes in advanced manufacturing and materials processing.

## Citation

If you use this dataset generator in your research, please cite:

```bibtex
@software{realtime_dataset_generator,
  title={Real-Time Training & Validation Dataset Generator for Digital Twin and RL Applications},
  author={AI Assistant},
  year={2024},
  url={https://github.com/your-repo/real-time-dataset-generator}
}
```

## Support

For questions, issues, or feature requests, please refer to the documentation or create an issue in the repository.

---

**Note**: This system generates synthetic data for research and development purposes. For production applications, validate against real experimental data and adjust parameters accordingly.