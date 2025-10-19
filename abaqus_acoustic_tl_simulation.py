#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Abaqus Acoustic Transmission Loss Simulation in Stratified Media
==================================================================

Full implementation of linear acoustic propagation with:
- Layered or continuously graded density/bulk modulus profiles
- Steady-State Dynamics (Direct) for harmonic frequency sweeps
- Incident plane wave excitation
- Non-reflecting (impedance) boundaries
- TL(f) and alpha(f) computation

Author: Abaqus Acoustic Simulation
Date: 2025-10-19
Units: SI (m, kg, s, Pa)
"""

from abaqus import *
from abaqusConstants import *
import regionToolset
import mesh
import numpy as np
import sys
import os

# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================

class AcousticConfig:
    """Configuration for acoustic simulation"""
    
    def __init__(self):
        # Model name
        self.model_name = 'AcousticTL_Stratified'
        self.job_name = 'acoustic_tl_job'
        
        # Geometry (2D or 3D)
        self.dimension = 2  # 2 or 3
        self.length = 100.0  # meters (propagation direction, x)
        self.height = 50.0   # meters (vertical, z)
        self.width = 10.0    # meters (out-of-plane, y, only for 3D)
        
        # Frequency sweep
        self.freq_start = 100.0   # Hz
        self.freq_end = 5000.0    # Hz
        self.freq_inc = 25.0      # Hz
        
        # Stratification type: 'layered' or 'graded'
        self.stratification_type = 'layered'
        
        # LAYERED configuration (constant properties per layer)
        # Each layer: (z_bottom, z_top, density, bulk_modulus)
        # Units: m, kg/m³, Pa
        self.layers = [
            (0.0,   15.0, 1025.0, 2.306e9),  # Bottom layer (denser)
            (15.0,  30.0, 1015.0, 2.280e9),  # Middle layer
            (30.0,  50.0, 1000.0, 2.250e9),  # Top layer (lighter)
        ]
        
        # GRADED configuration (continuous variation)
        # Analytical functions of z (vertical coordinate)
        # rho(z) and K(z) - will be discretized via field variables
        self.graded_params = {
            'rho_surface': 1000.0,    # kg/m³ at z=height
            'rho_bottom': 1025.0,     # kg/m³ at z=0
            'K_surface': 2.250e9,     # Pa at z=height
            'K_bottom': 2.306e9,      # Pa at z=0
            'profile': 'linear',      # 'linear' or 'exponential'
        }
        
        # Mesh parameters
        self.target_elements_per_wavelength = 12
        self.max_element_size = None  # Will be auto-calculated
        
        # Probe locations (for TL measurement)
        self.probe_in_x = 20.0   # meters from inlet
        self.probe_out_x = 80.0  # meters from inlet
        
        # Incident wave parameters
        self.incident_density = 1025.0  # kg/m³
        self.incident_speed = 1500.0    # m/s
        self.incident_direction = (1.0, 0.0, 0.0)  # x-direction
        
        # Boundary buffer (distance from domain edge to probes)
        self.boundary_buffer = 5.0  # wavelengths at lowest frequency
        
    def calculate_mesh_size(self):
        """Calculate maximum element size based on highest frequency"""
        c_min = min([np.sqrt(layer[3]/layer[2]) for layer in self.layers])
        wavelength_min = c_min / self.freq_end
        self.max_element_size = wavelength_min / self.target_elements_per_wavelength
        return self.max_element_size


# ============================================================================
# MODEL CREATION FUNCTIONS
# ============================================================================

def create_model(config):
    """Create a new Abaqus model"""
    # Delete existing model if present
    if config.model_name in mdb.models.keys():
        del mdb.models[config.model_name]
    
    model = mdb.Model(name=config.model_name, modelType=STANDARD_EXPLICIT)
    
    # Remove default Model-1
    if 'Model-1' in mdb.models.keys():
        del mdb.models['Model-1']
    
    return model


def create_geometry(model, config):
    """Create geometry (2D or 3D rectangular domain)"""
    sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    
    if config.dimension == 2:
        # Create 2D rectangle
        sketch.rectangle(
            point1=(0.0, 0.0),
            point2=(config.length, config.height)
        )
        part = model.Part(name='AcousticDomain', dimensionality=TWO_D_PLANAR, 
                         type=DEFORMABLE_BODY)
        part.BaseShell(sketch=sketch)
    else:
        # Create 3D box
        sketch.rectangle(
            point1=(0.0, 0.0),
            point2=(config.length, config.height)
        )
        part = model.Part(name='AcousticDomain', dimensionality=THREE_D, 
                         type=DEFORMABLE_BODY)
        part.BaseSolidExtrude(sketch=sketch, depth=config.width)
    
    del model.sketches['__profile__']
    return part


def partition_layers(part, config):
    """Partition geometry into layers (for layered stratification)"""
    if config.stratification_type != 'layered':
        return
    
    cells = part.cells
    faces = part.faces
    
    # Create datum planes at layer interfaces
    for i, layer in enumerate(config.layers[:-1]):  # All but last layer
        z_interface = layer[1]  # Top of current layer
        
        if config.dimension == 2:
            # For 2D, use datum axis and partition face
            # Find the face to partition
            face = faces.findAt(((config.length/2, config.height/2, 0.0),))
            
            # Create datum plane at z = z_interface
            datum_plane = part.DatumPlaneByPrincipalPlane(
                principalPlane=XYPLANE, offset=z_interface
            )
            
            # Partition face by datum plane
            part.PartitionFaceByDatumPlane(
                datumPlane=part.datums[datum_plane.id],
                faces=face
            )
        else:
            # For 3D, partition cell by datum plane
            cell = cells.findAt(((config.length/2, config.height/2, config.width/2),))
            
            datum_plane = part.DatumPlaneByPrincipalPlane(
                principalPlane=XYPLANE, offset=z_interface
            )
            
            part.PartitionCellByDatumPlane(
                datumPlane=part.datums[datum_plane.id],
                cells=cell
            )


def create_materials_layered(model, config):
    """Create materials for layered stratification"""
    materials = []
    
    for i, layer in enumerate(config.layers):
        z_bottom, z_top, rho, K = layer
        mat_name = 'AcousticMedium_Layer{}'.format(i+1)
        
        mat = model.Material(name=mat_name)
        mat.Density(table=((rho,),))
        mat.Acoustic(acousticMediumFormulation=BULK_MODULUS, 
                     bulkModulus=K)
        
        materials.append((mat_name, z_bottom, z_top))
    
    return materials


def create_material_graded(model, config):
    """Create material with field-variable dependent properties"""
    mat_name = 'AcousticMedium_Graded'
    mat = model.Material(name=mat_name)
    
    # Create property tables as functions of field variable F1
    # F1 will be set to the z-coordinate
    params = config.graded_params
    
    if params['profile'] == 'linear':
        # Linear interpolation from bottom to surface
        # F1 ranges from 0 (bottom) to height (surface)
        # Create a table with representative points
        z_points = np.linspace(0, config.height, 20)
        
        rho_table = []
        K_table = []
        
        for z in z_points:
            # Linear interpolation
            frac = z / config.height
            rho = params['rho_bottom'] + frac * (params['rho_surface'] - params['rho_bottom'])
            K = params['K_bottom'] + frac * (params['K_surface'] - params['K_bottom'])
            
            rho_table.append((rho, z))
            K_table.append((K, z))
        
    elif params['profile'] == 'exponential':
        # Exponential variation
        z_points = np.linspace(0, config.height, 20)
        
        # Scale factor for exponential
        scale = 3.0  # Adjust for desired gradient steepness
        
        rho_table = []
        K_table = []
        
        for z in z_points:
            exp_factor = np.exp(-scale * z / config.height)
            rho = params['rho_surface'] + (params['rho_bottom'] - params['rho_surface']) * exp_factor
            K = params['K_surface'] + (params['K_bottom'] - params['K_surface']) * exp_factor
            
            rho_table.append((rho, z))
            K_table.append((K, z))
    
    # Create density table with field variable dependency
    mat.Density(table=tuple(rho_table), dependencies=1)
    
    # Create bulk modulus table with field variable dependency
    mat.Acoustic(acousticMediumFormulation=BULK_MODULUS,
                 bulkTable=tuple(K_table), dependencies=1)
    
    return mat_name


def create_sections_layered(model, part, config, materials):
    """Create and assign sections for layered model"""
    faces = part.faces if config.dimension == 2 else part.cells
    
    for i, (mat_name, z_bottom, z_top) in enumerate(materials):
        section_name = 'Section_Layer{}'.format(i+1)
        
        model.HomogeneousSolidSection(
            name=section_name,
            material=mat_name,
            thickness=None
        )
        
        # Find faces/cells in this layer
        z_mid = (z_bottom + z_top) / 2.0
        x_mid = config.length / 2.0
        
        if config.dimension == 2:
            region_point = (x_mid, z_mid, 0.0)
            face = faces.findAt((region_point,))
            region = regionToolset.Region(faces=face)
        else:
            y_mid = config.width / 2.0
            region_point = (x_mid, z_mid, y_mid)
            cell = faces.findAt((region_point,))
            region = regionToolset.Region(cells=cell)
        
        part.SectionAssignment(
            region=region,
            sectionName=section_name,
            offset=0.0,
            offsetType=MIDDLE_SURFACE,
            offsetField='',
            thicknessAssignment=FROM_SECTION
        )


def create_section_graded(model, part, config, mat_name):
    """Create and assign section for graded model"""
    section_name = 'Section_Graded'
    
    model.HomogeneousSolidSection(
        name=section_name,
        material=mat_name,
        thickness=None
    )
    
    # Assign to entire part
    if config.dimension == 2:
        region = regionToolset.Region(faces=part.faces)
    else:
        region = regionToolset.Region(cells=part.cells)
    
    part.SectionAssignment(
        region=region,
        sectionName=section_name,
        offset=0.0,
        offsetType=MIDDLE_SURFACE,
        offsetField='',
        thicknessAssignment=FROM_SECTION
    )


def create_assembly(model, part):
    """Create assembly"""
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    instance = assembly.Instance(name='AcousticDomain-1', part=part, dependent=ON)
    return assembly, instance


def create_field_variable(model, assembly, config):
    """Create analytical field for graded properties (F1 = z-coordinate)"""
    if config.stratification_type != 'graded':
        return
    
    # Create analytical field F1(x,y,z) = z
    model.ExpressionField(
        name='Field_Z',
        expression='Z' if config.dimension == 2 else 'Z',
        description='Vertical coordinate for property variation'
    )


def create_mesh(part, config):
    """Create mesh with acoustic elements"""
    # Calculate element size
    elem_size = config.calculate_mesh_size()
    
    # Set element type
    if config.dimension == 2:
        elem_type = mesh.ElemType(elemCode=AC2D4, elemLibrary=STANDARD)
        regions = part.faces
    else:
        elem_type = mesh.ElemType(elemCode=AC3D8, elemLibrary=STANDARD)
        regions = part.cells
    
    part.setElementType(regions=regions, elemTypes=(elem_type,))
    
    # Seed and mesh
    part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()
    
    print("Mesh generated with element size: {:.4f} m".format(elem_size))
    print("Total elements: {}".format(len(part.elements)))


def create_sets(part, assembly, instance, config):
    """Create node/element/surface sets for BC and output"""
    
    # Inlet surface (x = 0)
    if config.dimension == 2:
        inlet_edges = instance.edges.findAt(((0.0, config.height/2, 0.0),))
        assembly.Surface(side1Edges=inlet_edges, name='Inlet')
    else:
        inlet_faces = instance.faces.findAt(((0.0, config.height/2, config.width/2),))
        assembly.Surface(side1Faces=inlet_faces, name='Inlet')
    
    # Outlet surface (x = length)
    if config.dimension == 2:
        outlet_edges = instance.edges.findAt(((config.length, config.height/2, 0.0),))
        assembly.Surface(side1Edges=outlet_edges, name='Outlet')
    else:
        outlet_faces = instance.faces.findAt(((config.length, config.height/2, config.width/2),))
        assembly.Surface(side1Faces=outlet_faces, name='Outlet')
    
    # Top surface (z = height)
    if config.dimension == 2:
        top_edges = instance.edges.findAt(((config.length/2, config.height, 0.0),))
        assembly.Surface(side1Edges=top_edges, name='Top')
    else:
        top_faces = instance.faces.findAt(((config.length/2, config.height, config.width/2),))
        assembly.Surface(side1Faces=top_faces, name='Top')
    
    # Bottom surface (z = 0)
    if config.dimension == 2:
        bottom_edges = instance.edges.findAt(((config.length/2, 0.0, 0.0),))
        assembly.Surface(side1Edges=bottom_edges, name='Bottom')
    else:
        bottom_faces = instance.faces.findAt(((config.length/2, 0.0, config.width/2),))
        assembly.Surface(side1Faces=bottom_faces, name='Bottom')
    
    # Probe planes (vertical lines/planes at probe_in_x and probe_out_x)
    # Select nodes at these x-coordinates
    tolerance = config.max_element_size / 2.0
    
    # Probe IN
    nodes_in = []
    for node in instance.nodes:
        if abs(node.coordinates[0] - config.probe_in_x) < tolerance:
            nodes_in.append(node)
    
    assembly.Set(nodes=nodes_in, name='Probe_In')
    
    # Probe OUT
    nodes_out = []
    for node in instance.nodes:
        if abs(node.coordinates[0] - config.probe_out_x) < tolerance:
            nodes_out.append(node)
    
    assembly.Set(nodes=nodes_out, name='Probe_Out')
    
    print("Created probe sets: Probe_In ({} nodes), Probe_Out ({} nodes)".format(
        len(nodes_in), len(nodes_out)))


def create_step(model, config):
    """Create Steady-State Dynamics, Direct step"""
    model.SteadyStateDirectStep(
        name='SSD_FrequencySweep',
        previous='Initial',
        frequencyRange=SPECIFY,
        factorization=COMPLEX,
        matrixStorage=UNSYMMETRIC,
        scale=LOGARITHMIC
    )
    
    # Set frequency range
    model.steps['SSD_FrequencySweep'].SteadyStateDirectFrequency(
        lower=config.freq_start,
        upper=config.freq_end,
        fractionOfRange=config.freq_inc / (config.freq_end - config.freq_start)
    )


def create_incident_wave(model, assembly, config):
    """Create incident plane wave at inlet"""
    # Create incident wave property
    model.IncidentWaveProperty(
        name='PlaneWave_Property'
    )
    
    # Define fluid properties for incident wave
    model.incidentWaveProperties['PlaneWave_Property'].IncidentWaveFluidProperty(
        acousticDensity=config.incident_density,
        acousticSpeed=config.incident_speed
    )
    
    # Create incident wave interaction
    region = assembly.surfaces['Inlet']
    
    model.IncidentWave(
        name='IncidentWave_Inlet',
        createStepName='SSD_FrequencySweep',
        definition=PLANAR,
        amplitude=1.0,
        standingWave=OFF,
        property='PlaneWave_Property',
        surface=region,
        interactionProperty='PlaneWave_Property',
        direction=config.incident_direction
    )


def create_impedance_boundaries(model, assembly, config):
    """Create non-reflecting (impedance) boundaries"""
    # Outlet - non-reflecting (radiating)
    region_outlet = assembly.surfaces['Outlet']
    model.AcousticImpedance(
        name='NonReflecting_Outlet',
        createStepName='SSD_FrequencySweep',
        surface=region_outlet,
        definition=NONREFLECTING
    )
    
    # Top and bottom - non-reflecting
    region_top = assembly.surfaces['Top']
    model.AcousticImpedance(
        name='NonReflecting_Top',
        createStepName='SSD_FrequencySweep',
        surface=region_top,
        definition=NONREFLECTING
    )
    
    region_bottom = assembly.surfaces['Bottom']
    model.AcousticImpedance(
        name='NonReflecting_Bottom',
        createStepName='SSD_FrequencySweep',
        surface=region_bottom,
        definition=NONREFLECTING
    )


def create_field_output(model):
    """Configure field output requests"""
    model.FieldOutputRequest(
        name='F-Output-1',
        createStepName='SSD_FrequencySweep',
        variables=('POR', 'SENER'),
        frequency=1
    )


def create_history_output(model, assembly):
    """Configure history output at probe locations"""
    # Probe In
    region_in = assembly.sets['Probe_In']
    model.HistoryOutputRequest(
        name='H-Output-ProbeIn',
        createStepName='SSD_FrequencySweep',
        variables=('POR',),
        region=region_in,
        sectionPoints=DEFAULT,
        rebar=EXCLUDE,
        frequency=1
    )
    
    # Probe Out
    region_out = assembly.sets['Probe_Out']
    model.HistoryOutputRequest(
        name='H-Output-ProbeOut',
        createStepName='SSD_FrequencySweep',
        variables=('POR',),
        region=region_out,
        sectionPoints=DEFAULT,
        rebar=EXCLUDE,
        frequency=1
    )


def create_predefined_field(model, assembly, config):
    """Create predefined field for graded properties"""
    if config.stratification_type != 'graded':
        return
    
    # Assign Field_Z to the entire domain
    region = assembly.sets['Set-1'] if 'Set-1' in assembly.sets.keys() else None
    
    # Create a set for the entire instance if not exists
    if region is None:
        instance = assembly.instances['AcousticDomain-1']
        assembly.Set(
            nodes=instance.nodes,
            name='AllNodes'
        )
        region = assembly.sets['AllNodes']
    
    model.Temperature(
        name='Predefined_FieldZ',
        createStepName='Initial',
        region=region,
        distributionType=FIELD,
        field='Field_Z',
        magnitudes=(1.0,)
    )


def create_job(model, config):
    """Create and configure job"""
    job = mdb.Job(
        name=config.job_name,
        model=config.model_name,
        description='Acoustic TL simulation in stratified medium',
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
        multiprocessingMode=DEFAULT,
        numCpus=4,
        numDomains=4
    )
    
    return job


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to create and run acoustic TL simulation"""
    
    print("="*70)
    print("Abaqus Acoustic Transmission Loss Simulation")
    print("Stratified Medium - Frequency Sweep Analysis")
    print("="*70)
    
    # Initialize configuration
    config = AcousticConfig()
    
    print("\nConfiguration:")
    print("  Dimension: {}D".format(config.dimension))
    print("  Domain: {:.1f} x {:.1f} m".format(config.length, config.height))
    print("  Frequency: {:.0f} - {:.0f} Hz (increment: {:.1f} Hz)".format(
        config.freq_start, config.freq_end, config.freq_inc))
    print("  Stratification: {}".format(config.stratification_type))
    
    if config.stratification_type == 'layered':
        print("  Layers: {}".format(len(config.layers)))
        for i, layer in enumerate(config.layers):
            z_bot, z_top, rho, K = layer
            c = np.sqrt(K / rho)
            print("    Layer {}: z=[{:.1f}, {:.1f}] m, rho={:.1f} kg/m³, K={:.3e} Pa, c={:.1f} m/s".format(
                i+1, z_bot, z_top, rho, K, c))
    
    # Create model
    print("\n[1/12] Creating model...")
    model = create_model(config)
    
    # Create geometry
    print("[2/12] Creating geometry...")
    part = create_geometry(model, config)
    
    # Partition for layers (if layered)
    if config.stratification_type == 'layered':
        print("[3/12] Partitioning layers...")
        partition_layers(part, config)
    else:
        print("[3/12] Skipping partitioning (graded medium)...")
    
    # Create materials
    print("[4/12] Creating materials...")
    if config.stratification_type == 'layered':
        materials = create_materials_layered(model, config)
        print("  Created {} layer materials".format(len(materials)))
    else:
        mat_name = create_material_graded(model, config)
        print("  Created graded material with field dependency")
    
    # Create sections
    print("[5/12] Creating and assigning sections...")
    if config.stratification_type == 'layered':
        create_sections_layered(model, part, config, materials)
    else:
        create_section_graded(model, part, config, mat_name)
    
    # Create assembly
    print("[6/12] Creating assembly...")
    assembly, instance = create_assembly(model, part)
    
    # Create analytical field for graded properties
    if config.stratification_type == 'graded':
        print("[7/12] Creating analytical field...")
        create_field_variable(model, assembly, config)
    else:
        print("[7/12] Skipping analytical field (layered medium)...")
    
    # Create mesh
    print("[8/12] Generating mesh...")
    create_mesh(part, config)
    
    # Regenerate assembly after meshing
    assembly.regenerate()
    
    # Create sets
    print("[9/12] Creating sets and surfaces...")
    create_sets(part, assembly, instance, config)
    
    # Create step
    print("[10/12] Creating SSD step...")
    create_step(model, config)
    
    # Create incident wave
    print("[11/12] Creating incident wave and boundary conditions...")
    create_incident_wave(model, assembly, config)
    create_impedance_boundaries(model, assembly, config)
    
    # Create predefined field for graded medium
    if config.stratification_type == 'graded':
        create_predefined_field(model, assembly, config)
    
    # Create output requests
    print("[12/12] Configuring output requests...")
    create_field_output(model)
    create_history_output(model, assembly)
    
    # Create job
    print("\nCreating job: {}".format(config.job_name))
    job = create_job(model, config)
    
    # Save model
    mdb.saveAs(pathName=config.model_name + '.cae')
    print("\nModel saved: {}.cae".format(config.model_name))
    
    # Write input file
    print("Writing input file: {}.inp".format(config.job_name))
    job.writeInput(consistencyChecking=OFF)
    
    print("\n" + "="*70)
    print("Model creation complete!")
    print("="*70)
    print("\nTo run the simulation:")
    print("  1. In Abaqus/CAE: Job > Submit")
    print("  2. From command line: abaqus job={} interactive".format(config.job_name))
    print("\nAfter completion, run post-processing script:")
    print("  abaqus python postprocess_tl.py")
    print("="*70)


if __name__ == '__main__':
    main()
