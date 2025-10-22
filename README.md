# Nigerian SME Innovation Research - Secondary Dataset

## 📊 Complete Dataset for Machine Learning Analysis

This repository contains a comprehensive secondary dataset for analyzing innovation adoption and constraints in Nigerian Small and Medium Enterprises (SMEs). The dataset spans **2015-2024** and includes macroeconomic indicators, technology adoption metrics, regional infrastructure data, sectoral performance, innovation barriers, and policy variables.

### 🎯 Research Focus
**"Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth"**

---

## 📁 Dataset Files

### Core Datasets (8 CSV files)

| File | Records | Description |
|------|---------|-------------|
| **macroeconomic_indicators.csv** | 10 | National economic indicators (GDP, inflation, interest rates, EODB) |
| **broadband_penetration_by_state.csv** | 100 | State-level digital infrastructure across 10 major states |
| **sectoral_growth_rates.csv** | 10 | Growth rates and GDP contribution for 14+ sectors |
| **technology_adoption_indices.csv** | 10 | FinTech, mobile money, digital payments, ICT development |
| **sme_landscape_indicators.csv** | 10 | SME sector structure, performance, and characteristics |
| **innovation_adoption_barriers.csv** | 60 | Regional barriers to innovation adoption (15 constraint types) |
| **regional_summary_statistics.csv** | 60 | Comprehensive regional ecosystem indicators |
| **policy_and_external_factors.csv** | 10 | Government interventions, institutional environment |

### Documentation

| File | Description |
|------|-------------|
| **DATA_DICTIONARY.md** | Complete data dictionary with variable descriptions, sources, insights |
| **README.md** | This file - dataset overview and quick start guide |

---

## 🔑 Key Features

### Temporal Coverage
- **10 years** of annual data (2015-2024)
- Captures Nigeria's recession (2016) and recovery
- Tracks FinTech revolution and digital transformation
- Shows COVID-19 impact (2020) and recovery

### Geographic Coverage
- **6 geopolitical regions**: South West, South East, South South, North Central, North West, North East
- **10 major states**: Lagos, Kano, Rivers, Kaduna, Oyo, Abuja FCT, Enugu, Borno, Anambra, Bauchi
- Urban-rural variations captured

### Thematic Coverage
1. **Macroeconomic Context**: GDP, inflation, exchange rates, unemployment
2. **Digital Infrastructure**: Broadband, mobile penetration, electricity access
3. **Technology Adoption**: FinTech, mobile money, e-commerce, digital payments
4. **SME Ecosystem**: 37-51 million SMEs, formality rates, survival rates
5. **Innovation Barriers**: 15 constraint types across regions
6. **Sectoral Dynamics**: 14+ sectors including ICT, manufacturing, trade
7. **Policy Interventions**: Government budgets, CBN schemes, SMEDAN programs
8. **Regional Disparities**: Ecosystem maturity, venture capital, innovation hubs

---

## 📈 Dataset Statistics

### Total Dataset Size
- **270 total records** across 8 files
- **120+ variables** covering economic, technological, institutional dimensions
- **Panel data structure** suitable for econometric analysis
- **Multi-level**: National, regional, state, sectoral observations

### Sample Insights from the Data

#### 🚀 Technology Adoption Growth (2015 → 2024)
- **FinTech Adoption**: 12.4% → 78.3% (+531% growth)
- **Mobile Money Users**: 8.5M → 102.3M (+1,103% growth)
- **ICT Development Index**: 3.24 → 6.48 (+100% improvement)
- **Tech-Enabled SMEs**: 8.7% → 49.7% (+471% growth)

#### 💡 Regional Disparities (2024)
- **Broadband Penetration**: South West (83.7%) vs North East (44.1%) - 90% gap
- **SME Revenue**: South West (₦14.7M) vs North East (₦7.6M) - 94% gap
- **Innovation Hubs**: South West (72) vs North East (14) - 5× difference
- **VC Investment**: South West (₦2.5B) vs North East (₦379M) - 6.5× difference

#### 🏢 SME Sector Evolution (2015 → 2024)
- **Total SMEs**: 37.1M → 51.2M (+38% growth)
- **GDP Contribution**: 48.2% → 54.2% (+6 percentage points)
- **Formalization Rate**: 15.6% → 23.2% (+49% relative increase)
- **Women Ownership**: 23.4% → 31.2% (+33% increase)

#### ⚠️ Top Innovation Barriers (2024 Average)
1. **Lack of Finance Access**: 65.8%
2. **Corruption/Bureaucracy**: 60.4%
3. **High Cost**: 56.7%
4. **Technical Skills Gap**: 60.7%
5. **Unreliable Power**: 55.7%

---

## 🤖 Machine Learning Applications

### Classification Problems
- **Innovation Adopter Classification**: Predict early vs. late adopters
- **SME Survival Prediction**: 5-year survival probability modeling
- **Credit Risk Assessment**: Default risk classification
- **Formalization Prediction**: Informal → formal transition likelihood

### Regression Problems
- **Revenue Prediction**: SME performance forecasting
- **Barrier Impact Quantification**: Constraint elasticity estimation
- **Infrastructure ROI**: Broadband impact on sectoral growth
- **Policy Effectiveness**: Intervention impact measurement

### Clustering Analysis
- **Regional Segmentation**: Ecosystem maturity typology
- **SME Archetypes**: Behavioral/characteristic clustering
- **Constraint Profiles**: Multi-dimensional barrier patterns
- **Technology Adoption Stages**: Diffusion curve segmentation

### Time Series Forecasting
- **Technology Diffusion**: S-curve modeling for FinTech adoption
- **Macroeconomic Scenarios**: SME outcome forecasting
- **Infrastructure Planning**: Broadband penetration projections
- **Policy Impact Trajectories**: Long-term intervention effects

### Causal Inference
- **Policy Impact Evaluation**: Difference-in-differences, synthetic control
- **Infrastructure Treatment Effects**: Regional variation exploitation
- **Constraint Relaxation Experiments**: Binding constraint identification
- **Intervention Timing**: Optimal policy deployment analysis

---

## 🛠️ Quick Start Guide

### Loading the Data (Python)

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load all datasets
macro = pd.read_csv('macroeconomic_indicators.csv')
broadband = pd.read_csv('broadband_penetration_by_state.csv')
sectors = pd.read_csv('sectoral_growth_rates.csv')
tech = pd.read_csv('technology_adoption_indices.csv')
sme = pd.read_csv('sme_landscape_indicators.csv')
barriers = pd.read_csv('innovation_adoption_barriers.csv')
regional = pd.read_csv('regional_summary_statistics.csv')
policy = pd.read_csv('policy_and_external_factors.csv')

# Quick exploration
print(f"Macroeconomic data shape: {macro.shape}")
print(f"Broadband data shape: {broadband.shape}")
print(f"Time period: {macro.Year.min()} - {macro.Year.max()}")

# Example: Merge national and regional data
merged = regional.merge(barriers, on=['Year', 'Region'], how='inner')
merged = merged.merge(policy, on='Year', how='left')

print(f"Merged dataset shape: {merged.shape}")
print(f"Available variables: {merged.columns.tolist()}")
```

### Example Analysis 1: FinTech Adoption Trends

```python
# Visualize FinTech adoption over time
plt.figure(figsize=(12, 6))
plt.plot(tech['Year'], tech['FinTech_Adoption_Rate_Percent'], 
         marker='o', linewidth=2, markersize=8)
plt.title('FinTech Adoption Rate in Nigeria (2015-2024)', fontsize=14, fontweight='bold')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Adoption Rate (%)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('fintech_adoption_trend.png', dpi=300)
plt.show()
```

### Example Analysis 2: Regional Barrier Comparison

```python
# Compare barriers across regions (2024 data)
barriers_2024 = barriers[barriers['Year'] == 2024]

barrier_cols = [col for col in barriers_2024.columns if 'Percent' in col]
barrier_means = barriers_2024[['Region'] + barrier_cols].set_index('Region').T

plt.figure(figsize=(14, 8))
sns.heatmap(barrier_means, annot=True, fmt='.1f', cmap='RdYlGn_r', 
            cbar_kws={'label': 'Percentage (%)'})
plt.title('Innovation Adoption Barriers by Region (2024)', fontsize=14, fontweight='bold')
plt.xlabel('Region', fontsize=12)
plt.ylabel('Barrier Type', fontsize=12)
plt.tight_layout()
plt.savefig('regional_barriers_heatmap.png', dpi=300)
plt.show()
```

### Example Analysis 3: Predictive Modeling Setup

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Prepare data for SME revenue prediction
regional_full = regional.merge(policy, on='Year')
regional_full = regional_full.merge(
    broadband.groupby(['Region', 'Year'])['Broadband_Penetration_Percent'].mean().reset_index(),
    on=['Region', 'Year']
)

# Define features and target
features = [
    'Broadband_Penetration_Percent', 
    'Venture_Capital_Investment_Million_NGN',
    'Business_Incubators_Count',
    'Government_SME_Budget_Billion_NGN',
    'Digital_Infrastructure_Score'
]
target = 'Average_SME_Revenue_Million_NGN'

# Prepare data
X = regional_full[features].dropna()
y = regional_full.loc[X.index, target]

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
train_score = model.score(X_train_scaled, y_train)
test_score = model.score(X_test_scaled, y_test)

print(f"Training R²: {train_score:.3f}")
print(f"Testing R²: {test_score:.3f}")

# Feature importance
importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature Importance:")
print(importance_df)
```

### Loading the Data (R)

```r
library(tidyverse)
library(lubridate)

# Load datasets
macro <- read_csv('macroeconomic_indicators.csv')
broadband <- read_csv('broadband_penetration_by_state.csv')
sectors <- read_csv('sectoral_growth_rates.csv')
tech <- read_csv('technology_adoption_indices.csv')
sme <- read_csv('sme_landscape_indicators.csv')
barriers <- read_csv('innovation_adoption_barriers.csv')
regional <- read_csv('regional_summary_statistics.csv')
policy <- read_csv('policy_and_external_factors.csv')

# Quick exploration
glimpse(macro)
summary(tech$FinTech_Adoption_Rate_Percent)

# Example: FinTech adoption visualization
ggplot(tech, aes(x = Year, y = FinTech_Adoption_Rate_Percent)) +
  geom_line(size = 1.2, color = "steelblue") +
  geom_point(size = 3, color = "darkblue") +
  labs(title = "FinTech Adoption Rate in Nigeria (2015-2024)",
       x = "Year", y = "Adoption Rate (%)") +
  theme_minimal() +
  theme(plot.title = element_text(size = 14, face = "bold"))
```

---

## 📊 Recommended Analysis Workflows

### Workflow 1: Barrier Impact Analysis
1. **Load**: `innovation_adoption_barriers.csv` + `regional_summary_statistics.csv`
2. **Merge**: By Year and Region
3. **Model**: Regress `Tech_Enabled_SMEs_Percent` on barrier variables
4. **Output**: Identify most binding constraints by region

### Workflow 2: Technology Diffusion Modeling
1. **Load**: `technology_adoption_indices.csv` + `broadband_penetration_by_state.csv`
2. **Feature Engineering**: Create lag variables, growth rates
3. **Model**: Logistic growth curves (S-curves) for FinTech adoption
4. **Forecast**: Predict 2025-2030 adoption trajectories

### Workflow 3: Policy Effectiveness Evaluation
1. **Load**: `policy_and_external_factors.csv` + `sme_landscape_indicators.csv`
2. **Merge**: By Year
3. **Model**: Difference-in-differences or panel fixed effects
4. **Output**: Estimate causal impact of CBN interventions on access to finance

### Workflow 4: Regional Ecosystem Clustering
1. **Load**: `regional_summary_statistics.csv` (2024 data)
2. **Features**: Innovation hubs, VC investment, digital infrastructure, SME density
3. **Model**: K-means or hierarchical clustering
4. **Output**: Ecosystem maturity typology (e.g., Leaders, Emerging, Laggards)

### Workflow 5: SME Survival Prediction
1. **Load**: All datasets, create regional-sectoral panel
2. **Target**: `SME_Survival_Rate_5Years_Percent`
3. **Features**: Macro, infrastructure, barriers, policy variables
4. **Model**: Random Forest, Gradient Boosting, or Neural Network
5. **Output**: Survival probability predictions by SME profile

---

## 🔬 Data Sources (Modeled After)

This synthetic dataset mimics patterns from authoritative Nigerian data sources:

### Primary Sources
- **Central Bank of Nigeria (CBN)**: Monetary policy, financial inclusion, FinTech data
- **National Bureau of Statistics (NBS)**: GDP, sectoral statistics, employment
- **Small and Medium Enterprises Development Agency of Nigeria (SMEDAN)**: SME landscape
- **Nigerian Communications Commission (NCC)**: Telecommunications and broadband data

### International Sources
- **World Bank**: Ease of Doing Business, macroeconomic indicators
- **International Telecommunication Union (ITU)**: ICT Development Index
- **Transparency International**: Corruption Perception Index

### Research Sources
- PwC Nigeria SME Surveys
- McKinsey Africa Growth Reports
- World Bank Enterprise Surveys
- EFInA Access to Financial Services

---

## ⚠️ Important Notes

### Data Authenticity
- This is **SYNTHETIC DATA** generated for research purposes
- Based on realistic patterns from literature review and domain knowledge
- **NOT actual historical records** from government/institutional sources
- Use for **methodology testing, exploratory analysis, hypothesis generation**

### Validation Required
- Results should be validated with actual primary data collection
- Consider this a **starting point** for research design
- Supplement with real-world case studies and interviews
- Cross-validate findings with published research

### Ethical Usage
- Acknowledge synthetic nature in all publications
- Do not misrepresent as actual government/institutional data
- Use appropriate disclaimers in research outputs
- Cite as: "Synthetic Nigerian SME Innovation Dataset (2025)"

---

## 📚 Research Applications

This dataset supports research on:

1. **Innovation Diffusion Theory**: Technology adoption patterns in developing economies
2. **Development Economics**: SME growth constraints and policy interventions
3. **Digital Transformation**: FinTech revolution and financial inclusion
4. **Regional Economics**: Spatial disparities in entrepreneurial ecosystems
5. **Machine Learning**: Predictive modeling for policy targeting
6. **Institutional Economics**: Governance quality and business environment
7. **Infrastructure Economics**: Broadband and electricity access impacts
8. **Gender Economics**: Women's entrepreneurship trends
9. **Public Policy**: SME support program effectiveness
10. **Causal Inference**: Natural experiments in development contexts

---

## 🎓 Educational Use Cases

### For Students
- **Data Science Projects**: Complete ML pipeline from EDA to deployment
- **Econometrics Assignments**: Panel data analysis, fixed effects models
- **Business Analytics**: Dashboard creation, insight generation
- **Policy Analysis**: Evidence-based policy recommendation exercises

### For Instructors
- **Teaching Dataset**: Realistic, multi-dimensional data for coursework
- **Thesis/Dissertation**: Secondary data for graduate research
- **Hackathons**: Machine learning competitions
- **Case Studies**: Nigerian SME ecosystem exploration

---

## 📞 Support and Contributions

### Questions?
- Refer to **DATA_DICTIONARY.md** for detailed variable descriptions
- Check this README for quick start examples
- Review source literature for context

### Potential Extensions
- Add micro-level SME survey data (firm-level characteristics)
- Include quarterly/monthly data for higher frequency analysis
- Expand to more states (all 36 states + FCT)
- Add social media/digital footprint variables
- Include climate/environmental factors

### Version History
- **v1.0** (Oct 2025): Initial release
  - 8 datasets, 270 records, 120+ variables
  - 10-year panel (2015-2024)
  - National, regional, state, sectoral coverage

---

## 📖 Recommended Reading

### Nigerian SME Context
- SMEDAN & NBS (2017). *National Survey of Micro, Small and Medium Enterprises*
- PwC Nigeria (2020). *MSME Survey Report*
- CBN (2022). *Microfinance Policy, Regulatory and Supervisory Framework*

### Innovation in Developing Economies
- Cirera & Maloney (2017). *The Innovation Paradox: Developing-Country Capabilities*
- Foster & Heeks (2013). "Innovation and scaling of ICT for the bottom-of-the-pyramid"
- World Bank (2020). *Doing Business Report*

### Machine Learning for Development
- Jean et al. (2016). "Combining satellite imagery and machine learning to predict poverty"
- Blumenstock et al. (2015). "Predicting poverty and wealth from mobile phone metadata"
- Burke & Lobell (2017). "Satellite-based assessment of yield variation"

---

## 🏆 Dataset Statistics Summary

| Metric | Value |
|--------|-------|
| **Total Files** | 10 (8 data + 2 documentation) |
| **Total Records** | 270 rows |
| **Total Variables** | 120+ unique variables |
| **Time Span** | 10 years (2015-2024) |
| **Geographic Coverage** | 6 regions, 10 states |
| **Sectoral Coverage** | 14+ industries |
| **File Size** | ~500 KB total |
| **Format** | CSV (UTF-8 encoding) |
| **Missing Values** | 0 (complete synthetic data) |
| **Data Structure** | Panel (time series + cross-sectional) |

---

## ✅ Quality Assurance

### Data Validation Checks Performed
- ✅ No missing values
- ✅ Consistent time periods across files
- ✅ Logical value ranges (e.g., percentages 0-100)
- ✅ Regional/state names standardized
- ✅ Currency units consistent (NGN/USD specified)
- ✅ Growth rates align with base values
- ✅ Temporal trends realistic (no sudden jumps)
- ✅ Regional disparities reflect known patterns

### Known Realistic Patterns Embedded
- ✅ 2016 recession reflected in GDP, manufacturing
- ✅ COVID-19 impact in 2020 (SME closures, digital surge)
- ✅ Naira depreciation trend (2015: ₦193/$1 → 2024: ₦845/$1)
- ✅ FinTech boom (2019-2024) captured
- ✅ North-South development gap consistent
- ✅ ICT sector as growth leader
- ✅ Declining oil GDP contribution (diversification)

---

## 🚀 Next Steps

### For Researchers
1. **Review DATA_DICTIONARY.md** thoroughly
2. **Load and explore** datasets using provided code snippets
3. **Formulate hypotheses** based on literature review
4. **Design ML experiments** (classification, regression, clustering)
5. **Validate synthetic findings** with primary data collection
6. **Publish results** with proper attribution and disclaimers

### For Policymakers (Conceptual Use)
1. **Identify key patterns** in barriers and adoption
2. **Benchmark regions** against best performers
3. **Simulate policy interventions** using predictive models
4. **Prioritize infrastructure investments** based on impact analysis
5. **Design targeted programs** for lagging regions/sectors

### For Entrepreneurs
1. **Understand regional ecosystems** (where to start business)
2. **Identify growth constraints** in your sector/region
3. **Benchmark performance** against averages
4. **Spot technology trends** for competitive advantage
5. **Plan expansion** to high-potential regions

---

**Generated**: October 22, 2025  
**Version**: 1.0  
**License**: Open for educational and research use (with attribution)  
**Format**: CSV + Markdown documentation  
**Total Size**: ~500 KB

**Ready for machine learning analysis!** 🎯🤖📊

---

*For detailed variable descriptions, data sources, and methodological notes, see **DATA_DICTIONARY.md***
