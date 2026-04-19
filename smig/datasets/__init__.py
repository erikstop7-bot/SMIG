"""smig.datasets — frozen Phase 3.4 dataset contract.

CONTRACT FROZEN as of Phase 3.4. Public symbols below are LOCKED.
"""
from smig.datasets.labels import EventClass, LabelVector, TOLERANCES
from smig.datasets.splits import assign_split
from smig.datasets.schema import (
    DATASET_SCHEMA_VERSION,
    HDF5_COMPRESSION,
    LABEL_DATASET_NAMES,
    SCIENCE_STAMP_SHAPE,
    science_stamp_chunks,
)
from smig.datasets.manifest import DatasetManifest

__all__ = [
    "EventClass",
    "LabelVector",
    "TOLERANCES",
    "assign_split",
    "DATASET_SCHEMA_VERSION",
    "HDF5_COMPRESSION",
    "LABEL_DATASET_NAMES",
    "SCIENCE_STAMP_SHAPE",
    "science_stamp_chunks",
    "DatasetManifest",
]
