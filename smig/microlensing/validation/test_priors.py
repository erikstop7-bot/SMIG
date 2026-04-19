"""Priors sampler tests.

Fast tests: basic API, frozen output, event_class assignment.
Slow tests: statistical moment checks (marked @pytest.mark.slow).
"""
from __future__ import annotations

import dataclasses
import math
import numpy as np
import pytest

from smig.catalogs.base import StarRecord
from smig.microlensing.event import EventClass, MicrolensingEvent
from smig.microlensing.priors import sample_event


def _make_source(**overrides) -> StarRecord:
    defaults = dict(
        galactic_l_deg=1.0, galactic_b_deg=-1.5,
        distance_kpc=8.0, mass_msun=1.0,
        teff_K=5000.0, log_g=4.5, metallicity_feh=0.0,
        mag_F146_ab=18.0, source_id="s0", catalog_tile_id="t0",
    )
    defaults.update(overrides)
    return StarRecord(**defaults)


def _make_rng(seed: int = 0) -> np.random.Generator:
    return np.random.default_rng(seed)


class TestSampleEventAPI:
    def test_returns_microlensing_event(self):
        ev = sample_event(_make_rng(), _make_source(), event_id="ev-001")
        assert isinstance(ev, MicrolensingEvent)

    def test_returned_event_is_frozen(self):
        ev = sample_event(_make_rng(), _make_source(), event_id="ev-001")
        with pytest.raises(dataclasses.FrozenInstanceError):
            ev.u0 = 99.0  # type: ignore[misc]

    def test_event_id_propagated(self):
        ev = sample_event(_make_rng(), _make_source(), event_id="my-unique-id")
        assert ev.event_id == "my-unique-id"

    def test_theta_E_positive(self):
        ev = sample_event(_make_rng(), _make_source(), event_id="ev-theta")
        assert ev.theta_E_mas > 0.0

    def test_rho_positive(self):
        ev = sample_event(_make_rng(), _make_source(), event_id="ev-rho")
        assert ev.rho > 0.0

    def test_tE_positive(self):
        ev = sample_event(_make_rng(), _make_source(), event_id="ev-te")
        assert ev.tE_days > 0.0


class TestEventClassTarget:
    def test_pspl_target(self):
        ev = sample_event(_make_rng(1), _make_source(), event_id="pspl",
                          event_class_target=EventClass.PSPL)
        assert ev.event_class == EventClass.PSPL
        assert ev.q == 0.0
        assert ev.rho < 1e-3

    def test_hmc_target_u0_below_threshold(self):
        ev = sample_event(_make_rng(2), _make_source(), event_id="hmc",
                          event_class_target=EventClass.HIGH_MAGNIFICATION_CUSP)
        assert ev.event_class == EventClass.HIGH_MAGNIFICATION_CUSP
        assert ev.u0 < 0.05

    def test_planetary_target(self):
        ev = sample_event(_make_rng(3), _make_source(), event_id="planet",
                          event_class_target=EventClass.PLANETARY_CAUSTIC)
        assert ev.event_class == EventClass.PLANETARY_CAUSTIC
        assert ev.q < 0.03
        assert ev.u0 >= 0.05

    def test_stellar_binary_target(self):
        ev = sample_event(_make_rng(4), _make_source(), event_id="binary",
                          event_class_target=EventClass.STELLAR_BINARY)
        assert ev.event_class == EventClass.STELLAR_BINARY
        assert ev.q >= 0.03


class TestBackendProvenance:
    def test_pspl_backend_is_analytic(self):
        ev = sample_event(_make_rng(10), _make_source(), event_id="b-pspl",
                          event_class_target=EventClass.PSPL)
        assert ev.backend == "analytic"
        assert ev.backend_version == "N/A"

    def test_binary_backend_is_vbbl(self):
        ev = sample_event(_make_rng(11), _make_source(), event_id="b-bin",
                          event_class_target=EventClass.PLANETARY_CAUSTIC)
        assert ev.backend == "VBBinaryLensing"
        assert ev.backend_version == "3.7.0"


class TestLogGValidation:
    def test_invalid_logg_raises(self):
        bad = _make_source(log_g=7.0)  # above 6.0
        with pytest.raises(ValueError, match="log_g"):
            sample_event(_make_rng(), bad, event_id="bad-logg")

    def test_logg_below_range_raises(self):
        bad = _make_source(log_g=0.0)  # below 0.5
        with pytest.raises(ValueError, match="log_g"):
            sample_event(_make_rng(), bad, event_id="bad-logg-low")


@pytest.mark.slow
class TestPriorMoments:
    """Statistical moment tests — draw 10,000 events and check distributions."""

    @pytest.fixture(scope="class")
    def events(self):
        source = _make_source()
        rng = np.random.default_rng(99)
        evts = [sample_event(rng, source, event_id=f"bulk-{i}") for i in range(10_000)]
        return evts

    def test_u0_uniform_moments(self, events):
        u0s = np.array([e.u0 for e in events])
        # Should be roughly uniform over [0, 1.5]; check mean ≈ 0.75
        assert abs(np.mean(u0s) - 0.75) < 0.05, "u0 mean deviates from 0.75"

    def test_theta_E_positive_always(self, events):
        assert all(e.theta_E_mas > 0.0 for e in events)

    def test_rho_positive_always(self, events):
        assert all(e.rho > 0.0 for e in events)

    def test_event_class_distribution_nondegenerate(self, events):
        classes = [e.event_class for e in events]
        counts = {c: classes.count(c) for c in set(classes)}
        # At least 2 distinct classes in a sample of 10,000
        assert len(counts) >= 2, f"Only one event class observed: {counts}"
