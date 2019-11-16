from typing import List

import numpy as np
from sympy.functions.elementary.trigonometric import cos
from sympy.functions.special.polynomials import legendre
from sympy.abc import theta, r
from sympy import lambdify, diff, Mul

from .calculate import distance, latitude, SATURN_RADIUS_KM
from .data_file import DataFile


def r_prefix(degree: int) -> Mul:
    return (degree + 1) * r ** -(degree + 2)


def theta_prefix(degree: int) -> Mul:
    return -(r ** -(degree + 2))


def phi_hat(r: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """The field strenth of the model phi component. Always returns zero."""
    return np.zeros_like(r)


class BFieldModel(object):
    """Model of a magnetic field strength based on an nth degree spherical
    harmonic expansion.

    Attributes
    ----------
    r_hat: vectorized function of r and theta
      The field strength of the r (range) component
    r_model: sympy function
      The symbolic representation of r_hat
    theta_hat: vectorized function of r and theta
      The field strength of the theta (co-latitude) component
    theta_model: sympy function
      The symbolic representation of r_hat
    phi_hat: vectorized function of r and theta
      The field strength of the phi component, always returns zero
    phi_model: sympy function
      The symbolic representation of r_hat
    """

    def __init__(self, gn0s: List[float]) -> None:
        """Arguments
        ---------
        gn0s: sequence of numbers
          the model coefficients to use, the length of gn0s determines
          the degree of the model constructed
        """

        self.gn0s = gn0s
        self.r_model = sum(
            [
                r_prefix(i + 1) * gn0s[i] * legendre(i + 1, cos(theta))
                for i, gn0 in enumerate(gn0s)
            ]
        )
        self.r_hat = lambdify([r, theta], self.r_model, "numpy")

        self.theta_model = sum(
            [
                theta_prefix(i + 1) * gn0s[i] * diff(legendre(i + 1, cos(theta)), theta)
                for i, gn0 in enumerate(gn0s)
            ]
        )
        self.theta_hat = lambdify([r, theta], self.theta_model, "numpy")

        self.phi_hat = phi_hat

    @property
    def degree(self) -> int:
        return len(self.gn0s)

    def process_datafile(self, df: DataFile):
        """Return the three field components (r^hat, theta^hat and phi^hat respectively)
        calculated from the positions stored in the Magda DataFile ``df``."""
        xyz = df["X_KG"].data, df["Y_KG"].data, df["Z_KG"].data
        r = distance(*xyz, radius=SATURN_RADIUS_KM)
        lat = latitude(*xyz)
        theta = (90.0 - lat) / 180 * np.pi

        return self.r_hat(r, theta), self.theta_hat(r, theta), self.phi_hat(r, theta)
