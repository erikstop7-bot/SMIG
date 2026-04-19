"""smig/datasets/labels.py
=========================
Frozen LabelVector and EventClass re-export for the SMIG v2 Phase 3.4 dataset contract.

CONTRACT FROZEN as of Phase 3.4. The LabelVector field list, field order, and dtypes
are LOCKED. Any change requires a new DATASET_SCHEMA_VERSION and explicit phase sign-off.

EventClass uint8 HDF5 encoding (stable — do NOT reorder):
    PSPL                   = 0
    FSPL_STAR              = 1
    PLANETARY_CAUSTIC      = 2
    STELLAR_BINARY         = 3
    HIGH_MAGNIFICATION_CUSP = 4

Field order in LabelVector maps 1-to-1 to LABEL_DATASET_NAMES in schema.py.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Iterator

from smig.microlensing.event import EventClass  # re-export
from smig.datasets.schema import LABEL_DATASET_NAMES

# Stable uint8 encoding: index is the HDF5 stored value. DO NOT reorder.
_EVENT_CLASS_ORDER: tuple[EventClass, ...] = (
    EventClass.PSPL,
    EventClass.FSPL_STAR,
    EventClass.PLANETARY_CAUSTIC,
    EventClass.STELLAR_BINARY,
    EventClass.HIGH_MAGNIFICATION_CUSP,
)
_EVENT_CLASS_TO_UINT8: dict[EventClass, int] = {
    cls: i for i, cls in enumerate(_EVENT_CLASS_ORDER)
}

# Shared tolerance constants for scientific regression tests.
# Prevent drift between microlensing unit tests and Phase 3.6 wrapper tests.
TOLERANCES: dict[str, float] = {
    "log_tE": 1e-4,
    "log_u0": 1e-4,
    "log_rho": 1e-4,
    "alpha_rad": 1e-5,
    "log_q": 1e-4,
    "log_s": 1e-4,
    "t0_mjd_normalized": 1e-6,
    "source_mag_F146_ab": 1e-3,
    "lens_mass_msun": 1e-4,
    "source_distance_kpc": 1e-4,
    "lens_distance_kpc": 1e-4,
}


@dataclasses.dataclass(frozen=True)
class LabelVector:
    """Frozen label record for one microlensing event.

    Field order matches LABEL_DATASET_NAMES in schema.py. DO NOT reorder fields.
    """

    event_class: EventClass
    log_tE: float
    log_u0: float
    log_rho: float
    alpha_rad: float
    log_q: float
    log_s: float
    t0_mjd_normalized: float
    source_mag_F146_ab: float
    lens_mass_msun: float
    source_distance_kpc: float
    lens_distance_kpc: float

    def to_label_dict(self) -> dict[str, Any]:
        """Return a flat dict with all label values; event_class encoded as uint8."""
        return {
            "event_class": _EVENT_CLASS_TO_UINT8[self.event_class],
            "log_tE": float(self.log_tE),
            "log_u0": float(self.log_u0),
            "log_rho": float(self.log_rho),
            "alpha_rad": float(self.alpha_rad),
            "log_q": float(self.log_q),
            "log_s": float(self.log_s),
            "t0_mjd_normalized": float(self.t0_mjd_normalized),
            "source_mag_F146_ab": float(self.source_mag_F146_ab),
            "lens_mass_msun": float(self.lens_mass_msun),
            "source_distance_kpc": float(self.source_distance_kpc),
            "lens_distance_kpc": float(self.lens_distance_kpc),
        }

    def iter_hdf5_datasets(self) -> Iterator[tuple[str, Any]]:
        """Yield (hdf5_dataset_name, value) for every label field, in LABEL_DATASET_NAMES order."""
        d = self.to_label_dict()
        for dataset_name in LABEL_DATASET_NAMES:
            field = dataset_name[len("label__"):]
            yield dataset_name, d[field]
