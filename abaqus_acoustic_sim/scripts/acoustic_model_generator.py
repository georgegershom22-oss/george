#!/usr/bin/env python3
"""
Abaqus Acoustic Simulation Model Generator
==========================================
Generates Abaqus models for acoustic transmission loss analysis in stratified media.
Supports both layered and continuously graded density/bulk modulus profiles.

Author: Acoustic Simulation Framework
Date: 2025-10-19
Version: 1.0.0
"""

import numpy as np
import sys
import os
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset
import mesh
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
import displayGroupOdbToolset as dgo


class AcousticStratifiedModel:
    """
    Main class for generating stratified acoustic models in Abaqus.
    """
    
    def __init__(self, model_name='AcousticStratified'):
        """
        Initialize the acoustic model.
        
        Parameters:
        -----------
        model_name : str
            Name of the Abaqus model
        """
        self.model_name = model_name
        self.model = mdb.Model(name=model_name)
        if 'Model-1' in mdb.models.keys():
            del mdb.models['Model-1']
        
        # Default parameters (SI units: m-kg-s-Pa)
        self.geometry = {
            'length': 10.0,      # Domain length (m)
            'width': 2.0,        # Domain width (m)
            'height': 2.0        # Domain height (m) - for 3D models
        }
        
        self.mesh_params = {
            'elem_per_wavelength': 12,  # Elements per wavelength
            'max_elem_size': 0.05,      # Maximum element size (m)
            'min_elem_size': 0.01       # Minimum element size (m)
        }
        
        self.frequency_params = {
            'f_min': 100.0,      # Minimum frequency (Hz)
            'f_max': 5000.0,     # Maximum frequency (Hz)
            'f_step': 25.0       # Frequency step (Hz)
        }
        
        # Water properties at standard conditions
        self.base_properties = {
            'rho': 1000.0,       # Density (kg/m³)
            'bulk_modulus': 2.2e9  # Bulk modulus (Pa)
        }
        
    def create_2d_geometry(self, use_partition=False, n_layers=1):
        """
        Create 2D rectangular waveguide geometry.
        
        Parameters:
        -----------
        use_partition : bool
            If True, partition geometry for layered media
        n_layers : int
            Number of layers for partitioning
        """
        # Create 2D part
        s = self.model.ConstrainedSketch(name='__profile__', sheetSize=20.0)
        s.rectangle(point1=(0.0, 0.0), 
                   point2=(self.geometry['length'], self.geometry['width']))
        
        part_2d = self.model.Part(name='AcousticDomain2D', 
                                  dimensionality=TWO_D_PLANAR, 
                                  type=DEFORMABLE_BODY)
        part_2d.BaseShell(sketch=s)
        
        # Partition for layers if requested
        if use_partition and n_layers > 1:
            layer_height = self.geometry['width'] / n_layers
            for i in range(1, n_layers):
                y_pos = i * layer_height
                # Create partition line
                p = part_2d
                f, e, d = p.faces, p.edges, p.datums
                t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1,
                                         origin=(0.0, 0.0, 0.0))
                s = self.model.ConstrainedSketch(name='__partition__', 
                                                sheetSize=20.0, transform=t)
                s.Line(point1=(0.0, y_pos), 
                      point2=(self.geometry['length'], y_pos))
                p.PartitionFaceBySketch(faces=f, sketch=s)
        
        return part_2d
    
    def create_3d_geometry(self, use_partition=False, n_layers=1):
        """
        Create 3D rectangular waveguide geometry.
        
        Parameters:
        -----------
        use_partition : bool
            If True, partition geometry for layered media
        n_layers : int
            Number of layers for partitioning
        """
        # Create 3D part
        s = self.model.ConstrainedSketch(name='__profile__', sheetSize=20.0)
        s.rectangle(point1=(0.0, 0.0), 
                   point2=(self.geometry['length'], self.geometry['width']))
        
        part_3d = self.model.Part(name='AcousticDomain3D', 
                                  dimensionality=THREE_D, 
                                  type=DEFORMABLE_BODY)
        part_3d.BaseSolidExtrude(sketch=s, depth=self.geometry['height'])
        
        # Partition for layers if requested
        if use_partition and n_layers > 1:
            layer_height = self.geometry['height'] / n_layers
            for i in range(1, n_layers):
                z_pos = i * layer_height
                # Create partition plane
                p = part_3d
                c = p.cells
                datum_plane = p.DatumPlaneByPrincipalPlane(
                    principalPlane=XYPLANE, offset=z_pos)
                p.PartitionCellByDatumPlane(datumPlane=p.datums[datum_plane.id], 
                                           cells=c)
        
        return part_3d
    
    def create_layered_materials(self, layer_properties):
        """
        Create acoustic materials for layered stratification.
        
        Parameters:
        -----------
        layer_properties : list of dict
            List containing {'rho': density, 'K': bulk_modulus} for each layer
        """
        materials = []
        
        for i, props in enumerate(layer_properties):
            mat_name = f'AcousticMedium_Layer{i+1}'
            mat = self.model.Material(name=mat_name)
            
            # Acoustic medium properties
            mat.AcousticMedium(acousticVolumetricDrag=0.0,
                              temperatureDependencyB=OFF,
                              temperatureDependencyV=OFF,
                              dependenciesB=0,
                              dependenciesV=0,
                              bulkTable=((props['K'], ), ),
                              volumetricTable=((props['rho'], ), ))
            
            materials.append(mat_name)
            
            # Create section for this material
            self.model.HomogeneousSolidSection(
                name=f'Section_Layer{i+1}',
                material=mat_name,
                thickness=None)
        
        return materials
    
    def create_gradient_material(self, gradient_type='linear'):
        """
        Create acoustic material with continuous gradient using field variables.
        
        Parameters:
        -----------
        gradient_type : str
            Type of gradient: 'linear', 'exponential', 'tanh'
        """
        mat = self.model.Material(name='AcousticMedium_Gradient')
        
        # Define field-dependent properties
        if gradient_type == 'linear':
            # Linear gradient from top to bottom
            # Field variable F1 will represent normalized z-coordinate (0 to 1)
            rho_table = []
            K_table = []
            n_points = 11  # Number of points in the table
            
            for i in range(n_points):
                f1_val = i / (n_points - 1)  # 0 to 1
                # Linear variation: 900 to 1100 kg/m³
                rho = 900.0 + 200.0 * f1_val
                # Corresponding bulk modulus variation
                K = 2.0e9 + 0.4e9 * f1_val
                
                rho_table.append((rho, f1_val))
                K_table.append((K, f1_val))
        
        elif gradient_type == 'exponential':
            # Exponential gradient
            rho_table = []
            K_table = []
            n_points = 21
            
            for i in range(n_points):
                f1_val = i / (n_points - 1)
                # Exponential variation
                rho = 900.0 * np.exp(0.2 * f1_val)
                K = 2.0e9 * np.exp(0.1 * f1_val)
                
                rho_table.append((rho, f1_val))
                K_table.append((K, f1_val))
        
        elif gradient_type == 'tanh':
            # Hyperbolic tangent profile (thermocline-like)
            rho_table = []
            K_table = []
            n_points = 31
            
            for i in range(n_points):
                f1_val = i / (n_points - 1)
                # Tanh profile centered at 0.5
                z_norm = (f1_val - 0.5) * 6  # Scale factor
                profile = 0.5 * (1 + np.tanh(z_norm))
                
                rho = 950.0 + 100.0 * profile
                K = 2.1e9 + 0.2e9 * profile
                
                rho_table.append((rho, f1_val))
                K_table.append((K, f1_val))
        
        # Apply field-dependent properties
        mat.AcousticMedium(acousticVolumetricDrag=0.0,
                          temperatureDependencyB=OFF,
                          temperatureDependencyV=OFF,
                          dependenciesB=1,  # One field variable
                          dependenciesV=1,  # One field variable
                          bulkTable=tuple(K_table),
                          volumetricTable=tuple(rho_table))
        
        # Create section
        self.model.HomogeneousSolidSection(
            name='Section_Gradient',
            material='AcousticMedium_Gradient',
            thickness=None)
        
        return 'AcousticMedium_Gradient'
    
    def setup_assembly_and_sets(self, part, is_3d=False):
        """
        Create assembly and define node/element sets for boundaries and probes.
        
        Parameters:
        -----------
        part : Abaqus Part object
            The acoustic domain part
        is_3d : bool
            Whether this is a 3D model
        """
        # Create instance
        a = self.model.rootAssembly
        a.DatumCsysByDefault(CARTESIAN)
        inst = a.Instance(name='AcousticDomain-1', part=part, dependent=ON)
        
        # Define sets for boundaries
        if is_3d:
            # 3D sets
            # Inlet face (x=0)
            faces = inst.faces.findAt(((0.0, self.geometry['width']/2, 
                                       self.geometry['height']/2), ))
            a.Set(faces=faces, name='INLET')
            
            # Outlet face (x=L)
            faces = inst.faces.findAt(((self.geometry['length'], 
                                       self.geometry['width']/2,
                                       self.geometry['height']/2), ))
            a.Set(faces=faces, name='OUTLET')
            
            # Lateral faces (y=0, y=W, z=0, z=H)
            lateral_coords = [
                (self.geometry['length']/2, 0.0, self.geometry['height']/2),
                (self.geometry['length']/2, self.geometry['width'], 
                 self.geometry['height']/2),
                (self.geometry['length']/2, self.geometry['width']/2, 0.0),
                (self.geometry['length']/2, self.geometry['width']/2, 
                 self.geometry['height'])
            ]
            lateral_faces = []
            for coord in lateral_coords:
                lateral_faces.extend(inst.faces.findAt((coord, )))
            a.Set(faces=lateral_faces, name='LATERAL')
            
            # Define probe planes
            probe_x1 = self.geometry['length'] * 0.2
            probe_x2 = self.geometry['length'] * 0.8
            
            # Create node sets for probes by selecting nodes on YZ planes
            nodes_in = inst.nodes.getByBoundingBox(xMin=probe_x1-0.001,
                                                   xMax=probe_x1+0.001)
            nodes_out = inst.nodes.getByBoundingBox(xMin=probe_x2-0.001,
                                                    xMax=probe_x2+0.001)
            a.Set(nodes=nodes_in, name='PROBE_IN')
            a.Set(nodes=nodes_out, name='PROBE_OUT')
            
        else:
            # 2D sets
            # Inlet edge (x=0)
            edges = inst.edges.findAt(((0.0, self.geometry['width']/2, 0.0), ))
            a.Set(edges=edges, name='INLET')
            
            # Outlet edge (x=L)
            edges = inst.edges.findAt(((self.geometry['length'], 
                                       self.geometry['width']/2, 0.0), ))
            a.Set(edges=edges, name='OUTLET')
            
            # Top and bottom edges
            top_edge = inst.edges.findAt(((self.geometry['length']/2, 
                                          self.geometry['width'], 0.0), ))
            bottom_edge = inst.edges.findAt(((self.geometry['length']/2, 
                                             0.0, 0.0), ))
            a.Set(edges=top_edge+bottom_edge, name='LATERAL')
            
            # Probe lines
            probe_x1 = self.geometry['length'] * 0.2
            probe_x2 = self.geometry['length'] * 0.8
            
            nodes_in = inst.nodes.getByBoundingBox(xMin=probe_x1-0.001,
                                                   xMax=probe_x1+0.001)
            nodes_out = inst.nodes.getByBoundingBox(xMin=probe_x2-0.001,
                                                    xMax=probe_x2+0.001)
            a.Set(nodes=nodes_in, name='PROBE_IN')
            a.Set(nodes=nodes_out, name='PROBE_OUT')
        
        return inst
    
    def apply_mesh(self, part, is_3d=False):
        """
        Apply acoustic mesh to the part.
        
        Parameters:
        -----------
        part : Abaqus Part object
            The part to mesh
        is_3d : bool
            Whether this is a 3D model
        """
        # Calculate element size based on minimum wavelength
        c_sound = np.sqrt(self.base_properties['bulk_modulus'] / 
                         self.base_properties['rho'])
        min_wavelength = c_sound / self.frequency_params['f_max']
        elem_size = min_wavelength / self.mesh_params['elem_per_wavelength']
        elem_size = max(min(elem_size, self.mesh_params['max_elem_size']),
                       self.mesh_params['min_elem_size'])
        
        # Set element type
        if is_3d:
            # 3D acoustic elements
            elemType1 = mesh.ElemType(elemCode=AC3D8, elemLibrary=STANDARD)
            elemType2 = mesh.ElemType(elemCode=AC3D6, elemLibrary=STANDARD)
            elemType3 = mesh.ElemType(elemCode=AC3D4, elemLibrary=STANDARD)
            
            cells = part.cells.getSequenceFromMask(mask=('[#1 ]', ), )
            part.setElementType(regions=(cells, ), elemTypes=(elemType1, 
                                                              elemType2, 
                                                              elemType3))
        else:
            # 2D acoustic elements
            elemType1 = mesh.ElemType(elemCode=AC2D4, elemLibrary=STANDARD)
            elemType2 = mesh.ElemType(elemCode=AC2D3, elemLibrary=STANDARD)
            
            faces = part.faces.getSequenceFromMask(mask=('[#1 ]', ), )
            part.setElementType(regions=(faces, ), elemTypes=(elemType1, 
                                                              elemType2))
        
        # Seed and generate mesh
        part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.1)
        part.generateMesh()
        
        return elem_size
    
    def create_ssd_step(self):
        """
        Create Steady-State Dynamics, Direct step for frequency sweep.
        """
        # Create the SSD step
        self.model.SteadyStateDynamics(
            name='FrequencySweep',
            previous='Initial',
            frequencyRange=(
                (self.frequency_params['f_min'], 
                 self.frequency_params['f_max'],
                 self.frequency_params['f_step'], 
                 LOGARITHMIC),
            ),
            description='Harmonic frequency sweep for TL analysis')
        
        # Modify field output requests
        self.model.fieldOutputRequests['F-Output-1'].setValues(
            variables=('P', 'POR'))
        
        # Create history output for probe points
        self.model.HistoryOutputRequest(
            name='ProbeIn',
            createStepName='FrequencySweep',
            variables=('P', ),
            region=self.model.rootAssembly.sets['PROBE_IN'],
            sectionPoints=DEFAULT,
            rebar=EXCLUDE)
        
        self.model.HistoryOutputRequest(
            name='ProbeOut',
            createStepName='FrequencySweep',
            variables=('P', ),
            region=self.model.rootAssembly.sets['PROBE_OUT'],
            sectionPoints=DEFAULT,
            rebar=EXCLUDE)
    
    def apply_incident_wave(self, amplitude=1.0):
        """
        Apply incident plane wave loading.
        
        Parameters:
        -----------
        amplitude : float
            Amplitude of the incident wave (Pa)
        """
        # Define incident wave interaction property
        self.model.IncidentWaveProperty(
            name='PlaneWave',
            definition=PLANAR,
            fluidDensity=self.base_properties['rho'],
            soundSpeed=np.sqrt(self.base_properties['bulk_modulus'] / 
                             self.base_properties['rho']),
            refMagnitude=amplitude,
            refAngle=0.0,
            refFrequency=self.frequency_params['f_min'])
        
        # Create incident wave interaction
        self.model.IncidentWaveInteraction(
            name='IncidentWave',
            createStepName='FrequencySweep',
            sourcePoint=None,
            standoffDistance=None,
            surface=self.model.rootAssembly.sets['INLET'],
            definition=self.model.interactionProperties['PlaneWave'],
            amplitude=UNSET)
    
    def apply_impedance_boundaries(self):
        """
        Apply non-reflecting impedance boundaries.
        """
        # Non-reflecting boundary on outlet
        self.model.AcousticImpedance(
            name='NonReflectingOutlet',
            createStepName='FrequencySweep',
            surface=self.model.rootAssembly.sets['OUTLET'],
            definition=NONREFLECTING)
        
        # Non-reflecting boundary on lateral surfaces
        self.model.AcousticImpedance(
            name='NonReflectingLateral',
            createStepName='FrequencySweep',
            surface=self.model.rootAssembly.sets['LATERAL'],
            definition=NONREFLECTING)
    
    def apply_field_gradient(self, instance, gradient_type='linear'):
        """
        Apply analytical field for continuous gradient.
        
        Parameters:
        -----------
        instance : Abaqus Instance object
            The instance to apply the field to
        gradient_type : str
            Type of gradient profile
        """
        # Define analytical field expression
        if gradient_type == 'linear':
            # Linear gradient in z (or y for 2D)
            expression = 'Y/2.0'  # Normalized to [0,1] for 2D with width=2
        elif gradient_type == 'exponential':
            expression = 'Y/2.0'
        elif gradient_type == 'tanh':
            expression = 'Y/2.0'
        
        # Create analytical field
        self.model.ExpressionField(
            name='GradientField',
            expression=expression,
            description='Spatial field for property gradient')
        
        # Apply as predefined field
        self.model.Temperature(
            name='FieldVariable',
            createStepName='Initial',
            region=instance.sets['Set-1'],
            distributionType=FIELD,
            field='GradientField',
            magnitudes=(1.0, ))
    
    def create_job(self, job_name=None, num_cpus=1):
        """
        Create and optionally submit the analysis job.
        
        Parameters:
        -----------
        job_name : str
            Name of the job (defaults to model name)
        num_cpus : int
            Number of CPUs for parallel execution
        """
        if job_name is None:
            job_name = self.model_name
        
        job = mdb.Job(name=job_name,
                     model=self.model_name,
                     description='Acoustic TL analysis in stratified medium',
                     type=ANALYSIS,
                     atTime=None,
                     waitMinutes=0,
                     waitHours=0,
                     queue=None,
                     memory=90,
                     memoryUnits=PERCENTAGE,
                     getMemoryFromAnalysis=True,
                     explicitPrecision=SINGLE,
                     nodalOutputPrecision=SINGLE,
                     echoPrint=OFF,
                     modelPrint=OFF,
                     contactPrint=OFF,
                     historyPrint=OFF,
                     userSubroutine='',
                     scratch='',
                     resultsFormat=ODB,
                     multiprocessingMode=DEFAULT,
                     numCpus=num_cpus,
                     numDomains=num_cpus)
        
        return job
    
    def build_layered_model(self, n_layers=3, dimension='2D'):
        """
        Build complete model with layered stratification.
        
        Parameters:
        -----------
        n_layers : int
            Number of layers
        dimension : str
            '2D' or '3D'
        """
        print(f"Building {dimension} layered model with {n_layers} layers...")
        
        # Create geometry
        if dimension == '2D':
            part = self.create_2d_geometry(use_partition=True, n_layers=n_layers)
            is_3d = False
        else:
            part = self.create_3d_geometry(use_partition=True, n_layers=n_layers)
            is_3d = True
        
        # Define layer properties (example: density increases with depth)
        layer_properties = []
        for i in range(n_layers):
            rho = 950.0 + 100.0 * i / (n_layers - 1)  # 950 to 1050 kg/m³
            K = 2.0e9 + 0.2e9 * i / (n_layers - 1)    # 2.0 to 2.2 GPa
            layer_properties.append({'rho': rho, 'K': K})
        
        # Create materials
        materials = self.create_layered_materials(layer_properties)
        
        # Apply sections to layers
        if dimension == '2D':
            faces = part.faces
        else:
            cells = part.cells
        
        for i in range(n_layers):
            if dimension == '2D':
                layer_region = faces[i:(i+1)]
                part.SectionAssignment(region=layer_region,
                                     sectionName=f'Section_Layer{i+1}')
            else:
                layer_region = cells[i:(i+1)]
                part.SectionAssignment(region=layer_region,
                                     sectionName=f'Section_Layer{i+1}')
        
        # Apply mesh
        self.apply_mesh(part, is_3d)
        
        # Setup assembly
        instance = self.setup_assembly_and_sets(part, is_3d)
        
        # Create step
        self.create_ssd_step()
        
        # Apply loads and BCs
        self.apply_incident_wave()
        self.apply_impedance_boundaries()
        
        # Create job
        job = self.create_job(job_name=f'{self.model_name}_layered_{dimension}')
        
        print(f"Model {self.model_name} created successfully!")
        return job
    
    def build_gradient_model(self, gradient_type='linear', dimension='2D'):
        """
        Build complete model with continuous gradient stratification.
        
        Parameters:
        -----------
        gradient_type : str
            Type of gradient: 'linear', 'exponential', 'tanh'
        dimension : str
            '2D' or '3D'
        """
        print(f"Building {dimension} gradient model with {gradient_type} profile...")
        
        # Create geometry (no partitions needed)
        if dimension == '2D':
            part = self.create_2d_geometry(use_partition=False)
            is_3d = False
        else:
            part = self.create_3d_geometry(use_partition=False)
            is_3d = True
        
        # Create gradient material
        material = self.create_gradient_material(gradient_type)
        
        # Apply section
        if dimension == '2D':
            region = regionToolset.Region(faces=part.faces)
        else:
            region = regionToolset.Region(cells=part.cells)
        
        part.SectionAssignment(region=region, sectionName='Section_Gradient')
        
        # Apply mesh
        self.apply_mesh(part, is_3d)
        
        # Setup assembly
        instance = self.setup_assembly_and_sets(part, is_3d)
        
        # Apply field gradient
        self.apply_field_gradient(instance, gradient_type)
        
        # Create step
        self.create_ssd_step()
        
        # Apply loads and BCs
        self.apply_incident_wave()
        self.apply_impedance_boundaries()
        
        # Create job
        job = self.create_job(
            job_name=f'{self.model_name}_gradient_{gradient_type}_{dimension}')
        
        print(f"Model {self.model_name} created successfully!")
        return job


# Main execution
if __name__ == '__main__':
    """
    Example usage showing both layered and gradient models.
    Run this script in Abaqus CAE: abaqus cae script=acoustic_model_generator.py
    """
    
    # Create model instance
    model_gen = AcousticStratifiedModel(model_name='AcousticTL')
    
    # Example 1: Build 2D layered model with 5 layers
    job1 = model_gen.build_layered_model(n_layers=5, dimension='2D')
    
    # Example 2: Build 2D gradient model with tanh profile (thermocline-like)
    model_gen2 = AcousticStratifiedModel(model_name='AcousticTL_Gradient')
    job2 = model_gen2.build_gradient_model(gradient_type='tanh', dimension='2D')
    
    # Example 3: Build 3D layered model
    model_gen3 = AcousticStratifiedModel(model_name='AcousticTL_3D')
    job3 = model_gen3.build_layered_model(n_layers=3, dimension='3D')
    
    print("\n" + "="*60)
    print("Models created successfully!")
    print("="*60)
    print("\nTo run the analyses:")
    print("1. job1.submit() - for 2D layered model")
    print("2. job2.submit() - for 2D gradient model") 
    print("3. job3.submit() - for 3D layered model")
    print("\nOr use: mdb.jobs['jobname'].submit()")
    print("\nAfter completion, use post_processing scripts to extract TL(f)")