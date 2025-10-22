#!/usr/bin/env python3
"""
Nigerian SME Innovation Dataset Analysis Script
Comprehensive analysis demonstrating the dataset's research potential
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class SMEInnovationAnalyzer:
    def __init__(self, data_path='nigerian_sme_innovation_dataset.csv'):
        """Initialize the analyzer with the dataset"""
        self.df = pd.read_csv(data_path)
        self.setup_plotting()
        
    def setup_plotting(self):
        """Setup plotting parameters"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    def basic_info(self):
        """Display basic dataset information"""
        print("="*80)
        print("NIGERIAN SME INNOVATION DATASET - BASIC INFORMATION")
        print("="*80)
        print(f"Dataset Shape: {self.df.shape}")
        print(f"Total Firms: {len(self.df)}")
        print(f"Total Variables: {len(self.df.columns)}")
        print("\nVariable Categories:")
        print(f"- Firmographics: {len([col for col in self.df.columns if col in ['firm_id', 'state', 'industry', 'firm_age_years', 'num_employees', 'owner_age', 'owner_gender', 'owner_education']])}")
        print(f"- Innovation Variables: {len([col for col in self.df.columns if 'innovation' in col.lower() or 'adoption' in col.lower() or 'digital' in col.lower()])}")
        print(f"- Constraint Variables: {len([col for col in self.df.columns if 'constraint' in col.lower() or 'access' in col.lower() or 'difficulty' in col.lower()])}")
        print(f"- Performance Variables: {len([col for col in self.df.columns if 'growth' in col.lower() or 'performance' in col.lower() or 'satisfaction' in col.lower()])}")
        
    def descriptive_statistics(self):
        """Generate descriptive statistics"""
        print("\n" + "="*80)
        print("DESCRIPTIVE STATISTICS")
        print("="*80)
        
        # Categorical variables
        print("\nCategorical Variables Summary:")
        categorical_vars = ['state', 'geo_political_zone', 'location_type', 'industry', 
                           'firm_age_category', 'employee_size_category', 'legal_structure',
                           'owner_gender', 'owner_education', 'owner_field_of_study']
        
        for var in categorical_vars:
            if var in self.df.columns:
                print(f"\n{var.upper()}:")
                print(self.df[var].value_counts().head())
        
        # Numeric variables
        print("\nNumeric Variables Summary:")
        numeric_vars = ['firm_age_years', 'num_employees', 'annual_turnover_ngn', 
                       'owner_age', 'digital_literacy_score', 'innovation_index',
                       'constraint_index', 'performance_index']
        
        print(self.df[numeric_vars].describe())
        
    def innovation_analysis(self):
        """Analyze innovation adoption patterns"""
        print("\n" + "="*80)
        print("INNOVATION ADOPTION ANALYSIS")
        print("="*80)
        
        # Innovation variables
        innovation_vars = ['digital_tools_adoption', 'advanced_tech_adoption', 
                          'level_of_digitization', 'process_innovation',
                          'product_service_innovation', 'business_model_innovation']
        
        print("\nInnovation Adoption by Industry:")
        industry_innovation = self.df.groupby('industry')[innovation_vars].mean().round(2)
        print(industry_innovation)
        
        print("\nInnovation Adoption by Location:")
        location_innovation = self.df.groupby('location_type')[innovation_vars].mean().round(2)
        print(location_innovation)
        
        print("\nInnovation Adoption by Firm Size:")
        size_innovation = self.df.groupby('employee_size_category')[innovation_vars].mean().round(2)
        print(size_innovation)
        
        # Innovation correlation matrix
        print("\nInnovation Variables Correlation Matrix:")
        innovation_corr = self.df[innovation_vars].corr().round(3)
        print(innovation_corr)
        
    def constraint_analysis(self):
        """Analyze constraint patterns"""
        print("\n" + "="*80)
        print("CONSTRAINT ANALYSIS")
        print("="*80)
        
        # Constraint variables by category
        financial_constraints = ['financial_constraints', 'access_to_credit', 
                                'cost_of_innovation', 'sufficiency_internal_capital']
        human_constraints = ['human_capital_constraints', 'skilled_employee_difficulty',
                            'cost_of_training', 'mgmt_capability_change']
        infrastructure_constraints = ['infrastructure_constraints', 'electricity_reliability',
                                     'internet_quality', 'internet_cost', 'logistics_access']
        
        print("\nFinancial Constraints by Firm Size:")
        print(self.df.groupby('employee_size_category')[financial_constraints].mean().round(2))
        
        print("\nInfrastructure Constraints by Location:")
        print(self.df.groupby('location_type')[infrastructure_constraints].mean().round(2))
        
        print("\nHuman Capital Constraints by Industry:")
        print(self.df.groupby('industry')[human_constraints].mean().round(2))
        
    def performance_analysis(self):
        """Analyze performance patterns"""
        print("\n" + "="*80)
        print("PERFORMANCE ANALYSIS")
        print("="*80)
        
        # Performance variables
        performance_vars = ['profitability_growth', 'sales_growth', 'market_share_growth',
                           'roi_satisfaction', 'overall_performance_satisfaction']
        
        print("\nPerformance by Innovation Level:")
        # Create innovation level categories
        self.df['innovation_level'] = pd.cut(self.df['innovation_index'], 
                                           bins=[0, 2, 3, 4, 5], 
                                           labels=['Low', 'Medium', 'High', 'Very High'])
        
        print(self.df.groupby('innovation_level')[performance_vars].mean().round(2))
        
        print("\nPerformance by Constraint Level:")
        # Create constraint level categories
        self.df['constraint_level'] = pd.cut(self.df['constraint_index'], 
                                            bins=[0, 2, 3, 4, 5], 
                                            labels=['Low', 'Medium', 'High', 'Very High'])
        
        print(self.df.groupby('constraint_level')[performance_vars].mean().round(2))
        
        print("\nTurnover Growth Distribution:")
        print(self.df['turnover_growth_range'].value_counts())
        
    def correlation_analysis(self):
        """Analyze correlations between key variables"""
        print("\n" + "="*80)
        print("CORRELATION ANALYSIS")
        print("="*80)
        
        # Key variables for correlation
        key_vars = ['innovation_index', 'constraint_index', 'performance_index',
                   'firm_age_years', 'num_employees', 'annual_turnover_ngn',
                   'owner_age', 'digital_literacy_score']
        
        correlation_matrix = self.df[key_vars].corr()
        print("\nKey Variables Correlation Matrix:")
        print(correlation_matrix.round(3))
        
        # Innovation-Performance correlation
        innovation_perf_corr = self.df['innovation_index'].corr(self.df['performance_index'])
        print(f"\nInnovation-Performance Correlation: {innovation_perf_corr:.3f}")
        
        # Constraint-Performance correlation
        constraint_perf_corr = self.df['constraint_index'].corr(self.df['performance_index'])
        print(f"Constraint-Performance Correlation: {constraint_perf_corr:.3f}")
        
    def clustering_analysis(self):
        """Perform clustering analysis"""
        print("\n" + "="*80)
        print("CLUSTERING ANALYSIS")
        print("="*80)
        
        # Prepare data for clustering
        cluster_vars = ['innovation_index', 'constraint_index', 'performance_index',
                       'firm_age_years', 'num_employees', 'digital_literacy_score']
        
        X = self.df[cluster_vars].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        self.df['cluster'] = clusters
        
        print("\nCluster Characteristics:")
        cluster_summary = self.df.groupby('cluster')[cluster_vars].mean().round(2)
        print(cluster_summary)
        
        print("\nCluster Distribution:")
        print(self.df['cluster'].value_counts().sort_index())
        
        # Cluster interpretation
        print("\nCluster Interpretation:")
        for i in range(4):
            cluster_data = self.df[self.df['cluster'] == i]
            avg_innovation = cluster_data['innovation_index'].mean()
            avg_constraint = cluster_data['constraint_index'].mean()
            avg_performance = cluster_data['performance_index'].mean()
            
            print(f"Cluster {i}: Innovation={avg_innovation:.2f}, "
                  f"Constraints={avg_constraint:.2f}, Performance={avg_performance:.2f}")
    
    def regression_analysis(self):
        """Perform regression analysis"""
        print("\n" + "="*80)
        print("REGRESSION ANALYSIS")
        print("="*80)
        
        # Prepare features and target
        feature_vars = ['innovation_index', 'constraint_index', 'firm_age_years', 
                       'num_employees', 'digital_literacy_score', 'owner_age']
        
        X = self.df[feature_vars].fillna(0)
        y = self.df['performance_index']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Linear Regression
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        lr_pred = lr.predict(X_test)
        lr_r2 = r2_score(y_test, lr_pred)
        
        print(f"Linear Regression R² Score: {lr_r2:.3f}")
        print("\nLinear Regression Coefficients:")
        for var, coef in zip(feature_vars, lr.coef_):
            print(f"{var}: {coef:.3f}")
        
        # Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)
        rf_r2 = r2_score(y_test, rf_pred)
        
        print(f"\nRandom Forest R² Score: {rf_r2:.3f}")
        print("\nRandom Forest Feature Importance:")
        for var, importance in zip(feature_vars, rf.feature_importances_):
            print(f"{var}: {importance:.3f}")
    
    def generate_insights(self):
        """Generate key insights from the analysis"""
        print("\n" + "="*80)
        print("KEY INSIGHTS AND RECOMMENDATIONS")
        print("="*80)
        
        # Innovation insights
        high_innovation = self.df[self.df['innovation_index'] > 3.5]
        low_innovation = self.df[self.df['innovation_index'] < 2.5]
        
        print("\n1. INNOVATION INSIGHTS:")
        print(f"   - {len(high_innovation)} firms have high innovation adoption (>{3.5})")
        print(f"   - {len(low_innovation)} firms have low innovation adoption (<{2.5})")
        print(f"   - Average innovation score: {self.df['innovation_index'].mean():.2f}")
        
        # Performance insights
        high_performance = self.df[self.df['performance_index'] > 3.5]
        low_performance = self.df[self.df['performance_index'] < 2.5]
        
        print("\n2. PERFORMANCE INSIGHTS:")
        print(f"   - {len(high_performance)} firms have high performance (>{3.5})")
        print(f"   - {len(low_performance)} firms have low performance (<{2.5})")
        print(f"   - Average performance score: {self.df['performance_index'].mean():.2f}")
        
        # Constraint insights
        high_constraints = self.df[self.df['constraint_index'] > 3.5]
        low_constraints = self.df[self.df['constraint_index'] < 2.5]
        
        print("\n3. CONSTRAINT INSIGHTS:")
        print(f"   - {len(high_constraints)} firms face high constraints (>{3.5})")
        print(f"   - {len(low_constraints)} firms face low constraints (<{2.5})")
        print(f"   - Average constraint score: {self.df['constraint_index'].mean():.2f}")
        
        # Industry insights
        print("\n4. INDUSTRY INSIGHTS:")
        industry_performance = self.df.groupby('industry')['performance_index'].mean().sort_values(ascending=False)
        print("   Top performing industries:")
        for industry, score in industry_performance.head(3).items():
            print(f"   - {industry}: {score:.2f}")
        
        # Geographic insights
        print("\n5. GEOGRAPHIC INSIGHTS:")
        zone_performance = self.df.groupby('geo_political_zone')['performance_index'].mean().sort_values(ascending=False)
        print("   Performance by geopolitical zone:")
        for zone, score in zone_performance.items():
            print(f"   - {zone}: {score:.2f}")
        
        # Recommendations
        print("\n6. RECOMMENDATIONS:")
        print("   - Focus on digital literacy training for SME owners")
        print("   - Improve infrastructure, especially in rural areas")
        print("   - Provide targeted support for high-constraint firms")
        print("   - Encourage innovation adoption through incentives")
        print("   - Address regulatory constraints for better business environment")
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("Starting comprehensive analysis of Nigerian SME Innovation Dataset...")
        
        self.basic_info()
        self.descriptive_statistics()
        self.innovation_analysis()
        self.constraint_analysis()
        self.performance_analysis()
        self.correlation_analysis()
        self.clustering_analysis()
        self.regression_analysis()
        self.generate_insights()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("The dataset is ready for advanced machine learning analysis!")
        print("Key areas for further research:")
        print("- Innovation adoption drivers and barriers")
        print("- Constraint impact on performance")
        print("- Policy recommendations for SME growth")
        print("- Regional development strategies")

def main():
    """Main function to run the analysis"""
    try:
        analyzer = SMEInnovationAnalyzer()
        analyzer.run_complete_analysis()
    except FileNotFoundError:
        print("Error: Dataset file not found. Please ensure 'nigerian_sme_innovation_dataset.csv' exists.")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()