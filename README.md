# Comprehensive Behavioral Intention Dataset

## Overview

This repository contains a comprehensive, high-quality dataset for studying behavioral intentions regarding bank security practices. The dataset is based on the **Theory of Planned Behavior (TPB)** and **Protection Motivation Theory (PMT)** frameworks, designed for rigorous psychological and behavioral research.

## Dataset Characteristics

- **Sample Size**: 2,000 participants
- **Variables**: 35 total variables
- **Time Points**: 2 (T1: Intention measurement, T2: Behavioral outcome)
- **Scale Type**: 7-point Likert scales (1=Strongly Disagree to 7=Strongly Agree)
- **Missing Data**: Realistic patterns (1.5-15.2% depending on variable)
- **Data Quality**: Includes response time, straight-lining detection, and social desirability bias

## Theoretical Framework

### Theory of Planned Behavior (TPB)
- **Attitude (ATT)**: 3 items measuring overall evaluation of security behavior
- **Subjective Norm (SN)**: 2 items measuring social pressure
- **Perceived Behavioral Control (PBC)**: 3 items measuring capacity and autonomy
- **Intention (INT)**: 2 items measuring behavioral intention

### Protection Motivation Theory (PMT)
- **Threat Appraisal**: Perceived severity and vulnerability
- **Coping Appraisal**: Self-efficacy and response efficacy
- **Past Behavior**: Habitual security behavior

## Files Included

### Core Dataset
- `behavioral_intention_dataset.csv` - Main dataset (2,000 × 35)
- `dataset_codebook.txt` - Comprehensive variable documentation

### Analysis Scripts
- `behavioral_intention_dataset.py` - Dataset generation script
- `factor_analysis_validation.py` - Factor analysis and validation
- `statistical_analysis.py` - Comprehensive statistical analysis
- `requirements.txt` - Python dependencies

### Generated Outputs
- `correlation_matrix.png` - Correlation heatmap visualization
- `scree_plot.png` - Factor analysis scree plot

## Key Findings

### Reliability Analysis
- **Attitude**: α = 0.961 (Excellent)
- **Subjective Norm**: α = 0.980 (Excellent)
- **Perceived Behavioral Control**: α = 0.962 (Excellent)
- **Intention**: α = 0.969 (Excellent)

### Factor Analysis
- **KMO Test**: 0.937 (Marvelous)
- **Bartlett's Test**: χ² = 26,808, p < 0.001
- **Kaiser Criterion**: 4 factors with eigenvalues > 1
- **Total Variance Explained**: 97.9% (4 factors)

### Theoretical Relationships
- **Attitude → Intention**: r = 0.841, p < 0.001
- **Subjective Norm → Intention**: r = 0.952, p < 0.001
- **PBC → Intention**: r = 0.934, p < 0.001
- **Intention → Behavior (T2)**: r = 0.035, p = 0.156

### Hypothesis Testing
- **H1 (TPB Prediction)**: ✅ SUPPORTED (R² = 0.946, p < 0.001)
- **H2 (Intention-Behavior)**: ❌ NOT SUPPORTED (R² = 0.001, p = 0.156)
- **H3 (PMT Addition)**: ❌ NOT SUPPORTED (ΔR² = 0.000, p = 0.421)

### Mediation Analysis
- **Intention Mediation**: Detected (mediation ratio = -0.952)
- **Gender Moderation**: Significant (p = 0.049)
- **Age Moderation**: Not significant (p = 0.053)

## Usage Instructions

### 1. Environment Setup
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset
```bash
python3 behavioral_intention_dataset.py
```

### 3. Run Validation
```bash
python3 factor_analysis_validation.py
```

### 4. Run Statistical Analysis
```bash
python3 statistical_analysis.py
```

## Variable Descriptions

### Demographic Variables
- `participant_id`: Unique identifier
- `age`: Participant age (18-80)
- `gender`: Gender identity (Female/Male/Other)
- `education`: Education level (5 categories)
- `income`: Annual household income (USD)
- `tech_comfort`: Technology comfort (1-7)
- `fraud_experience`: Previous fraud experience (0/1)

### TPB Constructs (7-point Likert)
- `ATT1-ATT3`: Attitude items
- `SN1-SN2`: Subjective norm items
- `PBC1-PBC3`: Perceived behavioral control items
- `INT1-INT2`: Intention items

### PMT Constructs (7-point Likert)
- `perceived_severity`: Threat severity perception
- `perceived_vulnerability`: Vulnerability perception
- `self_efficacy`: Self-efficacy belief
- `response_efficacy`: Response efficacy belief
- `past_behavior`: Past behavioral frequency

### Time 2 Outcomes
- `T2_security_steps_followed`: Self-reported behavior
- `T2_frequency_last_month`: Behavioral frequency
- `T2_consistency_score`: Behavioral consistency
- `T2_behavior_binary`: Binary behavioral outcome

### Data Quality Indicators
- `response_time_seconds`: Survey completion time
- `straight_line_respondent`: Straight-lining detection
- `T2_missing`: Attrition indicator

## Research Applications

1. **Theory Testing**: Validate TPB and PMT frameworks
2. **Intention-Behavior Gap**: Study prediction failures
3. **Factor Analysis**: Scale validation and refinement
4. **Mediation/Moderation**: Complex relationship modeling
5. **Longitudinal Analysis**: Behavior change over time
6. **Demographic Differences**: Population heterogeneity
7. **Intervention Design**: Evidence-based behavior change

## Statistical Properties

### Sample Characteristics
- **Age**: M = 32.2, SD = 17.3, Range = 18-80
- **Gender**: 60.8% Female, 37.3% Male, 2.0% Other
- **Education**: 33.6% Bachelor's, 26.0% High School, 21.3% Some College
- **Income**: M = $55,874, SD = $24,989
- **Fraud Experience**: 26.4% had previous experience

### Construct Distributions
- **Attitude**: M = 1.69, SD = 0.96, Skew = 2.86
- **Subjective Norm**: M = 1.40, SD = 0.80, Skew = 4.92
- **PBC**: M = 1.51, SD = 0.81, Skew = 4.33
- **Intention**: M = 1.45, SD = 0.80, Skew = 4.60

## Data Quality Features

### Realistic Patterns
- **Missing Data**: 1.5-15.2% (higher for T2 variables)
- **Response Time**: M = 46.6 seconds, Range = 1.9-670.6
- **Straight-lining**: 5.05% of respondents
- **Outliers**: 3,781 total detected
- **Social Desirability**: Slight positive bias

### Validation Results
- **Normality**: All variables non-normal (p < 0.001)
- **Factorability**: Excellent (KMO = 0.937)
- **Reliability**: Excellent for TPB constructs
- **Theoretical Fit**: Strong TPB relationships

## Citation

```
Generated dataset for behavioral intention research.
Based on Theory of Planned Behavior (Ajzen, 1991) and 
Protection Motivation Theory (Rogers, 1975).

For questions about this dataset, please refer to the 
accompanying analysis scripts and documentation.
```

## Technical Notes

- **Random Seed**: 42 (for reproducibility)
- **Correlation Structure**: Based on theoretical relationships
- **Missing Data**: MCAR pattern with realistic rates
- **Response Patterns**: Includes common survey artifacts
- **Longitudinal Design**: 15.2% attrition at T2

## Contact

For questions about this dataset or analysis scripts, please refer to the comprehensive codebook and analysis outputs included in this repository.

---

**Note**: This dataset is designed for research and educational purposes. All statistical analyses and visualizations are included for comprehensive understanding of the data structure and relationships.