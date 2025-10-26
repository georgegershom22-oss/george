# Banking Security Behavior Dataset

## 🎯 Overview

This repository contains a comprehensive dataset examining **banking security behaviors** through the lens of the **Theory of Planned Behavior (TPB)**. The dataset is specifically designed to investigate the **intention-behavior gap** and test whether **Perceived Behavioral Control (PBC)** moderates the relationship between intentions and actual security behaviors.

**Dataset Size:** N = 350 participants  
**Design:** Two-wave longitudinal study (Time 1 → Time 2, ~30 days apart)  
**Framework:** Theory of Planned Behavior (Ajzen, 1991)

---

## 📊 What's Included

### Core Dataset
- **`banking_security_behavior_dataset.csv`** - Main dataset (350 rows × 71 columns)
  - Time 1 (T1): Attitudes, Subjective Norms, PBC, Intentions
  - Time 2 (T2): Self-reported behaviors, Objective behavioral measures, Behavioral gap

### Documentation
- **`CODEBOOK.md`** - Complete variable descriptions, scales, and analysis guidance
- **`README.md`** - This file (quick start guide)

### Scripts
- **`generate_banking_security_dataset.py`** - Data generation script (reproducible with seed=42)
- **`example_analysis.py`** - Comprehensive analysis examples in Python

---

## 🚀 Quick Start

### 1. Load the Dataset

**Python:**
```python
import pandas as pd
data = pd.read_csv('banking_security_behavior_dataset.csv')
print(data.head())
```

**R:**
```r
data <- read.csv('banking_security_behavior_dataset.csv')
head(data)
```

### 2. Run Example Analysis

```bash
python3 example_analysis.py
```

This script will:
- ✓ Load and describe the dataset
- ✓ Calculate reliability (Cronbach's α)
- ✓ Test the intention-behavior gap
- ✓ Test PBC moderation (main hypothesis)
- ✓ Predict who shows the largest gaps
- ✓ Provide actionable insights

---

## 🧪 Key Research Questions

### Q1: Does the intention-behavior gap exist?
**Hypothesis:** People's intentions don't perfectly predict their actual behavior.

**Test:** Regress T2 behavior on T1 intentions. If R² < 0.50, a substantial gap exists.

**Expected Result:** Intentions explain ~30-40% of behavior variance, leaving a 60-70% "gap."

---

### Q2: Does PBC moderate the intention-behavior relationship? ⭐ MAIN HYPOTHESIS
**Hypothesis:** People with high PBC (confidence/control) translate intentions into behavior more effectively than those with low PBC.

**Test:** Moderation analysis with interaction term `Intention × PBC`

**Expected Result:** Significant positive interaction—high PBC reduces the intention-behavior gap.

---

### Q3: What predicts the behavioral gap?
**Hypothesis:** Individual differences (PBC, tech savviness, prior fraud experience) predict who shows a large gap.

**Test:** Regression with gap as DV and individual difference variables as predictors.

**Expected Result:** PBC is the strongest predictor of gap size.

---

## 📈 Key Variables

### Time 1 (T1) - Predictors
| Variable | Description | Scale |
|----------|-------------|-------|
| `T1_ATT_Mean` | Attitudes toward banking security | 1-7 (Disagree-Agree) |
| `T1_SN_Mean` | Subjective norms (social pressure) | 1-7 (Disagree-Agree) |
| **`T1_PBC_Mean`** | **Perceived Behavioral Control** ⭐ | 1-7 (Low-High control) |
| `T1_INT_Mean` | Behavioral intentions | 1-7 (Disagree-Agree) |

### Time 2 (T2) - Outcomes
| Variable | Description | Scale |
|----------|-------------|-------|
| **`T2_SRB_Mean`** | **Self-reported behavior** (primary DV) | 1-7 (Never-Always) |
| `T2_Objective_Score` | Scenario-based quiz score | 0-10 (sum of 5 scenarios) |
| **`T2_Intention_Behavior_Gap`** | **Residual from INT→SRB regression** ⭐ | Continuous (~-2.5 to +2.5) |
| `T2_Gap_Direction` | Categorical gap classification | -1 (under), 0 (matched), 1 (over) |

---

## 🎓 Theoretical Framework

This dataset operationalizes the **Theory of Planned Behavior (TPB)**:

```
Time 1 (T1)                           Time 2 (T2)
┌─────────────┐                       ┌─────────────┐
│  Attitudes  │──┐                    │             │
└─────────────┘  │                    │             │
                 ├──→ ┌────────────┐  │   Actual    │
┌─────────────┐  │    │ Intentions │─→│  Behavior   │
│ Subj. Norms │──┘    └────────────┘  │             │
└─────────────┘            ↑          │             │
                           │          └─────────────┘
┌─────────────┐            │
│     PBC     │────────────┴────────────→ [Direct Effect]
│ (Moderator) │
└─────────────┘
       │
       └─────────────→ [Moderates INT→Behavior]
```

**Key Insight:** The "gap" between intentions and behavior should be SMALLER when PBC is HIGH.

---

## 📋 Sample Characteristics

### Demographics
- **Age:** M = 39.7 years (SD = 13.4), Range = 18-75
- **Gender:** 48% Male, 50% Female, 2% Other
- **Education:** 40% Bachelor's, 20% Graduate degree
- **Prior Fraud:** 28% have experienced banking fraud

### Behavioral Gap Distribution
- **29.4%** Under-performers (Gap < -0.3) ⚠️ Problem group
- **34.0%** Matched performers (|Gap| ≤ 0.3) ✓
- **36.6%** Over-performers (Gap > 0.3) ✓✓

---

## 🔬 Data Quality

✅ **Complete data:** No missing values (N = 350)  
✅ **High reliability:** All scales α > .75 (most > .85)  
✅ **Theoretically consistent:** Correlations match TPB predictions  
✅ **Validated:** Self-report and objective measures converge (r = .45)  
✅ **Reproducible:** Generated with random seed = 42

---

## 📊 Expected Correlations

| Relationship | Expected r | Actual r | Status |
|--------------|-----------|----------|---------|
| Attitude → Intention | .25-.40 | .296 | ✓ |
| PBC → Intention | .25-.40 | .256 | ✓ |
| **Intention → Behavior** | **.40-.60** | **.543** | ✓ Shows gap |
| **PBC → Behavior** | **.45-.60** | **.546** | ✓ Direct effect |

---

## 🛠️ Analysis Tools

### Python Requirements
```bash
pip install pandas numpy scipy scikit-learn statsmodels matplotlib seaborn
```

### R Requirements
```r
install.packages(c("tidyverse", "psych", "lavaan", "interactions"))
```

---

## 📚 Key References

1. **Ajzen, I. (1991).** The theory of planned behavior. *Organizational Behavior and Human Decision Processes*, 50(2), 179-211.

2. **Sheeran, P., & Webb, T. L. (2016).** The intention–behavior gap. *Social and Personality Psychology Compass*, 10(9), 503-518.

3. **Armitage, C. J., & Conner, M. (2001).** Efficacy of the theory of planned behaviour: A meta-analytic review. *British Journal of Social Psychology*, 40(4), 471-499.

4. **Rhodes, R. E., & de Bruijn, G. J. (2013).** How big is the physical activity intention–behaviour gap? A meta-analysis using the action control framework. *British Journal of Health Psychology*, 18(2), 296-309.

---

## 🎯 Use Cases

This dataset is ideal for:

✅ Testing TPB in the banking security context  
✅ Examining intention-behavior gaps  
✅ Studying moderation effects in behavioral research  
✅ Teaching longitudinal research design  
✅ Demonstrating residual-based gap operationalization  
✅ Practicing structural equation modeling (SEM)  
✅ Multi-method behavioral assessment (self-report + objective)

---

## 📝 Citation

If you use this dataset, please cite:

```
Banking Security Behavior Dataset (2025). 
Generated using Theory of Planned Behavior framework.
N = 350, Two-wave longitudinal design.
```

---

## 📧 Questions?

For detailed variable descriptions, see **`CODEBOOK.md`**  
For analysis examples, run **`example_analysis.py`**  
For data generation details, see **`generate_banking_security_dataset.py`**

---

## ⚡ Quick Test

Want to verify the dataset works? Run this quick test:

**Python:**
```python
import pandas as pd
import statsmodels.formula.api as smf

data = pd.read_csv('banking_security_behavior_dataset.csv')

# Test main hypothesis: PBC moderates intention-behavior
model = smf.ols('T2_SRB_Mean ~ T1_INT_Mean * T1_PBC_Mean', data=data).fit()
print(model.summary())

# Look for significant interaction term (p < .05)
```

**Expected:** You should see a significant interaction between Intention and PBC!

---

## 🎉 Ready to Analyze!

Your dataset is complete and ready for analysis. Start with:

1. `example_analysis.py` - Run comprehensive analyses
2. `CODEBOOK.md` - Understand every variable
3. Your own hypotheses - This dataset supports many research questions!

**Good luck with your research!** 🚀

---

*Dataset generated: October 26, 2025*  
*Framework: Theory of Planned Behavior*  
*Design: Longitudinal (T1 → T2)*
