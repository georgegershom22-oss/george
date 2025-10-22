# Nigerian SME Innovation Adoption and Constraints Dataset

## 🎯 Research Context
**Research Topic:** Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth

This comprehensive dataset is designed to support advanced machine learning analysis of innovation adoption patterns, constraint factors, and their impact on SME performance in Nigeria.

## 📊 Dataset Overview
- **Total Firms:** 2,000 Nigerian SMEs
- **Total Variables:** 66 variables across 4 main sections
- **Geographic Coverage:** All 36 states + FCT, representing all 6 geopolitical zones
- **Industry Coverage:** 15 major industry sectors with ISIC codes
- **Data Quality:** Realistic correlations and relationships based on Nigerian SME characteristics

## 📁 Files Included

### Dataset Files
1. **`nigerian_sme_innovation_dataset.csv`** - Main dataset (CSV format)
2. **`nigerian_sme_innovation_dataset.xlsx`** - Multi-sheet Excel workbook
3. **`nigerian_sme_innovation_dataset.json`** - Structured JSON format

### Documentation Files
4. **`DATASET_DOCUMENTATION.md`** - Comprehensive dataset documentation
5. **`CODEBOOK.md`** - Detailed variable definitions and coding schemes
6. **`README.md`** - This overview file

### Analysis Scripts
7. **`generate_sme_dataset_fixed.py`** - Dataset generation script
8. **`analyze_sme_dataset.py`** - Comprehensive analysis script
9. **`explore_dataset.py`** - Quick dataset exploration script

## 🏗️ Dataset Structure

### Section A: Firmographics & Managerial Characteristics (8 variables)
- Firm identification and location
- Industry classification with ISIC codes
- Firm age, size, and legal structure
- Owner/manager demographics and education
- Digital literacy assessment

### Section B: Innovation Adoption - Independent Variables (10 variables)
- **Technological Innovation:** Digital tools, advanced tech, digitization
- **Process Innovation:** New production/delivery methods
- **Product/Service Innovation:** New product launches and improvements
- **Business Model Innovation:** Revenue model changes
- **Innovation Drivers:** Competitive pressure, customer demand, management attitude

### Section C: Constraint Assessment - Moderating Variables (10 variables)
- **Financial Constraints:** Credit access, innovation costs, capital sufficiency
- **Human Capital Constraints:** Skilled labor, training costs, management capability
- **Infrastructural Constraints:** Electricity, internet, logistics
- **Regulatory Constraints:** Government regulations, corruption, support programs
- **Market Constraints:** Competition, demand uncertainty, international access

### Section D: Firm Performance and Growth - Dependent Variables (11 variables)
- **Subjective Performance:** Profitability, sales, market share growth
- **Objective Performance:** Turnover growth, profit growth, employee growth
- **Non-Financial Indicators:** Product lines, quality, customer satisfaction

### Derived Variables (3 variables)
- **Innovation Index:** Composite innovation score
- **Constraint Index:** Composite constraint score
- **Performance Index:** Composite performance score

## 🔍 Key Features

### Realistic Data Patterns
- **Geographic Distribution:** 70% urban, 30% rural (realistic for SMEs)
- **Industry Distribution:** Manufacturing and retail trade most common
- **Firm Size:** Heavily skewed towards small firms (1-10 employees)
- **Age Distribution:** Most SMEs are relatively young (0-10 years)

### Realistic Correlations
- Higher digital literacy → Higher innovation adoption
- Urban location → Better infrastructure and digitization
- Larger firms → More advanced technology adoption
- Innovation adoption → Higher performance
- Constraint levels → Lower performance

### Data Quality
- ✅ Complete dataset (no missing values)
- ✅ Realistic value ranges
- ✅ Proper correlation structures
- ✅ Balanced representation across categories

## 🚀 Usage Examples

### For Machine Learning Analysis
```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv('nigerian_sme_innovation_dataset.csv')

# Prepare features and target
X = df[['innovation_index', 'constraint_index', 'firm_age_years', 'num_employees']]
y = df['performance_index']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Model R² Score: {score:.3f}")
```

### For Statistical Analysis
```python
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('nigerian_sme_innovation_dataset.csv')

# Innovation analysis by industry
innovation_by_industry = df.groupby('industry')['innovation_index'].mean().sort_values(ascending=False)
print("Innovation by Industry:")
print(innovation_by_industry)

# Performance analysis by location
performance_by_location = df.groupby('location_type')['performance_index'].mean()
print("\nPerformance by Location:")
print(performance_by_location)
```

## 📈 Research Applications

### 1. Innovation Studies
- Analyze adoption patterns across industries and regions
- Identify key drivers of innovation adoption
- Study the impact of digital literacy on innovation

### 2. Constraint Analysis
- Identify major barriers to SME growth
- Compare constraint levels across regions
- Analyze the impact of different constraint types

### 3. Performance Modeling
- Predict SME performance using innovation and constraint variables
- Identify high-performing SME characteristics
- Develop performance improvement strategies

### 4. Policy Analysis
- Evaluate the effectiveness of government support programs
- Assess regional development needs
- Design targeted intervention programs

### 5. Regional Analysis
- Compare performance across geopolitical zones
- Identify regional innovation clusters
- Analyze urban vs. rural differences

## 🛠️ Technical Requirements

### Software Requirements
- **Python:** 3.7+ with pandas, numpy, scikit-learn
- **R:** 4.0+ with tidyverse packages
- **Excel:** 2016+ for Excel file access
- **SPSS/Stata:** For statistical analysis

### Memory Requirements
- **Dataset Size:** ~2MB (CSV), ~3MB (Excel), ~5MB (JSON)
- **Memory Usage:** ~50MB when loaded into pandas
- **Processing:** Suitable for standard statistical software

## 📚 Documentation

### Quick Start
1. **Explore:** Run `python3 explore_dataset.py` to see dataset structure
2. **Analyze:** Run `python3 analyze_sme_dataset.py` for comprehensive analysis
3. **Read:** Check `DATASET_DOCUMENTATION.md` for detailed information
4. **Reference:** Use `CODEBOOK.md` for variable definitions

### Variable Reference
- **Firmographics:** 8 variables covering firm and owner characteristics
- **Innovation:** 10 variables measuring various innovation types
- **Constraints:** 10 variables assessing different constraint categories
- **Performance:** 11 variables measuring firm performance and growth
- **Derived:** 3 composite indices for overall assessment

## 🎯 Research Potential

This dataset is specifically designed for:
- **Machine Learning Research:** Classification, regression, clustering
- **Policy Research:** SME development and innovation policy
- **Academic Research:** Innovation adoption and constraint studies
- **Business Research:** SME performance and growth analysis
- **Regional Studies:** Geographic and industry-specific analysis

## 📞 Support

For questions about the dataset:
1. Check the comprehensive documentation files
2. Review the codebook for variable definitions
3. Run the exploration script to understand the data structure
4. Use the analysis script as a starting point for your research

## 🔬 Citation

When using this dataset, please acknowledge:
- Research context: Nigerian SME innovation adoption and constraints
- Dataset purpose: Machine learning analysis of SME performance
- Methodology: Realistic data generation with proper correlations

---

**Dataset Generated:** 2024  
**Research Focus:** Innovation Adoption and Constraints in Nigerian SMEs  
**Target Audience:** Researchers, Policy Makers, Business Analysts  
**Analysis Ready:** ✅ Complete with documentation and analysis scripts