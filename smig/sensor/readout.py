"""
smig/sensor/readout.py
=======================
MULTIACCUM (up-the-ramp) readout simulator stub.

Leaf module — must not import any sibling sensor module, with one deliberate
exception: NonLinearityModel is injected by the orchestrator (H4RG10Detector)
so that nonlinearity can be applied per-read within the ramp.

ARCHITECTURAL NOTE — one-way dependency:
    readout.py → nonlinearity.py  (this file, intentional, temporary)
    nonlinearity.py → readout.py  (FORBIDDEN — must remain zero)

This exception exists because the signal chain requires NL to be applied
per-frame inside the ramp when 3D MULTIACCUM is implemented.  Once full ramp
physics lands, revisit whether the import should be replaced with a Protocol.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import ReadoutConfig
from smig.sensor.nonlinearity import NonLinearityModel


class MultiAccumSimulator:
    """MULTIACCUM (up-the-ramp) readout simulator.

    Builds a non-destructive read ramp from an accumulated charge image,
    simulating the H4RG-10's sample-up-the-ramp readout mode.  In production,
    returns a 3D array (n_reads, ny, nx); this stub returns a 2D array.

    NonLinearityModel is injected by the orchestrator so that it can be
    applied per-read in the future 3D ramp.  The stub applies it once to the
    2D accumulation image to keep the wiring live.

    Parameters
    ----------
    config:
        Readout sub-configuration extracted from DetectorConfig.
    dark_current_e_per_s:
        Dark current rate in electrons per second from ``ElectricalConfig``.
    read_noise_cds_electrons:
        Correlated double-sampling read noise in electrons from
        ``ElectricalConfig``.
    nonlinearity:
        Nonlinearity model injected by the orchestrator.  Applied once per
        2D accumulation in the stub; will be applied per-read in the 3D ramp.
    """

    def __init__(
        self,
        config: ReadoutConfig,
        dark_current_e_per_s: float,
        read_noise_cds_electrons: float,
        nonlinearity: NonLinearityModel | None = None,
    ) -> None:
        self._config = config
        self._dark_current_e_per_s = dark_current_e_per_s
        self._read_noise_cds_electrons = read_noise_cds_electrons
        self._nonlinearity = nonlinearity

    def simulate_ramp(self, image: np.ndarray) -> np.ndarray:
        """Simulate MULTIACCUM ramp readout of a charge image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of accumulated electron counts.

        Returns
        -------
        np.ndarray
            Stub: 2D array with nonlinearity applied once (production will
            return 3D (n_reads, ny, nx) with NL applied per-read).

        # TODO: Implement physical model — build up-the-ramp sample cube with
        # per-frame dark current accumulation, read noise, and reset pedestal.
        # Apply self._nonlinearity per frame rather than once on the 2D image.
        """
        # Apply nonlinearity once on the 2D accumulation image.
        # TEMPORARY: when the 3D ramp is implemented, replace with per-read
        # application inside the ramp loop.
        if self._nonlinearity is not None:
            return self._nonlinearity.apply(image)
        return image.copy()
