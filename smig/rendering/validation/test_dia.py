"""
smig/rendering/validation/test_dia.py
======================================
Acceptance tests for :class:`~smig.rendering.dia.DIAPipeline`.

Coverage
--------
AC-D1  build_reference returns 2D float64 array of shape (context_stamp_size, context_stamp_size).
AC-D2  Determinism: two identically-seeded Generators yield bit-identical build_reference + subtract output.
AC-D3  Static field: difference image residuals satisfy |mean| < 3*std/sqrt(N).
AC-D4  Point source: AL subtraction recovers injected flux within 10%.
AC-D5  SFFT raises NotImplementedError.
AC-D6  extract_stamp returns correct shape for default config.
AC-D7  extract_stamp dynamically scales to arbitrary config inputs.
AC-D8  Input validation — build_reference: shape mismatch, length mismatch, wrong ndim.
AC-D9  Input validation — subtract: non-2D input, shape mismatch.
AC-D10 Input validation — extract_stamp: non-2D input, dimensions too small.

Run from the SMIG project root::

    python -m pytest smig/rendering/validation/test_dia.py -v
"""
from __future__ import annotations

import numpy as np
import pytest

from smig.config.optics_schemas import DIAConfig
from smig.config.schemas import DetectorConfig
from smig.rendering.dia import DIAPipeline


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def detector() -> DetectorConfig:
    """Default Phase 1 detector configuration."""
    return DetectorConfig()


@pytest.fixture()
def dia_config() -> DIAConfig:
    """Small stamp sizes for fast unit tests."""
    return DIAConfig(
        context_stamp_size=64,
        science_stamp_size=32,
        n_reference_epochs=5,
        subtraction_method="alard_lupton",
    )


@pytest.fixture()
def rng() -> np.random.Generator:
    return np.random.default_rng(42)


@pytest.fixture()
def pipeline(dia_config: DIAConfig, detector: DetectorConfig, rng: np.random.Generator) -> DIAPipeline:
    return DIAPipeline(config=dia_config, detector_config=detector, rng=rng)


def _make_flat_epochs(
    n: int, ctx: int, electrons: float = 5000.0
) -> list[np.ndarray]:
    """Return a list of *n* identical flat (uniform) context images."""
    return [np.full((ctx, ctx), electrons, dtype=np.float64) for _ in range(n)]


def _make_backgrounds(n: int, bg: float = 1.0) -> list[float]:
    return [bg] * n


# ---------------------------------------------------------------------------
# AC-D1: Output shape and dtype
# ---------------------------------------------------------------------------

class TestBuildReferenceShape:
    def test_output_shape(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        epochs = _make_flat_epochs(3, ctx)
        bgs = _make_backgrounds(3)

        ref = pipeline.build_reference(epochs, bgs)

        assert ref.ndim == 2, "Reference must be 2D"
        assert ref.shape == (ctx, ctx), f"Expected ({ctx},{ctx}), got {ref.shape}"
        assert ref.dtype == np.float64, f"Expected float64, got {ref.dtype}"


# ---------------------------------------------------------------------------
# AC-D2: Determinism — bit-identical outputs from identically-seeded RNGs
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_build_reference_deterministic(
        self, dia_config: DIAConfig, detector: DetectorConfig
    ) -> None:
        ctx = dia_config.context_stamp_size
        epochs = _make_flat_epochs(4, ctx, electrons=8000.0)
        bgs = _make_backgrounds(4, bg=2.0)

        rng_a = np.random.default_rng(99)
        rng_b = np.random.default_rng(99)

        ref_a = DIAPipeline(dia_config, detector, rng_a).build_reference(epochs, bgs)
        ref_b = DIAPipeline(dia_config, detector, rng_b).build_reference(epochs, bgs)

        np.testing.assert_array_equal(
            ref_a,
            ref_b,
            err_msg="build_reference must be bit-identical for equal seeds",
        )

    def test_subtract_deterministic(
        self, dia_config: DIAConfig, detector: DetectorConfig
    ) -> None:
        ctx = dia_config.context_stamp_size
        rng_a = np.random.default_rng(7)
        rng_b = np.random.default_rng(7)

        epochs = _make_flat_epochs(3, ctx)
        bgs = _make_backgrounds(3)

        pipe_a = DIAPipeline(dia_config, detector, rng_a)
        pipe_b = DIAPipeline(dia_config, detector, rng_b)

        ref_a = pipe_a.build_reference(epochs, bgs)
        ref_b = pipe_b.build_reference(epochs, bgs)

        # Identical science images for both pipelines
        sci = np.full((ctx, ctx), 110.0, dtype=np.float64)

        diff_a = pipe_a.subtract(sci, ref_a)
        diff_b = pipe_b.subtract(sci, ref_b)

        np.testing.assert_array_equal(
            diff_a,
            diff_b,
            err_msg="subtract must be bit-identical for equal seeds",
        )


# ---------------------------------------------------------------------------
# AC-D3: Static field — difference image residuals consistent with noise
# ---------------------------------------------------------------------------

class TestStaticFieldResiduals:
    def test_residuals_within_noise(
        self, detector: DetectorConfig
    ) -> None:
        """For a static (no-source) field the mean residual << noise std.

        Criterion: |mean(residuals)| < 3 * std(residuals) / sqrt(N)
        (i.e., the mean is not significantly non-zero).
        """
        ctx = 64
        n_ref = 20
        dia_cfg = DIAConfig(
            context_stamp_size=ctx,
            science_stamp_size=32,
            n_reference_epochs=n_ref,
            subtraction_method="alard_lupton",
        )
        rng = np.random.default_rng(2024)
        pipe = DIAPipeline(dia_cfg, detector, rng)

        bg_e_per_s = 3.0
        ideal_e = 4000.0
        epochs = _make_flat_epochs(n_ref, ctx, electrons=ideal_e)
        bgs = _make_backgrounds(n_ref, bg=bg_e_per_s)

        ref = pipe.build_reference(epochs, bgs)

        # Science image: same ideal signal, independent noise draw
        t = pipe._t_exp_s
        rn = pipe._read_noise_e
        dk = pipe._dark_e_per_s
        var_e = rn**2 + (dk + bg_e_per_s) * t
        variance_rate = var_e / (t**2)
        sci_rate = ideal_e / t + bg_e_per_s
        sci = np.full((ctx, ctx), sci_rate) + rng.normal(
            0.0, np.sqrt(variance_rate), size=(ctx, ctx)
        )

        diff = pipe.subtract(sci, ref)
        residuals = diff.ravel()
        n = residuals.size
        mean_r = np.mean(residuals)
        std_r = np.std(residuals)

        assert abs(mean_r) < 3.0 * std_r / np.sqrt(n), (
            f"|mean residual|={abs(mean_r):.6f} exceeds noise threshold "
            f"3*std/sqrt(N)={3.0 * std_r / np.sqrt(n):.6f}"
        )


# ---------------------------------------------------------------------------
# AC-D4: Point source recovery within 10% flux accuracy
# ---------------------------------------------------------------------------

class TestPointSourceRecovery:
    def test_flux_recovery_within_10_percent(
        self, detector: DetectorConfig
    ) -> None:
        """AL subtraction recovers an injected point source within 10% flux.

        Uses a noiseless flat reference to isolate AL kernel accuracy from
        noise statistics.  The reference and science share the same background
        level so the constant basis term absorbs it exactly, leaving only the
        point-source flux in the difference image.
        """
        ctx = 64
        dia_cfg = DIAConfig(
            context_stamp_size=ctx,
            science_stamp_size=32,
            n_reference_epochs=10,
            subtraction_method="alard_lupton",
        )
        pipe = DIAPipeline(dia_cfg, detector, np.random.default_rng(314))

        t = pipe._t_exp_s
        bg_rate = 3000.0 / t + 2.0  # flat background rate (e-/s per pixel)

        # Noiseless flat reference — isolates AL kernel accuracy
        ref = np.full((ctx, ctx), bg_rate, dtype=np.float64)

        # Science: same background + a narrow Gaussian point source at centre
        source_flux_rate = 500.0   # total e-/s injected
        source_sigma_px = 1.5      # sub-PSF width in pixels
        cy, cx_coord = ctx // 2, ctx // 2
        yy, xx = np.ogrid[:ctx, :ctx]
        gauss = np.exp(
            -((yy - cy) ** 2 + (xx - cx_coord) ** 2) / (2.0 * source_sigma_px**2)
        )
        gauss_norm = gauss / gauss.sum()  # unit-sum spatial profile
        sci = ref + source_flux_rate * gauss_norm

        # Subtract
        diff = pipe.subtract(sci, ref)

        # Measure recovered flux in a generous aperture (3*sigma + 2 px radius)
        aperture_radius_px = int(np.ceil(3.0 * source_sigma_px)) + 2
        dist = np.sqrt((yy - cy) ** 2 + (xx - cx_coord) ** 2)
        aperture_mask = dist <= aperture_radius_px
        recovered_flux = float(np.sum(diff[aperture_mask]))

        # Expected: source_flux_rate * fraction of the Gaussian inside aperture
        aperture_fraction = float(np.sum(gauss_norm[aperture_mask]))
        expected_in_aperture = source_flux_rate * aperture_fraction

        relative_error = abs(recovered_flux - expected_in_aperture) / abs(
            expected_in_aperture
        )
        assert relative_error < 0.10, (
            f"Point source flux recovery error {relative_error:.3f} exceeds 10%. "
            f"Recovered={recovered_flux:.4f}, expected≈{expected_in_aperture:.4f}"
        )


# ---------------------------------------------------------------------------
# AC-D5: SFFT raises NotImplementedError
# ---------------------------------------------------------------------------

class TestSFFTNotImplemented:
    def test_sfft_raises(self, detector: DetectorConfig) -> None:
        sfft_cfg = DIAConfig(
            context_stamp_size=32,
            science_stamp_size=16,
            n_reference_epochs=3,
            subtraction_method="sfft",
        )
        pipe = DIAPipeline(sfft_cfg, detector, np.random.default_rng(0))
        sci = np.ones((32, 32), dtype=np.float64)
        ref = np.ones((32, 32), dtype=np.float64)

        with pytest.raises(NotImplementedError):
            pipe.subtract(sci, ref)


# ---------------------------------------------------------------------------
# AC-D6: extract_stamp — default config shape
# ---------------------------------------------------------------------------

class TestExtractStampShape:
    def test_default_stamp_shape(
        self, pipeline: DIAPipeline, dia_config: DIAConfig
    ) -> None:
        ctx = dia_config.context_stamp_size
        sci = dia_config.science_stamp_size
        diff = np.zeros((ctx, ctx), dtype=np.float64)

        stamp = pipeline.extract_stamp(diff)

        assert stamp.shape == (sci, sci), (
            f"Expected ({sci},{sci}), got {stamp.shape}"
        )

    def test_stamp_is_central_crop(
        self, pipeline: DIAPipeline, dia_config: DIAConfig
    ) -> None:
        """Stamp values must match the central region of the difference image."""
        ctx = dia_config.context_stamp_size
        sci_size = dia_config.science_stamp_size
        diff = np.arange(ctx * ctx, dtype=np.float64).reshape(ctx, ctx)

        stamp = pipeline.extract_stamp(diff)

        center = ctx // 2
        half = sci_size // 2
        expected = diff[center - half : center + half, center - half : center + half]
        np.testing.assert_array_equal(stamp, expected)


# ---------------------------------------------------------------------------
# AC-D7: extract_stamp — dynamic scaling
# ---------------------------------------------------------------------------

class TestExtractStampDynamicScaling:
    @pytest.mark.parametrize(
        "ctx, sci",
        [
            (128, 64),
            (64, 32),
            (32, 16),
            (256, 128),
        ],
    )
    def test_dynamic_crop_shape(
        self, ctx: int, sci: int, detector: DetectorConfig
    ) -> None:
        cfg = DIAConfig(context_stamp_size=ctx, science_stamp_size=sci)
        pipe = DIAPipeline(cfg, detector, np.random.default_rng(0))
        diff = np.zeros((ctx, ctx), dtype=np.float64)

        stamp = pipe.extract_stamp(diff)

        assert stamp.shape == (sci, sci), (
            f"ctx={ctx} sci={sci}: expected ({sci},{sci}), got {stamp.shape}"
        )

    def test_no_hardcoded_indices(self, detector: DetectorConfig) -> None:
        """Verify crop does NOT use hardcoded offsets — uses config values."""
        # Use non-default sizes to expose hardcoding
        ctx, sci = 128, 48
        cfg = DIAConfig(context_stamp_size=ctx, science_stamp_size=sci)
        pipe = DIAPipeline(cfg, detector, np.random.default_rng(0))

        # Fill with distinct values so position matters
        diff = np.arange(ctx * ctx, dtype=np.float64).reshape(ctx, ctx)
        stamp = pipe.extract_stamp(diff)

        center = ctx // 2
        half = sci // 2
        expected = diff[center - half : center + half, center - half : center + half]
        np.testing.assert_array_equal(stamp, expected)


# ---------------------------------------------------------------------------
# AC-D8: Input validation — build_reference
# ---------------------------------------------------------------------------

class TestBuildReferenceValidation:
    def test_length_mismatch_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        epochs = _make_flat_epochs(3, ctx)
        bgs = _make_backgrounds(2)  # wrong length

        with pytest.raises(ValueError, match="must equal"):
            pipeline.build_reference(epochs, bgs)

    def test_wrong_ndim_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        epochs = [np.ones((ctx, ctx, 1))]  # 3D instead of 2D
        bgs = [1.0]

        with pytest.raises(ValueError, match="2D"):
            pipeline.build_reference(epochs, bgs)

    def test_wrong_shape_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        epochs = [np.ones((ctx + 4, ctx))]  # wrong height
        bgs = [1.0]

        with pytest.raises(ValueError, match="shape"):
            pipeline.build_reference(epochs, bgs)

    def test_empty_list_raises(self, pipeline: DIAPipeline) -> None:
        with pytest.raises(ValueError):
            pipeline.build_reference([], [])


# ---------------------------------------------------------------------------
# AC-D9: Input validation — subtract
# ---------------------------------------------------------------------------

class TestSubtractValidation:
    def test_science_non_2d_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci_3d = np.ones((1, ctx, ctx))
        ref = np.ones((ctx, ctx))

        with pytest.raises(ValueError, match="2D"):
            pipeline.subtract(sci_3d, ref)

    def test_reference_non_2d_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci = np.ones((ctx, ctx))
        ref_3d = np.ones((1, ctx, ctx))

        with pytest.raises(ValueError, match="2D"):
            pipeline.subtract(sci, ref_3d)

    def test_shape_mismatch_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci = np.ones((ctx, ctx))
        ref = np.ones((ctx + 2, ctx))  # different shape

        with pytest.raises(ValueError, match="match"):
            pipeline.subtract(sci, ref)


# ---------------------------------------------------------------------------
# AC-D10: Input validation — extract_stamp
# ---------------------------------------------------------------------------

class TestExtractStampValidation:
    def test_non_2d_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        diff_3d = np.zeros((ctx, ctx, 1))

        with pytest.raises(ValueError, match="2D"):
            pipeline.extract_stamp(diff_3d)

    def test_too_small_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        sci = dia_config.science_stamp_size
        # Image smaller than science_stamp_size
        tiny = np.zeros((sci - 2, sci - 2))

        with pytest.raises(ValueError, match="science_stamp_size"):
            pipeline.extract_stamp(tiny)


# ---------------------------------------------------------------------------
# Regression: odd science_stamp_size produces exact shape
# ---------------------------------------------------------------------------

class TestExtractStampOddSize:
    def test_odd_science_stamp_size_shape(self, detector: DetectorConfig) -> None:
        """extract_stamp returns exact (sci, sci) shape when sci is odd."""
        ctx, sci = 64, 33  # odd science_stamp_size
        cfg = DIAConfig(context_stamp_size=ctx, science_stamp_size=sci)
        pipe = DIAPipeline(cfg, detector, np.random.default_rng(0))
        diff = np.zeros((ctx, ctx), dtype=np.float64)

        stamp = pipe.extract_stamp(diff)

        assert stamp.shape == (sci, sci), (
            f"Odd sci_size={sci}: expected ({sci},{sci}), got {stamp.shape}"
        )

    def test_odd_science_stamp_correct_center(self, detector: DetectorConfig) -> None:
        """For odd sci_size the crop is geometrically centered on the input."""
        ctx, sci = 64, 33
        cfg = DIAConfig(context_stamp_size=ctx, science_stamp_size=sci)
        pipe = DIAPipeline(cfg, detector, np.random.default_rng(0))
        diff = np.arange(ctx * ctx, dtype=np.float64).reshape(ctx, ctx)

        stamp = pipe.extract_stamp(diff)

        center = ctx // 2
        half = sci // 2
        expected = diff[center - half : center - half + sci, center - half : center - half + sci]
        np.testing.assert_array_equal(stamp, expected)


# ---------------------------------------------------------------------------
# Regression: oversized input produces correct centered crop
# ---------------------------------------------------------------------------

class TestExtractStampOversized:
    def test_oversized_input_correct_center(self, detector: DetectorConfig) -> None:
        """An input larger than context_stamp_size still produces a correct crop."""
        ctx, sci = 64, 32
        cfg = DIAConfig(context_stamp_size=ctx, science_stamp_size=sci)
        pipe = DIAPipeline(cfg, detector, np.random.default_rng(0))

        # Feed a 128×128 array (2× context size) — center derived from actual shape.
        oversized = np.arange(128 * 128, dtype=np.float64).reshape(128, 128)
        stamp = pipe.extract_stamp(oversized)

        assert stamp.shape == (sci, sci), (
            f"Oversized input: expected ({sci},{sci}), got {stamp.shape}"
        )
        center = 128 // 2
        half = sci // 2
        expected = oversized[center - half : center - half + sci, center - half : center - half + sci]
        np.testing.assert_array_equal(stamp, expected)


# ---------------------------------------------------------------------------
# Regression: subtract raises ValueError on NaN/Inf inputs
# ---------------------------------------------------------------------------

class TestSubtractFiniteGuard:
    def test_nan_in_science_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci = np.full((ctx, ctx), float("nan"))
        ref = np.ones((ctx, ctx), dtype=np.float64)
        with pytest.raises(ValueError, match="science_rate_image"):
            pipeline.subtract(sci, ref)

    def test_inf_in_science_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci = np.full((ctx, ctx), float("inf"))
        ref = np.ones((ctx, ctx), dtype=np.float64)
        with pytest.raises(ValueError, match="science_rate_image"):
            pipeline.subtract(sci, ref)

    def test_nan_in_reference_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci = np.ones((ctx, ctx), dtype=np.float64)
        ref = np.full((ctx, ctx), float("nan"))
        with pytest.raises(ValueError, match="reference_rate_image"):
            pipeline.subtract(sci, ref)

    def test_inf_in_reference_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        sci = np.ones((ctx, ctx), dtype=np.float64)
        ref = np.full((ctx, ctx), float("-inf"))
        with pytest.raises(ValueError, match="reference_rate_image"):
            pipeline.subtract(sci, ref)


# ---------------------------------------------------------------------------
# Regression: build_reference raises on invalid backgrounds or t_exp_s <= 0
# ---------------------------------------------------------------------------

class TestBuildReferenceFiniteGuard:
    def test_nan_in_epoch_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        bad_epoch = np.full((ctx, ctx), float("nan"))
        with pytest.raises(ValueError, match="non-finite"):
            pipeline.build_reference([bad_epoch], [1.0])

    def test_inf_in_epoch_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        bad_epoch = np.full((ctx, ctx), float("inf"))
        with pytest.raises(ValueError, match="non-finite"):
            pipeline.build_reference([bad_epoch], [1.0])

    def test_nan_background_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        epoch = np.ones((ctx, ctx), dtype=np.float64)
        with pytest.raises(ValueError, match="non-finite"):
            pipeline.build_reference([epoch], [float("nan")])

    def test_inf_background_raises(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        ctx = dia_config.context_stamp_size
        epoch = np.ones((ctx, ctx), dtype=np.float64)
        with pytest.raises(ValueError, match="non-finite"):
            pipeline.build_reference([epoch], [float("inf")])

    def test_zero_t_exp_raises_in_build_reference(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        """build_reference raises ValueError when t_exp_s is 0."""
        ctx = dia_config.context_stamp_size
        epoch = np.ones((ctx, ctx), dtype=np.float64)
        # Patch after construction to simulate a broken derived value.
        original = pipeline._t_exp_s
        pipeline._t_exp_s = 0.0
        try:
            with pytest.raises(ValueError, match="t_exp_s"):
                pipeline.build_reference([epoch], [1.0])
        finally:
            pipeline._t_exp_s = original

    def test_negative_t_exp_raises_in_build_reference(self, pipeline: DIAPipeline, dia_config: DIAConfig) -> None:
        """build_reference raises ValueError when t_exp_s is negative."""
        ctx = dia_config.context_stamp_size
        epoch = np.ones((ctx, ctx), dtype=np.float64)
        original = pipeline._t_exp_s
        pipeline._t_exp_s = -1.0
        try:
            with pytest.raises(ValueError, match="t_exp_s"):
                pipeline.build_reference([epoch], [1.0])
        finally:
            pipeline._t_exp_s = original
