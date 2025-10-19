# Quick Start Guide - Abaqus Acoustic Transmission Loss

Get up and running in 5 minutes!

## Prerequisites

- Abaqus installed and accessible via `abaqus` command
- Python (for post-processing and visualization)
- Optional: matplotlib, numpy (for plotting)

## Quick Start (3 Commands)

```bash
# 1. Run simulation (15-45 min depending on hardware)
abaqus job=acoustic_TL input=acoustic_transmission_loss.inp cpus=4 interactive

# 2. Extract transmission loss data
abaqus python extract_transmission_loss.py acoustic_TL.odb

# 3. Visualize results
python plot_transmission_loss.py acoustic_TL_transmission_loss.csv
```

## Automated Workflow

Use the provided script for end-to-end automation:

```bash
chmod +x run_simulation.sh
./run_simulation.sh acoustic_transmission_loss 4
```

## Expected Outputs

After successful run, you'll have:

- `acoustic_TL.odb` - Abaqus results database
- `acoustic_TL_transmission_loss.csv` - TL and α data
- `acoustic_TL_comprehensive.png` - Multi-panel visualization
- `acoustic_TL_detailed.png` - Detailed TL plot
- `acoustic_TL_phase.png` - Phase analysis

## View Results in Abaqus/Viewer

```bash
abaqus viewer odb=acoustic_TL.odb
```

In Viewer:
1. Plot → Contours → Field Output: POR (pressure)
2. Animate through frequencies: Tools → XY Data → From ODB
3. Create XY plots of pressure vs frequency

## Customize Parameters

### Change Frequency Range

Edit `acoustic_transmission_loss.inp`, find:
```inp
*STEADY STATE DYNAMICS, DIRECT
100., 5000., 196
```

Change to your desired range, e.g., 50-10000 Hz:
```inp
*STEADY STATE DYNAMICS, DIRECT
50., 10000., 398
```

### Modify Stratification

Edit material properties in .inp file:
```inp
*MATERIAL, NAME=WATER_THERMOCLINE
*DENSITY
1026.0,              ← Change this
*BULK MODULUS
2.278e9,             ← And this
```

### Generate New Mesh

```bash
python mesh_generator.py --length 100 --depth 50 --size 0.2 --output custom_mesh.inp
```

## Validate Mesh Before Running

```bash
python validate_mesh.py acoustic_transmission_loss.inp
```

This checks:
- Mesh resolution (elements per wavelength)
- Element quality (aspect ratios)
- Material properties (sound speeds)

## Troubleshooting

### Job fails immediately
- Check .dat file: `cat acoustic_TL.dat | tail -50`
- Common issue: Material properties not defined

### Job runs but no output
- Check .sta file for convergence: `tail -f acoustic_TL.sta`
- Look for errors in .msg file: `cat acoustic_TL.msg | grep -i error`

### Post-processing fails
- Verify node sets exist: `grep "NSET" acoustic_transmission_loss.inp`
- Node sets must be named: PROBE_IN, PROBE_OUT

### Plot script fails
- Install dependencies: `pip install matplotlib numpy scipy`
- Or view CSV directly: `cat acoustic_TL_transmission_loss.csv | column -s, -t | less`

## Performance Tips

### Faster Runs
- Reduce frequency points: change increment in *STEADY STATE DYNAMICS
- Coarsen mesh: use larger element size (but maintain λ/6 minimum)
- Use fewer CPUs if memory-limited

### Higher Accuracy
- Refine mesh: λ/10 or λ/12 instead of λ/6
- Increase domain size: more distance from boundaries to probes
- Use finer frequency increments

## Expected Runtime

| Configuration | Elements | Freq. Points | CPUs | Time |
|---------------|----------|--------------|------|------|
| Quick test    | 20,000   | 50           | 4    | 5 min |
| Standard      | 80,000   | 197          | 4    | 30 min |
| High accuracy | 320,000  | 397          | 8    | 2-4 hrs |

## Key Results to Check

Look for in your results:

1. **Transmission Loss (TL):** Should be positive (energy loss through stratification)
   - Typical range: 0-10 dB for ocean thermocline
   - Frequency-dependent due to interference

2. **Attenuation Coefficient (α):** Rate of decay per unit distance
   - Typical range: 0.01-0.1 dB/m (10-100 dB/km)
   - Should increase with frequency (classical absorption)

3. **Spectral Features:** Peaks and troughs in TL(f)
   - Due to constructive/destructive interference at layer interfaces
   - Spacing related to layer thickness and sound speed contrasts

## Next Steps

1. **Experiment with stratification:**
   - Try different layer depths
   - Vary density/sound speed contrasts
   - Add more layers

2. **Frequency studies:**
   - Low frequency: < 500 Hz (long wavelengths, less scattering)
   - Mid frequency: 500-2000 Hz (transition region)
   - High frequency: > 2000 Hz (short wavelengths, more scattering)

3. **Parameter studies:**
   - Vary probe separation
   - Change domain length
   - Test different boundary conditions

4. **Validation:**
   - Compare with analytical solutions (homogeneous case)
   - Check energy conservation
   - Mesh convergence study

## Additional Resources

- Full documentation: `README_ABAQUS_ACOUSTIC.md`
- Abaqus acoustic analysis guide: [docs.software.vt.edu](https://docs.software.vt.edu)
- Theory: Jensen et al., "Computational Ocean Acoustics"

## Support Files

```
acoustic_transmission_loss.inp    Main input file (ready to run)
extract_transmission_loss.py      ODB post-processing
plot_transmission_loss.py         Visualization
mesh_generator.py                 Custom mesh generation
validate_mesh.py                  Pre-run validation
run_simulation.sh                 Automated workflow
README_ABAQUS_ACOUSTIC.md        Comprehensive documentation
QUICKSTART.md                    This guide
```

## Getting Help

1. **Abaqus errors:** Check .dat, .msg, .sta files
2. **Mesh issues:** Run `python validate_mesh.py <file.inp>`
3. **Physics questions:** See theory section in README_ABAQUS_ACOUSTIC.md
4. **Post-processing:** Check CSV file exists and has data

---

**Ready to run!** Just execute:
```bash
./run_simulation.sh
```

And in ~30 minutes you'll have complete transmission loss results!
