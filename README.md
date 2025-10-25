# Real-Time Training & Validation Dataset Generator
## Phase 2: Core Real-Time Training & Validation Data

This repository contains a comprehensive dataset generator for real-time Digital Twin and Reinforcement Learning training data, specifically designed for high-temperature sintering processes with Digital Image Correlation (DIC) monitoring.

## 🎯 Overview

The dataset generator creates synchronized, high-fidelity data streams that simulate:
- **Real-Time DIC Data**: High-frequency (100Hz) displacement and strain fields
- **Furnace Control Data**: Synchronized (10Hz) temperature, power, and atmosphere control
- **RL Training Data**: Complete state-action-reward-next_state tuples for agent training

## 📊 Dataset Components

### 1. Real-Time DIC Data Stream (100Hz)
- **Visual Data**: Stereo camera setup with realistic speckle patterns
- **Displacement Fields**: Full-field U, V, W displacement maps
- **Strain Fields**: Engineering strains (εxx, εyy, εxy) and principal strains
- **Temperature Fields**: Spatially distributed temperature maps
- **Quality Maps**: DIC correlation quality assessment

### 2. Synchronized Furnace Control & Sensor Data (10Hz)
- **Zone Control**: Multi-zone temperature setpoints and measurements
- **Power Management**: Zone-specific power outputs (0-100%)
- **Atmosphere Control**: Protective gas flow rates and composition
- **Process Monitoring**: Chamber pressure and environmental conditions

### 3. RL Agent Training Data
- **State Representation**: Compressed multi-modal system state
- **Action Vectors**: Furnace control parameter changes
- **Reward Calculation**: Multi-objective optimization rewards
- **Complete Tuples**: Ready-to-use (s, a, r, s') training data

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd realtime-dataset-generator

# Install dependencies
pip install -r requirements.txt
```

### Generate Dataset

```bash
# Generate complete dataset (8-hour simulation)
python generate_realtime_dataset.py

# Validate and visualize results
python data_validation_tools.py
```

### Dataset Structure

```
realtime_training_dataset/
├── dic_data/
│   └── dic_dataset.h5              # HDF5 format for large arrays
├── furnace_data/
│   ├── furnace_states.csv          # Time-series furnace data
│   └── furnace_states.pkl          # Detailed state objects
├── rl_data/
│   ├── rl_states.csv              # RL state vectors
│   ├── rl_actions.csv             # RL action vectors
│   ├── rl_rewards.csv             # Reward components
│   └── rl_tuples.pkl              # Complete training tuples
├── raw_images/
│   ├── camera_0_frame_*.png       # Stereo camera images
│   └── camera_1_frame_*.png
├── metadata/
│   └── dataset_metadata.json      # Complete dataset documentation
├── visualizations/
│   ├── dic_field_evolution.png    # DIC field analysis
│   ├── thermal_cycle_analysis.png # Furnace control analysis
│   ├── rl_analysis.png           # RL training data analysis
│   └── interactive_dashboard.html # Interactive exploration
└── validation_report.json         # Data quality assessment
```

## 📈 Dataset Specifications

### Physical Parameters
- **Sample Size**: 100mm × 100mm
- **Temperature Range**: 20°C - 1600°C
- **Simulation Duration**: 8 hours (complete sintering cycle)
- **Furnace Zones**: 6 independent heating zones
- **Camera Setup**: Stereo DIC configuration (2048×2048 resolution)

### Data Volumes
- **DIC Frames**: ~2.88M frames (8h × 100Hz)
- **Furnace States**: ~288K states (8h × 10Hz)
- **RL Tuples**: ~288K training examples
- **Raw Images**: Sample deformed speckle patterns
- **Total Size**: ~50-100GB (depending on compression)

### Sampling Rates
- **DIC System**: 100 Hz (real-time strain monitoring)
- **Furnace Control**: 10 Hz (process control frequency)
- **RL Decision**: 10 Hz (synchronized with furnace control)

## 🔬 Scientific Realism

The dataset incorporates realistic physical phenomena:

### Thermal Effects
- **Thermal Expansion**: Temperature-dependent coefficient of thermal expansion
- **Temperature Gradients**: Spatial and temporal temperature variations
- **Heat Transfer**: Realistic heating/cooling profiles

### Mechanical Behavior
- **Sintering Shrinkage**: Density-dependent volumetric shrinkage (up to 15%)
- **Warpage**: Temperature gradient-induced sample curvature
- **Stress Development**: Realistic strain evolution during sintering

### Process Control
- **PID Control**: Realistic furnace zone control with overshoot/undershoot
- **Atmosphere Management**: Protective gas flow and composition control
- **Multi-Zone Coordination**: Independent zone control for gradient management

## 🤖 RL Agent Integration

### State Representation (13 dimensions)
```python
state = {
    'max_principal_strain': float,      # Peak strain in sample
    'strain_heterogeneity': float,      # Strain field uniformity
    'sample_curvature': float,          # Warpage metric
    'displacement_magnitude': float,    # Overall deformation
    'avg_temperature': float,           # Mean sample temperature
    'temp_gradient': float,             # Temperature non-uniformity
    'temp_uniformity': float,           # Normalized uniformity metric
    'cycle_time': float,                # Process time (hours)
    'estimated_density': float,         # Real-time density estimate
    'densification_rate': float,        # Rate of densification
    'dic_quality': float,               # DIC measurement quality
    'thermal_stability': float          # Temperature stability metric
}
```

### Action Space (15 dimensions)
```python
action = {
    'zone_temp_changes': [6 floats],    # Temperature setpoint changes (°C)
    'power_adjustments': [6 floats],    # Power output changes (%)
    'gas_flow_changes': [3 floats]      # Gas flow rate changes
}
```

### Reward Function
Multi-objective optimization with configurable weights:
```python
reward = -(w1 * warpage_penalty + w2 * strain_penalty) + 
         w3 * density_reward + w4 * efficiency_reward
```

## 📊 Data Validation

The dataset includes comprehensive validation tools:

### Integrity Checks
- **Data Completeness**: Verify all expected data is present
- **Temporal Consistency**: Check sampling rate consistency
- **Physical Plausibility**: Validate realistic value ranges
- **Synchronization**: Verify timestamp alignment

### Quality Metrics
- **DIC Quality**: Correlation coefficient evolution
- **Control Performance**: Temperature tracking accuracy
- **RL Readiness**: State-action-reward tuple completeness

### Visualization Suite
- **Field Evolution**: Spatiotemporal DIC field analysis
- **Process Monitoring**: Furnace control performance
- **RL Analysis**: Training data characteristics
- **Interactive Dashboard**: Real-time data exploration

## 🔧 Customization

### Modify Physical Parameters
```python
generator = RealTimeDatasetGenerator()
generator.duration_hours = 12           # Extend simulation time
generator.sample_rate_hz = 200          # Increase DIC frequency
generator.max_temperature = 1800        # Higher sintering temperature
generator.num_zones = 8                 # More furnace zones
```

### Adjust RL Configuration
```python
generator.reward_weights = {
    'warpage': 0.4,     # Increase warpage importance
    'strain': 0.2,      # Reduce strain weight
    'density': 0.3,     # Maintain density focus
    'efficiency': 0.1   # Energy efficiency
}
```

### Custom Thermal Cycles
Modify the `simulate_thermal_cycle()` method to implement custom heating profiles:
```python
def custom_thermal_cycle(self, time_hours):
    # Implement your heating profile
    if time_hours < 2.0:
        return {'base_temperature': 20 + time_hours * 400}
    # ... custom logic
```

## 📚 Usage Examples

### Load DIC Data
```python
import h5py
import numpy as np

# Load DIC dataset
with h5py.File('realtime_training_dataset/dic_data/dic_dataset.h5', 'r') as f:
    timestamps = f['metadata']['timestamps'][:]
    U_displacements = f['displacements']['U'][:]
    strain_fields = f['strains']['strain_principal_max'][:]
    temperature_fields = f['temperatures']['temperature_field'][:]
```

### Load RL Training Data
```python
import pickle
import pandas as pd

# Load RL tuples for training
with open('realtime_training_dataset/rl_data/rl_tuples.pkl', 'rb') as f:
    rl_tuples = pickle.load(f)

# Convert to training format
states = [tuple_data['state'] for tuple_data in rl_tuples]
actions = [tuple_data['action'] for tuple_data in rl_tuples]
rewards = [tuple_data['reward'] for tuple_data in rl_tuples]
next_states = [tuple_data['next_state'] for tuple_data in rl_tuples]
```

### Train RL Agent
```python
from sklearn.preprocessing import StandardScaler
import tensorflow as tf

# Prepare training data
state_scaler = StandardScaler()
action_scaler = StandardScaler()

# Extract state vectors
state_vectors = np.array([[s[key] for key in sorted(s.keys())] for s in states])
action_vectors = np.array([[a[key] for key in sorted(a.keys()) if isinstance(a[key], list)] 
                          for a in actions])

# Scale data
scaled_states = state_scaler.fit_transform(state_vectors)
scaled_actions = action_scaler.fit_transform(action_vectors)

# Train your RL model
# ... model training code
```

## 🔍 Data Analysis

### Explore Dataset Statistics
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load and analyze RL states
rl_states = pd.read_csv('realtime_training_dataset/rl_data/rl_states.csv')

# Plot key metrics evolution
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

axes[0,0].plot(rl_states['timestamp']/3600, rl_states['max_principal_strain'])
axes[0,0].set_title('Maximum Principal Strain Evolution')

axes[0,1].plot(rl_states['timestamp']/3600, rl_states['estimated_density'])
axes[0,1].set_title('Density Evolution')

axes[1,0].plot(rl_states['timestamp']/3600, rl_states['avg_temperature'])
axes[1,0].set_title('Average Temperature')

axes[1,1].plot(rl_states['timestamp']/3600, rl_states['sample_curvature'])
axes[1,1].set_title('Sample Curvature (Warpage)')

plt.tight_layout()
plt.show()
```

## 🎛️ Advanced Features

### Real-Time Streaming Simulation
```python
class RealTimeStreamer:
    def __init__(self, dataset_path):
        self.dataset = self.load_dataset(dataset_path)
    
    def stream_data(self, callback_func):
        """Stream data in real-time simulation"""
        for frame in self.dataset:
            callback_func(frame)
            time.sleep(1.0 / 100)  # 100Hz simulation
```

### Custom Reward Functions
```python
def custom_reward_function(state, action, next_state):
    """Implement custom multi-objective reward"""
    # Your custom reward logic
    quality_reward = next_state['dic_quality'] * 0.1
    custom_penalty = -abs(next_state['temp_gradient']) * 0.05
    
    return quality_reward + custom_penalty
```

### Data Augmentation
```python
def augment_rl_data(rl_tuples, noise_level=0.01):
    """Add realistic noise for data augmentation"""
    augmented = []
    for tuple_data in rl_tuples:
        # Add Gaussian noise to states
        noisy_state = add_noise(tuple_data['state'], noise_level)
        augmented.append({
            'state': noisy_state,
            'action': tuple_data['action'],
            'reward': tuple_data['reward'],
            'next_state': tuple_data['next_state']
        })
    return augmented
```

## 🚨 Important Notes

### Performance Considerations
- **Memory Usage**: Full dataset requires ~50-100GB RAM for processing
- **Generation Time**: Complete dataset generation takes 2-4 hours
- **Storage**: Compressed HDF5 format reduces storage by ~70%

### Data Quality
- **Physical Realism**: All data follows realistic physical constraints
- **Temporal Consistency**: Proper causality in state transitions
- **Measurement Noise**: Realistic sensor noise and DIC quality variations

### Extensibility
- **Modular Design**: Easy to modify individual components
- **Custom Physics**: Implement domain-specific material models
- **Scalable**: Configurable for different sample sizes and processes

## 📖 Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{realtime_sintering_dataset_2024,
  title={Real-Time Training and Validation Dataset for Digital Twin and Reinforcement Learning in High-Temperature Sintering},
  author={Dataset Generator},
  year={2024},
  publisher={Phase 2 Core Training Data},
  version={1.0}
}
```

## 📞 Support

For questions, issues, or contributions:
- Check the validation report for data quality assessment
- Review the interactive dashboard for data exploration
- Examine the visualization suite for detailed analysis

## 🔄 Updates

### Version 1.0 (Current)
- Complete real-time DIC data stream generation
- Synchronized furnace control and sensor data
- Full RL state-action-reward-next_state tuples
- Comprehensive validation and visualization tools
- Interactive dashboard for data exploration

### Future Enhancements
- Multi-material sintering scenarios
- Advanced failure mode simulation
- Extended temperature ranges and atmospheres
- Integration with real hardware interfaces

---

**Ready for Digital Twin and RL Agent Training!** 🚀