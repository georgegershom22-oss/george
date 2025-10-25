"""
Real-Time DIC Processing Module
Advanced algorithms for real-time displacement and strain computation
"""

import numpy as np
import cv2
from scipy import ndimage, interpolate
from scipy.optimize import minimize
from skimage import filters, feature, measure
from skimage.feature import peak_local_maxima
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

class RealTimeDICProcessor:
    """
    High-performance real-time DIC processing for high-temperature applications
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_parameters()
        self.initialize_templates()
        self.setup_processing_pipeline()
        
    def setup_parameters(self):
        """Initialize processing parameters"""
        self.subset_size = self.config.get('subset_size', 21)
        self.step_size = self.config.get('step_size', 5)
        self.correlation_threshold = self.config.get('correlation_threshold', 0.8)
        self.max_displacement = self.config.get('max_displacement', 10)
        self.interpolation_order = self.config.get('interpolation_order', 3)
        
        # Multi-scale processing
        self.scales = self.config.get('scales', [1.0, 0.5, 0.25])
        self.scale_weights = self.config.get('scale_weights', [0.5, 0.3, 0.2])
        
        # Robust estimation
        self.robust_iterations = self.config.get('robust_iterations', 3)
        self.outlier_threshold = self.config.get('outlier_threshold', 2.0)
        
        # Real-time optimization
        self.use_gpu = self.config.get('use_gpu', False)
        self.parallel_workers = self.config.get('parallel_workers', 4)
        
    def initialize_templates(self):
        """Initialize correlation templates"""
        self.templates = {}
        self.template_centers = {}
        self.template_quality = {}
        
    def setup_processing_pipeline(self):
        """Setup real-time processing pipeline"""
        self.frame_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=100)
        self.processing_thread = None
        self.is_processing = False
        
    def start_processing(self):
        """Start real-time processing thread"""
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.start()
        
    def stop_processing(self):
        """Stop real-time processing"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join()
    
    def add_frame(self, frame: np.ndarray, timestamp: float):
        """Add frame to processing queue"""
        if not self.frame_queue.full():
            self.frame_queue.put((frame, timestamp))
    
    def get_result(self) -> Optional[Dict]:
        """Get latest processing result"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def _processing_loop(self):
        """Main processing loop"""
        while self.is_processing:
            try:
                frame, timestamp = self.frame_queue.get(timeout=0.1)
                result = self.process_frame(frame, timestamp)
                if result and not self.result_queue.full():
                    self.result_queue.put(result)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")
    
    def process_frame(self, frame: np.ndarray, timestamp: float) -> Dict:
        """Process single frame for DIC analysis"""
        start_time = time.time()
        
        # Preprocess frame
        processed_frame = self.preprocess_frame(frame)
        
        # Multi-scale correlation
        displacement_fields = self.multi_scale_correlation(processed_frame)
        
        # Calculate strain fields
        strain_fields = self.calculate_strain_fields(displacement_fields)
        
        # Quality assessment
        quality_metrics = self.assess_quality(displacement_fields, strain_fields)
        
        # Extract key metrics
        key_metrics = self.extract_key_metrics(displacement_fields, strain_fields)
        
        processing_time = time.time() - start_time
        
        return {
            'timestamp': timestamp,
            'displacement_fields': displacement_fields,
            'strain_fields': strain_fields,
            'quality_metrics': quality_metrics,
            'key_metrics': key_metrics,
            'processing_time': processing_time
        }
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for optimal DIC performance"""
        # Convert to float
        if frame.dtype != np.float32:
            frame = frame.astype(np.float32)
        
        # Normalize intensity
        frame = (frame - np.mean(frame)) / np.std(frame)
        
        # Apply Gaussian filter to reduce noise
        frame = cv2.GaussianBlur(frame, (3, 3), 0)
        
        # Enhance contrast
        frame = cv2.equalizeHist(frame.astype(np.uint8)).astype(np.float32)
        
        return frame
    
    def multi_scale_correlation(self, frame: np.ndarray) -> Dict:
        """Perform multi-scale correlation for robust displacement estimation"""
        displacement_fields = {
            'U': np.zeros((frame.shape[0] // self.step_size, frame.shape[1] // self.step_size)),
            'V': np.zeros((frame.shape[0] // self.step_size, frame.shape[1] // self.step_size)),
            'confidence': np.zeros((frame.shape[0] // self.step_size, frame.shape[1] // self.step_size))
        }
        
        # Process each scale
        for scale_idx, scale in enumerate(self.scales):
            # Resize frame
            scaled_frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            # Calculate displacement at this scale
            scale_displacements = self.calculate_displacement_field(scaled_frame, scale)
            
            # Upsample to full resolution
            scale_displacements['U'] = cv2.resize(scale_displacements['U'], 
                                                (displacement_fields['U'].shape[1], displacement_fields['U'].shape[0]))
            scale_displacements['V'] = cv2.resize(scale_displacements['V'], 
                                                (displacement_fields['V'].shape[1], displacement_fields['V'].shape[0]))
            scale_displacements['confidence'] = cv2.resize(scale_displacements['confidence'], 
                                                         (displacement_fields['confidence'].shape[1], displacement_fields['confidence'].shape[0]))
            
            # Weighted combination
            weight = self.scale_weights[scale_idx]
            displacement_fields['U'] += weight * scale_displacements['U']
            displacement_fields['V'] += weight * scale_displacements['V']
            displacement_fields['confidence'] += weight * scale_displacements['confidence']
        
        return displacement_fields
    
    def calculate_displacement_field(self, frame: np.ndarray, scale: float = 1.0) -> Dict:
        """Calculate displacement field using subset correlation"""
        h, w = frame.shape
        subset_h, subset_w = int(self.subset_size * scale), int(self.subset_size * scale)
        step_h, step_w = int(self.step_size * scale), int(self.step_size * scale)
        
        # Initialize displacement fields
        U = np.zeros((h // step_h, w // step_w))
        V = np.zeros((h // step_h, w // step_w))
        confidence = np.zeros((h // step_h, w // step_w))
        
        # Process each subset
        for i in range(0, h - subset_h, step_h):
            for j in range(0, w - subset_w, step_w):
                subset_idx_i = i // step_h
                subset_idx_j = j // step_w
                
                # Extract subset
                subset = frame[i:i+subset_h, j:j+subset_w]
                
                # Find best match
                displacement, conf = self.find_best_match(subset, frame, i, j)
                
                U[subset_idx_i, subset_idx_j] = displacement[0]
                V[subset_idx_i, subset_idx_j] = displacement[1]
                confidence[subset_idx_i, subset_idx_j] = conf
        
        return {'U': U, 'V': V, 'confidence': confidence}
    
    def find_best_match(self, subset: np.ndarray, full_frame: np.ndarray, 
                       center_i: int, center_j: int) -> Tuple[np.ndarray, float]:
        """Find best match for subset using normalized cross-correlation"""
        subset_h, subset_w = subset.shape
        search_h, search_w = full_frame.shape
        
        # Define search region
        search_radius = self.max_displacement
        search_i_min = max(0, center_i - search_radius)
        search_i_max = min(search_h - subset_h, center_i + search_radius)
        search_j_min = max(0, center_j - search_radius)
        search_j_max = min(search_w - subset_w, center_j + search_radius)
        
        best_correlation = -1
        best_displacement = np.array([0, 0])
        
        # Search in region
        for i in range(search_i_min, search_i_max):
            for j in range(search_j_min, search_j_max):
                # Extract candidate region
                candidate = full_frame[i:i+subset_h, j:j+subset_w]
                
                # Calculate normalized cross-correlation
                correlation = self.normalized_cross_correlation(subset, candidate)
                
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_displacement = np.array([j - center_j, i - center_i])
        
        return best_displacement, best_correlation
    
    def normalized_cross_correlation(self, template: np.ndarray, candidate: np.ndarray) -> float:
        """Calculate normalized cross-correlation coefficient"""
        # Ensure same size
        if template.shape != candidate.shape:
            return 0.0
        
        # Flatten arrays
        t_flat = template.flatten()
        c_flat = candidate.flatten()
        
        # Calculate means
        t_mean = np.mean(t_flat)
        c_mean = np.mean(c_flat)
        
        # Calculate correlation
        numerator = np.sum((t_flat - t_mean) * (c_flat - c_mean))
        denominator = np.sqrt(np.sum((t_flat - t_mean)**2) * np.sum((c_flat - c_mean)**2))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def calculate_strain_fields(self, displacement_fields: Dict) -> Dict:
        """Calculate strain fields from displacement fields"""
        U = displacement_fields['U']
        V = displacement_fields['V']
        
        # Calculate gradients
        dU_dx = np.gradient(U, axis=1)
        dU_dy = np.gradient(U, axis=0)
        dV_dx = np.gradient(V, axis=1)
        dV_dy = np.gradient(V, axis=0)
        
        # Calculate strain components
        epsilon_xx = dU_dx
        epsilon_yy = dV_dy
        epsilon_xy = 0.5 * (dU_dy + dV_dx)
        
        # Calculate principal strains
        principal_strains = self.calculate_principal_strains(epsilon_xx, epsilon_yy, epsilon_xy)
        
        return {
            'epsilon_xx': epsilon_xx,
            'epsilon_yy': epsilon_yy,
            'epsilon_xy': epsilon_xy,
            'principal_strains': principal_strains
        }
    
    def calculate_principal_strains(self, epsilon_xx: np.ndarray, epsilon_yy: np.ndarray, 
                                  epsilon_xy: np.ndarray) -> Dict:
        """Calculate principal strains and directions"""
        # Calculate principal strain magnitudes
        trace = epsilon_xx + epsilon_yy
        det = epsilon_xx * epsilon_yy - epsilon_xy**2
        
        # Principal strains
        epsilon_1 = 0.5 * (trace + np.sqrt(trace**2 - 4 * det))
        epsilon_2 = 0.5 * (trace - np.sqrt(trace**2 - 4 * det))
        
        # Principal directions
        theta = 0.5 * np.arctan2(2 * epsilon_xy, epsilon_xx - epsilon_yy)
        
        return {
            'epsilon_1': epsilon_1,
            'epsilon_2': epsilon_2,
            'theta': theta,
            'max_shear': 0.5 * (epsilon_1 - epsilon_2)
        }
    
    def assess_quality(self, displacement_fields: Dict, strain_fields: Dict) -> Dict:
        """Assess quality of DIC measurements"""
        U = displacement_fields['U']
        V = displacement_fields['V']
        confidence = displacement_fields['confidence']
        
        # Displacement quality
        displacement_magnitude = np.sqrt(U**2 + V**2)
        displacement_std = np.std(displacement_magnitude)
        displacement_max = np.max(displacement_magnitude)
        
        # Strain quality
        epsilon_xx = strain_fields['epsilon_xx']
        epsilon_yy = strain_fields['epsilon_yy']
        epsilon_xy = strain_fields['epsilon_xy']
        
        strain_magnitude = np.sqrt(epsilon_xx**2 + epsilon_yy**2 + epsilon_xy**2)
        strain_std = np.std(strain_magnitude)
        strain_max = np.max(strain_magnitude)
        
        # Correlation quality
        avg_confidence = np.mean(confidence)
        min_confidence = np.min(confidence)
        low_confidence_ratio = np.sum(confidence < self.correlation_threshold) / confidence.size
        
        return {
            'displacement_std': float(displacement_std),
            'displacement_max': float(displacement_max),
            'strain_std': float(strain_std),
            'strain_max': float(strain_max),
            'avg_confidence': float(avg_confidence),
            'min_confidence': float(min_confidence),
            'low_confidence_ratio': float(low_confidence_ratio)
        }
    
    def extract_key_metrics(self, displacement_fields: Dict, strain_fields: Dict) -> Dict:
        """Extract key metrics for RL agent"""
        U = displacement_fields['U']
        V = displacement_fields['V']
        epsilon_xx = strain_fields['epsilon_xx']
        epsilon_yy = strain_fields['epsilon_yy']
        epsilon_xy = strain_fields['epsilon_xy']
        
        # Displacement metrics
        U_max = np.max(np.abs(U))
        V_max = np.max(np.abs(V))
        displacement_magnitude = np.sqrt(U**2 + V**2)
        max_displacement = np.max(displacement_magnitude)
        
        # Strain metrics
        strain_magnitude = np.sqrt(epsilon_xx**2 + epsilon_yy**2 + epsilon_xy**2)
        max_strain = np.max(strain_magnitude)
        mean_strain = np.mean(strain_magnitude)
        strain_heterogeneity = np.std(strain_magnitude)
        
        # Principal strain metrics
        principal_strains = strain_fields['principal_strains']
        max_principal_strain = np.max(principal_strains['epsilon_1'])
        min_principal_strain = np.min(principal_strains['epsilon_2'])
        max_shear_strain = np.max(principal_strains['max_shear'])
        
        # Curvature estimation (simplified)
        curvature = self.estimate_curvature(U, V)
        
        return {
            'max_displacement': float(max_displacement),
            'U_max': float(U_max),
            'V_max': float(V_max),
            'max_strain': float(max_strain),
            'mean_strain': float(mean_strain),
            'strain_heterogeneity': float(strain_heterogeneity),
            'max_principal_strain': float(max_principal_strain),
            'min_principal_strain': float(min_principal_strain),
            'max_shear_strain': float(max_shear_strain),
            'curvature': float(curvature)
        }
    
    def estimate_curvature(self, U: np.ndarray, V: np.ndarray) -> float:
        """Estimate sample curvature from displacement fields"""
        # Calculate second derivatives
        d2U_dx2 = np.gradient(np.gradient(U, axis=1), axis=1)
        d2V_dy2 = np.gradient(np.gradient(V, axis=0), axis=0)
        
        # Estimate curvature (simplified)
        curvature = np.mean(np.abs(d2U_dx2 + d2V_dy2))
        
        return curvature
    
    def robust_displacement_estimation(self, displacement_fields: Dict) -> Dict:
        """Apply robust estimation to remove outliers"""
        U = displacement_fields['U'].copy()
        V = displacement_fields['V'].copy()
        confidence = displacement_fields['confidence'].copy()
        
        for iteration in range(self.robust_iterations):
            # Calculate displacement magnitude
            magnitude = np.sqrt(U**2 + V**2)
            
            # Identify outliers
            mean_mag = np.mean(magnitude)
            std_mag = np.std(magnitude)
            outlier_mask = np.abs(magnitude - mean_mag) > self.outlier_threshold * std_mag
            
            # Interpolate over outliers
            if np.any(outlier_mask):
                U[outlier_mask] = np.nan
                V[outlier_mask] = np.nan
                
                # Interpolate
                U = self.interpolate_nan(U)
                V = self.interpolate_nan(V)
        
        return {'U': U, 'V': V, 'confidence': confidence}
    
    def interpolate_nan(self, data: np.ndarray) -> np.ndarray:
        """Interpolate NaN values in 2D array"""
        mask = ~np.isnan(data)
        if not np.any(mask):
            return data
        
        # Get valid points
        valid_points = np.column_stack(np.where(mask))
        valid_values = data[mask]
        
        # Get all points
        all_points = np.column_stack(np.where(np.ones_like(data, dtype=bool)))
        
        # Interpolate
        interpolated = interpolate.griddata(valid_points, valid_values, all_points, method='linear')
        
        # Reshape
        interpolated = interpolated.reshape(data.shape)
        
        # Fill remaining NaN with nearest neighbor
        nan_mask = np.isnan(interpolated)
        if np.any(nan_mask):
            from scipy.spatial.distance import cdist
            nan_points = np.column_stack(np.where(nan_mask))
            distances = cdist(nan_points, valid_points)
            nearest_indices = np.argmin(distances, axis=1)
            interpolated[nan_mask] = valid_values[nearest_indices]
        
        return interpolated

class AdvancedDICAnalyzer:
    """
    Advanced DIC analysis tools for high-temperature applications
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_analysis_parameters()
        
    def setup_analysis_parameters(self):
        """Setup analysis parameters"""
        self.temperature_compensation = self.config.get('temperature_compensation', True)
        self.thermal_expansion_coeff = self.config.get('thermal_expansion_coeff', 8e-6)
        self.reference_temperature = self.config.get('reference_temperature', 25)
        
    def analyze_thermal_effects(self, displacement_fields: Dict, temperature_field: np.ndarray) -> Dict:
        """Analyze thermal effects on displacement measurements"""
        U = displacement_fields['U']
        V = displacement_fields['V']
        
        # Calculate thermal expansion
        delta_T = temperature_field - self.reference_temperature
        thermal_U = self.thermal_expansion_coeff * delta_T * U.shape[1] * 0.1
        thermal_V = self.thermal_expansion_coeff * delta_T * U.shape[0] * 0.1
        
        # Remove thermal component
        mechanical_U = U - thermal_U
        mechanical_V = V - thermal_V
        
        return {
            'thermal_U': thermal_U,
            'thermal_V': thermal_V,
            'mechanical_U': mechanical_U,
            'mechanical_V': mechanical_V,
            'thermal_contribution': np.mean(np.abs(thermal_U)) / np.mean(np.abs(U))
        }
    
    def analyze_strain_localization(self, strain_fields: Dict) -> Dict:
        """Analyze strain localization patterns"""
        epsilon_xx = strain_fields['epsilon_xx']
        epsilon_yy = strain_fields['epsilon_yy']
        epsilon_xy = strain_fields['epsilon_xy']
        
        # Calculate equivalent strain
        equivalent_strain = np.sqrt(2/3 * (epsilon_xx**2 + epsilon_yy**2 + 2*epsilon_xy**2))
        
        # Find strain concentration regions
        threshold = np.mean(equivalent_strain) + 2 * np.std(equivalent_strain)
        concentration_mask = equivalent_strain > threshold
        
        # Analyze concentration regions
        if np.any(concentration_mask):
            labeled_regions = measure.label(concentration_mask)
            region_props = measure.regionprops(labeled_regions, equivalent_strain)
            
            max_strain_regions = []
            for region in region_props:
                max_strain_regions.append({
                    'area': region.area,
                    'max_strain': region.max_intensity,
                    'mean_strain': region.mean_intensity,
                    'centroid': region.centroid
                })
        else:
            max_strain_regions = []
        
        return {
            'equivalent_strain': equivalent_strain,
            'concentration_mask': concentration_mask,
            'max_strain_regions': max_strain_regions,
            'strain_concentration_ratio': np.sum(concentration_mask) / concentration_mask.size
        }
    
    def analyze_fatigue_damage(self, strain_history: List[Dict]) -> Dict:
        """Analyze fatigue damage accumulation"""
        if len(strain_history) < 2:
            return {'damage_accumulation': 0.0, 'critical_regions': []}
        
        # Calculate strain range for each point
        strain_ranges = []
        for i in range(1, len(strain_history)):
            prev_strain = strain_history[i-1]['equivalent_strain']
            curr_strain = strain_history[i]['equivalent_strain']
            strain_range = np.abs(curr_strain - prev_strain)
            strain_ranges.append(strain_range)
        
        # Calculate damage accumulation (simplified Miner's rule)
        damage_accumulation = np.sum(strain_ranges, axis=0)
        
        # Find critical regions
        threshold = np.mean(damage_accumulation) + 2 * np.std(damage_accumulation)
        critical_mask = damage_accumulation > threshold
        
        return {
            'damage_accumulation': damage_accumulation,
            'critical_regions': critical_mask,
            'max_damage': np.max(damage_accumulation),
            'mean_damage': np.mean(damage_accumulation)
        }