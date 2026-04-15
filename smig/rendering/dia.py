"""
smig/rendering/dia.py
=====================
Difference Image Analysis (DIA) pipeline for SMIG v2 Phase 2.

Provides :class:`DIAPipeline`, which:

1. Builds a multi-epoch inverse-variance-weighted reference image from
   pre-rendered context stamps (``build_reference``).
2. Performs MVP Alard-Lupton kernel-basis image subtraction (``subtract``).
3. Extracts a science-size central crop from the difference image
   (``extract_stamp``).

Architecture boundary
---------------------
This module imports **only** from ``smig.config.schemas`` and
``smig.config.optics_schemas`` for config types.  No sensor-physics or
detector-pipeline modules from ``smig.sensor.*`` are imported.

Mixed-fidelity approximations (MVP)
------------------------------------
* Reference construction uses a **scalar variance** per epoch (read noise +
  dark + sky background).  Per-pixel Poisson variance from source photons is
  intentionally omitted for MVP speed.  MULTIACCUM covariance and IPC are
  also omitted.  This is a pragmatic mixed-fidelity approximation.
* Alard-Lupton subtraction uses **spatially constant** 3-Gaussian kernel
  basis; polynomial spatial variation is a future enhancement.
* A single additive background constant is fit; higher-order background
  polynomials are a future enhancement.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import convolve2d

from smig.config.optics_schemas import DIAConfig
from smig.config.schemas import DetectorConfig


class DIAPipeline:
    """MVP Difference Image Analysis pipeline.

    Parameters
    ----------
    config:
        DIA-specific configuration (stamp sizes, reference depth,
        subtraction method).
    detector_config:
        Phase 1 detector configuration.  Exposure time, read noise, and
        dark current are derived from this object — no hardcoded constants.
    rng:
        NumPy random Generator injected by the caller.  All stochastic
        operations (noise injection in ``build_reference``) use *this*
        generator exclusively.  The caller is responsible for seeding.
    """

    # Alard-Lupton basis: 3 Gaussian sigmas (pixels)
    _AL_SIGMAS: tuple[float, ...] = (1.0, 2.0, 4.0)

    def __init__(
        self,
        config: DIAConfig,
        detector_config: DetectorConfig,
        rng: np.random.Generator,
    ) -> None:
        self._config = config
        self._detector = detector_config
        self._rng = rng

        # Derived constants — all extracted from DetectorConfig, no hardcoding
        self._t_exp_s: float = (
            (detector_config.readout.n_ramp_reads - 1)
            * detector_config.readout.frame_time_s
        )
        self._read_noise_e: float = (
            detector_config.electrical.read_noise_cds_electrons
        )
        self._dark_e_per_s: float = (
            detector_config.electrical.dark_current_e_per_s
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_reference(
        self,
        ideal_electrons_epochs: list[np.ndarray],
        backgrounds_e_per_s: list[float],
    ) -> np.ndarray:
        """Inverse-variance weighted coadd of baseline epochs in rate space.

        Each epoch is independently noise-injected using a scalar per-epoch
        variance (read noise + dark + sky background).  Source Poisson noise
        is intentionally omitted (see module docstring).  The resulting noisy
        rate images are combined via strict inverse-variance weighting.

        Parameters
        ----------
        ideal_electrons_epochs:
            List of 2D arrays, each of shape
            ``(context_stamp_size, context_stamp_size)``, representing
            ideal (noiseless) rendered electrons for one reference epoch.
            An epoch-specific PSF may have been applied upstream before
            passing arrays here.
        backgrounds_e_per_s:
            Sky-background rate in electrons/s for each epoch.  Must have
            the same length as ``ideal_electrons_epochs``.

        Returns
        -------
        np.ndarray
            2D reference image in rate space (e⁻/s), dtype float64, shape
            ``(context_stamp_size, context_stamp_size)``.

        Raises
        ------
        ValueError
            If any input array is not 2D, has wrong shape, or if the list
            lengths do not match.
        """
        ctx = self._config.context_stamp_size
        expected_shape = (ctx, ctx)

        # --- Input validation ---
        if len(ideal_electrons_epochs) != len(backgrounds_e_per_s):
            raise ValueError(
                f"len(ideal_electrons_epochs)={len(ideal_electrons_epochs)} must "
                f"equal len(backgrounds_e_per_s)={len(backgrounds_e_per_s)}."
            )
        if len(ideal_electrons_epochs) == 0:
            raise ValueError("ideal_electrons_epochs must not be empty.")

        for i, arr in enumerate(ideal_electrons_epochs):
            if arr.ndim != 2:
                raise ValueError(
                    f"ideal_electrons_epochs[{i}] is {arr.ndim}D; expected 2D."
                )
            if arr.shape != expected_shape:
                raise ValueError(
                    f"ideal_electrons_epochs[{i}] has shape {arr.shape}; "
                    f"expected {expected_shape} (context_stamp_size={ctx})."
                )

        t = self._t_exp_s
        rn = self._read_noise_e
        dk = self._dark_e_per_s

        weighted_sum = np.zeros(expected_shape, dtype=np.float64)
        weight_total = 0.0

        for ideal_e, bg_e_per_s in zip(ideal_electrons_epochs, backgrounds_e_per_s):
            # Convert ideal electrons to rate space (e-/s)
            rate_image = ideal_e.astype(np.float64) / t + bg_e_per_s

            # Expected noise variance in electrons (scalar per epoch)
            # Omits source Poisson noise for MVP; see module docstring.
            var_e = rn**2 + (dk + bg_e_per_s) * t

            # Convert electron variance to rate-space variance
            variance_rate = var_e / (t**2)

            # Inject noise using only the injected RNG — never np.random global
            noise = self._rng.normal(
                0.0, np.sqrt(variance_rate), size=rate_image.shape
            )
            noisy_rate = rate_image + noise

            # Inverse-variance weight (scalar; same for all pixels in this epoch)
            weight = 1.0 / variance_rate

            weighted_sum += weight * noisy_rate
            weight_total += weight

        return (weighted_sum / weight_total).astype(np.float64)

    def subtract(
        self,
        science_rate_image: np.ndarray,
        reference_rate_image: np.ndarray,
    ) -> np.ndarray:
        """Alard-Lupton fixed-kernel convolution matching (MVP).

        Uses 3 spatially-constant Gaussian basis functions (σ = 1, 2, 4 px)
        plus an additive constant background term.  No polynomial spatial
        variation is implemented in this MVP.

        The reference image is convolved with each basis kernel to build a
        design matrix.  Least-squares coefficients are solved so that a linear
        combination of the convolved reference planes best matches the science
        image.  The difference (science − matched_reference) is returned.

        Parameters
        ----------
        science_rate_image:
            2D science image in rate space (e⁻/s).
        reference_rate_image:
            2D reference (template) image in rate space (e⁻/s).  Must have
            the same shape as ``science_rate_image``.

        Returns
        -------
        np.ndarray
            Difference image: ``science_rate_image − matched_reference``,
            same shape and dtype (float64) as inputs.

        Raises
        ------
        NotImplementedError
            If ``config.subtraction_method == 'sfft'``.
        ValueError
            If either input is not 2D, or shapes do not match.
        """
        if self._config.subtraction_method == "sfft":
            raise NotImplementedError(
                "SFFT subtraction is not yet implemented in this MVP. "
                "Set config.subtraction_method='alard_lupton'."
            )

        # --- Input validation ---
        if science_rate_image.ndim != 2:
            raise ValueError(
                f"science_rate_image must be 2D, got {science_rate_image.ndim}D."
            )
        if reference_rate_image.ndim != 2:
            raise ValueError(
                f"reference_rate_image must be 2D, got {reference_rate_image.ndim}D."
            )
        if science_rate_image.shape != reference_rate_image.shape:
            raise ValueError(
                f"science_rate_image.shape {science_rate_image.shape} must match "
                f"reference_rate_image.shape {reference_rate_image.shape}."
            )

        sci = science_rate_image.astype(np.float64)
        ref = reference_rate_image.astype(np.float64)

        # Kernel size: 2 * ceil(4 * sigma_max) + 1 = 33 px for sigma_max=4.0
        sigma_max = max(self._AL_SIGMAS)
        kernel_size = 2 * int(np.ceil(4.0 * sigma_max)) + 1

        # Convolve reference with each normalized Gaussian basis kernel
        convolved_planes: list[np.ndarray] = []
        for sigma in self._AL_SIGMAS:
            kernel = self._make_gaussian_kernel(sigma, kernel_size)
            conv = convolve2d(ref, kernel, mode="same", boundary="symm")
            convolved_planes.append(conv)

        ny, nx = sci.shape
        n_pixels = ny * nx

        # Design matrix A: [N_pixels, 4] — 3 basis convolutions + constant term
        A = np.empty((n_pixels, 4), dtype=np.float64)
        for k, plane in enumerate(convolved_planes):
            A[:, k] = plane.ravel()
        A[:, 3] = 1.0  # additive background constant

        b = sci.ravel()

        # Solve least squares: A @ coeffs ≈ b
        coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

        # Reconstruct matched reference from basis coefficients
        matched_ref = np.zeros((ny, nx), dtype=np.float64)
        for k, plane in enumerate(convolved_planes):
            matched_ref += coeffs[k] * plane
        matched_ref += coeffs[3]  # additive background constant term

        return sci - matched_ref

    def extract_stamp(self, difference_image: np.ndarray) -> np.ndarray:
        """Dynamic central crop to science_stamp_size.

        Crop boundaries are computed dynamically from config:
        center = context_stamp_size // 2, cropped symmetrically by
        science_stamp_size // 2 in each direction.

        Parameters
        ----------
        difference_image:
            2D difference image.  Both dimensions must be >=
            ``science_stamp_size``.  Typically of shape
            ``(context_stamp_size, context_stamp_size)``.

        Returns
        -------
        np.ndarray
            2D array of shape
            ``(science_stamp_size, science_stamp_size)``, dtype preserved.

        Raises
        ------
        ValueError
            If ``difference_image`` is not 2D or either dimension is smaller
            than ``science_stamp_size``.
        """
        sci_size = self._config.science_stamp_size
        ctx_size = self._config.context_stamp_size

        if difference_image.ndim != 2:
            raise ValueError(
                f"difference_image must be 2D, got {difference_image.ndim}D."
            )
        h, w = difference_image.shape
        if h < sci_size or w < sci_size:
            raise ValueError(
                f"difference_image shape {difference_image.shape} has a dimension "
                f"smaller than science_stamp_size={sci_size}."
            )

        # Dynamic crop: center on context_stamp_size // 2
        center = ctx_size // 2
        half = sci_size // 2
        row_start = center - half
        row_stop = center + half
        col_start = center - half
        col_stop = center + half

        return difference_image[row_start:row_stop, col_start:col_stop].copy()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_gaussian_kernel(sigma: float, size: int) -> np.ndarray:
        """Build a 2D Gaussian kernel, normalized so its sum equals 1.0.

        The kernel is centered on the middle pixel of a ``size × size`` grid.

        Parameters
        ----------
        sigma:
            Gaussian standard deviation in pixels.
        size:
            Side length of the square kernel (should be odd so the peak
            falls exactly on the centre pixel).

        Returns
        -------
        np.ndarray
            2D float64 array of shape ``(size, size)`` summing to 1.0.
        """
        half = size // 2
        # mgrid gives integer offsets from -half to +half inclusive
        y, x = np.mgrid[-half : half + 1, -half : half + 1]
        kernel = np.exp(-(x**2 + y**2) / (2.0 * sigma**2))
        kernel /= kernel.sum()
        return kernel
