# Installation Instructions

## Quick Start

1. Extract the dataset package
2. Install dependencies: `pip install -r requirements.txt`
3. Load the dataset: `python3 -c "import pandas as pd; data = pd.read_csv('welding_dataset/complete_dataset.csv'); print(data.shape)"`
4. Run analysis: `python3 analysis_tools.py`
5. Explore examples: Open `example_usage.ipynb` in Jupyter

## Files Overview

- `welding_dataset/`: Main dataset files (CSV format)
- `welding_dataset_generator.py`: Dataset generation script
- `analysis_tools.py`: Comprehensive analysis tools
- `example_usage.ipynb`: Interactive examples and tutorials
- `README.md`: Complete documentation
- `requirements.txt`: Python dependencies

## Dataset Structure

- **Input Parameters** (19 features): Process parameters you can control
- **Characterization Metrics** (21 features): Immediate weld quality measurements  
- **Performance Metrics** (22 features): Long-term cycling performance data

Total: 10,000 samples × 61 features

## Support

For questions or issues, refer to the documentation files or the example notebook.
