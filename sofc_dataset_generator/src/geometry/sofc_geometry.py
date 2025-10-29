"""
SOFC geometry generation and mesh creation module.
Creates 3D geometries for single cells and stacks with proper material domains.
"""

import numpy as np
import gmsh
import meshio
from typing import Dict, List, Tuple, Optional, Any
import os
import yaml


class SOFCGeometry:
    """
    Creates 3D SOFC geometries with multiple layers and flow channels.
    """
    
    def __init__(self, parameters: Dict[str, float]):
        """
        Initialize SOFC geometry with given parameters.
        
        Args:
            parameters: Dictionary containing geometric and material parameters
        """
        self.params = parameters
        self.gmsh_initialized = False
        
        # Material domain IDs
        self.domain_ids = {
            'anode': 1,
            'electrolyte': 2, 
            'cathode': 3,
            'interconnect_anode': 4,
            'interconnect_cathode': 5,
            'fuel_channel': 6,
            'air_channel': 7
        }
        
        # Boundary IDs
        self.boundary_ids = {
            'fuel_inlet': 10,
            'fuel_outlet': 11,
            'air_inlet': 12,
            'air_outlet': 13,
            'anode_current_collector': 14,
            'cathode_current_collector': 15,
            'external_walls': 16
        }
    
    def create_single_cell_geometry(self, mesh_size: float = 0.001) -> Dict[str, Any]:
        """
        Create a 3D single cell SOFC geometry.
        
        Args:
            mesh_size: Characteristic mesh size
            
        Returns:
            Dictionary containing geometry information
        """
        if not self.gmsh_initialized:
            gmsh.initialize()
            self.gmsh_initialized = True
        
        gmsh.clear()
        gmsh.model.add("sofc_single_cell")
        
        # Extract dimensions
        length = self.params.get('length', 0.1)
        width = self.params.get('width', 0.1)
        
        # Layer thicknesses
        t_anode = self.params['anode_thickness']
        t_electrolyte = self.params['electrolyte_thickness']
        t_cathode = self.params['cathode_thickness']
        t_interconnect = self.params['interconnect_thickness']
        
        # Flow channel dimensions
        ch_width = self.params['channel_width']
        ch_height = self.params['channel_height']
        rib_width = self.params['rib_width']
        
        # Create layer stack from bottom to top
        z_positions = self._calculate_layer_positions(
            t_anode, t_electrolyte, t_cathode, t_interconnect, ch_height
        )
        
        # Create solid layers
        layers = self._create_solid_layers(length, width, z_positions)
        
        # Create flow channels
        fuel_channels = self._create_flow_channels(
            length, width, z_positions['fuel_channel'], ch_width, ch_height, rib_width, 'fuel'
        )
        
        air_channels = self._create_flow_channels(
            length, width, z_positions['air_channel'], ch_width, ch_height, rib_width, 'air'
        )
        
        # Combine all volumes
        all_volumes = {**layers, **fuel_channels, **air_channels}
        
        # Set mesh sizes
        self._set_mesh_sizes(mesh_size)
        
        # Generate mesh
        gmsh.model.mesh.generate(3)
        
        # Get mesh information
        mesh_info = self._extract_mesh_info()
        
        geometry_info = {
            'domain_ids': self.domain_ids,
            'boundary_ids': self.boundary_ids,
            'volumes': all_volumes,
            'mesh_info': mesh_info,
            'parameters': self.params.copy()
        }
        
        return geometry_info
    
    def _calculate_layer_positions(self, t_anode: float, t_electrolyte: float, 
                                 t_cathode: float, t_interconnect: float, 
                                 ch_height: float) -> Dict[str, Tuple[float, float]]:
        """
        Calculate z-positions for all layers.
        
        Args:
            t_anode: Anode thickness
            t_electrolyte: Electrolyte thickness  
            t_cathode: Cathode thickness
            t_interconnect: Interconnect thickness
            ch_height: Channel height
            
        Returns:
            Dictionary with (z_min, z_max) for each layer
        """
        z = 0.0
        positions = {}
        
        # Bottom interconnect (anode side)
        positions['interconnect_anode'] = (z, z + t_interconnect)
        z += t_interconnect
        
        # Fuel channels
        positions['fuel_channel'] = (z, z + ch_height)
        z += ch_height
        
        # Anode
        positions['anode'] = (z, z + t_anode)
        z += t_anode
        
        # Electrolyte
        positions['electrolyte'] = (z, z + t_electrolyte)
        z += t_electrolyte
        
        # Cathode
        positions['cathode'] = (z, z + t_cathode)
        z += t_cathode
        
        # Air channels
        positions['air_channel'] = (z, z + ch_height)
        z += ch_height
        
        # Top interconnect (cathode side)
        positions['interconnect_cathode'] = (z, z + t_interconnect)
        
        return positions
    
    def _create_solid_layers(self, length: float, width: float, 
                           z_positions: Dict[str, Tuple[float, float]]) -> Dict[str, int]:
        """
        Create solid layer volumes.
        
        Args:
            length: Cell length
            width: Cell width
            z_positions: Z-positions for each layer
            
        Returns:
            Dictionary mapping layer names to volume tags
        """
        volumes = {}
        
        solid_layers = ['interconnect_anode', 'anode', 'electrolyte', 
                       'cathode', 'interconnect_cathode']
        
        for layer in solid_layers:
            if layer in z_positions:
                z_min, z_max = z_positions[layer]
                
                # Create rectangular box
                box_tag = gmsh.model.occ.addBox(0, 0, z_min, length, width, z_max - z_min)
                volumes[layer] = box_tag
                
                # Set physical group
                domain_id = self.domain_ids.get(layer, self.domain_ids.get(layer.split('_')[0], 1))
                gmsh.model.addPhysicalGroup(3, [box_tag], domain_id)
                gmsh.model.setPhysicalName(3, domain_id, layer)
        
        return volumes
    
    def _create_flow_channels(self, length: float, width: float, z_pos: Tuple[float, float],
                            ch_width: float, ch_height: float, rib_width: float,
                            channel_type: str) -> Dict[str, List[int]]:
        """
        Create flow channel geometry.
        
        Args:
            length: Cell length
            width: Cell width
            z_pos: (z_min, z_max) for channel layer
            ch_width: Channel width
            ch_height: Channel height
            rib_width: Rib width between channels
            channel_type: 'fuel' or 'air'
            
        Returns:
            Dictionary with channel volume tags
        """
        z_min, z_max = z_pos
        channel_volumes = []
        
        # Calculate number of channels that fit
        pitch = ch_width + rib_width
        n_channels = int(width // pitch)
        
        # Create channels along width direction
        for i in range(n_channels):
            y_start = i * pitch + rib_width / 2
            y_end = y_start + ch_width
            
            if y_end <= width:
                # Create channel volume
                channel_tag = gmsh.model.occ.addBox(0, y_start, z_min, 
                                                  length, ch_width, ch_height)
                channel_volumes.append(channel_tag)
        
        # Set physical group
        if channel_volumes:
            domain_id = self.domain_ids[f'{channel_type}_channel']
            gmsh.model.addPhysicalGroup(3, channel_volumes, domain_id)
            gmsh.model.setPhysicalName(3, domain_id, f'{channel_type}_channel')
        
        return {f'{channel_type}_channel': channel_volumes}
    
    def _set_mesh_sizes(self, base_size: float):
        """
        Set mesh sizes for different regions.
        
        Args:
            base_size: Base mesh size
        """
        # Get all points
        points = gmsh.model.getEntities(0)
        
        # Set different mesh sizes for different layers
        for point in points:
            point_tag = point[1]
            
            # Get point coordinates
            coords = gmsh.model.getValue(0, point_tag, [])
            z = coords[2] if len(coords) > 2 else 0
            
            # Finer mesh for thin electrolyte layer
            if self._is_in_electrolyte(z):
                mesh_size = base_size * 0.2  # 5x finer
            elif self._is_in_electrode(z):
                mesh_size = base_size * 0.5  # 2x finer
            else:
                mesh_size = base_size
            
            gmsh.model.mesh.setSize([point], mesh_size)
    
    def _is_in_electrolyte(self, z: float) -> bool:
        """Check if z-coordinate is in electrolyte layer."""
        # This would need the actual z-positions from layer calculation
        return False  # Placeholder
    
    def _is_in_electrode(self, z: float) -> bool:
        """Check if z-coordinate is in electrode layers."""
        # This would need the actual z-positions from layer calculation
        return False  # Placeholder
    
    def _extract_mesh_info(self) -> Dict[str, Any]:
        """
        Extract mesh information from gmsh.
        
        Returns:
            Dictionary with mesh statistics
        """
        # Get mesh statistics
        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements()
        
        mesh_info = {
            'n_nodes': len(node_tags),
            'n_elements': sum(len(tags) for tags in element_tags),
            'element_types': element_types,
            'bounding_box': self._get_bounding_box(node_coords)
        }
        
        return mesh_info
    
    def _get_bounding_box(self, node_coords: np.ndarray) -> Dict[str, Tuple[float, float]]:
        """
        Calculate bounding box from node coordinates.
        
        Args:
            node_coords: Flattened array of node coordinates
            
        Returns:
            Dictionary with min/max coordinates
        """
        coords = node_coords.reshape(-1, 3)
        
        return {
            'x': (coords[:, 0].min(), coords[:, 0].max()),
            'y': (coords[:, 1].min(), coords[:, 1].max()),
            'z': (coords[:, 2].min(), coords[:, 2].max())
        }
    
    def save_mesh(self, filename: str, format: str = 'msh'):
        """
        Save mesh to file.
        
        Args:
            filename: Output filename
            format: Mesh format ('msh', 'vtk', 'xdmf')
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if format == 'msh':
            gmsh.write(filename)
        elif format == 'vtk':
            gmsh.write(filename.replace('.msh', '.vtk'))
        elif format == 'xdmf':
            # Convert to XDMF using meshio
            mesh = meshio.gmsh.read(filename)
            meshio.write(filename.replace('.msh', '.xdmf'), mesh)
    
    def create_adaptive_mesh(self, error_field: np.ndarray = None, 
                           refinement_factor: float = 2.0) -> Dict[str, Any]:
        """
        Create adaptively refined mesh based on error indicators.
        
        Args:
            error_field: Error indicators for mesh refinement
            refinement_factor: Factor by which to refine high-error elements
            
        Returns:
            Dictionary with refined mesh information
        """
        if error_field is not None:
            # Mark elements for refinement based on error
            threshold = np.percentile(error_field, 75)  # Refine top 25%
            
            # This would require implementing adaptive mesh refinement
            # For now, return standard mesh
            pass
        
        return self.create_single_cell_geometry()
    
    def finalize(self):
        """Clean up gmsh resources."""
        if self.gmsh_initialized:
            gmsh.finalize()
            self.gmsh_initialized = False


class SOFCMeshGenerator:
    """
    High-level interface for generating SOFC meshes with different configurations.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize mesh generator with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def generate_mesh_for_parameters(self, parameters: Dict[str, float], 
                                   output_dir: str, sample_id: int) -> str:
        """
        Generate mesh for given parameters.
        
        Args:
            parameters: Parameter dictionary
            output_dir: Output directory
            sample_id: Sample identifier
            
        Returns:
            Path to generated mesh file
        """
        # Create geometry
        geometry = SOFCGeometry(parameters)
        
        # Determine mesh size based on configuration
        mesh_density = self.config['simulation']['mesh_density']
        base_sizes = {'coarse': 0.005, 'medium': 0.002, 'fine': 0.001}
        mesh_size = base_sizes.get(mesh_density, 0.002)
        
        # Generate geometry and mesh
        geom_info = geometry.create_single_cell_geometry(mesh_size)
        
        # Save mesh
        mesh_filename = os.path.join(output_dir, f'mesh_sample_{sample_id:06d}.msh')
        geometry.save_mesh(mesh_filename)
        
        # Save geometry info
        info_filename = mesh_filename.replace('.msh', '_info.yaml')
        with open(info_filename, 'w') as f:
            yaml.dump(geom_info, f, default_flow_style=False)
        
        geometry.finalize()
        
        return mesh_filename
    
    def generate_batch_meshes(self, parameter_samples: List[Dict[str, float]], 
                            output_dir: str) -> List[str]:
        """
        Generate meshes for a batch of parameter samples.
        
        Args:
            parameter_samples: List of parameter dictionaries
            output_dir: Output directory
            
        Returns:
            List of mesh file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        mesh_files = []
        
        for i, params in enumerate(parameter_samples):
            try:
                mesh_file = self.generate_mesh_for_parameters(params, output_dir, i)
                mesh_files.append(mesh_file)
                print(f"Generated mesh {i+1}/{len(parameter_samples)}: {mesh_file}")
            except Exception as e:
                print(f"Error generating mesh for sample {i}: {e}")
                mesh_files.append(None)
        
        return mesh_files


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('..')
    from sampling.parameter_sampler import SOFCParameterSampler
    
    # Load configuration
    config_path = "../../config/simulation_config.yaml"
    
    # Generate sample parameters
    sampler = SOFCParameterSampler(config_path)
    samples_df = sampler.generate_samples(5, seed=42)
    
    # Convert to list of dictionaries
    parameter_samples = samples_df.to_dict('records')
    
    # Generate meshes
    mesh_generator = SOFCMeshGenerator(config_path)
    output_dir = "../../data/meshes"
    
    mesh_files = mesh_generator.generate_batch_meshes(parameter_samples, output_dir)
    
    print(f"\nGenerated {len([f for f in mesh_files if f is not None])} meshes")
    print("Mesh files:", mesh_files)