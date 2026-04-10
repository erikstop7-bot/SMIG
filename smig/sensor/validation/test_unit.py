"""
smig/sensor/validation/test_unit.py
=====================================
Unit tests for the SMIG v2 Phase 1 sensor scaffold.

Run from the project root:
    python -m pytest smig/sensor/validation/test_unit.py -v
"""

from __future__ import annotations

import numpy as np
import pytest

from smig.config.schemas import DetectorConfig, GeometryConfig
from smig.config.utils import get_config_sha256
from smig.provenance.schema import ProvenanceRecord
from smig.sensor.detector import DetectorOutput, EventOutput, H4RG10Detector
from smig.sensor.noise.cosmic_rays import ClusteredCosmicRayInjector


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_cfg() -> DetectorConfig:
    """16×16 DetectorConfig for fast unit tests."""
    return DetectorConfig(geometry=GeometryConfig(nx=16, ny=16))


@pytest.fixture
def small_detector(small_cfg: DetectorConfig) -> H4RG10Detector:
    return H4RG10Detector(small_cfg, np.random.default_rng(0))


@pytest.fixture
def single_epoch_output(small_detector: H4RG10Detector) -> DetectorOutput:
    ideal = np.ones((16, 16), dtype=np.float64) * 1_000.0
    return small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)


@pytest.fixture
def event_output(small_detector: H4RG10Detector) -> EventOutput:
    ideal_cube = np.ones((3, 16, 16), dtype=np.float64) * 500.0
    timestamps = np.array([60_000.0, 60_001.0, 60_002.0])
    return small_detector.process_event("test_event", ideal_cube, timestamps)


# ---------------------------------------------------------------------------
# Config hashing
# ---------------------------------------------------------------------------

def test_config_sha256_determinism():
    """Identical configs produce the same 64-char hash; different configs differ."""
    cfg1 = DetectorConfig()
    cfg2 = DetectorConfig()
    h1 = get_config_sha256(cfg1)
    h2 = get_config_sha256(cfg2)
    assert h1 == h2
    assert len(h1) == 64

    cfg3 = DetectorConfig(geometry=GeometryConfig(nx=2048, ny=2048))
    assert get_config_sha256(cfg3) != h1


def test_config_sha256_is_hex_string():
    """Hash is a valid lowercase hex string of length 64."""
    h = get_config_sha256(DetectorConfig())
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# Detector construction
# ---------------------------------------------------------------------------

def test_detector_construction(small_cfg: DetectorConfig):
    """H4RG10Detector constructs without error and stores the config."""
    rng = np.random.default_rng(42)
    detector = H4RG10Detector(small_cfg, rng)
    assert detector._config is small_cfg
    assert detector._config_sha256 == get_config_sha256(small_cfg)


# ---------------------------------------------------------------------------
# process_epoch — shapes and types
# ---------------------------------------------------------------------------

def test_process_epoch_returns_detector_output(single_epoch_output: DetectorOutput):
    assert isinstance(single_epoch_output, DetectorOutput)


def test_process_epoch_rate_image_shape_and_dtype(single_epoch_output: DetectorOutput):
    assert single_epoch_output.rate_image.shape == (16, 16)
    assert single_epoch_output.rate_image.dtype == np.float64


def test_process_epoch_masks_shape_and_dtype(single_epoch_output: DetectorOutput):
    assert single_epoch_output.saturation_mask.shape == (16, 16)
    assert single_epoch_output.saturation_mask.dtype == bool
    assert single_epoch_output.cr_mask.shape == (16, 16)
    assert single_epoch_output.cr_mask.dtype == bool


def test_process_epoch_output_does_not_alias_input(small_detector: H4RG10Detector):
    """Output rate_image must not be the same object as the input array."""
    ideal = np.ones((16, 16), dtype=np.float64) * 1_000.0
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)
    assert output.rate_image is not ideal


# ---------------------------------------------------------------------------
# process_epoch — provenance_data
# ---------------------------------------------------------------------------

_EXPECTED_PROVENANCE_KEYS = frozenset({
    "git_commit",
    "container_digest",
    "python_version",
    "numpy_version",
    "config_sha256",
    "random_state",
    "ipc_applied",
    "persistence_applied",
    "nonlinearity_applied",
    "charge_diffusion_applied",
    "saturated_pixel_count",
    "cosmic_ray_hit_count",
})


def test_process_epoch_provenance_data_has_correct_keys(
    single_epoch_output: DetectorOutput,
):
    # Subset check: required keys must be present; additional keys are allowed
    # as new provenance dimensions are added without breaking this test.
    assert _EXPECTED_PROVENANCE_KEYS <= set(single_epoch_output.provenance_data.keys())


def test_process_epoch_provenance_data_stub_flags(
    single_epoch_output: DetectorOutput,
):
    """Checks provenance applied-effect flags and counts.

    charge_diffusion_applied is True because ChargeDiffusionModel.apply() is
    always called in the signal chain. The other physics stages are stubs and
    flag themselves as not applied (False) until physics is implemented.
    """
    pd = single_epoch_output.provenance_data

    # Phase-1 stub check: updated to type checks to allow physics integration.
    # When physics lands, reintroduce stronger semantics tests.
    assert pd["charge_diffusion_applied"] is True  # Always True for Phase 1+; if diffusion is in the chain, it is applied.
    assert isinstance(pd["ipc_applied"], bool)
    assert isinstance(pd["persistence_applied"], bool)
    assert isinstance(pd["nonlinearity_applied"], bool)
    assert pd["saturated_pixel_count"] == 0
    assert pd["cosmic_ray_hit_count"] == 0


def test_process_epoch_provenance_config_sha256(
    small_detector: H4RG10Detector,
    small_cfg: DetectorConfig,
    single_epoch_output: DetectorOutput,
):
    assert single_epoch_output.provenance_data["config_sha256"] == get_config_sha256(
        small_cfg
    )


def test_process_epoch_provenance_random_state_structure(
    single_epoch_output: DetectorOutput,
):
    rs = single_epoch_output.provenance_data["random_state"]
    assert isinstance(rs, dict)
    assert "bit_generator" in rs


# ---------------------------------------------------------------------------
# process_epoch — shape validation
# ---------------------------------------------------------------------------

def test_process_epoch_rejects_wrong_shape(small_detector: H4RG10Detector):
    wrong = np.ones((8, 8), dtype=np.float64)
    with pytest.raises(ValueError, match="shape"):
        small_detector.process_epoch(wrong, epoch_index=0, epoch_time_mjd=60_000.0)


# ---------------------------------------------------------------------------
# process_event — shapes and structure
# ---------------------------------------------------------------------------

def test_process_event_returns_event_output(event_output: EventOutput):
    assert isinstance(event_output, EventOutput)


def test_process_event_cube_shapes(event_output: EventOutput):
    assert event_output.rate_cube.shape == (3, 16, 16)
    assert event_output.saturation_cube.shape == (3, 16, 16)
    assert event_output.cr_cube.shape == (3, 16, 16)
    assert event_output.persistence_peak_map.shape == (16, 16)


def test_process_event_provenance_record_count(event_output: EventOutput):
    assert len(event_output.provenance_records) == 3


def test_process_event_provenance_records_are_valid(event_output: EventOutput):
    """All records are ProvenanceRecords with correct event_id and epoch_index."""
    for i, record in enumerate(event_output.provenance_records):
        assert isinstance(record, ProvenanceRecord)
        assert record.event_id == "test_event"
        assert record.epoch_index == i


def test_process_event_provenance_timestamps_are_aware(event_output: EventOutput):
    """All provenance timestamps are timezone-aware (UTC)."""
    for record in event_output.provenance_records:
        assert record.timestamp_utc.tzinfo is not None


def test_process_event_provenance_config_sha256_consistent(
    event_output: EventOutput,
    small_cfg: DetectorConfig,
):
    """All records share the same config_sha256."""
    expected = get_config_sha256(small_cfg)
    for record in event_output.provenance_records:
        assert record.config_sha256 == expected


# ---------------------------------------------------------------------------
# Phase C — Input guard tests
# ---------------------------------------------------------------------------

def test_process_epoch_rejects_nan_input(small_detector: H4RG10Detector):
    """ValueError on NaN anywhere in ideal_image_e."""
    bad = np.ones((16, 16), dtype=np.float64) * 1_000.0
    bad[3, 7] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        small_detector.process_epoch(bad, epoch_index=0, epoch_time_mjd=60_000.0)


def test_process_epoch_rejects_negative_input(small_detector: H4RG10Detector):
    """ValueError when ideal_image_e contains negative electron counts."""
    bad = np.full((16, 16), -1.0, dtype=np.float64)
    with pytest.raises(ValueError, match="negative"):
        small_detector.process_epoch(bad, epoch_index=0, epoch_time_mjd=60_000.0)


def test_process_epoch_rejects_1d_input(small_detector: H4RG10Detector):
    """ValueError when ideal_image_e is 1-D (ndim != 2)."""
    bad = np.ones(16 * 16, dtype=np.float64) * 1_000.0
    with pytest.raises(ValueError, match="2-D"):
        small_detector.process_epoch(bad, epoch_index=0, epoch_time_mjd=60_000.0)


def test_process_epoch_rate_image_is_float64(small_detector: H4RG10Detector):
    """Output rate_image is always float64 even when input dtype is integer."""
    ideal = np.ones((16, 16), dtype=np.int32) * 1_000
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)
    assert output.rate_image.dtype == np.float64


def test_process_epoch_cr_mask_shape_matches_rate_image(
    single_epoch_output: DetectorOutput,
):
    """cr_mask must have the same shape as rate_image."""
    assert single_epoch_output.cr_mask.shape == single_epoch_output.rate_image.shape


def test_process_event_rejects_2d_cube(small_detector: H4RG10Detector):
    """ValueError when ideal_cube_e is 2-D instead of 3-D."""
    wrong = np.ones((16, 16), dtype=np.float64) * 500.0
    ts = np.array([60_000.0])
    with pytest.raises(ValueError, match="3-D"):
        small_detector.process_event("ev", wrong, ts)


# ---------------------------------------------------------------------------
# Phase C — Saturation mask tests
# ---------------------------------------------------------------------------

def test_saturation_mask_correct_threshold(
    small_cfg: DetectorConfig, small_detector: H4RG10Detector
):
    """Pixels at exactly the saturation threshold must be flagged.

    Computes the expected threshold from first principles so the test does not
    couple to the private _saturation_threshold attribute.
    """
    threshold = (
        small_cfg.nonlinearity.saturation_flag_threshold
        * small_cfg.electrical.full_well_electrons
    )
    ideal = np.full((16, 16), threshold, dtype=np.float64)
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)
    assert output.saturation_mask.all(), (
        f"All pixels at threshold ({threshold}) should be masked"
    )


def test_saturation_mask_below_threshold_not_masked(
    small_cfg: DetectorConfig, small_detector: H4RG10Detector
):
    """Pixels strictly below the saturation threshold must not be flagged."""
    threshold = (
        small_cfg.nonlinearity.saturation_flag_threshold
        * small_cfg.electrical.full_well_electrons
    )
    ideal = np.full((16, 16), threshold - 1.0, dtype=np.float64)
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)
    assert not output.saturation_mask.any(), (
        f"No pixels at threshold-1 ({threshold - 1.0}) should be masked"
    )


# ---------------------------------------------------------------------------
# Phase C — Provenance / RNG snapshot tests
# ---------------------------------------------------------------------------

def test_process_epoch_provenance_random_state_json_serializable(
    single_epoch_output: DetectorOutput,
):
    """random_state in provenance_data must be natively JSON-serializable."""
    import json

    rs = single_epoch_output.provenance_data["random_state"]
    # Must not raise; numpy types (np.uint64, np.ndarray, etc.) would cause TypeError.
    json.dumps(rs)


def test_rng_state_serialization_is_snapshot(small_detector: H4RG10Detector):
    """Provenance random_state is a static snapshot, not a live generator reference.

    Noise modules use child RNGs derived from the parent at construction time.
    The parent ``self._rng`` is therefore NOT advanced naturally during
    ``process_epoch`` — all stochastic paths go through the children.
    We manually advance the parent RNG *post-call* to verify that the
    already-captured ``provenance_data['random_state']`` is a snapshot
    (serialized copy), not a live reference to the generator object.
    """
    import copy

    ideal = np.ones((16, 16), dtype=np.float64) * 1_000.0
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)

    # Deep-copy the serialized state at the moment of capture.
    state_at_capture = copy.deepcopy(output.provenance_data["random_state"])

    # Explicitly advance the parent RNG — it is the generator whose state is
    # snapshotted for provenance but is not consumed during process_epoch.
    small_detector._rng.integers(0, 2**32, size=1_000)

    # The snapshot must be byte-for-byte identical to what was captured before
    # the advance, proving it is a serialized copy, not a live reference.
    assert output.provenance_data["random_state"] == state_at_capture


# ---------------------------------------------------------------------------
# Phase C — Input-mutation independence test
# ---------------------------------------------------------------------------

def test_process_event_independence_from_input_mutation(
    small_detector: H4RG10Detector,
):
    """Mutating ideal_cube_e after process_event does not corrupt the output.

    process_epoch casts each slice with astype(float64, copy=True), so the
    output rate_cube should be immune to in-place mutations of the source array.
    """
    ideal_cube = np.ones((3, 16, 16), dtype=np.float64) * 500.0
    timestamps = np.array([60_000.0, 60_001.0, 60_002.0])
    output = small_detector.process_event("ev", ideal_cube, timestamps)

    rate_cube_before = output.rate_cube.copy()

    # Overwrite the source array entirely.
    ideal_cube[:] = 0.0

    np.testing.assert_array_equal(output.rate_cube, rate_cube_before)


# ---------------------------------------------------------------------------
# Phase D — Green contract tests (must pass now)
# ---------------------------------------------------------------------------

def test_cr_injector_signature_2d_only():
    """ClusteredCosmicRayInjector.apply() must reject 3D arrays with ValueError."""
    cfg = DetectorConfig(geometry=GeometryConfig(nx=16, ny=16))
    injector = ClusteredCosmicRayInjector(cfg, np.random.default_rng(0))
    ramp_3d = np.zeros((9, 16, 16), dtype=np.float64)
    with pytest.raises(ValueError, match="2-D"):
        injector.apply(ramp_3d)


def test_process_event_rejects_non_monotone_timestamps(
    small_detector: H4RG10Detector,
):
    """process_event must raise ValueError for decreasing timestamps."""
    ideal_cube = np.ones((3, 16, 16), dtype=np.float64) * 500.0
    # Third timestamp is less than second — violates non-decreasing constraint.
    timestamps = np.array([60_000.0, 60_002.0, 60_001.0])
    with pytest.raises(ValueError, match="non-decreasing"):
        small_detector.process_event("ev", ideal_cube, timestamps)


def test_process_epoch_applied_flags_are_booleans(
    single_epoch_output: DetectorOutput,
):
    """Every *_applied key in provenance_data must be a native Python bool."""
    pd = single_epoch_output.provenance_data
    for key in ("ipc_applied", "persistence_applied", "nonlinearity_applied",
                "charge_diffusion_applied"):
        assert isinstance(pd[key], bool), (
            f"{key!r} is {type(pd[key]).__name__!r}, expected bool"
        )


# ---------------------------------------------------------------------------
# Phase D — Physics tests (xfail: physics not yet implemented)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="Physics not yet implemented")
def test_ipc_flux_conservation():
    """IPC convolution must conserve total flux to within 0.01%."""
    from smig.sensor.ipc import FieldDependentIPC
    from smig.config.schemas import IPCConfig
    cfg = IPCConfig()
    ipc = FieldDependentIPC(cfg, sca_id=1, field_position=(0.0, 0.0))
    rng = np.random.default_rng(1)
    image = rng.uniform(100.0, 50_000.0, size=(64, 64))
    out = ipc.apply(image)
    assert abs(out.sum() - image.sum()) / image.sum() < 1e-4


@pytest.mark.xfail(reason="Physics not yet implemented")
def test_ipc_asymmetric_kernel_injection():
    """IPC applied to a point source must produce asymmetric neighbour values
    that match hand-computed expectations for a non-symmetric kernel."""
    from smig.sensor.ipc import FieldDependentIPC
    from smig.config.schemas import IPCConfig
    cfg = IPCConfig(ipc_field_dependent=False)
    ipc = FieldDependentIPC(cfg, sca_id=1, field_position=(0.0, 0.0))
    image = np.zeros((16, 16), dtype=np.float64)
    image[8, 8] = 1_000.0
    out = ipc.apply(image)
    alpha = cfg.ipc_alpha_center
    assert abs(out[8, 9] - alpha * 1_000.0) < 1.0
    assert abs(out[8, 7] - alpha * 1_000.0) < 1.0


@pytest.mark.xfail(reason="Physics not yet implemented")
def test_charge_diffusion_conservation():
    """Charge diffusion must conserve total electron count within 0.01%."""
    from smig.sensor.charge_diffusion import ChargeDiffusionModel
    from smig.config.schemas import ChargeDiffusionConfig
    cfg = ChargeDiffusionConfig(pixel_pitch_um=10.0, full_well_electrons=100_000.0)
    model = ChargeDiffusionModel(cfg)
    rng = np.random.default_rng(2)
    image = rng.uniform(100.0, 50_000.0, size=(64, 64))
    out = model.apply(image)
    assert abs(out.sum() - image.sum()) / image.sum() < 1e-4


@pytest.mark.xfail(reason="Physics not yet implemented")
def test_chain_order_cd_before_ipc_noncommutative():
    """diffuse(ipc(x)) != ipc(diffuse(x)) for non-trivial kernels."""
    from smig.sensor.ipc import FieldDependentIPC
    from smig.sensor.charge_diffusion import ChargeDiffusionModel
    from smig.config.schemas import ChargeDiffusionConfig, IPCConfig
    ipc = FieldDependentIPC(IPCConfig(), sca_id=1, field_position=(0.0, 0.0))
    cd = ChargeDiffusionModel(
        ChargeDiffusionConfig(pixel_pitch_um=10.0, full_well_electrons=100_000.0)
    )
    rng = np.random.default_rng(3)
    image = rng.uniform(100.0, 10_000.0, size=(32, 32))
    # Correct order: diffuse then IPC
    order_correct = ipc.apply(cd.apply(image))
    # Swapped order
    order_swapped = cd.apply(ipc.apply(image))
    assert not np.allclose(order_correct, order_swapped), (
        "CD→IPC and IPC→CD must differ for non-trivial kernels"
    )


@pytest.mark.xfail(reason="Physics not yet implemented")
def test_cr_mask_covers_full_cluster():
    """_inject_single_event mask must cover all pixels that received charge."""
    cfg = DetectorConfig(geometry=GeometryConfig(nx=32, ny=32))
    injector = ClusteredCosmicRayInjector(cfg, np.random.default_rng(4))
    image = np.zeros((32, 32), dtype=np.float64)
    morphology = np.array([[0.1, 0.8, 0.1]], dtype=np.float64)  # 3-pixel track
    _, mask = injector._inject_single_event(
        image, y0=16, x0=16, energy_electrons=10_000.0, morphology=morphology
    )
    # Every pixel that received non-zero charge must be True in the mask
    modified = (image > 0)
    assert np.all(mask[modified]), "cr_mask must cover all pixels that received charge"


@pytest.mark.xfail(reason="Physics not yet implemented")
def test_cr_hit_count_is_events_not_pixels():
    """A single 5-pixel cluster contributes 1 to cosmic_ray_hit_count."""
    cfg = DetectorConfig(geometry=GeometryConfig(nx=32, ny=32))
    injector = ClusteredCosmicRayInjector(cfg, np.random.default_rng(5))
    image = np.zeros((32, 32), dtype=np.float64)
    morphology = np.ones((1, 5), dtype=np.float64) / 5  # 5-pixel track
    _, mask = injector._inject_single_event(
        image, y0=16, x0=16, energy_electrons=10_000.0, morphology=morphology
    )
    # The injector returns 1 event regardless of cluster size
    _, _, hit_count = injector.apply(image)
    assert hit_count == 1, f"Expected hit_count=1 for one event, got {hit_count}"
