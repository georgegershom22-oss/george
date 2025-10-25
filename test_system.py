#!/usr/bin/env python3
"""
System Test Script
Tests all components of the dataset generation system
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from dataset_generator import DatasetGenerator, DICVideoGenerator, FurnaceController, StrainAnalyzer, RLStateRepresentation, RewardFunction
        print("  ✅ dataset_generator imported successfully")
    except ImportError as e:
        print(f"  ❌ dataset_generator import failed: {e}")
        return False
    
    try:
        from advanced_data_generator import AdvancedDICGenerator, AdvancedFurnaceSimulator, AdvancedStrainAnalyzer, DataVisualizer
        print("  ✅ advanced_data_generator imported successfully")
    except ImportError as e:
        print(f"  ❌ advanced_data_generator import failed: {e}")
        return False
    
    try:
        from data_validator import DataValidator
        print("  ✅ data_validator imported successfully")
    except ImportError as e:
        print(f"  ❌ data_validator import failed: {e}")
        return False
    
    try:
        from data_analyzer import DataAnalyzer
        print("  ✅ data_analyzer imported successfully")
    except ImportError as e:
        print(f"  ❌ data_analyzer import failed: {e}")
        return False
    
    return True

def test_dic_generator():
    """Test DIC video generator."""
    print("\n🎬 Testing DIC video generator...")
    
    try:
        from dataset_generator import DICVideoGenerator
        
        # Create generator
        generator = DICVideoGenerator(width=320, height=240, fps=30, duration=10)
        
        # Generate speckle pattern
        pattern = generator.generate_speckle_pattern()
        assert pattern.shape == (240, 320)
        assert pattern.dtype == np.uint8
        print("  ✅ Speckle pattern generation works")
        
        # Test thermal deformation
        temperature_profile = [25, 100, 200, 300, 400, 500, 600, 700, 800, 900]
        material_properties = {
            'thermal_expansion_base': 8e-6,
            'thermal_expansion_temp_factor': 1000
        }
        
        deformed, u_field, v_field = generator.simulate_thermal_deformation(
            pattern, 0, temperature_profile, material_properties
        )
        assert deformed.shape == (240, 320)
        assert u_field.shape == (240, 320)
        assert v_field.shape == (240, 320)
        print("  ✅ Thermal deformation simulation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ DIC generator test failed: {e}")
        return False

def test_furnace_controller():
    """Test furnace controller."""
    print("\n🔥 Testing furnace controller...")
    
    try:
        from dataset_generator import FurnaceController
        
        # Create controller
        controller = FurnaceController(num_zones=3, num_thermocouples=6)
        
        # Test control sequence generation
        control_data = controller.generate_control_sequence(60, 'sintering_cycle')
        assert len(control_data) > 0
        assert 'timestamp' in control_data[0]
        assert 'zone_powers' in control_data[0]
        assert 'thermocouple_temps' in control_data[0]
        print("  ✅ Control sequence generation works")
        
        # Test thermal response
        controller.update_zone_power(0, 50)
        controller.set_zone_temperature(0, 500)
        controller.simulate_thermal_response(1.0)
        assert len(controller.thermocouple_temps) == 6
        print("  ✅ Thermal response simulation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Furnace controller test failed: {e}")
        return False

def test_strain_analyzer():
    """Test strain analyzer."""
    print("\n📐 Testing strain analyzer...")
    
    try:
        from dataset_generator import StrainAnalyzer
        
        # Create analyzer
        analyzer = StrainAnalyzer(subset_size=16, step_size=8)
        
        # Create sample images
        ref_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        def_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        # Test displacement field computation
        u_field, v_field = analyzer.compute_displacement_field(ref_image, def_image)
        assert u_field.shape == (100, 100)
        assert v_field.shape == (100, 100)
        print("  ✅ Displacement field computation works")
        
        # Test strain field computation
        strain_data = analyzer.compute_strain_field(u_field, v_field)
        assert 'exx' in strain_data
        assert 'eyy' in strain_data
        assert 'exy' in strain_data
        assert 'e1' in strain_data
        assert 'e2' in strain_data
        assert 'e_vm' in strain_data
        print("  ✅ Strain field computation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Strain analyzer test failed: {e}")
        return False

def test_rl_components():
    """Test RL components."""
    print("\n🤖 Testing RL components...")
    
    try:
        from dataset_generator import RLStateRepresentation, RewardFunction
        
        # Test state representation
        state_rep = RLStateRepresentation(state_dim=20)
        
        # Create sample data
        strain_data = {
            'e1': np.random.rand(50, 50),
            'e2': np.random.rand(50, 50),
            'e_vm': np.random.rand(50, 50)
        }
        displacement_data = {
            'u_field': np.random.rand(50, 50),
            'v_field': np.random.rand(50, 50)
        }
        furnace_data = {
            'thermocouple_temps': np.random.rand(6),
            'zone_powers': np.random.rand(3)
        }
        
        # Test feature extraction
        dic_features = state_rep.extract_dic_features(strain_data, displacement_data)
        thermal_features = state_rep.extract_thermal_features(furnace_data)
        process_features = state_rep.extract_process_features(0, 100)
        
        assert len(dic_features) > 0
        assert len(thermal_features) > 0
        assert len(process_features) > 0
        print("  ✅ Feature extraction works")
        
        # Test state vector creation
        state = state_rep.create_state_vector(dic_features, thermal_features, process_features)
        assert len(state) == 20
        print("  ✅ State vector creation works")
        
        # Test reward function
        reward_func = RewardFunction()
        reward, components = reward_func.compute_reward(
            state, np.random.rand(3), state, strain_data, displacement_data
        )
        assert isinstance(reward, (int, float))
        assert isinstance(components, dict)
        print("  ✅ Reward function works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ RL components test failed: {e}")
        return False

def test_dataset_generator():
    """Test main dataset generator."""
    print("\n📊 Testing dataset generator...")
    
    try:
        from dataset_generator import DatasetGenerator
        
        # Create generator with minimal config
        config = {
            'dic': {'width': 160, 'height': 120, 'fps': 10, 'duration': 10},
            'furnace': {'num_zones': 2, 'num_thermocouples': 4},
            'strain': {'subset_size': 8, 'step_size': 4},
            'rl_state': {'state_dim': 10},
            'reward': {'weights': {'warpage': 1.0, 'strain': 0.5, 'density': 0.3}}
        }
        
        generator = DatasetGenerator(config)
        
        # Test single episode generation
        episodes = generator.generate_single_episode(
            episode_id=0,
            duration=10,
            material_type='alumina'
        )
        
        assert len(episodes) > 0
        assert 'state' in episodes[0]
        assert 'action' in episodes[0]
        assert 'reward' in episodes[0]
        print("  ✅ Dataset generation works")
        
        # Clean up
        import shutil
        if os.path.exists("test_dataset"):
            shutil.rmtree("test_dataset")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dataset generator test failed: {e}")
        return False

def test_validation():
    """Test data validation."""
    print("\n🔍 Testing data validation...")
    
    try:
        from data_validator import DataValidator
        
        # Create validator
        validator = DataValidator()
        
        # Test validation methods exist
        assert hasattr(validator, 'validate_dataset')
        assert hasattr(validator, 'validate_data_integrity')
        assert hasattr(validator, 'validate_timestamps')
        print("  ✅ Validation methods exist")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Validation test failed: {e}")
        return False

def test_analysis():
    """Test data analysis."""
    print("\n📈 Testing data analysis...")
    
    try:
        from data_analyzer import DataAnalyzer
        
        # Test analyzer methods exist
        assert hasattr(DataAnalyzer, 'analyze_reward_distribution')
        assert hasattr(DataAnalyzer, 'analyze_state_space')
        assert hasattr(DataAnalyzer, 'analyze_action_space')
        print("  ✅ Analysis methods exist")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Analysis test failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("🧪 Running System Tests")
    print("="*50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    tests = [
        ("Import Test", test_imports),
        ("DIC Generator Test", test_dic_generator),
        ("Furnace Controller Test", test_furnace_controller),
        ("Strain Analyzer Test", test_strain_analyzer),
        ("RL Components Test", test_rl_components),
        ("Dataset Generator Test", test_dataset_generator),
        ("Validation Test", test_validation),
        ("Analysis Test", test_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"  ✅ {test_name} PASSED")
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test function."""
    success = run_all_tests()
    
    if success:
        print("\n🚀 System is ready! You can now run:")
        print("  python generate_dataset.py --help")
        print("  python demo.py")
        sys.exit(0)
    else:
        print("\n❌ System has issues. Please fix the failing tests.")
        sys.exit(1)

if __name__ == "__main__":
    main()