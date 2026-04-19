"""VBBinaryLensing backend version pinning and verification.

Single source of truth: _PINNED_VERSION here.
test_backend_pin.py asserts this matches the "VBBinaryLensing==<version>" entry
in pyproject.toml [project.dependencies].
"""
from __future__ import annotations

import importlib.metadata

# PyPI distribution name — used with importlib.metadata.version()
_PINNED_DIST = "VBBinaryLensing"

# Logical backend identifier — written to MicrolensingEvent.backend for binary events.
# Intentionally kept as a separate constant from _PINNED_DIST: they happen to share
# the same string today, but the logical name and the PyPI distribution name are
# distinct concepts and must be independently updateable.
_BACKEND_NAME = "VBBinaryLensing"

# Pinned exact version — single source of truth; test enforces match to pyproject.toml.
_PINNED_VERSION = "3.7.0"

# Module-level assertion: fails loudly at import time if installed version drifts.
_installed = importlib.metadata.version(_PINNED_DIST)
assert _installed == _PINNED_VERSION, (
    f"VBBinaryLensing version mismatch: installed {_installed!r} != pinned "
    f"{_PINNED_VERSION!r}. Update pyproject.toml and _PINNED_VERSION together."
)


def get_primary_backend() -> tuple[str, str]:
    """Return (logical_backend_name, exact_version) for the pinned 2L1S backend."""
    return (_BACKEND_NAME, _PINNED_VERSION)
