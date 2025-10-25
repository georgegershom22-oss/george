# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Generate the Dataset
```bash
# Generate a small dataset for testing (100 episodes)
python run_dataset_generation.py --episodes 100

# Generate full dataset (1000 episodes) - takes ~2 hours
python run_dataset_generation.py --episodes 1000 --processes 4
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Examples
```bash
# Basic usage examples
python examples/basic_usage.py

# Train an RL agent
python train_agents.py --config config/training_config.json --agent ppo --episodes 100
```

## 📊 Quick Data Exploration

### Load and Visualize Data
```python
from utils.visualization import DatasetVisualizer

# Create visualizer
viz = DatasetVisualizer("/workspace/realtime_training_dataset")

# Plot episode overview
viz.plot_episode_overview(0)

# Show strain field evolution
viz.visualize_strain_field(0, frame_idx=0)

# Create interactive dashboard
fig = viz.create_interactive_dashboard(0)
fig.show()
```

### Use PyTorch DataLoader
```python
from utils.data_loader import create_data_loaders

# Create data loaders
train_loader, val_loader, test_loader = create_data_loaders(
    base_path="/workspace/realtime_training_dataset",
    train_episodes=list(range(80)),
    val_episodes=list(range(80, 90)),
    test_episodes=list(range(90, 100)),
    batch_size=32
)

# Load a batch
for batch in train_loader:
    print("States shape:", batch['states'].shape)
    print("Actions shape:", batch['actions'].shape)
    break
```

## 🤖 Train RL Agents

### PPO Agent
```python
from rl_models.environment import FurnaceControlEnv
from rl_models.agents import PPOAgent

# Create environment
env = FurnaceControlEnv(
    dataset_path="/workspace/realtime_training_dataset",
    episode_list=list(range(50))
)

# Create and train agent
agent = PPOAgent(state_dim=7, action_dim=6)

for episode in range(100):
    obs = env.reset()
    while True:
        action, log_prob, value = agent.get_action(obs)
        next_obs, reward, done, info = env.step(action)
        agent.store_transition(obs, action, reward, value, log_prob, done)
        obs = next_obs
        if done:
            break
    
    if episode % 10 == 0:
        agent.update()
```

### SAC Agent
```python
from rl_models.agents import SACAgent

agent = SACAgent(state_dim=7, action_dim=6)

# Training loop similar to PPO
for episode in range(100):
    obs = env.reset()
    while True:
        action = agent.get_action(obs)
        next_obs, reward, done, info = env.step(action)
        agent.store_transition(obs, action, reward, next_obs, done)
        agent.update()  # Update every step
        obs = next_obs
        if done:
            break
```

## 🔧 Command Line Training

### Basic Training
```bash
# Train PPO agent
python train_agents.py --config config/training_config.json --agent ppo --episodes 500

# Train SAC agent  
python train_agents.py --config config/training_config.json --agent sac --episodes 500

# Train Multi-Objective agent
python train_agents.py --config config/training_config.json --agent multi_objective --episodes 500
```

### Advanced Options
```bash
# Custom learning rate and batch size
python train_agents.py --config config/training_config.json --lr 1e-4 --episodes 1000

# Enable Weights & Biases logging
python train_agents.py --config config/training_config.json --use_wandb --episodes 1000
```

## 📈 Monitor Training

### Real-time Monitoring
Training automatically generates:
- Training progress plots
- Validation metrics
- Model checkpoints
- Interactive dashboards

### View Results
```bash
# Results saved to training_results/[agent_type_timestamp]/
ls training_results/

# View training plots
open training_results/ppo_20231025_143022/training_progress.png

# Load interactive dashboard
open training_results/ppo_20231025_143022/interactive_dashboard.html
```

## 🎯 Key Metrics to Watch

### Training Metrics
- **Episode Reward**: Target > 80
- **Success Rate**: Target > 0.8 (density ≥ 95%)
- **Final Density**: Target ≥ 0.95
- **Max Strain**: Keep < 0.05

### Process Objectives
1. **Minimize Warpage** (sample distortion)
2. **Control Strain** (mechanical stress)
3. **Achieve Density** (95% target)
4. **Temperature Uniformity** (low std dev)

## 🔍 Data Structure Quick Reference

### State Vector (7D)
```python
state = [
    max_principal_strain,    # [0] Maximum strain magnitude
    strain_std,              # [1] Strain heterogeneity  
    sample_curvature,        # [2] Out-of-plane warpage
    temperature_std,         # [3] Temperature uniformity
    current_density,         # [4] Relative density (0-1)
    mean_temperature,        # [5] Average temperature (°C)
    time_in_cycle           # [6] Process progress (0-1)
]
```

### Action Vector (6D)
```python
action = [
    zone1_power_adj,    # [-20, +20] Power adjustment for zone 1
    zone2_power_adj,    # [-20, +20] Power adjustment for zone 2
    zone3_power_adj,    # [-20, +20] Power adjustment for zone 3
    zone4_power_adj,    # [-20, +20] Power adjustment for zone 4
    zone5_power_adj,    # [-20, +20] Power adjustment for zone 5
    zone6_power_adj     # [-20, +20] Power adjustment for zone 6
]
```

## 🐛 Troubleshooting

### Common Issues

**Dataset not found**
```bash
# Make sure dataset is generated first
python run_dataset_generation.py --episodes 10
```

**Memory errors**
```python
# Reduce batch size
train_loader = DataLoader(dataset, batch_size=16)  # Instead of 32
```

**Slow training**
```bash
# Use fewer episodes for testing
python train_agents.py --episodes 50
```

**CUDA errors**
```python
# Force CPU usage
import torch
torch.cuda.is_available = lambda: False
```

## 📚 Next Steps

1. **Explore Examples**: Run all examples in `examples/basic_usage.py`
2. **Customize Training**: Modify `config/training_config.json`
3. **Advanced Agents**: Try multi-objective optimization
4. **Real-time Simulation**: Use streaming data loader
5. **Custom Rewards**: Modify reward function weights

## 🆘 Getting Help

- **Documentation**: Read `README.md` and `DATASET_SPECIFICATION.md`
- **Examples**: Check `examples/` directory
- **Issues**: Common problems in troubleshooting section
- **Code**: Well-commented source code in all modules

Happy training! 🎉