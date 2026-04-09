"""
smig/sensor/ipc.py
==================
Field-dependent inter-pixel capacitance (IPC) convolution stub.

Leaf module — must not import any sibling sensor module.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import IPCConfig


class FieldDependentIPC:
    """Field-dependent inter-pixel capacitance (IPC) convolution.

    Applies a spatially-varying IPC kernel to convert collected charge to
    electrically-sensed signal.  In production, loads a 9×9 kernel map from
    an HDF5 calibration file; this stub is a no-op pass-through.

    Parameters
    ----------
    config:
        IPC sub-configuration extracted from DetectorConfig.
    """

    def __init__(self, config: IPCConfig) -> None:
        self._config = config

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply IPC convolution to a charge image.

        Parameters
        ----------
        image:
            2D array (ny, nx) of electron counts.

        Returns
        -------
        np.ndarray
            IPC-convolved image (stub: copy of input).

        # TODO: Implement physical model — load 9×9 field-varying kernel from
        # HDF5 and apply via scipy.ndimage.convolve or equivalent.
        """
        return image.copy()
