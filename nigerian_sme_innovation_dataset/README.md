# Nigerian SME Innovation Dataset & Analysis Framework

## 🎯 Research Topic
**Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth**

## 📊 Dataset Overview
A comprehensive synthetic dataset of 5,000 Nigerian SMEs designed for machine learning analysis of innovation adoption patterns, operational constraints, and their impact on business performance.

### Key Features:
- **80 variables** covering firmographics, innovation metrics, constraints, and performance indicators
- **Realistic Nigerian context** with geopolitical zones, industry distributions, and local constraints
- **ML-ready** with calculated composite scores and engineered features
- **No missing values** in core numerical features

## 🗂️ Project Structure
```
nigerian_sme_innovation_dataset/
│
├── data/                           # Generated datasets
│   ├── nigerian_sme_innovation_data.csv         # Main dataset (5,000 records)
│   ├── nigerian_sme_innovation_data.xlsx        # Excel format with multiple sheets
│   ├── nigerian_sme_innovation_sample.csv       # Sample dataset (100 records)
│   ├── dataset_summary_report.txt               # Statistical summary
│   ├── detailed_analysis_report.txt             # Comprehensive analysis
│   └── analysis_visualizations.png              # Key charts and graphs
│
├── scripts/                        # Python scripts
│   ├── generate_sme_dataset.py                  # Data generation script
│   └── validate_and_analyze.py                  # Validation and analysis script
│
├── notebooks/                      # Jupyter notebooks
│   └── ml_analysis_demo.ipynb                   # ML analysis demonstration
│
├── documentation/                  # Documentation
│   └── data_dictionary.md                       # Complete variable descriptions
│
├── requirements.txt                # Package dependencies
├── requirements_simple.txt         # Basic dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or navigate to the project directory
cd nigerian_sme_innovation_dataset

# Install dependencies
pip install -r requirements_simple.txt
```

### 2. Generate Dataset
```bash
# Generate the synthetic dataset
python3 scripts/generate_sme_dataset.py
```

### 3. Run Analysis
```bash
# Validate and analyze the dataset
python3 scripts/validate_and_analyze.py
```

### 4. Explore ML Models
```bash
# Launch Jupyter notebook
jupyter notebook notebooks/ml_analysis_demo.ipynb
```

## 📈 Dataset Sections

### Section A: Firmographics & Managerial Characteristics
- Location (State, Geopolitical Zone, Urban/Rural)
- Industry/Sector (ISIC classification)
- Firm size and age
- Owner/Manager profile
- Digital literacy scores

### Section B: Innovation Adoption (Independent Variables)
- **Technological Innovation**: Digital tools, advanced tech adoption
- **Process Innovation**: New production methods, supply chain software
- **Product/Service Innovation**: New offerings, launch frequency
- **Business Model Innovation**: Revenue model changes, value propositions

### Section C: Constraint Assessment (Moderating Variables)
- **Financial**: Access to credit, innovation costs
- **Human Capital**: Skilled employee availability, training costs
- **Infrastructure**: Electricity, internet, logistics
- **Regulatory**: Government burden, corruption
- **Market**: Competition, demand uncertainty

### Section D: Performance & Growth (Dependent Variables)
- **Subjective Measures**: Profitability, sales, market share growth
- **Objective Measures**: Turnover growth, profit margins, employee growth
- **Non-Financial**: Product lines, quality, customer satisfaction

## 🤖 Machine Learning Applications

### Implemented Models:
1. **Linear Models**: Ridge, Lasso, Elastic Net
2. **Tree-Based Models**: Random Forest, Gradient Boosting
3. **Clustering**: K-Means for SME segmentation
4. **Feature Engineering**: Interaction terms, ratios, categorical encodings

### Key Insights:
- Innovation score is the **strongest predictor** of performance (R² > 0.75)
- **4 distinct SME segments** identified through clustering
- Constraints **moderate** the innovation-performance relationship
- Infrastructure and market constraints are **critical barriers**

## 📊 Key Statistics

### Geographic Distribution:
- South-West: 33.6%
- South-South: 21.1%
- South-East: 14.1%
- North-West: 12.4%
- North-Central: 10.7%
- North-East: 8.1%

### Firm Size Distribution:
- Micro (1-9 employees): 11.3%
- Small (10-49 employees): 80.8%
- Medium (50-250 employees): 7.9%

### Performance Metrics:
- Average Performance Score: 2.82/5.0
- Average Turnover Growth: 3.1%
- Average Profit Margin: 16.6%
- Customer Retention Rate: 64.7%

## 🎯 Use Cases

### Research Applications:
- Test hypotheses about innovation-performance relationships
- Analyze constraint impacts on SME growth
- Develop predictive models for SME success
- Identify factors driving digital transformation

### Policy Applications:
- Target support programs to specific SME segments
- Prioritize infrastructure investments by region
- Design effective innovation incentive schemes
- Evaluate intervention effectiveness

### Business Applications:
- Benchmark performance against industry peers
- Identify growth opportunities
- Assess competitive positioning
- Guide strategic planning

## 📝 Citation
If you use this dataset in your research, please cite:
```
Nigerian SME Innovation Dataset (2024): A Synthetic Dataset for Machine Learning 
Analysis of Innovation, Constraints, and Performance in Nigerian Small and Medium Enterprises.
Generated for: Leveraging Machine Learning to Examine Innovation Adoption and Constraints 
in Nigerian SMEs: Implications for Performance and Growth.
```

## ⚠️ Disclaimer
This is a **synthetic dataset** generated for research and educational purposes. While it reflects realistic patterns and relationships based on SME literature and Nigerian business context, it should not be used for actual business decisions or policy-making without validation with real data.

## 🛠️ Technical Requirements
- Python 3.8+
- 4GB RAM minimum
- 100MB storage space
- Jupyter Notebook (optional, for interactive analysis)

## 📧 Support
For questions about the dataset or analysis framework, please refer to the documentation in the `documentation/` folder or review the analysis notebooks.

## 🔄 Version
- Version: 1.0.0
- Generated: 2024
- Records: 5,000 SMEs
- Variables: 80

## 📜 License
This synthetic dataset is provided for research and educational purposes. Feel free to use, modify, and distribute with appropriate attribution.

---

**Happy Analyzing! 🚀📊**