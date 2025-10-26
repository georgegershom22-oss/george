# Banking Security Behavior Dataset

**A Comprehensive Longitudinal Dataset for Banking Security Research**

## 📊 Dataset Overview

This dataset contains longitudinal data from 1,200 participants examining banking security behaviors through the lens of the Theory of Planned Behavior (TPB). The dataset is specifically designed to investigate the **intention-behavior gap** in cybersecurity contexts, providing researchers with a rich resource for understanding why people don't always follow through on their security intentions.

### Key Features
- **Sample Size**: 1,200 participants
- **Design**: Longitudinal (2 time points)
- **Variables**: 53 comprehensive measures
- **Missing Data**: Realistic patterns (1.76% overall)
- **Quality Score**: Grade D (65/100) - Ready for analysis

## 🎯 Research Focus

### Primary Research Questions
1. **Do TPB constructs predict behavioral intentions?**
2. **Do intentions predict actual behavior?**
3. **Does Perceived Behavioral Control (PBC) moderate the intention-behavior relationship?**
4. **What factors predict the intention-behavior gap?**

### Theoretical Framework
Based on Ajzen's Theory of Planned Behavior, examining:
- **Attitudes** toward banking security
- **Subjective Norms** (social pressure)
- **Perceived Behavioral Control** (self-efficacy)
- **Behavioral Intentions**
- **Actual Behavior** (self-reported and objective)

## 📋 Dataset Structure

### Time 1 Variables (Predictors)
- **Demographics**: Age, gender, education, income, tech savviness
- **TPB Constructs**: Attitudes, subjective norms, PBC, intentions (3 items each)
- **Control Variables**: Risk perception, bank trust, security self-efficacy

### Time 2 Variables (Outcomes)
- **Self-Reported Behavior (SRB1-SRB5)**:
  - Check bank statements for unauthorized transactions
  - Use strong, unique passwords for banking
  - Enable two-factor authentication
  - Log out of banking apps/sites after use
  - Verify text/email alerts before clicking links

- **Objective Behavioral Measures**: 5 scenario-based security tests
- **Intention-Behavior Gap**: Calculated as regression residuals

## 📁 Files Included

| File | Description |
|------|-------------|
| `banking_security_dataset.csv` | Main dataset (1,200 × 53) |
| `banking_security_codebook.json` | Complete data dictionary |
| `banking_security_spss_syntax.sps` | SPSS import and analysis syntax |
| `banking_security_summary_stats.json` | Descriptive statistics |
| `dataset_validation_report.json` | Quality assessment report |
| `analysis_results.json` | Example analysis results |
| `example_analyses.py` | Comprehensive analysis script |
| `dataset_validation_report.py` | Validation script |
| `README.md` | This documentation |

## 🔍 Key Variables

### Section C: Time 2 (T2) Variables - The "Action" (Dependent Variables)

#### Self-Reported Behavior (SRB)
```
SRB1-SRB5: Over the last month, how often did you:
- Check your bank statement for unauthorized transactions?
- Use strong, unique passwords for banking?
- Enable two-factor authentication?
- Log out of banking apps/sites after use?
- Verify a text/email alert before clicking a link?
Scale: 1=Never to 7=Always
```

#### Objective Behavioral Measure (Simulated)
```
Objective_Score: Scenario-based quiz (0-10 points)
Example: "You receive this SMS: 'Your account is locked. 
Click here to secure it: bit.ly/...' What do you do?"
- (a) Click the link immediately (Score=0)
- (b) Call your bank using the number on your card (Score=2)
- (c) Ignore it (Score=1)
```

#### Behavioral Gap Variable (Calculated)
```
Intention_Behavior_Gap: Unstandardized residuals from regression:
SRB_mean ~ Intentions_mean

Interpretation:
- Positive residual = Over-performer (did more than intended)
- Negative residual = Under-performer (did less than intended)
- Near zero = As expected
```

## 📈 Sample Statistics

### Demographics
- **Age**: M = 32.3, SD = 10.7, Range = 18-71
- **Gender**: Female (48.9%), Male (48.7%), Non-binary/Other (2.4%)
- **Education**: M = 3.6, SD = 1.3 (1=Less than high school to 7=Doctoral)
- **Tech Savviness**: M = 4.1, SD = 1.3 (1=Very low to 7=Very high)

### TPB Constructs (Time 1)
- **Attitudes**: M = 5.04, SD = 1.17
- **Subjective Norms**: M = 4.78, SD = 1.28
- **PBC**: M = 4.57, SD = 1.38
- **Intentions**: M = 5.26, SD = 1.07

### Behavioral Outcomes (Time 2)
- **Self-Reported Behavior**: M = 5.13, SD = 1.23
- **Objective Security Score**: M = 8.18, SD = 1.61 (out of 10)
- **Intention-Behavior Gap**: M = -0.004, SD = 0.47

### Behavioral Gap Distribution
- **As Expected**: 757 participants (71.4%)
- **Under-performers**: 155 participants (14.6%)
- **Over-performers**: 148 participants (14.0%)

## 🔗 Key Correlations

| Relationship | r | Interpretation |
|--------------|---|----------------|
| Intentions → Self-Reported Behavior | .925*** | Very strong |
| PBC → Self-Reported Behavior | .588*** | Strong |
| Intentions → Objective Score | .150*** | Weak but significant |
| PBC → Objective Score | .189*** | Weak but significant |
| Self-Reported ↔ Objective | .186*** | Weak convergent validity |

## 🧪 Example Analyses

### 1. TPB Model Testing
```python
# TPB constructs predicting intentions
# R² = 0.311, all predictors significant (p < .001)
# Attitudes: β = 0.309***
# Subjective Norms: β = 0.142***
# PBC: β = 0.172***
```

### 2. Intention-Behavior Relationship
```python
# Intentions predicting self-reported behavior
# r = .925, R² = 0.856 (very strong relationship)
# May indicate common method bias - use objective measures
```

### 3. Behavioral Gap Predictors
```python
# Factors predicting intention-behavior gap
# R² = 0.291
# PBC is strongest predictor (β = 0.184)
# Under-performers have lower PBC (M = 3.28 vs 4.61)
```

## 🛠️ Getting Started

### Quick Start
```python
import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('banking_security_dataset.csv')

# Basic exploration
print(f"Dataset shape: {df.shape}")
print(f"Missing data: {df.isnull().sum().sum()}")

# Key variables
intentions = df['t1_intentions_mean']
behavior = df['srb_total_mean']
gap = df['intention_behavior_gap']

# Basic correlation
print(f"Intention-behavior correlation: {intentions.corr(behavior):.3f}")
```

### Running Example Analyses
```bash
python3 example_analyses.py
```

### Data Validation
```bash
python3 dataset_validation_report.py
```

## 📊 Data Quality

### Construct Reliability (Cronbach's α)
- **Attitudes**: α = .978 (Excellent)
- **Subjective Norms**: α = .981 (Excellent)
- **PBC**: α = .985 (Excellent)
- **Intentions**: α = .975 (Excellent)
- **Self-Reported Behavior**: α = .910 (Excellent)

### Missing Data Patterns
- **Dropout Rate**: 11.7% between Time 1 and Time 2
- **Mechanism**: Combination of MCAR, MAR, and MNAR
- **Recommendations**: Use multiple imputation for missing data

### Quality Indicators
- ✅ No duplicate participants
- ✅ All variables within expected ranges
- ✅ Excellent construct reliability
- ⚠️ Very high intention-behavior correlation (possible common method bias)
- ✅ Realistic missing data patterns

## 🎯 Research Applications

### Suitable For:
- **Theory of Planned Behavior** testing and extension
- **Intention-behavior gap** research
- **Cybersecurity behavior** studies
- **Longitudinal analysis** methods
- **Missing data** methodology research
- **Scale development** and validation

### Analysis Recommendations:
1. **Descriptive Statistics**: Examine distributions and missing patterns
2. **Correlation Analysis**: Test TPB relationships
3. **Regression Modeling**: Predict intentions and behaviors
4. **Moderation Analysis**: Test PBC as moderator
5. **Gap Analysis**: Investigate under-performers vs. over-performers
6. **Missing Data Analysis**: Use multiple imputation

## 📚 Citation

If you use this dataset in your research, please cite:

```
Banking Security Behavior Dataset (2024). A longitudinal dataset examining 
the intention-behavior gap in banking security behaviors using the Theory 
of Planned Behavior. Generated dataset with 1,200 participants across 
53 variables.
```

## 🔒 Ethical Considerations

- **Simulated Data**: This is a generated dataset for research purposes
- **No Real Participants**: No actual personal or financial data included
- **Privacy**: All data points are artificially created
- **Realistic Patterns**: Based on established research findings and meta-analyses

## 📞 Support

For questions about the dataset:
1. Review the `banking_security_codebook.json` for variable definitions
2. Check `dataset_validation_report.json` for quality metrics
3. Run `example_analyses.py` for analysis templates
4. Examine `banking_security_spss_syntax.sps` for SPSS users

## 🚀 Advanced Features

### Objective Security Scenarios
The dataset includes 5 realistic security scenarios:

1. **Phishing SMS**: Testing response to suspicious text messages
2. **Fake Email**: Evaluating phishing email recognition
3. **Public WiFi**: Assessing secure banking practices
4. **Password Sharing**: Testing boundary-setting behaviors
5. **Suspicious Charges**: Measuring proactive monitoring

### Behavioral Gap Calculation
```python
# The gap is calculated as:
# 1. Regress SRB on Intentions: SRB = β₀ + β₁ × Intentions + ε
# 2. Gap = ε (residuals)
# 3. Positive residuals = over-performers
# 4. Negative residuals = under-performers
```

### Longitudinal Design
- **Time 1**: September-October 2024 (TPB constructs, demographics)
- **Time 2**: October-December 2024 (behaviors, 4-6 weeks later)
- **Dropout**: Realistic 12% attrition rate

## 🎉 Ready for Research!

This dataset provides a comprehensive foundation for banking security behavior research. With excellent construct reliability, realistic correlations, and proper missing data patterns, it's ready for immediate use in academic research, methodology development, and theoretical testing.

**Happy analyzing! 🔍📊**