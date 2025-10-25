"""
Data Validation and Quality Assurance Tools
Comprehensive validation for DIC and RL training data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.spatial.distance import cdist
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class DataValidator:
    """
    Comprehensive data validation for DIC and RL training datasets
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_validation_parameters()
        self.validation_results = {}
        
    def setup_validation_parameters(self):
        """Setup validation parameters and thresholds"""
        self.thresholds = {
            'correlation_min': 0.7,
            'displacement_max': 10.0,  # pixels
            'strain_max': 0.1,
            'temperature_range': (20, 1700),  # °C
            'density_range': (0.5, 1.0),
            'reward_range': (-100, 100),
            'action_range': (-50, 50)
        }
        
        self.quality_metrics = {
            'outlier_threshold': 3.0,  # Standard deviations
            'missing_data_threshold': 0.05,  # 5% missing data
            'temporal_consistency_threshold': 0.1,
            'spatial_consistency_threshold': 0.2
        }
        
    def validate_dic_data(self, dic_data: Dict) -> Dict:
        """Validate DIC measurement data"""
        validation_results = {
            'overall_quality': 'good',
            'issues': [],
            'metrics': {},
            'recommendations': []
        }
        
        # Validate displacement fields
        disp_validation = self.validate_displacement_fields(dic_data.get('displacement_fields', []))
        validation_results['displacement_validation'] = disp_validation
        
        # Validate strain fields
        strain_validation = self.validate_strain_fields(dic_data.get('strain_fields', []))
        validation_results['strain_validation'] = strain_validation
        
        # Validate temporal consistency
        temporal_validation = self.validate_temporal_consistency(dic_data)
        validation_results['temporal_validation'] = temporal_validation
        
        # Validate spatial consistency
        spatial_validation = self.validate_spatial_consistency(dic_data)
        validation_results['spatial_validation'] = spatial_validation
        
        # Overall quality assessment
        validation_results = self.assess_overall_quality(validation_results)
        
        return validation_results
    
    def validate_displacement_fields(self, displacement_data: List[Dict]) -> Dict:
        """Validate displacement field data"""
        if not displacement_data:
            return {'quality': 'poor', 'issues': ['No displacement data'], 'metrics': {}}
        
        issues = []
        metrics = {}
        
        # Extract displacement arrays
        U_arrays = [frame['U'] for frame in displacement_data]
        V_arrays = [frame['V'] for frame in displacement_data]
        W_arrays = [frame.get('W', np.zeros_like(frame['U'])) for frame in displacement_data]
        
        # Check for missing data
        missing_data_ratio = self.calculate_missing_data_ratio(U_arrays + V_arrays + W_arrays)
        if missing_data_ratio > self.quality_metrics['missing_data_threshold']:
            issues.append(f'High missing data ratio: {missing_data_ratio:.3f}')
        
        metrics['missing_data_ratio'] = missing_data_ratio
        
        # Check displacement magnitudes
        max_displacements = [np.max(np.sqrt(U**2 + V**2 + W**2)) for U, V, W in zip(U_arrays, V_arrays, W_arrays)]
        avg_max_displacement = np.mean(max_displacements)
        
        if avg_max_displacement > self.thresholds['displacement_max']:
            issues.append(f'Excessive displacement: {avg_max_displacement:.3f} pixels')
        
        metrics['avg_max_displacement'] = avg_max_displacement
        metrics['max_displacement_std'] = np.std(max_displacements)
        
        # Check for outliers
        outlier_ratio = self.calculate_outlier_ratio(max_displacements)
        if outlier_ratio > 0.1:  # 10% outliers
            issues.append(f'High outlier ratio: {outlier_ratio:.3f}')
        
        metrics['outlier_ratio'] = outlier_ratio
        
        # Check displacement continuity
        continuity_score = self.calculate_displacement_continuity(U_arrays, V_arrays, W_arrays)
        metrics['continuity_score'] = continuity_score
        
        if continuity_score < 0.8:
            issues.append(f'Poor displacement continuity: {continuity_score:.3f}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 2 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_strain_fields(self, strain_data: List[Dict]) -> Dict:
        """Validate strain field data"""
        if not strain_data:
            return {'quality': 'poor', 'issues': ['No strain data'], 'metrics': {}}
        
        issues = []
        metrics = {}
        
        # Extract strain arrays
        eps_xx_arrays = [frame['epsilon_xx'] for frame in strain_data]
        eps_yy_arrays = [frame['epsilon_yy'] for frame in strain_data]
        eps_xy_arrays = [frame['epsilon_xy'] for frame in strain_data]
        
        # Check strain magnitudes
        max_strains = []
        for eps_xx, eps_yy, eps_xy in zip(eps_xx_arrays, eps_yy_arrays, eps_xy_arrays):
            strain_magnitude = np.sqrt(eps_xx**2 + eps_yy**2 + eps_xy**2)
            max_strains.append(np.max(strain_magnitude))
        
        avg_max_strain = np.mean(max_strains)
        
        if avg_max_strain > self.thresholds['strain_max']:
            issues.append(f'Excessive strain: {avg_max_strain:.6f}')
        
        metrics['avg_max_strain'] = avg_max_strain
        metrics['max_strain_std'] = np.std(max_strains)
        
        # Check strain field smoothness
        smoothness_scores = []
        for eps_xx, eps_yy, eps_xy in zip(eps_xx_arrays, eps_yy_arrays, eps_xy_arrays):
            smoothness = self.calculate_field_smoothness(eps_xx, eps_yy, eps_xy)
            smoothness_scores.append(smoothness)
        
        avg_smoothness = np.mean(smoothness_scores)
        metrics['avg_smoothness'] = avg_smoothness
        
        if avg_smoothness < 0.7:
            issues.append(f'Poor strain field smoothness: {avg_smoothness:.3f}')
        
        # Check strain compatibility
        compatibility_scores = []
        for eps_xx, eps_yy, eps_xy in zip(eps_xx_arrays, eps_yy_arrays, eps_xy_arrays):
            compatibility = self.check_strain_compatibility(eps_xx, eps_yy, eps_xy)
            compatibility_scores.append(compatibility)
        
        avg_compatibility = np.mean(compatibility_scores)
        metrics['avg_compatibility'] = avg_compatibility
        
        if avg_compatibility < 0.8:
            issues.append(f'Poor strain compatibility: {avg_compatibility:.3f}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 2 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_temporal_consistency(self, dic_data: Dict) -> Dict:
        """Validate temporal consistency of DIC data"""
        issues = []
        metrics = {}
        
        # Check frame rate consistency
        if 'timestamps' in dic_data:
            timestamps = dic_data['timestamps']
            if len(timestamps) > 1:
                time_diffs = np.diff(timestamps)
                expected_interval = 1.0 / self.config.get('fps', 120)
                
                time_consistency = 1.0 - np.std(time_diffs) / expected_interval
                metrics['time_consistency'] = time_consistency
                
                if time_consistency < 0.9:
                    issues.append(f'Poor temporal consistency: {time_consistency:.3f}')
        
        # Check displacement evolution smoothness
        if 'displacement_fields' in dic_data:
            disp_data = dic_data['displacement_fields']
            if len(disp_data) > 1:
                smoothness_scores = []
                for i in range(1, len(disp_data)):
                    prev_U = disp_data[i-1]['U']
                    curr_U = disp_data[i]['U']
                    prev_V = disp_data[i-1]['V']
                    curr_V = disp_data[i]['V']
                    
                    # Calculate change magnitude
                    U_change = np.mean(np.abs(curr_U - prev_U))
                    V_change = np.mean(np.abs(curr_V - prev_V))
                    
                    # Normalize by expected change
                    expected_change = 0.1  # pixels per frame
                    smoothness = 1.0 / (1.0 + (U_change + V_change) / expected_change)
                    smoothness_scores.append(smoothness)
                
                avg_smoothness = np.mean(smoothness_scores)
                metrics['displacement_smoothness'] = avg_smoothness
                
                if avg_smoothness < 0.7:
                    issues.append(f'Poor displacement smoothness: {avg_smoothness:.3f}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 1 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_spatial_consistency(self, dic_data: Dict) -> Dict:
        """Validate spatial consistency of DIC data"""
        issues = []
        metrics = {}
        
        if 'displacement_fields' not in dic_data:
            return {'quality': 'poor', 'issues': ['No displacement data'], 'metrics': {}}
        
        disp_data = dic_data['displacement_fields']
        if not disp_data:
            return {'quality': 'poor', 'issues': ['Empty displacement data'], 'metrics': {}}
        
        # Check spatial smoothness within each frame
        smoothness_scores = []
        for frame in disp_data:
            U = frame['U']
            V = frame['V']
            
            # Calculate spatial gradients
            U_grad_x = np.gradient(U, axis=1)
            U_grad_y = np.gradient(U, axis=0)
            V_grad_x = np.gradient(V, axis=1)
            V_grad_y = np.gradient(V, axis=0)
            
            # Calculate smoothness (lower gradient magnitude = smoother)
            U_smoothness = 1.0 / (1.0 + np.mean(np.sqrt(U_grad_x**2 + U_grad_y**2)))
            V_smoothness = 1.0 / (1.0 + np.mean(np.sqrt(V_grad_x**2 + V_grad_y**2)))
            
            smoothness_scores.append((U_smoothness + V_smoothness) / 2)
        
        avg_smoothness = np.mean(smoothness_scores)
        metrics['spatial_smoothness'] = avg_smoothness
        
        if avg_smoothness < 0.6:
            issues.append(f'Poor spatial smoothness: {avg_smoothness:.3f}')
        
        # Check for spatial outliers
        outlier_ratios = []
        for frame in disp_data:
            U = frame['U']
            V = frame['V']
            
            # Calculate displacement magnitude
            disp_magnitude = np.sqrt(U**2 + V**2)
            
            # Find outliers
            mean_disp = np.mean(disp_magnitude)
            std_disp = np.std(disp_magnitude)
            outlier_mask = np.abs(disp_magnitude - mean_disp) > self.quality_metrics['outlier_threshold'] * std_disp
            
            outlier_ratio = np.sum(outlier_mask) / disp_magnitude.size
            outlier_ratios.append(outlier_ratio)
        
        avg_outlier_ratio = np.mean(outlier_ratios)
        metrics['spatial_outlier_ratio'] = avg_outlier_ratio
        
        if avg_outlier_ratio > 0.05:  # 5% outliers
            issues.append(f'High spatial outlier ratio: {avg_outlier_ratio:.3f}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 1 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_rl_data(self, rl_data: Dict) -> Dict:
        """Validate RL training data"""
        validation_results = {
            'overall_quality': 'good',
            'issues': [],
            'metrics': {},
            'recommendations': []
        }
        
        # Validate states
        state_validation = self.validate_states(rl_data.get('states', []))
        validation_results['state_validation'] = state_validation
        
        # Validate actions
        action_validation = self.validate_actions(rl_data.get('actions', []))
        validation_results['action_validation'] = action_validation
        
        # Validate rewards
        reward_validation = self.validate_rewards(rl_data.get('rewards', []))
        validation_results['reward_validation'] = reward_validation
        
        # Validate state-action-reward consistency
        consistency_validation = self.validate_sar_consistency(rl_data)
        validation_results['consistency_validation'] = consistency_validation
        
        # Overall quality assessment
        validation_results = self.assess_overall_quality(validation_results)
        
        return validation_results
    
    def validate_states(self, states: List[Dict]) -> Dict:
        """Validate state data"""
        if not states:
            return {'quality': 'poor', 'issues': ['No state data'], 'metrics': {}}
        
        issues = []
        metrics = {}
        
        # Extract state values
        state_arrays = []
        for state in states:
            if 'dic_metrics' in state:
                dic_metrics = state['dic_metrics']
                state_array = [
                    dic_metrics.get('max_principal_strain', 0),
                    dic_metrics.get('strain_heterogeneity', 0),
                    dic_metrics.get('curvature', 0),
                    dic_metrics.get('warpage_rate', 0),
                    dic_metrics.get('max_displacement', 0)
                ]
                state_arrays.append(state_array)
        
        if not state_arrays:
            return {'quality': 'poor', 'issues': ['No valid state data'], 'metrics': {}}
        
        state_matrix = np.array(state_arrays)
        
        # Check for missing data
        missing_ratio = np.sum(np.isnan(state_matrix)) / state_matrix.size
        if missing_ratio > self.quality_metrics['missing_data_threshold']:
            issues.append(f'High missing data ratio: {missing_ratio:.3f}')
        
        metrics['missing_data_ratio'] = missing_ratio
        
        # Check for outliers
        outlier_ratios = []
        for i in range(state_matrix.shape[1]):
            values = state_matrix[:, i]
            valid_values = values[~np.isnan(values)]
            if len(valid_values) > 0:
                mean_val = np.mean(valid_values)
                std_val = np.std(valid_values)
                outlier_mask = np.abs(valid_values - mean_val) > self.quality_metrics['outlier_threshold'] * std_val
                outlier_ratio = np.sum(outlier_mask) / len(valid_values)
                outlier_ratios.append(outlier_ratio)
        
        avg_outlier_ratio = np.mean(outlier_ratios) if outlier_ratios else 0
        metrics['outlier_ratio'] = avg_outlier_ratio
        
        if avg_outlier_ratio > 0.1:
            issues.append(f'High outlier ratio: {avg_outlier_ratio:.3f}')
        
        # Check state value ranges
        for i, (key, (min_val, max_val)) in enumerate(self.thresholds.items()):
            if i < state_matrix.shape[1]:
                values = state_matrix[:, i]
                valid_values = values[~np.isnan(values)]
                if len(valid_values) > 0:
                    if np.any(valid_values < min_val) or np.any(valid_values > max_val):
                        issues.append(f'State values out of range for {key}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 2 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_actions(self, actions: List[Dict]) -> Dict:
        """Validate action data"""
        if not actions:
            return {'quality': 'poor', 'issues': ['No action data'], 'metrics': {}}
        
        issues = []
        metrics = {}
        
        # Extract action values
        action_arrays = []
        for action in actions:
            if 'zone_temperature_changes' in action:
                temp_changes = action['zone_temperature_changes']
                power_changes = action.get('power_adjustments', [0] * len(temp_changes))
                action_array = temp_changes + power_changes
                action_arrays.append(action_array)
        
        if not action_arrays:
            return {'quality': 'poor', 'issues': ['No valid action data'], 'metrics': {}}
        
        action_matrix = np.array(action_arrays)
        
        # Check action ranges
        for i in range(action_matrix.shape[1]):
            values = action_matrix[:, i]
            if np.any(values < self.thresholds['action_range'][0]) or np.any(values > self.thresholds['action_range'][1]):
                issues.append(f'Action values out of range for dimension {i}')
        
        # Check action smoothness
        if len(action_arrays) > 1:
            smoothness_scores = []
            for i in range(1, len(action_arrays)):
                prev_action = action_arrays[i-1]
                curr_action = action_arrays[i]
                change_magnitude = np.mean(np.abs(np.array(curr_action) - np.array(prev_action)))
                smoothness = 1.0 / (1.0 + change_magnitude)
                smoothness_scores.append(smoothness)
            
            avg_smoothness = np.mean(smoothness_scores)
            metrics['action_smoothness'] = avg_smoothness
            
            if avg_smoothness < 0.5:
                issues.append(f'Poor action smoothness: {avg_smoothness:.3f}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 1 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_rewards(self, rewards: List[float]) -> Dict:
        """Validate reward data"""
        if not rewards:
            return {'quality': 'poor', 'issues': ['No reward data'], 'metrics': {}}
        
        issues = []
        metrics = {}
        
        rewards_array = np.array(rewards)
        
        # Check reward range
        if np.any(rewards_array < self.thresholds['reward_range'][0]) or np.any(rewards_array > self.thresholds['reward_range'][1]):
            issues.append('Reward values out of range')
        
        # Check for NaN or infinite values
        nan_count = np.sum(np.isnan(rewards_array))
        inf_count = np.sum(np.isinf(rewards_array))
        
        if nan_count > 0:
            issues.append(f'NaN values in rewards: {nan_count}')
        
        if inf_count > 0:
            issues.append(f'Infinite values in rewards: {inf_count}')
        
        metrics['nan_count'] = nan_count
        metrics['inf_count'] = inf_count
        metrics['reward_mean'] = np.mean(rewards_array[~np.isnan(rewards_array)])
        metrics['reward_std'] = np.std(rewards_array[~np.isnan(rewards_array)])
        
        # Check reward distribution
        if len(rewards_array) > 10:
            # Check for reward sparsity
            unique_rewards = len(np.unique(rewards_array))
            sparsity = 1.0 - unique_rewards / len(rewards_array)
            
            if sparsity > 0.9:
                issues.append(f'High reward sparsity: {sparsity:.3f}')
            
            metrics['reward_sparsity'] = sparsity
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 1 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def validate_sar_consistency(self, rl_data: Dict) -> Dict:
        """Validate state-action-reward consistency"""
        issues = []
        metrics = {}
        
        states = rl_data.get('states', [])
        actions = rl_data.get('actions', [])
        rewards = rl_data.get('rewards', [])
        
        # Check data length consistency
        if len(states) != len(actions) or len(states) != len(rewards) + 1:
            issues.append(f'Data length mismatch: states={len(states)}, actions={len(actions)}, rewards={len(rewards)}')
        
        # Check temporal consistency
        if len(states) > 1:
            time_consistency_scores = []
            for i in range(1, len(states)):
                prev_state = states[i-1]
                curr_state = states[i]
                
                # Check if states are temporally ordered
                prev_time = prev_state.get('timestamp', i-1)
                curr_time = curr_state.get('timestamp', i)
                
                if isinstance(prev_time, str) and isinstance(curr_time, str):
                    from datetime import datetime
                    prev_dt = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))
                    curr_dt = datetime.fromisoformat(curr_time.replace('Z', '+00:00'))
                    time_diff = (curr_dt - prev_dt).total_seconds()
                else:
                    time_diff = curr_time - prev_time
                
                if time_diff < 0:
                    issues.append(f'Negative time difference at step {i}')
                
                time_consistency_scores.append(time_diff)
            
            if time_consistency_scores:
                time_std = np.std(time_consistency_scores)
                expected_interval = 1.0 / self.config.get('fps', 120)
                time_consistency = 1.0 - time_std / expected_interval
                metrics['time_consistency'] = time_consistency
                
                if time_consistency < 0.8:
                    issues.append(f'Poor time consistency: {time_consistency:.3f}')
        
        quality = 'good' if len(issues) == 0 else 'poor' if len(issues) > 1 else 'fair'
        
        return {
            'quality': quality,
            'issues': issues,
            'metrics': metrics
        }
    
    def calculate_missing_data_ratio(self, arrays: List[np.ndarray]) -> float:
        """Calculate ratio of missing data across arrays"""
        total_elements = sum(arr.size for arr in arrays)
        missing_elements = sum(np.sum(np.isnan(arr)) for arr in arrays)
        return missing_elements / total_elements if total_elements > 0 else 0.0
    
    def calculate_outlier_ratio(self, values: List[float]) -> float:
        """Calculate ratio of outliers in values"""
        if len(values) < 3:
            return 0.0
        
        values_array = np.array(values)
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        
        outlier_mask = np.abs(values_array - mean_val) > self.quality_metrics['outlier_threshold'] * std_val
        return np.sum(outlier_mask) / len(values_array)
    
    def calculate_displacement_continuity(self, U_arrays: List[np.ndarray], 
                                        V_arrays: List[np.ndarray], 
                                        W_arrays: List[np.ndarray]) -> float:
        """Calculate displacement field continuity"""
        if len(U_arrays) < 2:
            return 1.0
        
        continuity_scores = []
        for i in range(1, len(U_arrays)):
            prev_U, prev_V, prev_W = U_arrays[i-1], V_arrays[i-1], W_arrays[i-1]
            curr_U, curr_V, curr_W = U_arrays[i], V_arrays[i], W_arrays[i]
            
            # Calculate change magnitude
            U_change = np.mean(np.abs(curr_U - prev_U))
            V_change = np.mean(np.abs(curr_V - prev_V))
            W_change = np.mean(np.abs(curr_W - prev_W))
            
            # Normalize by expected change
            expected_change = 0.1  # pixels per frame
            continuity = 1.0 / (1.0 + (U_change + V_change + W_change) / expected_change)
            continuity_scores.append(continuity)
        
        return np.mean(continuity_scores)
    
    def calculate_field_smoothness(self, *fields: np.ndarray) -> float:
        """Calculate field smoothness score"""
        smoothness_scores = []
        for field in fields:
            # Calculate spatial gradients
            grad_x = np.gradient(field, axis=1)
            grad_y = np.gradient(field, axis=0)
            
            # Calculate gradient magnitude
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Smoothness is inverse of gradient magnitude
            smoothness = 1.0 / (1.0 + np.mean(grad_magnitude))
            smoothness_scores.append(smoothness)
        
        return np.mean(smoothness_scores)
    
    def check_strain_compatibility(self, eps_xx: np.ndarray, eps_yy: np.ndarray, 
                                 eps_xy: np.ndarray) -> float:
        """Check strain field compatibility"""
        # Calculate second derivatives
        d2eps_xx_dy2 = np.gradient(np.gradient(eps_xx, axis=0), axis=0)
        d2eps_yy_dx2 = np.gradient(np.gradient(eps_yy, axis=1), axis=1)
        d2eps_xy_dxdy = np.gradient(np.gradient(eps_xy, axis=1), axis=0)
        
        # Compatibility equation: d2eps_xx/dy2 + d2eps_yy/dx2 = 2*d2eps_xy/dxdy
        compatibility_error = np.abs(d2eps_xx_dy2 + d2eps_yy_dx2 - 2 * d2eps_xy_dxdy)
        
        # Calculate compatibility score
        max_error = np.max(compatibility_error)
        compatibility_score = 1.0 / (1.0 + max_error)
        
        return compatibility_score
    
    def assess_overall_quality(self, validation_results: Dict) -> Dict:
        """Assess overall data quality"""
        quality_scores = []
        all_issues = []
        
        for key, result in validation_results.items():
            if isinstance(result, dict) and 'quality' in result:
                if result['quality'] == 'good':
                    quality_scores.append(1.0)
                elif result['quality'] == 'fair':
                    quality_scores.append(0.5)
                else:
                    quality_scores.append(0.0)
                
                if 'issues' in result:
                    all_issues.extend(result['issues'])
        
        overall_quality_score = np.mean(quality_scores) if quality_scores else 0.0
        
        if overall_quality_score >= 0.8:
            overall_quality = 'excellent'
        elif overall_quality_score >= 0.6:
            overall_quality = 'good'
        elif overall_quality_score >= 0.4:
            overall_quality = 'fair'
        else:
            overall_quality = 'poor'
        
        validation_results['overall_quality'] = overall_quality
        validation_results['overall_quality_score'] = overall_quality_score
        validation_results['total_issues'] = len(all_issues)
        validation_results['all_issues'] = all_issues
        
        # Generate recommendations
        recommendations = self.generate_recommendations(validation_results)
        validation_results['recommendations'] = recommendations
        
        return validation_results
    
    def generate_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate recommendations for data improvement"""
        recommendations = []
        
        # Check for common issues
        if validation_results.get('total_issues', 0) > 5:
            recommendations.append("Consider data preprocessing to reduce noise and outliers")
        
        if 'displacement_validation' in validation_results:
            disp_val = validation_results['displacement_validation']
            if disp_val.get('quality') == 'poor':
                recommendations.append("Improve DIC correlation parameters or speckle pattern quality")
        
        if 'strain_validation' in validation_results:
            strain_val = validation_results['strain_validation']
            if strain_val.get('quality') == 'poor':
                recommendations.append("Apply strain field smoothing or filtering")
        
        if 'temporal_validation' in validation_results:
            temp_val = validation_results['temporal_validation']
            if temp_val.get('quality') == 'poor':
                recommendations.append("Check frame rate consistency and timing synchronization")
        
        if 'state_validation' in validation_results:
            state_val = validation_results['state_validation']
            if state_val.get('quality') == 'poor':
                recommendations.append("Normalize state values and remove outliers")
        
        if 'action_validation' in validation_results:
            action_val = validation_results['action_validation']
            if action_val.get('quality') == 'poor':
                recommendations.append("Smooth action sequences and check action bounds")
        
        if 'reward_validation' in validation_results:
            reward_val = validation_results['reward_validation']
            if reward_val.get('quality') == 'poor':
                recommendations.append("Review reward function and check for numerical issues")
        
        return recommendations
    
    def generate_validation_report(self, validation_results: Dict, save_path: str = None) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("DATA VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall quality
        overall_quality = validation_results.get('overall_quality', 'unknown')
        overall_score = validation_results.get('overall_quality_score', 0.0)
        total_issues = validation_results.get('total_issues', 0)
        
        report.append(f"Overall Quality: {overall_quality.upper()} (Score: {overall_score:.3f})")
        report.append(f"Total Issues Found: {total_issues}")
        report.append("")
        
        # Detailed results
        for key, result in validation_results.items():
            if isinstance(result, dict) and 'quality' in result:
                report.append(f"{key.replace('_', ' ').title()}:")
                report.append(f"  Quality: {result['quality']}")
                
                if 'issues' in result and result['issues']:
                    report.append(f"  Issues ({len(result['issues'])}):")
                    for issue in result['issues']:
                        report.append(f"    - {issue}")
                
                if 'metrics' in result and result['metrics']:
                    report.append(f"  Key Metrics:")
                    for metric, value in result['metrics'].items():
                        if isinstance(value, float):
                            report.append(f"    {metric}: {value:.6f}")
                        else:
                            report.append(f"    {metric}: {value}")
                
                report.append("")
        
        # Recommendations
        recommendations = validation_results.get('recommendations', [])
        if recommendations:
            report.append("RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
            print(f"Validation report saved to {save_path}")
        
        return report_text
    
    def visualize_validation_results(self, validation_results: Dict, save_path: str = None):
        """Visualize validation results"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Quality scores
        quality_scores = []
        quality_labels = []
        
        for key, result in validation_results.items():
            if isinstance(result, dict) and 'quality' in result:
                if result['quality'] == 'excellent':
                    score = 1.0
                elif result['quality'] == 'good':
                    score = 0.8
                elif result['quality'] == 'fair':
                    score = 0.5
                else:
                    score = 0.2
                
                quality_scores.append(score)
                quality_labels.append(key.replace('_', ' ').title())
        
        if quality_scores:
            axes[0].bar(quality_labels, quality_scores, color=['red' if s < 0.5 else 'orange' if s < 0.8 else 'green' for s in quality_scores])
            axes[0].set_title('Quality Scores by Category')
            axes[0].set_ylabel('Quality Score')
            axes[0].tick_params(axis='x', rotation=45)
            axes[0].set_ylim(0, 1)
        
        # Issue counts
        issue_counts = []
        issue_labels = []
        
        for key, result in validation_results.items():
            if isinstance(result, dict) and 'issues' in result:
                issue_counts.append(len(result['issues']))
                issue_labels.append(key.replace('_', ' ').title())
        
        if issue_counts:
            axes[1].bar(issue_labels, issue_counts, color='red')
            axes[1].set_title('Issues by Category')
            axes[1].set_ylabel('Number of Issues')
            axes[1].tick_params(axis='x', rotation=45)
        
        # Hide unused subplots
        for i in range(2, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()

def main():
    """Example usage of data validation"""
    # Example configuration
    config = {
        'fps': 120,
        'total_duration': 3600,
        'n_zones': 4
    }
    
    # Create validator
    validator = DataValidator(config)
    
    # Example validation (would use real data in practice)
    print("Data validation tools ready!")
    print("Use validator.validate_dic_data() and validator.validate_rl_data() with your data")

if __name__ == "__main__":
    main()