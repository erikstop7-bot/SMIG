"""
smig/config/schemas.py
======================
Immutable, validated detector configuration for the Roman WFI H4RG-10 sensor.

All numeric constants are sourced from the Roman Space Telescope WFI reference
documents and the Akeson et al. (2019) mission description.  Runtime code must
read every physical constant from an instantiated DetectorConfig — never from
bare numeric literals scattered through business logic.

Pydantic v2 is required (>= 2.0).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Sub-model: Focal-plane geometry
# ---------------------------------------------------------------------------

class GeometryConfig(BaseModel):
    """Focal-plane geometry of a single H4RG-10 SCA."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    nx: int = Field(
        default=4096,
        gt=0,
        description=(
            "Number of pixel columns per SCA (H4RG-10 native format).  "
            "Assumes 4096x4096 includes reference pixels "
            "(to be verified against final Roman flight ICD)."
        ),
    )
    ny: int = Field(
        default=4096,
        gt=0,
        description=(
            "Number of pixel rows per SCA.  "
            "Assumes 4096x4096 includes reference pixels "
            "(to be verified against final Roman flight ICD)."
        ),
    )
    pixel_pitch_um: float = Field(
        default=10.0,
        gt=0.0,
        description="Centre-to-centre pixel pitch in micrometres (um).",
    )
    pixel_scale_arcsec: float = Field(
        default=0.11,
        gt=0.0,
        description=(
            "On-sky plate scale in arcseconds per pixel for the WFI wide-field "
            "channel at the reference wavelength."
        ),
    )


# ---------------------------------------------------------------------------
# Sub-model: Electrical characteristics
# ---------------------------------------------------------------------------

class ElectricalConfig(BaseModel):
    """Electrical characteristics governing signal range and read noise."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    full_well_electrons: float = Field(
        default=100_000.0,
        gt=0.0,
        description=(
            "Full-well capacity in electrons (e-).  "
            "Defines the saturation ceiling; all charge models clamp to this value."
        ),
    )
    gain_e_per_adu: float = Field(
        default=1.5,
        gt=0.0,
        description="System gain: electrons per analogue-to-digital unit (e-/ADU).",
    )
    read_noise_cds_electrons: float = Field(
        default=12.0,
        ge=0.0,
        description=(
            "Single correlated double-sampling (CDS) read noise in electrons RMS.  "
            "Quoted for a single non-destructive read pair."
        ),
    )
    read_noise_effective_electrons: float = Field(
        default=5.0,
        ge=0.0,
        description=(
            "Effective read noise in electrons RMS after optimal Fowler / "
            "up-the-ramp sampling across a full ramp (used for signal-to-noise "
            "estimates, not per-frame noise injection)."
        ),
    )
    dark_current_e_per_s: float = Field(
        default=0.01,
        ge=0.0,
        description=(
            "Mean dark-current rate in electrons per second per pixel at the "
            "nominal operating temperature of ~95 K."
        ),
    )


# ---------------------------------------------------------------------------
# Sub-model: Readout timing
# ---------------------------------------------------------------------------

class ReadoutConfig(BaseModel):
    """Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.

    The three timing parameters are not independent: ``exposure_time_s`` must
    equal ``(n_ramp_reads - 1) * frame_time_s``.  A model validator enforces
    this identity at construction time.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    n_ramp_reads: int = Field(
        default=9,
        ge=2,
        description=(
            "Number of non-destructive reads per ramp (including the first reset "
            "read).  Must be >= 2 to allow at least one CDS difference.  "
            "Default of 9 gives (9 - 1) x 5.85 s = 46.8 s."
        ),
    )
    frame_time_s: float = Field(
        default=5.85,
        gt=0.0,
        description=(
            "Time to read out the full 4096 x 4096 array once, in seconds.  "
            "Determines the cadence of non-destructive samples."
        ),
    )
    exposure_time_s: float = Field(
        default=46.8,
        gt=0.0,
        description=(
            "Total integration time per exposure in seconds.  "
            "Must equal (n_ramp_reads - 1) x frame_time_s for a simple "
            "MULTIACCUM ramp; enforced by model validator."
        ),
    )

    @model_validator(mode="after")
    def _check_exposure_time_consistency(self) -> ReadoutConfig:
        expected = (self.n_ramp_reads - 1) * self.frame_time_s
        if not math.isclose(self.exposure_time_s, expected, rel_tol=1e-9):
            raise ValueError(
                f"exposure_time_s ({self.exposure_time_s}) must equal "
                f"(n_ramp_reads - 1) * frame_time_s = "
                f"({self.n_ramp_reads} - 1) * {self.frame_time_s} = {expected:.6f}"
            )
        return self


# ---------------------------------------------------------------------------
# Sub-model: Inter-pixel capacitance
# ---------------------------------------------------------------------------

class IPCConfig(BaseModel):
    """Inter-pixel capacitance (IPC) kernel parameters.

    Only scalar defaults are stored here; the full spatially-varying kernel
    array is loaded dynamically from an HDF5 calibration file at runtime by
    the FieldDependentIPC module, which reads ipc_alpha_center as its
    fallback uniform coupling coefficient.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ipc_kernel_size: int = Field(
        default=9,
        ge=3,
        description=(
            "Side length of the square IPC convolution kernel in pixels.  "
            "Must be odd so the kernel has a well-defined centre pixel.  "
            "A 9 x 9 kernel captures nearest- and next-nearest-neighbour coupling."
        ),
    )
    ipc_field_dependent: bool = Field(
        default=True,
        description=(
            "If True, the IPC kernel varies spatially across the SCA and is "
            "loaded from an HDF5 calibration map.  "
            "If False, a uniform alpha x identity-neighbourhood kernel is applied."
        ),
    )
    ipc_alpha_center: float = Field(
        default=0.02,
        ge=0.0,
        le=0.5,
        description=(
            "IPC coupling coefficient alpha at the SCA centre (dimensionless fraction "
            "of charge shared with each orthogonal neighbour).  "
            "Used as a uniform fallback when ipc_field_dependent is False or as "
            "a sanity-check reference value for the field-dependent map."
        ),
    )

    @field_validator("ipc_kernel_size")
    @classmethod
    def _must_be_odd(cls, val: int) -> int:
        if val % 2 == 0:
            raise ValueError(
                f"ipc_kernel_size must be odd (got {val}); "
                "an even kernel has no well-defined centre pixel."
            )
        return val


# ---------------------------------------------------------------------------
# Sub-model: Persistence (residual image)
# ---------------------------------------------------------------------------

class PersistenceConfig(BaseModel):
    """Two-component exponential persistence (residual-image) model.

    The persistence signal in electrons at time t after a saturating
    exposure is modelled as::

        P(t) = amp_short * exp(-t / tau_short_s)
               + amp_long  * exp(-t / tau_long_s)

    Both amplitudes are dimensionless fractions of full-well electrons
    trapped during saturation.  Their sum must not exceed 1.0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tau_short_s: float = Field(
        default=100.0,
        gt=0.0,
        description="Decay time constant of the short-lived trap population, seconds.",
    )
    tau_long_s: float = Field(
        default=1000.0,
        gt=0.0,
        description="Decay time constant of the long-lived trap population, seconds.",
    )
    amp_short: float = Field(
        default=0.005,
        ge=0.0,
        le=1.0,
        description=(
            "Amplitude of the short-lived component as a fraction of full-well "
            "electrons (dimensionless)."
        ),
    )
    amp_long: float = Field(
        default=0.001,
        ge=0.0,
        le=1.0,
        description=(
            "Amplitude of the long-lived component as a fraction of full-well "
            "electrons (dimensionless)."
        ),
    )

    @model_validator(mode="after")
    def _check_amplitude_sum(self) -> PersistenceConfig:
        total = self.amp_short + self.amp_long
        if total > 1.0:
            raise ValueError(
                f"amp_short + amp_long = {total:.6f} exceeds 1.0; "
                "the total trapped fraction cannot exceed the full well."
            )
        return self


# ---------------------------------------------------------------------------
# Sub-model: Nonlinearity
# ---------------------------------------------------------------------------

class NonlinearityConfig(BaseModel):
    """Polynomial detector nonlinearity model.

    The normalized measured response S_measured is related to the true
    accumulated charge Q_norm = Q_electrons / full_well_electrons by::

        S_measured = sum(coefficients[i] * Q_norm**i  for i in range(...))

    S_measured is a dimensionless normalized response (not raw ADU), which
    is why the constant term c_0 is approximately 1.0: at zero signal
    (Q_norm = 0), the ideal detector returns S_measured = 1.0 * 0^0 = 1.0
    ... equivalently, c_0 sets the small-signal gain normalization so that
    S_measured ≈ Q_norm for low charge.  The default coefficients
    (1.0, -2.7e-6, 7.8e-12) describe a mild sublinearity consistent with
    H4RG-10 laboratory measurements.

    Using tuple[float, ...] (immutable) prevents mutable-default bugs and
    is consistent with the frozen model contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    coefficients: tuple[float, ...] = Field(
        default=(1.0, -2.7e-6, 7.8e-12),
        min_length=2,
        description=(
            "Polynomial coefficients in ascending order of power, applied to "
            "Q_norm = e- / full_well_electrons.  "
            "Index 0 = constant (c_0 ~ 1.0), index 1 = linear correction, etc."
        ),
    )
    saturation_flag_threshold: float = Field(
        default=0.85,
        gt=0.0,
        le=1.0,
        description=(
            "Fraction of full-well electrons at which a pixel is flagged as "
            "approaching saturation (used for data-quality masking, not hard "
            "clipping -- hard clipping occurs at 1.0)."
        ),
    )


# ---------------------------------------------------------------------------
# Sub-model: Observing environment
# ---------------------------------------------------------------------------

class EnvironmentConfig(BaseModel):
    """Telescope and sky environment parameters."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    jitter_mas_per_axis: float = Field(
        default=5.0,
        ge=0.0,
        description=(
            "1-sigma pointing jitter per axis in milli-arcseconds (mas).  "
            "5.0 mas is the Roman pointing requirement; expected as-built "
            "performance is ~14 mas.  Applied as a Gaussian convolution to "
            "the PSF during image rendering."
        ),
    )
    sky_background_mag_per_arcsec2: float = Field(
        default=22.5,
        gt=0.0,
        description=(
            "Zodiacal-light sky background surface brightness in AB magnitudes "
            "per arcsecond^2 at the nominal WFI reference wavelength.  "
            "Used to set the Poisson background floor before dark-current addition."
        ),
    )


# ---------------------------------------------------------------------------
# Top-level immutable detector configuration
# ---------------------------------------------------------------------------

class DetectorConfig(BaseModel):
    """Immutable, fully-validated configuration for one Roman WFI H4RG-10 SCA.

    Instantiate once per simulation run and pass the object (never raw scalars)
    into all downstream pipeline stages.  The frozen=True / extra="forbid"
    contract guarantees that no stage can silently mutate or extend the config.

    Example
    -------
    >>> cfg = DetectorConfig()                     # use all defaults
    >>> cfg = DetectorConfig.model_validate(yaml.safe_load(Path("roman_wfi.yaml").read_text()))
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["2.0"] = Field(
        default="2.0",
        description="Schema version for forward-compatible config evolution.",
    )
    geometry: GeometryConfig = Field(default_factory=GeometryConfig)
    electrical: ElectricalConfig = Field(default_factory=ElectricalConfig)
    readout: ReadoutConfig = Field(default_factory=ReadoutConfig)
    ipc: IPCConfig = Field(default_factory=IPCConfig)
    persistence: PersistenceConfig = Field(default_factory=PersistenceConfig)
    nonlinearity: NonlinearityConfig = Field(default_factory=NonlinearityConfig)
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
