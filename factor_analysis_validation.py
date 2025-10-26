#!/usr/bin/env python3
"""
Factor Analysis and Validation Scripts for Behavioral Intention Dataset

This script provides comprehensive factor analysis, reliability testing,
and validation procedures for the behavioral intention dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
import warnings
warnings.filterwarnings('ignore')

class BehavioralIntentionValidator:
    def __init__(self, df):
        """
        Initialize validator with the dataset
        
        Args:
            df (pd.DataFrame): The behavioral intention dataset
        """
        self.df = df
        self.scaler = StandardScaler()
        
    def test_data_quality(self):
        """Test basic data quality indicators"""
        print("=" * 60)
        print("DATA QUALITY ASSESSMENT")
        print("=" * 60)
        
        # Missing data analysis
        missing_data = self.df.isnull().sum()
        missing_pct = (missing_data / len(self.df)) * 100
        
        print("\nMissing Data Summary:")
        print("-" * 30)
        for col in missing_data.index:
            if missing_data[col] > 0:
                print(f"{col}: {missing_data[col]} ({missing_pct[col]:.2f}%)")
        
        # Response time analysis
        print(f"\nResponse Time Analysis:")
        print("-" * 30)
        print(f"Mean: {self.df['response_time_seconds'].mean():.2f} seconds")
        print(f"Median: {self.df['response_time_seconds'].median():.2f} seconds")
        print(f"Range: {self.df['response_time_seconds'].min():.2f} - {self.df['response_time_seconds'].max():.2f} seconds")
        
        # Straight-lining detection
        straight_line_count = self.df['straight_line_respondent'].sum()
        print(f"\nStraight-line Respondents: {straight_line_count} ({straight_line_count/len(self.df)*100:.2f}%)")
        
        # Outlier detection using IQR method
        likert_vars = ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 
                      'INT1', 'INT2', 'perceived_severity', 'perceived_vulnerability',
                      'self_efficacy', 'response_efficacy', 'past_behavior']
        
        outliers = 0
        for var in likert_vars:
            if var in self.df.columns:
                Q1 = self.df[var].quantile(0.25)
                Q3 = self.df[var].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                var_outliers = ((self.df[var] < lower_bound) | (self.df[var] > upper_bound)).sum()
                outliers += var_outliers
        
        print(f"Total Outliers Detected: {outliers}")
        
    def test_normality(self):
        """Test normality of variables"""
        print("\n" + "=" * 60)
        print("NORMALITY TESTS")
        print("=" * 60)
        
        likert_vars = ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 
                      'INT1', 'INT2', 'perceived_severity', 'perceived_vulnerability',
                      'self_efficacy', 'response_efficacy', 'past_behavior']
        
        print("\nShapiro-Wilk Test Results (p < 0.05 indicates non-normality):")
        print("-" * 60)
        
        for var in likert_vars:
            if var in self.df.columns:
                data = self.df[var].dropna()
                if len(data) > 3:  # Minimum sample size for Shapiro-Wilk
                    stat, p_value = stats.shapiro(data)
                    print(f"{var:20s}: W = {stat:.4f}, p = {p_value:.4f} {'*' if p_value < 0.05 else ''}")
    
    def test_reliability(self):
        """Test internal consistency reliability (Cronbach's Alpha)"""
        print("\n" + "=" * 60)
        print("RELIABILITY ANALYSIS (CRONBACH'S ALPHA)")
        print("=" * 60)
        
        # Define scale items
        scales = {
            'Attitude': ['ATT1', 'ATT2', 'ATT3'],
            'Subjective Norm': ['SN1', 'SN2'],
            'Perceived Behavioral Control': ['PBC1', 'PBC2', 'PBC3'],
            'Intention': ['INT1', 'INT2'],
            'Threat Appraisal': ['perceived_severity', 'perceived_vulnerability'],
            'Coping Appraisal': ['self_efficacy', 'response_efficacy']
        }
        
        def cronbach_alpha(df, items):
            """Calculate Cronbach's alpha for a set of items"""
            items_df = df[items].dropna()
            if len(items_df) < 2:
                return np.nan, np.nan
            
            # Calculate item variances
            item_variances = items_df.var(axis=0, ddof=1)
            
            # Calculate total variance
            total_variance = items_df.sum(axis=1).var(ddof=1)
            
            # Calculate number of items
            k = len(items)
            
            # Calculate Cronbach's alpha
            alpha = (k / (k - 1)) * (1 - (item_variances.sum() / total_variance))
            
            # Calculate confidence interval (simplified)
            n = len(items_df)
            se = np.sqrt((2 * k) / ((k - 1) * n))
            ci_lower = alpha - 1.96 * se
            ci_upper = alpha + 1.96 * se
            
            return alpha, (ci_lower, ci_upper)
        
        print("\nCronbach's Alpha Results:")
        print("-" * 40)
        print(f"{'Scale':<25} {'Alpha':<8} {'95% CI':<15} {'Interpretation'}")
        print("-" * 70)
        
        for scale_name, items in scales.items():
            alpha, ci = cronbach_alpha(self.df, items)
            if not np.isnan(alpha):
                interpretation = "Excellent" if alpha >= 0.9 else "Good" if alpha >= 0.8 else "Acceptable" if alpha >= 0.7 else "Questionable" if alpha >= 0.6 else "Poor"
                print(f"{scale_name:<25} {alpha:<8.3f} {f'[{ci[0]:.3f}, {ci[1]:.3f}]':<15} {interpretation}")
            else:
                print(f"{scale_name:<25} {'N/A':<8} {'N/A':<15} {'Insufficient Data'}")
    
    def test_factorability(self):
        """Test factorability of the data"""
        print("\n" + "=" * 60)
        print("FACTORABILITY TESTS")
        print("=" * 60)
        
        # Prepare data for factor analysis
        likert_vars = ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 
                      'INT1', 'INT2', 'perceived_severity', 'perceived_vulnerability',
                      'self_efficacy', 'response_efficacy', 'past_behavior']
        
        fa_data = self.df[likert_vars].dropna()
        
        print(f"\nSample size for factor analysis: {len(fa_data)}")
        print(f"Number of variables: {len(likert_vars)}")
        print(f"Sample to variable ratio: {len(fa_data)/len(likert_vars):.2f}")
        
        # Kaiser-Meyer-Olkin (KMO) test
        try:
            kmo_all, kmo_model = calculate_kmo(fa_data)
            print(f"\nKaiser-Meyer-Olkin (KMO) Test:")
            print(f"Overall KMO: {kmo_model:.3f}")
            print("KMO Interpretation: ", end="")
            if kmo_model >= 0.9:
                print("Marvelous")
            elif kmo_model >= 0.8:
                print("Meritorious")
            elif kmo_model >= 0.7:
                print("Middling")
            elif kmo_model >= 0.6:
                print("Mediocre")
            elif kmo_model >= 0.5:
                print("Miserable")
            else:
                print("Unacceptable")
        except Exception as e:
            print(f"KMO test failed: {e}")
        
        # Bartlett's test of sphericity
        try:
            chi_square_value, p_value = calculate_bartlett_sphericity(fa_data)
            print(f"\nBartlett's Test of Sphericity:")
            print(f"Chi-square: {chi_square_value:.3f}")
            print(f"p-value: {p_value:.6f}")
            print("Interpretation: ", end="")
            if p_value < 0.001:
                print("Data is suitable for factor analysis (p < 0.001)")
            else:
                print("Data may not be suitable for factor analysis")
        except Exception as e:
            print(f"Bartlett's test failed: {e}")
    
    def perform_exploratory_factor_analysis(self):
        """Perform exploratory factor analysis"""
        print("\n" + "=" * 60)
        print("EXPLORATORY FACTOR ANALYSIS")
        print("=" * 60)
        
        # Prepare data
        likert_vars = ['ATT1', 'ATT2', 'ATT3', 'SN1', 'SN2', 'PBC1', 'PBC2', 'PBC3', 
                      'INT1', 'INT2', 'perceived_severity', 'perceived_vulnerability',
                      'self_efficacy', 'response_efficacy', 'past_behavior']
        
        fa_data = self.df[likert_vars].dropna()
        
        # Standardize data
        fa_data_scaled = self.scaler.fit_transform(fa_data)
        
        # Determine number of factors using parallel analysis
        print("\nDetermining number of factors...")
        
        # Kaiser criterion (eigenvalues > 1)
        fa = FactorAnalyzer(n_factors=len(likert_vars), rotation=None)
        fa.fit(fa_data_scaled)
        eigenvalues = fa.get_eigenvalues()[0]
        kaiser_factors = sum(eigenvalues > 1)
        print(f"Kaiser criterion (eigenvalues > 1): {kaiser_factors} factors")
        
        # Scree plot analysis
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(eigenvalues) + 1), eigenvalues, 'bo-')
        plt.axhline(y=1, color='r', linestyle='--', label='Kaiser criterion')
        plt.xlabel('Factor Number')
        plt.ylabel('Eigenvalue')
        plt.title('Scree Plot for Factor Analysis')
        plt.legend()
        plt.grid(True)
        plt.savefig('scree_plot.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Perform EFA with different numbers of factors
        for n_factors in [3, 4, 5, 6]:
            print(f"\n--- EFA with {n_factors} factors ---")
            fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax')
            fa.fit(fa_data_scaled)
            
            # Get factor loadings
            loadings = fa.loadings_
            
            # Create loadings dataframe
            loadings_df = pd.DataFrame(
                loadings,
                columns=[f'Factor_{i+1}' for i in range(n_factors)],
                index=likert_vars
            )
            
            print(f"\nFactor Loadings (n_factors={n_factors}):")
            print(loadings_df.round(3))
            
            # Calculate variance explained
            variance_explained = fa.get_eigenvalues()[1]
            print(f"\nVariance Explained by each factor:")
            for i, var in enumerate(variance_explained):
                print(f"Factor {i+1}: {var:.3f} ({var*100:.1f}%)")
            print(f"Total variance explained: {sum(variance_explained):.3f} ({sum(variance_explained)*100:.1f}%)")
    
    def perform_confirmatory_factor_analysis(self):
        """Perform confirmatory factor analysis for theoretical constructs"""
        print("\n" + "=" * 60)
        print("CONFIRMATORY FACTOR ANALYSIS")
        print("=" * 60)
        
        # Define theoretical factor structure
        theoretical_factors = {
            'Attitude': ['ATT1', 'ATT2', 'ATT3'],
            'Subjective_Norm': ['SN1', 'SN2'],
            'Perceived_Behavioral_Control': ['PBC1', 'PBC2', 'PBC3'],
            'Intention': ['INT1', 'INT2'],
            'Threat_Appraisal': ['perceived_severity', 'perceived_vulnerability'],
            'Coping_Appraisal': ['self_efficacy', 'response_efficacy']
        }
        
        print("Theoretical Factor Structure:")
        print("-" * 40)
        for factor, items in theoretical_factors.items():
            print(f"{factor}: {', '.join(items)}")
        
        # Test each theoretical factor
        print(f"\nFactor Analysis Results for Each Theoretical Construct:")
        print("-" * 60)
        
        for factor_name, items in theoretical_factors.items():
            if len(items) >= 2:  # Need at least 2 items for factor analysis
                print(f"\n{factor_name}:")
                print("-" * len(factor_name))
                
                # Get data for this factor
                factor_data = self.df[items].dropna()
                
                if len(factor_data) > 0:
                    # Standardize
                    factor_data_scaled = self.scaler.fit_transform(factor_data)
                    
                    # Single factor analysis
                    fa = FactorAnalyzer(n_factors=1, rotation=None)
                    fa.fit(factor_data_scaled)
                    
                    # Get loadings
                    loadings = fa.loadings_[:, 0]
                    
                    print("Factor Loadings:")
                    for item, loading in zip(items, loadings):
                        print(f"  {item}: {loading:.3f}")
                    
                    # Calculate reliability
                    from factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
                    try:
                        kmo_all, kmo_model = calculate_kmo(factor_data)
                        print(f"KMO: {kmo_model:.3f}")
                    except:
                        print("KMO: Could not calculate")
    
    def test_theoretical_relationships(self):
        """Test theoretical relationships between constructs"""
        print("\n" + "=" * 60)
        print("THEORETICAL RELATIONSHIPS TESTING")
        print("=" * 60)
        
        # Create composite scores if not already present
        if 'attitude_composite' not in self.df.columns:
            self.df['attitude_composite'] = self.df[['ATT1', 'ATT2', 'ATT3']].mean(axis=1)
        if 'subjective_norm_composite' not in self.df.columns:
            self.df['subjective_norm_composite'] = self.df[['SN1', 'SN2']].mean(axis=1)
        if 'pbc_composite' not in self.df.columns:
            self.df['pbc_composite'] = self.df[['PBC1', 'PBC2', 'PBC3']].mean(axis=1)
        if 'intention_composite' not in self.df.columns:
            self.df['intention_composite'] = self.df[['INT1', 'INT2']].mean(axis=1)
        if 'threat_appraisal_composite' not in self.df.columns:
            self.df['threat_appraisal_composite'] = self.df[['perceived_severity', 'perceived_vulnerability']].mean(axis=1)
        if 'coping_appraisal_composite' not in self.df.columns:
            self.df['coping_appraisal_composite'] = self.df[['self_efficacy', 'response_efficacy']].mean(axis=1)
        
        # Test TPB relationships
        print("\nTheory of Planned Behavior Relationships:")
        print("-" * 45)
        
        # Get common indices for all variables
        common_idx = self.df[['attitude_composite', 'subjective_norm_composite', 
                             'pbc_composite', 'intention_composite']].dropna().index
        
        # Attitude -> Intention
        corr_att_int, p_att_int = stats.pearsonr(
            self.df.loc[common_idx, 'attitude_composite'], 
            self.df.loc[common_idx, 'intention_composite']
        )
        print(f"Attitude -> Intention: r = {corr_att_int:.3f}, p = {p_att_int:.6f}")
        
        # Subjective Norm -> Intention
        corr_sn_int, p_sn_int = stats.pearsonr(
            self.df.loc[common_idx, 'subjective_norm_composite'], 
            self.df.loc[common_idx, 'intention_composite']
        )
        print(f"Subjective Norm -> Intention: r = {corr_sn_int:.3f}, p = {p_sn_int:.6f}")
        
        # PBC -> Intention
        corr_pbc_int, p_pbc_int = stats.pearsonr(
            self.df.loc[common_idx, 'pbc_composite'], 
            self.df.loc[common_idx, 'intention_composite']
        )
        print(f"PBC -> Intention: r = {corr_pbc_int:.3f}, p = {p_pbc_int:.6f}")
        
        # Intention -> Behavior (T2)
        if 'T2_security_steps_followed' in self.df.columns:
            t2_data = self.df[['intention_composite', 'T2_security_steps_followed']].dropna()
            if len(t2_data) > 0:
                corr_int_beh, p_int_beh = stats.pearsonr(
                    t2_data['intention_composite'], 
                    t2_data['T2_security_steps_followed']
                )
                print(f"Intention -> Behavior (T2): r = {corr_int_beh:.3f}, p = {p_int_beh:.6f}")
        
        # Test PMT relationships
        print(f"\nProtection Motivation Theory Relationships:")
        print("-" * 45)
        
        # Get common indices for PMT variables
        pmt_common_idx = self.df[['threat_appraisal_composite', 'coping_appraisal_composite',
                                 'past_behavior', 'intention_composite']].dropna().index
        
        # Threat Appraisal -> Intention
        corr_threat_int, p_threat_int = stats.pearsonr(
            self.df.loc[pmt_common_idx, 'threat_appraisal_composite'], 
            self.df.loc[pmt_common_idx, 'intention_composite']
        )
        print(f"Threat Appraisal -> Intention: r = {corr_threat_int:.3f}, p = {p_threat_int:.6f}")
        
        # Coping Appraisal -> Intention
        corr_coping_int, p_coping_int = stats.pearsonr(
            self.df.loc[pmt_common_idx, 'coping_appraisal_composite'], 
            self.df.loc[pmt_common_idx, 'intention_composite']
        )
        print(f"Coping Appraisal -> Intention: r = {corr_coping_int:.3f}, p = {p_coping_int:.6f}")
        
        # Past Behavior -> Intention
        corr_past_int, p_past_int = stats.pearsonr(
            self.df.loc[pmt_common_idx, 'past_behavior'], 
            self.df.loc[pmt_common_idx, 'intention_composite']
        )
        print(f"Past Behavior -> Intention: r = {corr_past_int:.3f}, p = {p_past_int:.6f}")
    
    def generate_correlation_matrix(self):
        """Generate and visualize correlation matrix"""
        print("\n" + "=" * 60)
        print("CORRELATION MATRIX")
        print("=" * 60)
        
        # Select key variables for correlation matrix
        key_vars = [
            'attitude_composite', 'subjective_norm_composite', 'pbc_composite',
            'intention_composite', 'threat_appraisal_composite', 'coping_appraisal_composite',
            'past_behavior', 'T2_security_steps_followed'
        ]
        
        # Filter to available variables
        available_vars = [var for var in key_vars if var in self.df.columns]
        corr_data = self.df[available_vars].dropna()
        
        if len(corr_data) > 0:
            # Calculate correlation matrix
            corr_matrix = corr_data.corr()
            
            # Create heatmap
            plt.figure(figsize=(12, 10))
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
            plt.title('Correlation Matrix of Key Constructs')
            plt.tight_layout()
            plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("\nCorrelation Matrix:")
            print(corr_matrix.round(3))
    
    def run_full_validation(self):
        """Run complete validation suite"""
        print("BEHAVIORAL INTENTION DATASET VALIDATION")
        print("=" * 60)
        
        self.test_data_quality()
        self.test_normality()
        self.test_reliability()
        self.test_factorability()
        self.perform_exploratory_factor_analysis()
        self.perform_confirmatory_factor_analysis()
        self.test_theoretical_relationships()
        self.generate_correlation_matrix()
        
        print("\n" + "=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        print("All validation tests have been completed.")
        print("Check the generated plots and statistics above for results.")

def main():
    """Main function to run validation"""
    # Load the dataset
    try:
        df = pd.read_csv('behavioral_intention_dataset.csv')
        print(f"Dataset loaded successfully. Shape: {df.shape}")
    except FileNotFoundError:
        print("Dataset file not found. Please run the dataset generator first.")
        return
    
    # Run validation
    validator = BehavioralIntentionValidator(df)
    validator.run_full_validation()

if __name__ == "__main__":
    main()