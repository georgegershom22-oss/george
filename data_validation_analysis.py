#!/usr/bin/env python3
"""
Data Validation and Analysis for SOFC Economic & Financial Dataset
Provides validation, cross-checks, and analytical insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

def validate_data_consistency():
    """Validate data consistency across all datasets"""
    
    print("🔍 Validating Data Consistency...")
    
    # Load main datasets
    main_data = pd.read_excel('sofc_economic_financial_data.xlsx', sheet_name=None)
    detailed_data = pd.read_excel('sofc_detailed_cost_breakdown.xlsx', sheet_name=None)
    
    validation_results = {
        'checks_passed': 0,
        'checks_failed': 0,
        'warnings': 0,
        'issues': []
    }
    
    # Check 1: SOFC CAPEX consistency
    sofc_costs = main_data['sofc_costs']
    component_breakdown = detailed_data['sofc_component_breakdown']
    
    total_component_cost = component_breakdown['cost_usd_per_kw'].sum()
    avg_sofc_capex = sofc_costs['capex_usd_per_kw'].mean()
    
    if abs(total_component_cost - avg_sofc_capex) / avg_sofc_capex < 0.1:  # Within 10%
        validation_results['checks_passed'] += 1
    else:
        validation_results['checks_failed'] += 1
        validation_results['issues'].append(f"SOFC CAPEX mismatch: Components sum to {total_component_cost:.0f}, average CAPEX is {avg_sofc_capex:.0f}")
    
    # Check 2: OPEX consistency
    sofc_opex = sofc_costs['opex_annual_usd_per_kw'].mean()
    opex_breakdown = detailed_data['operational_cost_breakdown']
    total_opex = opex_breakdown['annual_cost_usd_per_kw'].sum()
    
    if abs(total_opex - sofc_opex) / sofc_opex < 0.2:  # Within 20%
        validation_results['checks_passed'] += 1
    else:
        validation_results['warnings'] += 1
        validation_results['issues'].append(f"OPEX breakdown sum ({total_opex:.0f}) differs from average SOFC OPEX ({sofc_opex:.0f})")
    
    # Check 3: Financial parameter ranges
    financial_params = main_data['financial_parameters']
    
    # Check WACC calculation
    wacc_value = financial_params.loc[financial_params['parameter'] == 'wacc_pct', 'value'].iloc[0]
    if 10 <= wacc_value <= 30:  # Reasonable WACC range
        validation_results['checks_passed'] += 1
    else:
        validation_results['checks_failed'] += 1
        validation_results['issues'].append(f"WACC value ({wacc_value:.2f}%) outside reasonable range (10-30%)")
    
    # Check 4: Exchange rate reasonableness
    exchange_rate = financial_params.loc[financial_params['parameter'] == 'usd_ngn_exchange_rate', 'value'].iloc[0]
    if 1000 <= exchange_rate <= 2000:  # Reasonable NGN/USD range
        validation_results['checks_passed'] += 1
    else:
        validation_results['warnings'] += 1
        validation_results['issues'].append(f"Exchange rate ({exchange_rate:.0f}) may be outside current range")
    
    # Check 5: Technology cost learning curves
    learning_curves = component_breakdown['learning_curve_pct']
    if all(0 <= lc <= 50 for lc in learning_curves):  # Reasonable learning curve range
        validation_results['checks_passed'] += 1
    else:
        validation_results['checks_failed'] += 1
        validation_results['issues'].append("Learning curve values outside reasonable range (0-50%)")
    
    return validation_results

def generate_cost_comparison_analysis():
    """Generate comparative cost analysis between technologies"""
    
    print("📊 Generating Cost Comparison Analysis...")
    
    # Load data
    main_data = pd.read_excel('sofc_economic_financial_data.xlsx', sheet_name=None)
    
    sofc_costs = main_data['sofc_costs']
    diesel_costs = main_data['diesel_costs']
    solar_costs = main_data['solar_battery_costs']
    
    # Create comparison dataframe
    comparison_data = {
        'system_size_kw': sofc_costs['system_size_kw'],
        'sofc_capex': sofc_costs['capex_usd_per_kw'],
        'diesel_capex': diesel_costs['capex_usd_per_kw'],
        'solar_capex': solar_costs['total_capex_usd_per_kw'],
        'sofc_opex': sofc_costs['opex_annual_usd_per_kw'],
        'diesel_opex': diesel_costs['opex_annual_usd_per_kw'],
        'solar_opex': solar_costs['opex_annual_usd_per_kw'],
        'sofc_efficiency': sofc_costs['efficiency_percent'],
        'diesel_efficiency': diesel_costs['efficiency_percent'],
        'solar_efficiency': solar_costs['efficiency_percent']
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Calculate levelized cost of electricity (LCOE) - simplified
    project_lifetime = 20  # years
    discount_rate = 0.12  # 12%
    
    def calculate_lcoe(capex, opex, efficiency, capacity_factor=0.8):
        """Simplified LCOE calculation"""
        annual_capex = capex * (discount_rate * (1 + discount_rate)**project_lifetime) / ((1 + discount_rate)**project_lifetime - 1)
        annual_opex = opex
        annual_generation = 8760 * capacity_factor * efficiency / 100  # kWh/kW
        return (annual_capex + annual_opex) / annual_generation
    
    # Calculate LCOE for each technology
    comparison_df['sofc_lcoe'] = comparison_df.apply(
        lambda row: calculate_lcoe(row['sofc_capex'], row['sofc_opex'], row['sofc_efficiency']), axis=1
    )
    comparison_df['diesel_lcoe'] = comparison_df.apply(
        lambda row: calculate_lcoe(row['diesel_capex'], row['diesel_opex'], row['diesel_efficiency']), axis=1
    )
    comparison_df['solar_lcoe'] = comparison_df.apply(
        lambda row: calculate_lcoe(row['solar_capex'], row['solar_opex'], row['solar_efficiency'], 0.22), axis=1
    )
    
    return comparison_df

def generate_sensitivity_analysis():
    """Generate sensitivity analysis results"""
    
    print("🎯 Generating Sensitivity Analysis...")
    
    # Load sensitivity parameters
    detailed_data = pd.read_excel('sofc_detailed_cost_breakdown.xlsx', sheet_name=None)
    sensitivity_params = detailed_data['sensitivity_parameters']
    
    # Base case LCOE (using 500kW system as reference)
    base_capex = 6500  # USD/kW
    base_opex = 145    # USD/kW/year
    base_efficiency = 62  # %
    base_availability = 95  # %
    
    def calculate_lcoe_sensitivity(capex, opex, efficiency, availability):
        """Calculate LCOE with given parameters"""
        project_lifetime = 20
        discount_rate = 0.12
        capacity_factor = 0.8 * (availability / 100)
        
        annual_capex = capex * (discount_rate * (1 + discount_rate)**project_lifetime) / ((1 + discount_rate)**project_lifetime - 1)
        annual_generation = 8760 * capacity_factor * (efficiency / 100)
        return (annual_capex + opex) / annual_generation
    
    base_lcoe = calculate_lcoe_sensitivity(base_capex, base_opex, base_efficiency, base_availability)
    
    sensitivity_results = []
    
    for _, param in sensitivity_params.iterrows():
        if param['parameter'] == 'SOFC CAPEX':
            low_lcoe = calculate_lcoe_sensitivity(param['low_value'], base_opex, base_efficiency, base_availability)
            high_lcoe = calculate_lcoe_sensitivity(param['high_value'], base_opex, base_efficiency, base_availability)
        elif param['parameter'] == 'SOFC OPEX':
            low_lcoe = calculate_lcoe_sensitivity(base_capex, param['low_value'], base_efficiency, base_availability)
            high_lcoe = calculate_lcoe_sensitivity(base_capex, param['high_value'], base_efficiency, base_availability)
        elif param['parameter'] == 'System Efficiency':
            low_lcoe = calculate_lcoe_sensitivity(base_capex, base_opex, param['low_value'], base_availability)
            high_lcoe = calculate_lcoe_sensitivity(base_capex, base_opex, param['high_value'], base_availability)
        elif param['parameter'] == 'Availability Factor':
            low_lcoe = calculate_lcoe_sensitivity(base_capex, base_opex, base_efficiency, param['low_value'])
            high_lcoe = calculate_lcoe_sensitivity(base_capex, base_opex, base_efficiency, param['high_value'])
        else:
            continue  # Skip other parameters for this simplified analysis
        
        sensitivity_range = (high_lcoe - low_lcoe) / base_lcoe * 100
        sensitivity_results.append({
            'parameter': param['parameter'],
            'base_lcoe': base_lcoe,
            'low_lcoe': low_lcoe,
            'high_lcoe': high_lcoe,
            'sensitivity_range_pct': sensitivity_range,
            'sensitivity_rank': param['sensitivity_rank']
        })
    
    return pd.DataFrame(sensitivity_results)

def generate_risk_assessment():
    """Generate comprehensive risk assessment"""
    
    print("⚠️ Generating Risk Assessment...")
    
    # Load risk data
    detailed_data = pd.read_excel('sofc_detailed_cost_breakdown.xlsx', sheet_name=None)
    risk_data = detailed_data['risk_analysis']
    
    # Calculate risk scores
    risk_data['risk_score'] = risk_data['probability_pct'] * risk_data['impact_severity'].map({
        'Low': 1, 'Medium': 2, 'High': 3
    })
    
    # Calculate total risk exposure
    risk_data['total_exposure_usd_per_kw'] = (
        risk_data['risk_score'] * risk_data['mitigation_cost_usd_per_kw'] / 100
    )
    
    # Risk prioritization
    risk_data = risk_data.sort_values('risk_score', ascending=False)
    risk_data['risk_priority'] = range(1, len(risk_data) + 1)
    
    return risk_data

def generate_financial_scenarios():
    """Generate different financial scenarios"""
    
    print("💰 Generating Financial Scenarios...")
    
    # Load financial data
    main_data = pd.read_excel('sofc_economic_financial_data.xlsx', sheet_name=None)
    detailed_data = pd.read_excel('sofc_detailed_cost_breakdown.xlsx', sheet_name=None)
    
    financial_params = main_data['financial_parameters']
    financing_scenarios = detailed_data['financing_scenarios']
    
    # Base financial parameters
    base_wacc = financial_params.loc[financial_params['parameter'] == 'wacc_pct', 'value'].iloc[0]
    base_exchange_rate = financial_params.loc[financial_params['parameter'] == 'usd_ngn_exchange_rate', 'value'].iloc[0]
    
    scenario_results = []
    
    for _, scenario in financing_scenarios.iterrows():
        # Calculate effective WACC for this scenario
        debt_rate = scenario['debt_interest_rate_pct'] / 100
        equity_rate = scenario['equity_return_rate_pct'] / 100
        debt_ratio = scenario['debt_percentage'] / 100
        equity_ratio = scenario['equity_percentage'] / 100
        
        effective_wacc = (debt_rate * debt_ratio) + (equity_rate * equity_ratio)
        
        # Calculate project NPV (simplified)
        capex = 6500  # USD/kW
        annual_revenue = 1200  # USD/kW (assumed electricity sales)
        annual_opex = 145  # USD/kW
        project_lifetime = 20
        
        npv = -capex
        for year in range(1, project_lifetime + 1):
            annual_cashflow = annual_revenue - annual_opex
            npv += annual_cashflow / (1 + effective_wacc)**year
        
        scenario_results.append({
            'scenario': scenario['scenario'],
            'effective_wacc_pct': effective_wacc * 100,
            'project_npv_usd_per_kw': npv,
            'payback_period_years': capex / (annual_revenue - annual_opex),
            'irr_pct': ((annual_revenue - annual_opex) / capex) * 100,
            'debt_ratio': debt_ratio,
            'equity_ratio': equity_ratio
        })
    
    return pd.DataFrame(scenario_results)

def main():
    """Main function to run all validation and analysis"""
    
    print("🚀 Starting Comprehensive Data Validation and Analysis...")
    
    # Run all analyses
    validation_results = validate_data_consistency()
    cost_comparison = generate_cost_comparison_analysis()
    sensitivity_analysis = generate_sensitivity_analysis()
    risk_assessment = generate_risk_assessment()
    financial_scenarios = generate_financial_scenarios()
    
    # Save results
    with pd.ExcelWriter('sofc_analysis_results.xlsx', engine='openpyxl') as writer:
        cost_comparison.to_excel(writer, sheet_name='cost_comparison', index=False)
        sensitivity_analysis.to_excel(writer, sheet_name='sensitivity_analysis', index=False)
        risk_assessment.to_excel(writer, sheet_name='risk_assessment', index=False)
        financial_scenarios.to_excel(writer, sheet_name='financial_scenarios', index=False)
    
    # Create comprehensive report
    report = f"""
# SOFC Economic & Financial Data Analysis Report

## Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Data Validation Results:
- ✅ Checks Passed: {validation_results['checks_passed']}
- ❌ Checks Failed: {validation_results['checks_failed']}
- ⚠️ Warnings: {validation_results['warnings']}

## Key Findings:

### 1. Technology Cost Comparison (500kW System):
- **SOFC LCOE**: ${cost_comparison.loc[2, 'sofc_lcoe']:.3f}/kWh
- **Diesel LCOE**: ${cost_comparison.loc[2, 'diesel_lcoe']:.3f}/kWh
- **Solar LCOE**: ${cost_comparison.loc[2, 'solar_lcoe']:.3f}/kWh

### 2. Most Sensitive Parameters:
1. **{sensitivity_analysis.iloc[0]['parameter']}**: {sensitivity_analysis.iloc[0]['sensitivity_range_pct']:.1f}% LCOE variation
2. **{sensitivity_analysis.iloc[1]['parameter']}**: {sensitivity_analysis.iloc[1]['sensitivity_range_pct']:.1f}% LCOE variation
3. **{sensitivity_analysis.iloc[2]['parameter']}**: {sensitivity_analysis.iloc[2]['sensitivity_range_pct']:.1f}% LCOE variation

### 3. Highest Risk Factors:
1. **{risk_assessment.iloc[0]['risk_category']}**: Risk Score {risk_assessment.iloc[0]['risk_score']:.1f}
2. **{risk_assessment.iloc[1]['risk_category']}**: Risk Score {risk_assessment.iloc[1]['risk_score']:.1f}
3. **{risk_assessment.iloc[2]['risk_category']}**: Risk Score {risk_assessment.iloc[2]['risk_score']:.1f}

### 4. Best Financing Scenario:
- **{financial_scenarios.loc[financial_scenarios['project_npv_usd_per_kw'].idxmax(), 'scenario']}**
- NPV: ${financial_scenarios['project_npv_usd_per_kw'].max():.0f}/kW
- Payback: {financial_scenarios['payback_period_years'].min():.1f} years

## Files Generated:
- sofc_analysis_results.xlsx: Complete analysis results
- SOFC_Analysis_Report.md: This comprehensive report
- data_validation_analysis.py: Analysis code

## Recommendations:
1. **Focus on reducing SOFC CAPEX** - highest sensitivity parameter
2. **Implement risk mitigation** for top 3 risk factors
3. **Consider {financial_scenarios.loc[financial_scenarios['project_npv_usd_per_kw'].idxmax(), 'scenario']}** for financing
4. **Monitor {sensitivity_analysis.iloc[0]['parameter']}** closely during project implementation
"""
    
    with open('SOFC_Analysis_Report.md', 'w') as f:
        f.write(report)
    
    # Save validation results
    with open('validation_results.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print("✅ Analysis Complete!")
    print("📊 Files generated:")
    print("   - sofc_analysis_results.xlsx")
    print("   - SOFC_Analysis_Report.md")
    print("   - validation_results.json")
    print("   - data_validation_analysis.py")
    
    return {
        'validation': validation_results,
        'cost_comparison': cost_comparison,
        'sensitivity': sensitivity_analysis,
        'risk': risk_assessment,
        'financial': financial_scenarios
    }

if __name__ == "__main__":
    results = main()