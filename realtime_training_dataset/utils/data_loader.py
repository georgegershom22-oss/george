#!/usr/bin/env python3
"""
Real-Time Dataset Loader and Preprocessor
Efficient loading and preprocessing of the multi-modal dataset
"""

import numpy as np
import pandas as pd
import h5py
import pickle
import json
import os
from typing import Dict, List, Tuple, Optional, Generator
import torch
from torch.utils.data import Dataset, DataLoader
import cv2
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class RealTimeDataset(Dataset):
    """PyTorch Dataset for real-time training data"""
    
    def __init__(self, 
                 base_path: str,
                 episodes: List[int],
                 sequence_length: int = 10,
                 modalities: List[str] = ['dic', 'furnace', 'rl'],
                 transform=None):
        """
        Args:
            base_path: Path to dataset root
            episodes: List of episode indices to include
            sequence_length: Length of sequences for temporal modeling
            modalities: Which data modalities to include
            transform: Optional data transforms
        """
        self.base_path = base_path
        self.episodes = episodes
        self.sequence_length = sequence_length
        self.modalities = modalities
        self.transform = transform
        
        # Load dataset metadata
        self.metadata = self.load_metadata()
        
        # Build index of all sequences
        self.sequence_index = self.build_sequence_index()
        
        # Initialize scalers
        self.scalers = self.fit_scalers()
    
    def load_metadata(self) -> Dict:
        """Load dataset summary metadata"""
        metadata_path = os.path.join(self.base_path, "dataset_summary.json")
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def build_sequence_index(self) -> List[Tuple[int, int]]:
        """Build index of all valid sequences (episode, start_idx)"""
        sequences = []
        
        for episode in self.episodes:
            episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
            
            # Load episode metadata to get sequence length
            with open(os.path.join(episode_dir, "metadata.json"), 'r') as f:
                ep_metadata = json.load(f)
            
            rl_samples = ep_metadata['rl_samples']
            
            # Create sequences with overlap
            for start_idx in range(0, rl_samples - self.sequence_length + 1, 5):
                sequences.append((episode, start_idx))
        
        return sequences
    
    def fit_scalers(self) -> Dict:
        """Fit data scalers on training data"""
        scalers = {}
        
        # Collect sample data for fitting
        sample_states = []
        sample_actions = []
        
        for episode in self.episodes[:10]:  # Use first 10 episodes for fitting
            rl_data = self.load_rl_data(episode)
            sample_states.extend([self.state_to_vector(s) for s in rl_data['states']])
            sample_actions.extend(rl_data['actions'])
        
        # Fit state scaler
        scalers['state'] = StandardScaler()
        scalers['state'].fit(sample_states)
        
        # Fit action scaler
        scalers['action'] = StandardScaler()
        scalers['action'].fit(sample_actions)
        
        return scalers
    
    def state_to_vector(self, state: Dict) -> np.ndarray:
        """Convert state dictionary to vector"""
        return np.array([
            state['max_principal_strain'],
            state['strain_std'],
            state['sample_curvature'],
            state['temperature_std'],
            state['current_density'],
            state['mean_temperature'],
            state['time_in_cycle']
        ])
    
    def load_episode_data(self, episode: int) -> Dict:
        """Load all data for an episode"""
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        data = {}
        
        if 'dic' in self.modalities:
            # Load DIC data
            with h5py.File(os.path.join(episode_dir, "dic_data.h5"), 'r') as f:
                data['dic'] = {
                    'timestamps': f['timestamps'][:],
                    'displacement_fields': f['displacement_fields'][:],
                    'strain_fields': f['strain_fields'][:],
                    'video_frames': [f['video_frames'][key][:] for key in f['video_frames'].keys()]
                }
        
        if 'furnace' in self.modalities:
            # Load furnace data
            data['furnace'] = pd.read_parquet(os.path.join(episode_dir, "furnace_data.parquet"))
        
        if 'rl' in self.modalities:
            # Load RL data
            data['rl'] = self.load_rl_data(episode)
        
        return data
    
    def load_rl_data(self, episode: int) -> Dict:
        """Load RL data for an episode"""
        episode_dir = os.path.join(self.base_path, f"episode_{episode:04d}")
        with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
            return pickle.load(f)
    
    def __len__(self) -> int:
        return len(self.sequence_index)
    
    def __getitem__(self, idx: int) -> Dict:
        """Get a sequence sample"""
        episode, start_idx = self.sequence_index[idx]
        
        # Load RL data for this episode
        rl_data = self.load_rl_data(episode)
        
        # Extract sequence
        end_idx = start_idx + self.sequence_length
        
        # States and actions
        states = [self.state_to_vector(s) for s in rl_data['states'][start_idx:end_idx]]
        actions = rl_data['actions'][start_idx:end_idx-1]  # One less action than states
        rewards = rl_data['rewards'][start_idx:end_idx-1]
        next_states = [self.state_to_vector(s) for s in rl_data['next_states'][start_idx:end_idx-1]]
        
        # Convert to numpy arrays
        states = np.array(states)
        actions = np.array(actions)
        rewards = np.array(rewards)
        next_states = np.array(next_states)
        
        # Apply scaling
        states = self.scalers['state'].transform(states)
        next_states = self.scalers['state'].transform(next_states)
        actions = self.scalers['action'].transform(actions)
        
        sample = {
            'states': torch.FloatTensor(states),
            'actions': torch.FloatTensor(actions),
            'rewards': torch.FloatTensor(rewards),
            'next_states': torch.FloatTensor(next_states),
            'episode': episode,
            'sequence_start': start_idx
        }
        
        # Add DIC data if requested
        if 'dic' in self.modalities:
            # Load corresponding DIC frames (subsampled)
            episode_data = self.load_episode_data(episode)
            dic_indices = np.linspace(start_idx, end_idx-1, self.sequence_length, dtype=int)
            
            if len(episode_data['dic']['video_frames']) > max(dic_indices):
                dic_frames = [episode_data['dic']['video_frames'][i] for i in dic_indices]
                sample['dic_frames'] = torch.FloatTensor(np.array(dic_frames)) / 255.0
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample

class StreamingDataLoader:
    """Streaming data loader for real-time simulation"""
    
    def __init__(self, base_path: str, episode: int, buffer_size: int = 100):
        self.base_path = base_path
        self.episode = episode
        self.buffer_size = buffer_size
        
        # Load episode data
        self.episode_data = self.load_episode_data()
        self.current_idx = 0
        
    def load_episode_data(self) -> Dict:
        """Load episode data for streaming"""
        episode_dir = os.path.join(self.base_path, f"episode_{self.episode:04d}")
        
        # Load all data types
        data = {}
        
        # DIC data
        with h5py.File(os.path.join(episode_dir, "dic_data.h5"), 'r') as f:
            data['dic'] = {
                'timestamps': f['timestamps'][:],
                'displacement_fields': f['displacement_fields'][:],
                'strain_fields': f['strain_fields'][:]
            }
        
        # Furnace data
        data['furnace'] = pd.read_parquet(os.path.join(episode_dir, "furnace_data.parquet"))
        
        # RL data
        with open(os.path.join(episode_dir, "rl_data.pkl"), 'rb') as f:
            data['rl'] = pickle.load(f)
        
        return data
    
    def stream_data(self, dt: float = 1.0) -> Generator[Dict, None, None]:
        """Stream data at specified time intervals"""
        rl_data = self.episode_data['rl']
        
        while self.current_idx < len(rl_data['states']):
            # Current sample
            sample = {
                'timestamp': self.current_idx * dt,
                'state': rl_data['states'][self.current_idx],
                'action': rl_data['actions'][self.current_idx] if self.current_idx < len(rl_data['actions']) else None,
                'reward': rl_data['rewards'][self.current_idx] if self.current_idx < len(rl_data['rewards']) else None
            }
            
            # Add DIC data if available
            if self.current_idx < len(self.episode_data['dic']['displacement_fields']):
                sample['displacement'] = self.episode_data['dic']['displacement_fields'][self.current_idx]
                sample['strain'] = self.episode_data['dic']['strain_fields'][self.current_idx]
            
            # Add furnace data (interpolated)
            furnace_idx = min(self.current_idx, len(self.episode_data['furnace']) - 1)
            sample['furnace'] = self.episode_data['furnace'].iloc[furnace_idx].to_dict()
            
            yield sample
            self.current_idx += 1

def create_data_loaders(base_path: str, 
                       train_episodes: List[int],
                       val_episodes: List[int],
                       test_episodes: List[int],
                       batch_size: int = 32,
                       sequence_length: int = 10) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create train, validation, and test data loaders"""
    
    # Create datasets
    train_dataset = RealTimeDataset(base_path, train_episodes, sequence_length)
    val_dataset = RealTimeDataset(base_path, val_episodes, sequence_length)
    test_dataset = RealTimeDataset(base_path, test_episodes, sequence_length)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    
    return train_loader, val_loader, test_loader

if __name__ == "__main__":
    # Example usage
    base_path = "/workspace/realtime_training_dataset"
    
    # Split episodes
    train_episodes = list(range(0, 700))
    val_episodes = list(range(700, 900))
    test_episodes = list(range(900, 1000))
    
    # Create data loaders
    train_loader, val_loader, test_loader = create_data_loaders(
        base_path, train_episodes, val_episodes, test_episodes
    )
    
    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")
    print(f"Test batches: {len(test_loader)}")
    
    # Test loading a batch
    for batch in train_loader:
        print("Batch shapes:")
        for key, value in batch.items():
            if isinstance(value, torch.Tensor):
                print(f"  {key}: {value.shape}")
        break