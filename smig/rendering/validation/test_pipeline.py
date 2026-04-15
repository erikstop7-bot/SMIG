"""
smig/rendering/validation/test_pipeline.py
==========================================
Integration tests for :class:`~smig.rendering.pipeline.SceneSimulator`.

Coverage
--------
AC-P1  Smoke test: full pipeline runs end-to-end (3 science, 5 ref, 32×32 ctx,
       16×16 science crop).  Output arrays have correct shapes and dtypes.
AC-P2  Determinism: two runs with the same ``(master_seed, event_id)`` produce
       bit-identical ``EventSceneOutput`` arrays.
AC-P3  Provenance determinism: ``record.model_dump(mode='json')`` is identical
       across two runs for all epochs.
AC-P4  Phase 2 provenance fields are populated on every returned record:
       ``psf_config_hash``, ``n_neighbors_rendered``, ``dia_method``,
       ``reference_n_epochs``.
AC-P5  Memory ordering: ``H4RG10Detector.process_event`` is called and returns
       before ``DIAPipeline.subtract`` is first invoked, confirming that
       ``del ideal_cube_e`` lies between detector and DIA.
AC-P6  Different ``event_id`` values produce different difference stamps
       (seed isolation).
AC-P7  Architecture boundary: ``smig/rendering/pipeline.py`` does not import
       any internal sensor-physics leaf modules from ``smig.sensor.*``.

Run from the SMIG project root::

    python -m pytest smig/rendering/validation/test_pipeline.py -v
"""
from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import pytest

# Guard: skip entire module if galsim / pandas are not installed.
galsim = pytest.importorskip("galsim", reason="galsim required for pipeline tests")
pd = pytest.importorskip("pandas", reason="pandas required for pipeline tests")

from smig.config.optics_schemas import (
    CrowdedFieldConfig,
    DIAConfig,
    PSFConfig,
    RenderingConfig,
    SimulationConfig,
)
from smig.config.schemas import DetectorConfig, GeometryConfig
from smig.rendering.pipeline import EventSceneOutput, SceneSimulator


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_sim_config(
    ctx: int = 32,
    sci_sz: int = 16,
    n_ref: int = 5,
) -> SimulationConfig:
    """Build a small :class:`SimulationConfig` suitable for fast unit tests.

    Overrides detector geometry to ``ctx × ctx`` so that the stamp pipeline
    does not need a full 4096×4096 sensor array.  All other detector
    parameters use their defaults.
    """
    # Build detector with overridden geometry while keeping all other defaults.
    default_det = DetectorConfig()
    det_dict = default_det.model_dump()
    det_dict["geometry"]["nx"] = ctx
    det_dict["geometry"]["ny"] = ctx
    small_det = DetectorConfig.model_validate(det_dict)

    return SimulationConfig(
        detector=small_det,
        psf=PSFConfig(
            oversample=1,        # Minimal oversampling for speed
            n_wavelengths=2,     # Fewest wavelengths allowed (>=2)
            jitter_rms_mas=0.0,  # No jitter: removes stochastic PSF variation
        ),
        rendering=RenderingConfig(),
        crowded_field=CrowdedFieldConfig(
            stamp_size=sci_sz,
            pixel_scale_arcsec=0.11,
            brightness_cap_mag=None,
        ),
        dia=DIAConfig(
            n_reference_epochs=n_ref,
            context_stamp_size=ctx,
            science_stamp_size=sci_sz,
            subtraction_method="alard_lupton",
        ),
    )


def _make_source_params(n: int, flux_e: float = 5000.0) -> list[dict]:
    """Return *n* identical point-source parameter dicts."""
    return [
        {
            "flux_e": flux_e,
            "centroid_offset_pix": (0.0, 0.0),
            "rho_star_arcsec": 0.0,
            "limb_darkening_coeffs": None,
        }
        for _ in range(n)
    ]


def _make_timestamps(n: int, t0_mjd: float = 60_000.0, dt_days: float = 1.0) -> np.ndarray:
    """Return an evenly-spaced MJD timestamp array of length *n*."""
    return np.array([t0_mjd + i * dt_days for i in range(n)], dtype=np.float64)


@pytest.fixture(scope="module")
def sim_config() -> SimulationConfig:
    """Small 32×32 / 16×16 config shared across all tests in this module."""
    return _make_sim_config(ctx=32, sci_sz=16, n_ref=5)


@pytest.fixture(scope="module")
def simulator(sim_config: SimulationConfig) -> SceneSimulator:
    """A :class:`SceneSimulator` instance built from the small test config."""
    return SceneSimulator(sim_config, master_seed=42)


@pytest.fixture(scope="module")
def smoke_output(simulator: SceneSimulator) -> EventSceneOutput:
    """Run the full pipeline once and cache the result for multiple tests."""
    n_sci = 3
    return simulator.simulate_event(
        event_id="test_event_001",
        source_params_sequence=_make_source_params(n_sci),
        timestamps_mjd=_make_timestamps(n_sci),
        backgrounds_e_per_s=[1.0] * n_sci,
    )


# ---------------------------------------------------------------------------
# AC-P1: Smoke test — shapes and dtypes
# ---------------------------------------------------------------------------

class TestSmokeFullPipeline:
    """AC-P1: Verify that the pipeline runs end-to-end with correct outputs."""

    def test_difference_stamps_shape(self, smoke_output: EventSceneOutput) -> None:
        assert smoke_output.difference_stamps.shape == (3, 16, 16)

    def test_saturation_stamps_shape(self, smoke_output: EventSceneOutput) -> None:
        assert smoke_output.saturation_stamps.shape == (3, 16, 16)

    def test_cr_stamps_shape(self, smoke_output: EventSceneOutput) -> None:
        assert smoke_output.cr_stamps.shape == (3, 16, 16)

    def test_difference_stamps_dtype(self, smoke_output: EventSceneOutput) -> None:
        assert smoke_output.difference_stamps.dtype == np.float64

    def test_saturation_stamps_dtype(self, smoke_output: EventSceneOutput) -> None:
        assert smoke_output.saturation_stamps.dtype == bool

    def test_cr_stamps_dtype(self, smoke_output: EventSceneOutput) -> None:
        assert smoke_output.cr_stamps.dtype == bool

    def test_provenance_length(self, smoke_output: EventSceneOutput) -> None:
        assert len(smoke_output.provenance) == 3

    def test_provenance_types(self, smoke_output: EventSceneOutput) -> None:
        from smig.provenance.schema import ProvenanceRecord
        for rec in smoke_output.provenance:
            assert isinstance(rec, ProvenanceRecord)

    def test_difference_stamps_finite(self, smoke_output: EventSceneOutput) -> None:
        assert np.all(np.isfinite(smoke_output.difference_stamps))


# ---------------------------------------------------------------------------
# AC-P2 & AC-P3: Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    """AC-P2 / AC-P3: Two runs with the same seed → bit-identical outputs."""

    def _run(self, config: SimulationConfig, seed: int, event_id: str) -> EventSceneOutput:
        sim = SceneSimulator(config, master_seed=seed)
        n_sci = 3
        return sim.simulate_event(
            event_id=event_id,
            source_params_sequence=_make_source_params(n_sci),
            timestamps_mjd=_make_timestamps(n_sci),
            backgrounds_e_per_s=[1.0] * n_sci,
        )

    def test_difference_stamps_bit_identical(self, sim_config: SimulationConfig) -> None:
        out1 = self._run(sim_config, seed=99, event_id="evt_det")
        out2 = self._run(sim_config, seed=99, event_id="evt_det")
        np.testing.assert_array_equal(out1.difference_stamps, out2.difference_stamps)

    def test_saturation_stamps_bit_identical(self, sim_config: SimulationConfig) -> None:
        out1 = self._run(sim_config, seed=99, event_id="evt_det")
        out2 = self._run(sim_config, seed=99, event_id="evt_det")
        np.testing.assert_array_equal(out1.saturation_stamps, out2.saturation_stamps)

    def test_cr_stamps_bit_identical(self, sim_config: SimulationConfig) -> None:
        out1 = self._run(sim_config, seed=99, event_id="evt_det")
        out2 = self._run(sim_config, seed=99, event_id="evt_det")
        np.testing.assert_array_equal(out1.cr_stamps, out2.cr_stamps)

    def test_provenance_json_identical(self, sim_config: SimulationConfig) -> None:
        """AC-P3: model_dump(mode='json') must be identical for every record."""
        out1 = self._run(sim_config, seed=99, event_id="evt_det")
        out2 = self._run(sim_config, seed=99, event_id="evt_det")
        assert len(out1.provenance) == len(out2.provenance)
        for r1, r2 in zip(out1.provenance, out2.provenance):
            assert r1.model_dump(mode="json") == r2.model_dump(mode="json"), (
                f"Provenance mismatch at epoch {r1.epoch_index}"
            )


# ---------------------------------------------------------------------------
# AC-P4: Phase 2 provenance fields
# ---------------------------------------------------------------------------

class TestProvenancePhase2Fields:
    """AC-P4: All four Phase 2 provenance fields must be populated."""

    def test_psf_config_hash_not_none(self, smoke_output: EventSceneOutput) -> None:
        for rec in smoke_output.provenance:
            assert rec.psf_config_hash is not None, (
                f"psf_config_hash is None for epoch {rec.epoch_index}"
            )

    def test_psf_config_hash_is_hex_string(self, smoke_output: EventSceneOutput) -> None:
        for rec in smoke_output.provenance:
            h = rec.psf_config_hash
            assert isinstance(h, str) and len(h) == 64, (
                f"psf_config_hash '{h}' is not a 64-char hex string"
            )

    def test_n_neighbors_rendered_non_negative(
        self, smoke_output: EventSceneOutput
    ) -> None:
        for rec in smoke_output.provenance:
            assert rec.n_neighbors_rendered >= 0

    def test_n_neighbors_rendered_same_across_epochs(
        self, smoke_output: EventSceneOutput
    ) -> None:
        # Catalog is sampled once per event; count must be identical for all epochs.
        counts = [rec.n_neighbors_rendered for rec in smoke_output.provenance]
        assert len(set(counts)) == 1, f"n_neighbors_rendered varies across epochs: {counts}"

    def test_dia_method_correct(self, smoke_output: EventSceneOutput) -> None:
        for rec in smoke_output.provenance:
            assert rec.dia_method == "alard_lupton", (
                f"Expected 'alard_lupton', got {rec.dia_method!r}"
            )

    def test_reference_n_epochs_correct(self, smoke_output: EventSceneOutput) -> None:
        for rec in smoke_output.provenance:
            assert rec.reference_n_epochs == 5, (
                f"Expected 5, got {rec.reference_n_epochs}"
            )

    def test_provenance_json_serializable(self, smoke_output: EventSceneOutput) -> None:
        """Phase 2 fields must not break JSON round-trip."""
        import json
        for rec in smoke_output.provenance:
            # model_dump(mode='json') must not raise
            data = rec.model_dump(mode="json")
            # Confirm it can be serialised to a string
            json.dumps(data)


# ---------------------------------------------------------------------------
# AC-P5: Memory ordering (process_event before subtract)
# ---------------------------------------------------------------------------

class TestMemoryOrdering:
    """AC-P5: Confirm that process_event finishes before DIA subtract begins."""

    def test_process_event_before_subtract(self, sim_config: SimulationConfig) -> None:
        """Mock process_event and subtract to record call order."""
        call_log: list[str] = []

        original_process_event = SceneSimulator.__module__
        # We patch on the imported names inside pipeline.py.
        import smig.rendering.pipeline as pipeline_mod
        import smig.sensor.detector as det_mod
        import smig.rendering.dia as dia_mod

        original_pe = det_mod.H4RG10Detector.process_event
        original_sub = dia_mod.DIAPipeline.subtract

        def patched_process_event(self_det, event_id, ideal_cube_e, timestamps_mjd):
            call_log.append("process_event")
            return original_pe(self_det, event_id, ideal_cube_e, timestamps_mjd)

        def patched_subtract(self_dia, sci, ref):
            call_log.append("subtract")
            return original_sub(self_dia, sci, ref)

        with (
            patch.object(det_mod.H4RG10Detector, "process_event", patched_process_event),
            patch.object(dia_mod.DIAPipeline, "subtract", patched_subtract),
        ):
            sim = SceneSimulator(sim_config, master_seed=7)
            n_sci = 2
            sim.simulate_event(
                event_id="mem_order_test",
                source_params_sequence=_make_source_params(n_sci),
                timestamps_mjd=_make_timestamps(n_sci),
                backgrounds_e_per_s=[1.0] * n_sci,
            )

        # process_event must appear before ANY subtract call.
        assert "process_event" in call_log, "process_event was not called"
        assert "subtract" in call_log, "subtract was not called"
        first_pe = call_log.index("process_event")
        first_sub = call_log.index("subtract")
        assert first_pe < first_sub, (
            f"process_event (index {first_pe}) must precede subtract "
            f"(index {first_sub}) in call log: {call_log}"
        )


# ---------------------------------------------------------------------------
# AC-P6: Seed isolation — different event_id → different outputs
# ---------------------------------------------------------------------------

class TestSeedIsolation:
    """AC-P6: Different event_id values should produce different outputs."""

    def test_different_events_different_stamps(
        self, sim_config: SimulationConfig
    ) -> None:
        sim = SceneSimulator(sim_config, master_seed=42)
        n_sci = 2

        out_a = sim.simulate_event(
            event_id="event_alpha",
            source_params_sequence=_make_source_params(n_sci),
            timestamps_mjd=_make_timestamps(n_sci),
            backgrounds_e_per_s=[1.0] * n_sci,
        )
        out_b = sim.simulate_event(
            event_id="event_beta",
            source_params_sequence=_make_source_params(n_sci),
            timestamps_mjd=_make_timestamps(n_sci),
            backgrounds_e_per_s=[1.0] * n_sci,
        )
        # Difference stamps should differ (different catalog + detector seeds).
        assert not np.array_equal(
            out_a.difference_stamps, out_b.difference_stamps
        ), "Different event IDs produced identical difference stamps (seed isolation failure)"


# ---------------------------------------------------------------------------
# AC-P7: Architecture boundary — no internal sensor leaf imports
# ---------------------------------------------------------------------------

class TestArchitectureBoundary:
    """AC-P7: pipeline.py must not import sensor leaf modules."""

    # Leaf physics modules that must NOT be imported by pipeline.py.
    _FORBIDDEN_SENSOR_MODULES = {
        "smig.sensor.charge_diffusion",
        "smig.sensor.ipc",
        "smig.sensor.persistence",
        "smig.sensor.nonlinearity",
        "smig.sensor.readout",
        "smig.sensor.noise.correlated",
        "smig.sensor.noise.cosmic_rays",
        "smig.sensor.calibration",
    }

    def test_no_forbidden_imports_via_ast(self) -> None:
        """Parse pipeline.py with the AST and check import statements."""
        pipeline_path = (
            Path(__file__).parent.parent / "pipeline.py"
        )
        assert pipeline_path.exists(), f"pipeline.py not found at {pipeline_path}"

        source = pipeline_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module)

        violations = imported & self._FORBIDDEN_SENSOR_MODULES
        assert not violations, (
            f"pipeline.py imports forbidden sensor leaf modules: {violations}"
        )

    def test_detector_config_import_allowed(self) -> None:
        """Importing DetectorConfig from smig.config.schemas must be present."""
        import smig.rendering.pipeline as pipeline_mod
        # The import is allowed; simply verify DetectorConfig is accessible
        # from the config module (not that it's re-exported by pipeline.py).
        from smig.config.schemas import DetectorConfig  # noqa: F401
        assert True  # Reaching here means the import works.


# ---------------------------------------------------------------------------
# Additional: input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    """Verify that simulate_event raises ValueError on inconsistent inputs."""

    def test_mismatched_source_params_length(
        self, simulator: SceneSimulator
    ) -> None:
        with pytest.raises(ValueError, match="source_params_sequence"):
            simulator.simulate_event(
                event_id="bad",
                source_params_sequence=_make_source_params(3),
                timestamps_mjd=_make_timestamps(2),
                backgrounds_e_per_s=[1.0, 1.0],
            )

    def test_mismatched_backgrounds_length(
        self, simulator: SceneSimulator
    ) -> None:
        with pytest.raises(ValueError, match="backgrounds_e_per_s"):
            simulator.simulate_event(
                event_id="bad2",
                source_params_sequence=_make_source_params(2),
                timestamps_mjd=_make_timestamps(2),
                backgrounds_e_per_s=[1.0],  # wrong length
            )
