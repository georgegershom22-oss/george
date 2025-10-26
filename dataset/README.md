# Digital Banking Fraud Control Research Dataset

## Overview

This comprehensive dataset contains **5,000 observations** across **27 variables** designed for analyzing digital banking fraud control mechanisms in Nigeria and Ghana. The dataset includes demographic, banking profile, fraud experience, and additional control variables with realistic statistical relationships.

## Dataset Information

- **Sample Size**: 5,000 observations
- **Variables**: 27 variables
- **Countries**: Nigeria (60%) and Ghana (40%)
- **Generated Date**: 2025-10-26
- **File Formats**: CSV, Excel, JSON
- **Missing Values**: None

## Key Findings

### Fraud Statistics
- **Overall Fraud Victim Rate**: 38.5%
- **Nigeria**: 41.8% fraud rate
- **Ghana**: 33.6% fraud rate
- **Digital-Only Banks**: 46.1% fraud rate
- **Traditional Banks**: 34.4% fraud rate

### Key Insights
1. **Digital bank users are 11.7 percentage points more likely to be fraud victims**
2. **Younger users (under 30) are 15.4 percentage points more vulnerable than older users (45+)**
3. **Higher education correlates with better security knowledge (0.50 point difference)**
4. **Ghana shows 6.5 percentage points higher digital banking adoption than Nigeria**

## Variable Descriptions

### Core Demographic Variables
- **Country**: 1=Nigeria, 2=Ghana
- **Age**: Continuous variable (18-65 years)
- **Gender**: 1=Male, 2=Female, 3=Other/Prefer not to say
- **Education**: 1=No formal, 2=Primary, 3=Secondary, 4=Diploma, 5=Bachelor, 6=Postgraduate
- **Income_Level**: 1=Very Low, 2=Low, 3=Below Average, 4=Average, 5=Above Average, 6=High
- **Urban_Rural**: 1=Urban, 2=Rural

### Banking Profile Variables
- **Bank_Type**: 1=Traditional Commercial, 2=Digital-Only Bank, 3=Microfinance
- **Years_with_Account**: Number of years with current bank account
- **Frequency_of_Use**: 1=Daily, 2=Weekly, 3=Monthly, 4=Quarterly, 5=Less than monthly

### Fraud Experience Variables
- **Past_Victim**: 1=Yes, 0=No - Have you ever been a victim of bank fraud?
- **Fraud_Awareness**: 1-5 scale - How aware are you of banking fraud risks?
- **Fraud_Concern**: 1-5 scale - How concerned are you about banking fraud?
- **Security_Knowledge**: 1-5 scale - How knowledgeable are you about banking security?

### Technology and Trust Variables
- **Tech_Adoption**: 1-5 scale - General technology adoption level
- **Smartphone_Usage**: 1-5 scale - Smartphone usage frequency
- **Internet_Usage**: 1-5 scale - Internet usage frequency
- **Trust_Traditional_Banking**: 1-5 scale - Trust in traditional banking
- **Trust_Digital_Banking**: 1-5 scale - Trust in digital banking

### Additional Control Variables
- **Financial_Literacy**: 1-5 scale - Financial literacy level
- **Risk_Tolerance**: 1-5 scale - Risk tolerance level
- **Marital_Status**: 1=Single, 2=Married, 3=Divorced, 4=Widowed
- **Employment_Status**: 1=Employed, 2=Student, 3=Unemployed, 4=Retired
- **Household_Size**: Number of people in household

## Statistical Relationships

### Significant Correlations with Fraud Victim Status
- **Fraud_Concern**: 0.465 (strong positive)
- **Fraud_Awareness**: 0.308 (moderate positive)
- **Trust_Traditional_Banking**: -0.385 (moderate negative)
- **Trust_Digital_Banking**: -0.134 (weak negative)
- **Age**: -0.116 (weak negative)

### Statistical Significance Tests
- **Country differences in fraud rates**: Highly significant (p < 0.001)
- **Bank type and fraud victim status**: Highly significant (p < 0.001)
- **Age group differences in fraud awareness**: Highly significant (p < 0.001)

## File Structure

```
dataset/
├── banking_fraud_dataset.csv          # Main dataset in CSV format
├── banking_fraud_dataset.xlsx         # Main dataset in Excel format
├── banking_fraud_dataset.json         # Main dataset in JSON format
├── data_dictionary.json               # Variable definitions and coding
├── dataset_summary.txt                # Descriptive statistics summary
├── country_summary_stats.csv          # Country-level summary statistics
├── dataset_visualizations.png         # Key visualizations
└── README.md                          # This documentation file
```

## Usage Recommendations

### Research Applications
1. **Comparative Analysis**: Nigeria vs Ghana banking behavior
2. **Digital Banking Studies**: Traditional vs digital bank user analysis
3. **Fraud Risk Modeling**: Machine learning for fraud prediction
4. **Demographic Profiling**: Customer segmentation analysis
5. **Trust and Technology Studies**: Adoption and trust patterns

### Statistical Methods
- **Descriptive Statistics**: Cross-tabulations, means, distributions
- **Inferential Statistics**: T-tests, chi-square tests, ANOVA
- **Correlation Analysis**: Pearson correlations, partial correlations
- **Regression Analysis**: Logistic regression for fraud prediction
- **Machine Learning**: Classification, clustering, feature selection

### Data Quality
- **Completeness**: No missing values
- **Consistency**: Logical relationships between variables
- **Realism**: Based on actual West African banking patterns
- **Balance**: Appropriate sample sizes across groups

## Technical Notes

### Data Generation
- Generated using Python with realistic statistical distributions
- Country-specific parameters based on actual demographic data
- Correlations designed to reflect real-world banking behavior patterns
- Random seed set for reproducibility

### Variable Coding
- All categorical variables use numeric coding for analysis
- Scale variables (1-5) represent Likert-type responses
- Binary variables use 0/1 coding
- Continuous variables maintain original scales

### Ethical Considerations
- Synthetic data - no real personal information
- Designed for research and educational purposes
- Follows data privacy best practices
- Suitable for academic and commercial research

## Citation

If you use this dataset in your research, please cite:

```
Digital Banking Fraud Control Research Dataset (2025)
Generated for comparative analysis of banking fraud patterns
in Nigeria and Ghana. Contains 5,000 synthetic observations
across 27 variables with realistic statistical relationships.
```

## Contact

For questions about this dataset or requests for additional variables, please refer to the generation scripts in the parent directory.

---

**Note**: This is a synthetic dataset generated for research purposes. All data is fabricated and does not contain real personal information.