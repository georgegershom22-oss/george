#!/usr/bin/env python3
"""
Post-process Abaqus ODB from a Steady-State Dynamics, Direct acoustic analysis to compute
Transmission Loss TL(f) and amplitude-based attenuation alpha_amp(f).

Requirements
- Run with Abaqus Python (abaqus python postprocess_tl_from_odb.py --odb job.odb --dx 1.0)
- The ODB must contain:
  - Step named 'SSD'
  - Field output 'P' (complex pressure) available per frame
  - Node sets 'PROBE_IN' and 'PROBE_OUT'

Outputs
- Prints a small table to stdout: f, Pin_avg_mag, Pout_avg_mag, TL_dB, alpha_amp(1/m)
- Optionally writes CSV via --csv out.csv

Formulas
- TL(f) = 20*log10(|Pin|/|Pout|)
- alpha_amp(f) = (ln(10)/20) * TL(f) / dx

Notes
- Uses magnitude of complex pressure averaged over nodes in the probe sets.
- If you need intensity-based attenuation, replace formula with ln(10)/10 factor.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Compute TL(f) and alpha_amp(f) from Abaqus ODB")
    p.add_argument("--odb", required=True, help="Path to ODB file")
    p.add_argument("--step", default="SSD", help="Step name")
    p.add_argument("--probe-in", default="PROBE_IN", help="Inlet probe node set name")
    p.add_argument("--probe-out", default="PROBE_OUT", help="Outlet probe node set name")
    p.add_argument("--csv", default="", help="Optional CSV output path")
    p.add_argument("--dx", type=float, required=True, help="Axial spacing between probes (m)")

    args = p.parse_args(argv)

    try:
        from odbAccess import openOdb  # type: ignore
    except Exception as e:
        sys.stderr.write("This script must be run with Abaqus Python.\n")
        return 2

    odb = openOdb(args.odb)
    try:
        step = odb.steps[args.step]
    except Exception:
        sys.stderr.write(f"Step '{args.step}' not found in ODB.\n")
        odb.close()
        return 3

    root = odb.rootAssembly
    try:
        nset_in = root.nodeSets[args.probe_in]
        nset_out = root.nodeSets[args.probe_out]
    except Exception:
        sys.stderr.write("Probe node sets not found. Ensure PROBE_IN and PROBE_OUT exist.\n")
        odb.close()
        return 4

    frames = step.frames
    if not frames:
        sys.stderr.write("No frames found in the step (check analysis).\n")
        odb.close()
        return 5

    freqs = []
    pin = []
    pout = []

    for fr in frames:
        f = getattr(fr, 'frequency', None)
        if f is None:
            # In some versions, harmonic frequency is in frameValue for SSD
            f = getattr(fr, 'frameValue', None)
        if f is None:
            # Skip frames without frequency
            continue
        P = fr.fieldOutputs.get('P')
        if P is None:
            sys.stderr.write("Field output 'P' not found in a frame.\n")
            odb.close()
            return 6

        # Inlet average magnitude
        subset_in = P.getSubset(region=nset_in)
        vals_in = subset_in.values
        if not vals_in:
            sys.stderr.write("Empty PROBE_IN set.\n")
            odb.close()
            return 7
        mags_in = []
        for vi in vals_in:
            # vi.data is complex represented as (real, imag)
            if hasattr(vi, 'data'):  # NodeValue
                re = vi.data[0]
                im = vi.data[1]
            else:
                # Some versions use vi.pressure with magnitude/phase; fallback not supported broadly
                re = vi.pReal
                im = vi.pImag
            mags_in.append(math.hypot(re, im))
        avg_in = sum(mags_in) / float(len(mags_in))

        # Outlet average magnitude
        subset_out = P.getSubset(region=nset_out)
        vals_out = subset_out.values
        if not vals_out:
            sys.stderr.write("Empty PROBE_OUT set.\n")
            odb.close()
            return 8
        mags_out = []
        for vo in vals_out:
            if hasattr(vo, 'data'):
                re = vo.data[0]
                im = vo.data[1]
            else:
                re = vo.pReal
                im = vo.pImag
            mags_out.append(math.hypot(re, im))
        avg_out = sum(mags_out) / float(len(mags_out))

        freqs.append(float(f))
        pin.append(avg_in)
        pout.append(avg_out)

    # Compute TL and alpha_amp
    TL = [20.0 * math.log10(pi / po) for pi, po in zip(pin, pout)]
    alpha_amp = [(math.log(10.0) / 20.0) * tl / args.dx for tl in TL]

    # Output
    header = ["f_Hz", "Pin_avg_mag", "Pout_avg_mag", "TL_dB", "alpha_amp_1_per_m"]
    rows = [header]
    for f, pi, po, tl, a in zip(freqs, pin, pout, TL, alpha_amp):
        rows.append([f"{f:.6g}", f"{pi:.6g}", f"{po:.6g}", f"{tl:.6g}", f"{a:.6g}"])

    # Print concise table
    print(",".join(header))
    for r in rows[1:]:
        print(",".join(r))

    # Optional CSV
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"Wrote CSV: {args.csv}")

    odb.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
