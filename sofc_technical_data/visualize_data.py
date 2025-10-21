#!/usr/bin/env python3
"""
SOFC Dataset Visualization Script
Quick data exploration and visualization for SOFC technical dataset
"""

import pandas as pd
import sys

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_subheader(text):
    """Print formatted subheader"""
    print(f"\n--- {text} ---\n")

def explore_performance_data():
    """Explore SOFC performance characteristics"""
    print_header("SOFC PERFORMANCE CHARACTERISTICS")
    
    df = pd.read_csv('sofc_performance_characteristics.csv')
    
    print(f"Total records: {len(df)}")
    print(f"Manufacturers: {', '.join(df['Manufacturer'].unique())}")
    print(f"System sizes: {sorted(df['System_Size_kW'].unique())} kW")
    print(f"Load conditions: {sorted(df['Load_Percentage'].unique())}%")
    
    print_subheader("Efficiency Summary by Manufacturer (at 100% load)")
    summary = df[df['Load_Percentage'] == 100].groupby('Manufacturer').agg({
        'Electrical_Efficiency_LHV': ['mean', 'min', 'max'],
        'CHP_Total_Efficiency': ['mean', 'min', 'max']
    }).round(4)
    print(summary)
    
    print_subheader("Top 10 Most Efficient Systems (Electrical, 100% load)")
    top_eff = df[df['Load_Percentage'] == 100].nlargest(10, 'Electrical_Efficiency_LHV')[
        ['Manufacturer', 'System_Size_kW', 'Electrical_Efficiency_LHV', 'CHP_Total_Efficiency']
    ]
    print(top_eff.to_string(index=False))
    
    print_subheader("Degradation Rate Summary")
    deg_summary = df.groupby('Manufacturer')['Stack_Degradation_pct_per_1000h'].agg(['mean', 'min', 'max']).round(3)
    print(deg_summary)

def explore_fuel_flexibility():
    """Explore fuel flexibility data"""
    print_header("FUEL FLEXIBILITY & COMPATIBILITY")
    
    df = pd.read_csv('sofc_fuel_flexibility.csv')
    
    print(f"Total records: {len(df)}")
    print(f"Fuel types analyzed: {len(df['Fuel_Type'].unique())}")
    
    print_subheader("Fuel Types Available")
    for i, fuel in enumerate(df['Fuel_Type'].unique(), 1):
        print(f"{i:2d}. {fuel}")
    
    print_subheader("Fuel Performance Summary")
    fuel_perf = df.groupby('Fuel_Type').agg({
        'Relative_Efficiency_Impact': ['mean', 'min', 'max'],
        'Sulfur_Content_ppm': ['mean'],
        'Degradation_Impact_Multiplier': ['mean']
    }).round(3)
    print(fuel_perf)
    
    print_subheader("Best Fuels for Nigeria (by efficiency impact)")
    nigeria_fuels = [
        'Pipeline Natural Gas',
        'Associated Petroleum Gas (APG)',
        'LPG (Propane)',
        'Bio-methane (Anaerobic Digestion)'
    ]
    for fuel in nigeria_fuels:
        fuel_data = df[df['Fuel_Type'].str.contains(fuel.split('(')[0].strip())]
        if len(fuel_data) > 0:
            avg_eff = fuel_data['Relative_Efficiency_Impact'].mean()
            avg_sulfur = fuel_data['Sulfur_Content_ppm'].mean()
            print(f"  • {fuel:45s} - Eff: {avg_eff:.3f}, Sulfur: {avg_sulfur:.1f} ppm")

def explore_nigeria_adaptations():
    """Explore Nigeria-specific data"""
    print_header("NIGERIA-SPECIFIC ADAPTATIONS")
    
    df = pd.read_csv('nigeria_specific_adaptations.csv')
    
    print(f"Total records: {len(df)}")
    print(f"Locations covered: {len(df['Location'].unique())}")
    
    print_subheader("Performance by Location")
    location_perf = df.groupby('Location').agg({
        'Average_Temperature_C': 'mean',
        'Average_Humidity_pct': 'mean',
        'Performance_Derating_Factor': 'mean',
        'Grid_Stability_Score': 'mean',
        'Estimated_Grid_Outages_per_month': 'mean'
    }).round(2)
    print(location_perf)
    
    print_subheader("Best Locations for SOFC Deployment")
    best_locations = df.groupby('Location')['Performance_Derating_Factor'].mean().sort_values(ascending=False)
    print("\nRanked by performance (1=best):")
    for i, (location, derating) in enumerate(best_locations.items(), 1):
        performance_loss = (1 - derating) * 100
        print(f"{i}. {location:45s} - {performance_loss:.1f}% derating")
    
    print_subheader("Grid Reliability by Location")
    grid = df.groupby('Location').agg({
        'Grid_Stability_Score': 'mean',
        'Estimated_Grid_Outages_per_month': 'mean'
    }).sort_values('Grid_Stability_Score', ascending=False).round(1)
    print(grid)

def explore_operational_characteristics():
    """Explore operational characteristics"""
    print_header("OPERATIONAL CHARACTERISTICS")
    
    df = pd.read_csv('sofc_operational_characteristics.csv')
    
    print(f"Total records: {len(df)}")
    print(f"Operational modes: {', '.join(df['Operational_Mode'].unique())}")
    
    print_subheader("Start-up Time Summary by Manufacturer")
    startup = df.groupby('Manufacturer').agg({
        'Cold_Start_Time_hours': 'mean',
        'Warm_Start_Time_hours': 'mean',
        'Hot_Start_Time_minutes': 'mean'
    }).round(1)
    print(startup)
    
    print_subheader("Operational Mode Suitability")
    mode_suit = df.groupby('Operational_Mode')['Mode_Suitability_Rating'].value_counts().unstack(fill_value=0)
    print(mode_suit)
    
    print_subheader("Ramp Rate Summary")
    ramp = df.groupby('Manufacturer').agg({
        'Ramp_Up_Rate_pct_per_min': 'mean',
        'Ramp_Down_Rate_pct_per_min': 'mean',
        'Minimum_Load_pct': 'mean'
    }).round(2)
    print(ramp)

def explore_system_sizing():
    """Explore system sizing recommendations"""
    print_header("SYSTEM SIZING REFERENCE")
    
    df = pd.read_csv('system_sizing_reference.csv')
    
    print(f"Total applications: {len(df)}")
    
    print_subheader("Sizing Recommendations by Application")
    sizing = df[[
        'Application_Type',
        'Peak_Load_kW',
        'Average_Load_kW',
        'Recommended_SOFC_Size_BaseLoad_kW',
        'CHP_Suitability'
    ]].round(0)
    print(sizing.to_string(index=False))
    
    print_subheader("Best Applications for CHP")
    chp_apps = df[df['CHP_Suitability'].isin(['Excellent', 'Good'])][
        ['Application_Type', 'CHP_Suitability', 'Heat_Demand_Level']
    ]
    print(chp_apps.to_string(index=False))

def main():
    """Main exploration function"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                        ║")
    print("║           SOFC TECHNICAL DATASET - DATA EXPLORATION                    ║")
    print("║                                                                        ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    
    try:
        if len(sys.argv) > 1:
            option = sys.argv[1]
            if option == '1':
                explore_performance_data()
            elif option == '2':
                explore_fuel_flexibility()
            elif option == '3':
                explore_nigeria_adaptations()
            elif option == '4':
                explore_operational_characteristics()
            elif option == '5':
                explore_system_sizing()
            else:
                print("\nInvalid option. Choose 1-5 or run without arguments for all.")
        else:
            # Run all explorations
            explore_performance_data()
            explore_fuel_flexibility()
            explore_nigeria_adaptations()
            explore_operational_characteristics()
            explore_system_sizing()
        
        print("\n" + "="*80)
        print("  DATA EXPLORATION COMPLETE")
        print("="*80)
        print("\nFor detailed analysis:")
        print("  • Load CSV files in Python/R/Excel")
        print("  • See DATA_DICTIONARY.md for variable definitions")
        print("  • See QUICK_START_GUIDE.md for usage examples")
        print("\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find data file: {e}")
        print("Make sure you're running this script from the sofc_technical_data directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
