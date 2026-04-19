"""Tests for smig.datasets.schema — HDF5 layout constants."""
from __future__ import annotations

import inspect

import smig.datasets.schema as schema_mod
from smig.datasets.schema import (
    DATASET_SCHEMA_VERSION,
    HDF5_COMPRESSION,
    LABEL_DATASET_NAMES,
    SCIENCE_STAMP_SHAPE,
    science_stamp_chunks,
)


class TestSchemaVersion:
    def test_exact_version_string(self):
        assert DATASET_SCHEMA_VERSION == "phase3-contract-v1"

    def test_version_is_str(self):
        assert isinstance(DATASET_SCHEMA_VERSION, str)


class TestScienceStampShape:
    def test_shape(self):
        assert SCIENCE_STAMP_SHAPE == (64, 64)

    def test_is_tuple(self):
        assert isinstance(SCIENCE_STAMP_SHAPE, tuple)


class TestHdf5Compression:
    def test_codec(self):
        assert HDF5_COMPRESSION[0] == "gzip"

    def test_level(self):
        assert HDF5_COMPRESSION[1] == 4

    def test_is_tuple(self):
        assert isinstance(HDF5_COMPRESSION, tuple)


class TestScienceStampChunks:
    def test_returns_correct_shape(self):
        assert science_stamp_chunks(9) == (1, 9, 64, 64)

    def test_n_epochs_1(self):
        assert science_stamp_chunks(1) == (1, 1, 64, 64)

    def test_n_epochs_50(self):
        assert science_stamp_chunks(50) == (1, 50, 64, 64)

    def test_returns_tuple(self):
        assert isinstance(science_stamp_chunks(9), tuple)
        assert len(science_stamp_chunks(9)) == 4


class TestLabelDatasetNames:
    def test_all_prefixed(self):
        for name in LABEL_DATASET_NAMES:
            assert name.startswith("label__"), f"{name!r} lacks 'label__' prefix"

    def test_expected_count(self):
        assert len(LABEL_DATASET_NAMES) == 12

    def test_event_class_first(self):
        assert LABEL_DATASET_NAMES[0] == "label__event_class"

    def test_no_duplicates(self):
        assert len(set(LABEL_DATASET_NAMES)) == len(LABEL_DATASET_NAMES)

    def test_is_tuple(self):
        assert isinstance(LABEL_DATASET_NAMES, tuple)


class TestNoCompoundDtypes:
    def test_no_compound_dtype_in_source(self):
        src = inspect.getsource(schema_mod)
        assert "np.dtype([" not in src, "schema.py must not define compound numpy dtypes"
