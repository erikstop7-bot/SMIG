"""Tests for smig.datasets.manifest — DatasetManifest append-only builder."""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import pytest

from smig.datasets.manifest import DatasetManifest


def _tmp_path() -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    f.close()
    return Path(f.name)


class TestAddEvent:
    def test_basic_append(self):
        m = DatasetManifest()
        m.add_event("ev_001", "train", 42, {"t_E": 30.0})
        assert len(m) == 1

    def test_multiple_appends(self):
        m = DatasetManifest()
        for i in range(5):
            m.add_event(f"ev_{i:03d}", "train", i * 1000, {"t_E": float(i + 1)})
        assert len(m) == 5

    def test_invalid_split_raises(self):
        m = DatasetManifest()
        with pytest.raises(ValueError, match="Invalid split"):
            m.add_event("ev_001", "bad_split", 42, {"t_E": 30.0})

    def test_float_seed_raises(self):
        m = DatasetManifest()
        with pytest.raises(TypeError):
            m.add_event("ev_001", "train", 42.0, {"t_E": 30.0})  # type: ignore[arg-type]

    def test_bool_seed_raises(self):
        m = DatasetManifest()
        with pytest.raises(TypeError):
            m.add_event("ev_001", "train", True, {"t_E": 30.0})  # type: ignore[arg-type]

    def test_nan_in_params_raises(self):
        m = DatasetManifest()
        with pytest.raises(ValueError):
            m.add_event("ev_001", "train", 42, {"t_E": float("nan")})

    def test_inf_in_params_raises(self):
        m = DatasetManifest()
        with pytest.raises(ValueError):
            m.add_event("ev_001", "train", 42, {"t_E": float("inf")})


class TestToJsonPath:
    def test_json_round_trip(self):
        m = DatasetManifest()
        m.add_event("ev_001", "train", 42, {"t_E": 30.0, "u_0": 0.1})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        assert "events" in data
        assert len(data["events"]) == 1
        ev = data["events"][0]
        assert ev["event_id"] == "ev_001"
        assert ev["split"] == "train"
        assert ev["starfield_seed"] == 42
        assert ev["params"]["t_E"] == pytest.approx(30.0)

    def test_starfield_seed_is_json_int(self):
        m = DatasetManifest()
        m.add_event("ev_001", "train", 12345, {"t_E": 30.0})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        seed = data["events"][0]["starfield_seed"]
        assert isinstance(seed, int)
        assert not isinstance(seed, bool)
        # JSON int: must not have decimal point in raw text
        text = p.read_text()
        assert '"starfield_seed": 12345' in text

    def test_params_keys_sorted(self):
        m = DatasetManifest()
        m.add_event("ev_001", "train", 1, {"z_param": 1.0, "a_param": 2.0, "m_param": 3.0})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        keys = list(data["events"][0]["params"].keys())
        assert keys == sorted(keys)

    def test_event_keys_sorted(self):
        m = DatasetManifest()
        m.add_event("ev_001", "train", 1, {"t_E": 30.0})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        keys = list(data["events"][0].keys())
        assert keys == sorted(keys)

    def test_top_level_has_events_key(self):
        m = DatasetManifest()
        m.add_event("ev_001", "val", 99, {"t_E": 10.0})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        assert list(data.keys()) == ["events"]

    def test_multiple_events_preserved_in_order(self):
        m = DatasetManifest()
        for i in range(3):
            m.add_event(f"ev_{i:03d}", "train", i * 100, {"t_E": float(i + 1) * 10})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        ids = [ev["event_id"] for ev in data["events"]]
        assert ids == ["ev_000", "ev_001", "ev_002"]

    def test_nested_params_keys_sorted(self):
        m = DatasetManifest()
        m.add_event("ev_001", "train", 1, {"z": {"b": 2.0, "a": 1.0}, "a": 3.0})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        nested = data["events"][0]["params"]["z"]
        assert list(nested.keys()) == sorted(nested.keys())

    def test_all_splits_accepted(self):
        m = DatasetManifest()
        for i, split in enumerate(["train", "val", "test"]):
            m.add_event(f"ev_{i:03d}", split, i * 1000, {"t_E": float(i + 5)})
        p = _tmp_path()
        m.to_json_path(p)
        data = json.loads(p.read_text())
        splits_written = [ev["split"] for ev in data["events"]]
        assert splits_written == ["train", "val", "test"]
