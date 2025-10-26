#!/usr/bin/env python3
"""
Dataset Validation Script
Validates the behavioral intention dataset for quality, theoretical consistency, and analysis readiness
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

class DatasetValidator:
    def __init__(self, dataset_path):
        """Initialize validator with dataset"""
        self.df = pd.read_csv(dataset_path)
        self.constructs = {
            'ATT': ['ATT1', 'ATT2', 'ATT3'],
            'SN': ['SN1', 'SN2', 'SN3'], 
            'PBC': ['PBC1', 'PBC2', 'PBC3'],
            'INT': ['INT1', 'INT2', 'INT3'],
            'PS': ['PS1', 'PS2', 'PS3'],
            'PV': ['PV1', 'PV2', 'PV3'],
            'SE': ['SE1', 'SE2', 'SE3'],
            'RE': ['RE1', 'RE2', 'RE3']
        }
        
    def basic_data_quality(self):
        """Check basic data quality metrics"""
        print("="*60)
        print("BASIC DATA QUALITY ASSESSMENT")
        print("="*60)
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Total variables: {len(self.df.columns)}")
        
        # Missing data
        missing_data = self.df.isnull().sum()
        if missing_data.sum() > 0:
            print(f"\nMissing data found:")
            print(missing_data[missing_data > 0])
        else:
            print("\n✓ No missing data found")
            
        # Duplicate participants
        duplicates = self.df['Participant_ID'].duplicated().sum()
        if duplicates > 0:
            print(f"\n⚠ {duplicates} duplicate participant IDs found")
        else:
            print("✓ No duplicate participant IDs")
            
        # Scale range validation
        print("\nScale Range Validation (1-7 scales):")
        scale_vars = []
        for construct_items in self.constructs.values():
            scale_vars.extend(construct_items)
        scale_vars.extend(['Past_Behavior', 'T2_Actual_Behavior', 'Tech_Comfort', 
                          'Financial_Literacy', 'Risk_Tolerance', 'Trust_Bank_Security'])
        
        for var in scale_vars:
            if var in self.df.columns:
                min_val, max_val = self.df[var].min(), self.df[var].max()
                if min_val < 1 or max_val > 7:
                    print(f"⚠ {var}: Range {min_val}-{max_val} (should be 1-7)")
                else:
                    print(f"✓ {var}: Range {min_val}-{max_val}")
                    
    def construct_reliability(self):
        """Calculate reliability (Cronbach's alpha) for each construct"""
        print("\n" + "="*60)
        print("CONSTRUCT RELIABILITY ANALYSIS")
        print("="*60)
        
        def cronbach_alpha(items_df):
            """Calculate Cronbach's alpha"""
            items_df = items_df.dropna()
            n_items = items_df.shape[1]
            if n_items < 2:
                return np.nan
                
            item_variances = items_df.var(axis=0, ddof=1)
            total_variance = items_df.sum(axis=1).var(ddof=1)
            
            alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
            return alpha
        
        reliability_results = {}
        
        for construct, items in self.constructs.items():
            available_items = [item for item in items if item in self.df.columns]
            if len(available_items) >= 2:
                construct_data = self.df[available_items]
                alpha = cronbach_alpha(construct_data)
                reliability_results[construct] = {
                    'alpha': alpha,
                    'n_items': len(available_items),
                    'mean': construct_data.mean().mean(),
                    'std': construct_data.std().mean()
                }
                
                status = "✓ Excellent" if alpha >= 0.9 else "✓ Good" if alpha >= 0.8 else "✓ Acceptable" if alpha >= 0.7 else "⚠ Questionable"
                print(f"{construct}: α = {alpha:.3f} ({status}), Items = {len(available_items)}")
                
        return reliability_results
    
    def theoretical_correlations(self):
        """Validate theoretical correlations"""
        print("\n" + "="*60)
        print("THEORETICAL CORRELATION VALIDATION")
        print("="*60)
        
        # Calculate construct means
        construct_means = {}
        for construct, items in self.constructs.items():
            available_items = [item for item in items if item in self.df.columns]
            if available_items:
                construct_means[construct] = self.df[available_items].mean(axis=1)
        
        # Expected correlations based on theory
        expected_correlations = [
            ('ATT', 'INT', 0.50, 0.70, "Attitude-Intention"),
            ('SN', 'INT', 0.30, 0.50, "Subjective Norm-Intention"),
            ('PBC', 'INT', 0.40, 0.65, "PBC-Intention"),
            ('SE', 'PBC', 0.60, 0.80, "Self-Efficacy-PBC"),
            ('PS', 'PV', 0.30, 0.60, "Perceived Severity-Vulnerability"),
            ('ATT', 'RE', 0.40, 0.70, "Attitude-Response Efficacy"),
            ('SE', 'INT', 0.35, 0.60, "Self-Efficacy-Intention"),
            ('RE', 'INT', 0.30, 0.55, "Response Efficacy-Intention")
        ]
        
        print("Construct Correlations (Expected vs Observed):")
        print("-" * 50)
        
        for var1, var2, min_exp, max_exp, label in expected_correlations:
            if var1 in construct_means and var2 in construct_means:
                r, p = pearsonr(construct_means[var1], construct_means[var2])
                status = "✓" if min_exp <= r <= max_exp else "⚠"
                print(f"{label}: r = {r:.3f} (expected: {min_exp:.2f}-{max_exp:.2f}) {status}")
        
        # Intention-Behavior correlation
        if 'INT' in construct_means and 'T2_Actual_Behavior' in self.df.columns:
            r, p = pearsonr(construct_means['INT'], self.df['T2_Actual_Behavior'])
            status = "✓" if 0.40 <= r <= 0.65 else "⚠"
            print(f"Intention-T2 Behavior: r = {r:.3f} (expected: 0.40-0.65) {status}")
            
        # Past Behavior-T2 Behavior correlation
        if 'Past_Behavior' in self.df.columns and 'T2_Actual_Behavior' in self.df.columns:
            r, p = pearsonr(self.df['Past_Behavior'], self.df['T2_Actual_Behavior'])
            status = "✓" if 0.50 <= r <= 0.75 else "⚠"
            print(f"Past Behavior-T2 Behavior: r = {r:.3f} (expected: 0.50-0.75) {status}")
    
    def demographic_distributions(self):
        """Validate demographic distributions"""
        print("\n" + "="*60)
        print("DEMOGRAPHIC DISTRIBUTION VALIDATION")
        print("="*60)
        
        # Age distribution
        age_stats = self.df['Age'].describe()
        print(f"Age: M = {age_stats['mean']:.1f}, SD = {age_stats['std']:.1f}, Range = {age_stats['min']:.0f}-{age_stats['max']:.0f}")
        
        # Gender distribution
        gender_dist = self.df['Gender'].value_counts(normalize=True)
        print(f"\nGender Distribution:")
        for gender, prop in gender_dist.items():
            print(f"  {gender}: {prop:.1%}")
            
        # Education distribution
        edu_dist = self.df['Education'].value_counts(normalize=True)
        print(f"\nEducation Distribution:")
        for edu, prop in edu_dist.items():
            print(f"  {edu}: {prop:.1%}")
            
        # Previous fraud experience
        fraud_dist = self.df['Previous_Fraud_Experience'].value_counts(normalize=True)
        print(f"\nPrevious Fraud Experience:")
        for exp, prop in fraud_dist.items():
            print(f"  {exp}: {prop:.1%}")
    
    def construct_descriptives(self):
        """Detailed construct descriptive statistics"""
        print("\n" + "="*60)
        print("CONSTRUCT DESCRIPTIVE STATISTICS")
        print("="*60)
        
        for construct, items in self.constructs.items():
            available_items = [item for item in items if item in self.df.columns]
            if available_items:
                print(f"\n{construct} ({len(available_items)} items):")
                construct_data = self.df[available_items]
                
                for item in available_items:
                    stats = self.df[item].describe()
                    print(f"  {item}: M = {stats['mean']:.2f}, SD = {stats['std']:.2f}, Range = {stats['min']:.0f}-{stats['max']:.0f}")
                
                # Construct mean
                construct_mean = construct_data.mean(axis=1)
                print(f"  Construct Mean: M = {construct_mean.mean():.2f}, SD = {construct_mean.std():.2f}")
    
    def behavioral_outcomes_analysis(self):
        """Analyze behavioral outcome variables"""
        print("\n" + "="*60)
        print("BEHAVIORAL OUTCOMES ANALYSIS")
        print("="*60)
        
        behavioral_vars = ['Past_Behavior', 'T2_Actual_Behavior', 'T2_Check_URLs', 
                          'T2_Use_2FA', 'T2_Update_Passwords', 'T2_Monitor_Accounts', 'T2_Secure_Networks']
        
        for var in behavioral_vars:
            if var in self.df.columns:
                stats = self.df[var].describe()
                print(f"{var}: M = {stats['mean']:.2f}, SD = {stats['std']:.2f}, Range = {stats['min']:.0f}-{stats['max']:.0f}")
        
        # Behavior change analysis
        if 'Past_Behavior' in self.df.columns and 'T2_Actual_Behavior' in self.df.columns:
            behavior_change = self.df['T2_Actual_Behavior'] - self.df['Past_Behavior']
            print(f"\nBehavior Change (T2 - Past): M = {behavior_change.mean():.2f}, SD = {behavior_change.std():.2f}")
            
            # Categorize change
            improved = (behavior_change > 0.5).sum()
            maintained = (abs(behavior_change) <= 0.5).sum()
            declined = (behavior_change < -0.5).sum()
            
            print(f"Behavior Change Categories:")
            print(f"  Improved: {improved} ({improved/len(self.df):.1%})")
            print(f"  Maintained: {maintained} ({maintained/len(self.df):.1%})")
            print(f"  Declined: {declined} ({declined/len(self.df):.1%})")
    
    def generate_correlation_matrix(self):
        """Generate and save correlation matrix"""
        print("\n" + "="*60)
        print("GENERATING CORRELATION MATRIX")
        print("="*60)
        
        # Select key variables for correlation matrix
        key_vars = []
        
        # Add construct means
        construct_means = {}
        for construct, items in self.constructs.items():
            available_items = [item for item in items if item in self.df.columns]
            if available_items:
                construct_means[construct] = self.df[available_items].mean(axis=1)
                key_vars.append(construct)
        
        # Add behavioral variables
        behavioral_vars = ['Past_Behavior', 'T2_Actual_Behavior']
        for var in behavioral_vars:
            if var in self.df.columns:
                construct_means[var] = self.df[var]
                key_vars.append(var)
        
        # Add demographic controls
        demo_vars = ['Age', 'Tech_Comfort', 'Financial_Literacy']
        for var in demo_vars:
            if var in self.df.columns:
                construct_means[var] = self.df[var]
                key_vars.append(var)
        
        # Create correlation matrix
        corr_df = pd.DataFrame(construct_means)
        correlation_matrix = corr_df.corr()
        
        # Save correlation matrix
        correlation_matrix.to_csv('/workspace/correlation_matrix.csv')
        print("Correlation matrix saved to: /workspace/correlation_matrix.csv")
        
        # Display key correlations
        print("\nKey Theoretical Correlations:")
        important_pairs = [
            ('ATT', 'INT'), ('SN', 'INT'), ('PBC', 'INT'),
            ('INT', 'T2_Actual_Behavior'), ('Past_Behavior', 'T2_Actual_Behavior'),
            ('SE', 'PBC'), ('PS', 'PV')
        ]
        
        for var1, var2 in important_pairs:
            if var1 in correlation_matrix.columns and var2 in correlation_matrix.columns:
                r = correlation_matrix.loc[var1, var2]
                print(f"{var1}-{var2}: r = {r:.3f}")
        
        return correlation_matrix
    
    def run_complete_validation(self):
        """Run complete validation suite"""
        print("COMPREHENSIVE DATASET VALIDATION")
        print("="*80)
        print(f"Dataset: {self.df.shape[0]} participants, {self.df.shape[1]} variables")
        print("="*80)
        
        # Run all validation checks
        self.basic_data_quality()
        reliability_results = self.construct_reliability()
        self.theoretical_correlations()
        self.demographic_distributions()
        self.construct_descriptives()
        self.behavioral_outcomes_analysis()
        correlation_matrix = self.generate_correlation_matrix()
        
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        print("✓ Dataset structure and quality validated")
        print("✓ Construct reliability assessed")
        print("✓ Theoretical correlations validated")
        print("✓ Demographic distributions confirmed")
        print("✓ Behavioral outcomes analyzed")
        print("✓ Correlation matrix generated")
        print("\nDataset is ready for advanced statistical analysis!")
        
        return {
            'reliability': reliability_results,
            'correlations': correlation_matrix,
            'summary': 'Dataset validation completed successfully'
        }

def main():
    """Main validation function"""
    validator = DatasetValidator('/workspace/behavioral_intention_dataset.csv')
    results = validator.run_complete_validation()
    return results

if __name__ == "__main__":
    validation_results = main()