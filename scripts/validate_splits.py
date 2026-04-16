#!/usr/bin/env python3
"""
scripts/validate_splits.py
==========================
Data leakage prevention CLI for SMIG v2 training datasets.

Reads a JSON manifest and checks three types of leakage:

(a) **Duplicate event IDs**: no ``event_id`` may appear in more than one split.
(b) **Shared starfield seeds**: no ``starfield_seed`` may be shared across splits.
(c) **Parameter similarity**: events whose *all* microlensing parameters are
    within 5%% of each other must be in the same split.

Manifest schema
---------------
.. code-block:: json

    {
        "events": [
            {
                "event_id": "ob230001",
                "split": "train",
                "starfield_seed": 42,
                "params": {
                    "t_E": 30.0,
                    "u_0": 0.1,
                    "s": 1.0,
                    "q": 0.001
                }
            },
            ...
        ]
    }

``split`` must be one of ``"train"``, ``"val"``, or ``"test"``.

Parameter similarity definition
---------------------------------
Two events are "parameter-similar" when, for every key present in their
``params`` dicts, the symmetric relative difference satisfies:

    abs(a - b) / max(abs(a), abs(b), 1e-9) <= 0.05

This O(N²) MVP check is intentionally simple; production use at scale would
require an indexed approximate-nearest-neighbour search.

Exit codes
----------
* ``0`` — all checks pass (safe to proceed with training).
* ``1`` — at least one violation found (training must NOT proceed).

Usage
-----
::

    python scripts/validate_splits.py path/to/manifest.json

"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Similarity check
# ---------------------------------------------------------------------------

def _params_within_5pct(params_a: dict, params_b: dict) -> bool:
    """Return ``True`` if every parameter in both dicts is within 5%% of the other.

    Uses a symmetric relative difference with an absolute floor to handle
    near-zero parameter values safely:

        |a - b| / max(|a|, |b|, 1e-9) <= 0.05

    Parameters
    ----------
    params_a, params_b:
        Dicts mapping parameter name → float value.  Both dicts must contain
        the same keys; any key absent from either dict causes ``False``.

    Returns
    -------
    bool
        ``True`` when ALL pairwise comparisons satisfy the 5%% criterion.
    """
    all_keys = set(params_a) | set(params_b)
    for key in all_keys:
        if key not in params_a or key not in params_b:
            return False
        a = float(params_a[key])
        b = float(params_b[key])
        denom = max(abs(a), abs(b), 1e-9)
        if abs(a - b) / denom > 0.05:
            return False
    return True


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def validate_manifest(manifest: dict) -> list[str]:
    """Validate *manifest* for data leakage.  Return list of violation strings.

    An empty list means the manifest is clean.

    Parameters
    ----------
    manifest:
        Parsed JSON object with an ``"events"`` list.

    Returns
    -------
    list[str]
        Human-readable violation messages, one per detected problem.
    """
    events: list[dict] = manifest.get("events", [])
    violations: list[str] = []

    # ------------------------------------------------------------------
    # (a) No event_id in multiple splits
    # ------------------------------------------------------------------
    event_id_to_split: dict[str, str] = {}
    for ev in events:
        eid = str(ev["event_id"])
        split = str(ev["split"])
        if eid in event_id_to_split:
            if event_id_to_split[eid] != split:
                violations.append(
                    f"event_id '{eid}' appears in both split "
                    f"'{event_id_to_split[eid]}' and split '{split}'"
                )
        else:
            event_id_to_split[eid] = split

    # ------------------------------------------------------------------
    # (b) No starfield_seed shared across splits
    # ------------------------------------------------------------------
    seed_to_split: dict[int, str] = {}
    seed_to_event: dict[int, str] = {}
    for ev in events:
        seed = int(ev["starfield_seed"])
        split = str(ev["split"])
        eid = str(ev["event_id"])
        if seed in seed_to_split:
            if seed_to_split[seed] != split:
                violations.append(
                    f"starfield_seed {seed} is shared between "
                    f"event '{seed_to_event[seed]}' (split='{seed_to_split[seed]}') "
                    f"and event '{eid}' (split='{split}')"
                )
        else:
            seed_to_split[seed] = split
            seed_to_event[seed] = eid

    # ------------------------------------------------------------------
    # (c) Parameter similarity: events within 5%% of each other must be
    #     in the same split (O(N²) MVP loop).
    # ------------------------------------------------------------------
    n = len(events)
    for i in range(n):
        for j in range(i + 1, n):
            ev_a = events[i]
            ev_b = events[j]
            if ev_a["split"] == ev_b["split"]:
                # Same split — similarity is fine, no leakage risk.
                continue
            if _params_within_5pct(ev_a["params"], ev_b["params"]):
                violations.append(
                    f"events '{ev_a['event_id']}' (split='{ev_a['split']}') "
                    f"and '{ev_b['event_id']}' (split='{ev_b['split']}') "
                    f"have all parameters within 5%% of each other — "
                    f"potential parameter-space leakage across splits"
                )

    return violations


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Parse arguments, validate manifest, print results, return exit code."""
    parser = argparse.ArgumentParser(
        prog="validate_splits",
        description=(
            "Validate a SMIG dataset manifest for data leakage before training."
        ),
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to the JSON manifest file.",
    )
    args = parser.parse_args(argv)

    manifest_path: Path = args.manifest
    if not manifest_path.exists():
        print(f"ERROR: manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {manifest_path}: {exc}", file=sys.stderr)
        return 1

    violations = validate_manifest(manifest_data)

    if violations:
        print(
            f"FAILED — {len(violations)} data leakage violation(s) detected:",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  VIOLATION: {v}", file=sys.stderr)
        return 1

    n_events = len(manifest_data.get("events", []))
    print(
        f"OK — all leakage checks passed ({n_events} events validated).",
        file=sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
