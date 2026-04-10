"""
smig/sensor/charge_diffusion.py
================================
Charge diffusion and brighter-fatter effect (BFE) stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import ChargeDiffusionConfig


class ChargeDiffusionModel:
    """Charge diffusion and brighter-fatter effect (BFE) model.

    Models lateral charge migration in the HgCdTe detector layer and the
    signal-dependent PSF broadening (brighter-fatter effect).

    Static diffusion is applied via a fixed Gaussian kernel computed from
    ``config.pixel_pitch_um``.  BFE is applied as a signal-dependent
    perturbation kernel using only the *current* accumulated charge in
    ``image`` (per-ramp-read application is out of scope for this stub;
    revisit when MULTIACCUM is implemented).

    This stub is a no-op pass-through.

    Parameters
    ----------
    config:
        Charge diffusion sub-configuration built by the orchestrator from
        ``DetectorConfig.geometry.pixel_pitch_um`` and
        ``DetectorConfig.electrical.full_well_electrons``.
    """

    def __init__(self, config: ChargeDiffusionConfig) -> None:
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
