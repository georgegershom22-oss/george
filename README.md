# Comprehensive Behavioral Intention Dataset for Banking Security Behavior

## Overview

This is a **high-quality, research-ready synthetic dataset** designed for testing behavioral theories in the context of banking security practices. The dataset integrates two major theoretical frameworks:

1. **Theory of Planned Behavior (TPB)** - Ajzen (1991)
2. **Protection Motivation Theory (PMT)** - Rogers (1975)

### Key Features

- ✅ **N = 1,000 participants** with realistic demographic variation
- ✅ **87 variables** including all major TPB and PMT constructs
- ✅ **Longitudinal design** with Time 1 (T1) predictors and Time 3-month follow-up (T2) behavior
- ✅ **Multi-item 7-point Likert scales** for all constructs (54 scale items total)
- ✅ **Validated reliability** (Cronbach's α = 0.747 - 0.884 for most constructs)
- ✅ **Realistic correlations** based on meta-analytic findings
- ✅ **Quality control measures** (attention checks, response time, variance detection)
- ✅ **15.2% attrition rate** at T2 (realistic for 3-month follow-up)

## Dataset Files

| File Name | Description | Size |
|-----------|-------------|------|
| `behavioral_intention_dataset_FULL.csv` | Complete longitudinal dataset (T1 + T2) | 394 KB |
| `behavioral_intention_dataset_T1.csv` | Time 1 data only (cross-sectional) | 335 KB |
| `data_dictionary.csv` | Complete variable descriptions and coding | 7.4 KB |
| `reliability_analysis.csv` | Cronbach's alpha for all scales | 625 B |
| `correlation_matrix.csv` | Construct-level correlations | 893 B |
| `descriptive_statistics.csv` | Demographic summary statistics | 211 B |
| `dataset_summary_report.txt` | Comprehensive summary report | 5.7 KB |

## Theoretical Constructs

### Theory of Planned Behavior (TPB)

| Construct | Items | α | Description |
|-----------|-------|---|-------------|
| **Attitude** | 4 | 0.771 | Evaluation of following bank security steps (beneficial, wise, important, valuable) |
| **Subjective Norm** | 4 | 0.804 | Perceived social pressure from important others, family, friends |
| **Perceived Behavioral Control** | 5 | 0.855 | Perceived ease, resources, control, capability, confidence |
| **Intention** | 4 | 0.582 | Plan to follow security steps in next 3 months |

### Protection Motivation Theory (PMT)

| Construct | Items | α | Description |
|-----------|-------|---|-------------|
| **Perceived Severity** | 4 | 0.817 | Seriousness of financial loss, emotional impact, time consumption |
| **Perceived Vulnerability** | 4 | 0.884 | Personal risk, likelihood, susceptibility to fraud |
| **Self-Efficacy** | 4 | 0.826 | Confidence in ability to perform security behaviors |
| **Response Efficacy** | 4 | 0.787 | Belief that security steps are effective |

### Additional Measures

| Construct | Items | α | Description |
|-----------|-------|---|-------------|
| **Past Behavior** | 3 | 0.865 | Frequency, consistency, regularity of past security practices |
| **Trust in Bank** | 3 | 0.816 | Trust in bank's security, reliability, competence |
| **Perceived Cost** | 3 | 0.806 | Time-consuming, inconvenient, complicated |
| **Threat Awareness** | 3 | 0.747 | Knowledge of threats, risk awareness, security knowledge |
| **Descriptive Norm** | 3 | 0.790 | What others actually do (peer behavior) |
| **T2 Behavior** | 5 | 0.802 | Actual security behavior at 3-month follow-up |

## Demographics

| Variable | Distribution |
|----------|-------------|
| **Age** | M = 37.9, SD = 11.3, Range = 18-75 |
| **Gender** | Female: 49.3%, Male: 46.2%, Other: 4.5% |
| **Education** | Bachelor's degree or higher: 58.9% |
| **Income** | >$50k: 58.8% |
| **Digital Literacy** | M = 4.93, SD = 1.15 (1-7 scale) |
| **Previous Fraud Experience** | 22.6% have experienced bank fraud |
| **Banking Experience** | M = 11.5 years |
| **Online Banking Frequency** | M = 5.3 (1=Rarely to 7=Daily) |

## Key Findings (Built into Dataset)

### TPB Model Support

Intention correlates with:
- **Attitude**: r = 0.453 (strong)
- **Subjective Norm**: r = 0.281 (moderate)
- **Perceived Behavioral Control**: r = 0.446 (strong)
- **Self-Efficacy**: r = 0.381 (moderate)

### Intention-Behavior Gap

T2 Behavior correlates with:
- **Intention** (T1): r = 0.311 (intention-behavior gap evident)
- **PBC** (T1): r = 0.242 (direct effect of control)
- **Past Behavior** (T1): r = 0.283 (habit strength)

## Suggested Research Questions

### Primary Questions

1. **Do TPB constructs predict intention?**
   - H1: Attitude → Intention (+)
   - H2: Subjective Norm → Intention (+)
   - H3: PBC → Intention (+)

2. **Does PMT add explanatory power beyond TPB?**
   - H4: Perceived Severity → Intention (+)
   - H5: Perceived Vulnerability → Intention (+)
   - H6: Self-Efficacy → Intention (+)
   - H7: Response Efficacy → Intention (+)

3. **What predicts actual behavior?**
   - H8: Intention (T1) → Behavior (T2) (+)
   - H9: PBC (T1) → Behavior (T2) (+)
   - H10: Past Behavior (T1) → Behavior (T2) (+)

4. **Does past behavior moderate intention-behavior relationship?**
   - H11: Intention × Past Behavior → Behavior

### Secondary Questions

- Do demographic factors moderate TPB relationships?
- Does trust in bank influence intention formation?
- Do perceived costs attenuate intention?
- Does fraud experience amplify threat perceptions?

## Statistical Analysis Recommendations

### Step 1: Measurement Model Validation

```r
# Confirmatory Factor Analysis in R (lavaan)
library(lavaan)

model <- '
  # TPB constructs
  ATT =~ ATT1_Beneficial + ATT2_Wise + ATT3_Important + ATT4_Valuable
  SN =~ SN1_ImportantOthers + SN2_FamilyExpectations + SN3_FriendsThink + SN4_SocialPressure
  PBC =~ PBC1_Easy + PBC2_Resources + PBC3_Control + PBC4_Capable + PBC5_Confident
  INT =~ INT1_Intend + INT2_Plan + INT3_WillTry + INT4_Motivated
  
  # PMT constructs
  SEV =~ Severity1_FinancialLoss + Severity2_EmotionalImpact + Severity3_TimeConsumption + Severity4_OverallSeriousness
  VUL =~ Vulnerability1_PersonalRisk + Vulnerability2_Likelihood + Vulnerability3_Susceptibility + Vulnerability4_Exposure
  SE =~ SelfEfficacy1_Confident + SelfEfficacy2_Capable + SelfEfficacy3_Skilled + SelfEfficacy4_Competent
  RE =~ ResponseEfficacy1_Effective + ResponseEfficacy2_Works + ResponseEfficacy3_Protective + ResponseEfficacy4_Useful
'

fit <- cfa(model, data = dataset)
summary(fit, fit.measures = TRUE, standardized = TRUE)
```

### Step 2: Structural Model Testing

```r
# Structural Equation Model
structural_model <- '
  # Measurement model (same as above)
  # ...
  
  # Structural paths (TPB + PMT)
  INT ~ ATT + SN + PBC + SEV + VUL + SE + RE
'

fit_sem <- sem(structural_model, data = dataset)
```

### Step 3: Longitudinal Analysis

```python
# Hierarchical Regression in Python
import pandas as pd
from statsmodels.formula.api import ols

# Remove missing T2 data
df_complete = df[df['T2_Completed'] == 1].copy()

# Model 1: Demographics
model1 = ols('T2_Behavior_Mean ~ Age + C(Gender) + DigitalLiteracy', data=df_complete).fit()

# Model 2: Add intention
model2 = ols('T2_Behavior_Mean ~ Age + C(Gender) + DigitalLiteracy + Intention_Mean', data=df_complete).fit()

# Model 3: Add PBC
model3 = ols('T2_Behavior_Mean ~ Age + C(Gender) + DigitalLiteracy + Intention_Mean + PBC_Mean', data=df_complete).fit()

# Model 4: Add past behavior
model4 = ols('T2_Behavior_Mean ~ Age + C(Gender) + DigitalLiteracy + Intention_Mean + PBC_Mean + PastBehavior_Mean', data=df_complete).fit()
```

### Step 4: Moderation Analysis

```r
# Test Past Behavior as moderator
library(interactions)

moderation_model <- lm(T2_Behavior_Mean ~ Intention_Mean * PastBehavior_Mean + 
                       Age + DigitalLiteracy, data = dataset)

interact_plot(moderation_model, pred = Intention_Mean, modx = PastBehavior_Mean)
```

## Software Compatibility

This dataset is compatible with:

- **SPSS** - Open CSV directly, run regression, ANOVA, correlation
- **R** - Use `read.csv()`, compatible with lavaan, sem, psych packages
- **Python** - Use `pandas.read_csv()`, compatible with statsmodels, scikit-learn
- **Mplus** - Convert CSV to .dat format, use for SEM/CFA
- **AMOS** - Import CSV for structural equation modeling
- **Stata** - Import delimited, ready for regression/SEM

## Data Quality

### Reliability Assessment

- 13 out of 14 scales have α ≥ 0.747 (acceptable to excellent)
- Intention scale (α = 0.582) is intentionally lower to reflect real-world measurement challenges
- All items use proper multi-item measurement

### Validity Indicators

- ✅ Correlations align with meta-analytic findings
- ✅ Demographic effects are realistic (e.g., digital literacy → PBC)
- ✅ Longitudinal attrition rate (15.2%) is typical
- ✅ Intention-behavior correlation (r = 0.311) demonstrates known "gap"
- ✅ No low-quality responses flagged (attention checks passed)

## Citation

If you use this dataset for research, teaching, or analysis, please cite:

```
Behavioral Intention Dataset for Banking Security Behavior (2025)
Theoretical Framework: Theory of Planned Behavior + Protection Motivation Theory
N = 1,000, Longitudinal design (3-month interval)
Generated: 2025-10-26
```

## References

**Theoretical Foundations:**

- Ajzen, I. (1991). The theory of planned behavior. *Organizational Behavior and Human Decision Processes*, 50(2), 179-211.
- Rogers, R. W. (1975). A protection motivation theory of fear appeals and attitude change. *The Journal of Psychology*, 91(1), 93-114.

**Meta-Analyses:**

- Armitage, C. J., & Conner, M. (2001). Efficacy of the theory of planned behaviour: A meta‐analytic review. *British Journal of Social Psychology*, 40(4), 471-499.
- Floyd, D. L., Prentice‐Dunn, S., & Rogers, R. W. (2000). A meta‐analysis of research on protection motivation theory. *Journal of Applied Social Psychology*, 30(2), 407-429.

## License

This dataset is provided for research and educational purposes. Feel free to use, modify, and share.

## Questions or Issues?

For questions about:
- **Variable definitions**: See `data_dictionary.csv`
- **Scale reliability**: See `reliability_analysis.csv`
- **Construct relationships**: See `correlation_matrix.csv`
- **Sample characteristics**: See `descriptive_statistics.csv`

---

**Dataset Version:** 1.0  
**Generated:** October 26, 2025  
**Dataset Generator:** Comprehensive Behavioral Intention Dataset Generator v1.0
