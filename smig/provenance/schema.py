"""
smig/provenance/schema.py
=========================
Pydantic v2 model representing a single epoch's provenance record.

One ProvenanceRecord is created after each detector-simulation epoch
(i.e. after each simulated exposure in a multi-epoch microlensing event).
A list of these records is accumulated by ProvenanceTracker and serialised
as a JSON sidecar alongside the output FITS/HDF5 products.

Pydantic v2 is required (>= 2.0).
"""

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


def sanitize_rng_state(state: dict[str, Any]) -> dict[str, Any]:
    """Recursively convert numpy types in an RNG state dict to native Python.

    Converts ``np.ndarray`` -> list and ``np.generic`` -> Python scalar,
    traversing nested dicts and sequences.  Safe to call even when numpy is
    not installed (returns the input unchanged in that case).

    Parameters
    ----------
    state:
        A dict as returned by ``numpy.random.Generator.bit_generator.state``.

    Returns
    -------
    dict[str, Any]
        The same structure with all numpy types replaced by native Python types,
        making the result safe to pass to ``json.dumps``.
    """
    try:
        import numpy as np
    except ImportError:
        return state

    def _convert(obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, dict):
            return {k: _convert(val) for k, val in obj.items()}
        if isinstance(obj, (list, tuple)):
            converted = (_convert(item) for item in obj)
            return type(obj)(converted)
        return obj

    return _convert(state)


class ProvenanceRecord(BaseModel):
    """Immutable audit record for one simulated epoch of one microlensing event.

    All fields are required at construction time (no defaults) to force the
    caller to populate every provenance dimension explicitly.

    Timezone requirement
    --------------------
    ``timestamp_utc`` uses Pydantic's ``AwareDatetime`` type, which rejects
    naive (timezone-unaware) datetime objects at validation time.  Callers
    must supply a timezone-aware value, e.g.::

        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc)

    NumPy random-state snapshot
    ---------------------------
    The ``random_state`` field holds the dict returned by
    ``numpy.random.Generator.bit_generator.state``, e.g.::

        rng = numpy.random.default_rng(seed=42)
        state = rng.bit_generator.state   # {"bit_generator": "PCG64", ...}

    A field validator (``mode="before"``) recursively sanitizes the dict,
    converting ``np.ndarray`` to lists and ``np.generic`` scalars to native
    Python types so the output is cleanly JSON-serializable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # ------------------------------------------------------------------
    # Event / epoch identity
    # ------------------------------------------------------------------

    event_id: str = Field(
        description=(
            "Unique string identifier for the microlensing event, e.g. "
            "'ob230001' or a UUID.  All epochs belonging to the same event "
            "share this identifier."
        ),
    )
    epoch_index: int = Field(
        ge=0,
        description=(
            "Zero-based index of this epoch within the event's observation "
            "sequence.  Together with event_id this forms a unique primary key."
        ),
    )

    # ------------------------------------------------------------------
    # Wall-clock / audit metadata
    # ------------------------------------------------------------------

    timestamp_utc: AwareDatetime = Field(
        description=(
            "UTC timestamp at which this epoch's simulation completed.  "
            "Must be timezone-aware (naive datetimes are rejected at "
            "validation time).  Serialised to ISO-8601 string."
        ),
    )

    # ------------------------------------------------------------------
    # Software / environment fingerprints
    # ------------------------------------------------------------------

    git_commit: str | None = Field(
        description=(
            "Git commit identifier (SHA-1 or SHA-256 hex string) of the "
            "source code used to produce this epoch, or None if the "
            "environment variable GIT_COMMIT_SHA was not set (e.g. in a "
            "local development run outside CI)."
        ),
    )
    container_digest: str | None = Field(
        description=(
            "OCI container image digest (e.g. 'sha256:abc123...') of the "
            "execution environment, or None if the environment variable "
            "IMAGE_DIGEST was not set."
        ),
    )
    python_version: str = Field(
        description=(
            "Python interpreter version string (e.g. '3.11.7'), captured "
            "via ``platform.python_version()`` at simulation time."
        ),
    )
    numpy_version: str = Field(
        description=(
            "NumPy package version string (e.g. '1.26.3'), captured via "
            "``numpy.__version__`` at simulation time."
        ),
    )

    # ------------------------------------------------------------------
    # Configuration fingerprint
    # ------------------------------------------------------------------

    config_sha256: str = Field(
        min_length=64,
        max_length=64,
        description=(
            "SHA-256 hex digest of the canonical JSON serialisation of the "
            "DetectorConfig used for this epoch.  Allows downstream users to "
            "verify that two epochs used identical detector settings even if "
            "the YAML source file has changed."
        ),
    )

    # ------------------------------------------------------------------
    # Reproducibility: PRNG state
    # ------------------------------------------------------------------

    random_state: dict[str, Any] = Field(
        description=(
            "Full NumPy bit-generator state snapshot captured immediately "
            "before this epoch's stochastic stages (dark current, read noise, "
            "cosmic rays, etc.).  Must contain at least the keys 'bit_generator' "
            "and 'state' as returned by "
            "``numpy.random.Generator.bit_generator.state``.  "
            "NumPy types are sanitized to native Python before storage."
        ),
    )

    @field_validator("random_state", mode="before")
    @classmethod
    def _sanitize_numpy_types(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Delegate to the module-level sanitize_rng_state function."""
        return sanitize_rng_state(v)

    # ------------------------------------------------------------------
    # Applied-effect flags
    # ------------------------------------------------------------------

    ipc_applied: bool = Field(
        description=(
            "True if inter-pixel capacitance convolution was applied to this "
            "epoch's charge image."
        ),
    )
    persistence_applied: bool = Field(
        description=(
            "True if residual-image (persistence) charge was injected into "
            "this epoch."
        ),
    )
    nonlinearity_applied: bool = Field(
        description=(
            "True if the polynomial detector nonlinearity model was applied "
            "to convert accumulated charge to measured signal."
        ),
    )
    charge_diffusion_applied: bool = Field(
        description=(
            "True if the charge diffusion and brighter-fatter effect model "
            "was applied to this epoch's charge image."
        ),
    )

    # ------------------------------------------------------------------
    # Per-epoch pixel-level statistics
    # ------------------------------------------------------------------

    saturated_pixel_count: int = Field(
        ge=0,
        description=(
            "Number of pixels that reached or exceeded the saturation flag "
            "threshold (nonlinearity.saturation_flag_threshold x full_well) "
            "in this epoch."
        ),
    )
    cosmic_ray_hit_count: int = Field(
        ge=0,
        description=(
            "Number of individual cosmic-ray strike events injected into "
            "this epoch's ramp."
        ),
    )
