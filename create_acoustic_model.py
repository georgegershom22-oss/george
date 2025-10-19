#!/usr/bin/env python3
"""
Abaqus/CAE Python Script for Automated Acoustic Transmission Loss Model Creation

This script creates complete acoustic transmission loss models in Abaqus/CAE
with both layered and continuous gradient stratification options.

Usage:
    abaqus cae -noGUI create_acoustic_model.py
    or run within Abaqus/CAE: execfile('create_acoustic_model.py')

Features:
- Automated geometry creation
- Layered or continuous gradient material properties
- Proper mesh generation with acoustic elements
- Incident wave loading
- Non-reflecting boundary conditions
- Probe locations for TL calculation
- Job submission and monitoring

Author: Generated for Abaqus Acoustic Simulation
"""

from abaqus import *
from abaqusConstants import *
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import section
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import connectorBehavior
import odbAccess
from operator import add
import math


class AcousticModelBuilder:
    """
    Builder class for acoustic transmission loss models
    """
    
    def __init__(self, model_name='AcousticTL'):
        """
        Initialize the model builder
        
        Args:
            model_name (str): Name of the Abaqus model
        """
        self.model_name = model_name
        self.model = None
        self.part = None
        self.assembly = None
        
        # Default parameters
        self.length = 200.0  # m, waveguide length
        self.width = 10.0    # m, waveguide width
        self.freq_start = 100.0  # Hz
        self.freq_end = 5000.0   # Hz
        self.freq_inc = 25.0     # Hz
        
        # Mesh parameters
        self.element_size = 2.0  # m, target element size
        
        # Material properties for layers
        self.layer_properties = [
            {'depth_range': (0, 50), 'density': 1000.0, 'bulk_modulus': 2.2e9},
            {'depth_range': (50, 100), 'density': 1015.0, 'bulk_modulus': 2.25e9},
            {'depth_range': (100, 150), 'density': 1025.0, 'bulk_modulus': 2.3e9},
            {'depth_range': (150, 200), 'density': 1030.0, 'bulk_modulus': 2.32e9}
        ]
    
    def create_model(self):
        """Create new model"""
        if self.model_name in mdb.models:
            del mdb.models[self.model_name]
        
        self.model = mdb.Model(name=self.model_name)
        print(f"Created model: {self.model_name}")
    
    def create_layered_geometry(self):
        """Create geometry for layered stratification"""
        # Create sketch
        sketch = self.model.ConstrainedSketch(name='WaveguideSketch', sheetSize=300.0)
        
        # Draw rectangle
        sketch.rectangle(point1=(0.0, 0.0), point2=(self.width, self.length))
        
        # Add partition lines for layers
        for i, layer in enumerate(self.layer_properties[:-1]):  # Skip last layer
            y_coord = layer['depth_range'][1]
            sketch.Line(point1=(0.0, y_coord), point2=(self.width, y_coord))
        
        # Create part
        self.part = self.model.Part(name='Waveguide', dimensionality=TWO_D_PLANAR, 
                                   type=DEFORMABLE_BODY)
        self.part.BaseShell(sketch=sketch)
        
        # Partition the part for layers
        faces = self.part.faces
        for i, layer in enumerate(self.layer_properties[:-1]):
            y_coord = layer['depth_range'][1]
            # Find edge at partition location
            edges = self.part.edges.findAt(((self.width/2, y_coord, 0.0),))
            if edges:
                self.part.PartitionFaceByShortestPath(
                    faces=faces, 
                    point1=(0.0, y_coord, 0.0),
                    point2=(self.width, y_coord, 0.0))
        
        print("Created layered geometry")
    
    def create_gradient_geometry(self):
        """Create geometry for continuous gradient"""
        # Create sketch
        sketch = self.model.ConstrainedSketch(name='WaveguideGradSketch', sheetSize=300.0)
        
        # Draw rectangle
        sketch.rectangle(point1=(0.0, 0.0), point2=(self.width, self.length))
        
        # Create part
        self.part = self.model.Part(name='WaveguideGrad', dimensionality=TWO_D_PLANAR, 
                                   type=DEFORMABLE_BODY)
        self.part.BaseShell(sketch=sketch)
        
        print("Created gradient geometry")
    
    def create_layered_materials(self):
        """Create materials for layered stratification"""
        for i, layer in enumerate(self.layer_properties):
            mat_name = f'Water_Layer_{i+1}'
            material = self.model.Material(name=mat_name)
            
            # Set density
            material.Density(table=((layer['density'],),))
            
            # Set bulk modulus
            material.BulkModulus(table=((layer['bulk_modulus'],),))
            
            print(f"Created material: {mat_name} (ρ={layer['density']}, K={layer['bulk_modulus']:.2e})")
    
    def create_gradient_material(self):
        """Create material with field variable dependence"""
        mat_name = 'Water_Gradient'
        material = self.model.Material(name=mat_name)
        
        # Density with field variable dependence
        # rho(z) = 1000 + 0.15*z
        density_table = []
        bulk_table = []
        
        for z in range(0, int(self.length)+1, 25):
            rho = 1000.0 + 0.15 * z
            K = 2.2e9 + 600000.0 * z
            density_table.append((rho, z))
            bulk_table.append((K, z))
        
        material.Density(table=tuple(density_table), dependencies=1)
        material.BulkModulus(table=tuple(bulk_table), dependencies=1)
        
        print(f"Created gradient material: {mat_name}")
    
    def create_analytical_field(self):
        """Create analytical field for depth variation"""
        # Create analytical field F1 = z-coordinate
        self.model.AnalyticalField(name='DepthField', 
                                  localCsys=None, 
                                  description='Depth field for gradient properties',
                                  expression='Y')  # Y is z-coordinate in 2D
        
        print("Created analytical field for depth variation")
    
    def assign_layered_sections(self):
        """Assign sections to layered regions"""
        for i, layer in enumerate(self.layer_properties):
            section_name = f'Section_Layer_{i+1}'
            mat_name = f'Water_Layer_{i+1}'
            
            # Create section
            self.model.HomogeneousSolidSection(name=section_name, 
                                              material=mat_name, 
                                              thickness=None)
            
            # Find faces in the layer depth range
            y_min, y_max = layer['depth_range']
            y_center = (y_min + y_max) / 2.0
            
            # Find face at center of layer
            faces = self.part.faces.findAt(((self.width/2, y_center, 0.0),))
            if faces:
                region = regionToolset.Region(faces=faces)
                self.part.SectionAssignment(region=region, 
                                          sectionName=section_name, 
                                          offset=0.0, 
                                          offsetType=MIDDLE_SURFACE, 
                                          offsetField='')
                print(f"Assigned section {section_name} to layer {i+1}")
    
    def assign_gradient_section(self):
        """Assign section to gradient region"""
        section_name = 'Section_Gradient'
        
        # Create section
        self.model.HomogeneousSolidSection(name=section_name, 
                                          material='Water_Gradient', 
                                          thickness=None)
        
        # Assign to entire part
        faces = self.part.faces
        region = regionToolset.Region(faces=faces)
        self.part.SectionAssignment(region=region, 
                                  sectionName=section_name, 
                                  offset=0.0, 
                                  offsetType=MIDDLE_SURFACE, 
                                  offsetField='')
        
        print("Assigned gradient section")
    
    def create_assembly(self):
        """Create assembly"""
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        
        # Create instance
        instance_name = f'{self.part.name}-1'
        self.assembly.Instance(name=instance_name, part=self.part, dependent=ON)
        
        print("Created assembly")
    
    def create_sets_and_surfaces(self):
        """Create node sets and surfaces for boundary conditions"""
        instance = self.assembly.instances[f'{self.part.name}-1']
        
        # Inlet nodes (bottom edge)
        inlet_edges = instance.edges.findAt(((self.width/2, 0.0, 0.0),))
        if inlet_edges:
            inlet_nodes = []
            for edge in inlet_edges:
                inlet_nodes.extend(edge.getNodes())
            self.assembly.Set(nodes=inlet_nodes, name='Inlet')
        
        # Outlet nodes (top edge)
        outlet_edges = instance.edges.findAt(((self.width/2, self.length, 0.0),))
        if outlet_edges:
            outlet_nodes = []
            for edge in outlet_edges:
                outlet_nodes.extend(edge.getNodes())
            self.assembly.Set(nodes=outlet_nodes, name='Outlet')
        
        # Left wall nodes
        left_edges = instance.edges.findAt(((0.0, self.length/2, 0.0),))
        if left_edges:
            left_nodes = []
            for edge in left_edges:
                left_nodes.extend(edge.getNodes())
            self.assembly.Set(nodes=left_nodes, name='LeftWall')
        
        # Right wall nodes
        right_edges = instance.edges.findAt(((self.width, self.length/2, 0.0),))
        if right_edges:
            right_nodes = []
            for edge in right_edges:
                right_nodes.extend(edge.getNodes())
            self.assembly.Set(nodes=right_nodes, name='RightWall')
        
        # Probe locations
        probe_in_y = 25.0  # 25m from inlet
        probe_out_y = self.length - 25.0  # 25m from outlet
        
        # Find nodes near probe locations
        probe_in_nodes = instance.nodes.getByBoundingBox(
            xMin=-0.1, xMax=self.width+0.1,
            yMin=probe_in_y-2.0, yMax=probe_in_y+2.0,
            zMin=-0.1, zMax=0.1)
        if probe_in_nodes:
            self.assembly.Set(nodes=probe_in_nodes, name='ProbeIn')
        
        probe_out_nodes = instance.nodes.getByBoundingBox(
            xMin=-0.1, xMax=self.width+0.1,
            yMin=probe_out_y-2.0, yMax=probe_out_y+2.0,
            zMin=-0.1, zMax=0.1)
        if probe_out_nodes:
            self.assembly.Set(nodes=probe_out_nodes, name='ProbeOut')
        
        # Create surfaces
        # Inlet surface
        inlet_faces = instance.faces.findAt(((self.width/2, 0.0, 0.0),))
        if inlet_faces:
            self.assembly.Surface(side1Faces=inlet_faces, name='SurfInlet')
        
        # Outlet surface
        outlet_faces = instance.faces.findAt(((self.width/2, self.length, 0.0),))
        if outlet_faces:
            self.assembly.Surface(side1Faces=outlet_faces, name='SurfOutlet')
        
        # Left wall surface
        left_faces = instance.faces.findAt(((0.0, self.length/2, 0.0),))
        if left_faces:
            self.assembly.Surface(side1Faces=left_faces, name='SurfLeft')
        
        # Right wall surface
        right_faces = instance.faces.findAt(((self.width, self.length/2, 0.0),))
        if right_faces:
            self.assembly.Surface(side1Faces=right_faces, name='SurfRight')
        
        print("Created sets and surfaces")
    
    def create_mesh(self):
        """Create mesh with acoustic elements"""
        instance = self.assembly.instances[f'{self.part.name}-1']
        
        # Set element type to acoustic
        elemType1 = mesh.ElemType(elemCode=AC2D4, elemLibrary=STANDARD)
        elemType2 = mesh.ElemType(elemCode=AC2D3, elemLibrary=STANDARD)
        
        faces = instance.faces
        pickedRegions = (faces,)
        self.assembly.setElementType(regions=pickedRegions, 
                                   elemTypes=(elemType1, elemType2))
        
        # Seed the part
        self.assembly.seedPartInstance(regions=(instance,), size=self.element_size)
        
        # Generate mesh
        self.assembly.generateMesh(regions=(instance,))
        
        print(f"Generated mesh with element size: {self.element_size} m")
    
    def create_step(self):
        """Create steady-state dynamics step"""
        self.model.SteadyStateDirectStep(name='SSD', 
                                        previous='Initial',
                                        frequencyRange=(self.freq_start, self.freq_end, self.freq_inc),
                                        factorization=COMPLEX)
        
        print(f"Created SSD step: {self.freq_start}-{self.freq_end} Hz, inc={self.freq_inc} Hz")
    
    def create_incident_wave(self):
        """Create incident wave loading"""
        # Create incident wave property
        self.model.IncidentWaveProperty(name='PlaneWave')
        
        # Set fluid properties for incident wave (surface water)
        rho_incident = self.layer_properties[0]['density']
        K_incident = self.layer_properties[0]['bulk_modulus']
        c_incident = math.sqrt(K_incident / rho_incident)
        
        self.model.incidentWaveProperties['PlaneWave'].IncidentWaveFluidProperty(
            fluidDensity=rho_incident, 
            soundSpeed=c_incident)
        
        # Create incident wave interaction
        region = self.assembly.surfaces['SurfInlet']
        self.model.IncidentWave(name='IncidentLoading', 
                               createStepName='SSD', 
                               surface=region, 
                               interactionProperty='PlaneWave',
                               direction=(0.0, 1.0, 0.0),  # Y-direction (along waveguide)
                               amplitude=1.0)
        
        print("Created incident wave loading")
    
    def create_boundary_conditions(self):
        """Create non-reflecting boundary conditions"""
        # Outlet - non-reflecting
        region = self.assembly.surfaces['SurfOutlet']
        self.model.AcousticImpedance(name='OutletImpedance', 
                                    createStepName='SSD', 
                                    surface=region, 
                                    nonReflecting=ON)
        
        # Left wall - non-reflecting
        region = self.assembly.surfaces['SurfLeft']
        self.model.AcousticImpedance(name='LeftWallImpedance', 
                                    createStepName='SSD', 
                                    surface=region, 
                                    nonReflecting=ON)
        
        # Right wall - non-reflecting
        region = self.assembly.surfaces['SurfRight']
        self.model.AcousticImpedance(name='RightWallImpedance', 
                                    createStepName='SSD', 
                                    surface=region, 
                                    nonReflecting=ON)
        
        print("Created non-reflecting boundary conditions")
    
    def create_field_output(self):
        """Create field output requests"""
        self.model.fieldOutputRequests['F-Output-1'].setValues(
            variables=('P',), frequency=LAST_INCREMENT)
        
        print("Created field output request")
    
    def create_history_output(self):
        """Create history output requests for probes"""
        # Input probe
        region = self.assembly.sets['ProbeIn']
        self.model.HistoryOutputRequest(name='ProbeInHistory', 
                                       createStepName='SSD', 
                                       variables=('P',), 
                                       region=region, 
                                       sectionPoints=DEFAULT, 
                                       rebar=EXCLUDE,
                                       frequency=1)
        
        # Output probe
        region = self.assembly.sets['ProbeOut']
        self.model.HistoryOutputRequest(name='ProbeOutHistory', 
                                       createStepName='SSD', 
                                       variables=('P',), 
                                       region=region, 
                                       sectionPoints=DEFAULT, 
                                       rebar=EXCLUDE,
                                       frequency=1)
        
        print("Created history output requests")
    
    def create_job(self, job_name=None):
        """Create and submit job"""
        if job_name is None:
            job_name = f'{self.model_name}_Job'
        
        # Create job
        mdb.Job(name=job_name, model=self.model_name, description='Acoustic TL simulation')
        
        # Write input file
        mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
        
        print(f"Created job: {job_name}")
        print(f"Input file written: {job_name}.inp")
        
        return job_name
    
    def build_layered_model(self):
        """Build complete layered model"""
        print("Building layered acoustic transmission loss model...")
        
        self.create_model()
        self.create_layered_geometry()
        self.create_layered_materials()
        self.assign_layered_sections()
        self.create_assembly()
        self.create_sets_and_surfaces()
        self.create_mesh()
        self.create_step()
        self.create_incident_wave()
        self.create_boundary_conditions()
        self.create_field_output()
        self.create_history_output()
        
        job_name = self.create_job(f'{self.model_name}_Layered')
        
        print("Layered model build complete!")
        return job_name
    
    def build_gradient_model(self):
        """Build complete gradient model"""
        print("Building gradient acoustic transmission loss model...")
        
        self.create_model()
        self.create_gradient_geometry()
        self.create_analytical_field()
        self.create_gradient_material()
        self.assign_gradient_section()
        self.create_assembly()
        self.create_sets_and_surfaces()
        self.create_mesh()
        self.create_step()
        self.create_incident_wave()
        self.create_boundary_conditions()
        self.create_field_output()
        self.create_history_output()
        
        job_name = self.create_job(f'{self.model_name}_Gradient')
        
        print("Gradient model build complete!")
        return job_name


def create_layered_model():
    """Create layered stratification model"""
    builder = AcousticModelBuilder('AcousticTL_Layered')
    return builder.build_layered_model()


def create_gradient_model():
    """Create continuous gradient model"""
    builder = AcousticModelBuilder('AcousticTL_Gradient')
    return builder.build_gradient_model()


def create_both_models():
    """Create both layered and gradient models"""
    print("Creating both layered and gradient acoustic models...")
    
    layered_job = create_layered_model()
    gradient_job = create_gradient_model()
    
    print(f"\nBoth models created successfully!")
    print(f"Layered model job: {layered_job}")
    print(f"Gradient model job: {gradient_job}")
    
    return layered_job, gradient_job


# Main execution
if __name__ == "__main__":
    # Create both models
    layered_job, gradient_job = create_both_models()
    
    print("\n" + "="*60)
    print("ACOUSTIC TRANSMISSION LOSS MODELS CREATED")
    print("="*60)
    print("Models are ready for submission.")
    print("To submit jobs:")
    print(f"  mdb.jobs['{layered_job}'].submit()")
    print(f"  mdb.jobs['{gradient_job}'].submit()")
    print("\nTo monitor jobs:")
    print(f"  mdb.jobs['{layered_job}'].waitForCompletion()")
    print(f"  mdb.jobs['{gradient_job}'].waitForCompletion()")
    print("\nInput files have been written and are ready for manual submission.")
    print("="*60)


# Convenience functions for interactive use
def submit_jobs():
    """Submit both jobs"""
    try:
        mdb.jobs['AcousticTL_Layered_Job'].submit()
        print("Submitted layered model job")
    except:
        print("Layered job not found or already submitted")
    
    try:
        mdb.jobs['AcousticTL_Gradient_Job'].submit()
        print("Submitted gradient model job")
    except:
        print("Gradient job not found or already submitted")


def monitor_jobs():
    """Monitor job completion"""
    try:
        print("Waiting for layered job completion...")
        mdb.jobs['AcousticTL_Layered_Job'].waitForCompletion()
        print("Layered job completed")
    except:
        print("Layered job monitoring failed")
    
    try:
        print("Waiting for gradient job completion...")
        mdb.jobs['AcousticTL_Gradient_Job'].waitForCompletion()
        print("Gradient job completed")
    except:
        print("Gradient job monitoring failed")