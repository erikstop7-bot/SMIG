"""smig/datasets/schema.py
========================
HDF5 shard layout constants for the SMIG v2 Phase 3.4 dataset contract.

CONTRACT FROZEN as of Phase 3.4. DATASET_SCHEMA_VERSION, LABEL_DATASET_NAMES,
SCIENCE_STAMP_SHAPE, and HDF5_COMPRESSION are LOCKED. Any structural change
requires a new schema_version string and explicit phase sign-off.

HDF5 flat layout (one file per shard):
  /science_stamps       float32  (N, n_epochs, 64, 64)   chunk (1, n_epochs, 64, 64)
  /saturation_stamps    uint8    (N, n_epochs, 64, 64)   — omit if Phase 2 did not produce
  /cr_stamps            uint8    (N, n_epochs, 64, 64)   — omit if Phase 2 did not produce
  /label__event_class   uint8    (N,)
  /label__log_tE        float32  (N,)
  /label__log_u0        float32  (N,)
  /label__log_rho       float32  (N,)
  /label__alpha_rad     float32  (N,)
  /label__log_q         float32  (N,)
  /label__log_s         float32  (N,)
  /label__t0_mjd_normalized  float32  (N,)
  /label__source_mag_F146_ab float32  (N,)
  /label__lens_mass_msun     float32  (N,)
  /label__source_distance_kpc float32 (N,)
  /label__lens_distance_kpc  float32  (N,)
  /event_id             variable-length string  (N,)
  /starfield_seed       uint64   (N,)   values < 2^53 for JSON safety
  /shard_row_index      uint32   (N,)

File attributes:
  schema_version  str   "phase3-contract-v1"
  shard_id        int
  n_epochs        int   (per-dataset, NOT a compile-time constant)
  smig_version    str
  writer_backend  str   "h5py"

Compression: gzip level 4 (h5py built-in). No third-party codecs or alternative serialization backends.
"""
from __future__ import annotations

DATASET_SCHEMA_VERSION: str = "phase3-contract-v1"

SCIENCE_STAMP_SHAPE: tuple[int, int] = (64, 64)

HDF5_COMPRESSION: tuple[str, int] = ("gzip", 4)

# Frozen field order — must match LabelVector dataclass field order in labels.py.
LABEL_DATASET_NAMES: tuple[str, ...] = (
    "label__event_class",
    "label__log_tE",
    "label__log_u0",
    "label__log_rho",
    "label__alpha_rad",
    "label__log_q",
    "label__log_s",
    "label__t0_mjd_normalized",
    "label__source_mag_F146_ab",
    "label__lens_mass_msun",
    "label__source_distance_kpc",
    "label__lens_distance_kpc",
)


def science_stamp_chunks(n_epochs: int) -> tuple[int, int, int, int]:
    """Return chunk shape for /science_stamps enabling O(1) DataLoader access."""
    return (1, n_epochs, 64, 64)
