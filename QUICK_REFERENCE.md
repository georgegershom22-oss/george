# Quick Reference Guide - Welding ML Dataset

## 🚀 Instant Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate fresh dataset
python3 generate_welding_dataset.py

# Run statistical analysis
python3 exploratory_data_analysis.py

# Create visualizations
python3 visualizations.py

# Train ML models
python3 ml_modeling_starter.py

# Optimize parameters
python3 bayesian_inverse_design.py
```

## 📊 Load Dataset (Python)

```python
import pandas as pd

# Load data
df = pd.read_csv('welding_ml_dataset.csv')

# View structure
print(df.shape)        # (5000, 34)
print(df.columns)      # All feature names
print(df.head())       # First 5 rows
print(df.describe())   # Statistics
```

## 🎯 Key Features at a Glance

### Inputs (13)
```python
inputs = [
    'anode_material', 'cathode_material', 'surface_finish',
    'welding_technique', 'power_W', 'amplitude_um', 'force_N',
    'time_ms', 'frequency_Hz', 'speed_mm_s', 'tab_thickness_um',
    'preheat_temp_C', 'energy_density_J_mm2'
]
```

### Primary Target
```python
target = 'thermal_cycles_to_failure'  # Main goal: maximize this!
```

### Critical Metrics
```python
critical = [
    'IMC_thickness_um',           # MOST IMPORTANT (optimal: 1-3 µm)
    'contact_resistance_uOhm',    # Lower is better (< 50 µΩ)
    'overall_quality_score'       # Composite metric
]
```

## 🔬 Quick Analysis Snippets

### Best Performing Samples
```python
# Top 10 by thermal cycles
top_10 = df.nlargest(10, 'thermal_cycles_to_failure')
print(top_10[['welding_technique', 'thermal_cycles_to_failure', 'IMC_thickness_um']])

# Samples with optimal IMC
optimal = df[(df['IMC_thickness_um'] >= 1) & (df['IMC_thickness_um'] <= 3)]
print(f"Optimal IMC samples: {len(optimal)} ({len(optimal)/len(df)*100:.1f}%)")
```

### Technique Comparison
```python
# Average performance by technique
df.groupby('welding_technique').agg({
    'thermal_cycles_to_failure': 'mean',
    'contact_resistance_uOhm': 'mean',
    'tensile_shear_strength_N': 'mean'
})
```

### Material Analysis
```python
# Best material combination
materials = df.groupby(['anode_material', 'cathode_material'])
print(materials['thermal_cycles_to_failure'].mean().sort_values(ascending=False))
```

## 🤖 Quick ML Model

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Prepare data (encode categoricals first)
df_encoded = pd.get_dummies(df, columns=['anode_material', 'cathode_material', 
                                          'surface_finish', 'welding_technique'])

# Features and target
feature_cols = [c for c in df_encoded.columns if c not in 
                ['thermal_cycles_to_failure', ...]]  # exclude all targets
X = df_encoded[feature_cols]
y = df_encoded['thermal_cycles_to_failure']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"R² Score: {score:.4f}")
```

## 🎯 Inverse Design Template

```python
# Define target performance
TARGET_CYCLES = 2500
TARGET_RESISTANCE = 50  # µΩ

# Find candidates
candidates = df[
    (df['thermal_cycles_to_failure'] >= TARGET_CYCLES) &
    (df['contact_resistance_uOhm'] <= TARGET_RESISTANCE)
]

# Get best
best = candidates.loc[candidates['overall_quality_score'].idxmax()]
print(best[['welding_technique', 'power_W', 'force_N', 'time_ms']])
```

## 📈 Quick Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='energy_density_J_mm2', y='thermal_cycles_to_failure',
                hue='welding_technique', alpha=0.5)
plt.xlim(0, 1000)  # Focus on main distribution
plt.xlabel('Energy Density (J/mm²)')
plt.ylabel('Thermal Cycles to Failure')
plt.title('Energy vs Performance by Technique')
plt.show()
```

## 💡 Key Insights

| Finding | Value | Recommendation |
|---------|-------|----------------|
| **Optimal IMC** | 1-3 µm | Control temperature & time carefully |
| **Best Technique** | Resistance-Spot | 2043 avg cycles |
| **Best Surface** | Oxide-Removed | 2017 avg cycles |
| **Energy Sweet Spot** | 100-300 J/mm² | Avoid excessive energy |
| **Critical Feature** | Energy Density | 27.8% importance |

## ⚡ Power Tips

1. **Always check IMC thickness** - It's the most critical factor!
2. **Lower energy can be better** - Don't overcook the joint
3. **Surface prep matters** - 100+ cycle difference
4. **Use ensemble models** - Better than single models
5. **Validate with experiments** - This is synthetic data

## 📁 File Locations

```
welding_ml_dataset.csv          ← Main dataset
README.md                       ← Start here
DATASET_DOCUMENTATION.md        ← Detailed reference
DATASET_SUMMARY.txt             ← Complete delivery summary
QUICK_REFERENCE.md              ← This file

generate_welding_dataset.py     ← Regenerate data
exploratory_data_analysis.py    ← Stats analysis
visualizations.py               ← Create plots
ml_modeling_starter.py          ← Train models
bayesian_inverse_design.py      ← Optimize

requirements.txt                ← Python packages

After running scripts:
├── plots/*.png                 ← 10 visualization plots
├── *.pkl                       ← Trained models
├── optimal_welding_parameters.csv
├── pareto_optimal_solutions.csv
└── sensitivity_analysis.csv
```

## 🆘 Troubleshooting

**Import errors?**
```bash
pip install numpy pandas scipy matplotlib seaborn scikit-learn
```

**Low model performance?**
- Expected (R² ≈ 0.42) - real physics is complex
- Try technique-specific models
- Use XGBoost or neural networks
- Feature engineering

**Need better predictions?**
- Ensemble models
- Hyperparameter tuning
- More training data (regenerate with 10k+ samples)
- Domain-specific features

## 📞 Need Help?

1. Check `README.md` for overview
2. Read `DATASET_DOCUMENTATION.md` for details
3. Review `DATASET_SUMMARY.txt` for complete info
4. Examine code comments in scripts
5. Run example scripts to understand workflow

---

**Dataset Version:** 1.0  
**Last Updated:** 2025-10-27  
**Status:** Production Ready ✅
