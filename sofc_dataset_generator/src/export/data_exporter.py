"""
Data export and storage module for SOFC simulation results.
Handles saving of 3D field data, parameters, and metadata in various formats.
"""

import numpy as np
import h5py
import pandas as pd
import json
import yaml
import os
from typing import Dict, List, Tuple, Optional, Any, Union
import meshio
import vtk
from vtk.util.numpy_support import numpy_to_vtk
import xarray as xr
from datetime import datetime
import pickle


class SOFCDataExporter:
    """
    Exports SOFC simulation data in multiple formats for machine learning applications.
    """
    
    def __init__(self, output_dir: str, config: Dict[str, Any]):
        """
        Initialize data exporter.
        
        Args:
            output_dir: Base output directory
            config: Configuration dictionary
        """
        self.output_dir = output_dir
        self.config = config
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'hdf5'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'vtk'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'csv'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'metadata'), exist_ok=True)
        
        # Initialize dataset metadata
        self.dataset_metadata = {
            'creation_date': datetime.now().isoformat(),
            'config': config,
            'samples': []
        }
        
    def export_sample(self, sample_id: int, parameters: Dict[str, float], 
                     simulation_results: Dict[str, Dict[str, Any]], 
                     mesh_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Export a single simulation sample.
        
        Args:
            sample_id: Sample identifier
            parameters: Input parameters
            simulation_results: Results from all physics simulations
            mesh_info: Mesh and geometry information
            
        Returns:
            Dictionary with paths to exported files
        """
        
        export_paths = {}
        
        # Export to HDF5 format (primary format for ML)
        hdf5_path = self._export_to_hdf5(sample_id, parameters, simulation_results, mesh_info)
        export_paths['hdf5'] = hdf5_path
        
        # Export to VTK format (for visualization)
        vtk_path = self._export_to_vtk(sample_id, simulation_results, mesh_info)
        export_paths['vtk'] = vtk_path
        
        # Export parameters to CSV
        csv_path = self._export_parameters_to_csv(sample_id, parameters)
        export_paths['csv'] = csv_path
        
        # Export metadata
        metadata_path = self._export_sample_metadata(sample_id, parameters, 
                                                   simulation_results, mesh_info)
        export_paths['metadata'] = metadata_path
        
        # Update dataset metadata
        self._update_dataset_metadata(sample_id, parameters, simulation_results, export_paths)
        
        return export_paths
        
    def _export_to_hdf5(self, sample_id: int, parameters: Dict[str, float], 
                       simulation_results: Dict[str, Dict[str, Any]], 
                       mesh_info: Dict[str, Any]) -> str:
        """
        Export sample data to HDF5 format.
        
        Args:
            sample_id: Sample identifier
            parameters: Input parameters
            simulation_results: Simulation results
            mesh_info: Mesh information
            
        Returns:
            Path to HDF5 file
        """
        
        filename = os.path.join(self.output_dir, 'hdf5', f'sample_{sample_id:06d}.h5')
        
        with h5py.File(filename, 'w') as f:
            # Create groups for different data types
            input_group = f.create_group('inputs')
            output_group = f.create_group('outputs')
            mesh_group = f.create_group('mesh')
            metadata_group = f.create_group('metadata')
            
            # Store input parameters
            for param_name, param_value in parameters.items():
                input_group.create_dataset(param_name, data=param_value)
            
            # Store mesh information
            if 'coordinates' in mesh_info:
                mesh_group.create_dataset('coordinates', data=mesh_info['coordinates'])
            if 'connectivity' in mesh_info:
                mesh_group.create_dataset('connectivity', data=mesh_info['connectivity'])
            if 'cell_types' in mesh_info:
                mesh_group.create_dataset('cell_types', data=mesh_info['cell_types'])
            
            # Store simulation results
            for physics, results in simulation_results.items():
                physics_group = output_group.create_group(physics)
                
                # Store field data
                if 'field_data' in results:
                    field_group = physics_group.create_group('fields')
                    for field_name, field_data in results['field_data'].items():
                        if field_name != 'coordinates':  # Skip coordinates (stored in mesh)
                            field_group.create_dataset(field_name, data=field_data, 
                                                     compression='gzip', compression_opts=9)
                
                # Store metrics
                if 'metrics' in results:
                    metrics_group = physics_group.create_group('metrics')
                    for metric_name, metric_value in results['metrics'].items():
                        metrics_group.create_dataset(metric_name, data=metric_value)
            
            # Store metadata
            metadata_group.create_dataset('sample_id', data=sample_id)
            metadata_group.create_dataset('timestamp', data=datetime.now().isoformat().encode())
            
            # Store configuration as JSON string
            config_str = json.dumps(self.config, indent=2)
            metadata_group.create_dataset('config', data=config_str.encode())
        
        return filename
        
    def _export_to_vtk(self, sample_id: int, simulation_results: Dict[str, Dict[str, Any]], 
                      mesh_info: Dict[str, Any]) -> str:
        """
        Export sample data to VTK format for visualization.
        
        Args:
            sample_id: Sample identifier
            simulation_results: Simulation results
            mesh_info: Mesh information
            
        Returns:
            Path to VTK file
        """
        
        filename = os.path.join(self.output_dir, 'vtk', f'sample_{sample_id:06d}.vtu')
        
        # Create VTK unstructured grid
        grid = vtk.vtkUnstructuredGrid()
        
        # Add points (mesh coordinates)
        if 'coordinates' in mesh_info:
            points = vtk.vtkPoints()
            coords = mesh_info['coordinates']
            
            for i in range(coords.shape[0]):
                if coords.shape[1] == 2:
                    # 2D mesh - add z=0
                    points.InsertNextPoint(coords[i, 0], coords[i, 1], 0.0)
                else:
                    # 3D mesh
                    points.InsertNextPoint(coords[i, 0], coords[i, 1], coords[i, 2])
            
            grid.SetPoints(points)
        
        # Add cells (mesh connectivity)
        if 'connectivity' in mesh_info and 'cell_types' in mesh_info:
            connectivity = mesh_info['connectivity']
            cell_types = mesh_info['cell_types']
            
            for i, cell_type in enumerate(cell_types):
                if cell_type == 10:  # VTK_TETRA
                    cell = vtk.vtkTetra()
                    for j in range(4):
                        cell.GetPointIds().SetId(j, connectivity[i, j])
                elif cell_type == 12:  # VTK_HEXAHEDRON
                    cell = vtk.vtkHexahedron()
                    for j in range(8):
                        cell.GetPointIds().SetId(j, connectivity[i, j])
                else:
                    continue  # Skip unsupported cell types
                
                grid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
        
        # Add field data as point data
        for physics, results in simulation_results.items():
            if 'field_data' in results:
                for field_name, field_data in results['field_data'].items():
                    if field_name == 'coordinates':
                        continue
                    
                    if len(field_data.shape) == 1:
                        # Scalar field
                        vtk_array = numpy_to_vtk(field_data)
                        vtk_array.SetName(f"{physics}_{field_name}")
                        grid.GetPointData().AddArray(vtk_array)
                    elif len(field_data.shape) == 2 and field_data.shape[1] <= 3:
                        # Vector field
                        if field_data.shape[1] < 3:
                            # Pad to 3D
                            padded_data = np.zeros((field_data.shape[0], 3))
                            padded_data[:, :field_data.shape[1]] = field_data
                            field_data = padded_data
                        
                        vtk_array = numpy_to_vtk(field_data)
                        vtk_array.SetName(f"{physics}_{field_name}")
                        grid.GetPointData().AddArray(vtk_array)
        
        # Write VTK file
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(filename)
        writer.SetInputData(grid)
        writer.Write()
        
        return filename
        
    def _export_parameters_to_csv(self, sample_id: int, parameters: Dict[str, float]) -> str:
        """
        Export parameters to CSV format.
        
        Args:
            sample_id: Sample identifier
            parameters: Input parameters
            
        Returns:
            Path to CSV file
        """
        
        filename = os.path.join(self.output_dir, 'csv', f'parameters_{sample_id:06d}.csv')
        
        # Create DataFrame
        df = pd.DataFrame([parameters])
        df.insert(0, 'sample_id', sample_id)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
        return filename
        
    def _export_sample_metadata(self, sample_id: int, parameters: Dict[str, float], 
                               simulation_results: Dict[str, Dict[str, Any]], 
                               mesh_info: Dict[str, Any]) -> str:
        """
        Export sample metadata to YAML format.
        
        Args:
            sample_id: Sample identifier
            parameters: Input parameters
            simulation_results: Simulation results
            mesh_info: Mesh information
            
        Returns:
            Path to metadata file
        """
        
        filename = os.path.join(self.output_dir, 'metadata', f'sample_{sample_id:06d}_metadata.yaml')
        
        # Collect metrics from all physics
        all_metrics = {}
        for physics, results in simulation_results.items():
            if 'metrics' in results:
                all_metrics[physics] = results['metrics']
        
        metadata = {
            'sample_id': sample_id,
            'timestamp': datetime.now().isoformat(),
            'parameters': parameters,
            'metrics': all_metrics,
            'mesh_info': {
                'n_nodes': mesh_info.get('n_nodes', 0),
                'n_elements': mesh_info.get('n_elements', 0),
                'bounding_box': mesh_info.get('bounding_box', {})
            }
        }
        
        with open(filename, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False)
        
        return filename
        
    def _update_dataset_metadata(self, sample_id: int, parameters: Dict[str, float], 
                                simulation_results: Dict[str, Dict[str, Any]], 
                                export_paths: Dict[str, str]):
        """
        Update dataset-level metadata.
        
        Args:
            sample_id: Sample identifier
            parameters: Input parameters
            simulation_results: Simulation results
            export_paths: Paths to exported files
        """
        
        # Collect metrics
        all_metrics = {}
        for physics, results in simulation_results.items():
            if 'metrics' in results:
                all_metrics[physics] = results['metrics']
        
        sample_metadata = {
            'sample_id': sample_id,
            'parameters': parameters,
            'metrics': all_metrics,
            'export_paths': export_paths,
            'timestamp': datetime.now().isoformat()
        }
        
        self.dataset_metadata['samples'].append(sample_metadata)
        
    def export_dataset_summary(self) -> str:
        """
        Export dataset-level summary and metadata.
        
        Returns:
            Path to dataset summary file
        """
        
        # Calculate dataset statistics
        if self.dataset_metadata['samples']:
            # Parameter statistics
            param_stats = self._calculate_parameter_statistics()
            
            # Metric statistics
            metric_stats = self._calculate_metric_statistics()
            
            # Update metadata
            self.dataset_metadata['statistics'] = {
                'n_samples': len(self.dataset_metadata['samples']),
                'parameter_statistics': param_stats,
                'metric_statistics': metric_stats
            }
        
        # Export dataset metadata
        metadata_filename = os.path.join(self.output_dir, 'dataset_metadata.yaml')
        with open(metadata_filename, 'w') as f:
            yaml.dump(self.dataset_metadata, f, default_flow_style=False)
        
        # Export parameter summary as CSV
        csv_filename = self._export_parameter_summary_csv()
        
        # Export metric summary as CSV
        metric_csv_filename = self._export_metric_summary_csv()
        
        return metadata_filename
        
    def _calculate_parameter_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistics for all parameters across the dataset.
        
        Returns:
            Dictionary with parameter statistics
        """
        
        # Collect all parameters
        all_params = {}
        for sample in self.dataset_metadata['samples']:
            for param_name, param_value in sample['parameters'].items():
                if param_name not in all_params:
                    all_params[param_name] = []
                all_params[param_name].append(param_value)
        
        # Calculate statistics
        param_stats = {}
        for param_name, values in all_params.items():
            values_array = np.array(values)
            param_stats[param_name] = {
                'mean': float(np.mean(values_array)),
                'std': float(np.std(values_array)),
                'min': float(np.min(values_array)),
                'max': float(np.max(values_array)),
                'median': float(np.median(values_array)),
                'q25': float(np.percentile(values_array, 25)),
                'q75': float(np.percentile(values_array, 75))
            }
        
        return param_stats
        
    def _calculate_metric_statistics(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Calculate statistics for all metrics across the dataset.
        
        Returns:
            Dictionary with metric statistics organized by physics
        """
        
        # Collect all metrics by physics
        all_metrics = {}
        for sample in self.dataset_metadata['samples']:
            for physics, metrics in sample['metrics'].items():
                if physics not in all_metrics:
                    all_metrics[physics] = {}
                for metric_name, metric_value in metrics.items():
                    if metric_name not in all_metrics[physics]:
                        all_metrics[physics][metric_name] = []
                    all_metrics[physics][metric_name].append(metric_value)
        
        # Calculate statistics
        metric_stats = {}
        for physics, physics_metrics in all_metrics.items():
            metric_stats[physics] = {}
            for metric_name, values in physics_metrics.items():
                values_array = np.array(values)
                metric_stats[physics][metric_name] = {
                    'mean': float(np.mean(values_array)),
                    'std': float(np.std(values_array)),
                    'min': float(np.min(values_array)),
                    'max': float(np.max(values_array)),
                    'median': float(np.median(values_array)),
                    'q25': float(np.percentile(values_array, 25)),
                    'q75': float(np.percentile(values_array, 75))
                }
        
        return metric_stats
        
    def _export_parameter_summary_csv(self) -> str:
        """
        Export parameter summary as CSV.
        
        Returns:
            Path to parameter summary CSV
        """
        
        filename = os.path.join(self.output_dir, 'parameter_summary.csv')
        
        # Create DataFrame with all parameters
        param_data = []
        for sample in self.dataset_metadata['samples']:
            param_row = {'sample_id': sample['sample_id']}
            param_row.update(sample['parameters'])
            param_data.append(param_row)
        
        df = pd.DataFrame(param_data)
        df.to_csv(filename, index=False)
        
        return filename
        
    def _export_metric_summary_csv(self) -> str:
        """
        Export metric summary as CSV.
        
        Returns:
            Path to metric summary CSV
        """
        
        filename = os.path.join(self.output_dir, 'metric_summary.csv')
        
        # Create DataFrame with all metrics
        metric_data = []
        for sample in self.dataset_metadata['samples']:
            metric_row = {'sample_id': sample['sample_id']}
            
            # Flatten metrics from all physics
            for physics, metrics in sample['metrics'].items():
                for metric_name, metric_value in metrics.items():
                    metric_row[f"{physics}_{metric_name}"] = metric_value
            
            metric_data.append(metric_row)
        
        df = pd.DataFrame(metric_data)
        df.to_csv(filename, index=False)
        
        return filename
        
    def create_ml_dataset(self, output_format: str = 'hdf5') -> str:
        """
        Create a consolidated dataset for machine learning.
        
        Args:
            output_format: Output format ('hdf5', 'npz', 'pickle')
            
        Returns:
            Path to ML dataset file
        """
        
        if output_format == 'hdf5':
            return self._create_ml_hdf5_dataset()
        elif output_format == 'npz':
            return self._create_ml_npz_dataset()
        elif output_format == 'pickle':
            return self._create_ml_pickle_dataset()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    def _create_ml_hdf5_dataset(self) -> str:
        """
        Create consolidated HDF5 dataset for ML.
        
        Returns:
            Path to ML dataset file
        """
        
        filename = os.path.join(self.output_dir, 'sofc_ml_dataset.h5')
        
        with h5py.File(filename, 'w') as f:
            # Create groups
            inputs_group = f.create_group('inputs')
            outputs_group = f.create_group('outputs')
            metadata_group = f.create_group('metadata')
            
            # Collect all data
            n_samples = len(self.dataset_metadata['samples'])
            
            # Get parameter names and create input arrays
            if n_samples > 0:
                param_names = list(self.dataset_metadata['samples'][0]['parameters'].keys())
                n_params = len(param_names)
                
                input_array = np.zeros((n_samples, n_params))
                
                for i, sample in enumerate(self.dataset_metadata['samples']):
                    for j, param_name in enumerate(param_names):
                        input_array[i, j] = sample['parameters'][param_name]
                
                inputs_group.create_dataset('parameters', data=input_array, 
                                          compression='gzip', compression_opts=9)
                inputs_group.create_dataset('parameter_names', 
                                          data=[name.encode() for name in param_names])
            
            # Store metadata
            metadata_group.create_dataset('n_samples', data=n_samples)
            metadata_group.create_dataset('creation_date', 
                                        data=datetime.now().isoformat().encode())
            
            # Store configuration
            config_str = json.dumps(self.config, indent=2)
            metadata_group.create_dataset('config', data=config_str.encode())
        
        return filename
        
    def _create_ml_npz_dataset(self) -> str:
        """
        Create consolidated NumPy dataset for ML.
        
        Returns:
            Path to ML dataset file
        """
        
        filename = os.path.join(self.output_dir, 'sofc_ml_dataset.npz')
        
        # Collect input parameters
        n_samples = len(self.dataset_metadata['samples'])
        if n_samples == 0:
            return filename
        
        param_names = list(self.dataset_metadata['samples'][0]['parameters'].keys())
        n_params = len(param_names)
        
        input_array = np.zeros((n_samples, n_params))
        
        for i, sample in enumerate(self.dataset_metadata['samples']):
            for j, param_name in enumerate(param_names):
                input_array[i, j] = sample['parameters'][param_name]
        
        # Save as compressed NumPy archive
        np.savez_compressed(filename, 
                           inputs=input_array,
                           parameter_names=param_names,
                           n_samples=n_samples,
                           config=self.config)
        
        return filename
        
    def _create_ml_pickle_dataset(self) -> str:
        """
        Create consolidated pickle dataset for ML.
        
        Returns:
            Path to ML dataset file
        """
        
        filename = os.path.join(self.output_dir, 'sofc_ml_dataset.pkl')
        
        # Create comprehensive dataset dictionary
        ml_dataset = {
            'metadata': self.dataset_metadata,
            'config': self.config,
            'creation_date': datetime.now().isoformat()
        }
        
        # Save as pickle
        with open(filename, 'wb') as f:
            pickle.dump(ml_dataset, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        return filename


if __name__ == "__main__":
    # Example usage
    config = {
        'dataset': {'n_samples': 100},
        'simulation': {'mesh_density': 'medium'}
    }
    
    exporter = SOFCDataExporter('test_output', config)
    
    # Mock data for testing
    sample_id = 0
    parameters = {'voltage': 0.7, 'temperature': 1073.0}
    
    simulation_results = {
        'electrochemical': {
            'field_data': {
                'electric_potential': np.random.rand(100),
                'current_density': np.random.rand(100, 3)
            },
            'metrics': {
                'average_current_density': 0.5,
                'power_density': 0.35
            }
        }
    }
    
    mesh_info = {
        'coordinates': np.random.rand(100, 3),
        'n_nodes': 100,
        'n_elements': 50
    }
    
    print("Data exporter module loaded successfully")
    print("Example export paths:", 
          exporter.export_sample(sample_id, parameters, simulation_results, mesh_info))