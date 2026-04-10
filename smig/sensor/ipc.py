"""
smig/sensor/ipc.py
==================
Field-dependent inter-pixel capacitance (IPC) convolution stub.

Leaf module — must not import any sibling sensor module.

## Kernel shape contract

A uniform kernel is shape ``(K, K)`` with ``K = config.ipc_kernel_size``.
A field-dependent kernel map has shape ``(ny, nx, K, K)`` or
``(n_tiles, K, K)`` with accompanying tile-centre coordinates.
The HDF5 loader (not yet implemented) will produce one of these two layouts;
``_validate_kernel_shape`` enforces the contract at load time.
"""

from __future__ import annotations

import numpy as np

from smig.config.schemas import IPCConfig


class FieldDependentIPC:
    """Field-dependent inter-pixel capacitance (IPC) convolution.

    Applies a spatially-varying IPC kernel to convert collected charge to
    electrically-sensed signal.  In production, loads a 9×9 kernel map from
    an HDF5 calibration file keyed by ``sca_id``; this stub is a no-op
    pass-through.

    Parameters
    ----------
    config:
        IPC sub-configuration extracted from DetectorConfig.
    sca_id:
        Science camera array identifier (1–18).  Used as the HDF5 dataset
        lookup key when ``config.ipc_kernel_path`` is provided.  The HDF5
        loader will be called here once implemented.
    field_position:
        ``(x, y)`` fractional position within the SCA focal plane
        (0.0–1.0 in each axis), used to select the local kernel from the
        field-dependent kernel map.
    """

    def __init__(
        self,
        config: IPCConfig,
        sca_id: int,
        field_position: tuple[float, float],
    ) -> None:
        self._config = config
        self._sca_id = sca_id
        self._field_position = field_position

    def _validate_kernel_shape(self, kernel: np.ndarray) -> None:
        """Validate that a loaded IPC kernel has an expected shape.

        Raises ``NotImplementedError`` until the HDF5 loader is implemented;
        when implemented it must raise ``ValueError`` for any shape that does
        not match the kernel-shape contract defined in the module docstring.

        Parameters
        ----------
        kernel:
            Kernel array returned by the HDF5 loader.

        Raises
        ------
        NotImplementedError
            Always, until the HDF5 loader and shape validation are implemented.
        """
        raise NotImplementedError(
            "_validate_kernel_shape is not yet implemented. "
            "Implement alongside the HDF5 kernel loader."
        )

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
        # HDF5 (keyed by self._sca_id) and apply via scipy.ndimage.convolve
        # or equivalent.  Call _validate_kernel_shape after loading.
        """
        return image.copy()
