# Nigerian SME Innovation Dataset

## Research Title
**Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth**

---

## 📊 Dataset Overview

This comprehensive synthetic dataset has been generated for academic research on innovation adoption in Nigerian Small and Medium Enterprises (SMEs). The dataset includes **800 SME respondents** across Nigeria with **82 variables** covering:

- **Section A**: Firmographics & Managerial Characteristics
- **Section B**: Innovation Adoption (Independent Variables)
- **Section C**: Constraint Assessment (Moderating Variables)
- **Section D**: Firm Performance and Growth (Dependent Variables)
- **Composite Indices**: Calculated innovation, constraints, and performance metrics

### Dataset Characteristics

- **Sample Size**: 800 SMEs
- **Total Variables**: 82
- **Geographic Coverage**: All 6 geo-political zones of Nigeria
- **Industries**: 15 sectors (ISIC coded)
- **Firm Sizes**: Micro (1-10), Small (11-50), Medium (51-200) employees
- **Data Type**: Synthetic/Simulated with realistic correlations

---

## 📁 Files Included

### 1. **Dataset Files**
- `nigerian_sme_innovation_dataset.csv` - Main dataset (CSV format)
- `nigerian_sme_innovation_dataset.xlsx` - Excel format with 6 sheets:
  - Full_Dataset
  - A_Firmographics
  - B_Innovation
  - C_Constraints
  - D_Performance
  - E_Indices
- `nigerian_sme_innovation_dataset.json` - JSON format
- `nigerian_sme_dataset_with_clusters.csv` - Dataset with cluster assignments

### 2. **Documentation**
- `data_dictionary.json` - Complete variable documentation
- `summary_report.txt` - Statistical summary and insights
- `README.md` - This file

### 3. **Analysis Scripts**
- `generate_sme_dataset.py` - Dataset generation script
- `ml_analysis_starter.py` - Machine learning analysis examples
- `survey_questionnaire_template.py` - Survey questionnaire generator

### 4. **Visualizations**
- `correlation_heatmap.png` - Correlation matrix visualization
- `feature_importance.png` - Feature importance analysis
- `confusion_matrix.png` - Classification performance
- `cluster_visualization.png` - SME archetypes clusters
- `innovation_by_size.png` - Innovation by firm size
- `model_results_summary.csv` - Model performance metrics

---

## 🔍 Variable Categories

### Section A: Firmographics (17 variables)
- Firm ID, Location (State, Zone, Urban/Rural)
- Industry/Sector (ISIC coded)
- Firm Age, Size (Employees, Turnover in Naira)
- Legal Structure
- Owner/Manager Profile (Age, Gender, Education, Experience, Digital Literacy)

### Section B: Innovation Adoption (26 variables)
**Technological Innovation** (Likert 1-5):
- Digital tools: Computers, Accounting Software, CRM, E-commerce, Cloud, Social Media
- Advanced tech: AI/ML, IoT, Blockchain, Robotics
- Digital presence: Website, Social Media, Online Payments

**Process Innovation** (Likert 1-5):
- New production methods
- Supply chain software
- Inventory management
- HR software

**Product/Service Innovation** (Likert 1-5):
- New products/services
- Product improvements
- Launch frequency

**Business Model Innovation** (Likert 1-5):
- Revenue model changes
- Value proposition changes
- Customer engagement strategies

**Innovation Drivers** (Likert 1-5):
- Competitive pressure
- Customer demand
- Management attitude

### Section C: Constraints (16 variables, Likert 1-5)
**Financial**: Access to credit, cost of innovation, internal capital sufficiency  
**Human Capital**: Skilled employees difficulty, training costs, leadership capability  
**Infrastructure**: Electricity, internet quality/cost, logistics  
**Regulatory**: Regulatory burden, corruption, government support  
**Market**: Competition intensity, demand uncertainty, international access

### Section D: Performance (13 variables)
**Subjective Performance** (Likert 1-5):
- Profitability, sales, market share growth
- ROI, overall satisfaction

**Objective Performance** (%, with missing data):
- Turnover growth (70% response rate)
- Profit margin (60% response rate)
- Employee growth (75% response rate)
- New branches count (80% response rate)

**Non-Financial Growth** (Likert 1-5):
- Product line expansion
- Quality improvement
- Customer satisfaction
- Customer retention

### Composite Indices (10 variables, continuous)
- Overall Innovation Index
- Technology Innovation Index
- Advanced Technology Index
- Digital Presence Index
- Process Innovation Index
- Product Innovation Index
- Overall Constraints Index
- Financial Constraints Index
- Infrastructure Constraints Index
- Overall Performance Index

---

## 🎯 Key Research Findings

### 1. Innovation-Performance Relationship
- **Correlation**: 0.585 (strong positive)
- Innovation is a **significant predictor** of SME performance
- Linear Regression R² = 0.35 (explains 35% of performance variance)

### 2. Constraints Impact
- **Correlation with Performance**: -0.173 (negative)
- Constraints **moderate** the Innovation-Performance relationship
- **Moderation Effect**: -0.188 (constraints weaken innovation effectiveness)

### 3. Model Performance
| Model | R² Score | RMSE |
|-------|----------|------|
| Linear Regression | 0.354 | 0.604 |
| Random Forest | 0.299 | 0.629 |
| Gradient Boosting | 0.238 | 0.656 |

| Classification Model | Accuracy |
|---------------------|----------|
| Logistic Regression | 78.8% |
| Random Forest | 76.9% |

### 4. Top Innovation Drivers
1. Digital Presence Index
2. Process Innovation
3. Technology Adoption
4. Owner Digital Literacy
5. Firm Size

### 5. SME Archetypes (Clusters)
- **Cluster 0 & 1** (45.1%): High-Innovation, Low-Constraint, High-Performance
- **Cluster 2 & 3** (54.9%): Low-Innovation, High-Constraint, Low-Performance

### 6. Comparative Insights
**By Firm Size**:
- Medium firms: Innovation Index = 3.76, Performance = 3.06
- Small firms: Innovation Index = 3.46, Performance = 2.57
- Micro firms: Innovation Index = 3.23, Performance = 2.44

**By Location**:
- Urban SMEs: Innovation = 3.42, Performance = 2.62
- Rural SMEs: Innovation = 3.15, Performance = 2.32

**By Zone** (Top 3 for Innovation):
1. North Central: 3.48
2. North West: 3.44
3. North East: 3.35

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install numpy pandas openpyxl scikit-learn matplotlib seaborn
```

### Load Dataset
```python
import pandas as pd

# Load full dataset
df = pd.read_csv('nigerian_sme_innovation_dataset.csv')

# View structure
print(df.info())
print(df.describe())
```

### Run Complete Analysis
```bash
python3 ml_analysis_starter.py
```

This will generate:
- Correlation analysis
- Regression models (Linear, Random Forest, Gradient Boosting)
- Moderation analysis
- Classification models (Logistic, Random Forest)
- Clustering analysis
- Feature importance rankings
- Visualizations (heatmaps, confusion matrix, cluster plots)

---

## 📈 Recommended Analyses

### 1. **Regression Analysis**
Examine how innovation adoption predicts SME performance while controlling for firm characteristics.

```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

X = df[['Index_Overall_Innovation', 'Firm_Age_Years', 'Num_Employees']]
y = df['Index_Overall_Performance']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LinearRegression()
model.fit(X_scaled, y)
```

### 2. **Moderation Analysis**
Test whether constraints moderate the innovation-performance relationship.

```python
# Create interaction term
df['Innov_x_Const'] = df['Index_Overall_Innovation'] * df['Index_Overall_Constraints']

X_mod = df[['Index_Overall_Innovation', 'Index_Overall_Constraints', 'Innov_x_Const']]
y_mod = df['Index_Overall_Performance']
```

### 3. **Classification**
Predict high vs. low performing SMEs.

```python
from sklearn.ensemble import RandomForestClassifier

# Create binary target
df['High_Performer'] = (df['Index_Overall_Performance'] > df['Index_Overall_Performance'].median()).astype(int)

X_clf = df[['Index_Overall_Innovation', 'Index_Overall_Constraints', 'Num_Employees']]
y_clf = df['High_Performer']

clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_clf, y_clf)
```

### 4. **Clustering**
Identify distinct SME archetypes.

```python
from sklearn.cluster import KMeans

cluster_vars = ['Index_Overall_Innovation', 'Index_Overall_Constraints', 
                'Index_Overall_Performance']
X_cluster = df[cluster_vars]

kmeans = KMeans(n_clusters=4, random_state=42)
df['Cluster'] = kmeans.fit_predict(X_cluster)
```

### 5. **Comparative Analysis**
Compare innovation adoption across:
- Firm sizes (Micro, Small, Medium)
- Locations (Urban, Rural)
- Geo-political zones
- Industries

```python
# By firm size
df.groupby('Size_Category')[['Index_Overall_Innovation', 'Index_Overall_Performance']].mean()

# By location
df.groupby('Location_Type')[['Index_Overall_Innovation', 'Index_Overall_Performance']].mean()
```

---

## 📊 Data Quality Notes

### Realistic Correlations Built In:
✓ Higher innovation → Better performance  
✓ Higher constraints → Lower performance  
✓ Larger firms → More innovative  
✓ Urban location → More innovative  
✓ Higher education → Higher digital literacy  
✓ Rural/Northern areas → More constraints  

### Missing Data Patterns:
The dataset includes realistic missing data patterns for sensitive objective performance metrics:
- Turnover growth: 30% missing
- Profit margin: 40% missing
- Employee growth: 25% missing
- New branches: 20% missing

### Geographic Distribution:
- South West: 35% (Lagos, Ogun, Oyo, etc.) - Highest SME concentration
- South East: 20% (Anambra, Abia, Enugu, etc.)
- South South: 15% (Rivers, Delta, Akwa Ibom, etc.)
- North Central: 15% (FCT, Plateau, etc.)
- North East: 8%
- North West: 7%

---

## 🔬 Research Applications

This dataset is suitable for:

1. **Hypothesis Testing**
   - H1: Innovation adoption positively affects SME performance
   - H2: Constraints moderate the innovation-performance relationship
   - H3: Firm characteristics influence innovation adoption

2. **Machine Learning Applications**
   - Predictive modeling (regression, classification)
   - Feature importance analysis
   - Clustering and segmentation
   - Ensemble methods
   - Deep learning (with feature engineering)

3. **Statistical Analysis**
   - Multiple regression
   - Structural Equation Modeling (SEM)
   - Mediation and moderation analysis
   - ANOVA/MANOVA
   - Factor analysis

4. **Policy Implications Research**
   - Identify key innovation barriers
   - Develop targeted interventions
   - Inform SME support programs
   - Guide resource allocation

---

## 📚 Citation

If you use this dataset in your research, please cite:

```
Nigerian SME Innovation Dataset (2025)
Research: "Leveraging Machine Learning to Examine Innovation Adoption and 
Constraints in Nigerian SMEs: Implications for Performance and Growth"
Dataset Version: 1.0
Generated: October 2025
```

---

## ⚠️ Limitations

1. **Synthetic Data**: This is a simulated dataset created for research purposes. While it contains realistic patterns and correlations, it is not collected from actual SMEs.

2. **Self-Reported Measures**: Most variables are perceptual (Likert scales) which may contain response bias in real-world applications.

3. **Cross-Sectional**: The dataset represents a single time point. Longitudinal analysis would require temporal data.

4. **Missing Data**: Objective performance metrics have intentional missing values to simulate realistic survey response patterns.

---

## 🛠️ Technical Details

### Data Generation Method:
- **Base Variables**: Generated using appropriate distributions (normal, exponential, categorical)
- **Correlations**: Realistic relationships programmed between variables
- **Latent Variables**: Innovation propensity and constraint severity influence observed variables
- **Noise**: Random variation added to simulate real-world measurement error
- **Missing Data**: MCAR (Missing Completely at Random) mechanism for sensitive metrics

### Software Requirements:
- Python 3.7+
- NumPy 1.19+
- Pandas 1.2+
- Scikit-learn 0.24+
- Matplotlib 3.3+
- Seaborn 0.11+
- OpenPyXL 3.0+

---

## 📞 Support

For questions, issues, or suggestions regarding this dataset, please refer to the documentation files or examine the generation script (`generate_sme_dataset.py`).

---

## 📄 License

This dataset is provided for **academic and research purposes**. 

---

## 🎓 Educational Use

This dataset is ideal for:
- PhD dissertations on innovation and entrepreneurship
- Master's theses in business analytics
- Undergraduate capstone projects
- Academic workshops on ML in business research
- Teaching statistical methods and machine learning

---

**Generated**: October 22, 2025  
**Version**: 1.0  
**Status**: Ready for Analysis ✅

---

*Don't hold nothing back! This dataset is comprehensive, realistic, and ready for your groundbreaking research on Nigerian SME innovation!* 🚀📊🎯
