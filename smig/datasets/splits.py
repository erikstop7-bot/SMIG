"""smig/datasets/splits.py
=========================
Deterministic split assignment for the SMIG v2 Phase 3.4 dataset contract.

CONTRACT FROZEN as of Phase 3.4. The hash algorithm and bucket boundaries are LOCKED.

Split rule (purely a function of starfield_seed):
    bucket = int.from_bytes(sha256(str(starfield_seed)).digest()[:8], "little") % 10000
    train:  bucket in [0, 8000)
    val:    bucket in [8000, 9000)
    test:   bucket in [9000, 10000)

All events sharing a starfield_seed are guaranteed to receive the same split label.
catalog_tile_id and source_star_id are accepted as arguments for inclusion in
manifest.params (Phase 4 auditing) but do NOT affect the split assignment.
"""
from __future__ import annotations

import hashlib
from typing import Literal


def assign_split(
    event_id: str,
    starfield_seed: int,
    catalog_tile_id: str,
    source_star_id: str,
    ratios: tuple[float, float, float] = (0.8, 0.1, 0.1),
) -> Literal["train", "val", "test"]:
    """Return the split label for an event, determined solely by starfield_seed.

    The assignment is a pure function of starfield_seed: any two calls with the
    same starfield_seed will always return the same split, regardless of event_id,
    catalog_tile_id, or source_star_id.

    Parameters
    ----------
    event_id:
        Unique event identifier (unused in assignment; accepted for caller symmetry).
    starfield_seed:
        Integer seed identifying the starfield rendering. All events sharing this
        seed must land in the same split — this invariant is enforced by this function.
    catalog_tile_id:
        Catalog tile identifier. Included in manifest.params for Phase 4 auditing;
        does NOT affect split assignment.
    source_star_id:
        Source star identifier. Included in manifest.params for Phase 4 auditing;
        does NOT affect split assignment.
    ratios:
        (train_fraction, val_fraction, test_fraction). Must sum to 1.0.
        Bucket boundaries are computed as integer multiples of 10000.
    """
    digest = hashlib.sha256(f"{starfield_seed}".encode()).digest()
    bucket = int.from_bytes(digest[:8], "little") % 10000
    train_end = int(ratios[0] * 10000)
    val_end = train_end + int(ratios[1] * 10000)
    if bucket < train_end:
        return "train"
    if bucket < val_end:
        return "val"
    return "test"
