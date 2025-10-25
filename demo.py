#!/usr/bin/env python3
"""
Demonstration Script
Shows how to use the Real-Time Training & Validation Dataset Generator
"""

import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from dataset_generator import DatasetGenerator
from advanced_data_generator import AdvancedDICGenerator, AdvancedFurnaceSimulator, DataVisualizer
from data_validator import DataValidator
from data_analyzer import DataAnalyzer

def demo_basic_generation():
    """Demonstrate basic dataset generation."""
    print("🎬 Demo 1: Basic Dataset Generation")
    print("="*50)
    
    # Create a small dataset for demonstration
    config = {
        'dic': {
            'width': 640,
            'height': 480,
            'fps': 30,
            'duration': 60  # 1 minute for demo
        },
        'furnace': {
            'num_zones': 3,
            'num_thermocouples': 6
        },
        'strain': {
            'subset_size': 16,
            'step_size': 8
        },
        'rl_state': {
            'state_dim': 20
        },
        'reward': {
            'weights': {'warpage': 1.0, 'strain': 0.5, 'density': 0.3}
        }
    }
    
    # Initialize generator
    generator = DatasetGenerator(config)
    
    # Generate single episode
    print("Generating single episode...")
    episodes = generator.generate_single_episode(
        episode_id=0,
        duration=60,
        material_type='alumina'
    )
    
    print(f"✅ Generated {len(episodes)} timesteps")
    print(f"📊 State dimension: {len(episodes[0]['state'])}")
    print(f"🎯 Action dimension: {len(episodes[0]['action'])}")
    print(f"🏆 Reward range: [{min(ep['reward'] for ep in episodes):.2f}, {max(ep['reward'] for ep in episodes):.2f}]")
    
    return episodes

def demo_advanced_features():
    """Demonstrate advanced DIC and furnace features."""
    print("\n🔬 Demo 2: Advanced Features")
    print("="*50)
    
    # Advanced DIC generator
    dic_gen = AdvancedDICGenerator(width=640, height=480, fps=30)
    
    # Generate speckle patterns at different temperatures
    print("Generating speckle patterns at different temperatures...")
    temps = [25, 400, 800, 1200]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for i, temp in enumerate(temps):
        pattern = dic_gen.generate_realistic_speckle_pattern(
            temperature=temp, 
            material_type='alumina'
        )
        
        row, col = i // 2, i % 2
        axes[row, col].imshow(pattern, cmap='gray')
        axes[row, col].set_title(f'Temperature: {temp}°C')
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.savefig('demo_speckle_patterns.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Advanced furnace simulator
    furnace = AdvancedFurnaceSimulator(num_zones=3, num_thermocouples=6)
    control_data = furnace.generate_realistic_control_sequence(300, 'sintering_cycle')
    
    print(f"✅ Generated {len(control_data)} control timesteps")
    print(f"🌡️  Temperature range: {min(data['thermocouple_temps'].mean() for data in control_data):.1f}°C - {max(data['thermocouple_temps'].mean() for data in control_data):.1f}°C")
    
    return control_data

def demo_validation():
    """Demonstrate data validation."""
    print("\n🔍 Demo 3: Data Validation")
    print("="*50)
    
    if os.path.exists("demo_dataset"):
        validator = DataValidator()
        validation_results = validator.validate_dataset("demo_dataset")
        
        print("Validation Results:")
        for category, results in validation_results.items():
            if category != 'overall_score':
                status = "✅ PASSED" if results['passed'] else "❌ FAILED"
                print(f"  {category}: {status}")
                if results['issues']:
                    for issue in results['issues']:
                        print(f"    - {issue}")
        
        print(f"\n🎯 Overall Score: {validation_results['overall_score']:.2f}")
        
        return validation_results
    else:
        print("No dataset found for validation. Run demo_basic_generation() first.")
        return None

def demo_analysis():
    """Demonstrate data analysis."""
    print("\n📈 Demo 4: Data Analysis")
    print("="*50)
    
    if os.path.exists("demo_dataset"):
        analyzer = DataAnalyzer("demo_dataset")
        
        # Quick analysis
        print("Running quick analysis...")
        
        # Reward analysis
        rewards = analyzer.df['reward'].values
        print(f"📊 Reward Statistics:")
        print(f"  Mean: {np.mean(rewards):.4f}")
        print(f"  Std: {np.std(rewards):.4f}")
        print(f"  Min: {np.min(rewards):.4f}")
        print(f"  Max: {np.max(rewards):.4f}")
        
        # State space analysis
        states = analyzer.data['states']
        print(f"\n🧠 State Space:")
        print(f"  Dimension: {states.shape[1]}")
        print(f"  Mean variance: {np.mean(np.var(states, axis=0)):.4f}")
        print(f"  Range: [{np.min(states):.4f}, {np.max(states):.4f}]")
        
        # Action space analysis
        actions = analyzer.data['actions']
        print(f"\n🎮 Action Space:")
        print(f"  Dimension: {actions.shape[1]}")
        print(f"  Mean: {np.mean(actions):.4f}")
        print(f"  Std: {np.std(actions):.4f}")
        
        return True
    else:
        print("No dataset found for analysis. Run demo_basic_generation() first.")
        return False

def demo_visualization():
    """Demonstrate visualization capabilities."""
    print("\n🎨 Demo 5: Visualization")
    print("="*50)
    
    # Create sample data for visualization
    print("Creating sample visualization data...")
    
    # Sample strain data
    x = np.linspace(0, 10, 100)
    y = np.linspace(0, 10, 100)
    X, Y = np.meshgrid(x, y)
    
    # Create sample strain field
    exx = 0.001 * np.sin(X) * np.cos(Y)
    eyy = 0.001 * np.cos(X) * np.sin(Y)
    exy = 0.0005 * np.sin(X + Y)
    
    strain_data = {
        'exx': exx,
        'eyy': eyy,
        'exy': exy,
        'e1': exx + eyy,
        'e2': exx - eyy,
        'e_vm': np.sqrt(0.5 * (exx**2 + eyy**2 + exy**2))
    }
    
    # Create displacement data
    u_field = 0.1 * np.sin(X) * np.cos(Y)
    v_field = 0.1 * np.cos(X) * np.sin(Y)
    
    displacement_data = {
        'u_field': u_field,
        'v_field': v_field
    }
    
    # Visualize
    visualizer = DataVisualizer()
    
    print("Generating strain field visualization...")
    visualizer.plot_strain_field(strain_data, "Sample Strain Field")
    
    print("Generating displacement field visualization...")
    visualizer.plot_displacement_field(u_field, v_field, "Sample Displacement Field")
    
    print("✅ Visualizations generated!")

def demo_complete_workflow():
    """Demonstrate complete workflow."""
    print("\n🚀 Demo 6: Complete Workflow")
    print("="*50)
    
    print("This demonstrates the complete workflow from generation to analysis...")
    
    # Step 1: Generate dataset
    print("\n1️⃣ Generating dataset...")
    episodes = demo_basic_generation()
    
    # Step 2: Validate dataset
    print("\n2️⃣ Validating dataset...")
    validation_results = demo_validation()
    
    # Step 3: Analyze dataset
    print("\n3️⃣ Analyzing dataset...")
    analysis_success = demo_analysis()
    
    # Step 4: Generate visualizations
    print("\n4️⃣ Generating visualizations...")
    demo_visualization()
    
    # Summary
    print("\n📋 Workflow Summary:")
    print(f"  ✅ Dataset generated: {len(episodes)} timesteps")
    print(f"  ✅ Validation completed: Score {validation_results['overall_score']:.2f}" if validation_results else "  ❌ Validation failed")
    print(f"  ✅ Analysis completed" if analysis_success else "  ❌ Analysis failed")
    print(f"  ✅ Visualizations generated")
    
    print("\n🎉 Complete workflow demonstration finished!")

def main():
    """Main demonstration function."""
    print("🎬 Real-Time Training & Validation Dataset Generator Demo")
    print("="*60)
    print("This demo shows the key features of the dataset generator.")
    print("="*60)
    
    try:
        # Run individual demos
        demo_basic_generation()
        demo_advanced_features()
        demo_validation()
        demo_analysis()
        demo_visualization()
        
        # Run complete workflow
        demo_complete_workflow()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\n📁 Check the generated files:")
        print("  - demo_dataset/ (generated dataset)")
        print("  - demo_speckle_patterns.png (speckle pattern visualization)")
        print("  - Various analysis plots and reports")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()