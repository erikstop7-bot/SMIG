"""Tests for smig.datasets.splits — deterministic split assignment contract."""
from __future__ import annotations

from collections import Counter

import pytest

from smig.datasets.splits import assign_split

_VALID_SPLITS = frozenset({"train", "val", "test"})


class TestReturnValues:
    def test_returns_valid_split(self):
        result = assign_split("ev_001", 42, "tile_A", "star_1")
        assert result in _VALID_SPLITS

    def test_deterministic_same_inputs(self):
        a = assign_split("ev_001", 42, "tile_A", "star_1")
        b = assign_split("ev_001", 42, "tile_A", "star_1")
        assert a == b

    def test_deterministic_different_non_seed_args(self):
        """Same starfield_seed must produce same split regardless of other args."""
        a = assign_split("ev_001", 42, "tile_A", "star_1")
        b = assign_split("ev_999", 42, "tile_Z", "star_999")
        assert a == b


class TestWholeGroupInvariant:
    """Core contract: all events with the same starfield_seed → same split."""

    def test_500_events_same_seed_same_split(self):
        splits = {
            assign_split(f"ev_{i:05d}", 42, f"tile_{i}", f"star_{i}")
            for i in range(500)
        }
        assert len(splits) == 1, (
            f"Expected all 500 events with seed=42 to get the same split, "
            f"but got multiple splits: {splits}"
        )

    def test_invariant_holds_for_multiple_seeds(self):
        for seed in [0, 1, 7, 99, 12345, 999999]:
            splits = {
                assign_split(f"ev_{i}", seed, f"tile_{i}", f"star_{i}")
                for i in range(50)
            }
            assert len(splits) == 1, (
                f"Seed {seed}: expected all 50 events to get same split, got {splits}"
            )


class TestRatioConvergence:
    def test_ratios_within_2pct_on_10000_events(self):
        n = 10_000
        counts = Counter(
            assign_split(f"ev_{i}", i, "tile", "star")
            for i in range(n)
        )
        train_frac = counts["train"] / n
        val_frac = counts["val"] / n
        test_frac = counts["test"] / n

        assert abs(train_frac - 0.8) <= 0.02, (
            f"train fraction {train_frac:.4f} deviates >2% from 0.80"
        )
        assert abs(val_frac - 0.1) <= 0.02, (
            f"val fraction {val_frac:.4f} deviates >2% from 0.10"
        )
        assert abs(test_frac - 0.1) <= 0.02, (
            f"test fraction {test_frac:.4f} deviates >2% from 0.10"
        )

    def test_all_three_splits_populated(self):
        n = 1000
        splits_seen = {assign_split(f"ev_{i}", i, "t", "s") for i in range(n)}
        assert splits_seen == _VALID_SPLITS


class TestCustomRatios:
    def test_custom_ratios_respected(self):
        n = 5000
        counts = Counter(
            assign_split(f"ev_{i}", i, "t", "s", ratios=(0.6, 0.2, 0.2))
            for i in range(n)
        )
        assert abs(counts["train"] / n - 0.6) <= 0.03
        assert abs(counts["val"] / n - 0.2) <= 0.03
        assert abs(counts["test"] / n - 0.2) <= 0.03
