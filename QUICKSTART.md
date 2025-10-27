# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Verify Dataset Generation
```bash
ls -lh welding_dataset/
```

You should see 6 files:
- ✅ `welding_dataset_[timestamp].csv` (1.4 MB)
- ✅ `welding_dataset_[timestamp].xlsx` (2.1 MB)
- ✅ `welding_dataset_[timestamp].json` (3.6 MB)
- ✅ `data_dictionary_[timestamp].json`
- ✅ `data_dictionary_[timestamp].txt`
- ✅ `summary_statistics_[timestamp].txt`

### Step 2: Load and Explore Data

#### Python (Pandas)
```python
import pandas as pd

# Load CSV
df = pd.read_csv('welding_dataset/welding_dataset_20251027_033338.csv')

# Quick overview
print(df.shape)  # (2000, 49)
print(df.head())

# Check target variable
print(df['Thermal_Cycles_to_Failure'].describe())
```

#### Excel
Simply open `welding_dataset_[timestamp].xlsx` in Excel, LibreOffice, or Google Sheets.

The file has 4 sheets:
1. **Complete_Dataset** - All 49 features
2. **Input_Parameters** - 20 controllable variables
3. **Characterization_Metrics** - 13 immediate quality measures
4. **Performance_Metrics** - 13 long-term performance indicators

#### R
```r
library(readr)
df <- read_csv("welding_dataset/welding_dataset_20251027_033338.csv")
summary(df$Thermal_Cycles_to_Failure)
```

### Step 3: Run Analysis
```bash
python3 analyze_dataset.py
```

This will show you:
- Dataset statistics
- Feature distributions
- Correlation analysis
- Performance by technique
- Key insights and recommendations

### Step 4: Start ML Development

#### Install ML Libraries
```bash
pip install scikit-learn xgboost lightgbm matplotlib seaborn
```

#### Run Example Training Script
```bash
python3 example_ml_training.py
```

This provides templates for:
- Data preprocessing
- Feature engineering
- Model training
- Inverse design optimization

## 📊 Key Dataset Features

### Primary Target
**Thermal_Cycles_to_Failure** - Number of thermal cycles before weld failure
- Range: 100 - 12,000 cycles
- Mean: ~3,827 cycles
- Goal: Maximize this metric

### Input Parameters (20 features)
- Materials: Anode/Cathode (Cu, Al, Ni, Steel, Ti)
- Techniques: Ultrasonic, Laser, Resistance Spot, TIG, Friction Stir
- Process: Power, amplitude, force, pressure, time, speed
- Environment: Temperature, humidity, atmosphere

### Quality Metrics (13 features)
- Weld strength, joint resistance
- Nugget diameter, penetration depth
- Porosity, surface roughness
- Microhardness, grain size

### Performance Metrics (13 features)
- Thermal cycles to failure ⭐
- Retained strength, resistance increase
- Fatigue life, max operating temperature
- Overall performance score

## 🎯 Common Use Cases

### 1. Forward Prediction
**Goal**: Predict performance from input parameters

```python
# Select features
input_cols = [col for col in df.columns if any(x in col for x in 
              ['Material', 'Thickness', 'Power', 'Amplitude', 'Force'])]
X = df[input_cols]
y = df['Thermal_Cycles_to_Failure']

# Train model
from sklearn.ensemble import GradientBoostingRegressor
model = GradientBoostingRegressor()
model.fit(X_train, y_train)
```

### 2. Inverse Design
**Goal**: Find optimal parameters for target performance

```python
# Train forward model
# Then use optimization:
from scipy.optimize import minimize

def objective(params):
    # Predict performance from params
    X_new = create_feature_vector(params)
    predicted_cycles = model.predict(X_new)
    return -predicted_cycles[0]  # Negative for maximization

# Optimize
result = minimize(objective, x0=initial_params, bounds=param_bounds)
optimal_params = result.x
```

### 3. Quality Control
**Goal**: Classify if design meets requirements

```python
# Binary classification
X = df[input_cols]
y = df['Optimal_Design']  # 1 if meets quality + performance

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier()
classifier.fit(X_train, y_train)
```

### 4. Multi-Objective Optimization
**Goal**: Balance multiple objectives

```python
# Objectives:
# - Maximize thermal cycles
# - Minimize resistance increase
# - Minimize cost

from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2

# Define multi-objective problem
# Run NSGA-II or similar
```

## 📈 Best Practices

### Data Splitting
```python
from sklearn.model_selection import train_test_split

# Stratify by technique for representative splits
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=df['Welding_Technique'], random_state=42
)
```

### Feature Engineering
```python
# Material mismatch
df['thermal_expansion_mismatch'] = abs(
    get_property(df['Anode_Material'], 'thermal_expansion') -
    get_property(df['Cathode_Material'], 'thermal_expansion')
)

# Interaction terms
df['power_time_interaction'] = df['Power_W'] * df['Time_ms']

# Ratios
df['thickness_ratio'] = df['Anode_Thickness_um'] / df['Cathode_Thickness_um']
```

### Cross-Validation
```python
from sklearn.model_selection import cross_val_score

# Use GroupKFold to avoid data leakage
scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
```

## 🔍 Important Insights from Analysis

1. **Best Technique**: Laser welding (avg performance score: 53.4)
2. **Best Materials**: Ni-Ni combination performs best
3. **Critical Quality Metrics**:
   - Low porosity (<3%) → 676% improvement in thermal cycling
   - Low residual stress → Better fatigue performance
   - High interfacial bonding → Better retention

4. **Strong Correlations** with thermal cycling:
   - Positive: Microhardness, nugget diameter, interfacial bonding
   - Negative: Porosity, crack density, resistance increase

## 🛠️ Troubleshooting

### Issue: Dataset not found
```bash
# Regenerate dataset
python3 generate_welding_dataset.py
```

### Issue: Missing dependencies
```bash
# Install core packages
pip install numpy pandas openpyxl

# Install ML packages
pip install scikit-learn xgboost lightgbm matplotlib seaborn
```

### Issue: Memory error
```python
# Load specific columns only
df = pd.read_csv('dataset.csv', usecols=['col1', 'col2', ...])

# Or load in chunks
for chunk in pd.read_csv('dataset.csv', chunksize=500):
    process(chunk)
```

## 📚 Next Steps

1. ✅ **Explore** - Run `analyze_dataset.py` to understand the data
2. ✅ **Feature Engineer** - Create domain-specific features
3. ✅ **Model** - Try different algorithms (see `example_ml_training.py`)
4. ✅ **Optimize** - Implement inverse design for your application
5. ✅ **Validate** - Test predictions against physical constraints
6. ✅ **Deploy** - Integrate into manufacturing workflow

## 🎓 Learning Resources

- **README.md** - Comprehensive dataset documentation
- **data_dictionary_[timestamp].txt** - Detailed feature descriptions
- **summary_statistics_[timestamp].txt** - Statistical overview
- **example_ml_training.py** - ML workflow templates

## 💡 Pro Tips

1. Start with gradient boosting (XGBoost/LightGBM) - they work well out of the box
2. Material property mismatches are critical features
3. Use technique-specific models for better performance
4. Always validate predictions with domain knowledge
5. Low porosity (<3%) is crucial for thermal cycling
6. Consider multi-objective optimization for real-world applications

## 🤝 Support

Having issues? Check:
1. README.md for detailed documentation
2. data_dictionary files for feature definitions
3. Run `analyze_dataset.py` to verify data integrity

---

**Ready to build world-class ML models for welding optimization!** 🚀
