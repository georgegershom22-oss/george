#!/usr/bin/env python3
"""
Data Validation Module
Validates the generated dataset for physical consistency and data integrity
"""

import numpy as np
import pandas as pd
import h5py
import json
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class DataValidator:
    """Validates generated dataset for physical consistency and data integrity."""
    
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.validation_results = {}
        
    def _load_config(self, config_path):
        """Load configuration file."""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            # Default configuration
            return {
                'validation': {
                    'check_data_integrity': True,
                    'validate_timestamps': True,
                    'check_physical_constraints': True,
                    'validate_strain_continuity': True,
                    'check_temperature_monotonicity': False
                }
            }
    
    def validate_dataset(self, dataset_path: str) -> Dict:
        """Validate complete dataset."""
        print("Starting dataset validation...")
        
        validation_results = {
            'data_integrity': self._validate_data_integrity(dataset_path),
            'timestamps': self._validate_timestamps(dataset_path),
            'physical_constraints': self._validate_physical_constraints(dataset_path),
            'strain_continuity': self._validate_strain_continuity(dataset_path),
            'temperature_consistency': self._validate_temperature_consistency(dataset_path),
            'reward_function': self._validate_reward_function(dataset_path),
            'state_representation': self._validate_state_representation(dataset_path)
        }
        
        # Overall validation score
        validation_results['overall_score'] = self._calculate_overall_score(validation_results)
        
        self.validation_results = validation_results
        return validation_results
    
    def validate_data_integrity(self, dataset_path: str) -> Dict:
        """Validate basic data integrity."""
        return self._validate_data_integrity(dataset_path)
    
    def validate_timestamps(self, dataset_path: str) -> Dict:
        """Validate timestamp consistency."""
        return self._validate_timestamps(dataset_path)
    
    def validate_physical_constraints(self, dataset_path: str) -> Dict:
        """Validate physical constraints."""
        return self._validate_physical_constraints(dataset_path)
    
    def validate_strain_continuity(self, dataset_path: str) -> Dict:
        """Validate strain field continuity."""
        return self._validate_strain_continuity(dataset_path)
    
    def validate_temperature_consistency(self, dataset_path: str) -> Dict:
        """Validate temperature consistency across sensors."""
        return self._validate_temperature_consistency(dataset_path)
    
    def validate_reward_function(self, dataset_path: str) -> Dict:
        """Validate reward function consistency."""
        return self._validate_reward_function(dataset_path)
    
    def validate_state_representation(self, dataset_path: str) -> Dict:
        """Validate state representation consistency."""
        return self._validate_state_representation(dataset_path)
    
    def _validate_data_integrity(self, dataset_path: str) -> Dict:
        """Validate basic data integrity."""
        print("Validating data integrity...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            # Load HDF5 dataset
            with h5py.File(f"{dataset_path}/training_data.h5", 'r') as f:
                # Check required datasets exist
                required_datasets = ['states', 'actions', 'rewards', 'timestamps', 'episodes', 'timesteps']
                for dataset in required_datasets:
                    if dataset not in f:
                        results['issues'].append(f"Missing required dataset: {dataset}")
                        results['passed'] = False
                
                # Check data shapes and types
                if 'states' in f:
                    states = f['states'][:]
                    results['statistics']['num_states'] = len(states)
                    results['statistics']['state_dim'] = states.shape[1] if len(states.shape) > 1 else 0
                    
                    # Check for NaN or infinite values
                    if np.any(np.isnan(states)) or np.any(np.isinf(states)):
                        results['issues'].append("States contain NaN or infinite values")
                        results['passed'] = False
                
                if 'actions' in f:
                    actions = f['actions'][:]
                    results['statistics']['num_actions'] = len(actions)
                    results['statistics']['action_dim'] = actions.shape[1] if len(actions.shape) > 1 else 0
                    
                    if np.any(np.isnan(actions)) or np.any(np.isinf(actions)):
                        results['issues'].append("Actions contain NaN or infinite values")
                        results['passed'] = False
                
                if 'rewards' in f:
                    rewards = f['rewards'][:]
                    results['statistics']['num_rewards'] = len(rewards)
                    results['statistics']['reward_range'] = [np.min(rewards), np.max(rewards)]
                    
                    if np.any(np.isnan(rewards)) or np.any(np.isinf(rewards)):
                        results['issues'].append("Rewards contain NaN or infinite values")
                        results['passed'] = False
                
        except Exception as e:
            results['issues'].append(f"Error loading dataset: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _validate_timestamps(self, dataset_path: str) -> Dict:
        """Validate timestamp consistency."""
        print("Validating timestamps...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            with h5py.File(f"{dataset_path}/training_data.h5", 'r') as f:
                if 'timestamps' in f:
                    timestamps = f['timestamps'][:]
                    episodes = f['episodes'][:]
                    
                    # Check timestamp monotonicity within episodes
                    unique_episodes = np.unique(episodes)
                    for episode in unique_episodes:
                        episode_mask = episodes == episode
                        episode_timestamps = timestamps[episode_mask]
                        
                        if not np.all(np.diff(episode_timestamps) >= 0):
                            results['issues'].append(f"Non-monotonic timestamps in episode {episode}")
                            results['passed'] = False
                    
                    results['statistics']['timestamp_range'] = [np.min(timestamps), np.max(timestamps)]
                    results['statistics']['num_episodes'] = len(unique_episodes)
                    
        except Exception as e:
            results['issues'].append(f"Error validating timestamps: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _validate_physical_constraints(self, dataset_path: str) -> Dict:
        """Validate physical constraints."""
        print("Validating physical constraints...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            # Load detailed CSV data
            df = pd.read_csv(f"{dataset_path}/detailed_data.csv")
            
            # Check temperature constraints
            if 'max_temperature' in df.columns:
                max_temp = df['max_temperature'].max()
                min_temp = df['max_temperature'].min()
                
                if max_temp > 2000:  # Unrealistic temperature
                    results['issues'].append(f"Maximum temperature too high: {max_temp}°C")
                    results['passed'] = False
                
                if min_temp < 0:  # Negative temperature
                    results['issues'].append(f"Minimum temperature too low: {min_temp}°C")
                    results['passed'] = False
                
                results['statistics']['temperature_range'] = [min_temp, max_temp]
            
            # Check strain constraints
            if 'max_von_mises_strain' in df.columns:
                max_strain = df['max_von_mises_strain'].max()
                
                if max_strain > 0.1:  # Unrealistic strain
                    results['issues'].append(f"Maximum strain too high: {max_strain}")
                    results['passed'] = False
                
                results['statistics']['max_strain'] = max_strain
            
            # Check power constraints
            if 'total_power' in df.columns:
                max_power = df['total_power'].max()
                
                if max_power > 600:  # 6 zones * 100kW max
                    results['issues'].append(f"Total power too high: {max_power}kW")
                    results['passed'] = False
                
                results['statistics']['max_power'] = max_power
            
        except Exception as e:
            results['issues'].append(f"Error validating physical constraints: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _validate_strain_continuity(self, dataset_path: str) -> Dict:
        """Validate strain field continuity."""
        print("Validating strain continuity...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            df = pd.read_csv(f"{dataset_path}/detailed_data.csv")
            
            # Check strain field smoothness
            strain_columns = [col for col in df.columns if 'strain' in col.lower()]
            
            for col in strain_columns:
                if col in df.columns:
                    strain_values = df[col].values
                    
                    # Check for sudden jumps (discontinuities)
                    diff = np.abs(np.diff(strain_values))
                    large_jumps = np.sum(diff > 3 * np.std(diff))
                    
                    if large_jumps > len(diff) * 0.05:  # More than 5% large jumps
                        results['issues'].append(f"Strain field discontinuities in {col}: {large_jumps} large jumps")
                        results['passed'] = False
                    
                    results['statistics'][f'{col}_jumps'] = large_jumps
                    results['statistics'][f'{col}_std'] = np.std(strain_values)
            
        except Exception as e:
            results['issues'].append(f"Error validating strain continuity: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _validate_temperature_consistency(self, dataset_path: str) -> Dict:
        """Validate temperature consistency across sensors."""
        print("Validating temperature consistency...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            df = pd.read_csv(f"{dataset_path}/detailed_data.csv")
            
            # Check temperature gradient consistency
            if 'max_temperature' in df.columns and 'min_temperature' in df.columns:
                temp_gradient = df['max_temperature'] - df['min_temperature']
                max_gradient = temp_gradient.max()
                
                if max_gradient > 200:  # Unrealistic temperature gradient
                    results['issues'].append(f"Temperature gradient too high: {max_gradient}°C")
                    results['passed'] = False
                
                results['statistics']['max_temp_gradient'] = max_gradient
                results['statistics']['mean_temp_gradient'] = temp_gradient.mean()
            
        except Exception as e:
            results['issues'].append(f"Error validating temperature consistency: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _validate_reward_function(self, dataset_path: str) -> Dict:
        """Validate reward function consistency."""
        print("Validating reward function...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            df = pd.read_csv(f"{dataset_path}/detailed_data.csv")
            
            # Check reward distribution
            if 'reward' in df.columns:
                rewards = df['reward'].values
                
                # Check for reasonable reward range
                if np.min(rewards) < -1000 or np.max(rewards) > 1000:
                    results['issues'].append(f"Reward range too extreme: [{np.min(rewards)}, {np.max(rewards)}]")
                    results['passed'] = False
                
                # Check for reward consistency
                reward_std = np.std(rewards)
                if reward_std > 100:
                    results['issues'].append(f"Reward variance too high: {reward_std}")
                    results['passed'] = False
                
                results['statistics']['reward_range'] = [np.min(rewards), np.max(rewards)]
                results['statistics']['reward_std'] = reward_std
                results['statistics']['reward_mean'] = np.mean(rewards)
            
        except Exception as e:
            results['issues'].append(f"Error validating reward function: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _validate_state_representation(self, dataset_path: str) -> Dict:
        """Validate state representation consistency."""
        print("Validating state representation...")
        
        results = {
            'passed': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            with h5py.File(f"{dataset_path}/training_data.h5", 'r') as f:
                if 'states' in f:
                    states = f['states'][:]
                    
                    # Check state vector consistency
                    state_dim = states.shape[1]
                    if state_dim < 10:
                        results['issues'].append(f"State dimension too low: {state_dim}")
                        results['passed'] = False
                    
                    # Check for state normalization
                    state_std = np.std(states, axis=0)
                    if np.any(state_std > 10):
                        results['issues'].append("State vectors not properly normalized")
                        results['passed'] = False
                    
                    results['statistics']['state_dim'] = state_dim
                    results['statistics']['state_std_range'] = [np.min(state_std), np.max(state_std)]
                    
        except Exception as e:
            results['issues'].append(f"Error validating state representation: {str(e)}")
            results['passed'] = False
        
        return results
    
    def _calculate_overall_score(self, validation_results: Dict) -> float:
        """Calculate overall validation score."""
        scores = []
        for category, results in validation_results.items():
            if category != 'overall_score' and isinstance(results, dict):
                if results['passed']:
                    scores.append(1.0)
                else:
                    # Penalty based on number of issues
                    penalty = min(0.5, len(results['issues']) * 0.1)
                    scores.append(1.0 - penalty)
        
        return np.mean(scores) if scores else 0.0
    
    def generate_validation_report(self, output_path: str = "validation_report.html"):
        """Generate comprehensive validation report."""
        print("Generating validation report...")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dataset Validation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .passed {{ color: green; font-weight: bold; }}
                .failed {{ color: red; font-weight: bold; }}
                .issue {{ background-color: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .statistics {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .score {{ font-size: 24px; font-weight: bold; color: {'green' if self.validation_results.get('overall_score', 0) > 0.8 else 'red'}; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Dataset Validation Report</h1>
                <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <div class="score">Overall Score: {self.validation_results.get('overall_score', 0):.2f}</div>
            </div>
        """
        
        for category, results in self.validation_results.items():
            if category == 'overall_score':
                continue
                
            status = "PASSED" if results['passed'] else "FAILED"
            status_class = "passed" if results['passed'] else "failed"
            
            html_content += f"""
            <div class="section">
                <h2>{category.replace('_', ' ').title()}</h2>
                <p class="{status_class}">Status: {status}</p>
            """
            
            if results['issues']:
                html_content += "<h3>Issues:</h3>"
                for issue in results['issues']:
                    html_content += f'<div class="issue">{issue}</div>'
            
            if results['statistics']:
                html_content += "<h3>Statistics:</h3>"
                for key, value in results['statistics'].items():
                    html_content += f'<div class="statistics"><strong>{key}:</strong> {value}</div>'
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Validation report saved to: {output_path}")
    
    def plot_validation_summary(self, output_path: str = "validation_summary.png"):
        """Generate validation summary plots."""
        print("Generating validation summary plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Overall score
        categories = [k for k in self.validation_results.keys() if k != 'overall_score']
        scores = [1.0 if self.validation_results[k]['passed'] else 0.5 for k in categories]
        
        axes[0, 0].bar(categories, scores)
        axes[0, 0].set_title('Validation Results by Category')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Issue count
        issue_counts = [len(self.validation_results[k]['issues']) for k in categories]
        axes[0, 1].bar(categories, issue_counts, color='red', alpha=0.7)
        axes[0, 1].set_title('Issues by Category')
        axes[0, 1].set_ylabel('Number of Issues')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Overall score pie chart
        overall_score = self.validation_results.get('overall_score', 0)
        axes[1, 0].pie([overall_score, 1 - overall_score], 
                       labels=['Passed', 'Failed'], 
                       colors=['green', 'red'],
                       autopct='%1.1f%%')
        axes[1, 0].set_title('Overall Validation Score')
        
        # Summary statistics
        axes[1, 1].text(0.1, 0.8, f"Total Categories: {len(categories)}", fontsize=12)
        axes[1, 1].text(0.1, 0.7, f"Passed: {sum(scores)}", fontsize=12)
        axes[1, 1].text(0.1, 0.6, f"Failed: {len(categories) - sum(scores)}", fontsize=12)
        axes[1, 1].text(0.1, 0.5, f"Overall Score: {overall_score:.2f}", fontsize=12)
        axes[1, 1].text(0.1, 0.4, f"Total Issues: {sum(issue_counts)}", fontsize=12)
        axes[1, 1].set_title('Summary Statistics')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Validation summary plot saved to: {output_path}")

def main():
    """Test the data validator."""
    validator = DataValidator()
    
    # Test with a sample dataset (if it exists)
    dataset_path = "real_time_training_dataset"
    
    if os.path.exists(dataset_path):
        validation_results = validator.validate_dataset(dataset_path)
        
        print("\nValidation Results:")
        for category, results in validation_results.items():
            if category != 'overall_score':
                status = "PASSED" if results['passed'] else "FAILED"
                print(f"{category}: {status}")
                if results['issues']:
                    for issue in results['issues']:
                        print(f"  - {issue}")
        
        print(f"\nOverall Score: {validation_results['overall_score']:.2f}")
        
        # Generate reports
        validator.generate_validation_report()
        validator.plot_validation_summary()
    else:
        print("No dataset found for validation. Please generate dataset first.")

if __name__ == "__main__":
    main()