# Banking Fraud Study Dataset - Section A: Demographics and Control Variables (T1)

## Overview
This dataset contains comprehensive demographic and control variables for a comparative study of banking fraud intention and behavior in Nigeria and Ghana.

**Sample Size:** 1,000 participants (500 from Nigeria, 500 from Ghana)
**Collection Period:** January 2025
**Study Design:** Cross-sectional, comparative

## Files Included

1. **banking_fraud_dataset_full.csv** - Complete dataset with all variables (numeric codes and text labels)
2. **banking_fraud_dataset_full.xlsx** - Excel workbook with multiple sheets:
   - Full Dataset
   - Nigeria Only
   - Ghana Only  
   - Summary by Country
3. **banking_fraud_dataset_numeric.csv** - Numeric variables only (for statistical analysis)
4. **banking_fraud_dataset_full.json** - JSON format for programming applications
5. **data_dictionary.json** - Comprehensive variable descriptions, coding schemes, and notes
6. **summary_statistics.json** - Descriptive statistics and distributions
7. **README.md** - This file

## Variables Included

### Core Demographics
- **Country**: Nigeria (1) vs Ghana (2)
- **Age**: Continuous, 18-75 years
- **Gender**: Male (1), Female (2), Other/Prefer not to say (3)
- **Education**: 6-level ordinal scale (No formal to Postgraduate)
- **Income_Level**: 6-level ordinal scale with country-specific currency bands

### Banking Profile
- **Bank_Type**: Traditional Commercial (1), Digital-Only (2), Microfinance (3)
- **Years_with_Account**: Continuous, years of having a bank account
- **Frequency_of_Use**: 5-level ordinal scale (Daily to Less than monthly)

### Experience
- **Past_Victim**: Binary (1=Yes, 0=No) - Previous experience with bank fraud

## Key Features

### Realistic Data Quality
- All correlations are theoretically justified and realistic
- Age correlated with education and income
- Digital bank users skew younger and more educated
- Fraud victimization correlated with usage frequency and tenure
- Country differences reflected in digital banking adoption

### Statistical Considerations
- No missing data (complete cases)
- Balanced sample across countries
- Realistic distributions based on West African banking populations
- All variables ready for statistical analysis

## Recommended Analyses

1. **Descriptive Statistics**: 
   - Frequency distributions for categorical variables
   - Means and SDs for continuous variables
   - Cross-tabulations by country

2. **Comparative Analyses**:
   - Chi-square tests for categorical variables (Nigeria vs Ghana)
   - Independent t-tests for continuous variables
   - Mann-Whitney U tests for ordinal variables

3. **Correlation Analyses**:
   - Pearson correlations for continuous variables
   - Spearman correlations for ordinal variables
   - Point-biserial correlations with binary outcomes

4. **Regression Analyses**:
   - Logistic regression with Past_Victim as outcome
   - Multiple regression with demographic predictors
   - Hierarchical regression testing country differences

## Usage Example (Python)

```python
import pandas as pd

# Load full dataset
df = pd.read_csv('banking_fraud_dataset_full.csv')

# Basic exploration
print(df.info())
print(df.describe())

# Country comparison
nigeria = df[df['Country'] == 1]
ghana = df[df['Country'] == 2]

# Analyze fraud victimization
fraud_rate = df.groupby('Country_Name')['Past_Victim'].mean()
print(f"Fraud victimization rates:\n{fraud_rate}")
```

## Usage Example (R)

```r
# Load full dataset
df <- read.csv('banking_fraud_dataset_full.csv')

# Basic exploration
str(df)
summary(df)

# Country comparison
library(dplyr)
country_summary <- df %>%
  group_by(Country_Name) %>%
  summarise(
    mean_age = mean(Age),
    fraud_rate = mean(Past_Victim)
  )

# Chi-square test
chisq.test(df$Country, df$Past_Victim)
```

## Citation
If using this dataset, please cite:
- Study: "Banking Fraud Intention and Behavior: A Comparative Study of Nigeria and Ghana"
- Dataset Version: 1.0
- Generation Date: 2025-10-26

## Contact
For questions about this dataset, refer to the data_dictionary.json file for comprehensive variable documentation.

## License
This is a fabricated dataset for research and educational purposes.
