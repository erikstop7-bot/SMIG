"""
smig/sensor/persistence.py
===========================
Two-component exponential persistence (residual image) model stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import PersistenceConfig


class DynamicPersistence:
    """Two-component exponential persistence (residual image) model.

    Tracks trapped charge from previous epochs and injects a persistence signal
    into subsequent frames.  The decay follows::

        P(t) = amp_short * exp(-t / tau_short_s)
               + amp_long  * exp(-t / tau_long_s)

    This stub is a no-op pass-through.

    Parameters
    ----------
    config:
        Persistence sub-configuration extracted from DetectorConfig.
    """

    def __init__(self, config: PersistenceConfig) -> None:
        self._config = config

    def apply(self, image: np.ndarray, delta_time_s: float = 0.0) -> np.ndarray:
        """Apply persistence injection to a charge image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of electron counts.
        delta_time_s:
            Time elapsed since the previous epoch in seconds.  Used to compute
            the exponential decay of trapped charge from prior saturation events.

        Returns
        -------
        np.ndarray
            Image with persistence signal added (stub: copy of input).

        # TODO: Implement physical model — two-component exponential decay from
        # a running per-pixel trap-state map updated after each epoch.
        """
        return image.copy()
