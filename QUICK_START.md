# Quick Start Guide - Abaqus Acoustic Transmission Loss

## 🚀 Immediate Usage

### Option 1: Pre-built Input Files (Fastest)
```bash
# Submit layered model
abaqus job=acoustic_layered input=acoustic_transmission_loss_layered.inp

# Submit gradient model  
abaqus job=acoustic_gradient input=acoustic_transmission_loss_gradient.inp

# Post-process (after completion)
abaqus python acoustic_postprocess.py acoustic_layered.odb 190.0
abaqus python acoustic_postprocess.py acoustic_gradient.odb 190.0
```

### Option 2: Automated Workflow
```bash
# Complete automation - creates models, submits, waits, and post-processes
python run_simulation.py --both --submit --wait --post-process

# Custom frequency range
python run_simulation.py --layered --freq-start 200 --freq-end 2000 --submit
```

### Option 3: CAE Interactive
```bash
# Launch Abaqus/CAE and run
abaqus cae -noGUI create_acoustic_model.py

# Or in CAE command line:
execfile('create_acoustic_model.py')
```

## 📁 Files Overview

| File | Purpose | Usage |
|------|---------|-------|
| `acoustic_transmission_loss_layered.inp` | Ready-to-run layered model | `abaqus job=name input=file.inp` |
| `acoustic_transmission_loss_gradient.inp` | Ready-to-run gradient model | `abaqus job=name input=file.inp` |
| `create_acoustic_model.py` | CAE automation script | `abaqus cae -noGUI script.py` |
| `acoustic_postprocess.py` | Results analysis | `abaqus python script.py job.odb` |
| `run_simulation.py` | Master automation | `python run_simulation.py --help` |
| `material_properties.py` | Material utilities | `python material_properties.py --examples` |

## ⚡ Key Parameters

### Geometry
- **Length**: 200 m (waveguide)
- **Width**: 10 m 
- **Element size**: 2 m (adjust for frequency)

### Frequency
- **Range**: 100-5000 Hz
- **Increment**: 25 Hz
- **Total points**: 197 frequencies

### Materials
- **Layered**: 4 distinct layers with different ρ, K
- **Gradient**: Continuous ρ(z), K(z) variation

## 🔧 Quick Modifications

### Change Frequency Range
```bash
# Edit input files or use:
python run_simulation.py --freq-start 500 --freq-end 3000 --freq-inc 50
```

### Adjust Mesh Resolution
```bash
# For higher frequencies, reduce element size:
python run_simulation.py --element-size 1.0  # Finer mesh
```

### Custom Materials
```python
# Edit in create_acoustic_model.py:
self.layer_properties = [
    {'depth_range': (0, 50), 'density': 1000.0, 'bulk_modulus': 2.2e9},
    # Add your layers here
]
```

## 📊 Expected Results

### Transmission Loss (TL)
- **Low freq (100-500 Hz)**: 1-5 dB
- **Mid freq (500-2000 Hz)**: 5-20 dB  
- **High freq (2000-5000 Hz)**: 15-40 dB

### Output Files
- `acoustic_results.csv` - Tabulated data
- `acoustic_transmission_loss.png` - Plots
- `job_name.odb` - Abaqus results database

## 🚨 Troubleshooting

### Job Fails
- Check `.msg` file for errors
- Verify material properties (ρ > 0, K > 0)
- Reduce frequency increment if memory issues

### Poor Results
- Refine mesh (smaller elements)
- Check boundary conditions
- Verify probe locations

### Slow Performance
- Use fewer frequencies
- Increase element size (if acceptable)
- Use parallel processing: `cpus=4`

## 📞 Quick Help

```bash
# Get help on any script
python run_simulation.py --help
python material_properties.py --help

# Check Abaqus job status
abaqus job=jobname status

# View results in Abaqus/Viewer
abaqus viewer database=jobname.odb
```

## 🎯 Common Use Cases

### Research Study
```bash
python run_simulation.py --both --freq-start 100 --freq-end 2000 --submit --wait --post-process
```

### Quick Test
```bash
abaqus job=test input=acoustic_transmission_loss_layered.inp cpus=2
```

### Parameter Study
```bash
for size in 1.0 2.0 4.0; do
    python run_simulation.py --layered --element-size $size --freq-end 1000
done
```

---
**Need more details?** See `README.md` for complete documentation and `EXAMPLES.md` for detailed use cases.