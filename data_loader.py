#!/usr/bin/env python3
"""
Data Loader and Analysis Toolkit
for Real-Time Training & Validation Dataset

This module provides efficient data loading, preprocessing, and analysis
capabilities for the generated dataset.
"""

import numpy as np
import pandas as pd
import h5py
import json
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import interpolate, signal
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DatasetConfig:
    """Configuration for dataset loading and preprocessing."""
    dataset_dir: str = "real_time_dataset"
    batch_size: int = 32
    sequence_length: int = 10
    normalize_data: bool = True
    add_noise: bool = False
    noise_level: float = 0.01
    interpolation_method: str = 'linear'

class RealTimeDataLoader:
    """
    Efficient data loader for real-time training and validation dataset.
    """
    
    def __init__(self, config: DatasetConfig):
        """
        Initialize the data loader.
        
        Args:
            config: Dataset configuration
        """
        self.config = config
        self.metadata = self._load_metadata()
        self._normalization_params = None
        
    def _load_metadata(self) -> Dict:
        """Load dataset metadata."""
        with open(f"{self.config.dataset_dir}/metadata.json", 'r') as f:
            return json.load(f)
    
    def load_dic_data(self, frame_indices: Optional[List[int]] = None, 
                     fields: Optional[List[str]] = None) -> Dict:
        """
        Load DIC data with optional filtering.
        
        Args:
            frame_indices: Specific frames to load (if None, loads all)
            fields: Specific fields to load (if None, loads all)
            
        Returns:
            Dictionary containing requested DIC data
        """
        dic_data = {}
        
        with h5py.File(f"{self.config.dataset_dir}/dic_data.h5", 'r') as f:
            available_fields = list(f.keys())
            
            if fields is None:
                fields = available_fields
            
            for field in fields:
                if field in available_fields:
                    data = f[field][:]
                    
                    if frame_indices is not None:
                        data = data[frame_indices]
                    
                    dic_data[field] = data
        
        return dic_data
    
    def load_furnace_data(self, time_indices: Optional[List[int]] = None,
                         fields: Optional[List[str]] = None) -> Dict:
        """
        Load furnace control and sensor data.
        
        Args:
            time_indices: Specific time indices to load (if None, loads all)
            fields: Specific fields to load (if None, loads all)
            
        Returns:
            Dictionary containing requested furnace data
        """
        furnace_data = {}
        
        with h5py.File(f"{self.config.dataset_dir}/furnace_data.h5", 'r') as f:
            available_fields = list(f.keys())
            
            if fields is None:
                fields = available_fields
            
            for field in fields:
                if field in available_fields:
                    data = f[field][:]
                    
                    if time_indices is not None:
                        data = data[time_indices]
                    
                    furnace_data[field] = data
        
        return furnace_data
    
    def load_rl_data(self, tuple_indices: Optional[List[int]] = None,
                    fields: Optional[List[str]] = None) -> Dict:
        """
        Load RL training data.
        
        Args:
            tuple_indices: Specific tuple indices to load (if None, loads all)
            fields: Specific fields to load (if None, loads all)
            
        Returns:
            Dictionary containing requested RL data
        """
        rl_data = {}
        
        with h5py.File(f"{self.config.dataset_dir}/rl_data.h5", 'r') as f:
            available_fields = list(f.keys())
            
            if fields is None:
                fields = available_fields
            
            for field in fields:
                if field in available_fields:
                    data = f[field][:]
                    
                    if tuple_indices is not None:
                        data = data[tuple_indices]
                    
                    rl_data[field] = data
        
        return rl_data
    
    def create_sequence_dataset(self, sequence_length: int = None) -> Dict:
        """
        Create sequence dataset for time series models.
        
        Args:
            sequence_length: Length of sequences (if None, uses config value)
            
        Returns:
            Dictionary containing sequence data
        """
        if sequence_length is None:
            sequence_length = self.config.sequence_length
        
        # Load RL data
        rl_data = self.load_rl_data()
        states = rl_data['states']
        actions = rl_data['actions']
        rewards = rl_data['rewards']
        next_states = rl_data['next_states']
        
        # Create sequences
        num_sequences = len(states) - sequence_length + 1
        state_sequences = np.zeros((num_sequences, sequence_length, states.shape[1]))
        action_sequences = np.zeros((num_sequences, sequence_length, actions.shape[1]))
        reward_sequences = np.zeros((num_sequences, sequence_length))
        next_state_sequences = np.zeros((num_sequences, sequence_length, next_states.shape[1]))
        
        for i in range(num_sequences):
            state_sequences[i] = states[i:i+sequence_length]
            action_sequences[i] = actions[i:i+sequence_length]
            reward_sequences[i] = rewards[i:i+sequence_length]
            next_state_sequences[i] = next_states[i:i+sequence_length]
        
        return {
            'state_sequences': state_sequences,
            'action_sequences': action_sequences,
            'reward_sequences': reward_sequences,
            'next_state_sequences': next_state_sequences,
            'sequence_length': sequence_length,
            'num_sequences': num_sequences
        }
    
    def create_batch_loader(self, data_type: str = 'rl', 
                           batch_size: int = None) -> 'BatchLoader':
        """
        Create batch loader for training.
        
        Args:
            data_type: Type of data ('dic', 'furnace', 'rl')
            batch_size: Batch size (if None, uses config value)
            
        Returns:
            BatchLoader instance
        """
        if batch_size is None:
            batch_size = self.config.batch_size
        
        if data_type == 'rl':
            data = self.load_rl_data()
        elif data_type == 'dic':
            data = self.load_dic_data()
        elif data_type == 'furnace':
            data = self.load_furnace_data()
        else:
            raise ValueError("data_type must be 'dic', 'furnace', or 'rl'")
        
        return BatchLoader(data, batch_size, self.config)
    
    def synchronize_data(self, reference_timestamps: np.ndarray) -> Dict:
        """
        Synchronize all data to a common time base.
        
        Args:
            reference_timestamps: Reference time points for synchronization
            
        Returns:
            Dictionary containing synchronized data
        """
        # Load all data
        dic_data = self.load_dic_data()
        furnace_data = self.load_furnace_data()
        rl_data = self.load_rl_data()
        
        synchronized_data = {}
        
        # Synchronize DIC data
        dic_interp = {}
        for field in ['max_principal_strain', 'strain_heterogeneity', 'sample_curvature']:
            if field in dic_data:
                f = interpolate.interp1d(
                    dic_data['timestamps'], dic_data[field],
                    kind=self.config.interpolation_method,
                    bounds_error=False, fill_value='extrapolate'
                )
                dic_interp[field] = f(reference_timestamps)
        
        synchronized_data['dic'] = dic_interp
        
        # Synchronize furnace data
        furnace_interp = {}
        for field in ['zone_temperatures', 'thermocouple_temps', 'oxygen_levels', 'actions']:
            if field in furnace_data:
                if field == 'actions':
                    # Actions need special handling
                    f = interpolate.interp1d(
                        furnace_data['timestamps'][1:], furnace_data[field],
                        kind=self.config.interpolation_method,
                        bounds_error=False, fill_value='extrapolate'
                    )
                    furnace_interp[field] = f(reference_timestamps)
                else:
                    f = interpolate.interp1d(
                        furnace_data['timestamps'], furnace_data[field],
                        kind=self.config.interpolation_method,
                        bounds_error=False, fill_value='extrapolate'
                    )
                    furnace_interp[field] = f(reference_timestamps)
        
        synchronized_data['furnace'] = furnace_interp
        
        # Synchronize RL data
        rl_interp = {}
        for field in ['states', 'rewards']:
            if field in rl_data:
                f = interpolate.interp1d(
                    rl_data['timestamps'], rl_data[field],
                    kind=self.config.interpolation_method,
                    bounds_error=False, fill_value='extrapolate'
                )
                rl_interp[field] = f(reference_timestamps)
        
        synchronized_data['rl'] = rl_interp
        synchronized_data['timestamps'] = reference_timestamps
        
        return synchronized_data
    
    def normalize_data(self, data: np.ndarray, 
                      method: str = 'z_score') -> Tuple[np.ndarray, Dict]:
        """
        Normalize data using specified method.
        
        Args:
            data: Data to normalize
            method: Normalization method ('z_score', 'min_max', 'robust')
            
        Returns:
            Tuple of (normalized_data, normalization_params)
        """
        if method == 'z_score':
            mean = np.mean(data, axis=0)
            std = np.std(data, axis=0)
            normalized_data = (data - mean) / (std + 1e-8)
            params = {'mean': mean, 'std': std, 'method': 'z_score'}
        
        elif method == 'min_max':
            min_val = np.min(data, axis=0)
            max_val = np.max(data, axis=0)
            normalized_data = (data - min_val) / (max_val - min_val + 1e-8)
            params = {'min': min_val, 'max': max_val, 'method': 'min_max'}
        
        elif method == 'robust':
            median = np.median(data, axis=0)
            mad = np.median(np.abs(data - median), axis=0)
            normalized_data = (data - median) / (mad + 1e-8)
            params = {'median': median, 'mad': mad, 'method': 'robust'}
        
        else:
            raise ValueError("method must be 'z_score', 'min_max', or 'robust'")
        
        return normalized_data, params
    
    def denormalize_data(self, normalized_data: np.ndarray, 
                        params: Dict) -> np.ndarray:
        """
        Denormalize data using stored parameters.
        
        Args:
            normalized_data: Normalized data
            params: Normalization parameters
            
        Returns:
            Denormalized data
        """
        method = params['method']
        
        if method == 'z_score':
            return normalized_data * params['std'] + params['mean']
        elif method == 'min_max':
            return normalized_data * (params['max'] - params['min']) + params['min']
        elif method == 'robust':
            return normalized_data * params['mad'] + params['median']
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def add_noise(self, data: np.ndarray, 
                  noise_level: float = None) -> np.ndarray:
        """
        Add noise to data for data augmentation.
        
        Args:
            data: Data to add noise to
            noise_level: Noise level (if None, uses config value)
            
        Returns:
            Data with added noise
        """
        if noise_level is None:
            noise_level = self.config.noise_level
        
        noise = np.random.normal(0, noise_level, data.shape)
        return data + noise
    
    def create_train_val_split(self, data: Dict, 
                              val_ratio: float = 0.2) -> Tuple[Dict, Dict]:
        """
        Create train/validation split.
        
        Args:
            data: Data dictionary
            val_ratio: Validation ratio
            
        Returns:
            Tuple of (train_data, val_data)
        """
        # Determine split index
        total_samples = len(data['states']) if 'states' in data else len(data['timestamps'])
        split_idx = int(total_samples * (1 - val_ratio))
        
        train_data = {}
        val_data = {}
        
        for key, value in data.items():
            if isinstance(value, np.ndarray) and len(value) == total_samples:
                train_data[key] = value[:split_idx]
                val_data[key] = value[split_idx:]
            else:
                train_data[key] = value
                val_data[key] = value
        
        return train_data, val_data
    
    def get_data_statistics(self) -> Dict:
        """
        Get comprehensive data statistics.
        
        Returns:
            Dictionary containing data statistics
        """
        stats = {}
        
        # DIC statistics
        dic_data = self.load_dic_data()
        stats['dic'] = {
            'num_frames': len(dic_data['timestamps']),
            'frame_rate': self.metadata['dic_fps'],
            'duration_hours': self.metadata['sample_duration_hours'],
            'max_principal_strain': {
                'mean': float(np.mean(dic_data['max_principal_strain'])),
                'std': float(np.std(dic_data['max_principal_strain'])),
                'min': float(np.min(dic_data['max_principal_strain'])),
                'max': float(np.max(dic_data['max_principal_strain']))
            }
        }
        
        # Furnace statistics
        furnace_data = self.load_furnace_data()
        stats['furnace'] = {
            'num_updates': len(furnace_data['timestamps']),
            'update_frequency': self.metadata['furnace_update_freq'],
            'num_zones': self.metadata['num_heating_zones'],
            'num_thermocouples': self.metadata['num_thermocouples'],
            'temperature_range': {
                'min': float(np.min(furnace_data['zone_temperatures'])),
                'max': float(np.max(furnace_data['zone_temperatures']))
            }
        }
        
        # RL statistics
        rl_data = self.load_rl_data()
        stats['rl'] = {
            'num_tuples': len(rl_data['states']),
            'state_dimension': rl_data['states'].shape[1],
            'action_dimension': rl_data['actions'].shape[1],
            'reward_range': {
                'min': float(np.min(rl_data['rewards'])),
                'max': float(np.max(rl_data['rewards']))
            }
        }
        
        return stats


class BatchLoader:
    """
    Batch loader for efficient data loading during training.
    """
    
    def __init__(self, data: Dict, batch_size: int, config: DatasetConfig):
        """
        Initialize batch loader.
        
        Args:
            data: Data dictionary
            batch_size: Batch size
            config: Dataset configuration
        """
        self.data = data
        self.batch_size = batch_size
        self.config = config
        self.num_samples = len(data['states']) if 'states' in data else len(data['timestamps'])
        self.num_batches = (self.num_samples + batch_size - 1) // batch_size
        self.current_batch = 0
        
    def __iter__(self):
        """Make the loader iterable."""
        self.current_batch = 0
        return self
    
    def __next__(self):
        """Get next batch."""
        if self.current_batch >= self.num_batches:
            raise StopIteration
        
        start_idx = self.current_batch * self.batch_size
        end_idx = min(start_idx + self.batch_size, self.num_samples)
        
        batch = {}
        for key, value in self.data.items():
            if isinstance(value, np.ndarray) and len(value) == self.num_samples:
                batch[key] = value[start_idx:end_idx]
            else:
                batch[key] = value
        
        self.current_batch += 1
        return batch
    
    def __len__(self):
        """Get number of batches."""
        return self.num_batches


class DataAnalyzer:
    """
    Advanced data analysis tools for the dataset.
    """
    
    def __init__(self, data_loader: RealTimeDataLoader):
        """
        Initialize data analyzer.
        
        Args:
            data_loader: RealTimeDataLoader instance
        """
        self.data_loader = data_loader
    
    def analyze_temporal_correlations(self) -> Dict:
        """
        Analyze temporal correlations in the data.
        
        Returns:
            Dictionary containing correlation analysis results
        """
        # Load all data
        dic_data = self.data_loader.load_dic_data()
        furnace_data = self.data_loader.load_furnace_data()
        rl_data = self.data_loader.load_rl_data()
        
        correlations = {}
        
        # DIC temporal correlations
        dic_metrics = ['max_principal_strain', 'strain_heterogeneity', 'sample_curvature']
        dic_corr_matrix = np.corrcoef([dic_data[metric] for metric in dic_metrics])
        correlations['dic'] = {
            'metrics': dic_metrics,
            'correlation_matrix': dic_corr_matrix.tolist()
        }
        
        # Furnace temporal correlations
        furnace_metrics = ['zone_temperatures', 'thermocouple_temps', 'oxygen_levels']
        furnace_corr_data = []
        for metric in furnace_metrics:
            if metric in furnace_data:
                if metric in ['zone_temperatures', 'thermocouple_temps']:
                    furnace_corr_data.append(np.mean(furnace_data[metric], axis=1))
                else:
                    furnace_corr_data.append(furnace_data[metric])
        
        if furnace_corr_data:
            furnace_corr_matrix = np.corrcoef(furnace_corr_data)
            correlations['furnace'] = {
                'metrics': furnace_metrics,
                'correlation_matrix': furnace_corr_matrix.tolist()
            }
        
        # RL temporal correlations
        rl_corr_matrix = np.corrcoef([rl_data['states'][:, i] for i in range(rl_data['states'].shape[1])])
        correlations['rl'] = {
            'metrics': [f'state_{i}' for i in range(rl_data['states'].shape[1])],
            'correlation_matrix': rl_corr_matrix.tolist()
        }
        
        return correlations
    
    def analyze_frequency_content(self) -> Dict:
        """
        Analyze frequency content of the data.
        
        Returns:
            Dictionary containing frequency analysis results
        """
        # Load data
        dic_data = self.data_loader.load_dic_data()
        furnace_data = self.data_loader.load_furnace_data()
        
        frequency_analysis = {}
        
        # DIC frequency analysis
        dic_metrics = ['max_principal_strain', 'strain_heterogeneity', 'sample_curvature']
        for metric in dic_metrics:
            if metric in dic_data:
                data = dic_data[metric]
                freqs, psd = signal.periodogram(data, fs=self.data_loader.metadata['dic_fps'])
                frequency_analysis[f'dic_{metric}'] = {
                    'frequencies': freqs.tolist(),
                    'power_spectral_density': psd.tolist(),
                    'dominant_frequency': float(freqs[np.argmax(psd)])
                }
        
        # Furnace frequency analysis
        furnace_metrics = ['zone_temperatures', 'thermocouple_temps']
        for metric in furnace_metrics:
            if metric in furnace_data:
                data = np.mean(furnace_data[metric], axis=1)
                freqs, psd = signal.periodogram(data, fs=self.data_loader.metadata['furnace_update_freq'])
                frequency_analysis[f'furnace_{metric}'] = {
                    'frequencies': freqs.tolist(),
                    'power_spectral_density': psd.tolist(),
                    'dominant_frequency': float(freqs[np.argmax(psd)])
                }
        
        return frequency_analysis
    
    def analyze_data_quality(self) -> Dict:
        """
        Analyze data quality and identify potential issues.
        
        Returns:
            Dictionary containing data quality analysis
        """
        quality_analysis = {
            'issues': [],
            'recommendations': [],
            'quality_score': 1.0
        }
        
        # Load data
        dic_data = self.data_loader.load_dic_data()
        furnace_data = self.data_loader.load_furnace_data()
        rl_data = self.data_loader.load_rl_data()
        
        # Check for missing values
        for field, data in dic_data.items():
            if isinstance(data, np.ndarray) and np.any(np.isnan(data)):
                quality_analysis['issues'].append(f"Missing values in DIC field: {field}")
                quality_analysis['quality_score'] *= 0.9
        
        for field, data in furnace_data.items():
            if isinstance(data, np.ndarray) and np.any(np.isnan(data)):
                quality_analysis['issues'].append(f"Missing values in furnace field: {field}")
                quality_analysis['quality_score'] *= 0.9
        
        # Check for outliers
        reward_std = np.std(rl_data['rewards'])
        reward_mean = np.mean(rl_data['rewards'])
        outliers = np.abs(rl_data['rewards'] - reward_mean) > 3 * reward_std
        if np.any(outliers):
            quality_analysis['issues'].append(f"Outliers detected in rewards: {np.sum(outliers)} points")
            quality_analysis['quality_score'] *= 0.95
        
        # Check for temporal consistency
        dic_timestamps = dic_data['timestamps']
        furnace_timestamps = furnace_data['timestamps']
        
        dic_dt = np.diff(dic_timestamps)
        furnace_dt = np.diff(furnace_timestamps)
        
        if np.std(dic_dt) > 0.1 * np.mean(dic_dt):
            quality_analysis['issues'].append("Inconsistent DIC sampling intervals")
            quality_analysis['quality_score'] *= 0.9
        
        if np.std(furnace_dt) > 0.1 * np.mean(furnace_dt):
            quality_analysis['issues'].append("Inconsistent furnace sampling intervals")
            quality_analysis['quality_score'] *= 0.9
        
        # Generate recommendations
        if quality_analysis['quality_score'] < 0.8:
            quality_analysis['recommendations'].append("Consider data preprocessing to improve quality")
        
        if len(quality_analysis['issues']) > 0:
            quality_analysis['recommendations'].append("Address identified data quality issues")
        
        return quality_analysis


def main():
    """Demonstrate data loader and analyzer usage."""
    print("Data Loader and Analyzer Demo")
    print("=" * 40)
    
    # Initialize data loader
    config = DatasetConfig(
        dataset_dir="real_time_dataset",
        batch_size=16,
        sequence_length=5,
        normalize_data=True
    )
    
    data_loader = RealTimeDataLoader(config)
    
    # Load data
    print("\n1. Loading data...")
    dic_data = data_loader.load_dic_data()
    furnace_data = data_loader.load_furnace_data()
    rl_data = data_loader.load_rl_data()
    
    print(f"DIC data: {len(dic_data['timestamps'])} frames")
    print(f"Furnace data: {len(furnace_data['timestamps'])} updates")
    print(f"RL data: {len(rl_data['states'])} tuples")
    
    # Create batch loader
    print("\n2. Creating batch loader...")
    batch_loader = data_loader.create_batch_loader('rl', batch_size=8)
    print(f"Number of batches: {len(batch_loader)}")
    
    # Demonstrate batch loading
    for i, batch in enumerate(batch_loader):
        print(f"Batch {i}: states shape {batch['states'].shape}, actions shape {batch['actions'].shape}")
        if i >= 2:  # Show only first 3 batches
            break
    
    # Create sequence dataset
    print("\n3. Creating sequence dataset...")
    sequence_data = data_loader.create_sequence_dataset(sequence_length=5)
    print(f"Sequence data: {sequence_data['num_sequences']} sequences of length {sequence_data['sequence_length']}")
    
    # Analyze data
    print("\n4. Analyzing data...")
    analyzer = DataAnalyzer(data_loader)
    
    # Get statistics
    stats = data_loader.get_data_statistics()
    print(f"Data statistics: {json.dumps(stats, indent=2)}")
    
    # Analyze correlations
    correlations = analyzer.analyze_temporal_correlations()
    print(f"Temporal correlations analyzed for {len(correlations)} data types")
    
    # Analyze frequency content
    frequency_analysis = analyzer.analyze_frequency_content()
    print(f"Frequency analysis completed for {len(frequency_analysis)} metrics")
    
    # Analyze data quality
    quality_analysis = analyzer.analyze_data_quality()
    print(f"Data quality score: {quality_analysis['quality_score']:.2f}")
    if quality_analysis['issues']:
        print(f"Issues found: {len(quality_analysis['issues'])}")
    
    print("\n" + "=" * 40)
    print("Data Loader and Analyzer Demo Complete!")


if __name__ == "__main__":
    main()