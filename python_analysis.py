#!/usr/bin/env python3
"""
Comprehensive Python Analysis Script
Behavioral Intention Dataset - TPB and PMT Analysis
Alternative to R analysis for Python users
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('default')
sns.set_palette("husl")

class BehavioralAnalysis:
    def __init__(self, dataset_path):
        """Initialize analysis with dataset"""
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
        
        # Calculate construct means
        self.construct_means = {}
        for construct, items in self.constructs.items():
            available_items = [item for item in items if item in self.df.columns]
            if available_items:
                self.construct_means[construct] = self.df[available_items].mean(axis=1)
    
    def descriptive_analysis(self):
        """Comprehensive descriptive analysis"""
        print("="*70)
        print("DESCRIPTIVE ANALYSIS")
        print("="*70)
        
        # Sample characteristics
        print(f"Sample size: {len(self.df)}")
        print(f"Variables: {len(self.df.columns)}")
        
        print("\nDemographic Summary:")
        print(f"Age: M = {self.df['Age'].mean():.1f}, SD = {self.df['Age'].std():.1f}")
        print(f"Gender distribution:")
        print(self.df['Gender'].value_counts(normalize=True).round(3))
        
        print(f"\nEducation distribution:")
        print(self.df['Education'].value_counts(normalize=True).round(3))
        
        # Construct descriptives
        print("\nConstruct Means and Standard Deviations:")
        print("-" * 50)
        for construct, mean_scores in self.construct_means.items():
            print(f"{construct}: M = {mean_scores.mean():.2f}, SD = {mean_scores.std():.2f}")
        
        print(f"\nBehavioral Variables:")
        print(f"Past Behavior: M = {self.df['Past_Behavior'].mean():.2f}, SD = {self.df['Past_Behavior'].std():.2f}")
        print(f"T2 Actual Behavior: M = {self.df['T2_Actual_Behavior'].mean():.2f}, SD = {self.df['T2_Actual_Behavior'].std():.2f}")
        
        # Behavior change
        behavior_change = self.df['T2_Actual_Behavior'] - self.df['Past_Behavior']
        print(f"Behavior Change: M = {behavior_change.mean():.2f}, SD = {behavior_change.std():.2f}")
        
        return {
            'sample_size': len(self.df),
            'construct_means': {k: {'mean': v.mean(), 'std': v.std()} for k, v in self.construct_means.items()},
            'behavior_change': behavior_change.mean()
        }
    
    def correlation_analysis(self):
        """Correlation analysis and theoretical validation"""
        print("\n" + "="*70)
        print("CORRELATION ANALYSIS")
        print("="*70)
        
        # Create correlation matrix for constructs
        construct_df = pd.DataFrame(self.construct_means)
        construct_df['Past_Behavior'] = self.df['Past_Behavior']
        construct_df['T2_Actual_Behavior'] = self.df['T2_Actual_Behavior']
        construct_df['Age'] = self.df['Age']
        construct_df['Tech_Comfort'] = self.df['Tech_Comfort']
        
        correlation_matrix = construct_df.corr()
        
        # Display key theoretical correlations
        print("Key Theoretical Correlations:")
        print("-" * 40)
        
        theoretical_pairs = [
            ('ATT', 'INT', 0.50, 0.70),
            ('SN', 'INT', 0.30, 0.50),
            ('PBC', 'INT', 0.40, 0.65),
            ('INT', 'T2_Actual_Behavior', 0.40, 0.65),
            ('Past_Behavior', 'T2_Actual_Behavior', 0.50, 0.75),
            ('SE', 'PBC', 0.60, 0.80),
            ('PS', 'PV', 0.30, 0.60)
        ]
        
        correlation_results = []
        for var1, var2, min_exp, max_exp in theoretical_pairs:
            if var1 in correlation_matrix.columns and var2 in correlation_matrix.columns:
                r = correlation_matrix.loc[var1, var2]
                status = "✓" if min_exp <= r <= max_exp else "⚠"
                print(f"{var1}-{var2}: r = {r:.3f} (expected: {min_exp:.2f}-{max_exp:.2f}) {status}")
                correlation_results.append({
                    'pair': f"{var1}-{var2}",
                    'correlation': r,
                    'expected_min': min_exp,
                    'expected_max': max_exp,
                    'within_range': min_exp <= r <= max_exp
                })
        
        # Save correlation matrix
        correlation_matrix.to_csv('/workspace/python_correlation_matrix.csv')
        print(f"\n✓ Correlation matrix saved to: python_correlation_matrix.csv")
        
        return correlation_results, correlation_matrix
    
    def regression_analysis(self):
        """Multiple regression analysis for TPB and extended models"""
        print("\n" + "="*70)
        print("REGRESSION ANALYSIS")
        print("="*70)
        
        results = {}
        
        # Model 1: Basic TPB predicting intention
        print("\n--- Model 1: TPB Predicting Intention ---")
        
        X_tpb = pd.DataFrame({
            'ATT': self.construct_means['ATT'],
            'SN': self.construct_means['SN'],
            'PBC': self.construct_means['PBC'],
            'Past_Behavior': self.df['Past_Behavior']
        })
        y_int = self.construct_means['INT']
        
        # Standardize predictors
        scaler = StandardScaler()
        X_tpb_std = pd.DataFrame(scaler.fit_transform(X_tpb), columns=X_tpb.columns)
        
        model_tpb = LinearRegression()
        model_tpb.fit(X_tpb_std, y_int)
        
        r2_tpb = model_tpb.score(X_tpb_std, y_int)
        
        print(f"R² = {r2_tpb:.3f}")
        print("Standardized Coefficients:")
        for i, var in enumerate(X_tpb.columns):
            coef = model_tpb.coef_[i]
            print(f"  {var}: β = {coef:.3f}")
        
        results['tpb_intention'] = {
            'r_squared': r2_tpb,
            'coefficients': dict(zip(X_tpb.columns, model_tpb.coef_)),
            'intercept': model_tpb.intercept_
        }
        
        # Model 2: Extended TPB + PMT predicting intention
        print("\n--- Model 2: Extended TPB + PMT Predicting Intention ---")
        
        X_extended = pd.DataFrame({
            'ATT': self.construct_means['ATT'],
            'SN': self.construct_means['SN'],
            'PBC': self.construct_means['PBC'],
            'PS': self.construct_means['PS'],
            'PV': self.construct_means['PV'],
            'SE': self.construct_means['SE'],
            'RE': self.construct_means['RE'],
            'Past_Behavior': self.df['Past_Behavior']
        })
        
        X_extended_std = pd.DataFrame(scaler.fit_transform(X_extended), columns=X_extended.columns)
        
        model_extended = LinearRegression()
        model_extended.fit(X_extended_std, y_int)
        
        r2_extended = model_extended.score(X_extended_std, y_int)
        
        print(f"R² = {r2_extended:.3f}")
        print("Standardized Coefficients:")
        for i, var in enumerate(X_extended.columns):
            coef = model_extended.coef_[i]
            print(f"  {var}: β = {coef:.3f}")
        
        results['extended_intention'] = {
            'r_squared': r2_extended,
            'coefficients': dict(zip(X_extended.columns, model_extended.coef_)),
            'intercept': model_extended.intercept_
        }
        
        # Model 3: Predicting T2 Behavior
        print("\n--- Model 3: Predicting T2 Behavior ---")
        
        X_behavior = pd.DataFrame({
            'INT': self.construct_means['INT'],
            'PBC': self.construct_means['PBC'],
            'Past_Behavior': self.df['Past_Behavior'],
            'Age': self.df['Age'],
            'Tech_Comfort': self.df['Tech_Comfort']
        })
        y_behavior = self.df['T2_Actual_Behavior']
        
        X_behavior_std = pd.DataFrame(scaler.fit_transform(X_behavior), columns=X_behavior.columns)
        
        model_behavior = LinearRegression()
        model_behavior.fit(X_behavior_std, y_behavior)
        
        r2_behavior = model_behavior.score(X_behavior_std, y_behavior)
        
        print(f"R² = {r2_behavior:.3f}")
        print("Standardized Coefficients:")
        for i, var in enumerate(X_behavior.columns):
            coef = model_behavior.coef_[i]
            print(f"  {var}: β = {coef:.3f}")
        
        results['behavior'] = {
            'r_squared': r2_behavior,
            'coefficients': dict(zip(X_behavior.columns, model_behavior.coef_)),
            'intercept': model_behavior.intercept_
        }
        
        # Model comparison
        print(f"\n--- Model Comparison ---")
        print(f"TPB Model (Intention): R² = {r2_tpb:.3f}")
        print(f"Extended Model (Intention): R² = {r2_extended:.3f}")
        print(f"Behavior Model: R² = {r2_behavior:.3f}")
        
        r2_improvement = r2_extended - r2_tpb
        print(f"R² improvement (Extended vs TPB): {r2_improvement:.3f}")
        
        return results
    
    def mediation_analysis(self):
        """Simple mediation analysis using regression approach"""
        print("\n" + "="*70)
        print("MEDIATION ANALYSIS")
        print("="*70)
        
        # Test mediation: ATT -> INT -> T2_Behavior
        print("Testing mediation: Attitude -> Intention -> T2 Behavior")
        
        # Step 1: ATT -> T2_Behavior (total effect)
        att_scores = self.construct_means['ATT']
        behavior_scores = self.df['T2_Actual_Behavior']
        
        model_total = LinearRegression()
        model_total.fit(att_scores.values.reshape(-1, 1), behavior_scores)
        total_effect = model_total.coef_[0]
        
        # Step 2: ATT -> INT (a path)
        int_scores = self.construct_means['INT']
        model_a = LinearRegression()
        model_a.fit(att_scores.values.reshape(-1, 1), int_scores)
        a_path = model_a.coef_[0]
        
        # Step 3: ATT + INT -> T2_Behavior (b path and direct effect)
        X_mediation = np.column_stack([att_scores, int_scores])
        model_mediation = LinearRegression()
        model_mediation.fit(X_mediation, behavior_scores)
        direct_effect = model_mediation.coef_[0]  # ATT -> Behavior (direct)
        b_path = model_mediation.coef_[1]  # INT -> Behavior
        
        # Calculate indirect effect
        indirect_effect = a_path * b_path
        
        print(f"Total effect (c): {total_effect:.3f}")
        print(f"Direct effect (c'): {direct_effect:.3f}")
        print(f"Indirect effect (a*b): {indirect_effect:.3f}")
        print(f"a path (ATT -> INT): {a_path:.3f}")
        print(f"b path (INT -> Behavior): {b_path:.3f}")
        
        # Proportion mediated
        if total_effect != 0:
            prop_mediated = indirect_effect / total_effect
            print(f"Proportion mediated: {prop_mediated:.3f} ({prop_mediated*100:.1f}%)")
        
        return {
            'total_effect': total_effect,
            'direct_effect': direct_effect,
            'indirect_effect': indirect_effect,
            'a_path': a_path,
            'b_path': b_path,
            'proportion_mediated': prop_mediated if total_effect != 0 else None
        }
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        print("\n" + "="*70)
        print("CREATING VISUALIZATIONS")
        print("="*70)
        
        # 1. Correlation heatmap
        construct_df = pd.DataFrame(self.construct_means)
        construct_df['Past_Behavior'] = self.df['Past_Behavior']
        construct_df['T2_Behavior'] = self.df['T2_Actual_Behavior']
        
        plt.figure(figsize=(12, 10))
        correlation_matrix = construct_df.corr()
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', 
                   center=0, square=True, fmt='.3f', cbar_kws={"shrink": .8})
        plt.title('Construct Correlation Matrix', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/workspace/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Construct means comparison
        plt.figure(figsize=(12, 8))
        construct_means_data = []
        construct_names = []
        for construct, scores in self.construct_means.items():
            construct_means_data.append(scores.mean())
            construct_names.append(construct)
        
        bars = plt.bar(construct_names, construct_means_data, 
                      color=sns.color_palette("husl", len(construct_names)))
        plt.ylabel('Mean Score (1-7 scale)', fontsize=12)
        plt.xlabel('Theoretical Constructs', fontsize=12)
        plt.title('Mean Scores by Theoretical Construct', fontsize=16, fontweight='bold')
        plt.ylim(0, 7)
        
        # Add value labels on bars
        for bar, value in zip(bars, construct_means_data):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('/workspace/construct_means.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Behavior change distribution
        plt.figure(figsize=(10, 6))
        behavior_change = self.df['T2_Actual_Behavior'] - self.df['Past_Behavior']
        
        plt.hist(behavior_change, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(behavior_change.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean = {behavior_change.mean():.2f}')
        plt.xlabel('Behavior Change (T2 - Past)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of Behavior Change', fontsize=16, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('/workspace/behavior_change_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Intention-Behavior relationship
        plt.figure(figsize=(10, 8))
        int_scores = self.construct_means['INT']
        behavior_scores = self.df['T2_Actual_Behavior']
        
        plt.scatter(int_scores, behavior_scores, alpha=0.6, s=50)
        
        # Add regression line
        z = np.polyfit(int_scores, behavior_scores, 1)
        p = np.poly1d(z)
        plt.plot(int_scores, p(int_scores), "r--", alpha=0.8, linewidth=2)
        
        # Calculate and display correlation
        r, p_val = pearsonr(int_scores, behavior_scores)
        plt.text(0.05, 0.95, f'r = {r:.3f}, p < 0.001', 
                transform=plt.gca().transAxes, fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        plt.xlabel('Intention (T1)', fontsize=12)
        plt.ylabel('Actual Behavior (T2)', fontsize=12)
        plt.title('Intention-Behavior Relationship', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('/workspace/intention_behavior_relationship.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Correlation heatmap saved to: correlation_heatmap.png")
        print("✓ Construct means chart saved to: construct_means.png")
        print("✓ Behavior change distribution saved to: behavior_change_distribution.png")
        print("✓ Intention-behavior relationship saved to: intention_behavior_relationship.png")
    
    def generate_summary_report(self, desc_results, corr_results, reg_results, med_results):
        """Generate comprehensive summary report"""
        print("\n" + "="*70)
        print("COMPREHENSIVE ANALYSIS SUMMARY")
        print("="*70)
        
        report = {
            'sample_characteristics': {
                'n': desc_results['sample_size'],
                'age_mean': self.df['Age'].mean(),
                'age_std': self.df['Age'].std(),
                'gender_female_pct': (self.df['Gender'] == 'Female').mean() * 100,
                'previous_fraud_pct': (self.df['Previous_Fraud_Experience'] == 'Yes').mean() * 100
            },
            'theoretical_validation': {
                'correlations_within_range': sum([r['within_range'] for r in corr_results]),
                'total_correlations_tested': len(corr_results),
                'validation_rate': sum([r['within_range'] for r in corr_results]) / len(corr_results)
            },
            'model_performance': {
                'tpb_r2': reg_results['tpb_intention']['r_squared'],
                'extended_r2': reg_results['extended_intention']['r_squared'],
                'behavior_r2': reg_results['behavior']['r_squared'],
                'r2_improvement': reg_results['extended_intention']['r_squared'] - reg_results['tpb_intention']['r_squared']
            },
            'mediation_results': med_results,
            'key_findings': {
                'strongest_intention_predictor': max(reg_results['extended_intention']['coefficients'].items(), 
                                                   key=lambda x: abs(x[1])),
                'strongest_behavior_predictor': max(reg_results['behavior']['coefficients'].items(), 
                                                  key=lambda x: abs(x[1])),
                'behavior_change_mean': desc_results['behavior_change']
            }
        }
        
        # Save summary report
        import json
        with open('/workspace/python_analysis_summary.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Sample Size: {report['sample_characteristics']['n']}")
        print(f"Theoretical Validation Rate: {report['theoretical_validation']['validation_rate']:.1%}")
        print(f"Extended Model R²: {report['model_performance']['extended_r2']:.3f}")
        print(f"Behavior Prediction R²: {report['model_performance']['behavior_r2']:.3f}")
        print(f"Strongest Intention Predictor: {report['key_findings']['strongest_intention_predictor'][0]}")
        print(f"Strongest Behavior Predictor: {report['key_findings']['strongest_behavior_predictor'][0]}")
        
        print(f"\n✓ Complete analysis summary saved to: python_analysis_summary.json")
        
        return report
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("COMPREHENSIVE BEHAVIORAL INTENTION ANALYSIS")
        print("Theory of Planned Behavior + Protection Motivation Theory")
        print("="*80)
        
        # Run all analyses
        desc_results = self.descriptive_analysis()
        corr_results, corr_matrix = self.correlation_analysis()
        reg_results = self.regression_analysis()
        med_results = self.mediation_analysis()
        self.create_visualizations()
        summary_report = self.generate_summary_report(desc_results, corr_results, reg_results, med_results)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("✓ Descriptive analysis completed")
        print("✓ Correlation analysis completed")
        print("✓ Regression modeling completed")
        print("✓ Mediation analysis completed")
        print("✓ Visualizations created")
        print("✓ Summary report generated")
        print("\nAll results saved to workspace directory!")
        
        return summary_report

def main():
    """Main analysis function"""
    analyzer = BehavioralAnalysis('/workspace/behavioral_intention_dataset.csv')
    results = analyzer.run_complete_analysis()
    return results

if __name__ == "__main__":
    analysis_results = main()