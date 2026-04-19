"""smig.microlensing — Phase 3.2 microlensing physics engine."""
from __future__ import annotations

from smig.microlensing.backends import get_primary_backend
from smig.microlensing.errors import ClaretGridError, MicrolensingComputationError
from smig.microlensing.event import EventClass, MicrolensingEvent, SourceProperties
from smig.microlensing.priors import sample_event

__all__ = [
    "EventClass",
    "MicrolensingEvent",
    "SourceProperties",
    "get_primary_backend",
    "sample_event",
    "MicrolensingComputationError",
    "ClaretGridError",
]
