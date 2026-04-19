"""Tests for smig.datasets.labels — frozen LabelVector contract."""
from __future__ import annotations

import dataclasses

import pytest

from smig.datasets.labels import EventClass, LabelVector, TOLERANCES
from smig.datasets.schema import LABEL_DATASET_NAMES


def _make_label() -> LabelVector:
    return LabelVector(
        event_class=EventClass.PSPL,
        log_tE=1.5,
        log_u0=-0.5,
        log_rho=-2.0,
        alpha_rad=0.0,
        log_q=-3.0,
        log_s=0.1,
        t0_mjd_normalized=0.5,
        source_mag_F146_ab=18.0,
        lens_mass_msun=0.3,
        source_distance_kpc=8.0,
        lens_distance_kpc=4.0,
    )


class TestFrozen:
    def test_cannot_set_field(self):
        lv = _make_label()
        with pytest.raises((AttributeError, dataclasses.FrozenInstanceError, TypeError)):
            lv.log_tE = 99.0  # type: ignore[misc]

    def test_cannot_delete_field(self):
        lv = _make_label()
        with pytest.raises((AttributeError, dataclasses.FrozenInstanceError, TypeError)):
            del lv.log_tE  # type: ignore[misc]


class TestFieldOrder:
    def test_dataclass_fields_match_label_dataset_names(self):
        """LabelVector field names must match LABEL_DATASET_NAMES (strip 'label__' prefix)."""
        lv_fields = [f.name for f in dataclasses.fields(LabelVector)]
        expected = [name[len("label__"):] for name in LABEL_DATASET_NAMES]
        assert lv_fields == expected, (
            f"LabelVector fields {lv_fields} do not match "
            f"LABEL_DATASET_NAMES-derived fields {expected}"
        )


class TestIterHdf5Datasets:
    def test_yields_all_dataset_names_exactly_once(self):
        lv = _make_label()
        pairs = list(lv.iter_hdf5_datasets())
        names = [name for name, _ in pairs]
        assert names == list(LABEL_DATASET_NAMES)

    def test_yields_correct_count(self):
        lv = _make_label()
        assert len(list(lv.iter_hdf5_datasets())) == len(LABEL_DATASET_NAMES)

    def test_event_class_encoded_as_uint8(self):
        lv = _make_label()
        pairs = dict(lv.iter_hdf5_datasets())
        ec_val = pairs["label__event_class"]
        assert isinstance(ec_val, int)
        assert 0 <= ec_val <= 4

    def test_pspl_encodes_to_zero(self):
        lv = _make_label()
        pairs = dict(lv.iter_hdf5_datasets())
        assert pairs["label__event_class"] == 0

    def test_all_float_fields_are_float(self):
        lv = _make_label()
        pairs = dict(lv.iter_hdf5_datasets())
        for name in LABEL_DATASET_NAMES:
            if name == "label__event_class":
                continue
            assert isinstance(pairs[name], float), f"{name} should be float"


class TestToLabelDict:
    def test_all_keys_present(self):
        lv = _make_label()
        d = lv.to_label_dict()
        expected_keys = {name[len("label__"):] for name in LABEL_DATASET_NAMES}
        assert set(d.keys()) == expected_keys

    def test_event_class_all_values(self):
        for cls in EventClass:
            lv = dataclasses.replace(_make_label(), event_class=cls)
            d = lv.to_label_dict()
            assert isinstance(d["event_class"], int)
            assert 0 <= d["event_class"] <= 4


class TestTolerances:
    def test_all_float_fields_have_tolerance(self):
        float_fields = [
            name[len("label__"):] for name in LABEL_DATASET_NAMES
            if name != "label__event_class"
        ]
        for field in float_fields:
            assert field in TOLERANCES, f"TOLERANCES missing entry for {field!r}"

    def test_all_tolerances_positive(self):
        for key, val in TOLERANCES.items():
            assert val > 0, f"TOLERANCES[{key!r}] must be positive"
