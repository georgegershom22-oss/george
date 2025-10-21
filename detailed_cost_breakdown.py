#!/usr/bin/env python3
"""
Detailed Cost Breakdown for SOFC Systems
Provides granular cost analysis for techno-economic modeling
"""

import pandas as pd
import numpy as np
import json

def generate_detailed_sofc_breakdown():
    """Generate detailed SOFC system cost breakdown"""
    
    # Detailed SOFC system component costs (USD/kW)
    components = {
        'component': [
            'SOFC Stack',
            'Fuel Processing Unit',
            'Power Conditioning System',
            'Heat Recovery System',
            'Control & Monitoring',
            'Balance of Plant',
            'Installation & Commissioning',
            'Engineering & Design',
            'Project Management',
            'Contingency',
            'Transportation',
            'Insurance',
            'Permits & Licenses'
        ],
        'cost_usd_per_kw': [
            3200,  # SOFC Stack (largest component)
            1200,  # Fuel Processing Unit
            800,   # Power Conditioning System
            600,   # Heat Recovery System
            300,   # Control & Monitoring
            500,   # Balance of Plant
            400,   # Installation & Commissioning
            200,   # Engineering & Design
            150,   # Project Management
            300,   # Contingency (5-10%)
            100,   # Transportation
            80,    # Insurance
            70     # Permits & Licenses
        ],
        'uncertainty_pct': [
            20,    # Stack cost uncertainty
            15,    # Fuel processing uncertainty
            10,    # Power conditioning uncertainty
            12,    # Heat recovery uncertainty
            8,     # Control system uncertainty
            15,    # BOP uncertainty
            20,    # Installation uncertainty
            25,    # Engineering uncertainty
            30,    # Project management uncertainty
            50,    # Contingency uncertainty
            25,    # Transportation uncertainty
            20,    # Insurance uncertainty
            40     # Permits uncertainty
        ],
        'learning_curve_pct': [
            15,    # Stack learning curve
            10,    # Fuel processing learning curve
            8,     # Power conditioning learning curve
            5,     # Heat recovery learning curve
            3,     # Control system learning curve
            8,     # BOP learning curve
            5,     # Installation learning curve
            2,     # Engineering learning curve
            2,     # Project management learning curve
            0,     # Contingency (no learning)
            3,     # Transportation learning curve
            0,     # Insurance (no learning)
            0      # Permits (no learning)
        ],
        'local_content_pct': [
            5,     # Stack (mostly imported)
            20,    # Fuel processing (some local)
            30,    # Power conditioning (more local)
            40,    # Heat recovery (significant local)
            60,    # Control & monitoring (mostly local)
            50,    # Balance of plant (mixed)
            80,    # Installation (mostly local)
            70,    # Engineering (mostly local)
            90,    # Project management (local)
            0,     # Contingency (not applicable)
            30,    # Transportation (mixed)
            100,   # Insurance (local)
            100    # Permits (local)
        ]
    }
    
    return pd.DataFrame(components)

def generate_operational_cost_breakdown():
    """Generate detailed operational cost breakdown"""
    
    opex_breakdown = {
        'cost_category': [
            'Stack Replacement',
            'Preventive Maintenance',
            'Corrective Maintenance',
            'Fuel Processing Maintenance',
            'Power Conditioning Maintenance',
            'Heat Recovery Maintenance',
            'Control System Maintenance',
            'Labor Costs',
            'Utilities (Water, Air)',
            'Insurance',
            'Permits & Compliance',
            'Spare Parts Inventory',
            'Technical Support',
            'Training',
            'Environmental Monitoring'
        ],
        'annual_cost_usd_per_kw': [
            45,    # Stack replacement (amortized)
            25,    # Preventive maintenance
            15,    # Corrective maintenance
            12,    # Fuel processing maintenance
            8,     # Power conditioning maintenance
            10,    # Heat recovery maintenance
            5,     # Control system maintenance
            20,    # Labor costs
            8,     # Utilities
            6,     # Insurance
            3,     # Permits & compliance
            10,    # Spare parts inventory
            5,     # Technical support
            2,     # Training
            3      # Environmental monitoring
        ],
        'frequency': [
            'Every 7 years',
            'Monthly',
            'As needed',
            'Quarterly',
            'Semi-annually',
            'Quarterly',
            'Semi-annually',
            'Monthly',
            'Continuous',
            'Annually',
            'Annually',
            'As needed',
            'Quarterly',
            'Annually',
            'Continuous'
        ],
        'uncertainty_pct': [
            25,    # Stack replacement uncertainty
            20,    # Preventive maintenance uncertainty
            30,    # Corrective maintenance uncertainty
            15,    # Fuel processing uncertainty
            10,    # Power conditioning uncertainty
            12,    # Heat recovery uncertainty
            8,     # Control system uncertainty
            15,    # Labor cost uncertainty
            20,    # Utilities uncertainty
            10,    # Insurance uncertainty
            25,    # Permits uncertainty
            20,    # Spare parts uncertainty
            15,    # Technical support uncertainty
            30,    # Training uncertainty
            20     # Environmental monitoring uncertainty
        ]
    }
    
    return pd.DataFrame(opex_breakdown)

def generate_financing_scenarios():
    """Generate different financing scenarios for sensitivity analysis"""
    
    financing_scenarios = {
        'scenario': [
            'Government Grant (50%)',
            'Development Bank Loan',
            'Commercial Bank Loan',
            'Equipment Lease',
            'Power Purchase Agreement',
            'Build-Operate-Transfer',
            'Public-Private Partnership',
            'Carbon Credit Financing',
            'Export Credit Agency',
            'Multilateral Development Bank'
        ],
        'debt_percentage': [0, 70, 80, 100, 0, 60, 50, 0, 75, 80],
        'equity_percentage': [50, 30, 20, 0, 100, 40, 50, 100, 25, 20],
        'grant_percentage': [50, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'debt_interest_rate_pct': [0, 8, 12, 15, 0, 10, 9, 0, 6, 4],
        'equity_return_rate_pct': [0, 15, 18, 0, 20, 16, 15, 25, 12, 10],
        'loan_tenor_years': [0, 15, 10, 7, 0, 20, 15, 0, 12, 20],
        'grace_period_years': [0, 2, 1, 0, 0, 3, 2, 0, 2, 3],
        'collateral_required': ['None', 'Project Assets', 'Project + Personal', 'Equipment', 'None', 'Project Assets', 'Project Assets', 'None', 'Project Assets', 'Project Assets'],
        'currency_risk': ['None', 'Medium', 'High', 'High', 'None', 'Medium', 'Low', 'None', 'Low', 'Low'],
        'political_risk': ['Low', 'Medium', 'High', 'High', 'Low', 'Medium', 'Low', 'Low', 'Low', 'Low']
    }
    
    return pd.DataFrame(financing_scenarios)

def generate_risk_analysis():
    """Generate risk analysis parameters"""
    
    risk_factors = {
        'risk_category': [
            'Technology Risk',
            'Market Risk',
            'Financial Risk',
            'Regulatory Risk',
            'Operational Risk',
            'Environmental Risk',
            'Political Risk',
            'Currency Risk',
            'Fuel Price Risk',
            'Grid Integration Risk'
        ],
        'probability_pct': [15, 20, 25, 30, 10, 5, 20, 40, 35, 15],
        'impact_severity': ['High', 'Medium', 'High', 'Medium', 'Low', 'Medium', 'High', 'High', 'High', 'Medium'],
        'mitigation_cost_usd_per_kw': [200, 100, 150, 80, 50, 120, 180, 100, 200, 90],
        'mitigation_effectiveness_pct': [70, 80, 85, 90, 95, 75, 60, 70, 65, 85],
        'insurance_available': ['No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No'],
        'insurance_cost_usd_per_kw': [0, 20, 30, 0, 10, 15, 25, 20, 35, 0]
    }
    
    return pd.DataFrame(risk_factors)

def generate_sensitivity_parameters():
    """Generate parameters for sensitivity analysis"""
    
    sensitivity_params = {
        'parameter': [
            'SOFC CAPEX',
            'SOFC OPEX',
            'Stack Lifetime',
            'System Efficiency',
            'Availability Factor',
            'Gas Price',
            'Electricity Price',
            'Interest Rate',
            'Exchange Rate',
            'Inflation Rate',
            'Project Lifetime',
            'Discount Rate',
            'Tax Rate',
            'Carbon Price',
            'Grid Reliability'
        ],
        'base_value': [6500, 145, 7, 62, 95, 0.008, 0.12, 18.25, 1500, 21.47, 20, 12, 30, 50, 65],
        'low_value': [5200, 116, 5, 55, 90, 0.005, 0.08, 12, 1200, 15, 15, 8, 20, 20, 50],
        'high_value': [7800, 174, 10, 70, 98, 0.012, 0.18, 25, 1800, 30, 25, 18, 40, 100, 85],
        'unit': ['USD/kW', 'USD/kW/year', 'years', '%', '%', 'USD/MJ', 'USD/kWh', '%', 'NGN/USD', '%', 'years', '%', '%', 'USD/tCO2', '%'],
        'sensitivity_rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    }
    
    return pd.DataFrame(sensitivity_params)

def main():
    """Generate detailed cost breakdown datasets"""
    
    print("Generating Detailed Cost Breakdown Data...")
    
    data = {
        'sofc_component_breakdown': generate_detailed_sofc_breakdown(),
        'operational_cost_breakdown': generate_operational_cost_breakdown(),
        'financing_scenarios': generate_financing_scenarios(),
        'risk_analysis': generate_risk_analysis(),
        'sensitivity_parameters': generate_sensitivity_parameters()
    }
    
    # Save to Excel
    with pd.ExcelWriter('sofc_detailed_cost_breakdown.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Create summary
    summary = f"""
# Detailed SOFC Cost Breakdown Analysis

## Generated Components Analysis:
- **Total Components**: {len(data['sofc_component_breakdown'])} major cost components
- **Operational Costs**: {len(data['operational_cost_breakdown'])} OPEX categories
- **Financing Options**: {len(data['financing_scenarios'])} different financing scenarios
- **Risk Factors**: {len(data['risk_analysis'])} identified risk categories
- **Sensitivity Parameters**: {len(data['sensitivity_parameters'])} parameters for sensitivity analysis

## Key Insights:
- **Largest Cost Component**: SOFC Stack ({data['sofc_component_breakdown'].loc[0, 'cost_usd_per_kw']} USD/kW)
- **Highest Uncertainty**: {data['sofc_component_breakdown'].loc[data['sofc_component_breakdown']['uncertainty_pct'].idxmax(), 'component']} ({data['sofc_component_breakdown']['uncertainty_pct'].max()}% uncertainty)
- **Best Learning Curve**: {data['sofc_component_breakdown'].loc[data['sofc_component_breakdown']['learning_curve_pct'].idxmax(), 'component']} ({data['sofc_component_breakdown']['learning_curve_pct'].max()}% reduction potential)
- **Highest Local Content**: {data['sofc_component_breakdown'].loc[data['sofc_component_breakdown']['local_content_pct'].idxmax(), 'component']} ({data['sofc_component_breakdown']['local_content_pct'].max()}% local)

## Files Generated:
- sofc_detailed_cost_breakdown.xlsx
- detailed_cost_breakdown.py
"""
    
    with open('SOFC_Detailed_Cost_Summary.md', 'w') as f:
        f.write(summary)
    
    print("✅ Detailed Cost Breakdown Generation Complete!")
    print("📁 Files created:")
    print("   - sofc_detailed_cost_breakdown.xlsx")
    print("   - SOFC_Detailed_Cost_Summary.md")
    print("   - detailed_cost_breakdown.py")
    
    return data

if __name__ == "__main__":
    data = main()