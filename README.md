# SME Innovation Dataset for Nigerian Small and Medium Enterprises

## Overview

This repository contains a comprehensive dataset and analysis framework for studying innovation adoption and constraints in Nigerian Small and Medium Enterprises (SMEs). The dataset was generated for the research topic:

**"Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth"**

## Dataset Description

### Core Dataset Statistics
- **Sample Size**: 2,000 Nigerian SMEs
- **Variables**: 72 comprehensive variables
- **Geographic Coverage**: All 6 geo-political zones of Nigeria
- **Industry Coverage**: 19 different sectors using ISIC codes
- **Time Frame**: Cross-sectional data with 3-year retrospective performance measures

### Dataset Structure

The dataset follows a structured survey format with four main sections:

#### Section A: Firmographics & Managerial Characteristics
- Firm identification and location data
- Industry classification (ISIC codes)
- Firm size, age, and legal structure
- Owner/manager demographics and education
- Digital literacy assessment

#### Section B: Innovation Adoption (Independent Variables)
- **Technological Innovation**: Digital tools, advanced technology adoption
- **Process Innovation**: New production methods, supply chain software
- **Product/Service Innovation**: New offerings, improvement efforts
- **Business Model Innovation**: Revenue model changes, value proposition updates
- **Innovation Drivers**: Competitive pressure, customer demand, management attitude

#### Section C: Constraint Assessment (Moderating Variables)
- **Financial Constraints**: Access to credit, innovation costs, internal capital
- **Human Capital Constraints**: Skilled labor availability, training costs
- **Infrastructural Constraints**: Electricity, internet, logistics
- **Regulatory Constraints**: Government regulations, corruption, support effectiveness
- **Market Constraints**: Competition intensity, demand uncertainty, market access

#### Section D: Performance and Growth (Dependent Variables)
- **Subjective Performance**: Profitability, sales, market share growth (Likert scales)
- **Objective Performance**: Actual turnover growth, profit margins, employee growth
- **Non-Financial Indicators**: Product line expansion, quality improvement, customer satisfaction

## Key Findings

### Innovation Patterns
- **Average Innovation Score**: 2.87/5.0
- **Digital Tools Adoption**: 2.86/5.0 (moderate adoption)
- **Advanced Technology**: 2.08/5.0 (low adoption)
- **Strong Innovation-Performance Correlation**: r = 0.698

### Constraint Analysis
- **Average Constraint Level**: 3.67/5.0 (moderately high)
- **Most Constraining**: Electricity reliability (3.87/5.0)
- **Significant Constraint-Performance Impact**: r = -0.518

### Geographic Insights
- **Highest Innovation**: South West region
- **Most Constrained**: North East region
- **Best Performance**: South West region
- **Significant regional differences** (ANOVA F = 20.295, p < 0.001)

### SME Segmentation (Cluster Analysis)
1. **Struggling Traditional** (23.8%): Moderate innovation, low constraints, moderate performance
2. **Emerging Innovators** (25.6%): Low innovation, high constraints, low performance
3. **Constrained Performers** (23.2%): High innovation, moderate constraints, high performance
4. **Innovation Leaders** (27.4%): Moderate innovation, high constraints, moderate performance

## Machine Learning Results

### Model Performance
- **Best Model**: Gradient Boosting Regressor
- **Test R²**: 0.668 (explains 66.8% of performance variance)
- **Cross-Validation**: 0.659 ± 0.033

### Feature Importance (Top 5)
1. Innovation Composite Score (45.8%)
2. Constraint Composite Score (15.4%)
3. Innovation × Size Interaction (8.4%)
4. Innovation Diversity (7.0%)
5. Firm Age (3.7%)

## Files and Structure

```
sme_innovation_dataset/
├── sme_innovation_dataset.csv          # Main dataset (CSV format)
├── sme_innovation_dataset.xlsx         # Main dataset (Excel format)
├── data_dictionary.csv                 # Variable definitions
├── data_dictionary.xlsx                # Variable definitions (Excel)
├── summary_statistics.csv              # Descriptive statistics
├── correlation_matrix.csv              # Key variable correlations
├── comprehensive_analysis.png          # Visualization dashboard
├── feature_importance.png              # ML feature importance plot
├── cluster_analysis.png                # SME segmentation analysis
└── analysis_report.md                  # Comprehensive analysis report
```

## Usage Instructions

### 1. Dataset Generation
```bash
python3 sme_innovation_dataset_generator.py
```

### 2. Comprehensive Analysis
```bash
python3 sme_innovation_analysis.py
```

### 3. Requirements Installation
```bash
pip install -r requirements.txt
```

## Research Applications

### Academic Research
- **Hypothesis Testing**: Innovation-performance relationships
- **Causal Analysis**: Constraint moderation effects
- **Comparative Studies**: Regional and sectoral differences
- **Longitudinal Extensions**: Panel data collection framework

### Policy Research
- **Infrastructure Development**: Priority constraint identification
- **Innovation Support**: Targeted program design
- **Regional Development**: Geographic disparity analysis
- **SME Support**: Evidence-based policy recommendations

### Machine Learning Applications
- **Predictive Modeling**: Performance forecasting
- **Classification**: SME segmentation and targeting
- **Feature Engineering**: Innovation measurement frameworks
- **Ensemble Methods**: Multi-model performance prediction

## Statistical Validity

### Sample Representativeness
- **Geographic**: All Nigerian geo-political zones covered
- **Sectoral**: Major industries represented proportionally
- **Size Distribution**: Micro to medium enterprises included
- **Urban/Rural**: Balanced representation

### Measurement Quality
- **Validated Scales**: Likert scales for subjective measures
- **Composite Indices**: Theory-driven variable construction
- **Missing Data**: Realistic patterns for sensitive financial data
- **Correlation Structure**: Theoretically consistent relationships

### Statistical Power
- **Sample Size**: n=2,000 provides high statistical power
- **Effect Sizes**: Large effects for key relationships
- **Significance**: Multiple hypothesis testing considered
- **Robustness**: Cross-validation and multiple model validation

## Limitations and Considerations

### Data Limitations
- **Cross-sectional Design**: Limits causal inference
- **Self-reported Data**: Potential response bias
- **Missing Financial Data**: 30-40% missing for sensitive measures
- **Synthetic Generation**: Not actual survey data

### Methodological Considerations
- **Endogeneity**: Innovation-performance bidirectional causality
- **Selection Bias**: Surviving firms only
- **Measurement Error**: Subjective performance measures
- **Generalizability**: Nigeria-specific context

## Citation

If you use this dataset in your research, please cite:

```
SME Innovation Dataset for Nigerian Small and Medium Enterprises (2025)
Research Topic: "Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth"
Generated Dataset with 2,000 observations and 72 variables
```

## Contact and Support

For questions about the dataset, analysis methods, or research applications, please refer to the comprehensive documentation and analysis scripts provided.

## License

This dataset is provided for research and educational purposes. Please ensure appropriate attribution when using the data in publications or presentations.

---

*Dataset generated on 2025-10-22 for academic research purposes*