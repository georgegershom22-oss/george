"""
Main simulation runner for SOFC dataset generation.
Orchestrates the complete multi-physics simulation pipeline.
"""

import os
import sys
import yaml
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from tqdm import tqdm
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
from datetime import datetime
import traceback

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sampling.parameter_sampler import SOFCParameterSampler
from geometry.sofc_geometry import SOFCMeshGenerator
from simulation.electrochemical import ElectrochemicalSolver
from simulation.thermal import ThermalSolver
from simulation.mechanical import MechanicalSolver
from simulation.species_transport import SpeciesTransportSolver
from export.data_exporter import SOFCDataExporter


class SOFCSimulationRunner:
    """
    Main class for running SOFC simulation campaigns.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize simulation runner.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.parameter_sampler = SOFCParameterSampler(config_path)
        self.mesh_generator = SOFCMeshGenerator(config_path)
        self.electrochemical_solver = ElectrochemicalSolver(config_path)
        self.thermal_solver = ThermalSolver(config_path)
        self.mechanical_solver = MechanicalSolver(config_path)
        self.species_solver = SpeciesTransportSolver(config_path)
        
        # Setup output directory
        self.output_dir = self.config['dataset']['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize data exporter
        self.data_exporter = SOFCDataExporter(self.output_dir, self.config)
        
        self.logger.info(f"SOFC Simulation Runner initialized")
        self.logger.info(f"Output directory: {self.output_dir}")
        
    def _setup_logging(self):
        """Setup logging configuration."""
        
        log_dir = os.path.join(self.config['dataset']['output_dir'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def generate_dataset(self, n_samples: Optional[int] = None, 
                        parallel: bool = True, n_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate complete SOFC dataset.
        
        Args:
            n_samples: Number of samples to generate (overrides config)
            parallel: Whether to use parallel processing
            n_workers: Number of worker processes (None for auto)
            
        Returns:
            Dictionary with generation statistics
        """
        
        # Determine number of samples
        if n_samples is None:
            n_samples = self.config['dataset']['n_samples']
        
        self.logger.info(f"Starting dataset generation with {n_samples} samples")
        
        # Generate parameter samples
        self.logger.info("Generating parameter samples...")
        parameter_samples = self.parameter_sampler.generate_samples(
            n_samples, sampling_method='lhs', seed=42
        )
        
        # Save parameter samples
        param_file = os.path.join(self.output_dir, 'parameter_samples.csv')
        self.parameter_sampler.save_samples(parameter_samples, param_file)
        self.logger.info(f"Parameter samples saved to {param_file}")
        
        # Run simulations
        if parallel and n_samples > 1:
            results = self._run_parallel_simulations(parameter_samples, n_workers)
        else:
            results = self._run_sequential_simulations(parameter_samples)
        
        # Generate dataset summary
        summary_file = self.data_exporter.export_dataset_summary()
        self.logger.info(f"Dataset summary saved to {summary_file}")
        
        # Create ML-ready dataset
        ml_dataset_file = self.data_exporter.create_ml_dataset('hdf5')
        self.logger.info(f"ML dataset saved to {ml_dataset_file}")
        
        # Calculate generation statistics
        successful_samples = len([r for r in results if r['success']])
        failed_samples = len([r for r in results if not r['success']])
        
        statistics = {
            'total_samples': n_samples,
            'successful_samples': successful_samples,
            'failed_samples': failed_samples,
            'success_rate': successful_samples / n_samples,
            'output_directory': self.output_dir,
            'parameter_file': param_file,
            'summary_file': summary_file,
            'ml_dataset_file': ml_dataset_file
        }
        
        self.logger.info(f"Dataset generation completed:")
        self.logger.info(f"  Successful samples: {successful_samples}/{n_samples}")
        self.logger.info(f"  Success rate: {statistics['success_rate']:.2%}")
        
        return statistics
        
    def _run_sequential_simulations(self, parameter_samples: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run simulations sequentially.
        
        Args:
            parameter_samples: DataFrame with parameter samples
            
        Returns:
            List of simulation results
        """
        
        results = []
        
        for i, (_, params) in enumerate(tqdm(parameter_samples.iterrows(), 
                                           total=len(parameter_samples),
                                           desc="Running simulations")):
            
            try:
                result = self._run_single_simulation(i, params.to_dict())
                results.append(result)
                
                if result['success']:
                    self.logger.info(f"Sample {i} completed successfully")
                else:
                    self.logger.warning(f"Sample {i} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"Sample {i} failed with exception: {e}")
                results.append({
                    'sample_id': i,
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        return results
        
    def _run_parallel_simulations(self, parameter_samples: pd.DataFrame, 
                                 n_workers: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Run simulations in parallel.
        
        Args:
            parameter_samples: DataFrame with parameter samples
            n_workers: Number of worker processes
            
        Returns:
            List of simulation results
        """
        
        if n_workers is None:
            n_workers = min(mp.cpu_count(), len(parameter_samples))
        
        self.logger.info(f"Running simulations with {n_workers} workers")
        
        results = [None] * len(parameter_samples)
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            # Submit all jobs
            future_to_index = {}
            for i, (_, params) in enumerate(parameter_samples.iterrows()):
                future = executor.submit(self._run_single_simulation, i, params.to_dict())
                future_to_index[future] = i
            
            # Collect results with progress bar
            with tqdm(total=len(parameter_samples), desc="Running simulations") as pbar:
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    
                    try:
                        result = future.result()
                        results[index] = result
                        
                        if result['success']:
                            self.logger.info(f"Sample {index} completed successfully")
                        else:
                            self.logger.warning(f"Sample {index} failed: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        self.logger.error(f"Sample {index} failed with exception: {e}")
                        results[index] = {
                            'sample_id': index,
                            'success': False,
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        }
                    
                    pbar.update(1)
        
        return results
        
    def _run_single_simulation(self, sample_id: int, parameters: Dict[str, float]) -> Dict[str, Any]:
        """
        Run a single multi-physics simulation.
        
        Args:
            sample_id: Sample identifier
            parameters: Parameter dictionary
            
        Returns:
            Dictionary with simulation results and metadata
        """
        
        try:
            # Step 1: Generate mesh
            mesh_dir = os.path.join(self.output_dir, 'meshes')
            os.makedirs(mesh_dir, exist_ok=True)
            
            mesh_file = self.mesh_generator.generate_mesh_for_parameters(
                parameters, mesh_dir, sample_id
            )
            
            # Load geometry info
            info_file = mesh_file.replace('.msh', '_info.yaml')
            with open(info_file, 'r') as f:
                geometry_info = yaml.safe_load(f)
            
            # Step 2: Solve electrochemical problem
            electrochemical_results = self.electrochemical_solver.solve_for_parameters(
                mesh_file, parameters, geometry_info
            )
            
            # Step 3: Solve thermal problem (coupled with electrochemical)
            thermal_results = self.thermal_solver.solve_for_parameters(
                mesh_file, parameters, geometry_info, electrochemical_results
            )
            
            # Step 4: Solve mechanical problem (coupled with thermal)
            mechanical_results = self.mechanical_solver.solve_for_parameters(
                mesh_file, parameters, geometry_info, thermal_results
            )
            
            # Step 5: Solve species transport (coupled with electrochemical and thermal)
            species_results = self.species_solver.solve_for_parameters(
                mesh_file, parameters, geometry_info, 
                electrochemical_results, thermal_results
            )
            
            # Step 6: Combine all results
            simulation_results = {
                'electrochemical': electrochemical_results,
                'thermal': thermal_results,
                'mechanical': mechanical_results,
                'species_transport': species_results
            }
            
            # Step 7: Export data
            export_paths = self.data_exporter.export_sample(
                sample_id, parameters, simulation_results, geometry_info
            )
            
            return {
                'sample_id': sample_id,
                'success': True,
                'parameters': parameters,
                'simulation_results': simulation_results,
                'export_paths': export_paths,
                'mesh_file': mesh_file
            }
            
        except Exception as e:
            return {
                'sample_id': sample_id,
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'parameters': parameters
            }
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Validate the generated dataset.
        
        Returns:
            Dictionary with validation results
        """
        
        self.logger.info("Validating generated dataset...")
        
        validation_results = {
            'parameter_validation': self._validate_parameters(),
            'file_validation': self._validate_files(),
            'data_quality': self._validate_data_quality()
        }
        
        # Save validation report
        validation_file = os.path.join(self.output_dir, 'validation_report.yaml')
        with open(validation_file, 'w') as f:
            yaml.dump(validation_results, f, default_flow_style=False)
        
        self.logger.info(f"Validation report saved to {validation_file}")
        
        return validation_results
        
    def _validate_parameters(self) -> Dict[str, Any]:
        """Validate parameter samples."""
        
        param_file = os.path.join(self.output_dir, 'parameter_samples.csv')
        
        if not os.path.exists(param_file):
            return {'status': 'failed', 'error': 'Parameter file not found'}
        
        try:
            df = pd.read_csv(param_file)
            
            # Check parameter ranges
            param_info = self.parameter_sampler.get_parameter_info()
            range_violations = []
            
            for param_name, info in param_info.items():
                if param_name in df.columns:
                    values = df[param_name]
                    if values.min() < info['min'] or values.max() > info['max']:
                        range_violations.append(param_name)
            
            return {
                'status': 'passed' if not range_violations else 'warning',
                'n_samples': len(df),
                'n_parameters': len(df.columns) - 1,  # Exclude sample_id
                'range_violations': range_violations
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
            
    def _validate_files(self) -> Dict[str, Any]:
        """Validate exported files."""
        
        # Check for required directories
        required_dirs = ['hdf5', 'vtk', 'csv', 'metadata', 'meshes']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = os.path.join(self.output_dir, dir_name)
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_name)
        
        # Count files in each directory
        file_counts = {}
        for dir_name in required_dirs:
            dir_path = os.path.join(self.output_dir, dir_name)
            if os.path.exists(dir_path):
                file_counts[dir_name] = len(os.listdir(dir_path))
            else:
                file_counts[dir_name] = 0
        
        return {
            'status': 'passed' if not missing_dirs else 'warning',
            'missing_directories': missing_dirs,
            'file_counts': file_counts
        }
        
    def _validate_data_quality(self) -> Dict[str, Any]:
        """Validate data quality."""
        
        # Check dataset summary
        summary_file = os.path.join(self.output_dir, 'dataset_metadata.yaml')
        
        if not os.path.exists(summary_file):
            return {'status': 'failed', 'error': 'Dataset summary not found'}
        
        try:
            with open(summary_file, 'r') as f:
                metadata = yaml.safe_load(f)
            
            n_samples = len(metadata.get('samples', []))
            
            # Check for NaN or infinite values in metrics
            invalid_metrics = []
            for sample in metadata.get('samples', []):
                for physics, metrics in sample.get('metrics', {}).items():
                    for metric_name, value in metrics.items():
                        if not np.isfinite(value):
                            invalid_metrics.append(f"{physics}.{metric_name}")
            
            return {
                'status': 'passed' if not invalid_metrics else 'warning',
                'n_samples': n_samples,
                'invalid_metrics': list(set(invalid_metrics))
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}


def main():
    """Main entry point for dataset generation."""
    
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate SOFC simulation dataset')
    parser.add_argument('--config', default='config/simulation_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--samples', type=int, default=None,
                       help='Number of samples to generate')
    parser.add_argument('--parallel', action='store_true', default=True,
                       help='Use parallel processing')
    parser.add_argument('--workers', type=int, default=None,
                       help='Number of worker processes')
    parser.add_argument('--validate', action='store_true', default=False,
                       help='Validate dataset after generation')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = SOFCSimulationRunner(args.config)
    
    # Generate dataset
    statistics = runner.generate_dataset(
        n_samples=args.samples,
        parallel=args.parallel,
        n_workers=args.workers
    )
    
    print("\nDataset Generation Summary:")
    print(f"Total samples: {statistics['total_samples']}")
    print(f"Successful: {statistics['successful_samples']}")
    print(f"Failed: {statistics['failed_samples']}")
    print(f"Success rate: {statistics['success_rate']:.2%}")
    print(f"Output directory: {statistics['output_directory']}")
    
    # Validate if requested
    if args.validate:
        validation_results = runner.validate_dataset()
        print(f"\nValidation Status: {validation_results}")
    
    print("\nDataset generation completed!")


if __name__ == "__main__":
    main()