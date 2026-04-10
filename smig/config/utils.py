"""
smig/config/utils.py
====================
Config loading and canonical hashing utilities.

These two functions are the sole sanctioned way to load a DetectorConfig from
disk and to compute its reproducibility fingerprint.  All pipeline stages that
need a config hash should call ``get_config_sha256`` rather than rolling their
own serialisation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from .schemas import DetectorConfig


def load_detector_config(path: str | Path) -> DetectorConfig:
    """Load and validate a DetectorConfig from a YAML file.

    Parameters
    ----------
    path:
        Path to the YAML configuration file.

    Returns
    -------
    DetectorConfig
        Fully validated, immutable detector configuration.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    yaml.YAMLError
        If the file content is not valid YAML.
    pydantic.ValidationError
        If the parsed YAML does not satisfy the DetectorConfig schema.
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(
            "Configuration file is empty or contains only comments."
        )
    if not isinstance(raw, dict):
        raise ValueError(
            f"Expected a YAML mapping at the top level, got {type(raw).__name__!r}."
        )
    return DetectorConfig.model_validate(raw)


def get_config_sha256(config: DetectorConfig) -> str:
    """Compute the SHA-256 fingerprint of a DetectorConfig.

    Uses ``model_dump_json(round_trip=True)`` for canonical serialisation so
    that two configs constructed from the same YAML (or with the same defaults)
    always produce identical hashes, regardless of construction path.

    Parameters
    ----------
    config:
        Fully validated detector configuration.

    Returns
    -------
    str
        64-character lowercase hexadecimal digest.
    """
    # Pydantic serializes fields in field-definition order (not YAML key order),
    # guaranteeing hash stability regardless of the original YAML key ordering.
    canonical = config.model_dump_json(round_trip=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
