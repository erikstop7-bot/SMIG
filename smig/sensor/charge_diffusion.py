"""
smig/sensor/charge_diffusion.py
================================
Charge diffusion and brighter-fatter effect (BFE) stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import DetectorConfig


class ChargeDiffusionModel:
    """Charge diffusion and brighter-fatter effect (BFE) model.

    Models lateral charge migration in the HgCdTe detector layer and the
    signal-dependent PSF broadening (brighter-fatter effect).  Requires the
    full DetectorConfig because the BFE kernel depends on both geometry and
    electrical parameters.

    This stub is a no-op pass-through.

    Parameters
    ----------
    config:
        Full detector configuration.
    """

    def __init__(self, config: DetectorConfig) -> None:
        self._config = config

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply charge diffusion and BFE to a charge image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of electron counts.

        Returns
        -------
        np.ndarray
            Diffused image (stub: copy of input).

        # TODO: Implement physical model — Gaussian diffusion kernel +
        # signal-dependent BFE kernel from Antilogus et al. (2014).
        """
        return image.copy()
