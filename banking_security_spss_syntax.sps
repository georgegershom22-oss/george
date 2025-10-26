* Banking Security Behavior Dataset - SPSS Syntax
* Generated automatically - modify as needed
* 
* Import the CSV file first, then run this syntax

* Set up variable labels and value labels

VARIABLE LABELS
  participant_id 'Unique participant identifier'
  age 'Age in years'
  gender 'Gender identity'
  education 'Highest education level'
  income 'Annual household income'
  tech_savviness 'Self-reported technology proficiency'
  banking_frequency 'Frequency of online/mobile banking use'
  previous_incidents 'Previous security incidents'
  t1_attitudes_1 'Attitudes toward banking security - Item 1'
  t1_attitudes_2 'Attitudes toward banking security - Item 2'
  t1_attitudes_3 'Attitudes toward banking security - Item 3'
  t1_attitudes_mean 'Mean of attitudes items'
  t1_subjective_norms_1 'Subjective norms - Item 1'
  t1_subjective_norms_2 'Subjective norms - Item 2'
  t1_subjective_norms_3 'Subjective norms - Item 3'
  t1_subjective_norms_mean 'Mean of subjective norms items'
  t1_pbc_1 'Perceived Behavioral Control - Item 1'
  t1_pbc_2 'Perceived Behavioral Control - Item 2'
  t1_pbc_3 'Perceived Behavioral Control - Item 3'
  t1_pbc_mean 'Mean of PBC items'
  t1_intentions_1 'Behavioral intentions - Item 1'
  t1_intentions_2 'Behavioral intentions - Item 2'
  t1_intentions_3 'Behavioral intentions - Item 3'
  t1_intentions_mean 'Mean of intentions items'
  srb_1_check_statements 'How often: Check bank statements for unauthorized transactions'
  srb_2_strong_passwords 'How often: Use strong, unique passwords for banking'
  srb_3_two_factor_auth 'How often: Enable two-factor authentication'
  srb_4_logout_properly 'How often: Log out of banking apps/sites after use'
  srb_5_verify_alerts 'How often: Verify text/email alerts before clicking links'
  srb_total_mean 'Mean of all SRB items'
  objective_total_score 'Total score on objective security scenarios'
  predicted_behavior 'Predicted behavior based on T1 intentions'
  intention_behavior_gap 'Residual score: actual - predicted behavior'
  gap_category 'Categorized gap'
  risk_perception 'Perceived risk of banking security threats'
  bank_trust 'Trust in bank's security measures'
  security_self_efficacy 'Confidence in personal security abilities'
  months_since_training 'Months since last security training'
  primary_device 'Primary device for banking'
  t1_date 'Date of Time 1 data collection'
  t2_date 'Date of Time 2 data collection'
  t1_response_time_minutes 'Time to complete T1 survey (minutes)'
  t2_response_time_minutes 'Time to complete T2 survey (minutes)'
.

VALUE LABELS
  gender
    1 'Female'
    2 'Male'
    3 'Non-binary/Other'
  gap_category
    1 'Under-performer'
    2 'As expected'
    3 'Over-performer'
  primary_device
    1 'Desktop'
    2 'Mobile'
    3 'Tablet'
    4 'Multiple'
.

MISSING VALUES
  participant_id ('Missing')
  gender ('Missing')
  income ('Missing')
  previous_incidents ('Missing')
  srb_1_check_statements ('Missing')
  srb_2_strong_passwords ('Missing')
  srb_3_two_factor_auth ('Missing')
  srb_4_logout_properly ('Missing')
  srb_5_verify_alerts ('Missing')
  obj_scenario_1_phishing_sms ('Missing')
  obj_scenario_2_fake_email ('Missing')
  obj_scenario_3_public_wifi ('Missing')
  obj_scenario_4_password_sharing ('Missing')
  obj_scenario_5_suspicious_charge ('Missing')
  gap_category ('Missing')
  primary_device ('Missing')
  t1_date ('Missing')
  t2_date ('Missing')
  t2_response_time_minutes ('Missing')
.

* Compute scale scores
COMPUTE t1_attitudes_mean = MEAN(t1_attitudes_1, t1_attitudes_2, t1_attitudes_3).
COMPUTE t1_subjective_norms_mean = MEAN(t1_subjective_norms_1, t1_subjective_norms_2, t1_subjective_norms_3).
COMPUTE t1_pbc_mean = MEAN(t1_pbc_1, t1_pbc_2, t1_pbc_3).
COMPUTE t1_intentions_mean = MEAN(t1_intentions_1, t1_intentions_2, t1_intentions_3).
COMPUTE srb_total_mean = MEAN(srb_1_check_statements, srb_2_strong_passwords, srb_3_two_factor_auth, srb_4_logout_properly, srb_5_verify_alerts).
EXECUTE.

* Reliability analysis for scales
RELIABILITY /VARIABLES=t1_attitudes_1 t1_attitudes_2 t1_attitudes_3 /SCALE('Attitudes') ALL.
RELIABILITY /VARIABLES=t1_subjective_norms_1 t1_subjective_norms_2 t1_subjective_norms_3 /SCALE('Subjective Norms') ALL.
RELIABILITY /VARIABLES=t1_pbc_1 t1_pbc_2 t1_pbc_3 /SCALE('PBC') ALL.
RELIABILITY /VARIABLES=t1_intentions_1 t1_intentions_2 t1_intentions_3 /SCALE('Intentions') ALL.
RELIABILITY /VARIABLES=srb_1_check_statements srb_2_strong_passwords srb_3_two_factor_auth srb_4_logout_properly srb_5_verify_alerts /SCALE('SRB') ALL.

* Basic descriptive statistics
DESCRIPTIVES VARIABLES=age t1_attitudes_mean t1_subjective_norms_mean t1_pbc_mean t1_intentions_mean srb_total_mean objective_total_score intention_behavior_gap
  /STATISTICS=MEAN STDDEV MIN MAX.

* Correlations
CORRELATIONS
  /VARIABLES=t1_attitudes_mean t1_subjective_norms_mean t1_pbc_mean t1_intentions_mean srb_total_mean objective_total_score
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

* Regression analysis - Intentions predicting behavior
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT srb_total_mean
  /METHOD=ENTER t1_intentions_mean.

