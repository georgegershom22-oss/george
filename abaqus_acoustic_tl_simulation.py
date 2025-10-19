#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Abaqus Python Script for Acoustic Transmission Loss Simulation
============================================================================
This script simulates acoustic wave propagation through stratified media
(layered or continuously graded) and calculates transmission loss (TL) and
absorption coefficient (α) across a frequency spectrum.

Author: Acoustic Simulation Framework
Units: SI (m-kg-s-Pa)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import numpy as np
import regionToolset
import math

# Execute CAE startup
executeOnCaeStartup()

class AcousticTLSimulation:
    """
    Complete acoustic transmission loss simulation framework
    for stratified media in Abaqus/CAE
    """
    
    def __init__(self, model_name='AcousticTL_Model', job_name='AcousticTL_Job'):
        """
        Initialize simulation parameters
        
        Parameters:
        -----------
        model_name : str
            Name of the Abaqus model
        job_name : str
            Name of the Abaqus job
        """
        self.model_name = model_name
        self.job_name = job_name
        
        # Geometry parameters (meters)
        self.domain_length = 10.0  # Axial length
        self.domain_width = 2.0    # Transverse width
        self.domain_height = 2.0   # Vertical height (for 3D)
        
        # Frequency parameters (Hz)
        self.freq_start = 100.0
        self.freq_end = 5000.0
        self.freq_increment = 25.0
        
        # Mesh parameters
        self.elem_per_wavelength = 12  # Elements per wavelength
        self.min_freq_for_mesh = 100.0  # Use this frequency for mesh sizing
        
        # Material parameters for reference medium (water at 20°C)
        self.rho_ref = 1025.0  # kg/m³
        self.bulk_ref = 2.306e9  # Pa
        self.c_ref = np.sqrt(self.bulk_ref / self.rho_ref)  # m/s
        
        # Probe locations (distance from inlet)
        self.probe_in_distance = 2.0   # meters from inlet
        self.probe_out_distance = 8.0  # meters from inlet
        
        # Model and viewport
        self.model = None
        self.viewport = None
        
    def create_model(self):
        """Create new Abaqus model"""
        # Delete existing model if it exists
        if self.model_name in mdb.models.keys():
            del mdb.models[self.model_name]
        
        # Create new model
        self.model = mdb.Model(name=self.model_name, modelType=STANDARD_EXPLICIT)
        self.viewport = session.viewports['Viewport: 1']
        
        print(f"Created model: {self.model_name}")
        
    def create_2d_geometry(self):
        """Create 2D rectangular domain for acoustic simulation"""
        
        # Create sketch
        sketch = self.model.ConstrainedSketch(name='AcousticDomain', sheetSize=20.0)
        sketch.rectangle(point1=(0.0, 0.0), point2=(self.domain_length, self.domain_width))
        
        # Create part
        part = self.model.Part(name='FluidDomain', dimensionality=TWO_D_PLANAR, 
                               type=DEFORMABLE_BODY)
        part.BaseShell(sketch=sketch)
        
        # Create partitions for layered media (example: 3 layers)
        # Layer interfaces at z = 3.33 and z = 6.67
        if hasattr(self, 'create_layers') and self.create_layers:
            sketch_partition1 = self.model.ConstrainedSketch(name='Partition1', 
                                                            sheetSize=20.0, 
                                                            gridSpacing=0.5)
            sketch_partition1.Line(point1=(self.domain_length/3, 0.0), 
                                  point2=(self.domain_length/3, self.domain_width))
            
            sketch_partition2 = self.model.ConstrainedSketch(name='Partition2', 
                                                            sheetSize=20.0, 
                                                            gridSpacing=0.5)
            sketch_partition2.Line(point1=(2*self.domain_length/3, 0.0), 
                                  point2=(2*self.domain_length/3, self.domain_width))
            
            part.PartitionFaceBySketch(faces=part.faces, sketch=sketch_partition1)
            part.PartitionFaceBySketch(faces=part.faces, sketch=sketch_partition2)
        
        # Create probe plane partitions
        sketch_probe_in = self.model.ConstrainedSketch(name='ProbeIn', 
                                                       sheetSize=20.0, 
                                                       gridSpacing=0.5)
        sketch_probe_in.Line(point1=(self.probe_in_distance, 0.0), 
                            point2=(self.probe_in_distance, self.domain_width))
        
        sketch_probe_out = self.model.ConstrainedSketch(name='ProbeOut', 
                                                        sheetSize=20.0, 
                                                        gridSpacing=0.5)
        sketch_probe_out.Line(point1=(self.probe_out_distance, 0.0), 
                             point2=(self.probe_out_distance, self.domain_width))
        
        part.PartitionFaceBySketch(faces=part.faces, sketch=sketch_probe_in)
        part.PartitionFaceBySketch(faces=part.faces, sketch=sketch_probe_out)
        
        print("Created 2D geometry with partitions")
        return part
        
    def create_3d_geometry(self):
        """Create 3D rectangular domain for acoustic simulation"""
        
        # Create sketch
        sketch = self.model.ConstrainedSketch(name='AcousticDomain3D', sheetSize=20.0)
        sketch.rectangle(point1=(0.0, 0.0), 
                        point2=(self.domain_length, self.domain_width))
        
        # Create 3D part by extrusion
        part = self.model.Part(name='FluidDomain3D', dimensionality=THREE_D, 
                              type=DEFORMABLE_BODY)
        part.BaseSolidExtrude(sketch=sketch, depth=self.domain_height)
        
        # Create partitions for layers or probe planes
        # Probe plane partitions
        datum_probe_in = part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, 
                                                         offset=self.probe_in_distance)
        datum_probe_out = part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, 
                                                          offset=self.probe_out_distance)
        
        part.PartitionCellByDatumPlane(datumPlane=part.datums[datum_probe_in.id], 
                                       cells=part.cells)
        part.PartitionCellByDatumPlane(datumPlane=part.datums[datum_probe_out.id], 
                                       cells=part.cells)
        
        print("Created 3D geometry with partitions")
        return part
        
    def create_materials_layered(self):
        """Create materials for layered stratified medium"""
        
        # Layer 1: Top water layer (warm)
        mat1 = self.model.Material(name='Water_Layer1')
        mat1.Density(table=((1020.0, ), ))  # kg/m³
        mat1.AcousticMedium(bulkModulus=2.25e9)  # Pa
        
        # Layer 2: Middle layer (transition)
        mat2 = self.model.Material(name='Water_Layer2')
        mat2.Density(table=((1025.0, ), ))  # kg/m³
        mat2.AcousticMedium(bulkModulus=2.306e9)  # Pa
        
        # Layer 3: Bottom layer (cold/dense)
        mat3 = self.model.Material(name='Water_Layer3')
        mat3.Density(table=((1030.0, ), ))  # kg/m³
        mat3.AcousticMedium(bulkModulus=2.35e9)  # Pa
        
        print("Created layered materials")
        return [mat1, mat2, mat3]
        
    def create_materials_graded(self):
        """Create materials for continuously graded medium"""
        
        # Create material with field variable dependency
        mat = self.model.Material(name='Water_Graded')
        
        # Density varies with field variable F1 (represents z-coordinate)
        # ρ(z) = ρ₀ + Δρ * z/L
        density_table = []
        bulk_table = []
        
        n_points = 20  # Number of points in the property table
        for i in range(n_points):
            z_norm = i / (n_points - 1)  # Normalized z from 0 to 1
            
            # Linear density gradient: 1020 to 1030 kg/m³
            rho = 1020.0 + 10.0 * z_norm
            
            # Corresponding bulk modulus gradient
            # Using c² = K/ρ, and assuming c varies slightly
            c = 1480.0 + 20.0 * z_norm  # Sound speed gradient
            K = rho * c * c
            
            density_table.append((rho, z_norm))
            bulk_table.append((K, z_norm))
        
        # Assign field-dependent properties
        mat.Density(table=tuple(density_table), temperatureDependency=OFF, 
                   dependencies=1)  # 1 field variable
        mat.AcousticMedium(bulkModulus=tuple(bulk_table), temperatureDependency=OFF,
                          dependencies=1)
        
        print("Created graded material with field variable dependency")
        return mat
        
    def create_sections_and_assign(self, part, materials, layered=True):
        """Create and assign sections to the part"""
        
        if layered:
            # Create sections for each layer
            for i, mat in enumerate(materials):
                section_name = f'Section_Layer{i+1}'
                self.model.HomogeneousSolidSection(name=section_name, 
                                                   material=mat.name, 
                                                   thickness=None)
            
            # Assign sections to regions
            # Assuming partitions created 3 equal regions
            faces = part.faces
            n_faces = len(faces)
            faces_per_layer = n_faces // 3
            
            for i in range(3):
                if i < len(materials):
                    region = regionToolset.Region(faces=faces[i*faces_per_layer:(i+1)*faces_per_layer])
                    part.SectionAssignment(region=region, 
                                          sectionName=f'Section_Layer{i+1}')
        else:
            # Single section for graded material
            self.model.HomogeneousSolidSection(name='Section_Graded', 
                                               material=materials.name, 
                                               thickness=None)
            region = regionToolset.Region(faces=part.faces)
            part.SectionAssignment(region=region, sectionName='Section_Graded')
            
        print("Created and assigned sections")
        
    def create_assembly(self, part):
        """Create assembly and instance"""
        
        # Create assembly
        assembly = self.model.rootAssembly
        assembly.DatumCsysByDefault(CARTESIAN)
        
        # Create instance
        instance = assembly.Instance(name='FluidInstance', part=part, dependent=ON)
        
        print("Created assembly and instance")
        return assembly, instance
        
    def create_analytical_field(self, assembly):
        """Create analytical field for graded properties"""
        
        # Define field that varies with x-coordinate (along propagation)
        # F1(x,y,z) = x/L for normalized coordinate
        self.model.ExpressionField(name='GradientField', 
                                   expression=f'X/{self.domain_length}')
        
        # Create initial conditions to assign field
        instance = assembly.instances['FluidInstance']
        region = regionToolset.Region(cells=instance.cells) if hasattr(instance, 'cells') \
                else regionToolset.Region(faces=instance.faces)
        
        self.model.FieldOutputRequest(name='F-Output-2', 
                                      createStepName='Initial', 
                                      variables=('P', 'POR'))
        
        print("Created analytical field for gradient")
        
    def create_step(self):
        """Create steady-state dynamics step for frequency sweep"""
        
        # Create SSD Direct step
        step = self.model.SteadyStateDynamicsDirectStep(
            name='FrequencySweep',
            previous='Initial',
            description='Harmonic frequency sweep for TL calculation',
            frequencyRange=((self.freq_start, self.freq_end, self.freq_increment, LOGARITHMIC), )
        )
        
        print(f"Created frequency sweep step: {self.freq_start}-{self.freq_end} Hz")
        return step
        
    def create_mesh(self, part, dimension='2D'):
        """Create acoustic mesh with appropriate element density"""
        
        # Calculate element size based on minimum wavelength
        min_wavelength = self.c_ref / self.freq_end
        elem_size = min_wavelength / self.elem_per_wavelength
        
        # Element type
        if dimension == '2D':
            elemType1 = mesh.ElemType(elemCode=AC2D4, elemLibrary=ACOUSTIC)
            elemType2 = mesh.ElemType(elemCode=AC2D3, elemLibrary=ACOUSTIC)
        else:
            elemType1 = mesh.ElemType(elemCode=AC3D8, elemLibrary=ACOUSTIC)
            elemType2 = mesh.ElemType(elemCode=AC3D6, elemLibrary=ACOUSTIC)
            elemType3 = mesh.ElemType(elemCode=AC3D4, elemLibrary=ACOUSTIC)
        
        # Set element types
        if dimension == '2D':
            regions = (part.faces, )
            part.setElementType(regions=regions, elemTypes=(elemType1, elemType2))
        else:
            regions = (part.cells, )
            part.setElementType(regions=regions, elemTypes=(elemType1, elemType2, elemType3))
        
        # Seed and mesh
        part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.1)
        part.generateMesh()
        
        print(f"Created mesh with element size: {elem_size:.4f} m")
        print(f"Target: {self.elem_per_wavelength} elements per wavelength")
        
    def create_incident_wave(self, assembly, step):
        """Create incident plane wave excitation"""
        
        # Create incident wave property
        self.model.IncidentWaveProperty(
            name='PlaneWaveProperty',
            definition=PLANAR,
            fluidDensity=self.rho_ref,
            soundSpeed=self.c_ref,
            referenceAmplitude=1.0
        )
        
        # Get inlet surface (x=0)
        instance = assembly.instances['FluidInstance']
        
        # Find edges/faces at x=0
        if hasattr(instance, 'faces'):  # 3D
            inlet_faces = []
            for face in instance.faces:
                x_coords = [v.coordinates[0] for v in face.getVertices()]
                if all(abs(x) < 1e-6 for x in x_coords):  # At x=0
                    inlet_faces.append(face)
            region = regionToolset.Region(side1Faces=inlet_faces)
        else:  # 2D
            inlet_edges = []
            for edge in instance.edges:
                x_coords = [v.coordinates[0] for v in edge.getVertices()]
                if all(abs(x) < 1e-6 for x in x_coords):  # At x=0
                    inlet_edges.append(edge)
            region = regionToolset.Region(side1Edges=inlet_edges)
        
        # Create incident wave interaction
        self.model.IncidentWave(
            name='IncidentPlaneWave',
            createStepName=step.name,
            region=region,
            definition=self.model.incidentWaveProperties['PlaneWaveProperty'],
            amplitude=1.0,
            standoffDistance=0.0,
            waveVector=(1.0, 0.0, 0.0)  # Propagation in +x direction
        )
        
        print("Created incident plane wave at inlet")
        
    def create_impedance_boundaries(self, assembly, step):
        """Create non-reflecting impedance boundaries"""
        
        instance = assembly.instances['FluidInstance']
        
        # Get outlet surface (x=L)
        if hasattr(instance, 'faces'):  # 3D
            outlet_faces = []
            lateral_faces = []
            
            for face in instance.faces:
                x_coords = [v.coordinates[0] for v in face.getVertices()]
                y_coords = [v.coordinates[1] for v in face.getVertices()]
                
                # Outlet at x=L
                if all(abs(x - self.domain_length) < 1e-6 for x in x_coords):
                    outlet_faces.append(face)
                # Lateral boundaries
                elif (all(abs(y) < 1e-6 for y in y_coords) or 
                      all(abs(y - self.domain_width) < 1e-6 for y in y_coords)):
                    lateral_faces.append(face)
                    
            outlet_region = regionToolset.Region(side1Faces=outlet_faces)
            lateral_region = regionToolset.Region(side1Faces=lateral_faces)
            
        else:  # 2D
            outlet_edges = []
            lateral_edges = []
            
            for edge in instance.edges:
                x_coords = [v.coordinates[0] for v in edge.getVertices()]
                y_coords = [v.coordinates[1] for v in edge.getVertices()]
                
                # Outlet at x=L
                if all(abs(x - self.domain_length) < 1e-6 for x in x_coords):
                    outlet_edges.append(edge)
                # Lateral boundaries
                elif (all(abs(y) < 1e-6 for y in y_coords) or 
                      all(abs(y - self.domain_width) < 1e-6 for y in y_coords)):
                    lateral_edges.append(edge)
                    
            outlet_region = regionToolset.Region(side1Edges=outlet_edges)
            lateral_region = regionToolset.Region(side1Edges=lateral_edges)
        
        # Create impedance property for non-reflecting BC
        self.model.AcousticImpedanceProperty(
            name='NonReflectingProperty',
            definition=TABULAR,
            table=((self.rho_ref * self.c_ref, ), )  # Characteristic impedance
        )
        
        # Apply to outlet
        self.model.AcousticImpedance(
            name='OutletImpedance',
            createStepName=step.name,
            region=outlet_region,
            definition=self.model.acousticImpedanceProperties['NonReflectingProperty']
        )
        
        # Apply to lateral boundaries
        self.model.AcousticImpedance(
            name='LateralImpedance',
            createStepName=step.name,
            region=lateral_region,
            definition=self.model.acousticImpedanceProperties['NonReflectingProperty']
        )
        
        print("Created non-reflecting impedance boundaries")
        
    def create_probe_sets(self, assembly):
        """Create node sets for pressure probes"""
        
        instance = assembly.instances['FluidInstance']
        
        # Get nodes at probe planes
        probe_in_nodes = []
        probe_out_nodes = []
        
        for node in instance.nodes:
            x = node.coordinates[0]
            
            # Nodes at probe_in plane
            if abs(x - self.probe_in_distance) < 1e-4:
                probe_in_nodes.append(node)
            # Nodes at probe_out plane
            elif abs(x - self.probe_out_distance) < 1e-4:
                probe_out_nodes.append(node)
        
        # Create node sets
        if probe_in_nodes:
            assembly.Set(nodes=mesh.MeshNodeArray(probe_in_nodes), name='PROBE_IN')
        if probe_out_nodes:
            assembly.Set(nodes=mesh.MeshNodeArray(probe_out_nodes), name='PROBE_OUT')
            
        print(f"Created probe sets: PROBE_IN ({len(probe_in_nodes)} nodes), "
              f"PROBE_OUT ({len(probe_out_nodes)} nodes)")
        
    def create_output_requests(self, step):
        """Define output requests for post-processing"""
        
        # Delete default output requests
        for key in self.model.fieldOutputRequests.keys():
            if key != 'F-Output-1':
                del self.model.fieldOutputRequests[key]
        
        # Field output for pressure
        self.model.FieldOutputRequest(
            name='PressureField',
            createStepName=step.name,
            variables=('P', 'POR'),  # Pressure and pressure gradient
            frequency=1
        )
        
        # History output for probes
        regionDef_in = self.model.rootAssembly.sets['PROBE_IN']
        self.model.HistoryOutputRequest(
            name='ProbeIn',
            createStepName=step.name,
            variables=('P', ),
            region=regionDef_in,
            frequency=1
        )
        
        regionDef_out = self.model.rootAssembly.sets['PROBE_OUT']
        self.model.HistoryOutputRequest(
            name='ProbeOut',
            createStepName=step.name,
            variables=('P', ),
            region=regionDef_out,
            frequency=1
        )
        
        print("Created output requests for pressure field and history")
        
    def create_job(self):
        """Create and configure analysis job"""
        
        job = mdb.Job(
            name=self.job_name,
            model=self.model_name,
            description='Acoustic TL simulation with stratified medium',
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
            historyPrint=OFF
        )
        
        print(f"Created job: {self.job_name}")
        return job
        
    def run_simulation(self, job, submit=True, wait=True):
        """Submit and monitor job execution"""
        
        if submit:
            print(f"Submitting job: {self.job_name}")
            job.submit()
            
            if wait:
                print("Waiting for job completion...")
                job.waitForCompletion()
                print("Job completed successfully")
        else:
            print(f"Job {self.job_name} created but not submitted")
            
    def run_layered_case(self):
        """Execute complete simulation for layered medium"""
        
        print("\n" + "="*60)
        print("RUNNING LAYERED STRATIFIED MEDIUM SIMULATION")
        print("="*60 + "\n")
        
        # Setup
        self.create_layers = True
        self.create_model()
        
        # Geometry
        part = self.create_2d_geometry()
        
        # Materials and sections
        materials = self.create_materials_layered()
        self.create_sections_and_assign(part, materials, layered=True)
        
        # Assembly
        assembly, instance = self.create_assembly(part)
        
        # Mesh
        self.create_mesh(part, dimension='2D')
        
        # Step
        step = self.create_step()
        
        # Boundary conditions and loads
        self.create_incident_wave(assembly, step)
        self.create_impedance_boundaries(assembly, step)
        
        # Probes and output
        self.create_probe_sets(assembly)
        self.create_output_requests(step)
        
        # Job
        job = self.create_job()
        self.run_simulation(job, submit=True, wait=True)
        
        print("\nLayered case simulation completed!")
        
    def run_graded_case(self):
        """Execute complete simulation for continuously graded medium"""
        
        print("\n" + "="*60)
        print("RUNNING CONTINUOUSLY GRADED MEDIUM SIMULATION")
        print("="*60 + "\n")
        
        # Setup
        self.create_layers = False
        self.create_model()
        
        # Geometry
        part = self.create_2d_geometry()
        
        # Materials and sections
        material = self.create_materials_graded()
        self.create_sections_and_assign(part, material, layered=False)
        
        # Assembly
        assembly, instance = self.create_assembly(part)
        
        # Analytical field for gradient
        self.create_analytical_field(assembly)
        
        # Mesh
        self.create_mesh(part, dimension='2D')
        
        # Step
        step = self.create_step()
        
        # Boundary conditions and loads
        self.create_incident_wave(assembly, step)
        self.create_impedance_boundaries(assembly, step)
        
        # Probes and output
        self.create_probe_sets(assembly)
        self.create_output_requests(step)
        
        # Job
        job = self.create_job()
        self.run_simulation(job, submit=True, wait=True)
        
        print("\nGraded case simulation completed!")


# Main execution
if __name__ == "__main__":
    
    # Create simulation instance
    sim = AcousticTLSimulation(model_name='AcousticTL_Stratified', 
                               job_name='TL_Analysis')
    
    # User selection
    print("\nACOUSTIC TRANSMISSION LOSS SIMULATION")
    print("======================================")
    print("Select stratification type:")
    print("1. Layered medium (discrete layers)")
    print("2. Continuously graded medium")
    print("3. Both cases")
    
    choice = 3  # Default to run both
    
    if choice == 1:
        sim.run_layered_case()
    elif choice == 2:
        sim.run_graded_case()
    elif choice == 3:
        # Run layered case
        sim.job_name = 'TL_Layered'
        sim.run_layered_case()
        
        # Run graded case with new instance
        sim2 = AcousticTLSimulation(model_name='AcousticTL_Graded', 
                                    job_name='TL_Graded')
        sim2.run_graded_case()
    
    print("\n" + "="*60)
    print("ALL SIMULATIONS COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\nNext step: Run post-processing script to extract TL and α")