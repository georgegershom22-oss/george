#!/usr/bin/env python3
"""
Main script to generate and visualize SOFC technical dataset for Nigeria
Author: SOFC Research Team
Date: 2025-10-21
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

def main():
    """Main function to orchestrate data generation and visualization"""
    
    print("="*70)
    print(" SOFC TECHNICAL DATASET FOR NIGERIA POWER GENERATION")
    print("="*70)
    print("\nA Techno-Economic Analysis of Solid Oxide Fuel Cells")
    print("for Mitigating Nigeria's Electricity Crisis")
    print("-"*70)
    
    # Check if data exists
    raw_data_path = Path("data/raw")
    if not raw_data_path.exists():
        print("\nError: Raw data directory not found!")
        print("Please ensure the data/ directory structure exists.")
        return
    
    # Count existing data files
    json_files = list(raw_data_path.glob("*.json"))
    print(f"\n✓ Found {len(json_files)} raw data files")
    
    # Import modules
    try:
        from data_generator import SOFCDataGenerator
        from data_visualization import SOFCDataVisualizer
    except ImportError as e:
        print(f"\nError importing modules: {e}")
        print("Please ensure all scripts are in the scripts/ directory")
        return
    
    # User menu
    while True:
        print("\n" + "="*50)
        print(" MAIN MENU")
        print("="*50)
        print("1. Generate synthetic operational data")
        print("2. Create all visualizations")
        print("3. Run complete analysis (1 + 2)")
        print("4. View dataset statistics")
        print("5. Exit")
        print("-"*50)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            print("\n" + "-"*50)
            print(" GENERATING SYNTHETIC DATA")
            print("-"*50)
            generator = SOFCDataGenerator()
            
            # Generate all synthetic data
            print("\n→ Generating operational time-series...")
            generator.generate_operational_timeseries(duration_days=365)
            
            print("\n→ Generating economic scenarios...")
            generator.generate_economic_analysis()
            
            print("\n→ Generating reliability data...")
            generator.generate_reliability_data()
            
            print("\n→ Generating sensitivity analysis...")
            generator.generate_sensitivity_analysis()
            
            print("\n✓ All synthetic data generated successfully!")
            
        elif choice == "2":
            print("\n" + "-"*50)
            print(" CREATING VISUALIZATIONS")
            print("-"*50)
            
            # Change to scripts directory for proper path resolution
            os.chdir("scripts")
            visualizer = SOFCDataVisualizer()
            
            viz_dir = Path("../visualizations")
            viz_dir.mkdir(exist_ok=True)
            
            print("\n→ Creating efficiency curves...")
            visualizer.plot_efficiency_curves(save_path=viz_dir / "efficiency_curves.png")
            
            print("→ Creating fuel comparison...")
            visualizer.plot_fuel_comparison(save_path=viz_dir / "fuel_comparison.html")
            
            print("→ Creating power density analysis...")
            visualizer.plot_power_density_analysis(save_path=viz_dir / "power_density.png")
            
            print("→ Creating manufacturer comparison...")
            visualizer.plot_manufacturer_comparison(save_path=viz_dir / "manufacturer_comparison.html")
            
            print("→ Creating Nigeria scenarios...")
            visualizer.plot_nigeria_scenarios(save_path=viz_dir / "nigeria_scenarios.html")
            
            # Change back to main directory
            os.chdir("..")
            
            print(f"\n✓ All visualizations saved to: {viz_dir.absolute()}")
            
        elif choice == "3":
            print("\n" + "-"*50)
            print(" RUNNING COMPLETE ANALYSIS")
            print("-"*50)
            
            # Generate data
            print("\n[1/2] Generating Synthetic Data...")
            generator = SOFCDataGenerator()
            generator.generate_operational_timeseries(duration_days=365)
            generator.generate_economic_analysis()
            generator.generate_reliability_data()
            generator.generate_sensitivity_analysis()
            
            # Create visualizations
            print("\n[2/2] Creating Visualizations...")
            os.chdir("scripts")
            visualizer = SOFCDataVisualizer()
            
            viz_dir = Path("../visualizations")
            viz_dir.mkdir(exist_ok=True)
            
            visualizer.plot_efficiency_curves(save_path=viz_dir / "efficiency_curves.png")
            visualizer.plot_fuel_comparison(save_path=viz_dir / "fuel_comparison.html")
            visualizer.plot_power_density_analysis(save_path=viz_dir / "power_density.png")
            visualizer.plot_manufacturer_comparison(save_path=viz_dir / "manufacturer_comparison.html")
            visualizer.plot_nigeria_scenarios(save_path=viz_dir / "nigeria_scenarios.html")
            
            os.chdir("..")
            
            print("\n✓ Complete analysis finished successfully!")
            
        elif choice == "4":
            print("\n" + "-"*50)
            print(" DATASET STATISTICS")
            print("-"*50)
            
            # Count files
            raw_files = list(Path("data/raw").glob("*.json"))
            processed_files = list(Path("data/processed").glob("*.json"))
            simulated_files = list(Path("data/simulated").glob("*.json")) if Path("data/simulated").exists() else []
            viz_files = list(Path("visualizations").glob("*")) if Path("visualizations").exists() else []
            
            print(f"\n📁 Raw Data Files: {len(raw_files)}")
            for f in raw_files:
                size_kb = f.stat().st_size / 1024
                print(f"   • {f.name} ({size_kb:.1f} KB)")
            
            print(f"\n📁 Processed Data Files: {len(processed_files)}")
            for f in processed_files:
                size_kb = f.stat().st_size / 1024
                print(f"   • {f.name} ({size_kb:.1f} KB)")
            
            print(f"\n📁 Simulated Data Files: {len(simulated_files)}")
            for f in simulated_files:
                size_kb = f.stat().st_size / 1024
                print(f"   • {f.name} ({size_kb:.1f} KB)")
            
            print(f"\n📊 Visualizations: {len(viz_files)}")
            for f in viz_files:
                size_kb = f.stat().st_size / 1024
                print(f"   • {f.name} ({size_kb:.1f} KB)")
            
            # Dataset summary
            print("\n" + "-"*50)
            print(" KEY METRICS")
            print("-"*50)
            print("• SOFC Manufacturers analyzed: 7")
            print("• Fuel types covered: 5")
            print("• Nigeria deployment scenarios: 8")
            print("• Operating temperature range: 550-950°C")
            print("• Efficiency range: 50-65% (LHV)")
            print("• Power range: 1.5 kW - 10 MW")
            print("• Cost range: $3,500-6,000/kW")
            print("• Nigeria suitability ratings: 6.5-8.5/10")
            
        elif choice == "5":
            print("\n" + "="*50)
            print(" Thank you for using the SOFC Nigeria Dataset!")
            print("="*50)
            break
        
        else:
            print("\n⚠ Invalid option. Please select 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Program interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()