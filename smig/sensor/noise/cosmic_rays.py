"""
smig/sensor/noise/cosmic_rays.py
=================================
Clustered cosmic-ray hit injector stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import DetectorConfig


class ClusteredCosmicRayInjector:
    """Clustered cosmic-ray hit injector.

    Simulates cosmic-ray strikes as spatially clustered charge deposits in the
    detector, with energies and morphologies drawn from empirical distributions.

    This stub is a no-op.

    Parameters
    ----------
    config:
        Full detector configuration (geometry and electrical parameters required).
    rng:
        NumPy random generator for reproducible noise realizations.
    """

    def __init__(self, config: DetectorConfig, rng: np.random.Generator) -> None:
        self._config = config
        self._rng = rng

    def apply(self, image: np.ndarray) -> tuple[np.ndarray, int]:
        """Inject cosmic-ray hits into an image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of electron counts.

        Returns
        -------
        tuple[np.ndarray, int]
            ``(modified_image, cosmic_ray_hit_count)``.
            Stub: returns ``(copy of input, 0)``.

        # TODO: Implement physical model — sample hit positions, energies, and
        # cluster morphologies from empirical distributions, then deposit charge.
        """
        return image.copy(), 0
