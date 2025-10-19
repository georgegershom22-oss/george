#!/usr/bin/env python3
"""
Generate a complete 2-D linear acoustics Abaqus input deck (Helmholtz) to measure
transmission loss TL(f) and attenuation alpha(f) across a layered or graded medium
(graded realized via many thin layers).

Key features
- 2-D rectangular waveguide domain (x: propagation, y: transverse)
- Acoustic elements AC2D4 (4-node)
- Materials defined by density rho and bulk modulus K (c = sqrt(K/rho))
- Layering along y via element set partitioning and per-layer materials
- Plane-wave loading via *INCIDENT WAVE INTERACTION on inlet
- Non-reflecting (radiating) impedance on outlet and optionally on lateral walls
- Steady-State Dynamics, Direct step for harmonic sweep
- Probe node sets PROBE_IN/PROBE_OUT for post-processing (averaged |P|)

Usage
  python generate_abaqus_acoustic_tl_inp.py \
      --out job_acoustic_tl.inp \
      --length-x 2.0 --height-y 0.5 \
      --f-start 100 --f-end 5000 --f-step 25 \
      --incident-rho 1025 --incident-c 1500 \
      --lateral-bc nonreflecting \
      --auto-mesh 12 \
      --layers '[{"y_top":0.5, "y_bottom":0.25, "rho":1025, "K":2.306e9, "name":"L1"}, {"y_top":0.25, "y_bottom":0.0, "rho":980, "K":2.162e9, "name":"L2"}]'

Alternatively, you can specify --nx and --ny to override auto meshing.

Notes
- Coordinates use SI units (m, kg, s, Pa). Frequencies in Hz.
- Lateral boundary condition can be 'nonreflecting' or 'rigid'.
  'rigid' is implemented by omitting impedance on lateral edges (hard walls by geometry).
- Probe planes are placed at x = x_in = max(dx, 0.5*lambda_min) and x = x_out = Lx - max(dx, 0.5*lambda_min).
  They snap to nearest node columns.
- Graded media can be approximated by providing many thin layers or by providing
  a y-profile with --profile-points and --profile-slices to automatically layer.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass(frozen=True)
class Layer:
    y_top: float
    y_bottom: float
    rho: float
    K: float
    name: str

    @property
    def thickness(self) -> float:
        return self.y_top - self.y_bottom

    def sound_speed(self) -> float:
        if self.rho <= 0 or self.K <= 0:
            raise ValueError(f"Layer {self.name}: rho and K must be positive.")
        return math.sqrt(self.K / self.rho)


def parse_layers_arg(layers_json: str) -> List[Layer]:
    data = json.loads(layers_json)
    layers: List[Layer] = []
    for i, d in enumerate(data):
        name = d.get("name", f"L{i+1}")
        layers.append(Layer(
            y_top=float(d["y_top"]),
            y_bottom=float(d["y_bottom"]),
            rho=float(d["rho"]),
            K=float(d["K"]),
            name=name,
        ))
    # Validate stacking order and coverage
    if not layers:
        raise ValueError("At least one layer required.")
    # Sort by descending y_top (top to bottom)
    layers.sort(key=lambda L: (-L.y_top, -L.y_bottom))
    # Ensure contiguous and no overlaps when projected
    for i in range(len(layers) - 1):
        a = layers[i]
        b = layers[i+1]
        if a.y_bottom < b.y_top:  # gaps or overlap check
            # Allow slight floating tolerance
            if abs(a.y_bottom - b.y_top) > 1e-9:
                raise ValueError("Layers must be contiguous or properly ordered (top-down).")
    return layers


def build_layers_from_profile(height_y: float, profile_points_json: str, num_slices: int) -> List[Layer]:
    """
    Build piecewise-constant layers by interpolating rho(y), K(y) from profile points.
    profile_points_json: JSON array of objects with {y, rho, K} where y in [0, height_y]
    """
    pts_raw = json.loads(profile_points_json)
    pts = sorted([(float(p["y"]), float(p["rho"]), float(p["K"])) for p in pts_raw], key=lambda t: t[0])
    if not pts or pts[0][0] > 0 or pts[-1][0] < height_y:
        raise ValueError("Profile points must span from y=0 to y=height_y.")

    def interp(y: float) -> Tuple[float, float]:
        # linear interpolate between nearest bounding points
        for i in range(len(pts) - 1):
            y0, rho0, K0 = pts[i]
            y1, rho1, K1 = pts[i+1]
            if y0 <= y <= y1:
                if y1 == y0:
                    return rho0, K0
                t = (y - y0) / (y1 - y0)
                rho = rho0 + t * (rho1 - rho0)
                K = K0 + t * (K1 - K0)
                return rho, K
        # clamp
        return pts[-1][1], pts[-1][2]

    dy = height_y / num_slices
    layers: List[Layer] = []
    yb = 0.0
    for i in range(num_slices):
        yt = min(height_y, yb + dy)
        yc = 0.5 * (yb + yt)
        rho, K = interp(yc)
        layers.append(Layer(y_top=yt, y_bottom=yb, rho=rho, K=K, name=f"G{i+1}"))
        yb = yt
    return layers


def compute_mesh_counts(length_x: float, height_y: float, f_max: float, layers: List[Layer], elems_per_lambda: int,
                        nx_override: Optional[int], ny_override: Optional[int]) -> Tuple[int, int]:
    c_min = min(L.sound_speed() for L in layers)
    lambda_min = c_min / f_max
    target_dx = lambda_min / float(elems_per_lambda)
    nx = int(math.ceil(length_x / target_dx))
    # make at least 4 elements if tiny
    nx = max(nx, 4)
    # vertical resolution: do not be too coarse; scale somewhat with dx
    ny = int(math.ceil(height_y / target_dx))
    ny = max(ny, 4)

    if nx_override:
        nx = int(nx_override)
    if ny_override:
        ny = int(ny_override)
    return nx, ny


def assign_elements_to_layers(ny: int, dy: float, layers: List[Layer]) -> List[int]:
    """For each j-row (0..ny-1), return the index of the layer that contains the element row centroid.
       This assumes layers fully cover [0, height_y] and are contiguous.
    """
    # Build lookup of y ranges
    layer_ranges: List[Tuple[float, float]] = [(L.y_bottom, L.y_top) for L in layers]
    assigned: List[int] = []
    for j in range(ny):
        y0 = j * dy
        y1 = (j + 1) * dy
        yc = 0.5 * (y0 + y1)
        found = None
        for idx, (yb, yt) in enumerate(layer_ranges):
            if yb - 1e-9 <= yc <= yt + 1e-9:
                found = idx
                break
        if found is None:
            raise RuntimeError(f"No layer found for element row j={j}, yc={yc}")
        assigned.append(found)
    return assigned


def build_input_deck(
    length_x: float,
    height_y: float,
    nx: int,
    ny: int,
    layers: List[Layer],
    f_start: float,
    f_end: float,
    f_step: float,
    incident_rho: float,
    incident_c: float,
    lateral_bc: str,
) -> str:
    # Basic grid
    dx = length_x / float(nx)
    dy = height_y / float(ny)

    # Compute probe positions based on lambda_min
    c_min = min(L.sound_speed() for L in layers)
    lambda_min = c_min / max(f_start, 1e-6)  # conservative near start for probe spacing; but we will offset by 0.5*lambda_min
    probe_margin = max(dx, 0.5 * (c_min / max(f_end, 1e-6)))  # use lambda_min at f_end

    # Snap probe columns
    i_probe_in = min(max(1, int(round(probe_margin / dx))), nx - 2)
    i_probe_out = max(min(nx - 2, int(round((length_x - probe_margin) / dx))), 1)

    # Layer assignment per element row (constant along x for horizontal layering)
    row_to_layer_index = assign_elements_to_layers(ny, dy, layers)

    lines: List[str] = []
    lines.append("*HEADING")
    lines.append("** 2-D Linear Acoustics TL sweep (AC2D4) - generated by generate_abaqus_acoustic_tl_inp.py")

    # Nodes
    lines.append("*NODE")
    # Node indexing: (i, j) -> n = j*(nx+1) + i + 1
    def node_id(i: int, j: int) -> int:
        return j * (nx + 1) + i + 1

    for j in range(ny + 1):
        y = j * dy
        for i in range(nx + 1):
            x = i * dx
            nid = node_id(i, j)
            lines.append(f"{nid}, {x:.9g}, {y:.9g}")

    # Elements (AC2D4)
    lines.append("*ELEMENT, TYPE=AC2D4, ELSET=ALL")
    def elem_id(i: int, j: int) -> int:
        # (i: 0..nx-1, j: 0..ny-1)
        return j * nx + i + 1

    # Track per-layer element sets
    layer_to_elems: List[List[int]] = [[] for _ in layers]

    for j in range(ny):
        for i in range(nx):
            e = elem_id(i, j)
            n1 = node_id(i, j)
            n2 = node_id(i + 1, j)
            n3 = node_id(i + 1, j + 1)
            n4 = node_id(i, j + 1)
            lines.append(f"{e}, {n1}, {n2}, {n3}, {n4}")
            layer_idx = row_to_layer_index[j]
            layer_to_elems[layer_idx].append(e)

    # Materials and Sections
    for L in layers:
        lines.append(f"*MATERIAL, NAME={L.name}")
        lines.append("*DENSITY")
        lines.append(f"{L.rho:.9g},")
        lines.append("*BULK MODULUS")
        lines.append(f"{L.K:.9g},")

    for idx, L in enumerate(layers):
        elset_name = f"ESET_{L.name}"
        # Element set for this layer
        lines.append(f"*ELSET, ELSET={elset_name}")
        elems = layer_to_elems[idx]
        # Write in chunks of up to ~16 per line
        chunk = []
        for k, eid in enumerate(elems, 1):
            chunk.append(str(eid))
            if (k % 16) == 0:
                lines.append(", ".join(chunk))
                chunk = []
        if chunk:
            lines.append(", ".join(chunk))
        # Section assignment
        lines.append(f"*SOLID SECTION, ELSET={elset_name}, MATERIAL={L.name}")

    # Surfaces (element-based)
    # Quad AC2D4 face numbering: S1=bottom (n1-n2), S2=right (n2-n3), S3=top (n3-n4), S4=left (n4-n1)
    # Inlet: i=0 column -> S4 edges
    lines.append("*SURFACE, NAME=SURF_INLET, TYPE=ELEMENT")
    for j in range(ny):
        e = elem_id(0, j)
        lines.append(f"{e}, S4")

    # Outlet: i=nx-1 column -> S2 edges
    lines.append("*SURFACE, NAME=SURF_OUTLET, TYPE=ELEMENT")
    for j in range(ny):
        e = elem_id(nx - 1, j)
        lines.append(f"{e}, S2")

    # Bottom: j=0 row -> S1 edges across i
    lines.append("*SURFACE, NAME=SURF_BOTTOM, TYPE=ELEMENT")
    for i in range(nx):
        e = elem_id(i, 0)
        lines.append(f"{e}, S1")

    # Top: j=ny-1 row -> S3 edges across i
    lines.append("*SURFACE, NAME=SURF_TOP, TYPE=ELEMENT")
    for i in range(nx):
        e = elem_id(i, ny - 1)
        lines.append(f"{e}, S3")

    # Probe node sets (node columns)
    def write_node_set(name: str, i_col: int):
        lines.append(f"*NSET, NSET={name}")
        chunk = []
        for j in range(ny + 1):
            nid = node_id(i_col, j)
            chunk.append(str(nid))
            if (len(chunk) % 16) == 0:
                lines.append(", ".join(chunk))
                chunk = []
        if chunk:
            lines.append(", ".join(chunk))

    write_node_set("PROBE_IN", i_probe_in)
    write_node_set("PROBE_OUT", i_probe_out)

    # Step: SSD Direct
    lines.append("*STEP, NAME=SSD, NLGEOM=NO")
    lines.append("*STEADY STATE DYNAMICS, DIRECT")
    lines.append(f"{f_start:.9g}, {f_end:.9g}, {f_step:.9g}")

    # Incident wave loading on inlet
    lines.append("*INCIDENT WAVE INTERACTION PROPERTY, NAME=PLANEWAVE")
    lines.append("*INCIDENT WAVE FLUID PROPERTY")
    lines.append(f"{incident_rho:.9g}, {incident_c:.9g}")
    lines.append("*INCIDENT WAVE INTERACTION, NAME=INC1, PROPERTY=PLANEWAVE")
    # Direction cosines for x-normal (incoming wave entering from SURF_INLET along +x)
    lines.append("SURF_INLET, 1., 0., 0.")

    # Impedance / Non-reflecting boundaries
    if lateral_bc.lower() == "nonreflecting":
        lines.append("*IMPEDANCE, TYPE=NONREFLECTING")
        lines.append("SURF_BOTTOM,")
        lines.append("SURF_TOP,")
    else:
        # Rigid walls are simply the default (no impedance); leave as is
        pass
    # Always non-reflecting outlet
    lines.append("*IMPEDANCE, TYPE=NONREFLECTING")
    lines.append("SURF_OUTLET,")

    # Output requests
    lines.append("*OUTPUT, FIELD, FREQUENCY=1")
    lines.append("*NODE OUTPUT")
    lines.append("P")
    lines.append("*OUTPUT, HISTORY, FREQUENCY=1")
    lines.append("*NODE OUTPUT, NSET=PROBE_IN")
    lines.append("P")
    lines.append("*NODE OUTPUT, NSET=PROBE_OUT")
    lines.append("P")

    lines.append("*END STEP")

    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Generate a 2D Abaqus input for acoustic TL sweep (SSD Direct)")
    p.add_argument("--out", required=False, default="job_acoustic_tl.inp", help="Output INP filename")
    p.add_argument("--length-x", type=float, default=2.0, help="Domain length in x (m)")
    p.add_argument("--height-y", type=float, default=0.5, help="Domain height in y (m)")
    p.add_argument("--f-start", type=float, default=100.0, help="Start frequency (Hz)")
    p.add_argument("--f-end", type=float, default=5000.0, help="End frequency (Hz)")
    p.add_argument("--f-step", type=float, default=25.0, help="Frequency increment (Hz)")
    p.add_argument("--incident-rho", type=float, default=1025.0, help="Incident field density (kg/m^3)")
    p.add_argument("--incident-c", type=float, default=1500.0, help="Incident field sound speed (m/s)")
    p.add_argument("--lateral-bc", choices=["nonreflecting", "rigid"], default="nonreflecting",
                   help="Lateral boundary type")

    # Mesh: either auto based on elems/lambda at f_end, or override with nx/ny
    p.add_argument("--auto-mesh", type=int, default=12, help="Target elems per lambda_min at f_end")
    p.add_argument("--nx", type=int, default=0, help="Override elements along x (0 to auto)")
    p.add_argument("--ny", type=int, default=0, help="Override elements along y (0 to auto)")

    # Layering options
    group = p.add_mutually_exclusive_group()
    group.add_argument("--layers", type=str, default="",
                       help="JSON array of layers [{y_top,y_bottom,rho,K,name?}, ...] (top-down)")
    group.add_argument("--profile-points", type=str, default="",
                       help="JSON array of {y,rho,K} points spanning [0,height_y] for graded media")
    p.add_argument("--profile-slices", type=int, default=50, help="Number of slices for graded profile")

    args = p.parse_args(argv)

    # Layers input
    if args.layers:
        layers = parse_layers_arg(args.layers)
    elif args.profile_points:
        layers = build_layers_from_profile(args.height_y, args.profile_points, args.profile_slices)
    else:
        # Default 2-layer example if none provided
        layers = [
            Layer(y_top=args.height_y, y_bottom=0.5 * args.height_y, rho=1025.0, K=2.306e9, name="L1"),
            Layer(y_top=0.5 * args.height_y, y_bottom=0.0, rho=980.0, K=2.162e9, name="L2"),
        ]

    # Validate total coverage
    top_y = max(L.y_top for L in layers)
    bot_y = min(L.y_bottom for L in layers)
    if abs(top_y - args.height_y) > 1e-9 or abs(bot_y - 0.0) > 1e-9:
        raise ValueError("Layers must cover [0, height_y] exactly (top to  height, bottom to 0).")

    nx, ny = compute_mesh_counts(
        length_x=args.length_x,
        height_y=args.height_y,
        f_max=args.f_end,
        layers=layers,
        elems_per_lambda=args.auto_mesh,
        nx_override=args.nx if args.nx > 0 else None,
        ny_override=args.ny if args.ny > 0 else None,
    )

    deck = build_input_deck(
        length_x=args.length_x,
        height_y=args.height_y,
        nx=nx,
        ny=ny,
        layers=layers,
        f_start=args.f_start,
        f_end=args.f_end,
        f_step=args.f_step,
        incident_rho=args.incident_rho,
        incident_c=args.incident_c,
        lateral_bc=args.lateral_bc,
    )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(deck)

    # Print a concise summary
    c_min = min(L.sound_speed() for L in layers)
    lambda_min = c_min / args.f_end
    print("Generated:", args.out)
    print(f"- Domain: Lx={args.length_x} m, Hy={args.height_y} m; Mesh: nx={nx}, ny={ny}")
    print(f"- f: {args.f_start} .. {args.f_end} Hz (step {args.f_step})")
    print(f"- Incident wave: rho={args.incident_rho} kg/m^3, c={args.incident_c} m/s")
    print(f"- Layers: {len(layers)} (c_min={c_min:.3f} m/s, lambda_min@f_end={lambda_min:.4f} m)")
    print("- Boundaries: inlet=incident wave, outlet=nonreflecting, laterals=", args.lateral_bc)
    print("- Probes: node sets PROBE_IN / PROBE_OUT (averaged |P|)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
