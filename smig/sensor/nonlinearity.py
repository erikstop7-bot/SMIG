"""
smig/sensor/nonlinearity.py
============================
Polynomial detector nonlinearity model stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import NonlinearityConfig


class NonLinearityModel:
    """Polynomial detector nonlinearity model.

    Converts accumulated charge (in electrons) to measured signal using a
    polynomial transfer function applied to the normalized charge
    Q_norm = Q_electrons / full_well_electrons.

    This stub is a no-op pass-through.

    Parameters
    ----------
    config:
        Nonlinearity sub-configuration extracted from DetectorConfig.
    """

    def __init__(self, config: NonlinearityConfig) -> None:
        self._config = config

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply the nonlinearity polynomial to a charge image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of electron counts.

        Returns
        -------
        np.ndarray
            Nonlinearity-corrected image (stub: copy of input).

        # TODO: Implement physical model — evaluate polynomial
        # sum(coefficients[i] * Q_norm**i) and rescale back to electrons.
        """
        return image.copy()
