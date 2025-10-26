# Banking Security Behavior Dataset

## Overview

This dataset was generated to study the intention-behavior gap in banking security practices. It contains comprehensive data from 2,000 participants across two time points (T1 and T2), measuring intentions, behaviors, and the gap between them.

## Dataset Structure

### Sample Size
- **Total Participants**: 2,000
- **Time Points**: 2 (T1 baseline, T2 follow-up)
- **Variables**: 24

### Key Variables

#### T1 Baseline Variables (Time 1)
- `intention`: Intention to practice security behaviors (1-7 scale)
- `pbc`: Perceived Behavioral Control (1-7 scale)
- `attitude`: Attitude toward security behaviors (1-7 scale)
- `subjective_norm`: Subjective norm (1-7 scale)

#### T2 Action Variables (Time 2) - The Core of Your Research

**Self-Reported Behavior (SRB1-SRB5)**
- `SRB1_check_statements`: Check bank statement for unauthorized transactions (1-7 scale)
- `SRB2_unique_passwords`: Use strong, unique passwords for banking (1-7 scale)
- `SRB3_two_factor`: Enable two-factor authentication (1-7 scale)
- `SRB4_logout`: Log out of banking apps/sites after use (1-7 scale)
- `SRB5_verify_alerts`: Verify text/email alert before clicking a link (1-7 scale)

**Objective Behavioral Measure**
- `objective_score`: Scenario-based quiz score (0-10 scale)
  - Based on 10 realistic banking security scenarios
  - Measures actual knowledge and behavioral tendencies
  - Mitigates social desirability bias in self-reports

**Intention-Behavior Gap (Core Dependent Variable)**
- `intention_behavior_gap`: Residual score from regression (T2 behavior ~ T1 intention)
  - Positive values = Overperformers (did more than intended)
  - Negative values = Underperformers (the "Gap" - did less than intended)
  - This is the operationalization of your core concept

#### Demographic Variables
- `age`: Age in years (18-75)
- `gender`: Gender (Female/Male)
- `education`: Education level (1=High school, 5=Graduate degree)
- `income`: Income level (1=Under $25k, 6=Over $150k)
- `banking_experience`: Years of banking experience
- `tech_comfort`: Technology comfort level (1-7)
- `previous_incident`: Previous security incident (0=No, 1=Yes)

#### Contextual Variables
- `time_gap_weeks`: Time between T1 and T2 (weeks)
- `security_news_exposure`: Recent security news exposure (1-7)
- `app_usage_frequency`: Banking app usage frequency (1-7)
- `perceived_threat`: Perceived security threat level (1-7)
- `social_influence`: Social influence on security behaviors (1-7)

## Research Applications

### Primary Research Questions
1. **What predicts the intention-behavior gap in banking security?**
2. **How does Perceived Behavioral Control (PBC) moderate the intention-behavior relationship?**
3. **What factors influence actual security behavior beyond intentions?**

### Key Analyses Supported
- **Intention-Behavior Gap Analysis**: Core dependent variable ready for analysis
- **PBC Moderation**: Test PBC as moderator of intention-behavior relationship
- **Multi-method Validation**: Compare self-reported vs. objective behavioral measures
- **Predictive Modeling**: Identify factors that predict security behavior
- **Gap Categorization**: Classify participants as overperformers vs. underperformers

## Data Quality Features

### Realistic Relationships
- T1 intentions strongly correlate with T2 behaviors (r ≈ 0.6-0.7)
- PBC shows expected moderation effects
- Demographic variables influence both intentions and behaviors
- Objective and self-reported measures show convergent validity

### Statistical Properties
- **Intention-Behavior Gap**: Mean ≈ 0 (by design), SD ≈ 0.56
- **Normal Distributions**: All variables follow realistic distributions
- **No Missing Data**: Complete dataset ready for analysis
- **Range Validation**: All variables within expected ranges

## Files Included

### Core Dataset
- `banking_security_dataset.csv`: Main dataset (2,000 × 24 variables)

### Analysis Tools
- `generate_banking_security_dataset.py`: Dataset generation script
- `analyze_dataset.py`: Comprehensive analysis script
- `scenario_quiz_generator.py`: Generates the objective behavioral measure

### Supporting Materials
- `banking_security_quiz_scenarios.json`: 10 scenario-based quiz questions
- `banking_security_quiz_instructions.json`: Quiz instructions and scoring
- `banking_security_quiz_readable.txt`: Human-readable quiz format

## Usage Instructions

### 1. Load the Dataset
```python
import pandas as pd
df = pd.read_csv('banking_security_dataset.csv')
```

### 2. Run Basic Analysis
```python
python3 analyze_dataset.py
```

### 3. Key Analysis Examples

#### Intention-Behavior Gap Analysis
```python
# Gap statistics
print(df['intention_behavior_gap'].describe())

# Categorize participants
gap_quartiles = np.percentile(df['intention_behavior_gap'], [25, 50, 75])
df['gap_category'] = pd.cut(df['intention_behavior_gap'], 
                           bins=[-np.inf, gap_quartiles[0], gap_quartiles[1], gap_quartiles[2], np.inf],
                           labels=['Underperformer', 'Slight Underperformer', 'Slight Overperformer', 'Overperformer'])
```

#### PBC Moderation Analysis
```python
from sklearn.linear_model import LinearRegression

# Prepare data for moderation analysis
X = df[['intention', 'pbc']].copy()
X['intention_pbc_interaction'] = X['intention'] * X['pbc']
y = df[['SRB1_check_statements', 'SRB2_unique_passwords', 'SRB3_two_factor', 
        'SRB4_logout', 'SRB5_verify_alerts']].mean(axis=1)

# Fit moderation model
model = LinearRegression()
model.fit(X, y)
print(f"R²: {model.score(X, y):.3f}")
print(f"Intention × PBC interaction: {model.coef_[2]:.3f}")
```

## Theoretical Foundation

### Theory of Planned Behavior (TPB)
- **Intention**: Measured at T1
- **Attitude**: Measured at T1
- **Subjective Norm**: Measured at T1
- **Perceived Behavioral Control**: Measured at T1 (key moderator)

### Intention-Behavior Gap Theory
- **Gap Measurement**: Residual from intention-behavior regression
- **PBC as Moderator**: Higher PBC should reduce the gap
- **Multi-method Validation**: Self-report + objective measures

## Citation

If you use this dataset in your research, please cite:

```
Banking Security Behavior Dataset (2024)
Generated for studying intention-behavior gap in banking security practices
Sample: N=2,000, Variables: 24, Time points: 2
```

## Contact

For questions about this dataset or the generation methodology, please refer to the analysis scripts and documentation provided.

---

**Note**: This dataset was generated using realistic statistical relationships and demographic distributions. It is designed for research purposes and should be used in conjunction with appropriate statistical methods for your specific research questions.