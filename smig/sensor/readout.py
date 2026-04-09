"""
smig/sensor/readout.py
=======================
MULTIACCUM (up-the-ramp) readout simulator stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import ReadoutConfig


class MultiAccumSimulator:
    """MULTIACCUM (up-the-ramp) readout simulator.

    Builds a non-destructive read ramp from an accumulated charge image,
    simulating the H4RG-10's sample-up-the-ramp readout mode.  In production,
    returns a 3D array (n_reads, ny, nx); this stub returns a 2D copy matching
    the input shape.

    Parameters
    ----------
    config:
        Readout sub-configuration extracted from DetectorConfig.
    """

    def __init__(self, config: ReadoutConfig) -> None:
        self._config = config

    def simulate_ramp(self, image: np.ndarray) -> np.ndarray:
        """Simulate MULTIACCUM ramp readout of a charge image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of accumulated electron counts.

        Returns
        -------
        np.ndarray
            Ramp output (stub: 2D copy of input; production returns 3D array
            of shape (n_reads, ny, nx)).

        # TODO: Implement physical model — build up-the-ramp sample cube with
        # per-frame dark current accumulation, read noise, and reset pedestal.
        """
        return image.copy()
