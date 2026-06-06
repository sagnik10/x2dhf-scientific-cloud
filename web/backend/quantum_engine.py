import math
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.sparse import diags, eye, kron
from scipy.sparse.linalg import eigsh

warnings.filterwarnings("ignore")


@dataclass
class FiniteDifferenceGrid:
    """Uniform Dirichlet finite-difference grid."""

    points: int = 301
    extent: float = 35.0

    def axis(self) -> Tuple[np.ndarray, float]:
        points = max(int(self.points), 25)
        extent = max(float(self.extent), 4.0)
        axis = np.linspace(-extent, extent, points + 2)[1:-1]
        return axis, float(axis[1] - axis[0])

    def radial_axis(self) -> Tuple[np.ndarray, float]:
        points = max(int(self.points), 101)
        extent = max(float(self.extent), 20.0)
        axis = np.linspace(0.0, extent, points + 2)[1:-1]
        return axis, float(axis[1] - axis[0])


class QuantumComputationEngine:
    """
    Finite-difference one-electron Schrodinger solver.

    This compatibility class intentionally does not use Gaussian or other finite
    basis functions. Atomic one-electron systems are solved on a radial grid for
    the reduced wavefunction u(r). Diatomic one-electron systems are solved on a
    3D Cartesian finite-difference grid with sparse eigensolver diagonalization.
    """

    def __init__(
        self,
        geometry: np.ndarray,
        nuclear_charges: np.ndarray,
        basis_functions: Optional[List[object]] = None,
        grid_points: int = 301,
        grid_extent: float = 35.0,
    ):
        self.geometry = np.asarray(geometry, dtype=float)
        self.nuclear_charges = np.asarray(nuclear_charges, dtype=float)
        self.grid = FiniteDifferenceGrid(grid_points, grid_extent)
        self.converged = False
        self.iteration_history: List[Dict] = []
        self.basis = []
        self.nbasis = 0
        if basis_functions:
            warnings.warn(
                "basis_functions is ignored; QuantumComputationEngine now uses finite differences.",
                RuntimeWarning,
                stacklevel=2,
            )

    def _nuclear_repulsion(self) -> float:
        energy = 0.0
        for i in range(len(self.nuclear_charges)):
            for j in range(i + 1, len(self.nuclear_charges)):
                distance = np.linalg.norm(self.geometry[i] - self.geometry[j])
                if distance > 1e-12:
                    energy += self.nuclear_charges[i] * self.nuclear_charges[j] / distance
        return float(energy)

    def _solve_atomic(self) -> Dict:
        charge = float(self.nuclear_charges[0])
        r, dr = self.grid.radial_axis()
        n = len(r)
        main = np.full(n, 1.0 / dr**2) - charge / np.maximum(r, 1e-8)
        off = np.full(n - 1, -0.5 / dr**2)
        hamiltonian = diags([off, main, off], [-1, 0, 1], format="csr")
        values, vectors = eigsh(hamiltonian, k=1, which="SA", tol=1e-10, maxiter=n * 20)
        index = int(np.argmin(values))
        energy = float(values[index])
        residual = hamiltonian.dot(vectors[:, index]) - energy * vectors[:, index]
        self.converged = True
        self.iteration_history = [{"iteration": 1, "energy": energy, "residual_norm": float(np.linalg.norm(residual))}]
        return {
            "electronic_energy": energy,
            "final_energy": energy,
            "kinetic_energy": None,
            "potential_energy": None,
            "nuclear_repulsion_energy": 0.0,
            "orbital_energies": [energy],
            "residual_norm": float(np.linalg.norm(residual)),
            "grid": {"dimensions": 1, "points": n, "spacing": dr, "extent": self.grid.extent},
        }

    def _solve_diatomic(self) -> Dict:
        points = min(max(int(self.grid.points), 25), 45)
        distance = float(np.linalg.norm(self.geometry[0] - self.geometry[1]))
        half_box = max(min(float(self.grid.extent), 24.0), distance * 0.5 + 8.0)
        axis, h = FiniteDifferenceGrid(points, half_box).axis()
        lap1 = diags([np.ones(points - 1), -2.0 * np.ones(points), np.ones(points - 1)], [-1, 0, 1], format="csr") / (h * h)
        ident = eye(points, format="csr")
        laplacian = kron(kron(lap1, ident), ident) + kron(kron(ident, lap1), ident) + kron(kron(ident, ident), lap1)

        x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
        potential = np.zeros_like(x)
        softening = 0.35 * h
        for charge, center in zip(self.nuclear_charges, self.geometry):
            dx = x - center[0]
            dy = y - center[1]
            dz = z - center[2]
            potential -= charge / np.sqrt(dx * dx + dy * dy + dz * dz + softening * softening)

        hamiltonian = (-0.5 * laplacian) + diags(potential.ravel(), 0, format="csr")
        values, vectors = eigsh(hamiltonian, k=1, which="SA", tol=1e-8, maxiter=1200)
        index = int(np.argmin(values))
        electronic = float(values[index])
        nuclear = self._nuclear_repulsion()
        residual = hamiltonian.dot(vectors[:, index]) - electronic * vectors[:, index]
        self.converged = True
        self.iteration_history = [{"iteration": 1, "energy": electronic + nuclear, "residual_norm": float(np.linalg.norm(residual))}]
        return {
            "electronic_energy": electronic,
            "final_energy": electronic + nuclear,
            "kinetic_energy": None,
            "potential_energy": None,
            "nuclear_repulsion_energy": nuclear,
            "orbital_energies": [electronic],
            "residual_norm": float(np.linalg.norm(residual)),
            "grid": {"dimensions": 3, "points": points, "spacing": h, "extent": half_box},
        }

    def solve_schrodinger(self, n_electrons: int = 1) -> Dict:
        if int(n_electrons) != 1:
            raise NotImplementedError("The Python finite-difference engine currently solves one-electron systems. Use native X2DHF for HF/DFT many-electron jobs.")
        if len(self.nuclear_charges) == 1 or np.count_nonzero(np.abs(self.nuclear_charges) > 1e-12) == 1:
            return self._solve_atomic()
        if len(self.nuclear_charges) == 2:
            return self._solve_diatomic()
        raise NotImplementedError("Only one-electron atomic and diatomic finite-difference systems are supported.")

    def run_hartree_fock(self, n_electrons: int) -> Dict:
        result = self.solve_schrodinger(n_electrons)
        return {
            "converged": self.converged,
            "final_energy": float(result["final_energy"]),
            "iterations": len(self.iteration_history),
            "orbital_energies": result["orbital_energies"],
            "orbitals": None,
            "iteration_history": self.iteration_history,
            "grid": result["grid"],
        }

    def run_dft(self, n_electrons: int, functional: str = "LDA") -> Dict:
        result = self.solve_schrodinger(n_electrons)
        return {
            "converged": self.converged,
            "final_energy": float(result["final_energy"]),
            "iterations": len(self.iteration_history),
            "functional": functional,
            "orbitals": None,
            "orbital_energies": result["orbital_energies"],
            "iteration_history": self.iteration_history,
            "grid": result["grid"],
        }

    def compute_total_energy(self, _orbitals=None, n_electrons: int = 1) -> float:
        return float(self.solve_schrodinger(n_electrons)["final_energy"])


class GaussianBasisFunction:
    """Deprecated compatibility stub; finite-difference grids replace basis functions."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError("GaussianBasisFunction has been removed. Use QuantumComputationEngine with finite-difference grid settings.")
