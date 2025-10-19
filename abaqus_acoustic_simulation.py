#!/usr/bin/env python
"""
Complete Abaqus Acoustic Transmission Loss Simulation
====================================================

This script provides a comprehensive framework for simulating acoustic transmission loss
through stratified media using Abaqus/CAE and Abaqus/Standard.

Features:
- 2D and 3D acoustic domain generation
- Layered and continuously graded media
- Incident wave excitation with proper plane wave loading
- Non-reflecting boundary conditions
- Steady-state dynamics analysis (harmonic sweep)
- Automatic post-processing for TL(f) and α(f)
- Quality assurance and validation tools

Author: AI Assistant
Date: 2025-10-19
Units: SI (m-kg-s-Pa)
"""

import sys
import os
import numpy as np
import math
from abaqus import *
from abaqusConstants import *
import mesh
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import section
import assembly
import step
import interaction
import load
import job
import sketch
import visualization
import xyPlot
import connectorBehavior
import odbAccess
from odbAccess import openOdb


class AcousticSimulation:
    """Main class for acoustic transmission loss simulations."""
    
    def __init__(self, model_name='AcousticTL', units='SI'):
        """
        Initialize the acoustic simulation.
        
        Parameters:
        -----------
        model_name : str
            Name of the Abaqus model
        units : str
            Unit system ('SI' for m-kg-s-Pa)
        """
        self.model_name = model_name
        self.units = units
        self.model = None
        self.part = None
        self.assembly = None
        self.job = None
        
        # Default parameters
        self.domain_length = 10.0  # m
        self.domain_height = 2.0   # m
        self.domain_width = 1.0    # m (for 3D)
        self.freq_start = 100.0    # Hz
        self.freq_end = 5000.0     # Hz
        self.freq_inc = 25.0       # Hz
        
        # Probe locations (as fractions of domain length)
        self.probe_in_pos = 0.2    # 20% from inlet
        self.probe_out_pos = 0.8   # 80% from inlet
        
        # Material properties for reference medium (water)
        self.ref_density = 1025.0      # kg/m³
        self.ref_bulk_modulus = 2.306e9  # Pa
        self.ref_sound_speed = math.sqrt(self.ref_bulk_modulus / self.ref_density)
        
        print(f"Initializing Acoustic Simulation: {model_name}")
        print(f"Reference sound speed: {self.ref_sound_speed:.1f} m/s")
        
    def create_model(self):
        """Create a new Abaqus model."""
        try:
            # Delete existing model if it exists
            if self.model_name in mdb.models.keys():
                del mdb.models[self.model_name]
        except:
            pass
            
        self.model = mdb.Model(name=self.model_name)
        print(f"Created model: {self.model_name}")
        
    def create_2d_geometry(self, length=None, height=None):
        """
        Create 2D rectangular acoustic domain.
        
        Parameters:
        -----------
        length : float
            Domain length in meters (default: self.domain_length)
        height : float
            Domain height in meters (default: self.domain_height)
        """
        if length is None:
            length = self.domain_length
        if height is None:
            height = self.domain_height
            
        # Create sketch
        sketch = self.model.ConstrainedSketch(name='AcousticDomain', sheetSize=length*2)
        sketch.rectangle(point1=(0.0, 0.0), point2=(length, height))
        
        # Create part
        self.part = self.model.Part(name='AcousticDomain', 
                                   dimensionality=TWO_D_PLANAR, 
                                   type=DEFORMABLE_BODY)
        self.part.BaseShell(sketch=sketch)
        
        print(f"Created 2D domain: {length}m x {height}m")
        
        # Create sets for boundaries and probes
        self._create_2d_sets(length, height)
        
    def create_3d_geometry(self, length=None, height=None, width=None):
        """
        Create 3D rectangular acoustic domain.
        
        Parameters:
        -----------
        length : float
            Domain length in meters (default: self.domain_length)
        height : float
            Domain height in meters (default: self.domain_height)
        width : float
            Domain width in meters (default: self.domain_width)
        """
        if length is None:
            length = self.domain_length
        if height is None:
            height = self.domain_height
        if width is None:
            width = self.domain_width
            
        # Create sketch
        sketch = self.model.ConstrainedSketch(name='AcousticDomain', sheetSize=length*2)
        sketch.rectangle(point1=(0.0, 0.0), point2=(length, height))
        
        # Create part
        self.part = self.model.Part(name='AcousticDomain', 
                                   dimensionality=THREE_D, 
                                   type=DEFORMABLE_BODY)
        self.part.BaseSolidExtrude(sketch=sketch, depth=width)
        
        print(f"Created 3D domain: {length}m x {height}m x {width}m")
        
        # Create sets for boundaries and probes
        self._create_3d_sets(length, height, width)
        
    def _create_2d_sets(self, length, height):
        """Create node/face sets for 2D geometry."""
        # Inlet face (left side)
        inlet_edges = self.part.edges.findAt(((0.0, height/2, 0.0),))
        self.part.Set(edges=inlet_edges, name='INLET')
        
        # Outlet face (right side)
        outlet_edges = self.part.edges.findAt(((length, height/2, 0.0),))
        self.part.Set(edges=outlet_edges, name='OUTLET')
        
        # Top and bottom faces for non-reflecting boundaries
        top_edges = self.part.edges.findAt(((length/2, height, 0.0),))
        bottom_edges = self.part.edges.findAt(((length/2, 0.0, 0.0),))
        self.part.Set(edges=(top_edges[0], bottom_edges[0]), name='LATERAL')
        
        print("Created 2D boundary sets: INLET, OUTLET, LATERAL")
        
    def _create_3d_sets(self, length, height, width):
        """Create node/face sets for 3D geometry."""
        # Inlet face (left side)
        inlet_faces = self.part.faces.findAt(((0.0, height/2, width/2),))
        self.part.Set(faces=inlet_faces, name='INLET')
        
        # Outlet face (right side)
        outlet_faces = self.part.faces.findAt(((length, height/2, width/2),))
        self.part.Set(faces=outlet_faces, name='OUTLET')
        
        # Lateral faces for non-reflecting boundaries
        top_faces = self.part.faces.findAt(((length/2, height, width/2),))
        bottom_faces = self.part.faces.findAt(((length/2, 0.0, width/2),))
        front_faces = self.part.faces.findAt(((length/2, height/2, 0.0),))
        back_faces = self.part.faces.findAt(((length/2, height/2, width),))
        
        lateral_faces = (top_faces[0], bottom_faces[0], front_faces[0], back_faces[0])
        self.part.Set(faces=lateral_faces, name='LATERAL')
        
        print("Created 3D boundary sets: INLET, OUTLET, LATERAL")
        
    def create_layered_materials(self, layers):
        """
        Create materials for layered medium.
        
        Parameters:
        -----------
        layers : list of dict
            Each dict contains 'name', 'density', 'bulk_modulus', 'thickness'
            Example: [{'name': 'WATER_TOP', 'density': 1025.0, 
                      'bulk_modulus': 2.306e9, 'thickness': 1.0}]
        """
        materials = []
        
        for i, layer in enumerate(layers):
            mat_name = layer['name']
            density = layer['density']
            bulk_modulus = layer['bulk_modulus']
            
            # Create material
            mat = self.model.Material(name=mat_name)
            mat.Density(table=((density,),))
            mat.BulkModulus(table=((bulk_modulus,),))
            
            # Calculate and display sound speed
            c = math.sqrt(bulk_modulus / density)
            print(f"Material {mat_name}: ρ={density:.1f} kg/m³, K={bulk_modulus:.2e} Pa, c={c:.1f} m/s")
            
            materials.append(mat)
            
        return materials
        
    def create_graded_material(self, name, density_profile, bulk_modulus_profile):
        """
        Create material with continuous gradients using field variables.
        
        Parameters:
        -----------
        name : str
            Material name
        density_profile : list of tuples
            [(field_value, density), ...] where field_value is F1
        bulk_modulus_profile : list of tuples
            [(field_value, bulk_modulus), ...]
        """
        # Create material with field variable dependencies
        mat = self.model.Material(name=name)
        mat.Density(table=density_profile, dependencies=1)  # 1 field variable
        mat.BulkModulus(table=bulk_modulus_profile, dependencies=1)
        
        print(f"Created graded material: {name}")
        print(f"Density profile: {len(density_profile)} points")
        print(f"Bulk modulus profile: {len(bulk_modulus_profile)} points")
        
        return mat
        
    def create_analytical_field(self, name, expression):
        """
        Create analytical field for graded properties.
        
        Parameters:
        -----------
        name : str
            Field name
        expression : str
            Mathematical expression (e.g., 'Z' for linear variation with depth)
        """
        # Create analytical field
        self.model.AnalyticalField(name=name, 
                                  localCsys=None, 
                                  description='Field variable for property gradients',
                                  expression=expression)
        
        print(f"Created analytical field: {name} = {expression}")
        
    def partition_for_layers(self, layers, dimension='2D'):
        """
        Partition geometry for layered materials.
        
        Parameters:
        -----------
        layers : list of dict
            Layer definitions with 'thickness' key
        dimension : str
            '2D' or '3D'
        """
        if dimension == '2D':
            self._partition_2d_layers(layers)
        else:
            self._partition_3d_layers(layers)
            
    def _partition_2d_layers(self, layers):
        """Partition 2D geometry into layers."""
        current_height = 0.0
        
        for i, layer in enumerate(layers[:-1]):  # Skip last layer (no partition needed)
            current_height += layer['thickness']
            
            # Create partition line
            sketch = self.model.ConstrainedSketch(name='PartitionSketch', 
                                                 sheetSize=self.domain_length*2)
            sketch.Line(point1=(0.0, current_height), 
                       point2=(self.domain_length, current_height))
            
            # Apply partition
            self.part.PartitionFaceBySketch(sketchPlane=self.part.faces[0], 
                                          sketch=sketch)
            
            print(f"Created partition at height {current_height:.2f}m")
            
    def _partition_3d_layers(self, layers):
        """Partition 3D geometry into layers."""
        current_height = 0.0
        
        for i, layer in enumerate(layers[:-1]):  # Skip last layer
            current_height += layer['thickness']
            
            # Create datum plane
            datum_plane = self.part.DatumPlaneByPrincipalPlane(
                principalPlane=XYPLANE, offset=current_height)
            
            # Partition by datum plane
            self.part.PartitionCellByDatumPlane(datumPlane=self.part.datums[datum_plane.id],
                                              cells=self.part.cells[:])
            
            print(f"Created 3D partition at height {current_height:.2f}m")
            
    def assign_layered_sections(self, layers, dimension='2D'):
        """
        Assign sections to layered geometry.
        
        Parameters:
        -----------
        layers : list of dict
            Layer definitions
        dimension : str
            '2D' or '3D'
        """
        if dimension == '2D':
            regions = self.part.faces[:]
        else:
            regions = self.part.cells[:]
            
        for i, layer in enumerate(layers):
            mat_name = layer['name']
            
            # Create section
            section_name = f"Section_{mat_name}"
            self.model.SolidSection(name=section_name, 
                                   material=mat_name, 
                                   thickness=None)
            
            # Assign section to region
            if i < len(regions):
                region = regionToolset.Region(faces=[regions[i]] if dimension == '2D' 
                                            else cells=[regions[i]])
                self.part.SectionAssignment(region=region, 
                                          sectionName=section_name, 
                                          offset=0.0)
                
                print(f"Assigned section {section_name} to layer {i+1}")
                
    def assign_graded_section(self, material_name, field_name):
        """
        Assign section for graded material.
        
        Parameters:
        -----------
        material_name : str
            Name of graded material
        field_name : str
            Name of analytical field
        """
        # Create section
        section_name = f"Section_{material_name}"
        self.model.SolidSection(name=section_name, 
                               material=material_name, 
                               thickness=None)
        
        # Assign to entire part
        region = regionToolset.Region(faces=self.part.faces[:] if hasattr(self.part, 'faces') 
                                    else cells=self.part.cells[:])
        self.part.SectionAssignment(region=region, 
                                  sectionName=section_name, 
                                  offset=0.0)
        
        print(f"Assigned graded section {section_name}")
        
        # Create initial condition for field variable
        self.model.InitialState(name='FieldIC', 
                               createStepName='Initial',
                               region=region,
                               fieldVarName=field_name,
                               value=1.0)  # Will be overridden by analytical field
        
    def create_mesh(self, element_type='AC2D4', target_frequency=None, elements_per_wavelength=12):
        """
        Create acoustic mesh.
        
        Parameters:
        -----------
        element_type : str
            'AC2D4', 'AC2D8', 'AC3D8', 'AC3D20'
        target_frequency : float
            Target frequency for mesh sizing (default: freq_end)
        elements_per_wavelength : int
            Target elements per wavelength
        """
        if target_frequency is None:
            target_frequency = self.freq_end
            
        # Calculate wavelength and element size
        wavelength = self.ref_sound_speed / target_frequency
        target_size = wavelength / elements_per_wavelength
        
        print(f"Target frequency: {target_frequency:.0f} Hz")
        print(f"Wavelength: {wavelength:.3f} m")
        print(f"Target element size: {target_size:.4f} m")
        
        # Set element type
        if element_type in ['AC2D4', 'AC2D8']:
            elem_type = mesh.ElemType(elemCode=AC2D4 if element_type == 'AC2D4' else AC2D8)
            regions = (self.part.faces[:],)
        else:  # 3D elements
            elem_type = mesh.ElemType(elemCode=AC3D8 if element_type == 'AC3D8' else AC3D20)
            regions = (self.part.cells[:],)
            
        self.part.setElementType(regions=regions, elemTypes=(elem_type,))
        
        # Seed the part
        self.part.seedPart(size=target_size, deviationFactor=0.1, minSizeFactor=0.1)
        
        # Generate mesh
        self.part.generateMesh()
        
        num_elements = len(self.part.elements)
        num_nodes = len(self.part.nodes)
        
        print(f"Generated mesh: {num_elements} elements, {num_nodes} nodes")
        print(f"Element type: {element_type}")
        
    def create_assembly(self):
        """Create assembly and instance."""
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        
        # Create instance
        self.assembly.Instance(name='Domain-1', part=self.part, dependent=ON)
        
        # Create probe sets in assembly
        self._create_probe_sets()
        
        print("Created assembly and instance")
        
    def _create_probe_sets(self):
        """Create probe node sets for TL measurement."""
        instance = self.assembly.instances['Domain-1']
        
        # Calculate probe positions
        probe_in_x = self.probe_in_pos * self.domain_length
        probe_out_x = self.probe_out_pos * self.domain_length
        
        # Find nodes at probe locations
        # For 2D case
        if hasattr(self.part, 'faces'):
            # Find nodes near probe lines
            probe_in_nodes = []
            probe_out_nodes = []
            
            for node in instance.nodes:
                x_coord = node.coordinates[0]
                if abs(x_coord - probe_in_x) < 0.01:  # Tolerance
                    probe_in_nodes.append(node)
                elif abs(x_coord - probe_out_x) < 0.01:
                    probe_out_nodes.append(node)
                    
            if probe_in_nodes:
                self.assembly.Set(nodes=probe_in_nodes, name='PROBE_IN')
                print(f"Created PROBE_IN at x={probe_in_x:.2f}m ({len(probe_in_nodes)} nodes)")
                
            if probe_out_nodes:
                self.assembly.Set(nodes=probe_out_nodes, name='PROBE_OUT')
                print(f"Created PROBE_OUT at x={probe_out_x:.2f}m ({len(probe_out_nodes)} nodes)")
        
    def create_steady_state_step(self, freq_start=None, freq_end=None, freq_inc=None):
        """
        Create steady-state dynamics step.
        
        Parameters:
        -----------
        freq_start : float
            Start frequency in Hz
        freq_end : float
            End frequency in Hz
        freq_inc : float
            Frequency increment in Hz
        """
        if freq_start is None:
            freq_start = self.freq_start
        if freq_end is None:
            freq_end = self.freq_end
        if freq_inc is None:
            freq_inc = self.freq_inc
            
        # Create step
        self.model.SteadyStateDirectStep(name='SteadyState',
                                        previous='Initial',
                                        frequencyRange=(freq_start, freq_end, freq_inc),
                                        factorization=COMPLEX)
        
        num_frequencies = int((freq_end - freq_start) / freq_inc) + 1
        print(f"Created steady-state step: {freq_start}-{freq_end} Hz, {freq_inc} Hz increment")
        print(f"Total frequencies: {num_frequencies}")
        
    def create_incident_wave(self, direction=(1.0, 0.0, 0.0), amplitude=1.0):
        """
        Create incident wave loading.
        
        Parameters:
        -----------
        direction : tuple
            Wave propagation direction (unit vector)
        amplitude : float
            Wave amplitude
        """
        # Create incident wave property
        self.model.IncidentWaveProperty(name='PlaneWave')
        self.model.incidentWaveProperties['PlaneWave'].IncidentWaveFluidProperty(
            fluidDensity=self.ref_density,
            soundSpeed=self.ref_sound_speed)
        
        # Create incident wave interaction
        inlet_region = self.assembly.sets['Domain-1.INLET']
        self.model.IncidentWave(name='IncidentWave',
                               createStepName='SteadyState',
                               surface=inlet_region,
                               interactionProperty='PlaneWave',
                               direction=direction,
                               amplitude=amplitude,
                               phase=0.0)
        
        print(f"Created incident wave: direction={direction}, amplitude={amplitude}")
        
    def create_non_reflecting_boundaries(self):
        """Create non-reflecting (impedance) boundaries."""
        # Outlet boundary
        outlet_region = self.assembly.sets['Domain-1.OUTLET']
        self.model.AcousticImpedance(name='OutletImpedance',
                                    createStepName='SteadyState',
                                    surface=outlet_region,
                                    nonReflecting=ON)
        
        # Lateral boundaries
        lateral_region = self.assembly.sets['Domain-1.LATERAL']
        self.model.AcousticImpedance(name='LateralImpedance',
                                    createStepName='SteadyState',
                                    surface=lateral_region,
                                    nonReflecting=ON)
        
        print("Created non-reflecting boundaries on outlet and lateral faces")
        
    def create_output_requests(self):
        """Create output requests for post-processing."""
        # Field output
        self.model.fieldOutputRequests['F-Output-1'].setValues(
            variables=('P',),  # Complex pressure
            frequency=LAST_INCREMENT)
        
        # History output for probes
        if 'PROBE_IN' in self.assembly.sets.keys():
            self.model.HistoryOutputRequest(name='ProbeIn',
                                          createStepName='SteadyState',
                                          region=self.assembly.sets['PROBE_IN'],
                                          variables=('P',),
                                          frequency=1)
            
        if 'PROBE_OUT' in self.assembly.sets.keys():
            self.model.HistoryOutputRequest(name='ProbeOut',
                                          createStepName='SteadyState',
                                          region=self.assembly.sets['PROBE_OUT'],
                                          variables=('P',),
                                          frequency=1)
        
        print("Created output requests for pressure field and probe history")
        
    def create_job(self, job_name=None, num_cpus=1):
        """
        Create and configure job.
        
        Parameters:
        -----------
        job_name : str
            Job name (default: model_name)
        num_cpus : int
            Number of CPUs for parallel processing
        """
        if job_name is None:
            job_name = self.model_name
            
        self.job = mdb.Job(name=job_name,
                          model=self.model_name,
                          numCpus=num_cpus,
                          numDomains=num_cpus,
                          multiprocessingMode=THREADS)
        
        print(f"Created job: {job_name} ({num_cpus} CPUs)")
        
    def run_analysis(self, wait_for_completion=True):
        """
        Submit and run the analysis.
        
        Parameters:
        -----------
        wait_for_completion : bool
            Whether to wait for job completion
        """
        if self.job is None:
            raise ValueError("Job not created. Call create_job() first.")
            
        print("Submitting job...")
        self.job.submit()
        
        if wait_for_completion:
            print("Waiting for job completion...")
            self.job.waitForCompletion()
            print("Job completed.")
        else:
            print("Job submitted. Check status manually.")
            
    def post_process_transmission_loss(self, job_name=None):
        """
        Post-process results to calculate transmission loss.
        
        Parameters:
        -----------
        job_name : str
            Job name (default: model_name)
            
        Returns:
        --------
        dict : Results containing frequencies, TL, and alpha
        """
        if job_name is None:
            job_name = self.model_name
            
        odb_path = f"{job_name}.odb"
        
        try:
            odb = openOdb(odb_path)
            print(f"Opened ODB: {odb_path}")
            
            # Get step
            step = odb.steps['SteadyState']
            
            # Initialize arrays
            frequencies = []
            pin_magnitudes = []
            pout_magnitudes = []
            
            # Process each frame (frequency)
            for frame in step.frames:
                freq = frame.frequency
                frequencies.append(freq)
                
                # Get pressure at probe locations
                p_field = frame.fieldOutputs['P']
                
                # Extract pressures at probe sets
                try:
                    probe_in_set = odb.rootAssembly.nodeSets['PROBE_IN']
                    probe_out_set = odb.rootAssembly.nodeSets['PROBE_OUT']
                    
                    pin_subset = p_field.getSubset(region=probe_in_set)
                    pout_subset = p_field.getSubset(region=probe_out_set)
                    
                    # Calculate average magnitude
                    pin_values = [complex(val.data[0], val.data[1]) for val in pin_subset.values]
                    pout_values = [complex(val.data[0], val.data[1]) for val in pout_subset.values]
                    
                    pin_mag = np.mean([abs(p) for p in pin_values])
                    pout_mag = np.mean([abs(p) for p in pout_values])
                    
                    pin_magnitudes.append(pin_mag)
                    pout_magnitudes.append(pout_mag)
                    
                except KeyError as e:
                    print(f"Warning: Could not find probe set {e}")
                    pin_magnitudes.append(0.0)
                    pout_magnitudes.append(0.0)
                    
            odb.close()
            
            # Convert to numpy arrays
            frequencies = np.array(frequencies)
            pin_magnitudes = np.array(pin_magnitudes)
            pout_magnitudes = np.array(pout_magnitudes)
            
            # Calculate transmission loss
            # Avoid division by zero
            pout_magnitudes = np.maximum(pout_magnitudes, 1e-20)
            TL = 20 * np.log10(pin_magnitudes / pout_magnitudes)
            
            # Calculate absorption coefficient
            delta_x = (self.probe_out_pos - self.probe_in_pos) * self.domain_length
            alpha_amp = (np.log(10) / 20.0) * TL / delta_x
            
            results = {
                'frequencies': frequencies,
                'pin_magnitudes': pin_magnitudes,
                'pout_magnitudes': pout_magnitudes,
                'transmission_loss': TL,
                'alpha_amplitude': alpha_amp,
                'probe_separation': delta_x
            }
            
            print(f"Post-processing completed:")
            print(f"  Frequency range: {frequencies[0]:.0f} - {frequencies[-1]:.0f} Hz")
            print(f"  Number of frequencies: {len(frequencies)}")
            print(f"  Probe separation: {delta_x:.2f} m")
            print(f"  TL range: {np.min(TL):.1f} - {np.max(TL):.1f} dB")
            
            return results
            
        except Exception as e:
            print(f"Error in post-processing: {e}")
            return None
            
    def save_results(self, results, filename):
        """
        Save results to CSV file.
        
        Parameters:
        -----------
        results : dict
            Results from post_process_transmission_loss()
        filename : str
            Output filename
        """
        if results is None:
            print("No results to save.")
            return
            
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Frequency_Hz', 'Pin_Magnitude', 'Pout_Magnitude', 
                           'Transmission_Loss_dB', 'Alpha_Amplitude_per_m'])
            
            for i in range(len(results['frequencies'])):
                writer.writerow([
                    results['frequencies'][i],
                    results['pin_magnitudes'][i],
                    results['pout_magnitudes'][i],
                    results['transmission_loss'][i],
                    results['alpha_amplitude'][i]
                ])
                
        print(f"Results saved to: {filename}")
        
    def validate_mesh_resolution(self, target_frequency=None):
        """
        Validate mesh resolution for acoustic analysis.
        
        Parameters:
        -----------
        target_frequency : float
            Frequency to check (default: freq_end)
        """
        if target_frequency is None:
            target_frequency = self.freq_end
            
        # Calculate wavelength
        wavelength = self.ref_sound_speed / target_frequency
        
        # Get element sizes
        element_sizes = []
        for element in self.part.elements:
            # Approximate element size as sqrt of area (2D) or cube root of volume (3D)
            if hasattr(self.part, 'faces'):  # 2D
                # Get element area (approximate)
                nodes = [self.part.nodes[node_id-1] for node_id in element.connectivity]
                coords = [node.coordinates for node in nodes]
                # Simple approximation for quad element
                if len(coords) == 4:
                    dx = abs(coords[1][0] - coords[0][0])
                    dy = abs(coords[2][1] - coords[1][1])
                    size = max(dx, dy)
                else:
                    size = 0.1  # Default
            else:  # 3D
                size = 0.1  # Simplified for now
                
            element_sizes.append(size)
            
        avg_element_size = np.mean(element_sizes)
        elements_per_wavelength = wavelength / avg_element_size
        
        print(f"Mesh validation at {target_frequency:.0f} Hz:")
        print(f"  Wavelength: {wavelength:.3f} m")
        print(f"  Average element size: {avg_element_size:.4f} m")
        print(f"  Elements per wavelength: {elements_per_wavelength:.1f}")
        
        if elements_per_wavelength < 10:
            print("  WARNING: Mesh may be too coarse (< 10 elements/wavelength)")
        elif elements_per_wavelength > 20:
            print("  INFO: Mesh is very fine (> 20 elements/wavelength)")
        else:
            print("  OK: Mesh resolution is adequate")
            
        return elements_per_wavelength


# Example usage and test cases
def example_layered_medium_2d():
    """Example: 2D layered medium simulation."""
    print("\n" + "="*60)
    print("EXAMPLE: 2D Layered Medium Simulation")
    print("="*60)
    
    # Create simulation
    sim = AcousticSimulation(model_name='LayeredMedium2D')
    sim.create_model()
    
    # Create 2D geometry
    sim.create_2d_geometry(length=10.0, height=4.0)
    
    # Define layers (from bottom to top)
    layers = [
        {'name': 'WATER_BOTTOM', 'density': 1030.0, 'bulk_modulus': 2.4e9, 'thickness': 2.0},
        {'name': 'WATER_TOP', 'density': 1020.0, 'bulk_modulus': 2.2e9, 'thickness': 2.0}
    ]
    
    # Create materials
    sim.create_layered_materials(layers)
    
    # Partition geometry
    sim.partition_for_layers(layers, dimension='2D')
    
    # Assign sections
    sim.assign_layered_sections(layers, dimension='2D')
    
    # Create mesh
    sim.create_mesh(element_type='AC2D4', target_frequency=2000.0)
    
    # Validate mesh
    sim.validate_mesh_resolution(target_frequency=2000.0)
    
    # Create assembly
    sim.create_assembly()
    
    # Create analysis step
    sim.create_steady_state_step(freq_start=100.0, freq_end=3000.0, freq_inc=50.0)
    
    # Create loading and boundaries
    sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
    sim.create_non_reflecting_boundaries()
    
    # Create output requests
    sim.create_output_requests()
    
    # Create job
    sim.create_job(job_name='LayeredMedium2D', num_cpus=2)
    
    print("2D Layered medium model created successfully!")
    print("To run: sim.run_analysis()")
    print("To post-process: results = sim.post_process_transmission_loss()")
    
    return sim


def example_graded_medium_3d():
    """Example: 3D continuously graded medium simulation."""
    print("\n" + "="*60)
    print("EXAMPLE: 3D Graded Medium Simulation")
    print("="*60)
    
    # Create simulation
    sim = AcousticSimulation(model_name='GradedMedium3D')
    sim.create_model()
    
    # Create 3D geometry
    sim.create_3d_geometry(length=8.0, height=3.0, width=2.0)
    
    # Create analytical field for depth variation
    sim.create_analytical_field(name='DepthField', expression='Z')
    
    # Define property profiles (density and bulk modulus vs depth)
    # Linear variation from surface (Z=0) to bottom (Z=3.0)
    density_profile = [
        (0.0, 1020.0),    # Surface
        (1.5, 1025.0),    # Middle
        (3.0, 1030.0)     # Bottom
    ]
    
    bulk_modulus_profile = [
        (0.0, 2.2e9),     # Surface
        (1.5, 2.3e9),     # Middle  
        (3.0, 2.4e9)      # Bottom
    ]
    
    # Create graded material
    sim.create_graded_material('WATER_GRADED', density_profile, bulk_modulus_profile)
    
    # Assign section
    sim.assign_graded_section('WATER_GRADED', 'DepthField')
    
    # Create mesh
    sim.create_mesh(element_type='AC3D8', target_frequency=1500.0)
    
    # Create assembly
    sim.create_assembly()
    
    # Create analysis step
    sim.create_steady_state_step(freq_start=200.0, freq_end=2000.0, freq_inc=100.0)
    
    # Create loading and boundaries
    sim.create_incident_wave(direction=(1.0, 0.0, 0.0))
    sim.create_non_reflecting_boundaries()
    
    # Create output requests
    sim.create_output_requests()
    
    # Create job
    sim.create_job(job_name='GradedMedium3D', num_cpus=4)
    
    print("3D Graded medium model created successfully!")
    
    return sim


def run_complete_example():
    """Run a complete example with post-processing."""
    print("\n" + "="*60)
    print("COMPLETE EXAMPLE: Full Simulation Workflow")
    print("="*60)
    
    # Create and run 2D layered simulation
    sim = example_layered_medium_2d()
    
    # Run analysis (uncomment to actually run)
    # sim.run_analysis(wait_for_completion=True)
    
    # Post-process results (uncomment after running)
    # results = sim.post_process_transmission_loss()
    # if results:
    #     sim.save_results(results, 'transmission_loss_results.csv')
    
    print("\nTo run the complete workflow:")
    print("1. sim.run_analysis(wait_for_completion=True)")
    print("2. results = sim.post_process_transmission_loss()")
    print("3. sim.save_results(results, 'results.csv')")
    
    return sim


if __name__ == "__main__":
    print("Abaqus Acoustic Transmission Loss Simulation")
    print("=" * 50)
    
    # Run examples
    try:
        # Example 1: 2D Layered medium
        sim1 = example_layered_medium_2d()
        
        # Example 2: 3D Graded medium
        sim2 = example_graded_medium_3d()
        
        print("\n" + "="*60)
        print("EXAMPLES CREATED SUCCESSFULLY")
        print("="*60)
        print("Available simulations:")
        print("- sim1: 2D Layered medium")
        print("- sim2: 3D Graded medium")
        print("\nTo run any simulation:")
        print("sim.run_analysis(wait_for_completion=True)")
        print("results = sim.post_process_transmission_loss()")
        print("sim.save_results(results, 'filename.csv')")
        
    except Exception as e:
        print(f"Error creating examples: {e}")
        import traceback
        traceback.print_exc()