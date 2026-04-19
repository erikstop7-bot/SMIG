"""smig/datasets/manifest.py
===========================
Append-only DatasetManifest builder and canonical JSON emitter for the SMIG v2
Phase 3.4 dataset contract.

CONTRACT FROZEN as of Phase 3.4. The JSON manifest shape and serialization rules
below are LOCKED. Any structural change is a versioned migration.

Manifest JSON shape (must match scripts/validate_splits.py exactly):
---------------------------------------------------------------------------
{
    "events": [
        {
            "event_id": "<str>",
            "split": "train" | "val" | "test",
            "starfield_seed": <int>,   // plain integer, never float, never bool
            "params": {                // flat or nested dict, all-finite floats
                "t_E": 30.0,
                "u_0": 0.1,
                ...
            }
        },
        ...
    ]
}

Required event keys (from scripts/validate_splits.py):
    event_id, split, starfield_seed, params

Validator constraints enforced by scripts/validate_splits.py:
    1. split must be "train", "val", or "test".
    2. starfield_seed must be a plain int (float and bool are rejected).
    3. Duplicate event_id within or across splits → violation.
    4. Duplicate starfield_seed within any split → violation.
    5. Same starfield_seed in different splits → leakage violation.
       (Consequence: each starfield_seed must be globally unique across all events.)
    6. Parameter-similarity Union-Find at 5% threshold:
           |a - b| / max(|a|, |b|, 1e-9) <= 0.05  for ALL shared param keys
       Connected components spanning multiple splits → leakage violation.

Serialization rules:
    - All dict keys sorted throughout (sort_keys=True).
    - starfield_seed written as JSON integer (int, not float).
    - No NaN or Inf anywhere in params (validated at insert and at serialize).
    - Analytics sidecars: not produced in this phase; may be added in Phase 4.

Note: DatasetManifest is NOT frozen=True — it uses controlled mutation via .add_event()
only. Do not add any other mutating methods.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _canonicalize(obj: Any) -> Any:
    """Recursively sort dict keys and reject NaN/Inf floats."""
    if isinstance(obj, dict):
        return {k: _canonicalize(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [_canonicalize(item) for item in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError(f"NaN/Inf not allowed in manifest params: {obj!r}")
        return obj
    return obj


class DatasetManifest:
    """Append-only manifest builder that emits validator-compatible JSON.

    Mutation is only permitted via .add_event(). No other mutating methods exist.
    """

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def add_event(
        self,
        event_id: str,
        split: str,
        starfield_seed: int,
        params: dict[str, Any],
    ) -> None:
        """Append one event record to the manifest.

        Parameters
        ----------
        event_id:
            Unique string identifier for this event.
        split:
            One of "train", "val", "test".
        starfield_seed:
            Integer seed. Must be a plain int (not float, not bool).
            Values < 2^53 are required for JSON-safe serialization.
        params:
            Dict of microlensing parameters. All float values must be finite.
            Nested dicts are allowed; keys are sorted recursively at insert time.

        Raises
        ------
        ValueError
            If split is invalid or params contain NaN/Inf.
        TypeError
            If starfield_seed is not an int, or is a bool.
        """
        if split not in {"train", "val", "test"}:
            raise ValueError(f"Invalid split {split!r}: must be 'train', 'val', or 'test'")
        if isinstance(starfield_seed, bool):
            raise TypeError(f"starfield_seed must be int, got bool")
        if not isinstance(starfield_seed, int):
            raise TypeError(
                f"starfield_seed must be int, got {type(starfield_seed).__name__!r}"
            )
        canonical_params = _canonicalize(params)
        self._events.append(
            {
                "event_id": str(event_id),
                "split": split,
                "starfield_seed": int(starfield_seed),
                "params": canonical_params,
            }
        )

    def to_json_path(self, path: Path) -> None:
        """Write the manifest as canonical JSON to *path*.

        Serialization guarantees:
            - All dict keys sorted (sort_keys=True propagates through all nesting).
            - starfield_seed is a JSON integer (no decimal point).
            - NaN/Inf raise ValueError (allow_nan=False).
        """
        data: dict[str, Any] = {"events": list(self._events)}
        text = json.dumps(data, sort_keys=True, indent=2, allow_nan=False)
        Path(path).write_text(text, encoding="utf-8")

    def __len__(self) -> int:
        return len(self._events)
