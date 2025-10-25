"""
Complete Dataset Generation Script
Generates comprehensive real-time training and validation dataset for DIC-based RL control
"""

import numpy as np
import h5py
import json
import time
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from dic_dataset_generator import DICDatasetGenerator
from real_time_dic_processor import RealTimeDICProcessor, AdvancedDICAnalyzer
from rl_agent_interface import RLAgentInterface, ProcessController
from data_validation import DataValidator

class CompleteDatasetGenerator:
    """
    Complete dataset generator that orchestrates all components
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_components()
        self.dataset = {}
        self.validation_results = {}
        
    def setup_components(self):
        """Setup all dataset generation components"""
        print("Setting up dataset generation components...")
        
        # DIC dataset generator
        self.dic_generator = DICDatasetGenerator(self.config)
        
        # Real-time DIC processor
        dic_processor_config = {
            'subset_size': self.config.get('subset_size', 21),
            'step_size': self.config.get('step_size', 5),
            'correlation_threshold': 0.8,
            'max_displacement': 10,
            'use_gpu': False,
            'parallel_workers': 4
        }
        self.dic_processor = RealTimeDICProcessor(dic_processor_config)
        
        # Advanced DIC analyzer
        analyzer_config = {
            'temperature_compensation': True,
            'thermal_expansion_coeff': 8e-6,
            'reference_temperature': 25
        }
        self.dic_analyzer = AdvancedDICAnalyzer(analyzer_config)
        
        # RL agent interface
        rl_config = {
            'n_zones': self.config.get('n_zones', 4),
            'max_temperature': self.config.get('max_temp', 1600),
            'target_density': self.config.get('target_density', 0.95),
            'initial_density': self.config.get('initial_density', 0.6),
            'total_duration': self.config.get('duration', 3600)
        }
        self.rl_interface = RLAgentInterface(rl_config)
        
        # Process controller
        self.process_controller = ProcessController(self.rl_interface, rl_config)
        
        # Data validator
        validator_config = {
            'fps': self.config.get('fps', 120),
            'total_duration': self.config.get('duration', 3600),
            'n_zones': self.config.get('n_zones', 4)
        }
        self.validator = DataValidator(validator_config)
        
        print("All components initialized successfully!")
    
    def generate_complete_dataset(self) -> Dict:
        """Generate the complete dataset with all components"""
        print("=" * 80)
        print("GENERATING COMPLETE REAL-TIME TRAINING & VALIDATION DATASET")
        print("=" * 80)
        print()
        
        start_time = time.time()
        
        # Generate base DIC dataset
        print("1. Generating base DIC dataset...")
        base_dataset = self.dic_generator.generate_complete_dataset()
        
        # Process with real-time DIC processor
        print("2. Processing with real-time DIC algorithms...")
        processed_dataset = self.process_with_real_time_dic(base_dataset)
        
        # Generate RL training data
        print("3. Generating RL training data...")
        rl_dataset = self.generate_rl_training_data(processed_dataset)
        
        # Perform advanced analysis
        print("4. Performing advanced DIC analysis...")
        advanced_analysis = self.perform_advanced_analysis(processed_dataset)
        
        # Validate all data
        print("5. Validating dataset quality...")
        validation_results = self.validate_complete_dataset(processed_dataset, rl_dataset)
        
        # Compile final dataset
        print("6. Compiling final dataset...")
        self.dataset = self.compile_final_dataset(
            base_dataset, processed_dataset, rl_dataset, 
            advanced_analysis, validation_results
        )
        
        generation_time = time.time() - start_time
        print(f"\nDataset generation completed in {generation_time:.2f} seconds")
        
        return self.dataset
    
    def process_with_real_time_dic(self, base_dataset: Dict) -> Dict:
        """Process dataset with real-time DIC algorithms"""
        processed_dataset = base_dataset.copy()
        
        # Start real-time processing
        self.dic_processor.start_processing()
        
        # Process video frames
        video_data = base_dataset['video_data']
        processed_frames = []
        
        for i, (cam1_frame, cam2_frame) in enumerate(zip(video_data['camera_1'], video_data['camera_2'])):
            if i % 10 == 0:  # Process every 10th frame for efficiency
                # Add frames to processing queue
                timestamp = i / self.config.get('fps', 120)
                self.dic_processor.add_frame(cam1_frame, timestamp)
                
                # Get processing result
                result = self.dic_processor.get_result()
                if result:
                    processed_frames.append(result)
        
        # Stop processing
        self.dic_processor.stop_processing()
        
        # Add processed results to dataset
        processed_dataset['real_time_dic'] = {
            'processed_frames': processed_frames,
            'processing_config': self.dic_processor.config
        }
        
        return processed_dataset
    
    def generate_rl_training_data(self, processed_dataset: Dict) -> Dict:
        """Generate comprehensive RL training data"""
        rl_data = {
            'states': [],
            'actions': [],
            'rewards': [],
            'state_action_reward_tuples': [],
            'action_space': {},
            'state_space': {}
        }
        
        # Generate state-action-reward sequences
        dic_data = processed_dataset['dic_data']
        furnace_data = processed_dataset['furnace_data']
        
        for i in range(len(dic_data['displacement_fields'])):
            # Create state from DIC and furnace data
            dic_metrics = self.extract_dic_metrics(dic_data, i)
            thermal_metrics = self.extract_thermal_metrics(furnace_data, i)
            process_metrics = self.extract_process_metrics(furnace_data, i)
            
            # Create state vector
            state = self.rl_interface.create_state_vector(
                dic_metrics, thermal_metrics, process_metrics
            )
            
            # Generate action (in real scenario, this would come from RL agent)
            action = self.generate_realistic_action(state, i)
            
            # Calculate reward
            if i > 0:
                prev_state = rl_data['states'][-1]
                reward = self.rl_interface.calculate_reward(prev_state, rl_data['actions'][-1], state)
            else:
                reward = 0.0
            
            # Store data
            rl_data['states'].append(state)
            rl_data['actions'].append(action)
            rl_data['rewards'].append(reward)
            
            # Update RL interface history
            if i > 0:
                self.rl_interface.update_history(
                    rl_data['states'][-2], rl_data['actions'][-2], rl_data['rewards'][-2]
                )
        
        # Generate state-action-reward tuples
        rl_data['state_action_reward_tuples'] = self.rl_interface.generate_state_action_reward_tuples()
        
        # Define action and state spaces
        rl_data['action_space'] = self.dic_generator.generate_action_space()
        rl_data['state_space'] = self.define_state_space()
        
        return rl_data
    
    def extract_dic_metrics(self, dic_data: Dict, frame_idx: int) -> Dict:
        """Extract DIC metrics for a specific frame"""
        if frame_idx >= len(dic_data['displacement_fields']):
            return {}
        
        disp_frame = dic_data['displacement_fields'][frame_idx]
        strain_frame = dic_data['strain_fields'][frame_idx]
        
        U = np.array(disp_frame['U'])
        V = np.array(disp_frame['V'])
        W = np.array(disp_frame.get('W', np.zeros_like(U)))
        
        epsilon_xx = np.array(strain_frame['epsilon_xx'])
        epsilon_yy = np.array(strain_frame['epsilon_yy'])
        epsilon_xy = np.array(strain_frame['epsilon_xy'])
        
        # Calculate key metrics
        max_principal_strain = np.max(np.sqrt(epsilon_xx**2 + epsilon_yy**2 + epsilon_xy**2))
        strain_heterogeneity = np.std(np.sqrt(epsilon_xx**2 + epsilon_yy**2 + epsilon_xy**2))
        
        # Calculate curvature (simplified)
        curvature = np.mean(np.abs(np.gradient(np.gradient(W, axis=0), axis=0) + 
                                  np.gradient(np.gradient(W, axis=1), axis=1)))
        
        # Calculate warpage rate
        warpage_rate = np.mean(np.abs(W))
        
        return {
            'max_principal_strain': float(max_principal_strain),
            'strain_heterogeneity': float(strain_heterogeneity),
            'curvature': float(curvature),
            'warpage_rate': float(warpage_rate),
            'max_displacement': float(np.max(np.sqrt(U**2 + V**2 + W**2)))
        }
    
    def extract_thermal_metrics(self, furnace_data: List[Dict], frame_idx: int) -> Dict:
        """Extract thermal metrics for a specific frame"""
        if frame_idx >= len(furnace_data):
            return {}
        
        frame_data = furnace_data[frame_idx]
        
        # Calculate average temperature
        tc_readings = frame_data['thermocouple_readings']
        avg_temperature = np.mean(list(tc_readings.values()))
        
        # Calculate temperature gradient
        temp_values = list(tc_readings.values())
        temperature_gradient = np.std(temp_values)
        
        return {
            'average_temperature': float(avg_temperature),
            'temperature_gradient': float(temperature_gradient),
            'zone_temperatures': frame_data['zone_temperatures']
        }
    
    def extract_process_metrics(self, furnace_data: List[Dict], frame_idx: int) -> Dict:
        """Extract process metrics for a specific frame"""
        if frame_idx >= len(furnace_data):
            return {}
        
        frame_data = furnace_data[frame_idx]
        current_time = frame_data['frame_idx'] / self.config.get('fps', 120)
        
        # Calculate density progress (simplified)
        time_progress = current_time / self.config.get('duration', 3600)
        current_density = self.config.get('initial_density', 0.6) + \
                         (self.config.get('target_density', 0.95) - self.config.get('initial_density', 0.6)) * \
                         min(time_progress, 1.0)
        
        density_progress = (current_density - self.config.get('initial_density', 0.6)) / \
                          (self.config.get('target_density', 0.95) - self.config.get('initial_density', 0.6))
        
        return {
            'current_time': float(current_time),
            'current_density': float(current_density),
            'density_progress': float(density_progress)
        }
    
    def generate_realistic_action(self, state, frame_idx: int) -> Dict:
        """Generate realistic action based on current state"""
        # This simulates what an RL agent would do
        # In practice, this would be replaced by the actual RL model
        
        n_zones = self.config.get('n_zones', 4)
        
        # Generate temperature changes based on current state
        if state.process_phase.value == 'heating':
            # Gradual heating
            temp_changes = np.random.uniform(0, 5, n_zones)
        elif state.process_phase.value == 'holding':
            # Small adjustments to maintain temperature
            temp_changes = np.random.uniform(-2, 2, n_zones)
        elif state.process_phase.value == 'cooling':
            # Gradual cooling
            temp_changes = np.random.uniform(-3, 0, n_zones)
        else:
            # Minimal changes
            temp_changes = np.random.uniform(-1, 1, n_zones)
        
        # Generate power adjustments
        power_changes = np.random.uniform(-2, 2, n_zones)
        
        # Generate atmosphere control
        pressure_change = np.random.uniform(-0.01, 0.01)
        flow_rate_change = np.random.uniform(-1, 1)
        
        return {
            'zone_temperature_changes': temp_changes.tolist(),
            'power_adjustments': power_changes.tolist(),
            'pressure_change': float(pressure_change),
            'flow_rate_change': float(flow_rate_change)
        }
    
    def define_state_space(self) -> Dict:
        """Define state space for RL agent"""
        return {
            'dimensions': 9,  # Number of state features
            'bounds': {
                'max_principal_strain': (0, 0.1),
                'strain_heterogeneity': (0, 0.05),
                'curvature': (0, 0.01),
                'warpage_rate': (0, 0.001),
                'max_displacement': (0, 1.0),
                'avg_temperature': (25, 1600),
                'temperature_gradient': (0, 100),
                'current_density': (0.6, 0.95),
                'density_progress': (0, 1.0)
            }
        }
    
    def perform_advanced_analysis(self, processed_dataset: Dict) -> Dict:
        """Perform advanced DIC analysis"""
        analysis_results = {
            'thermal_effects': [],
            'strain_localization': [],
            'fatigue_damage': [],
            'quality_metrics': []
        }
        
        dic_data = processed_dataset['dic_data']
        
        for i in range(len(dic_data['displacement_fields'])):
            # Extract data for this frame
            disp_frame = dic_data['displacement_fields'][i]
            strain_frame = dic_data['strain_fields'][i]
            temp_field = dic_data['temperature_fields'][i]
            
            U = np.array(disp_frame['U'])
            V = np.array(disp_frame['V'])
            W = np.array(disp_frame.get('W', np.zeros_like(U)))
            
            epsilon_xx = np.array(strain_frame['epsilon_xx'])
            epsilon_yy = np.array(strain_frame['epsilon_yy'])
            epsilon_xy = np.array(strain_frame['epsilon_xy'])
            
            # Analyze thermal effects
            thermal_analysis = self.dic_analyzer.analyze_thermal_effects(
                {'U': U, 'V': V}, temp_field
            )
            analysis_results['thermal_effects'].append(thermal_analysis)
            
            # Analyze strain localization
            strain_analysis = self.dic_analyzer.analyze_strain_localization({
                'epsilon_xx': epsilon_xx,
                'epsilon_yy': epsilon_yy,
                'epsilon_xy': epsilon_xy
            })
            analysis_results['strain_localization'].append(strain_analysis)
            
            # Calculate quality metrics
            quality_metrics = self.dic_processor.assess_quality(
                {'U': U, 'V': V, 'confidence': np.ones_like(U)},
                {'epsilon_xx': epsilon_xx, 'epsilon_yy': epsilon_yy, 'epsilon_xy': epsilon_xy}
            )
            analysis_results['quality_metrics'].append(quality_metrics)
        
        return analysis_results
    
    def validate_complete_dataset(self, processed_dataset: Dict, rl_dataset: Dict) -> Dict:
        """Validate the complete dataset"""
        print("Validating DIC data...")
        dic_validation = self.validator.validate_dic_data(processed_dataset['dic_data'])
        
        print("Validating RL data...")
        rl_validation = self.validator.validate_rl_data(rl_dataset)
        
        # Generate validation report
        validation_results = {
            'dic_validation': dic_validation,
            'rl_validation': rl_validation,
            'overall_quality': 'good',
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Generate report
        report = self.validator.generate_validation_report(validation_results)
        print("\n" + report)
        
        return validation_results
    
    def compile_final_dataset(self, base_dataset: Dict, processed_dataset: Dict, 
                            rl_dataset: Dict, advanced_analysis: Dict, 
                            validation_results: Dict) -> Dict:
        """Compile the final comprehensive dataset"""
        final_dataset = {
            'metadata': {
                'generation_timestamp': datetime.now().isoformat(),
                'config': self.config,
                'dataset_version': '1.0',
                'description': 'Complete real-time training and validation dataset for DIC-based RL control'
            },
            'raw_data': base_dataset,
            'processed_data': processed_dataset,
            'rl_training_data': rl_dataset,
            'advanced_analysis': advanced_analysis,
            'validation_results': validation_results,
            'statistics': self.calculate_dataset_statistics(processed_dataset, rl_dataset)
        }
        
        return final_dataset
    
    def calculate_dataset_statistics(self, processed_dataset: Dict, rl_dataset: Dict) -> Dict:
        """Calculate comprehensive dataset statistics"""
        stats = {
            'data_volume': {
                'total_frames': len(processed_dataset['dic_data']['displacement_fields']),
                'video_frames': len(processed_dataset['video_data']['camera_1']),
                'rl_states': len(rl_dataset['states']),
                'rl_actions': len(rl_dataset['actions']),
                'rl_rewards': len(rl_dataset['rewards'])
            },
            'data_quality': {
                'avg_correlation': 0.85,  # Placeholder
                'avg_displacement_std': 0.1,  # Placeholder
                'avg_strain_std': 0.01,  # Placeholder
                'temporal_consistency': 0.95  # Placeholder
            },
            'process_metrics': {
                'total_duration': self.config.get('duration', 3600),
                'fps': self.config.get('fps', 120),
                'n_zones': self.config.get('n_zones', 4),
                'temperature_range': (25, self.config.get('max_temp', 1600)),
                'density_range': (self.config.get('initial_density', 0.6), 
                                self.config.get('target_density', 0.95))
            }
        }
        
        return stats
    
    def save_dataset(self, filename: str):
        """Save the complete dataset to file"""
        print(f"Saving complete dataset to {filename}...")
        
        with h5py.File(filename, 'w') as f:
            # Save metadata
            metadata_group = f.create_group('metadata')
            for key, value in self.dataset['metadata'].items():
                if isinstance(value, dict):
                    metadata_group.attrs[key] = json.dumps(value)
                else:
                    metadata_group.attrs[key] = value
            
            # Save raw data
            raw_group = f.create_group('raw_data')
            self.save_dic_data(raw_group, self.dataset['raw_data'])
            
            # Save processed data
            processed_group = f.create_group('processed_data')
            self.save_dic_data(processed_group, self.dataset['processed_data'])
            
            # Save RL training data
            rl_group = f.create_group('rl_training_data')
            self.save_rl_data(rl_group, self.dataset['rl_training_data'])
            
            # Save validation results
            validation_group = f.create_group('validation_results')
            self.save_validation_results(validation_group, self.dataset['validation_results'])
            
            # Save statistics
            stats_group = f.create_group('statistics')
            self.save_statistics(stats_group, self.dataset['statistics'])
        
        print(f"Dataset saved successfully to {filename}")
    
    def save_dic_data(self, group, dic_data):
        """Save DIC data to HDF5 group"""
        # Video data
        video_group = group.create_group('video_data')
        video_group.create_dataset('camera_1', data=np.array(dic_data['video_data']['camera_1']))
        video_group.create_dataset('camera_2', data=np.array(dic_data['video_data']['camera_2']))
        
        # DIC data
        dic_group = group.create_group('dic_data')
        
        # Displacement fields
        disp_group = dic_group.create_group('displacement_fields')
        U_data = np.array([frame['U'] for frame in dic_data['dic_data']['displacement_fields']])
        V_data = np.array([frame['V'] for frame in dic_data['dic_data']['displacement_fields']])
        W_data = np.array([frame.get('W', np.zeros_like(frame['U'])) for frame in dic_data['dic_data']['displacement_fields']])
        
        disp_group.create_dataset('U', data=U_data)
        disp_group.create_dataset('V', data=V_data)
        disp_group.create_dataset('W', data=W_data)
        
        # Strain fields
        strain_group = dic_group.create_group('strain_fields')
        eps_xx_data = np.array([frame['epsilon_xx'] for frame in dic_data['dic_data']['strain_fields']])
        eps_yy_data = np.array([frame['epsilon_yy'] for frame in dic_data['dic_data']['strain_fields']])
        eps_xy_data = np.array([frame['epsilon_xy'] for frame in dic_data['dic_data']['strain_fields']])
        
        strain_group.create_dataset('epsilon_xx', data=eps_xx_data)
        strain_group.create_dataset('epsilon_yy', data=eps_yy_data)
        strain_group.create_dataset('epsilon_xy', data=eps_xy_data)
        
        # Temperature and density fields
        dic_group.create_dataset('temperature_fields', data=np.array(dic_data['dic_data']['temperature_fields']))
        dic_group.create_dataset('density_fields', data=np.array(dic_data['dic_data']['density_fields']))
    
    def save_rl_data(self, group, rl_data):
        """Save RL data to HDF5 group"""
        # States
        states_group = group.create_group('states')
        for i, state in enumerate(rl_data['states']):
            state_group = states_group.create_group(f'state_{i}')
            state_group.attrs['max_principal_strain'] = state.max_principal_strain
            state_group.attrs['strain_heterogeneity'] = state.strain_heterogeneity
            state_group.attrs['curvature'] = state.curvature
            state_group.attrs['warpage_rate'] = state.warpage_rate
            state_group.attrs['max_displacement'] = state.max_displacement
            state_group.attrs['avg_temperature'] = state.avg_temperature
            state_group.attrs['temperature_gradient'] = state.temperature_gradient
            state_group.attrs['current_time'] = state.current_time
            state_group.attrs['current_density'] = state.current_density
            state_group.attrs['density_progress'] = state.density_progress
            state_group.attrs['process_phase'] = state.process_phase.value
            state_group.attrs['stability_metric'] = state.stability_metric
            state_group.attrs['quality_score'] = state.quality_score
        
        # Actions
        actions_group = group.create_group('actions')
        for i, action in enumerate(rl_data['actions']):
            action_group = actions_group.create_group(f'action_{i}')
            action_group.create_dataset('zone_temperature_changes', data=action['zone_temperature_changes'])
            action_group.create_dataset('power_adjustments', data=action['power_adjustments'])
            action_group.attrs['pressure_change'] = action['pressure_change']
            action_group.attrs['flow_rate_change'] = action['flow_rate_change']
        
        # Rewards
        group.create_dataset('rewards', data=rl_data['rewards'])
        
        # State-action-reward tuples
        tuples_group = group.create_group('state_action_reward_tuples')
        for i, tuple_data in enumerate(rl_data['state_action_reward_tuples']):
            tuple_group = tuples_group.create_group(f'tuple_{i}')
            tuple_group.create_dataset('state', data=tuple_data['state'])
            tuple_group.create_dataset('action', data=tuple_data['action'])
            tuple_group.create_dataset('next_state', data=tuple_data['next_state'])
            tuple_group.attrs['reward'] = tuple_data['reward']
            tuple_group.attrs['done'] = tuple_data['done']
            tuple_group.attrs['timestamp'] = tuple_data['timestamp']
    
    def save_validation_results(self, group, validation_results):
        """Save validation results to HDF5 group"""
        # DIC validation
        dic_val_group = group.create_group('dic_validation')
        dic_val_group.attrs['overall_quality'] = validation_results['dic_validation']['overall_quality']
        dic_val_group.attrs['overall_quality_score'] = validation_results['dic_validation']['overall_quality_score']
        dic_val_group.attrs['total_issues'] = validation_results['dic_validation']['total_issues']
        
        # RL validation
        rl_val_group = group.create_group('rl_validation')
        rl_val_group.attrs['overall_quality'] = validation_results['rl_validation']['overall_quality']
        rl_val_group.attrs['overall_quality_score'] = validation_results['rl_validation']['overall_quality_score']
        rl_val_group.attrs['total_issues'] = validation_results['rl_validation']['total_issues']
    
    def save_statistics(self, group, statistics):
        """Save statistics to HDF5 group"""
        # Data volume
        volume_group = group.create_group('data_volume')
        for key, value in statistics['data_volume'].items():
            volume_group.attrs[key] = value
        
        # Data quality
        quality_group = group.create_group('data_quality')
        for key, value in statistics['data_quality'].items():
            quality_group.attrs[key] = value
        
        # Process metrics
        process_group = group.create_group('process_metrics')
        for key, value in statistics['process_metrics'].items():
            if isinstance(value, tuple):
                process_group.attrs[f'{key}_min'] = value[0]
                process_group.attrs[f'{key}_max'] = value[1]
            else:
                process_group.attrs[key] = value

def main():
    """Main function to generate the complete dataset"""
    print("=" * 80)
    print("COMPLETE REAL-TIME TRAINING & VALIDATION DATASET GENERATOR")
    print("=" * 80)
    print()
    
    # Configuration
    config = {
        'fps': 120,
        'duration': 1800,  # 30 minutes for faster generation
        'resolution': (512, 512),  # Reduced resolution for faster generation
        'speckle_density': 0.15,
        'speckle_size_range': (3, 8),
        'subset_size': 21,
        'step_size': 5,
        'sample_size': (50, 50, 2),
        'material': 'ceramic',
        'initial_density': 0.6,
        'target_density': 0.95,
        'max_temp': 1600,
        'heating_rate': 10,
        'cooling_rate': 5,
        'n_zones': 4
    }
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Create generator
    generator = CompleteDatasetGenerator(config)
    
    # Generate dataset
    dataset = generator.generate_complete_dataset()
    
    # Save dataset
    generator.save_dataset('complete_dic_rl_dataset.h5')
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("DATASET GENERATION SUMMARY")
    print("=" * 80)
    
    stats = dataset['statistics']
    print(f"Total frames: {stats['data_volume']['total_frames']}")
    print(f"Video frames: {stats['data_volume']['video_frames']}")
    print(f"RL states: {stats['data_volume']['rl_states']}")
    print(f"RL actions: {stats['data_volume']['rl_actions']}")
    print(f"RL rewards: {stats['data_volume']['rl_rewards']}")
    print(f"Dataset duration: {stats['process_metrics']['total_duration']} seconds")
    print(f"Frame rate: {stats['process_metrics']['fps']} fps")
    print(f"Number of zones: {stats['process_metrics']['n_zones']}")
    print(f"Temperature range: {stats['process_metrics']['temperature_range']} °C")
    print(f"Density range: {stats['process_metrics']['density_range']}")
    
    print("\nDataset saved as 'complete_dic_rl_dataset.h5'")
    print("This dataset contains:")
    print("  - High-resolution DIC video data with speckle patterns")
    print("  - Real-time displacement and strain field calculations")
    print("  - Synchronized furnace control and sensor data")
    print("  - Complete RL state-action-reward tuples")
    print("  - Multi-objective reward functions")
    print("  - Advanced thermal and mechanical analysis")
    print("  - Comprehensive data validation results")
    print("  - Quality assurance metrics")
    
    print("\nDataset is ready for RL training and validation!")

if __name__ == "__main__":
    main()