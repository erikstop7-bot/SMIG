"""
smig/sensor/detector.py
========================
Star-topology orchestrator for the Roman WFI H4RG-10 detector simulation.

H4RG10Detector is the sole orchestrator in the signal chain.  Leaf modules
(ipc, charge_diffusion, etc.) are owned by the detector and must not import
each other.

Fixed signal chain order (CLAUDE.md §Architectural Constraints):
    charge diffusion → IPC → persistence → MULTIACCUM readout (with per-read NL)
    → noise injection (1/f, RTS, cosmic rays)
"""

from __future__ import annotations

import gc
import os
import platform
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

from smig.config.schemas import DetectorConfig
from smig.config.utils import get_config_sha256
from smig.provenance.schema import ProvenanceRecord, sanitize_rng_state
from smig.sensor.charge_diffusion import ChargeDiffusionModel
from smig.sensor.ipc import FieldDependentIPC
from smig.sensor.noise.correlated import OneOverFNoise, RTSNoise
from smig.sensor.noise.cosmic_rays import ClusteredCosmicRayInjector
from smig.sensor.nonlinearity import NonLinearityModel
from smig.sensor.persistence import DynamicPersistence
from smig.sensor.readout import MultiAccumSimulator

# MJD epoch: 1858-11-17 00:00:00 UTC
_MJD_EPOCH = datetime(1858, 11, 17, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Output data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DetectorOutput:
    """Per-epoch detector simulation result.

    Note: ``frozen=True`` freezes attribute *bindings* (``self.rate_image``
    cannot be rebound to a different array), but the ``np.ndarray`` contents
    remain mutable.  This is a deliberate trade-off: deep immutability of large
    arrays is prohibitively expensive.

    Attributes
    ----------
    rate_image:
        2D float64 array (ny, nx) of electron counts after the full signal chain.
    saturation_mask:
        2D bool array (ny, nx); True where charge met or exceeded the saturation
        flag threshold.
    cr_mask:
        2D bool array (ny, nx); True at pixels struck by cosmic rays.
    provenance_data:
        Dict containing exactly the 12 ``ProvenanceRecord`` constructor kwargs
        that are not supplied by ``process_event``:
        ``git_commit``, ``container_digest``, ``python_version``,
        ``numpy_version``, ``config_sha256``, ``random_state``,
        ``ipc_applied``, ``persistence_applied``, ``nonlinearity_applied``,
        ``charge_diffusion_applied``,
        ``saturated_pixel_count``, ``cosmic_ray_hit_count``.
    """

    rate_image: np.ndarray
    saturation_mask: np.ndarray
    cr_mask: np.ndarray
    provenance_data: dict[str, Any]


@dataclass(frozen=True)
class EventOutput:
    """Multi-epoch event simulation result.

    Note: ``frozen=True`` freezes attribute bindings; ``np.ndarray`` contents
    remain mutable.  See ``DetectorOutput`` docstring.

    Attributes
    ----------
    rate_cube:
        3D float64 array (n_epochs, ny, nx).
    saturation_cube:
        3D bool array (n_epochs, ny, nx).
    cr_cube:
        3D bool array (n_epochs, ny, nx).
    persistence_peak_map:
        2D float64 array (ny, nx); maximum persistence signal seen across all
        epochs (stub: all zeros).
    provenance_records:
        One ``ProvenanceRecord`` per epoch, in epoch-index order.
    peak_memory_mb:
        Peak resident memory consumed during ``process_event`` in megabytes
        (stub: 0.0).
    """

    rate_cube: np.ndarray
    saturation_cube: np.ndarray
    cr_cube: np.ndarray
    persistence_peak_map: np.ndarray
    provenance_records: list[ProvenanceRecord]
    peak_memory_mb: float


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class H4RG10Detector:
    """Star-topology orchestrator for the Roman WFI H4RG-10 detector.

    Owns all leaf-module instances and drives the fixed signal chain:
    charge diffusion → IPC → persistence → MULTIACCUM readout (with per-read NL)
    → noise injection.

    Parameters
    ----------
    config:
        Fully validated, immutable detector configuration.
    rng:
        NumPy random generator consumed by noise leaf modules for reproducible
        stochastic realizations.

    Notes
    -----
    ``config_sha256`` is computed once at construction time.  Because
    ``DetectorConfig`` is frozen, the hash cannot change for the lifetime of
    this object.
    """

    def __init__(self, config: DetectorConfig, rng: np.random.Generator) -> None:
        self._config = config
        self._rng = rng
        self._config_sha256 = get_config_sha256(config)
        self._git_commit: str | None = os.environ.get("GIT_COMMIT_SHA")
        self._container_digest: str | None = os.environ.get("IMAGE_DIGEST")

        # Leaf module instances (star topology: detector owns all, none import peers).
        # Exception: readout.py imports nonlinearity.py (one-way, documented in readout.py).
        self._charge_diffusion = ChargeDiffusionModel(config)
        self._ipc = FieldDependentIPC(config.ipc)
        self._persistence = DynamicPersistence(config.persistence)
        # NonLinearityModel must be created before MultiAccumSimulator: it is
        # injected into the readout simulator so NL can be applied per-read
        # when the 3D MULTIACCUM ramp is implemented.
        self._nonlinearity = NonLinearityModel(
            config.nonlinearity,
            full_well_electrons=config.electrical.full_well_electrons,
        )
        self._readout = MultiAccumSimulator(
            config.readout,
            dark_current_e_per_s=config.electrical.dark_current_e_per_s,
            read_noise_cds_electrons=config.electrical.read_noise_cds_electrons,
            nonlinearity=self._nonlinearity,
        )

        # Spawn independent, deterministic child RNGs for each noise module.
        # SeedSequence.spawn guarantees zero correlation between child streams.
        # Reproducibility contract: the parent RNG state captured per-epoch is
        # sufficient to reproduce all child states because children are derived
        # deterministically from the parent's SeedSequence at construction time.
        _seed_seq = rng.bit_generator.seed_seq
        if _seed_seq is None:
            # Fallback for bit generators not backed by a SeedSequence (e.g.
            # custom BitGenerators or legacy wrappers). Sample entropy directly
            # from the parent generator to build a deterministic SeedSequence.
            _seed_seq = np.random.SeedSequence(
                int(rng.integers(0, 2**63, dtype=np.int64))
            )
        _child_seeds = _seed_seq.spawn(3)
        self._onef_noise = OneOverFNoise(config, np.random.default_rng(_child_seeds[0]))
        self._rts_noise = RTSNoise(config, np.random.default_rng(_child_seeds[1]))
        self._cr_injector = ClusteredCosmicRayInjector(
            config, np.random.default_rng(_child_seeds[2])
        )

        # Precompute once at construction time; config is frozen so this cannot drift.
        self._saturation_threshold: float = (
            config.nonlinearity.saturation_flag_threshold
            * config.electrical.full_well_electrons
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_epoch(
        self,
        ideal_image_e: np.ndarray,
        epoch_index: int,
        epoch_time_mjd: float,
        prev_epoch_time_mjd: float | None = None,
    ) -> DetectorOutput:
        """Process a single epoch through the detector signal chain.

        The current implementation is a structural stub: leaf module calls are
        wired in the correct order, but each is a no-op returning a copy.
        Physics will be enabled in subsequent phases.

        Parameters
        ----------
        ideal_image_e:
            2D array (ny, nx) of ideal electron counts (no detector effects
            applied).  Must match ``config.geometry.ny`` × ``config.geometry.nx``.
        epoch_index:
            Zero-based index of this epoch within the event.
        epoch_time_mjd:
            Modified Julian Date of this epoch's observation midpoint.  Used to
            derive a deterministic, physically consistent UTC timestamp for
            provenance (via MJD epoch 1858-11-17), and to compute the
            inter-epoch time delta for persistence.
        prev_epoch_time_mjd:
            MJD of the immediately preceding epoch, or ``None`` for the first
            epoch.  The inter-epoch time delta is derived exclusively from
            ``epoch_time_mjd - prev_epoch_time_mjd``; there is no separate
            ``delta_time_s`` parameter to prevent duplicate formulas.

        Returns
        -------
        DetectorOutput

        Raises
        ------
        ValueError
            If ``ideal_image_e`` is not 2-D, does not match the configured
            geometry, contains non-finite values, contains negative electrons,
            or if ``epoch_index`` is negative.
        """
        if ideal_image_e.ndim != 2:
            raise ValueError(
                f"ideal_image_e must be 2-D, got ndim={ideal_image_e.ndim}."
            )
        ny = self._config.geometry.ny
        nx = self._config.geometry.nx
        if ideal_image_e.shape != (ny, nx):
            raise ValueError(
                f"ideal_image_e.shape {ideal_image_e.shape!r} does not match "
                f"configured geometry ({ny}, {nx})."
            )
        if not np.all(np.isfinite(ideal_image_e)):
            raise ValueError(
                "ideal_image_e contains non-finite values (NaN or Inf)."
            )
        if np.any(ideal_image_e < 0):
            raise ValueError(
                "ideal_image_e contains negative electron counts."
            )
        if epoch_index < 0:
            raise ValueError(
                f"epoch_index must be >= 0, got {epoch_index}."
            )

        # Capture RNG state snapshot BEFORE any operations (reproducibility anchor).
        rng_state = self._rng.bit_generator.state

        # Inter-epoch time delta — single source of truth, derived from MJD only.
        # No separate delta_time_s parameter exists on this method.
        if prev_epoch_time_mjd is not None:
            delta_time_s = (epoch_time_mjd - prev_epoch_time_mjd) * 86400.0
        else:
            delta_time_s = 0.0

        # Cast to float64 and begin the signal chain.
        image = ideal_image_e.astype(np.float64, copy=True)

        # --- Fixed signal chain (stubs: each leaf returns input.copy()) ---
        image = self._charge_diffusion.apply(image)
        image = self._ipc.apply(image)
        image = self._persistence.apply(image, delta_time_s=delta_time_s)
        # NonLinearityModel is applied inside MultiAccumSimulator (per-read
        # when 3D ramp is implemented; once on 2D image in the stub).
        image = self._readout.simulate_ramp(image)
        # TEMPORARY GUARD: stub simulate_ramp returns 2D; production will return
        # 3D (n_reads, ny, nx). Replace with 3D ramp-collapse (e.g. slope fitting)
        # when MULTIACCUM physics is implemented. Remove this check at that point.
        if image.ndim != 2:
            raise RuntimeError(
                f"readout.simulate_ramp returned ndim={image.ndim}; "
                "expected 2-D from stub. Implement 3D ramp-collapse before removing guard."
            )

        # Noise injection
        image = self._onef_noise.apply(image)
        image = self._rts_noise.apply(image)
        image, cr_mask, cr_hit_count = self._cr_injector.apply(image)

        # Saturation mask: threshold precomputed in __init__ from frozen config.
        saturation_mask = image >= self._saturation_threshold
        saturated_pixel_count = int(saturation_mask.sum())

        provenance_data: dict[str, Any] = {
            "git_commit": self._git_commit,
            "container_digest": self._container_digest,
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "config_sha256": self._config_sha256,
            "random_state": sanitize_rng_state(rng_state),
            "ipc_applied": False,
            "persistence_applied": False,
            "nonlinearity_applied": False,
            "charge_diffusion_applied": True,
            "saturated_pixel_count": saturated_pixel_count,
            "cosmic_ray_hit_count": cr_hit_count,
        }

        return DetectorOutput(
            rate_image=image,
            saturation_mask=saturation_mask,
            cr_mask=cr_mask,
            provenance_data=provenance_data,
        )

    def process_event(
        self,
        event_id: str,
        ideal_cube_e: np.ndarray,
        timestamps_mjd: np.ndarray,
    ) -> EventOutput:
        """Process a multi-epoch event through the detector signal chain.

        Iterates over the epoch dimension of ``ideal_cube_e``, calling
        ``process_epoch`` for each slice.  Explicitly frees per-epoch
        intermediate data after extracting results to stay within the 32 GB
        memory budget.

        Parameters
        ----------
        event_id:
            Unique event identifier recorded in every provenance record.
        ideal_cube_e:
            3D array (n_epochs, ny, nx) of ideal electron counts.
        timestamps_mjd:
            1D array (n_epochs,) of Modified Julian Dates, one per epoch.

        Returns
        -------
        EventOutput

        Raises
        ------
        ValueError
            If ``ideal_cube_e`` is not 3-D, if ``timestamps_mjd`` length does
            not match the epoch dimension, or if ``timestamps_mjd`` contains
            non-finite values.
        """
        if ideal_cube_e.ndim != 3:
            raise ValueError(
                f"ideal_cube_e must be 3-D, got ndim={ideal_cube_e.ndim}."
            )
        n_epochs = ideal_cube_e.shape[0]
        if timestamps_mjd.shape != (n_epochs,):
            raise ValueError(
                f"timestamps_mjd.shape {timestamps_mjd.shape!r} does not match "
                f"n_epochs {n_epochs}."
            )
        if not np.all(np.isfinite(timestamps_mjd)):
            raise ValueError(
                "timestamps_mjd contains non-finite values (NaN or Inf)."
            )

        ny, nx = ideal_cube_e.shape[1], ideal_cube_e.shape[2]
        rate_cube = np.empty((n_epochs, ny, nx), dtype=np.float64)
        saturation_cube = np.zeros((n_epochs, ny, nx), dtype=bool)
        cr_cube = np.zeros((n_epochs, ny, nx), dtype=bool)
        persistence_peak_map = np.zeros((ny, nx), dtype=np.float64)
        provenance_records: list[ProvenanceRecord] = []

        for i in range(n_epochs):
            prev_mjd = float(timestamps_mjd[i - 1]) if i > 0 else None
            epoch_output = self.process_epoch(
                ideal_image_e=ideal_cube_e[i],
                epoch_index=i,
                epoch_time_mjd=float(timestamps_mjd[i]),
                prev_epoch_time_mjd=prev_mjd,
            )

            rate_cube[i] = epoch_output.rate_image
            saturation_cube[i] = epoch_output.saturation_mask
            cr_cube[i] = epoch_output.cr_mask

            record = ProvenanceRecord(
                event_id=event_id,
                epoch_index=i,
                timestamp_utc=_MJD_EPOCH + timedelta(days=float(timestamps_mjd[i])),
                **epoch_output.provenance_data,
            )
            provenance_records.append(record)

            # Aggressive GC required to prevent 3D ramp cubes from exceeding
            # 32GB limit during long events.
            del epoch_output
            gc.collect()

        return EventOutput(
            rate_cube=rate_cube,
            saturation_cube=saturation_cube,
            cr_cube=cr_cube,
            persistence_peak_map=persistence_peak_map,
            provenance_records=provenance_records,
            peak_memory_mb=0.0,
        )
