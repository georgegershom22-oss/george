
# COMPREHENSIVE BANKING FRAUD PREVENTION DATASET CODEBOOK
## Section A: Demographic and Control Variables (T1 Measurement)

Generated on: 2025-10-26 18:52:39
Sample Size: 2500
Countries: Nigeria, Ghana

## VARIABLE DEFINITIONS

### Core Demographic Variables

**Participant_ID**
- Type: Integer
- Range: 1 to N
- Description: Unique identifier for each participant

**Country**
- Type: Categorical (Integer coded)
- Values: 1 = Nigeria, 2 = Ghana
- Description: Country of residence and data collection

**Age**
- Type: Continuous (Integer)
- Range: 18-75 years
- Description: Participant's age in years at time of data collection

**Gender**
- Type: Categorical (Integer coded)
- Values: 1 = Male, 2 = Female, 3 = Other/Prefer not to say
- Description: Self-reported gender identity

**Education**
- Type: Ordinal (Integer coded)
- Values: 1 = No formal education
         2 = Primary education
         3 = Secondary education
         4 = Tertiary/University
         5 = Professional certification
         6 = Postgraduate
- Description: Highest level of education completed

**Income_Level**
- Type: Ordinal (Integer coded)
- Values: 1-6 representing income bands in local currency
- Nigeria (NGN): 1 = 0-50k, 2 = 50k-150k, 3 = 150k-300k, 4 = 300k-600k, 5 = 600k-1.2M, 6 = >1.2M
- Ghana (GHS): 1 = 0-1k, 2 = 1k-3k, 3 = 3k-6k, 4 = 6k-12k, 5 = 12k-25k, 6 = >25k
- Description: Monthly household income in local currency bands

**Location_Type**
- Type: Categorical (Integer coded)
- Values: 1 = Urban, 2 = Rural
- Description: Type of residential area

**Employment_Status**
- Type: Categorical (Integer coded)
- Values: 1 = Employed (Full-time)
         2 = Employed (Part-time)
         3 = Self-employed/Business owner
         4 = Student
         5 = Unemployed
         6 = Retired
- Description: Current employment status

### Banking Profile Variables

**Bank_Type**
- Type: Categorical (Integer coded)
- Values: 1 = Traditional Commercial Bank
         2 = Digital-Only Bank
         3 = Microfinance Institution
- Description: Primary bank type used by participant

**Years_with_Account**
- Type: Continuous (Integer)
- Range: 1-25 years
- Description: Number of years participant has maintained a bank account

**Frequency_of_Use**
- Type: Ordinal (Integer coded)
- Values: 1 = Daily
         2 = Several times per week
         3 = Weekly
         4 = Monthly
         5 = Less than monthly
- Description: Frequency of banking service usage

### Fraud Experience Variables

**Past_Victim**
- Type: Binary (Integer coded)
- Values: 0 = No, 1 = Yes
- Description: Whether participant has ever been a victim of bank fraud

**Num_Fraud_Incidents**
- Type: Discrete (Integer)
- Range: 0-5
- Description: Number of fraud incidents experienced (0 if never victimized)

**Months_Since_Last_Incident**
- Type: Continuous (Integer)
- Range: 1-60 months (NaN if never victimized)
- Description: Months since most recent fraud incident

**Financial_Loss_Band**
- Type: Ordinal (Integer coded)
- Range: 0-5 (0 if never victimized)
- Description: Financial loss category from fraud incidents

**Recovery_Success**
- Type: Binary (Integer coded)
- Values: 0 = No recovery, 1 = Successful recovery (NaN if never victimized)
- Description: Whether participant recovered losses from fraud

**Fraud Type Variables** (All binary: 0 = No, 1 = Yes)
- Card_Fraud: Credit/debit card fraud experience
- Online_Banking_Fraud: Internet banking fraud experience
- SMS_Phishing: SMS-based phishing fraud experience
- ATM_Skimming: ATM skimming fraud experience
- Social_Engineering: Social engineering fraud experience

### Additional Control Variables

**Technology_Adoption_Score**
- Type: Continuous (Float)
- Range: 1.0-10.0
- Description: Self-reported technology adoption and comfort level

**Financial_Literacy_Score**
- Type: Continuous (Float)
- Range: 1.0-10.0
- Description: Assessed financial literacy level

**Risk_Tolerance**
- Type: Ordinal (Integer)
- Range: 1-7 (1 = Very risk averse, 7 = Very risk seeking)
- Description: General risk tolerance in financial decisions

**Trust_in_Banks**
- Type: Continuous (Float)
- Range: 1.0-10.0
- Description: General trust level in banking institutions

**Internet_Hours_Daily**
- Type: Continuous (Float)
- Range: 0.5-16.0
- Description: Average hours of internet usage per day

**Social_Media_Usage**
- Type: Ordinal (Integer coded)
- Values: 0 = None, 1 = Low, 2 = Medium, 3 = High
- Description: Level of social media engagement

**Data_Collection_Timestamp**
- Type: Datetime
- Format: YYYY-MM-DD HH:MM:SS
- Description: Timestamp of data collection

## DATA QUALITY NOTES

1. All correlations are realistic and based on established demographic patterns
2. Missing values are intentional for fraud-related variables (NaN when Past_Victim = 0)
3. Country-specific parameters reflect actual demographic and economic differences
4. Sample weights: Nigeria (60%), Ghana (40%) reflect population and research access
5. All random generation uses seed for reproducibility

## USAGE RECOMMENDATIONS

1. Use Country as primary grouping variable for comparative analyses
2. Control for Age, Gender, Education, and Income_Level in regression models
3. Past_Victim is the key predictor variable for fraud prevention behaviors
4. Technology_Adoption_Score and Financial_Literacy_Score are important mediators
5. Consider interaction effects between Country and other demographic variables

## CITATION

Dataset generated using comprehensive demographic modeling for banking fraud prevention research.
Generated: 2025-10-26 18:52:39
Version: 1.0
        