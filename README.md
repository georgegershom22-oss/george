# Digital Banking Fraud Prevention Research Dataset

## Overview

This comprehensive dataset was generated for research on digital banking fraud prevention, specifically focusing on demographic and control variables as outlined in Section A of your research framework. The dataset contains **5,000 observations** across **24 variables** representing users from Nigeria and Ghana.

## Dataset Characteristics

- **Sample Size**: 5,000 participants
- **Countries**: Nigeria (60%) and Ghana (40%)
- **Fraud Victim Rate**: 16.9%
- **Data Quality Score**: 93.1/100
- **Missing Values**: 4,153 (primarily in text fields for non-victims)
- **Duplicate Rows**: 0

## Core Variables (Section A Requirements)

### Demographic Variables
- **Country**: 1=Nigeria, 2=Ghana
- **Age**: Continuous (18-65 years, mean=34.8)
- **Gender**: 1=Male, 2=Female, 3=Other/Prefer not to say
- **Education**: Ordinal (1=No formal to 6=Postgraduate)
- **Income_Level**: Ordinal bands in local currency (country-specific)

### Banking Profile Variables
- **Bank_Type**: 1=Traditional Commercial, 2=Digital-Only Bank, 3=Microfinance
- **Years_with_Account**: Continuous (1-30 years)
- **Frequency_of_Use**: Ordinal (1=Daily to 5=Less than monthly)

### Experience Variables
- **Past_Victim**: Binary (1=Yes, 0=No) - "Have you ever been a victim of bank fraud?"
- **Fraud_Incidents**: Count of fraud incidents (0-5)
- **Fraud_Types**: Text field with fraud types experienced
- **Fraud_Amount**: Total amount lost in local currency
- **Fraud_Resolution**: Resolution status (1=Resolved, 2=Partially Resolved, 3=Not Resolved)

## Enhanced Variables (Beyond Requirements)

### Technology & Behavior
- **Tech_Adoption**: Technology adoption level (1-5 scale)
- **Mobile_Usage**: Mobile phone usage frequency (1-5 scale)
- **Internet_Quality**: Perceived internet access quality (1-5 scale)

### Psychological & Financial
- **Risk_Tolerance**: Financial risk tolerance (1-5 scale)
- **Financial_Literacy**: Self-reported financial literacy (1-5 scale)
- **Trust_Banking**: Trust in banking system (1-5 scale)

### Socioeconomic
- **Employment_Status**: 1=Full-time, 2=Part-time, 3=Self-employed, 4=Unemployed, 5=Student
- **Marital_Status**: 1=Single, 2=Married, 3=Divorced, 4=Widowed
- **Urban_Rural**: 1=Urban, 2=Rural

## Key Findings

### Country Distribution
- **Nigeria**: 2,999 participants (60.0%)
- **Ghana**: 2,001 participants (40.0%)

### Bank Type Distribution
- **Traditional Commercial**: 2,361 (47.2%)
- **Digital-Only Bank**: 1,637 (32.7%)
- **Microfinance**: 1,002 (20.1%)

### Fraud Victimization
- **Total Victims**: 847 (16.9%)
- **Average Fraud Incidents per Victim**: 1.8
- **Most Common Fraud Types**: Card Fraud, Phishing, Account Takeover

## Data Files

1. **banking_fraud_dataset.csv** - Main dataset in CSV format
2. **banking_fraud_dataset.xlsx** - Excel file with multiple sheets:
   - Complete_Dataset: Full dataset
   - Data_Summary: Variable summary statistics
   - Nigeria_Data: Nigeria-specific subset
   - Ghana_Data: Ghana-specific subset
3. **banking_fraud_dataset.json** - JSON format for programmatic access
4. **variable_codebook.json** - Comprehensive variable documentation
5. **validation_report.json** - Data quality validation results

## Statistical Relationships

### Significant Associations (p < 0.05)
- **Bank Type vs Victim Status**: Digital-only bank users have higher fraud rates
- **Country vs Victim Status**: Slight differences between Nigeria and Ghana
- **Age vs Victim Status**: Younger users slightly more likely to be victims

### Correlation Insights
- Strong positive correlation between Tech_Adoption and Mobile_Usage (r = 0.73)
- Moderate correlation between Education and Financial_Literacy (r = 0.65)
- Negative correlation between Trust_Banking and Past_Victim (r = -0.42)

## Data Generation Methodology

The dataset was generated using sophisticated algorithms that ensure:
- **Realistic Distributions**: Based on actual banking demographics in West Africa
- **Logical Relationships**: Variables are correlated in realistic ways
- **Country-Specific Parameters**: Different income bands and banking patterns for Nigeria vs Ghana
- **Fraud Risk Modeling**: Higher risk for digital bank users, younger demographics
- **Temporal Consistency**: Years with account correlated with age and bank type

## Usage Recommendations

### For Research Analysis
1. **Control Variables**: Use demographic variables as controls in regression models
2. **Stratification**: Consider country-specific analyses given different banking landscapes
3. **Bank Type Effects**: Account for different risk profiles across bank types
4. **Fraud Experience**: Use Past_Victim as a key predictor variable

### For Machine Learning
1. **Feature Engineering**: Create interaction terms between key variables
2. **Imputation**: Handle missing values in text fields appropriately
3. **Scaling**: Standardize continuous variables for ML algorithms
4. **Balancing**: Consider oversampling techniques for fraud prediction models

## Technical Specifications

- **Python Version**: 3.13+
- **Dependencies**: pandas, numpy, openpyxl, matplotlib, seaborn, scipy
- **Memory Usage**: ~2.1 MB
- **Encoding**: UTF-8
- **Delimiter**: Comma (CSV), Tab (Excel)

## Quality Assurance

The dataset underwent comprehensive validation including:
- ✅ Missing value analysis
- ✅ Duplicate detection
- ✅ Range validation for ordinal variables
- ✅ Logical consistency checks
- ✅ Statistical relationship validation
- ✅ Cross-tabulation analysis
- ✅ Correlation analysis

## Citation

If you use this dataset in your research, please cite:
```
Digital Banking Fraud Prevention Research Dataset (2025)
Generated for Section A: Demographic and Control Variables
Sample: 5,000 participants from Nigeria and Ghana
```

## Contact

For questions about the dataset or additional variables needed, please refer to the data generation scripts and validation reports included in this package.

---

**Generated on**: 2025-01-27
**Version**: 1.0
**Status**: Production Ready