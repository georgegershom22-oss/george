from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .config import FARADAY_CONSTANT, GAS_CONSTANT, LayerNames


@dataclass
class SolverGrid:
    nx: int
    ny: int
    nz: int
    dx: float
    dy: float
    dz: float


def _harmonic_mean(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (2.0 * a * b) / (a + b + 1e-30)


def _build_div_sigma_grad_matrix(sigma: np.ndarray, g: SolverGrid, dirichlet_mask: np.ndarray) -> sp.csr_matrix:
    """Construct sparse matrix for div(sigma grad u) with 7-point stencil and variable coefficients.

    Dirichlet nodes are handled by setting a 1 on the diagonal and zero elsewhere for those rows.
    """
    nx, ny, nz = g.nx, g.ny, g.nz
    N = nx * ny * nz

    # Precompute face conductivities using harmonic means
    # X faces: between i and i+1 at half-grid x
    sigma_x = _harmonic_mean(sigma[1:, :, :], sigma[:-1, :, :])  # shape (nx-1, ny, nz)
    sigma_y = _harmonic_mean(sigma[:, 1:, :], sigma[:, :-1, :])  # shape (nx, ny-1, nz)
    sigma_z = _harmonic_mean(sigma[:, :, 1:], sigma[:, :, :-1])  # shape (nx, ny, nz-1)

    dx2 = g.dx * g.dx
    dy2 = g.dy * g.dy
    dz2 = g.dz * g.dz

    rows = []
    cols = []
    vals = []

    def idx(i: int, j: int, k: int) -> int:
        return (k * ny + j) * nx + i

    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                p = idx(i, j, k)
                if dirichlet_mask[i, j, k]:
                    rows.append(p); cols.append(p); vals.append(1.0)
                    continue

                diag = 0.0
                # X- neighbors
                if i > 0:
                    s = sigma_x[i-1, j, k] / dx2
                    rows.append(p); cols.append(idx(i-1, j, k)); vals.append(-s)
                    diag += s
                if i < nx - 1:
                    s = sigma_x[i, j, k] / dx2
                    rows.append(p); cols.append(idx(i+1, j, k)); vals.append(-s)
                    diag += s
                # Y- neighbors
                if j > 0:
                    s = sigma_y[i, j-1, k] / dy2
                    rows.append(p); cols.append(idx(i, j-1, k)); vals.append(-s)
                    diag += s
                if j < ny - 1:
                    s = sigma_y[i, j, k] / dy2
                    rows.append(p); cols.append(idx(i, j+1, k)); vals.append(-s)
                    diag += s
                # Z- neighbors
                if k > 0:
                    s = sigma_z[i, j, k-1] / dz2
                    rows.append(p); cols.append(idx(i, j, k-1)); vals.append(-s)
                    diag += s
                if k < nz - 1:
                    s = sigma_z[i, j, k] / dz2
                    rows.append(p); cols.append(idx(i, j, k+1)); vals.append(-s)
                    diag += s

                rows.append(p); cols.append(p); vals.append(diag)

    A = sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
    return A


def solve_potential(phi_dirichlet: Dict[str, Tuple[np.ndarray, float]], sigma_total: np.ndarray, g: SolverGrid) -> np.ndarray:
    """Solve div(sigma grad phi) = 0 with Dirichlet BC on specified masks.

    phi_dirichlet: mapping of name -> (mask, value)
    """
    nx, ny, nz = g.nx, g.ny, g.nz
    dirichlet_mask = np.zeros((nx, ny, nz), dtype=bool)
    phi_bc = np.zeros((nx, ny, nz), dtype=np.float64)
    for _name, (mask, value) in phi_dirichlet.items():
        dirichlet_mask |= mask
        phi_bc[mask] = value

    A = _build_div_sigma_grad_matrix(sigma_total, g, dirichlet_mask)
    b = np.zeros(A.shape[0], dtype=np.float64)

    # Impose Dirichlet by setting RHS to value at those rows
    # Since rows were set to identity in matrix builder, we simply set b to phi_bc
    b[dirichlet_mask.ravel(order="C")] = phi_bc.ravel(order="C")[dirichlet_mask.ravel(order="C")]

    phi_vec = spla.spsolve(A, b)
    phi = phi_vec.reshape((nx, ny, nz), order="C")
    return phi.astype(np.float32)


def compute_current_density(phi: np.ndarray, sigma: np.ndarray, g: SolverGrid) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute current density vector j = -sigma grad(phi) and its magnitude."""
    dphidx = np.zeros_like(phi, dtype=np.float32)
    dphidy = np.zeros_like(phi, dtype=np.float32)
    dphidz = np.zeros_like(phi, dtype=np.float32)

    # central differences interior, one-sided at boundaries
    dphidx[1:-1, :, :] = (phi[2:, :, :] - phi[:-2, :, :]) / (2.0 * g.dx)
    dphidx[0, :, :] = (phi[1, :, :] - phi[0, :, :]) / g.dx
    dphidx[-1, :, :] = (phi[-1, :, :] - phi[-2, :, :]) / g.dx

    dphidy[:, 1:-1, :] = (phi[:, 2:, :] - phi[:, :-2, :]) / (2.0 * g.dy)
    dphidy[:, 0, :] = (phi[:, 1, :] - phi[:, 0, :]) / g.dy
    dphidy[:, -1, :] = (phi[:, -1, :] - phi[:, -2, :]) / g.dy

    dphidz[:, :, 1:-1] = (phi[:, :, 2:] - phi[:, :, :-2]) / (2.0 * g.dz)
    dphidz[:, :, 0] = (phi[:, :, 1] - phi[:, :, 0]) / g.dz
    dphidz[:, :, -1] = (phi[:, :, -1] - phi[:, :, -2]) / g.dz

    jx = -sigma * dphidx
    jy = -sigma * dphidy
    jz = -sigma * dphidz

    jmag = np.sqrt(jx * jx + jy * jy + jz * jz, dtype=np.float32)
    return jx.astype(np.float32), jy.astype(np.float32), jz.astype(np.float32), jmag.astype(np.float32)


def overpotential_from_current(jmag: np.ndarray, j0: np.ndarray, T: float, alpha: float = 0.5) -> np.ndarray:
    """Compute overpotential using inverse Butler-Volmer: eta = (R T / (alpha F)) asinh(j/(2 j0))."""
    j0_safe = np.maximum(j0, 1e-6)
    eta = (GAS_CONSTANT * T) / (alpha * FARADAY_CONSTANT) * np.arcsinh(0.5 * jmag / j0_safe)
    return eta.astype(np.float32)


def solve_heat(k_th: np.ndarray, q_vol: np.ndarray, g: SolverGrid, T_dirichlet: Dict[str, Tuple[np.ndarray, float]]) -> np.ndarray:
    """Solve div(k grad T) + q = 0 with Dirichlet boundary conditions."""
    nx, ny, nz = g.nx, g.ny, g.nz

    dirichlet_mask = np.zeros((nx, ny, nz), dtype=bool)
    T_bc = np.zeros((nx, ny, nz), dtype=np.float64)
    for _name, (mask, value) in T_dirichlet.items():
        dirichlet_mask |= mask
        T_bc[mask] = value

    A = _build_div_sigma_grad_matrix(k_th, g, dirichlet_mask)

    b = -q_vol.ravel(order="C").astype(np.float64)
    b[dirichlet_mask.ravel(order="C")] = T_bc.ravel(order="C")[dirichlet_mask.ravel(order="C")]

    T_vec = spla.spsolve(A, b)
    T = T_vec.reshape((nx, ny, nz), order="C")
    return T.astype(np.float32)


def compute_species_fields(
    jmag: np.ndarray,
    anode_mask: np.ndarray,
    fuel_flow_rate_m3_per_s: float,
    porosity: np.ndarray,
    g: SolverGrid,
    c_h2_in: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute H2 and H2O fields with a simplified linewise mass balance along x direction.

    For each (y,z) within the anode, update c[i+1] = c[i] - k * j[i] * dx.
    The proportionality constant aggregates velocity and Faraday terms.
    Output concentrations are dimensionless (normalized to inlet mol fraction).
    """
    nx, ny, nz = jmag.shape

    # Effective cross-section at each x slice for anode flow (sum porosity over anode voxels in that slice)
    porosity_slice = porosity.copy()
    porosity_slice[~anode_mask] = 0.0
    A_eff = np.maximum(np.sum(porosity_slice, axis=(1, 2)) * g.dy * g.dz, 1e-12)

    # Superficial velocity u = Q / A_eff(x)
    u = fuel_flow_rate_m3_per_s / A_eff  # shape (nx,)

    # Aggregated proportionality constant for consumption
    # k_consume ~ (1 / (u * F)) scaled to keep values reasonable numerically
    k_line = (g.dx / (np.maximum(u, 1e-9) * FARADAY_CONSTANT))
    # normalize to practical range
    k_line = np.clip(k_line, 0.0, np.percentile(k_line, 95))

    c_h2 = np.full((nx, ny, nz), c_h2_in, dtype=np.float32)
    c_h2o = np.zeros((nx, ny, nz), dtype=np.float32)

    # Iterate along x for each (y,z)
    for i in range(nx - 1):
        # average current in slice i across anode voxels
        j_slice = jmag[i, :, :] * anode_mask[i, :, :]
        j_avg = np.mean(j_slice[j_slice > 0.0]) if np.any(j_slice > 0.0) else 0.0
        dc = k_line[i] * j_avg
        if dc == 0.0:
            continue
        # update only inside anode
        c_next = c_h2[i, :, :] - dc
        c_next = np.clip(c_next, 0.0, c_h2_in)
        c_h2[i + 1, :, :] = np.where(anode_mask[i + 1, :, :], c_next, c_h2[i + 1, :, :])

    # H2O production mirrors H2 consumption (dimensionless scaling)
    c_h2o = (c_h2_in - c_h2) * anode_mask.astype(np.float32)

    # Extend to non-anode regions with simple diffusion from boundaries (smooth)
    # Here we just fill non-anode with nearest anode values along z to keep full 3D fields
    for k in range(nz):
        for j in range(ny):
            line = anode_mask[:, j, k]
            if not np.any(line):
                continue
            idxs = np.where(line)[0]
            i_min, i_max = int(idxs.min()), int(idxs.max())
            c_h2[:i_min, j, k] = c_h2[i_min, j, k]
            c_h2[i_max + 1:, j, k] = c_h2[i_max, j, k]
            c_h2o[:i_min, j, k] = c_h2o[i_min, j, k]
            c_h2o[i_max + 1:, j, k] = c_h2o[i_max, j, k]

    return c_h2.astype(np.float32), c_h2o.astype(np.float32)


def compute_thermo_mechanics(
    T: np.ndarray,
    E: np.ndarray,
    nu: np.ndarray,
    alpha: np.ndarray,
    T_ref: float = 1073.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Approximate thermoelastic stress/strain and displacement.

    Stress magnitude approximation: sigma_vm ~ kappa * E * alpha * |T - T_ref| / (1 - nu)
    Strain equivalent: eps_eq ~ alpha * (T - T_ref)
    Displacement is a heuristic mapping of temperature gradients to a plausible field.
    """
    dT = (T - T_ref).astype(np.float32)
    eps_eq = alpha * dT

    # avoid unphysically large stresses by limiting amplification
    kappa = 0.35
    denom = np.maximum(1.0 - nu, 0.1)
    sigma_vm = kappa * E * alpha * np.abs(dT) / denom

    # Construct a smooth displacement field informed by temperature gradients
    # u_z primarily from through-thickness expansion; u_x, u_y from in-plane gradients
    # Scale factors chosen for numerical plausibility
    grad_x = np.zeros_like(T, dtype=np.float32)
    grad_y = np.zeros_like(T, dtype=np.float32)
    grad_z = np.zeros_like(T, dtype=np.float32)

    grad_x[1:-1, :, :] = (T[2:, :, :] - T[:-2, :, :]) * 0.5
    grad_x[0, :, :] = T[1, :, :] - T[0, :, :]
    grad_x[-1, :, :] = T[-1, :, :] - T[-2, :, :]

    grad_y[:, 1:-1, :] = (T[:, 2:, :] - T[:, :-2, :]) * 0.5
    grad_y[:, 0, :] = T[:, 1, :] - T[:, 0, :]
    grad_y[:, -1, :] = T[:, -1, :] - T[:, -2, :]

    grad_z[:, :, 1:-1] = (T[:, :, 2:] - T[:, :, :-2]) * 0.5
    grad_z[:, :, 0] = T[:, :, 1] - T[:, :, 0]
    grad_z[:, :, -1] = T[:, :, -1] - T[:, :, -2]

    c_u = 1e-9  # overall scale to keep displacements small (meters)
    ux = -c_u * alpha * grad_x
    uy = -c_u * alpha * grad_y
    uz = c_u * alpha * dT

    return sigma_vm.astype(np.float32), eps_eq.astype(np.float32), ux.astype(np.float32), uy.astype(np.float32), uz.astype(np.float32)
