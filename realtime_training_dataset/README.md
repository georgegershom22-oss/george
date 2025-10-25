# Real-Time Training & Validation Dataset for RL-Controlled Furnace System

## Overview
This dataset contains comprehensive real-time data for training Reinforcement Learning agents and validating Digital Twin models for high-temperature furnace control systems with Digital Image Correlation (DIC) monitoring.

## Dataset Structure

### 1. Real-Time DIC Data Stream (`dic_data/`)
- High-frequency synchronized video streams from multiple cameras
- Real-time displacement and strain field computations
- Synchronized timestamps with furnace controller

### 2. Synchronized Furnace Control & Sensor Data (`furnace_data/`)
- Time-synchronized furnace control commands (actions)
- Multi-point temperature measurements (states)
- Atmospheric gas readings and process parameters

### 3. RL State Representation (`rl_data/`)
- Complete state-action-reward-next_state tuples
- Compressed state representations for efficient training
- Multi-objective reward calculations

### 4. Utilities (`utils/`)
- Data generation scripts
- Visualization tools
- Data preprocessing utilities

## Data Specifications

### Sampling Rates
- DIC Video: 100 Hz (high-speed cameras)
- DIC Derived Data: 100 Hz (real-time processing)
- Furnace Control: 10 Hz
- Temperature Sensors: 10 Hz
- RL State Updates: 1 Hz

### Data Volume
- Total dataset size: ~50GB
- Training sequences: 1000 episodes
- Validation sequences: 200 episodes
- Test sequences: 100 episodes

## Usage
See individual component README files for detailed usage instructions.