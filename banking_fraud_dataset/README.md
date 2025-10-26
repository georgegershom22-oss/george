# 🏦 COMPREHENSIVE BANKING FRAUD PREVENTION DATASET

## 📋 Overview

This is a **comprehensive, fabricated dataset** designed for research on banking fraud prevention behaviors in West Africa. The dataset contains **2,500 participants** from **Nigeria** (1,500) and **Ghana** (1,000) with **28 variables** covering demographics, banking profiles, fraud experiences, and behavioral measures.

## 🎯 Dataset Purpose

This dataset was specifically designed for:
- **Comparative analysis** between Nigeria and Ghana
- **Banking fraud prevention behavior** research
- **Digital banking adoption** studies
- **Cross-cultural financial behavior** analysis
- **Fraud victimization pattern** investigation

## 📊 Dataset Specifications

### Sample Composition
- **Total Sample**: 2,500 participants
- **Nigeria**: 1,500 participants (60%)
- **Ghana**: 1,000 participants (40%)
- **Age Range**: 18-75 years
- **Data Collection Period**: January-June 2024 (simulated)

### Key Variables (28 total)

#### 🏷️ Core Demographics
- `Participant_ID`: Unique identifier
- `Country`: 1=Nigeria, 2=Ghana
- `Age`: Age in years (18-75)
- `Gender`: 1=Male, 2=Female, 3=Other/Prefer not to say
- `Education`: 1=No formal to 6=Postgraduate
- `Income_Level`: Income bands in local currency (1-6)
- `Location_Type`: 1=Urban, 2=Rural
- `Employment_Status`: Employment category (1-6)

#### 🏦 Banking Profile
- `Bank_Type`: 1=Traditional, 2=Digital-Only, 3=Microfinance
- `Years_with_Account`: Banking experience (1-25 years)
- `Frequency_of_Use`: Usage frequency (1=Daily to 5=Less than monthly)

#### 🔐 Fraud Experience
- `Past_Victim`: 0=No, 1=Yes (ever been fraud victim)
- `Num_Fraud_Incidents`: Number of incidents (0-5)
- `Months_Since_Last_Incident`: Time since last incident
- `Financial_Loss_Band`: Loss category (0-5)
- `Recovery_Success`: 0=No recovery, 1=Successful recovery
- **Fraud Types**: Card_Fraud, Online_Banking_Fraud, SMS_Phishing, ATM_Skimming, Social_Engineering

#### 📱 Behavioral Measures
- `Technology_Adoption_Score`: Tech comfort (1-10 scale)
- `Financial_Literacy_Score`: Financial knowledge (1-10 scale)
- `Risk_Tolerance`: Risk preference (1-7 scale)
- `Trust_in_Banks`: Trust level (1-10 scale)
- `Internet_Hours_Daily`: Daily internet usage
- `Social_Media_Usage`: Social media engagement (0-3)

## 📁 File Formats Available

1. **`comprehensive_banking_fraud_dataset.csv`** - Main dataset (CSV format)
2. **`comprehensive_banking_fraud_dataset.xlsx`** - Excel with multiple sheets
3. **`comprehensive_banking_fraud_dataset.json`** - JSON format
4. **`comprehensive_banking_fraud_dataset.parquet`** - Parquet format (efficient)
5. **`CODEBOOK.md`** - Comprehensive variable documentation
6. **`validation_results.json`** - Data validation metrics
7. **`variable_definitions.json`** - Variable coding definitions
8. **`RESEARCH_SUMMARY.md`** - Key findings and research applications

## 🔍 Key Findings

### Fraud Prevalence
- **Overall**: 30.5% fraud victimization rate
- **Nigeria**: 32.7% (higher risk)
- **Ghana**: 27.1% (lower risk)

### Digital Banking Adoption
- **Overall**: 27.2% use digital-only banks
- **Nigeria**: 28.5% digital adoption
- **Ghana**: 25.1% digital adoption

### Risk Patterns
- **High-risk profile**: Urban, 30-50 years, digital bank users, frequent usage
- **Digital bank users**: 36.1% fraud rate vs 29.8% traditional bank users
- **Age effect**: Peak fraud risk in 36-45 age group

## 📈 Data Quality Features

✅ **Realistic Correlations**: All variables show expected relationships  
✅ **Country Differences**: Significant variations support comparative analysis  
✅ **Missing Data Pattern**: Intentional missingness for fraud variables (when not applicable)  
✅ **Statistical Validity**: Proper distributions and effect sizes  
✅ **Research Ready**: Suitable for advanced statistical analysis  

## 🔬 Statistical Highlights

### Key Correlations
- Education ↔ Financial Literacy: r = 0.601
- Age ↔ Technology Adoption: r = -0.524
- Past Victim ↔ Trust in Banks: r = -0.533
- Education ↔ Income Level: r = 0.278

### Significant Country Differences
- Fraud prevalence: p = 0.003 (Nigeria > Ghana)
- Bank type distribution: p = 0.097 (marginally significant)
- Education levels: p = 0.444 (not significant)

## 🚀 Usage Instructions

### Loading the Data

**Python (pandas):**
```python
import pandas as pd
df = pd.read_csv('comprehensive_banking_fraud_dataset.csv')
```

**R:**
```r
df <- read.csv('comprehensive_banking_fraud_dataset.csv')
```

**Excel:** Open the `.xlsx` file with multiple sheets for different views

### Recommended Analysis Approaches

1. **Comparative Analysis**: Use `Country` as grouping variable
2. **Fraud Prediction**: Use `Past_Victim` as outcome variable
3. **Control Variables**: Include Age, Gender, Education, Income_Level
4. **Mediator Analysis**: Technology_Adoption_Score, Financial_Literacy_Score
5. **Interaction Effects**: Country × other demographic variables

## ⚠️ Important Notes

- This is a **fabricated dataset** created for research purposes
- All correlations and patterns are **realistic** but **simulated**
- Missing values in fraud variables are **intentional** (NaN when Past_Victim = 0)
- Use appropriate statistical methods for **cross-cultural comparison**
- Consider **clustering** by country in regression models

## 📚 Citation

```
Banking Fraud Prevention Dataset - Nigeria & Ghana Comparative Study
Generated: October 2024
Sample Size: N = 2,500 (Nigeria: 1,500, Ghana: 1,000)
Variables: 28 demographic, behavioral, and fraud experience measures
```

## 📞 Support

For questions about variable definitions, see `CODEBOOK.md`  
For analysis examples, see `RESEARCH_SUMMARY.md`  
For technical validation, see `validation_results.json`

---

**🎉 Dataset is ready for comprehensive research analysis!**

*This dataset provides a rich foundation for understanding banking fraud prevention behaviors across West African contexts with realistic demographic patterns, meaningful correlations, and comprehensive fraud experience measures.*