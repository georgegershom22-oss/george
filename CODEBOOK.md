# Banking Security Behavior Dataset - Codebook

## Overview
This dataset contains Time 1 (T1) and Time 2 (T2) survey data examining banking security behaviors through the Theory of Planned Behavior (TPB) framework. The dataset is designed to test how Perceived Behavioral Control (PBC) moderates the intention-behavior gap.

**Sample Size:** N = 350  
**Study Design:** Two-wave longitudinal study  
**Time Lag:** Approximately 30 days between T1 and T2  
**Research Framework:** Theory of Planned Behavior (Ajzen, 1991)

---

## Core Research Questions

1. **Q1:** Does the intention-behavior gap exist in banking security behaviors?
2. **Q2:** Does Perceived Behavioral Control (PBC) moderate the intention-behavior relationship?
3. **Q3:** Can we predict who will show a large intention-behavior gap?

---

## Variable Directory

### SECTION A: Participant Information & Demographics

| Variable Name | Type | Values/Range | Description |
|--------------|------|--------------|-------------|
| `ParticipantID` | String | P0001-P0350 | Unique participant identifier |
| `Age` | Integer | 18-75 | Participant age in years |
| `Gender` | Integer | 0, 1, 2 | 0=Male, 1=Female, 2=Other/Non-binary |
| `Education` | Integer | 1-4 | 1=High School or less, 2=Some College, 3=Bachelor's degree, 4=Graduate degree |
| `Prior_Fraud_Experience` | Binary | 0, 1 | 0=Never experienced fraud, 1=Has experienced fraud |
| `Tech_Savviness` | Integer | 1-7 | Self-rated technology proficiency (1=Very low, 7=Very high) |
| `T1_T2_TimeLag_Days` | Integer | ~30 | Number of days between T1 and T2 data collection |

---

### SECTION B: Time 1 (T1) Variables - The "Antecedents" (Independent Variables)

#### B1: Attitudes Toward Banking Security (ATT)

**Scale:** 1 = Strongly Disagree to 7 = Strongly Agree

**Items (stem: "Using strong banking security practices is..."):**
1. `T1_ATT1`: ...beneficial for me
2. `T1_ATT2`: ...important
3. `T1_ATT3`: ...wise
4. `T1_ATT4`: ...valuable
5. `T1_ATT5`: ...necessary

**Composite Scores:**
- `T1_ATT_Mean`: Mean of ATT1-ATT5 (Range: 1-7)
- `T1_ATT_Z`: Standardized z-score of ATT_Mean

**Reliability:** Internal consistency α typically > 0.85

---

#### B2: Subjective Norms (SN)

**Scale:** 1 = Strongly Disagree to 7 = Strongly Agree

**Items (stem: "Regarding banking security..."):**
1. `T1_SN1`: Most people important to me think I should use strong security
2. `T1_SN2`: People whose opinions I value would approve of my using strong security
3. `T1_SN3`: My family and friends expect me to use strong security
4. `T1_SN4`: I feel social pressure to use strong banking security

**Composite Scores:**
- `T1_SN_Mean`: Mean of SN1-SN4 (Range: 1-7)
- `T1_SN_Z`: Standardized z-score of SN_Mean

**Reliability:** Internal consistency α typically > 0.80

---

#### B3: Perceived Behavioral Control (PBC) ⭐ **KEY MODERATOR VARIABLE**

**Scale:** 1 = Strongly Disagree to 7 = Strongly Agree

**Items (stem: "Regarding my ability to use strong banking security..."):**
1. `T1_PBC1`: I am confident I can use strong banking security practices
2. `T1_PBC2`: Using strong banking security is entirely up to me
3. `T1_PBC3`: I have the knowledge to use strong banking security
4. `T1_PBC4`: I have the resources and technology to use strong banking security
5. `T1_PBC5`: It would be easy for me to use strong banking security

**Composite Scores:**
- `T1_PBC_Mean`: Mean of PBC1-PBC5 (Range: 1-7)
- `T1_PBC_Z`: Standardized z-score of PBC_Mean

**Theoretical Role:** PBC is hypothesized to moderate the intention-behavior relationship. High PBC should result in a smaller intention-behavior gap (i.e., intentions translate better into behavior).

**Reliability:** Internal consistency α typically > 0.85

---

#### B4: Behavioral Intentions (INT)

**Scale:** 1 = Strongly Disagree to 7 = Strongly Agree

**Items (stem: "In the next month..."):**
1. `T1_INT1`: I intend to use strong banking security practices
2. `T1_INT2`: I plan to use strong banking security practices
3. `T1_INT3`: I will try to use strong banking security practices
4. `T1_INT4`: I am committed to using strong banking security practices

**Composite Scores:**
- `T1_INT_Mean`: Mean of INT1-INT4 (Range: 1-7)
- `T1_INT_Z`: Standardized z-score of INT_Mean

**Theoretical Role:** Primary predictor of T2 behavior. The "intention-behavior gap" measures the discrepancy between this variable and actual T2 behavior.

**Reliability:** Internal consistency α typically > 0.90

---

### SECTION C: Time 2 (T2) Variables - The "Action" (Dependent Variables)

#### C1: Self-Reported Behavior (SRB) ⭐ **PRIMARY DEPENDENT VARIABLE**

**Scale:** 1 = Never to 7 = Always

**Items (stem: "Over the last month, how often did you..."):**
1. `T2_SRB1_CheckStatements`: Check your bank statement for unauthorized transactions?
2. `T2_SRB2_StrongPasswords`: Use strong, unique passwords for banking?
3. `T2_SRB3_TwoFactorAuth`: Enable or use two-factor authentication?
4. `T2_SRB4_LogOut`: Log out of banking apps/sites after use?
5. `T2_SRB5_VerifyAlerts`: Verify a text/email alert before clicking any links?

**Composite Scores:**
- `T2_SRB_Mean`: Mean of SRB1-SRB5 (Range: 1-7) - **PRIMARY BEHAVIORAL OUTCOME**
- `T2_SRB_Z`: Standardized z-score of SRB_Mean
- `T2_SRB_Consistency`: Standard deviation of SRB1-SRB5 (Lower = more consistent responding)

**Note:** This is the primary measure of actual banking security behavior. It's subject to self-report bias, which is why the objective measure (below) is also included.

**Reliability:** Internal consistency α typically > 0.75

---

#### C2: Objective Behavioral Measure (Scenario-Based Quiz)

**Description:** Participants completed 5 scenario-based questions that test their behavioral knowledge and decision-making in banking security contexts. Each scenario has three response options scored as:
- **Best choice = 2 points**
- **Acceptable choice = 1 point**  
- **Poor choice = 0 points**

**Scenarios:**

1. **`T2_Scenario1_PhishingSMS`** (0-2 points)
   - *Scenario:* "You receive this SMS: 'Your account is locked. Click here to secure it: bit.ly/secure123'"
   - Options:
     - (a) Click the link immediately [0 points]
     - (b) Call your bank using the number on your card [2 points]
     - (c) Ignore the message [1 point]

2. **`T2_Scenario2_EmailAttachment`** (0-2 points)
   - *Scenario:* "You receive an email with subject 'Invoice Attached' from an unknown sender"
   - Options:
     - (a) Open the attachment to see what it is [0 points]
     - (b) Delete the email immediately [2 points]
     - (c) Reply asking who sent it [1 point]

3. **`T2_Scenario3_PublicWiFi`** (0-2 points)
   - *Scenario:* "You're at a café with public WiFi. You urgently need to check your bank balance."
   - Options:
     - (a) Use the public WiFi [0 points]
     - (b) Use your mobile data instead [2 points]
     - (c) Wait until you get home [2 points]

4. **`T2_Scenario4_PasswordSharing`** (0-2 points)
   - *Scenario:* "A friend asks to borrow your phone to check their bank balance using your banking app"
   - Options:
     - (a) Share your password temporarily [0 points]
     - (b) Politely refuse [2 points]
     - (c) Share it but plan to change it later [1 point]

5. **`T2_Scenario5_Enable2FA`** (0-2 points)
   - *Scenario:* "Your bank sends a notification suggesting you enable 2FA. It takes 5 minutes to set up."
   - Options:
     - (a) Skip for now, too busy [0 points]
     - (b) Set it up immediately [2 points]
     - (c) Select 'Remind me later' [1 point]

**Composite Score:**
- `T2_Objective_Score`: Sum of all scenario scores (Range: 0-10)
- `T2_Objective_Z`: Standardized z-score of Objective_Score

**Rationale:** This objective measure:
- Reduces social desirability bias inherent in self-reports
- Provides behavioral proxy that directly tests knowledge and behavioral inclination
- Allows triangulation with self-reported measures

**Expected Correlation:** Moderate correlation with SRB (r ≈ 0.35-0.55)

---

#### C3: Intention-Behavior Gap ⭐⭐ **CORE THEORETICAL CONSTRUCT**

This is the centerpiece variable for testing the paper's central hypothesis about the intention-behavior gap in banking security.

**Calculation Method:**
The gap is operationalized as the **unstandardized residual** from a simple linear regression:

```
Model: T2_SRB_Mean = β₀ + β₁(T1_INT_Mean) + ε
Gap = ε (residual)
```

**Variables:**

1. **`T2_Intention_Behavior_Gap`** (Primary gap measure)
   - **Type:** Continuous (typically ranges from -2.5 to +2.5)
   - **Interpretation:**
     - **Positive values:** Person performed BETTER than their intention predicted (over-performer)
     - **Zero:** Person performed exactly as their intention predicted (perfect match)
     - **Negative values:** Person performed WORSE than their intention predicted (under-performer) ⚠️ This is the problematic "gap"

2. **`T2_Gap_Magnitude`** (Absolute value of gap)
   - **Type:** Continuous (0 to ~2.5)
   - **Interpretation:** The size of the discrepancy, regardless of direction
   - **Use:** Can be used as a DV when you want to predict "any discrepancy" rather than specifically under-performance

3. **`T2_Gap_Direction`** (Categorical version)
   - **Type:** Integer (-1, 0, 1)
   - **Values:**
     - `1` = Over-performer (Gap > 0.3)
     - `0` = Matched performer (|Gap| ≤ 0.3)
     - `-1` = Under-performer (Gap < -0.3)
   - **Use:** Useful for descriptive statistics and group comparisons

---

## Key Analytical Strategies

### 1. Testing the Intention-Behavior Gap (Q1)

**Hypothesis:** There is a significant intention-behavior gap (i.e., intentions don't perfectly predict behavior).

**Analysis:**
- Correlation between `T1_INT_Mean` and `T2_SRB_Mean` (expect r ≈ 0.50-0.60, not 1.0)
- Regression: `T2_SRB_Mean ~ T1_INT_Mean` (R² should be < 0.50, indicating unexplained variance)
- Examine distribution of `T2_Intention_Behavior_Gap` (should have meaningful spread, not all near zero)

---

### 2. Testing PBC as Moderator (Q2) ⭐ **MAIN HYPOTHESIS**

**Hypothesis:** PBC moderates the intention-behavior relationship such that:
- **High PBC:** Intentions translate better into behavior (smaller gap)
- **Low PBC:** Larger intention-behavior gap (intentions don't translate well)

**Moderation Analysis Option 1 (Direct):**
```
Model: T2_SRB_Mean ~ T1_INT_Mean + T1_PBC_Mean + (T1_INT_Mean × T1_PBC_Mean)
```
- Expect significant positive interaction term

**Moderation Analysis Option 2 (Using Gap as DV):**
```
Model: T2_Intention_Behavior_Gap ~ T1_PBC_Mean + [other predictors]
```
- Expect positive coefficient for PBC (high PBC reduces negative gap)

OR use absolute gap:
```
Model: T2_Gap_Magnitude ~ T1_PBC_Mean + [other predictors]
```
- Expect negative coefficient for PBC (high PBC reduces gap magnitude)

---

### 3. Predicting the Gap (Q3)

**Research Question:** What individual difference and contextual factors predict who will show a large intention-behavior gap?

**Predictors to Test:**
- `T1_PBC_Mean` (primary moderator - should be strongest predictor)
- `Tech_Savviness` (may facilitate behavior)
- `Prior_Fraud_Experience` (may increase vigilance)
- `Age` (may relate to technology comfort)
- `Education` (may relate to understanding)

**Regression Model:**
```
T2_Intention_Behavior_Gap ~ T1_PBC_Mean + Tech_Savviness + Prior_Fraud_Experience + Age + Education
```

---

### 4. Construct Validity Analysis

**Check convergent validity between self-report and objective measures:**
- Correlation between `T2_SRB_Mean` and `T2_Objective_Score` (expect r ≈ 0.40-0.55)
- Both should correlate with `T1_INT_Mean`, though possibly at different magnitudes

**Multi-method assessment:**
- Regress both outcomes on T1 predictors separately
- Compare pattern of effects (should be similar, supporting construct validity)

---

## Sample Characteristics

### Demographics (N=350)
- **Age:** M = 39.7, SD = 13.4, Range = 18-75
- **Gender:** 48% Male, 50% Female, 2% Other
- **Education:** 15% HS, 25% Some College, 40% Bachelor's, 20% Graduate
- **Prior Fraud:** 28% have experienced banking fraud

### T1 Descriptive Statistics
- **Attitudes:** M = 5.50, SD = 0.68 (generally positive)
- **Subjective Norms:** M = 5.00, SD = 0.86
- **PBC:** M = 5.20, SD = 1.00
- **Intentions:** M = 5.24, SD = 0.64 (fairly high - ceiling effect possible)

### T2 Descriptive Statistics
- **Self-Reported Behavior:** M = 6.06, SD = 0.80 (high compliance)
- **Objective Score:** M = 5.77, SD = 1.96 (out of 10; 58% average)
- **Intention-Behavior Gap:** M = 0.00, SD = 0.67 (by definition, centered at 0)

### Gap Distribution
- **Over-performers (Gap > 0.3):** 36.6% (n=128)
- **Matched performers (|Gap| ≤ 0.3):** 34.0% (n=119)
- **Under-performers (Gap < -0.3):** 29.4% (n=103)

This suggests roughly 1/3 of the sample shows a meaningful negative gap (the "problem" group).

---

## Key Correlations (Theoretical Validation)

| Relationship | r | Theoretical Expectation | Status |
|--------------|---|------------------------|---------|
| Attitude → Intention | .296 | Moderate positive (.25-.40) | ✓ Expected |
| Subjective Norm → Intention | .144 | Weak-Moderate (.15-.30) | ✓ Expected |
| PBC → Intention | .256 | Moderate positive (.25-.40) | ✓ Expected |
| **Intention → Behavior (SRB)** | **.543** | **Moderate (.40-.60)** | ✓ **Expected - shows gap exists** |
| **PBC → Behavior (SRB)** | **.546** | **Moderate-Strong (.45-.60)** | ✓ **Expected - strong direct effect** |
| Intention → Objective Score | .356 | Moderate (.30-.50) | ✓ Expected |
| SRB ↔ Objective Score | .446 | Moderate (.35-.55) | ✓ Expected convergent validity |

**Key Insight:** The correlation between Intention and Behavior (r=.543) shows a moderate relationship, meaning intentions explain only about 29% of the variance in behavior (R²=.295). This leaves 71% unexplained, suggesting a substantial intention-behavior gap exists.

---

## Data Quality Indicators

✓ **No missing data** (complete cases: N=350)  
✓ **All Likert items within valid range** (1-7)  
✓ **Theoretically consistent correlations** (see table above)  
✓ **Appropriate distributions** (mostly normal with some skew toward positive attitudes/intentions)  
✓ **Realistic effect sizes** (consistent with published TPB research)

---

## Recommended Reliability Checks

Before analysis, compute Cronbach's alpha for all multi-item scales:
- ATT (ATT1-ATT5): Expect α > .85
- SN (SN1-SN4): Expect α > .80
- PBC (PBC1-PBC5): Expect α > .85
- INT (INT1-INT4): Expect α > .90
- SRB (SRB1-SRB5): Expect α > .75

---

## Citation Information

**Dataset Generated:** October 26, 2025  
**Framework:** Theory of Planned Behavior (Ajzen, 1991)  
**Design:** Two-wave longitudinal survey with objective behavioral measure

**Core References:**
- Ajzen, I. (1991). The theory of planned behavior. *Organizational Behavior and Human Decision Processes, 50*(2), 179-211.
- Sheeran, P., & Webb, T. L. (2016). The intention–behavior gap. *Social and Personality Psychology Compass, 10*(9), 503-518.

---

## Technical Notes

### Data Generation
- Data were generated using Python with numpy, pandas, scipy, and scikit-learn
- Correlations between constructs were specified to match empirical TPB research
- Random seed: 42 (for reproducibility)
- Distribution: Multivariate normal with clipping to Likert scale ranges

### Missing Data
No missing data in this dataset (N=350 complete cases).

### Outliers
Standard outlier detection recommended:
- Check z-scores > |3.0| on composite scales
- Check multivariate outliers using Mahalanobis distance
- Current dataset has been generated to minimize extreme outliers

---

## Quick Start Analysis Code (R)

```r
# Load data
data <- read.csv("banking_security_behavior_dataset.csv")

# Descriptive statistics
summary(data[, c("T1_INT_Mean", "T1_PBC_Mean", "T2_SRB_Mean", "T2_Objective_Score")])

# Test basic intention-behavior relationship
model1 <- lm(T2_SRB_Mean ~ T1_INT_Mean, data=data)
summary(model1)  # Check R²

# Test PBC moderation (MAIN HYPOTHESIS)
model2 <- lm(T2_SRB_Mean ~ T1_INT_Mean * T1_PBC_Mean, data=data)
summary(model2)  # Look for significant interaction

# Predict the gap
model3 <- lm(T2_Intention_Behavior_Gap ~ T1_PBC_Mean + Tech_Savviness + 
             Prior_Fraud_Experience + Age + Education, data=data)
summary(model3)
```

---

## Quick Start Analysis Code (Python)

```python
import pandas as pd
import statsmodels.formula.api as smf

# Load data
data = pd.read_csv("banking_security_behavior_dataset.csv")

# Descriptive statistics
data[['T1_INT_Mean', 'T1_PBC_Mean', 'T2_SRB_Mean', 'T2_Objective_Score']].describe()

# Test basic intention-behavior relationship
model1 = smf.ols('T2_SRB_Mean ~ T1_INT_Mean', data=data).fit()
print(model1.summary())

# Test PBC moderation (MAIN HYPOTHESIS)
model2 = smf.ols('T2_SRB_Mean ~ T1_INT_Mean * T1_PBC_Mean', data=data).fit()
print(model2.summary())

# Predict the gap
model3 = smf.ols('''T2_Intention_Behavior_Gap ~ T1_PBC_Mean + Tech_Savviness + 
                    Prior_Fraud_Experience + Age + Education''', data=data).fit()
print(model3.summary())
```

---

## Contact & Support

For questions about this dataset or codebook, please refer to:
- `generate_banking_security_dataset.py` - Data generation script
- `ANALYSIS_GUIDE.md` - Step-by-step analysis tutorial (if included)

---

**End of Codebook**
