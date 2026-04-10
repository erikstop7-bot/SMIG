"""
smig/sensor/nonlinearity.py
============================
Polynomial detector nonlinearity model.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import NonlinearityConfig


class NonLinearityModel:
    """Polynomial detector nonlinearity model.

    Converts accumulated charge Q (electrons) to a measured signal by
    evaluating a polynomial transfer function in normalised charge::

        Q_norm = Q / Q_FW
        S_measured = c_0 + c_1*Q_norm + c_2*Q_norm**2 + ...
        output = Q * S_measured

    ``S_measured`` is a dimensionless multiplicative factor (≈ 1 at low
    signal).  Negative higher-order coefficients encode the detector's
    sublinearity (measured response falls below ideal at high charge).

    After the polynomial is evaluated, any pixel whose output would
    exceed ``saturation_flag_threshold * full_well_electrons`` is
    hard-clipped to that level.  Hard clipping here combined with
    saturation-read exclusion in the OLS slope fit is the intended design.

    Parameters
    ----------
    config:
        Nonlinearity sub-configuration extracted from DetectorConfig.
    full_well_electrons:
        Full-well capacity in electrons from ``ElectricalConfig``.  Passed
        explicitly so this module receives only the scalar it needs.
    """

    def __init__(self, config: NonlinearityConfig, full_well_electrons: float) -> None:
        self._config = config
        self._full_well_electrons = full_well_electrons
        # Pre-compute saturation clip level (electrons).
        self._Q_sat: float = config.saturation_flag_threshold * full_well_electrons

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply the polynomial nonlinearity transfer function.

        Parameters
        ----------
        image:
            Array of accumulated electron counts (any shape; typically
            2D ``(ny, nx)``).  Input is not modified.

        Returns
        -------
        np.ndarray
            Nonlinearity-corrected signal in electrons, same shape and
            dtype float64.  Pixels at or above the saturation threshold
            are clipped to ``saturation_flag_threshold * full_well_electrons``.
        """
        Q_FW = self._full_well_electrons
        coefficients = self._config.coefficients  # ascending-order tuple

        # Normalised charge.  Division is safe: Q_FW > 0 enforced by schema.
        Q_norm = image / Q_FW

        # Polynomial response factor S_measured using Horner's method via
        # np.polynomial.polynomial.polyval (ascending-order coefficients).
        S_measured = np.polynomial.polynomial.polyval(Q_norm, coefficients)

        # Measured signal = physical charge * response factor.
        output = image * S_measured

        # Hard saturation clip; in-place to avoid an extra allocation.
        np.clip(output, 0.0, self._Q_sat, out=output)

        return output
