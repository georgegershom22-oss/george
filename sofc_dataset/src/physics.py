from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

F = 96485.3329  # C/mol
R = 8.314462618  # J/mol/K


def _smooth_random_field(nx: int, ny: int, rng: np.random.Generator, scale: float = 0.05) -> np.ndarray:
    noise = rng.standard_normal((nx, ny))
    # Low-pass by FFT: keep only low frequencies
    # rfft2 output has shape (nx, ny//2+1). Use fftfreq for x and rfftfreq for y.
    fx = np.fft.fftfreq(nx)
    fy = np.fft.rfftfreq(ny)
    kx, ky = np.meshgrid(fx, fy, indexing="ij")  # shapes (nx, ny//2+1)
    H = np.exp(-((kx**2 + ky**2) / 0.02))
    Nf = np.fft.rfft2(noise)
    smooth = np.fft.irfft2(Nf * H, s=(nx, ny)).real
    smooth = (smooth - np.min(smooth)) / (np.ptp(smooth) + 1e-12)
    return 1.0 + scale * (smooth - 0.5)


def generate_current_density_interface(params: Dict[str, float], grid: Dict[str, np.ndarray], seed: int | None = None) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x, y = grid["x"], grid["y"]
    nx, ny = len(x), len(y)

    j_avg = max(0.01, params["current_density_A_per_cm2"])  # A/cm^2
    # Convert to A/m^2 for internal calculations
    j_avg_m2 = j_avg * 1e4

    # Along x (flow direction) decay due to fuel depletion
    Lx = grid["Lx"]
    flow = max(0.1, params["fuel_flow_sLpm"])  # sL/min
    depletion_scale = np.clip(j_avg / (flow * 0.5), 0.05, 1.5)
    fx = np.exp(-depletion_scale * (x / (Lx + 1e-12)))  # shape (nx,)

    # Along y channels: sinusoidal modulation based on number of channels
    nchan = int(params["num_flow_channels"]) if "num_flow_channels" in params else 5
    gy = 0.5 * (1.0 + np.cos(2 * np.pi * nchan * (y / (grid["Ly"] + 1e-12))))  # [0,1]
    gy = 0.6 + 0.4 * gy  # [0.6,1.0]

    base = (fx[:, None]) * (gy[None, :])
    base = base / base.mean()  # normalize to mean 1

    rnd = _smooth_random_field(nx, ny, rng, scale=0.1)

    j_xy = j_avg_m2 * base * rnd  # A/m^2

    # Overpotential via inverse Butler-Volmer (symmetric approx via asinh)
    T = 0.5 * (params["air_inlet_T_K"] + params["fuel_inlet_T_K"])  # simple average
    alpha = np.clip(params.get("alpha", 0.5), 0.2, 0.9)
    i0 = max(1e-3, params.get("i0_A_per_cm2", 0.05)) * 1e4  # A/m^2
    eta_xy = (R * T / (alpha * F)) * np.arcsinh(j_xy / (2.0 * i0))  # V

    return j_xy, eta_xy


def volumetric_heat_source_from_interface(j_xy: np.ndarray, eta_xy: np.ndarray, grid: Dict[str, np.ndarray]) -> np.ndarray:
    # Spread interfacial heat q" = j*eta (W/m^2) over a thin active layer in anode and cathode sides
    nx, ny = j_xy.shape
    nz = len(grid["z"])
    q = np.zeros((nx, ny, nz), dtype=np.float32)

    q_area = j_xy * eta_xy  # W/m^2

    # Assign to first few cells in anode and cathode near the electrolyte interface
    layer_cells = grid["layer_cells"]
    anode_cells = layer_cells["anode"]
    electrolyte_cells = layer_cells["electrolyte"]
    # Interface index between anode and electrolyte is anode_cells-1 and anode_cells
    i_start_anode = max(0, anode_cells - min(3, anode_cells))
    i_end_anode = anode_cells  # exclusive upper bound slice index

    # Cathode side just after electrolyte
    i_start_cath = anode_cells + electrolyte_cells
    i_end_cath = min(nz, i_start_cath + min(3, grid["layer_cells"]["cathode"]))

    if i_end_anode > i_start_anode:
        q[:, :, i_start_anode:i_end_anode] += (q_area[:, :, None] / max(1, (i_end_anode - i_start_anode)))
    if i_end_cath > i_start_cath:
        q[:, :, i_start_cath:i_end_cath] += (0.5 * q_area[:, :, None] / max(1, (i_end_cath - i_start_cath)))

    return q.astype(np.float32)


def solve_temperature(q: np.ndarray, k_field: np.ndarray, params: Dict[str, float], grid: Dict[str, np.ndarray], n_iter: int = 400) -> np.ndarray:
    # Simple Jacobi iteration for -div(k grad T) = q with Dirichlet at z=0 (fuel inlet) and z=H (air inlet)
    nx, ny, nz = q.shape
    T = np.empty_like(q, dtype=np.float32)
    T[:, :, 0] = params["fuel_inlet_T_K"]
    T[:, :, -1] = params["air_inlet_T_K"]
    # Initialize interior as linear interp
    for k in range(1, nz - 1):
        a = k / (nz - 1)
        T[:, :, k] = (1 - a) * T[:, :, 0] + a * T[:, :, -1]

    # Precompute spacings as uniform
    dx = grid["Lx"] / max(1, nx - 1)
    dy = grid["Ly"] / max(1, ny - 1)
    dz = grid["total_thickness_m"] / max(1, nz - 1)

    inv_dx2 = 1.0 / (dx * dx)
    inv_dy2 = 1.0 / (dy * dy)
    inv_dz2 = 1.0 / (dz * dz)

    for _ in range(n_iter):
        T_new = T.copy()
        # Interior update
        T_new[1:-1, 1:-1, 1:-1] = (
            (
                k_field[2:, 1:-1, 1:-1] * T[2:, 1:-1, 1:-1]
                + k_field[:-2, 1:-1, 1:-1] * T[:-2, 1:-1, 1:-1]
            )
            * inv_dx2
            + (
                k_field[1:-1, 2:, 1:-1] * T[1:-1, 2:, 1:-1]
                + k_field[1:-1, :-2, 1:-1] * T[1:-1, :-2, 1:-1]
            )
            * inv_dy2
            + (
                k_field[1:-1, 1:-1, 2:] * T[1:-1, 1:-1, 2:]
                + k_field[1:-1, 1:-1, :-2] * T[1:-1, 1:-1, :-2]
            )
            * inv_dz2
            + q[1:-1, 1:-1, 1:-1]
        ) / (
            (k_field[2:, 1:-1, 1:-1] + k_field[:-2, 1:-1, 1:-1]) * inv_dx2
            + (k_field[1:-1, 2:, 1:-1] + k_field[1:-1, :-2, 1:-1]) * inv_dy2
            + (k_field[1:-1, 1:-1, 2:] + k_field[1:-1, 1:-1, :-2]) * inv_dz2
            + 1e-12
        )
        # Neumann zero-flux sides in x,y: copy neighbor
        T_new[0, :, :] = T_new[1, :, :]
        T_new[-1, :, :] = T_new[-2, :, :]
        T_new[:, 0, :] = T_new[:, 1, :]
        T_new[:, -1, :] = T_new[:, -2, :]
        # Dirichlet maintained at z boundaries
        T_new[:, :, 0] = params["fuel_inlet_T_K"]
        T_new[:, :, -1] = params["air_inlet_T_K"]
        T = T_new

    return T


def species_fields(params: Dict[str, float], grid: Dict[str, np.ndarray], j_xy: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # Simple plug-flow model along x and uniform across y,z in anode pores
    nx, ny = j_xy.shape
    nz = len(grid["z"])
    c_h2 = np.zeros((nx, ny, nz), dtype=np.float32)
    c_h2o = np.zeros_like(c_h2)

    # Assume standard conditions molar concentration at 1 atm ~ 40.9 mol/m^3 at 1000K (approx using ideal gas)
    # Use inlet temps to compute inlet total concentration
    T_in = max(300.0, params["fuel_inlet_T_K"])
    c_total = 101325.0 / (R * T_in)
    y_h2_in = 0.7  # assume fuel composition 70% H2
    y_h2o_in = 0.3
    c_h2_in = y_h2_in * c_total
    c_h2o_in = y_h2o_in * c_total

    # Consumption proportional to current via Faraday's law: j = n*F*r, n=2 for H2 -> r mol/m^2/s
    r_area = j_xy / (2.0 * F)
    # Convert to along-x depletion fraction scaled by flow (very simplified)
    flow = max(0.1, params["fuel_flow_sLpm"])  # standard L/min
    flow_m3s = flow * 1e-3 / 60.0  # m^3/s at STP approx
    A = grid["Lx"] * grid["Ly"]
    # Compute cumulative consumption along x proportionally
    cons_profile = np.cumsum(r_area.mean(axis=1)) * (grid["Ly"] / max(1, ny))  # mol/s per x-slice
    # Convert to concentration drop: dc = consumption/flow
    dc = cons_profile / max(1e-9, flow_m3s)

    dc = np.clip(dc, 0.0, 0.8 * c_h2_in)
    c_h2_x = np.clip(c_h2_in - dc, 1e-6, None)
    c_h2o_x = c_h2o_in + (c_h2_in - c_h2_x)

    # Fill in anode region only
    anode_mask_z = grid["anode_mask_z"]
    for ix in range(nx):
        c_h2[ix, :, anode_mask_z] = c_h2_x[ix]
        c_h2o[ix, :, anode_mask_z] = c_h2o_x[ix]

    return c_h2, c_h2o


def thermoelastic_stress(T: np.ndarray, grid: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Compute simple layer-wise in-plane stress due to thermal expansion mismatch
    E = grid["E_field"]
    nu = grid["nu_field"]
    alpha = grid["alpha_field"]
    T_ref = 973.15  # reference temperature

    eps_th = alpha * (T - T_ref)
    # Enforce in-plane compatibility by subtracting the z-slice average thermal strain
    eps_avg = eps_th.mean(axis=(0, 1), keepdims=True)
    # Plane stress approximation for thin layers
    sigma_xx = (E / (1 - nu**2)) * (eps_th - eps_avg)
    sigma_yy = (E / (1 - nu**2)) * (eps_th - eps_avg)
    sigma_zz = np.zeros_like(sigma_xx)
    tau_xy = np.zeros_like(sigma_xx)
    tau_xz = np.zeros_like(sigma_xx)
    tau_yz = np.zeros_like(sigma_xx)

    # Von Mises for plane stress
    von_mises = np.sqrt(
        sigma_xx**2 - sigma_xx * sigma_yy + sigma_yy**2 + 3 * tau_xy**2
    ).astype(np.float32)

    return (
        sigma_xx.astype(np.float32),
        sigma_yy.astype(np.float32),
        sigma_zz.astype(np.float32),
        tau_xy.astype(np.float32),
        tau_xz.astype(np.float32),
        tau_yz.astype(np.float32),
        von_mises,
    )


def approximate_displacement_z(T: np.ndarray, grid: Dict[str, np.ndarray]) -> np.ndarray:
    # Approximate out-of-plane displacement from cumulative thermal expansion along z
    alpha = grid["alpha_field"]
    dz = grid["total_thickness_m"] / max(1, T.shape[2] - 1)
    eps_th = alpha * (T - 973.15)
    # Integrate strain along z
    w = np.cumsum(eps_th[:, :, :], axis=2) * dz
    # Take the last plane as displacement
    uz = w[:, :, -1].astype(np.float32)
    return uz
