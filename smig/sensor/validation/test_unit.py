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


def test_process_epoch_stub_returns_copy_not_alias(small_detector: H4RG10Detector):
    """Stub returns a copy of the input, not the same object."""
    ideal = np.ones((16, 16), dtype=np.float64) * 1_000.0
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)
    assert np.array_equal(output.rate_image, ideal)
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
    assert set(single_epoch_output.provenance_data.keys()) == _EXPECTED_PROVENANCE_KEYS


def test_process_epoch_provenance_data_stub_flags(
    single_epoch_output: DetectorOutput,
):
    """Checks provenance applied-effect flags and counts.

    charge_diffusion_applied is True because ChargeDiffusionModel.apply() is
    always called in the signal chain. The other physics stages are stubs and
    flag themselves as not applied (False) until physics is implemented.
    """
    pd = single_epoch_output.provenance_data
    assert pd["charge_diffusion_applied"] is True
    assert pd["ipc_applied"] is False
    assert pd["persistence_applied"] is False
    assert pd["nonlinearity_applied"] is False
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

def test_saturation_mask_correct_threshold(small_detector: H4RG10Detector):
    """Pixels at exactly the saturation threshold must be flagged.

    Uses _saturation_threshold directly (precomputed from frozen config) to
    ensure the test is tied to the same value the implementation uses.
    """
    threshold = small_detector._saturation_threshold
    ideal = np.full((16, 16), threshold, dtype=np.float64)
    output = small_detector.process_epoch(ideal, epoch_index=0, epoch_time_mjd=60_000.0)
    assert output.saturation_mask.all(), (
        f"All pixels at threshold ({threshold}) should be masked"
    )


def test_saturation_mask_below_threshold_not_masked(small_detector: H4RG10Detector):
    """Pixels strictly below the saturation threshold must not be flagged."""
    threshold = small_detector._saturation_threshold
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

    After Phase B, noise modules use child RNGs derived from the parent at
    construction time.  The parent ``self._rng`` is therefore NOT advanced
    naturally during ``process_epoch`` — all stochastic paths go through
    the children.  We manually advance ``self._rng`` here so the assertion
    is non-vacuous: if ``provenance_data["random_state"]`` were a live
    reference to the generator object, it would reflect the new state after
    the advance.  The test proves it does not.
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
